
import pandas as pd

from .EEMIndMeasureAnalysisObject import ImplementMeasures
from .AnalyzeUtilityData import *
from .RunSimulationCase import *
from .EEMIndMeasureAnalysisObject import *
from .PostProcessing import *
import os


class Measure:
    def __init__(self):
        self.PropName = None
        self.PropValue = None
        self.FixedCost = None
        self.UnitVarCost = None
        self.UnitProp = None
        self.UnitValue = None
        

class MeasureUtilities:
    def __init__(self,CurrentRunDir):
        self.CurrentRunDir = CurrentRunDir
        self.ElectrifiedCheck = False

    def SetMeasure(self,Measure,MeasureTypes):
        df_input = pd.read_pickle(os.path.join(self.CurrentRunDir,"BldgPropInputsFile.pkl")).reset_index(drop=True)
        BestModelParams = pd.read_csv(os.path.join(self.CurrentRunDir,"BestModelParams.csv")).iloc[0].to_dict()
    
        SetCurrentMeasure = ImplementMeasures(df_input,self.CurrentRunDir,BestModelParams)
        
        
        if "HeatingEquipment" in Measure.PropName and not self.ElectrifiedCheck:
            HeatingEqpOrg = df_input.loc[df_input["PropKey"] == "HeatingEquipment","PropValue"].iloc[0]
            HeatingEqpEEM = Measure.PropName.replace("HeatingEquipment ","")
            SetCurrentMeasure.HeatingEquipment(HeatingEqpOrg,HeatingEqpEEM)
            df_input.loc[df_input["PropKey"] == "HeatingEquipment", "PropValue"] = Measure.PropName.replace("HeatingEquipment ","")
            df_input.loc[df_input["PropKey"] == "HeatingEff", "PropValue"] = Measure.PropValue    
            if isinstance(Measure.UnitValue,str) and "autosize" in Measure.UnitValue:
                df_input.loc[df_input["PropKey"] == "HeatingCap", "PropValue"] = "autosize"
            else:
                df_input.loc[df_input["PropKey"] == "HeatingCap", "PropValue"] = float(Measure.UnitValue)/12 # Convert kBtuh to tons
            if "AirSourceHeatPump" in Measure.PropName:
                df_input.loc[df_input["PropKey"] == "CoolingEquipment", "PropValue"] = Measure.PropName.replace("HeatingEquipment ","")
                dfASHPOptions = pd.read_csv(os.path.join("Measures","System-AirSourceHeatPump.csv"))
                df_input.loc[df_input["PropKey"] == "CoolingEff", "PropValue"] = dfASHPOptions.loc[dfASHPOptions["HeatingEff"]==float(Measure.PropValue),"SEER"].iloc[0]
                if isinstance(Measure.UnitValue,str) and "autosize" in Measure.UnitValue:
                    df_input.loc[df_input["PropKey"] == "CoolingCap", "PropValue"] = "autosize"
                else:
                    df_input.loc[df_input["PropKey"] == "CoolingCap", "PropValue"] = float(Measure.UnitValue)/12 # Convert kBtuh to tons
                self.ElectrifiedCheck = True
        
        elif "CoolingEquipment" in Measure.PropName and not self.ElectrifiedCheck:
            df_input.loc[df_input["PropKey"] == "CoolingEquipment", "PropValue"] = Measure.PropName.replace("CoolingEquipment ","")
            df_input.loc[df_input["PropKey"] == "CoolingEff", "PropValue"] = Measure.PropValue
            if isinstance(Measure.UnitValue,str) and "autosize" in Measure.UnitValue:
                df_input.loc[df_input["PropKey"] == "CoolingCap", "PropValue"] = "autosize"
            else:
                df_input.loc[df_input["PropKey"] == "CoolingCap", "PropValue"] = float(Measure.UnitValue)/12 # Convert kBtuh to tons
            if "AirSourceHeatPump" in Measure.PropName:
                HeatingEqpOrg = df_input.loc[df_input["PropKey"] == "HeatingEquipment","PropValue"].iloc[0]
                HeatingEqpEEM = Measure.PropName.replace("CoolingEquipment ","")
                SetCurrentMeasure.HeatingEquipment(HeatingEqpOrg,HeatingEqpEEM)
                df_input.loc[df_input["PropKey"] == "HeatingEquipment", "PropValue"] = Measure.PropName.replace("CoolingEquipment ","")
                dfASHPOptions = pd.read_csv(os.path.join("Measures","System-AirSourceHeatPump.csv"))
                df_input.loc[df_input["PropKey"] == "HeatingEff", "PropValue"] = dfASHPOptions.loc[dfASHPOptions["SEER"]==float(Measure.PropValue),"HeatingEff"].iloc[0]

                if isinstance(Measure.UnitValue,str) and "autosize" in Measure.UnitValue:
                    df_input.loc[df_input["PropKey"] == "HeatingCap", "PropValue"] = "autosize"
                else:
                    df_input.loc[df_input["PropKey"] == "HeatingCap", "PropValue"] = float(Measure.UnitValue)/12 # Convert kBtuh to tons
                self.ElectrifiedCheck = True
        
        elif "DHWSystemType" in Measure.PropName:
            df_input.loc[df_input["PropKey"] == "DHWSystemType", "PropValue"] = Measure.PropName.replace("DHWSystemType ","")
            df_input.loc[df_input["PropKey"] == "DHWTankVol", "PropValue"] = Measure.UnitValue
        
        elif "WallInsulation" in Measure.PropName:
            ExtWallConst = df_input.loc[df_input["PropKey"] == "ExtWallConst","PropValue"].iloc[0]
            WallInsOrg = df_input.loc[df_input["PropKey"] == Measure.PropName,"PropValue"].iloc[0]
            WallInsEEM = Measure.PropValue
            SetCurrentMeasure.WallInsulation(ExtWallConst,WallInsOrg,WallInsEEM)
            df_input.loc[df_input["PropKey"] == Measure.PropName, "PropValue"] = WallInsEEM

        elif "ACH50" in Measure.PropName:
            ACH50Org = float(df_input.loc[df_input["PropKey"] == Measure.PropName,"PropValue"].iloc[0])
            ACH50EEM = float(Measure.PropValue)
            SetCurrentMeasure.Infiltration(ACH50Org,ACH50EEM)
            df_input.loc[df_input["PropKey"] == Measure.PropName, "PropValue"] = ACH50EEM

        elif "CeilingInsulation" in Measure.PropName:
            ExtRoofConst = df_input.loc[df_input["PropKey"] == "ExtRoofConst","PropValue"].iloc[0]
            CeilingConst = df_input.loc[df_input["PropKey"] == "CeilingConst","PropValue"].iloc[0]
            CeilingInsOrg = df_input.loc[df_input["PropKey"] == Measure.PropName,"PropValue"].iloc[0]
            CeilingInsEEM = Measure.PropValue
            SetCurrentMeasure.CeilingInsulation(ExtRoofConst,CeilingConst,CeilingInsOrg,CeilingInsEEM)
            df_input.loc[df_input["PropKey"] == Measure.PropName, "PropValue"] = CeilingInsEEM

        elif "WindowMaterial" in Measure.PropName:
            WindowMatOrg = df_input.loc[df_input["PropKey"] == Measure.PropName,"PropValue"].iloc[0]
            WindowMatEEM = Measure.PropValue
            SetCurrentMeasure.WindowMaterial(WindowMatOrg,WindowMatEEM)
            df_input.loc[df_input["PropKey"] == Measure.PropName, "PropValue"] = WindowMatEEM

        elif "OccupancySensor" in Measure.PropName:
            OccupancySensorOrg = df_input.loc[df_input["PropKey"] == Measure.PropName,"PropValue"].iloc[0]
            OccupancySensorEEM = Measure.PropValue
            pct_savings = SetCurrentMeasure.OccupancySensorControls()
            df_input.loc[df_input["PropKey"] == Measure.PropName, "PropValue"] = OccupancySensorEEM
            df_input.loc[df_input["PropKey"] == "LPD", "PropValue"] = (1-pct_savings)*float(df_input.loc[df_input["PropKey"] == "LPD", "PropValue"].iloc[0])

        elif "Daylighting" in Measure.PropName:
            DaylightingOrg = df_input.loc[df_input["PropKey"] == Measure.PropName,"PropValue"].iloc[0]
            DaylightingEEM = Measure.PropValue
            pct_savings = SetCurrentMeasure.DaylightingControls()
            df_input.loc[df_input["PropKey"] == Measure.PropName, "PropValue"] = DaylightingEEM
            df_input.loc[df_input["PropKey"] == "LPD", "PropValue"] = (1-pct_savings)*float(df_input.loc[df_input["PropKey"] == "LPD", "PropValue"].iloc[0])

        elif "LED" in Measure.PropName:
            pctLEDOrg = df_input.loc[df_input["PropKey"] == "LEDCurrent","PropValue"].iloc[0]
            pctLEDEEM = Measure.PropValue
            pct_savings = SetCurrentMeasure.ReplaceLighting(pctLEDOrg,pctLEDEEM)
            df_input.loc[df_input["PropKey"] == "LEDECM", "PropValue"] = pctLEDEEM
            df_input.loc[df_input["PropKey"] == "LPD", "PropValue"] = (1-pct_savings)*float(df_input.loc[df_input["PropKey"] == "LPD", "PropValue"].iloc[0])
        
        elif "Economizer" in Measure.PropName:
            economizer_org = df_input.loc[df_input["PropKey"] == "Economizer","PropValue"].iloc[0]
            economizer_eem = Measure.PropValue
            location = df_input.loc[df_input["PropKey"] == "Location","PropValue"].iloc[0]
            SetCurrentMeasure.Economizer(location)
            df_input.loc[df_input["PropKey"] == "Economizer","PropValue"] = economizer_eem

        else:
            df_input.loc[df_input["PropKey"] == Measure.PropName, "PropValue"] = Measure.PropValue

        df_input.to_pickle(os.path.join(self.CurrentRunDir,"BldgPropInputsFile.pkl"))
        return  

    

    def RunMeasure(self,CostMetrics,df_weather):
        
        df_input = pd.read_pickle(os.path.join(self.CurrentRunDir,"BldgPropInputsFile.pkl")).reset_index(drop=True)
        print("Running simulation for measure with inputs:", df_input.loc[df_input["PropKey"].isin(["HeatingEquipment","HeatingEff","HeatingCap","CoolingEquipment","CoolingEff","CoolingCap"]), ["PropKey","PropValue"]])
        UpdatedModelParams = pd.read_csv(os.path.join(self.CurrentRunDir,"BestModelParams.csv")).iloc[0].to_dict()
        GetMonthlyEndUseBreakdown(UpdatedModelParams,df_weather,df_input,self.CurrentRunDir)
        GetSummaryResults(self.CurrentRunDir,CostMetrics)
        
        return 
    
    def GetMeasurePackageResults(self,MeasureList):
        BestModelParams = pd.read_csv(os.path.join(self.CurrentRunDir,"SummaryResults.csv")).iloc[0].to_dict()
        BestModelParams["TIC"] = 0.0
        for m in MeasureList:
            if isinstance(m.UnitValue, str) and "autosize" in m.UnitValue:
                UnitVal = 0.0
            else:
                UnitVal = (m.UnitValue)
            

            BestModelParams["TIC"] += float(m.FixedCost) + float(m.UnitVarCost)*float(UnitVal)

        BestModelParams["LCC"] = BestModelParams["TIC"] + BestModelParams["TOC"]

        dfRunIDFSummaryRes = pd.DataFrame([BestModelParams])
        dfRunIDFSummaryRes.to_csv(os.path.join(self.CurrentRunDir,"RunResults"+".csv"),index=False)
        return 
    

