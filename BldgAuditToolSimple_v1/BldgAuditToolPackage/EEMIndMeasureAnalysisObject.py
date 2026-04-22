import pandas as pd
import geocoder
import numpy 
import matplotlib.pyplot as plt
import os
# from AnalyzeUtilityData import *
# from PostProcessing import *
from .AnalyzeUtilityData import *
from .PostProcessing import *


class EvaluateMeasure:
    def __init__(self,df_input,df_weather,MainPath,ProjectPath,BestModelParams):
        self.df_input = df_input.copy()
        self.df_weather = df_weather.copy()
        self.MainPath = MainPath
        self.ProjectPath = ProjectPath
        self.BestModelParams = BestModelParams
        
        self.FloorArea = df_input.loc[df_input.PropKey == "FloorArea"].PropValue.astype(float).iloc[0]
        FloorQty = df_input.loc[df_input.PropKey == "FloorQty"].PropValue.astype(float).iloc[0]
        WWR = df_input.loc[df_input.PropKey == "WWR"].PropValue.iloc[0].copy()
        ShapeType = df_input.loc[df_input.PropKey == "Shape"].PropValue.item()
        WallHeight = df_input.loc[df_input.PropKey == "WallHeight"].PropValue.astype(float).iloc[0]
        self.Volume = self.FloorArea*WallHeight*FloorQty
        WindowHeight = df_input.loc[df_input.PropKey == "WindowHeight"].PropValue.astype(float).iloc[0]
        x1 = df_input.loc[df_input.PropKey == "x1"].PropValue.astype(float).iloc[0]
        x2 = df_input.loc[df_input.PropKey == "x2"].PropValue.astype(float).iloc[0]
        y1 = df_input.loc[df_input.PropKey == "y1"].PropValue.astype(float).iloc[0]
        y2 = df_input.loc[df_input.PropKey == "y2"].PropValue.astype(float).iloc[0]
    
        if ShapeType == "Rectangle":
            self.WallArea = {}
            self.WallArea["Front"] = x1*WallHeight
            self.WallArea["Left"] = y1*WallHeight
            self.WallArea["Right"] = y1*WallHeight
            self.WallArea["Back"] = x1*WallHeight

            self.WindowArea = {}
            self.WindowArea["Front"] = WWR["Front"]/100*self.WallArea["Front"]
            self.WindowArea["Left"] = WWR["Left"]/100*self.WallArea["Left"]
            self.WindowArea["Right"] = WWR["Right"]/100*self.WallArea["Right"]
            self.WindowArea["Back"] = WWR["Back"]/100*self.WallArea["Back"]

            self.ExtWallArea = {}
            for face in self.WallArea.keys():
                self.ExtWallArea[face] = self.WallArea[face] - self.WindowArea[face]
        
        self.BestModelParams["BLC_Heating_NG_adj"] = self.BestModelParams["BLC_Heat_NG"] 
        self.BestModelParams["BLC_Heating_EL_adj"] = self.BestModelParams["BLC_Heat_EL"] 
        self.BestModelParams["BLC_Cooling_EL_adj"] = self.BestModelParams["BLC_Cool_EL"] 
    
    


    def WallInsulation(self,ExtWallConst,WallInsOrg,WallInsEEM):
        WallConstOptions = pd.read_csv(os.path.join(self.MainPath,"Inputs","InputCSVData","Construction-Wall.csv"))
        WallConstRvalue = WallConstOptions.loc[WallConstOptions.Construction==ExtWallConst,"Rvalue_IP"].astype(float).iloc[0] #hr-ft2-F/Btu

        WallInsProp = pd.read_csv(os.path.join(self.ProjectPath,"CostData","Materials-WallInsulation.csv"))
        if (WallInsOrg != "Uninsulated")&(WallInsOrg != "Unknown"):
            WallInsRvalue_org = WallInsProp.loc[WallInsProp.InsulationName==WallInsOrg,"Rvalue_IP"].astype(float).iloc[0] #hr-ft2-F/Btu

        if (WallInsEEM != "Uninsulated")&(WallInsEEM != "Unknown"):
            WallInsRvalue_EEM = WallInsProp.loc[WallInsProp.InsulationName==WallInsEEM,"Rvalue_IP"].astype(float).iloc[0] #hr-ft2-F/Btu
            
        Delta_BLC = 0

        if WallInsOrg == "Uninsulated":
            Delta_BLC = sum(self.ExtWallArea.values())*(1/(WallInsRvalue_EEM+WallConstRvalue) - 1/WallConstRvalue)
            BLC_wall_org = sum(self.ExtWallArea.values())*(1/WallConstRvalue)
        else:
            Delta_BLC = sum(self.ExtWallArea.values())*(1/(WallInsRvalue_EEM+WallConstRvalue) - 1/(WallInsRvalue_org+WallConstRvalue)) 
            BLC_wall_org = sum(self.ExtWallArea.values())*(1/(WallInsRvalue_org+WallConstRvalue))

        # Use these ratios only when the BLC calculated is lower than the changein UA value due to wall
        f_Savings = abs(Delta_BLC)/BLC_wall_org # Percentage reduction in BLC of element due to insulation
        f_WallArea = sum(self.ExtWallArea.values())/(sum(self.ExtWallArea.values())+sum(self.WindowArea.values())+2*self.FloorArea) # Percentage of wall area as fraction of total envelope area
        
        # Adjust the BLC values only if the savings are less than the BLC value
        if self.BestModelParams["BLC_Heating_NG_adj"] > self.BestModelParams["BLC_Heating_EL_adj"]:
            if self.BestModelParams["BLC_Heating_NG_adj"] > abs(Delta_BLC):
                self.BestModelParams["BLC_Heating_NG_adj"] += Delta_BLC
            else:
                self.BestModelParams["BLC_Heating_NG_adj"]  = (1-f_WallArea)*self.BestModelParams["BLC_Heating_NG_adj"] + (1-f_Savings)*f_WallArea*self.BestModelParams["BLC_Heating_NG_adj"]

        elif self.BestModelParams["BLC_Heating_NG_adj"] < self.BestModelParams["BLC_Heating_EL_adj"]:   
            if self.BestModelParams["BLC_Heating_EL_adj"] > abs(Delta_BLC):
                self.BestModelParams["BLC_Heating_EL_adj"] += Delta_BLC
            else:
                self.BestModelParams["BLC_Heating_EL_adj"]  = (1-f_WallArea)*self.BestModelParams["BLC_Heating_EL_adj"] + (1-f_Savings)*f_WallArea*self.BestModelParams["BLC_Heating_EL_adj"]

        if self.BestModelParams["BLC_Cooling_EL_adj"] > abs(Delta_BLC):
            self.BestModelParams["BLC_Cooling_EL_adj"] += Delta_BLC
        else:
            self.BestModelParams["BLC_Cooling_EL_adj"]  = (1-f_WallArea)*self.BestModelParams["BLC_Cooling_EL_adj"] + (1-f_Savings)*f_WallArea*self.BestModelParams["BLC_Cooling_EL_adj"]
            
        ECMEval = True

        df_MonthlyEndUse_EEM = GetMonthlyEndUseBreakdown(self.BestModelParams,self.df_weather,self.df_input,ECMEval)
        print(self.BestModelParams)
        EEMResults = {}
        EEMResults["Measure"] = "WallInsulation"
        EEMResults["OrgPropValue"] = WallInsOrg
        EEMResults["NewPropValue"] = WallInsEEM
        EEMResults["InitFixedCost"] = 0
        EEMResults["UnitVarCost"] = WallInsProp.loc[WallInsProp.InsulationName==WallInsEEM,"Costpersft"].astype(float).iloc[0]
        EEMResults["Unit"] = sum(self.ExtWallArea.values())
        EEMResults["InitVarCost"] = EEMResults["UnitVarCost"]*EEMResults["Unit"]
        EEMResults["RetrofitCost"] = 0
        EEMResults["Salvage"] = 0
        EEMResults["OrgTotalElectricity"] = self.BestModelParams["OrgTotalElectricity"]
        EEMResults["OrgTotalNaturalGas"] = self.BestModelParams["OrgTotalNaturalGas"]
        EEMResults["EEMTotalElectricity"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("EL-")].sum().sum()/3.41 # Convert to kWh
        EEMResults["EEMTotalNaturalGas"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("NG-")].sum().sum()/100 # Convert to Therms
        
        
        return df_MonthlyEndUse_EEM,EEMResults
    
    def Infiltration(self,ACH50Org,ACH50EEM):
        # First convert into average infiltration values based on rule of thumb.
        # https://www.aivc.org/sites/default/files/airbase_3097.pdf
        ACHOrg = ACH50Org/20
        ACHEEM = ACH50EEM/20
        
        VinfOrg = ACHOrg*self.Volume # Convert to cubic ft per hour
        VinfEEM = ACHEEM*self.Volume # Convert to cubic ft per hour
        
        rho_air = 0.0752 # lb/ft3 at 20C and 1atm
        Cp = 0.2402 # Btu/lb-F at 20C and 1atm
        
        # Even though the change in heating BLC is the same you still have to do this separately to ensure that you are only changing an existing BLC
        Delta_BLC = rho_air*Cp*(VinfEEM - VinfOrg)
        
        f_Savings = abs(Delta_BLC)/(rho_air*Cp*VinfOrg) # Percentage reduction in BLC of element due to infiltration change
        # This needs a better estimate. For now, I am assuming that the infiltration is a percentage of the total inverse model BLC
        f_pct = 0.3# Straight up assume a percentage with no reference for this.

        if self.BestModelParams["BLC_Heating_NG_adj"] > self.BestModelParams["BLC_Heating_EL_adj"]:
            if self.BestModelParams["BLC_Heating_NG_adj"] > abs(Delta_BLC):
                self.BestModelParams["BLC_Heating_NG_adj"] += Delta_BLC
            else:
                self.BestModelParams["BLC_Heating_NG_adj"]  = (1-f_pct)*self.BestModelParams["BLC_Heating_NG_adj"] + (1-f_Savings)*f_pct*self.BestModelParams["BLC_Heating_NG_adj"]
        
        elif self.BestModelParams["BLC_Heating_NG_adj"] < self.BestModelParams["BLC_Heating_EL_adj"]:
            if self.BestModelParams["BLC_Heating_EL_adj"] > abs(Delta_BLC):
                self.BestModelParams["BLC_Heating_EL_adj"] += Delta_BLC
            else:
                self.BestModelParams["BLC_Heating_EL_adj"]  = (1-f_pct)*self.BestModelParams["BLC_Heating_EL_adj"] + (1-f_Savings)*f_pct*self.BestModelParams["BLC_Heating_EL_adj"]

        if self.BestModelParams["BLC_Cooling_EL_adj"] > abs(Delta_BLC):
            self.BestModelParams["BLC_Cooling_EL_adj"] += Delta_BLC
        else:
            #print(f_Savings,f_pct)
            self.BestModelParams["BLC_Cooling_EL_adj"]  = (1-f_pct)*self.BestModelParams["BLC_Cooling_EL_adj"] + (1-f_Savings)*f_pct*self.BestModelParams["BLC_Cooling_EL_adj"]
        

        ECMEval = True

        df_MonthlyEndUse_EEM = GetMonthlyEndUseBreakdown(self.BestModelParams,self.df_weather,self.df_input,ECMEval)
        
        InfilOptions = pd.read_csv(os.path.join(self.ProjectPath,"CostData","Infiltration.csv")).astype(float) # Cost values are per unit finished floor area
        
        
        EEMResults = {}
        EEMResults["Measure"] = "Infiltration"
        EEMResults["OrgPropValue"] = ACH50Org
        EEMResults["NewPropValue"] = ACH50EEM
        EEMResults["InitFixedCost"] = 0
        EEMResults["UnitVarCost"] = InfilOptions.loc[InfilOptions.ACH50==ACH50EEM,["Costpersft","CostperACHsft"]].astype(float).sum(axis=1).iloc[0]
        EEMResults["Unit"] = self.FloorArea
        EEMResults["InitVarCost"] = EEMResults["UnitVarCost"]*EEMResults["Unit"]
        EEMResults["RetrofitCost"] = 0
        EEMResults["Salvage"] = 0
        EEMResults["OrgTotalElectricity"] = self.BestModelParams["OrgTotalElectricity"]
        EEMResults["OrgTotalNaturalGas"] = self.BestModelParams["OrgTotalNaturalGas"]
        EEMResults["EEMTotalElectricity"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("EL-")].sum().sum()/3.41 # Convert to kWh
        EEMResults["EEMTotalNaturalGas"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("NG-")].sum().sum()/100 # Convert to Therms
        
        
        return df_MonthlyEndUse_EEM,EEMResults
        
    def CeilingInsulation(self,ExtRoofConst,CeilConst,CeilingInsOrg,CeilingInsEEM):
        
        RoofConstOptions = pd.read_csv(os.path.join(self.MainPath,"Inputs","InputCSVData","Construction-Roof.csv"))
        RoofConstRvalue = RoofConstOptions.loc[RoofConstOptions.Construction==ExtRoofConst,"Rvalue_IP"].astype(float).iloc[0] #hr-ft2-F/Btu
        
        CeilingConstOptions = pd.read_csv(os.path.join(self.MainPath,"Inputs","InputCSVData","Construction-Floor.csv"))
        CeilingConstRvalue = CeilingConstOptions.loc[CeilingConstOptions.Construction==CeilConst,"Rvalue_IP"].astype(float).iloc[0]

        CeilingInsProp = pd.read_csv(os.path.join(self.ProjectPath,"CostData","Materials-CeilingInsulation.csv"))
        if (CeilingInsOrg != "Uninsulated") & (CeilingInsOrg != "Unknown"):
            CeilingInsRvalueOrg = CeilingInsProp.loc[CeilingInsProp.InsulationName==CeilingInsOrg,"Rvalue_IP"].astype(float).iloc[0] #hr-ft2-F/Btu
        
        if (CeilingInsEEM != "Uninsulated") & (CeilingInsEEM != "Unknown"):
            CeilingInsRvalueEEM = CeilingInsProp.loc[CeilingInsProp.InsulationName==CeilingInsEEM,"Rvalue_IP"].astype(float).iloc[0] #hr-ft2-F/Btu
        
        Delta_BLC = 0
        
        if CeilingInsOrg == "Uninsulated":
            Delta_BLC = self.FloorArea*(1/(CeilingInsRvalueEEM+CeilingConstRvalue+RoofConstRvalue) - 1/(CeilingConstRvalue+RoofConstRvalue))
            BLC_Ceil_org = self.FloorArea*(1/(CeilingConstRvalue+RoofConstRvalue))
            
        else:
            
            Delta_BLC = self.FloorArea*(1/(CeilingInsRvalueEEM+CeilingConstRvalue+RoofConstRvalue) - 1/(CeilingInsRvalueOrg+CeilingConstRvalue+RoofConstRvalue)) 
            BLC_Ceil_org = self.FloorArea*(1/(CeilingInsRvalueOrg+CeilingConstRvalue+RoofConstRvalue))
        #print("Delta BLC",Delta_BLC)
        #print(self.BestModelParams)
        f_Savings = abs(Delta_BLC)/BLC_Ceil_org # Percentage reduction in BLC of element due to insulation
        f_CeilArea = self.FloorArea/(2*self.FloorArea+sum(self.ExtWallArea.values())+sum(self.WindowArea.values())) # Percentage of ceiling area as fraction of total envelope area
        if self.BestModelParams["BLC_Heating_NG_adj"] > self.BestModelParams["BLC_Heating_EL_adj"]:
            if self.BestModelParams["BLC_Heating_NG_adj"] > abs(Delta_BLC):
                self.BestModelParams["BLC_Heating_NG_adj"] += Delta_BLC
            else:
                self.BestModelParams["BLC_Heating_NG_adj"]  = (1-f_CeilArea)*self.BestModelParams["BLC_Heating_NG_adj"] + (1-f_Savings)*f_CeilArea*self.BestModelParams["BLC_Heating_NG_adj"]
        elif self.BestModelParams["BLC_Heating_NG_adj"] < self.BestModelParams["BLC_Heating_EL_adj"]:
            if self.BestModelParams["BLC_Heating_EL_adj"] > abs(Delta_BLC):
                self.BestModelParams["BLC_Heating_EL_adj"] += Delta_BLC
            else:
                self.BestModelParams["BLC_Heating_EL_adj"]  = (1-f_CeilArea)*self.BestModelParams["BLC_Heating_EL_adj"] + (1-f_Savings)*f_CeilArea*self.BestModelParams["BLC_Heating_EL_adj"]   
        
        if self.BestModelParams["BLC_Cooling_EL_adj"] > abs(Delta_BLC):
            self.BestModelParams["BLC_Cooling_EL_adj"] += Delta_BLC
        else:
            self.BestModelParams["BLC_Cooling_EL_adj"]  = (1-f_CeilArea)*self.BestModelParams["BLC_Cooling_EL_adj"] + (1-f_Savings)*f_CeilArea*self.BestModelParams["BLC_Cooling_EL_adj"]
        
        #print(self.BestModelParams["BLC_Heating_NG_adj"],self.BestModelParams["BLC_Heating_EL_adj"],self.BestModelParams["BLC_Cooling_EL_adj"])
        
        ECMEval = True
        
        df_MonthlyEndUse_EEM = GetMonthlyEndUseBreakdown(self.BestModelParams,self.df_weather,self.df_input,ECMEval)
        
        EEMResults = {}
        EEMResults["Measure"] = "CeilingInsulation"
        EEMResults["OrgPropValue"] = CeilingInsOrg
        EEMResults["NewPropValue"] = CeilingInsEEM
        EEMResults["InitFixedCost"] = 0
        EEMResults["UnitVarCost"] = CeilingInsProp.loc[CeilingInsProp.InsulationName==CeilingInsEEM,"Costpersft"].astype(float).iloc[0]
        EEMResults["Unit"] = self.FloorArea
        EEMResults["InitVarCost"] = EEMResults["UnitVarCost"]*EEMResults["Unit"]
        EEMResults["RetrofitCost"] = 0
        EEMResults["Salvage"] = 0
        EEMResults["OrgTotalElectricity"] = self.BestModelParams["OrgTotalElectricity"]
        EEMResults["OrgTotalNaturalGas"] = self.BestModelParams["OrgTotalNaturalGas"]
        EEMResults["EEMTotalElectricity"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("EL-")].sum().sum()/3.41 # Convert to kWh
        EEMResults["EEMTotalNaturalGas"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("NG-")].sum().sum()/100 # Convert to Therms
        
        
        return df_MonthlyEndUse_EEM,EEMResults
        
    def WindowMaterial(self,WindowConstOrg,WindowConstEEM):
        
        WindowConstOptions = pd.read_csv(os.path.join(self.ProjectPath,"CostData","Materials-WindowMaterial.csv"))
        WindowConstUvalueOrg = WindowConstOptions.loc[WindowConstOptions.WindowMaterial==WindowConstOrg,"Uvalue"].astype(float).iloc[0] #hr-ft2-F/Btu
        
        WindowInsUvalueEEM = WindowConstOptions.loc[WindowConstOptions.WindowMaterial==WindowConstEEM,"Uvalue"].astype(float).iloc[0] #hr-ft2-F/Btu
        
        
        Delta_BLC = sum(self.WindowArea.values())*(WindowInsUvalueEEM - WindowConstUvalueOrg) 
        BLC_Window_org = sum(self.WindowArea.values())*(WindowConstUvalueOrg)

        f_Savings = abs(Delta_BLC)/BLC_Window_org # Percentage reduction in BLC of element due to insulation
        f_WindowArea = sum(self.WindowArea.values())/(sum(self.ExtWallArea.values())+sum(self.WindowArea.values())+2*self.FloorArea)

        if self.BestModelParams["BLC_Heating_NG_adj"] > self.BestModelParams["BLC_Heating_EL_adj"]:
            if self.BestModelParams["BLC_Heating_NG_adj"] > abs(Delta_BLC):
                self.BestModelParams["BLC_Heating_NG_adj"] += Delta_BLC
            else:
                self.BestModelParams["BLC_Heating_NG_adj"]  = (1-f_WindowArea)*self.BestModelParams["BLC_Heating_NG_adj"] + (1-f_Savings)*f_WindowArea*self.BestModelParams["BLC_Heating_NG_adj"]
        
        elif self.BestModelParams["BLC_Heating_NG_adj"] < self.BestModelParams["BLC_Heating_EL_adj"]:
            if self.BestModelParams["BLC_Heating_EL_adj"] > abs(Delta_BLC):
                self.BestModelParams["BLC_Heating_EL_adj"] += Delta_BLC
            else:
                self.BestModelParams["BLC_Heating_EL_adj"]  = (1-f_WindowArea)*self.BestModelParams["BLC_Heating_EL_adj"] + (1-f_Savings)*f_WindowArea*self.BestModelParams["BLC_Heating_EL_adj"]
        
        if self.BestModelParams["BLC_Cooling_EL_adj"] > abs(Delta_BLC):
            self.BestModelParams["BLC_Cooling_EL_adj"] += Delta_BLC
        else:
            self.BestModelParams["BLC_Cooling_EL_adj"]  = (1-f_WindowArea)*self.BestModelParams["BLC_Cooling_EL_adj"] + (1-f_Savings)*f_WindowArea*self.BestModelParams["BLC_Cooling_EL_adj"]
        
        ECMEval = True
        
        df_MonthlyEndUse_EEM = GetMonthlyEndUseBreakdown(self.BestModelParams,self.df_weather,self.df_input,ECMEval)
        
        EEMResults = {}
        EEMResults["Measure"] = "WindowMaterial"
        EEMResults["OrgPropValue"] = WindowConstOrg
        EEMResults["NewPropValue"] = WindowConstEEM
        EEMResults["InitFixedCost"] = 0
        EEMResults["UnitVarCost"] = WindowConstOptions.loc[WindowConstOptions.WindowMaterial==WindowConstEEM,"Costpersft"].astype(float).iloc[0]
        EEMResults["Unit"] = sum(self.WindowArea.values())
        EEMResults["InitVarCost"] = EEMResults["UnitVarCost"]*EEMResults["Unit"]
        EEMResults["RetrofitCost"] = 0
        EEMResults["Salvage"] = 0
        EEMResults["OrgTotalElectricity"] = self.BestModelParams["OrgTotalElectricity"]
        EEMResults["OrgTotalNaturalGas"] = self.BestModelParams["OrgTotalNaturalGas"]
        EEMResults["EEMTotalElectricity"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("EL-")].sum().sum()/3.41 # Convert to kWh
        EEMResults["EEMTotalNaturalGas"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("NG-")].sum().sum()/100 # Convert to Therms
        
        
        return df_MonthlyEndUse_EEM,EEMResults
    
    def OccupancySensor(self):
    #%% Occupancy Sensor 
    #Reference: https://www.energy.gov/femp/articles/wireless-occupancy-sensors-lighting-controls-applications-guide-federal-facility
    #percentage of space
        breakroom = 0
        classroom = .34
        conference_room = .41 
        corridor = 0
        office_private = 0
        office_open = .25
        restroom = 0
        storage_area = 0
        warehouse = 0
        
        percentage_savings = (breakroom*.29) + (classroom*.43) + (conference_room*.45) + (corridor*.55) + (office_private*.31) + (office_open*.10) + (restroom*.60) + (storage_area*.62) + (warehouse*.45)
        
        ECMEval = True
        df_MonthlyEndUse_EEM = GetMonthlyEndUseBreakdown(self.BestModelParams,self.df_weather,self.df_input,ECMEval)
        df_MonthlyEndUse_EEM["EL-Lighting"] = (1-percentage_savings)*df_MonthlyEndUse_EEM["EL-Lighting"]
        
        OccSensorOptions = pd.read_csv(os.path.join(self.ProjectPath,"CostData","Equipment-OccupancySensor.csv"))
        
        EEMResults = {}
        EEMResults["Measure"] = "OccupancySensor"
        EEMResults["OrgPropValue"] = "No"
        EEMResults["NewPropValue"] = "Yes"
        EEMResults["InitFixedCost"] = OccSensorOptions.loc[OccSensorOptions.OccupancySensor=="Yes","FixedCost"].astype(float).iloc[0]
        EEMResults["UnitVarCost"] = OccSensorOptions.loc[OccSensorOptions.OccupancySensor=="Yes","Costpersft"].astype(float).iloc[0]
        EEMResults["Unit"] = self.FloorArea
        EEMResults["InitVarCost"] = EEMResults["UnitVarCost"]*EEMResults["Unit"]
        EEMResults["RetrofitCost"] = 0
        EEMResults["Salvage"] = 0
        EEMResults["OrgTotalElectricity"] = self.BestModelParams["OrgTotalElectricity"]
        EEMResults["OrgTotalNaturalGas"] = self.BestModelParams["OrgTotalNaturalGas"]
        EEMResults["EEMTotalElectricity"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("EL-")].sum().sum()/3.41 # Convert to kWh
        EEMResults["EEMTotalNaturalGas"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("NG-")].sum().sum()/100 # Convert to Therms
        
        
        return df_MonthlyEndUse_EEM,EEMResults
    
    def ReplaceLighting(self,pct_LED,pct_LED_EEM):
        #%% Precentage LED
        # Reference: https://doi.org/10.1155/2014/745894
        
        
        percentage_change = pct_LED_EEM - pct_LED
        
        if percentage_change == 10:
            lighting_savings = 0.04
        
        elif percentage_change == 20:
            lighting_savings = 0.08
        
        elif percentage_change == 30:
            lighting_savings = 0.12
        
        elif percentage_change == 40:
            lighting_savings = 0.16
        
        elif percentage_change == 50:
            lighting_savings = 0.20
        
        elif percentage_change == 60:
            lighting_savings = 0.24
        
        elif percentage_change == 70:
            lighting_savings = 0.28
        
        elif percentage_change == 80:
            lighting_savings = 0.32
        
        elif percentage_change == 90:
            lighting_savings = 0.36
        
        elif percentage_change == 100:
            lighting_savings = 0.40
        
        else:
            lighting_savings = 0.0

        ECMEval = True
        df_MonthlyEndUse_EEM = GetMonthlyEndUseBreakdown(self.BestModelParams,self.df_weather,self.df_input,ECMEval)
        #print("Lighting Original", df_MonthlyEndUse_EEM["EL-Lighting"])
        df_MonthlyEndUse_EEM["EL-Lighting"] = (1-lighting_savings)*df_MonthlyEndUse_EEM["EL-Lighting"]
        #print("Lighting New", df_MonthlyEndUse_EEM["EL-Lighting"])
        
        LEDOptions = pd.read_csv(os.path.join(self.ProjectPath,"CostData","Equipment-LED.csv"))

        # Snap percentage_change to the nearest available row in the CSV
        nearest_idx = (LEDOptions["PercentageLED"] - percentage_change).abs().idxmin()

        EEMResults = {}
        EEMResults["Measure"] = "LEDLighting"
        EEMResults["OrgPropValue"] = pct_LED
        EEMResults["NewPropValue"] = pct_LED_EEM
        EEMResults["InitFixedCost"] = float(LEDOptions.loc[nearest_idx, "FixedCost"])
        EEMResults["UnitVarCost"] = float(LEDOptions.loc[nearest_idx, "Costpersft"])
        EEMResults["Unit"] = self.FloorArea
        EEMResults["InitVarCost"] = EEMResults["UnitVarCost"]*EEMResults["Unit"]
        EEMResults["RetrofitCost"] = 0
        EEMResults["Salvage"] = 0
        EEMResults["OrgTotalElectricity"] = self.BestModelParams["OrgTotalElectricity"]
        print("Original Electricity", EEMResults["OrgTotalElectricity"])
        EEMResults["OrgTotalNaturalGas"] = self.BestModelParams["OrgTotalNaturalGas"]
        EEMResults["EEMTotalElectricity"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("EL-")].sum().sum()/3.41 # Convert to kWh
        print("EEMTotalElectricity", EEMResults["EEMTotalElectricity"])
        EEMResults["EEMTotalNaturalGas"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("NG-")].sum().sum()/100 # Convert to Therms
        
        
        return df_MonthlyEndUse_EEM,EEMResults
    
    def DaylightingSensor(self):
            #%% Daylighting
        #Reference: https://www.aceee.org/files/proceedings/2006/data/papers/SS06_Panel3_Paper19.pdf
        
        daylight_savings = .32
        
        ECMEval = True
        df_MonthlyEndUse_EEM = GetMonthlyEndUseBreakdown(self.BestModelParams,self.df_weather,self.df_input,ECMEval)
        df_MonthlyEndUse_EEM["EL-Lighting"] = (1-daylight_savings)*df_MonthlyEndUse_EEM["EL-Lighting"]
        
        DayLtOccSensorOptions = pd.read_csv(os.path.join(self.ProjectPath,"CostData","Equipment-Daylighting.csv"))
        
        EEMResults = {}
        EEMResults["Measure"] = "DaylightingSensor"
        EEMResults["OrgPropValue"] = "No"
        EEMResults["NewPropValue"] = "Yes"
        EEMResults["InitFixedCost"] = DayLtOccSensorOptions.loc[DayLtOccSensorOptions.Daylighting=="Yes","FixedCost"].astype(float).iloc[0]
        EEMResults["UnitVarCost"] = DayLtOccSensorOptions.loc[DayLtOccSensorOptions.Daylighting=="Yes","Costpersft"].astype(float).iloc[0]
        EEMResults["Unit"] = self.FloorArea
        EEMResults["InitVarCost"] = EEMResults["UnitVarCost"]*EEMResults["Unit"]
        EEMResults["RetrofitCost"] = 0
        EEMResults["Salvage"] = 0
        EEMResults["OrgTotalElectricity"] = self.BestModelParams["OrgTotalElectricity"]
        EEMResults["OrgTotalNaturalGas"] = self.BestModelParams["OrgTotalNaturalGas"]
        EEMResults["EEMTotalElectricity"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("EL-")].sum().sum()/3.41 # Convert to kWh
        EEMResults["EEMTotalNaturalGas"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("NG-")].sum().sum()/100 # Convert to Therms
        
        
        return df_MonthlyEndUse_EEM,EEMResults
    
    def Economizer(self,bldg_address):
        #%% Economizer
        #Reference: https://www.nrel.gov/docs/fy24osti/86105.pdf
        
        import re
        g = geocoder.arcgis(bldg_address)
        if g.ok and "address" in g.json:
            address = g.json['address']  # Extract the state name
            state_pattern = r'\b(A[LKZR]|C[AOT]|D[EC]|F[LM]|G[AU]|H[I]|I[DLN]|K[SY]|L[A]|M[ADEINSOT]|N[CDEHJMVY]|O[HKR]|P[A]|R[I]|S[CD]|T[NX]|U[T]|V[AIT]|W[AIVY])\b|\b(?:Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming)\b'    
            match = re.search(state_pattern, address)
            state = match.group(0) 
        else:
            state = None
        
        if state == "Colorado":
            economizer_savings = .069
        elif state == "Utha":
            economizer_savings = .050
        elif state == "Wyoming":
            economizer_savings = .094
        elif state == "Idaho":
            economizer_savings = .091
        elif state == "Montana":
            economizer_savings = .108
        elif state  == None:
            economizer_savings = None    
            
        
        ECMEval = True
        df_MonthlyEndUse_EEM = GetMonthlyEndUseBreakdown(self.BestModelParams,self.df_weather,self.df_input,ECMEval)
        df_MonthlyEndUse_EEM.loc["EL-Space Cooling"] = (1-economizer_savings)*df_MonthlyEndUse_EEM.loc["EL-Space Cooling"]
        
        EconOptions = pd.read_csv(os.path.join(self.ProjectPath,"CostData","System-Economizer.csv"))
        
        EEMResults = {}
        EEMResults["Measure"] = "Economizer"
        EEMResults["OrgPropValue"] = "No"
        EEMResults["NewPropValue"] = "Yes"
        EEMResults["InitFixedCost"] = EconOptions.loc[EconOptions.Economizer=="Yes","FixedCost"].astype(float).iloc[0]
        EEMResults["UnitVarCost"] = EconOptions.loc[EconOptions.Economizer=="Yes","Costpersft"].astype(float).iloc[0]
        EEMResults["Unit"] = self.FloorArea
        EEMResults["InitVarCost"] = EEMResults["UnitVarCost"]*EEMResults["Unit"]
        EEMResults["RetrofitCost"] = 0
        EEMResults["Salvage"] = 0
        EEMResults["OrgTotalElectricity"] = self.BestModelParams["OrgTotalElectricity"]
        EEMResults["OrgTotalNaturalGas"] = self.BestModelParams["OrgTotalNaturalGas"]
        EEMResults["EEMTotalElectricity"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("EL-")].sum().sum()/3.41 # Convert to kWh
        EEMResults["EEMTotalNaturalGas"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("NG-")].sum().sum()/100 # Convert to Therms
        
        
        return df_MonthlyEndUse_EEM,EEMResults
    
    #%% Reduce Equipment Load
    def ReduceEquipmentLoad(self,EquipLoadRed):
        
        
        ECMEval = True
        df_MonthlyEndUse_EEM = GetMonthlyEndUseBreakdown(self.BestModelParams,self.df_weather,self.df_input,ECMEval)
        df_MonthlyEndUse_EEM["EL-Electric Equipment"] = (1-(EquipLoadRed/100))*df_MonthlyEndUse_EEM["EL-Electric Equipment"]
           
        EEMResults = {}
        EEMResults["Measure"] = "ReduceEquipmentLoad"
        EEMResults["OrgPropValue"] = 0
        EEMResults["NewPropValue"] = EquipLoadRed
        EEMResults["InitFixedCost"] = 0
        EEMResults["UnitVarCost"] = 0
        EEMResults["Unit"] = self.FloorArea
        EEMResults["InitVarCost"] = EEMResults["UnitVarCost"]*EEMResults["Unit"]
        EEMResults["RetrofitCost"] = 0
        EEMResults["Salvage"] = 0
        EEMResults["OrgTotalElectricity"] = self.BestModelParams["OrgTotalElectricity"]
        EEMResults["OrgTotalNaturalGas"] = self.BestModelParams["OrgTotalNaturalGas"]
        EEMResults["EEMTotalElectricity"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("EL-")].sum().sum()/3.41 # Convert to kWh
        EEMResults["EEMTotalNaturalGas"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("NG-")].sum().sum()/100 # Convert to Therms
        
        
        return df_MonthlyEndUse_EEM,EEMResults
    
    #%% NightSetBack
    def NightSetBack(self,temp_org,hour_org,temp_eem,hour_eem):
        
        
        ECMEval = True
        df_MonthlyEndUse_EEM = GetMonthlyEndUseBreakdown(self.BestModelParams,self.df_weather,self.df_input,ECMEval)
                  
        EEMResults = {}
        EEMResults["Measure"] = "NightSetBack"
        EEMResults["OrgPropValue"] = f"{temp_org} and {hour_org}"
        EEMResults["NewPropValue"] = f"{temp_eem} and {hour_eem}"
        EEMResults["InitFixedCost"] = 0
        EEMResults["UnitVarCost"] = 0
        EEMResults["Unit"] = self.FloorArea
        EEMResults["InitVarCost"] = EEMResults["UnitVarCost"]*EEMResults["Unit"]
        EEMResults["RetrofitCost"] = 0
        EEMResults["Salvage"] = 0
        EEMResults["OrgTotalElectricity"] = self.BestModelParams["OrgTotalElectricity"]
        EEMResults["OrgTotalNaturalGas"] = self.BestModelParams["OrgTotalNaturalGas"]
        EEMResults["EEMTotalElectricity"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("EL-")].sum().sum()/3.41 # Convert to kWh
        EEMResults["EEMTotalNaturalGas"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("NG-")].sum().sum()/100 # Convert to Therms
        
        
        return df_MonthlyEndUse_EEM,EEMResults
    
    #%% Cooling Eff
    def CoolingEff(self,CoolingEqp,CoolingEffOrg,CoolingEffEEM):
        
        
        ECMEval = True
        df_MonthlyEndUse_EEM = GetMonthlyEndUseBreakdown(self.BestModelParams,self.df_weather,self.df_input,ECMEval)
        
        CoolingEffOptions = pd.read_csv(os.path.join(self.ProjectPath,"CostData","System-"+CoolingEqp+".csv"))
               
        EEMResults = {}
        EEMResults["Measure"] = "CoolingEff"
        EEMResults["OrgPropValue"] = CoolingEffOrg
        EEMResults["NewPropValue"] = CoolingEffEEM
        EEMResults["InitFixedCost"] = CoolingEffOptions.loc[CoolingEffOptions.SEER.astype(float)==CoolingEffEEM,"Costperunit"].astype(float).iloc[0]
        EEMResults["UnitVarCost"] = CoolingEffOptions.loc[CoolingEffOptions.SEER.astype(float)==CoolingEffEEM,"CostperkBtuh"].astype(float).iloc[0]
        EEMResults["Unit"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("Space Cooling")].sum().sum()/(365*24) #from monthly kBtu to kBtuh
        EEMResults["InitVarCost"] = EEMResults["UnitVarCost"]*EEMResults["Unit"]
        EEMResults["RetrofitCost"] = 0
        EEMResults["Salvage"] = 0
        EEMResults["OrgTotalElectricity"] = self.BestModelParams["OrgTotalElectricity"]
        EEMResults["OrgTotalNaturalGas"] = self.BestModelParams["OrgTotalNaturalGas"]
        EEMResults["EEMTotalElectricity"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("EL-")].sum().sum()/3.41 # Convert to kWh
        EEMResults["EEMTotalNaturalGas"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("NG-")].sum().sum()/100 # Convert to Therms
        
        
        return df_MonthlyEndUse_EEM,EEMResults
    
    
    
    def HeatingEff(self,HeatingEqp,HeatingEffOrg,HeatingEffEEM):
        # Change this so that it takes the BLC adj value if it already exists
        # If not then the adj value is the same as the original value
        
        ECMEval = True
        df_MonthlyEndUse_EEM = GetMonthlyEndUseBreakdown(self.BestModelParams,self.df_weather,self.df_input,ECMEval)
        
        HeatingEffOptions = pd.read_csv(os.path.join(self.ProjectPath,"CostData","System-"+HeatingEqp+".csv"))
               
        EEMResults = {}
        EEMResults["Measure"] = "HeatingEff"
        EEMResults["OrgPropValue"] = HeatingEffOrg
        EEMResults["NewPropValue"] = HeatingEffEEM
        EEMResults["InitFixedCost"] = HeatingEffOptions.loc[HeatingEffOptions.HeatingEff.astype(float)==HeatingEffEEM,"Costperunit"].astype(float).iloc[0]
        EEMResults["UnitVarCost"] = HeatingEffOptions.loc[HeatingEffOptions.HeatingEff.astype(float)==HeatingEffEEM,"CostperkBtuh"].astype(float).iloc[0]
        EEMResults["Unit"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("Space Heating")].sum().sum()/(365*24) #from monthly kBtu to kBtuh
        EEMResults["InitVarCost"] = EEMResults["UnitVarCost"]*EEMResults["Unit"]
        EEMResults["RetrofitCost"] = 0
        EEMResults["Salvage"] = 0
        EEMResults["OrgTotalElectricity"] = self.BestModelParams["OrgTotalElectricity"]
        EEMResults["OrgTotalNaturalGas"] = self.BestModelParams["OrgTotalNaturalGas"]
        EEMResults["EEMTotalElectricity"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("EL-")].sum().sum()/3.41 # Convert to kWh
        EEMResults["EEMTotalNaturalGas"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("NG-")].sum().sum()/100 # Convert to Therms
        
        
        return df_MonthlyEndUse_EEM,EEMResults
    
    #%% Heat Pump Addition
    def HeatPumpAddition(self,CoolingEffOrg,CoolingEffEEM,HeatingEffOrg,HeatingEffEEM):
        
        
        ECMEval = True
        df_MonthlyEndUse_EEM = GetMonthlyEndUseBreakdown(self.BestModelParams,self.df_weather,self.df_input,ECMEval)
        

        HeatPumpOptions = pd.read_csv(os.path.join(self.ProjectPath,"CostData","System-"+"AirSourceHeatPump"+".csv"))
        Eff_Org = "HSPF"+str(HeatingEffOrg)+"-SEER"+str(CoolingEffOrg)
        Eff_EEM = "HSPF"+str(HeatingEffEEM)+"-SEER"+str(CoolingEffEEM)

        HeatCap = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("Space Heating")].sum().sum()/(365*24)
        CoolCap = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("Space Cooling")].sum()/(365*24)

        EEMResults = {}
        EEMResults["Measure"] = "HeatPumpAddition"
        EEMResults["OrgPropValue"] = Eff_Org
        EEMResults["NewPropValue"] = Eff_EEM
        EEMResults["InitFixedCost"] = HeatPumpOptions.loc[HeatPumpOptions.EffName==Eff_EEM,"Costperunit"].astype(float).iloc[0]
        EEMResults["UnitVarCost"] = HeatPumpOptions.loc[HeatPumpOptions.EffName==Eff_EEM,"CostperkBtuh"].astype(float).iloc[0]
        EEMResults["Unit"] = max(HeatCap,CoolCap) #from monthly kBtu to kBtuh
        EEMResults["InitVarCost"] = EEMResults["UnitVarCost"]*EEMResults["Unit"]
        EEMResults["RetrofitCost"] = 0
        EEMResults["Salvage"] = 0
        EEMResults["OrgTotalElectricity"] = self.BestModelParams["OrgTotalElectricity"]
        EEMResults["OrgTotalNaturalGas"] = self.BestModelParams["OrgTotalNaturalGas"]
        EEMResults["EEMTotalElectricity"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("EL-")].sum().sum()/3.41 # Convert to kWh
        EEMResults["EEMTotalNaturalGas"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("NG-")].sum().sum()/100 # Convert to Therms
        
        
        return df_MonthlyEndUse_EEM,EEMResults