class MeasureOptions:
    def __init__(self, RunDir):
        # self.SimResClass = GetSimResults(CostMetrics)
        # self.SumRes = self.SimResClass.getSummaryResults("CurrentWorkingDir") # THis has to take results from the autocalibrated simulation.
        self.SumRes = pd.read_csv(os.path.join(RunDir,"SummaryResults.csv")).iloc[0].to_dict()


    def WallInsulation(self):
        WallInsProp = pd.read_csv(os.path.join("Measures","Materials-WallInsulation.csv"))
        WallInsOptions = []
        for i in range(WallInsProp.shape[0]):
            MeasureObj = Measure()
            MeasureObj.PropName = "R-WallInsulation"
            MeasureObj.PropValue = WallInsProp.loc[i,"InsulationName"]
            MeasureObj.FixedCost = WallInsProp.loc[i,"FixedCost"]
            MeasureObj.UnitVarCost = WallInsProp.loc[i,"Costpersft"]
            MeasureObj.UnitProp = "ExtWallArea"
            MeasureObj.UnitValue = self.SumRes[MeasureObj.UnitProp]
            WallInsOptions.append(MeasureObj)
        return WallInsOptions


    def CeilingInsulation(self):
        CeilingInsProp = pd.read_csv(os.path.join("Measures","Materials-CeilingInsulation.csv"))
        CeilingInsOptions = []
        for i in range(CeilingInsProp.shape[0]):
            MeasureObj = Measure()
            MeasureObj.PropName = "R-CeilingInsulation"
            MeasureObj.PropValue = CeilingInsProp.loc[i,"InsulationName"]
            MeasureObj.FixedCost = CeilingInsProp.loc[i,"FixedCost"]
            MeasureObj.UnitVarCost = CeilingInsProp.loc[i,"Costpersft"]
            MeasureObj.UnitProp = "FloorArea"
            MeasureObj.UnitValue = self.SumRes[MeasureObj.UnitProp]
            CeilingInsOptions.append(MeasureObj)
        return CeilingInsOptions
    
    def Infiltration(self):
        InfiltrationProp = pd.read_csv(os.path.join("Measures","Infiltration.csv"))
        InfiltrationOptions = []
        for i in range(InfiltrationProp.shape[0]):
            MeasureObj = Measure()
            MeasureObj.PropName = "ACH50"
            MeasureObj.PropValue = float(InfiltrationProp.loc[i,"ACH50"])
            MeasureObj.FixedCost = InfiltrationProp.loc[i,"FixedCost"]
            MeasureObj.UnitVarCost = InfiltrationProp[["Costpersft","CostperACHsft"]].sum(axis=1).iloc[i]
            MeasureObj.UnitProp = "FloorArea"
            MeasureObj.UnitValue = self.SumRes[MeasureObj.UnitProp]
            InfiltrationOptions.append(MeasureObj)
        return InfiltrationOptions
    
    def WindowMaterial(self):
        WindowMaterialProp = pd.read_csv(os.path.join("Measures","Materials-WindowMaterial.csv"))
        WindowMaterialOptions = []
        for i in range(WindowMaterialProp.shape[0]):
            MeasureObj = Measure()
            MeasureObj.PropName = "WindowMaterial"
            MeasureObj.PropValue = WindowMaterialProp.loc[i,"WindowMaterial"]
            MeasureObj.FixedCost = WindowMaterialProp.loc[i,"FixedCost"]
            MeasureObj.UnitVarCost = WindowMaterialProp.loc[i,"Costpersft"]
            MeasureObj.UnitProp = "WindowArea"
            MeasureObj.UnitValue = self.SumRes[MeasureObj.UnitProp]
            WindowMaterialOptions.append(MeasureObj)
        return WindowMaterialOptions
    
    def DaylightingControls(self):
        DaylightingControlsProp = pd.read_csv(os.path.join("Measures","Equipment-Daylighting.csv"))
        DaylightingControlsOptions = []
        for i in range(DaylightingControlsProp.shape[0]):
            MeasureObj = Measure()
            MeasureObj.PropName = "Daylighting"
            MeasureObj.PropValue = DaylightingControlsProp.loc[i,"Daylighting"]
            MeasureObj.FixedCost = DaylightingControlsProp.loc[i,"FixedCost"]
            MeasureObj.UnitVarCost = DaylightingControlsProp.loc[i,"Costpersft"]
            MeasureObj.UnitProp = "FloorArea"
            MeasureObj.UnitValue = self.SumRes[MeasureObj.UnitProp]
            DaylightingControlsOptions.append(MeasureObj)
        return DaylightingControlsOptions
    
    def OccupancySensorControls(self):
        OccupancySensorControlsProp = pd.read_csv(os.path.join("Measures","Equipment-OccupancySensor.csv"))
        OccupancySensorControlsOptions = []
        for i in range(OccupancySensorControlsProp.shape[0]):
            MeasureObj = Measure()
            MeasureObj.PropName = "OccupancySensor"
            MeasureObj.PropValue = OccupancySensorControlsProp.loc[i,"OccupancySensor"]
            MeasureObj.FixedCost = OccupancySensorControlsProp.loc[i,"FixedCost"]
            MeasureObj.UnitVarCost = OccupancySensorControlsProp.loc[i,"Costpersft"]
            MeasureObj.UnitProp = "FloorArea"
            MeasureObj.UnitValue = self.SumRes[MeasureObj.UnitProp]
            OccupancySensorControlsOptions.append(MeasureObj)
        return OccupancySensorControlsOptions

    def PercentageLED(self):
        PercentageLEDProp = pd.read_csv(os.path.join("Measures","Equipment-LED.csv"))
        PercentageLEDOptions = []
        for i in range(PercentageLEDProp.shape[0]):
            MeasureObj = Measure()
            MeasureObj.PropName = "LEDECM"
            MeasureObj.PropValue = float(PercentageLEDProp.loc[i,"PercentageLED"])
            MeasureObj.FixedCost = PercentageLEDProp.loc[i,"FixedCost"]
            MeasureObj.UnitVarCost = PercentageLEDProp.loc[i,"Costpersft"]
            MeasureObj.UnitProp = "FloorArea"
            MeasureObj.UnitValue = self.SumRes[MeasureObj.UnitProp]
            PercentageLEDOptions.append(MeasureObj)
        return PercentageLEDOptions

    def Economizer(self):
        EconomizerProp = pd.read_csv(os.path.join("Measures","System-Economizer.csv"))
        EconomizerOptions = []
        for i in range(EconomizerProp.shape[0]):
            MeasureObj = Measure()
            MeasureObj.PropName = "Economizer"
            MeasureObj.PropValue = EconomizerProp.loc[i,"Economizer"]
            MeasureObj.FixedCost = EconomizerProp.loc[i,"FixedCost"]
            MeasureObj.UnitVarCost = EconomizerProp.loc[i,"Costpersft"]
            MeasureObj.UnitProp = "FloorArea"
            MeasureObj.UnitValue = self.SumRes[MeasureObj.UnitProp]
            EconomizerOptions.append(MeasureObj)
        return EconomizerOptions

    def ReduceEquipmentLoad(self):
        PctEqpLoadReduction = pd.read_csv(os.path.join("Measures","Equipment-ReduceEquipmentLoad.csv"))
        PercentageLEDOptions = []
        for i in range(PctEqpLoadReduction.shape[0]):
            MeasureObj = Measure()
            MeasureObj.PropName = "EquipLoadRed"
            MeasureObj.PropValue = float(PctEqpLoadReduction.loc[i,"PctLoadReduction"])
            MeasureObj.FixedCost = PctEqpLoadReduction.loc[i,"FixedCost"]
            MeasureObj.UnitVarCost = PctEqpLoadReduction.loc[i,"Costpersft"]
            MeasureObj.UnitProp = "FloorArea"
            MeasureObj.UnitValue = self.SumRes[MeasureObj.UnitProp]
            PercentageLEDOptions.append(MeasureObj)
        return PercentageLEDOptions
    
    def NightSetback(self):
        NightSetbackProp = pd.read_csv(os.path.join("Measures","Controls-NightSetback.csv"))
        NightSetbackOptions = []
        for i in range(NightSetbackProp.shape[0]):
            MeasureObj = Measure()
            MeasureObj.PropName = "NightSetback"
            MeasureObj.PropValue = float(NightSetbackProp.loc[i,"NightSetback"])
            MeasureObj.FixedCost = NightSetbackProp.loc[i,"FixedCost"]
            MeasureObj.UnitVarCost = NightSetbackProp.loc[i,"Costpersft"]
            MeasureObj.UnitProp = "FloorArea" # This doesn't matter because both costs are 0.
            MeasureObj.UnitValue = self.SumRes[MeasureObj.UnitProp]
            NightSetbackOptions.append(MeasureObj)
        return NightSetbackOptions
    
    def HoursNightSetback(self):
        NightSetbackProp = pd.read_csv(os.path.join("Measures","Controls-HoursNightSetback.csv"))
        NightSetbackOptions = []
        for i in range(NightSetbackProp.shape[0]):
            MeasureObj = Measure()
            MeasureObj.PropName = "nNightSetbackHours"
            MeasureObj.PropValue = float(NightSetbackProp.loc[i,"HoursNightSetback"])
            MeasureObj.FixedCost = NightSetbackProp.loc[i,"FixedCost"]
            MeasureObj.UnitVarCost = NightSetbackProp.loc[i,"Costpersft"]
            MeasureObj.UnitProp = "FloorArea" # This doesn't matter because both costs are 0.
            MeasureObj.UnitValue = self.SumRes[MeasureObj.UnitProp]
            NightSetbackOptions.append(MeasureObj)
        return NightSetbackOptions
    
    def HeatingEquipment(self):
        HeatingEquipmentProp = pd.read_csv(os.path.join("Measures","System-HeatingEquipment.csv"))
        HeatingEquipmentOptions = []
        for i in range(HeatingEquipmentProp.shape[0]):
            CurrentHeatingEqpProp = pd.read_csv(os.path.join("Measures","System-"+HeatingEquipmentProp.loc[i,"System"].replace(" ","")+".csv"))
            for j in range(CurrentHeatingEqpProp.shape[0]):
                CurrentHeatingCapProp = pd.read_csv(os.path.join("Measures","System-CoilCapacities.csv"))
                for k in range(CurrentHeatingCapProp.shape[0]):
                    MeasureObj = Measure()
                    MeasureObj.PropName = "HeatingEquipment" +" "+HeatingEquipmentProp.loc[i,"System"].replace(" ","")
                    MeasureObj.PropValue = CurrentHeatingEqpProp.loc[j,"HeatingEff"]
                    MeasureObj.FixedCost = CurrentHeatingEqpProp.loc[j,"Costperunit"]
                    MeasureObj.UnitVarCost = CurrentHeatingEqpProp.loc[j,"CostperkBtuh"]
                    MeasureObj.UnitProp = "CoilCapacity"
                    MeasureObj.UnitValue = CurrentHeatingCapProp.loc[k,"Capacity (tons)"]*12 #Convert tons to kBtuh
                    HeatingEquipmentOptions.append(MeasureObj)
        return HeatingEquipmentOptions
    
    def CoolingEquipment(self):
        CoolingEquipmentProp = pd.read_csv(os.path.join("Measures","System-CoolingEquipment.csv"))
        CoolingEquipmentOptions = []
        for i in range(CoolingEquipmentProp.shape[0]):
            CurrentCoolingEqpProp = pd.read_csv(os.path.join("Measures","System-"+CoolingEquipmentProp.loc[i,"System"].replace(" ","")+".csv"))
            for j in range(CurrentCoolingEqpProp.shape[0]):
                CurrentCoolingCapProp = pd.read_csv(os.path.join("Measures","System-CoilCapacities.csv"))
                for k in range(CurrentCoolingCapProp.shape[0]):
                    MeasureObj = Measure()
                    MeasureObj.PropName = "CoolingEquipment" +" "+CoolingEquipmentProp.loc[i,"System"].replace(" ","")
                    MeasureObj.PropValue = CurrentCoolingEqpProp.loc[j,"SEER"].astype(str)
                    MeasureObj.FixedCost = CurrentCoolingEqpProp.loc[j,"Costperunit"]
                    MeasureObj.UnitVarCost = CurrentCoolingEqpProp.loc[j,"CostperkBtuh"]
                    MeasureObj.UnitProp = "CoilCapacity"
                    MeasureObj.UnitValue = CurrentCoolingCapProp.loc[k,"Capacity (tons)"]*12 #Convert tons to kBtuh
                    CoolingEquipmentOptions.append(MeasureObj)
        return CoolingEquipmentOptions
    
    def DHWEquipment(self):
        DHWEquipmentProp = pd.read_csv(os.path.join("Measures","System-DHWSystemType.csv"))
        DHWEquipmentOptions = []
        for i in range(DHWEquipmentProp.shape[0]):
            CurrentDHWProp = pd.read_csv(os.path.join("Measures","System-"+DHWEquipmentProp.loc[i,"System"].replace(" ","")+".csv"))
            for j in range(CurrentDHWProp.shape[0]):
                CurrentDHWCapProp = pd.read_csv(os.path.join("Measures","System-DHWTankVolumes.csv"))
                for k in range(CurrentDHWCapProp.shape[0]):
                    MeasureObj = Measure()
                    MeasureObj.PropName = "DHWSystemType" +" "+DHWEquipmentProp.loc[i,"System"].replace(" ","")
                    MeasureObj.PropValue = CurrentDHWProp.loc[j,"HeatingEff"].astype(str)
                    MeasureObj.FixedCost = CurrentDHWProp.loc[j,"Costperunit"]
                    MeasureObj.UnitVarCost = CurrentDHWProp.loc[j,"Costpergallon"]
                    MeasureObj.UnitProp = "TankVolume"
                    MeasureObj.UnitValue = CurrentDHWCapProp.loc[k,"Capacity (gal)"] 
                    DHWEquipmentOptions.append(MeasureObj)
        return DHWEquipmentOptions