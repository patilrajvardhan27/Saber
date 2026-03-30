import pandas as pd
import geocoder
import numpy 
import matplotlib.pyplot as plt
import os
# from AnalyzeUtilityData import *
# from PostProcessing import *
# from EEMIndMeasureAnalysisObject import *


from .AnalyzeUtilityData import *
from .PostProcessing import *
from .EEMIndMeasureAnalysisObject import *




def MeasurePackageAnalysis(Measures,df_MonthlyEndUse,BestModelParams,CostData,MainPath,ProjectPath,df_weather):
    df_input_org = pd.read_pickle(ProjectPath+"/BldgPropInputFile-Baseline.pkl")
    df_input_EEM = pd.read_pickle(ProjectPath+"/BldgPropInputsFile.pkl")
    EvalMeasure = EvaluateMeasure(df_input_EEM,df_weather, MainPath, ProjectPath, BestModelParams)
    dfMeasure = pd.DataFrame()
    
    NonEndUseCols = ['BLC_Heat_NG', 'BLC_Heat_EL', 'BLC_Cool_EL', 'HDD_EL', 'HDD_NG', 'CDD','AL-Space Heating']
    dfSavings = df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(NonEndUseCols)].copy()
    #print(dfSavings["EL-Space Cooling"])

    if Measures["WallInsChange"]:
        ExtWallConst = df_input_org.loc[df_input_org.PropKey == "ExtWallConst"].PropValue.item()
        WallInsOrg = df_input_org.loc[df_input_org.PropKey == "R-WallInsulation"].PropValue.item()
        WallInsEEM = df_input_EEM.loc[df_input_EEM.PropKey == "R-WallInsulation"].PropValue.item()
        
        df_MonthlyEndUse_EEM,EEMResults = EvalMeasure.WallInsulation(ExtWallConst, WallInsOrg, WallInsEEM)
        dfMeasure = pd.concat([dfMeasure,pd.DataFrame([EEMResults])],ignore_index=True)
        
        # print(df_MonthlyEndUse["EL-Space Heating"] - df_MonthlyEndUse_EEM["EL-Space Heating"])
        dfSavings = dfSavings - (df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(NonEndUseCols)] - df_MonthlyEndUse_EEM.loc[:,~df_MonthlyEndUse_EEM.columns.isin(NonEndUseCols)])
        #print(dfSavings["EL-Space Cooling"])

    if Measures["InfilChange"]:
        ACH50Org = df_input_org.loc[df_input_org.PropKey == "ACH50"].PropValue.astype(float).iloc[0]
        ACH50EEM = df_input_EEM.loc[df_input_org.PropKey == "ACH50"].PropValue.astype(float).iloc[0]
        
        df_MonthlyEndUse_EEM,EEMResults = EvalMeasure.Infiltration(ACH50Org, ACH50EEM)
        dfMeasure = pd.concat([dfMeasure,pd.DataFrame([EEMResults])],ignore_index=True)
        dfSavings = dfSavings - (df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(NonEndUseCols)] - df_MonthlyEndUse_EEM.loc[:,~df_MonthlyEndUse_EEM.columns.isin(NonEndUseCols)])
    
    if Measures["CeilInsChange"]:
        ExtRoofConst = df_input_org.loc[df_input_org.PropKey == "ExtRoofConst"].PropValue.item()
        CeilConst = df_input_org.loc[df_input_org.PropKey == "CeilingConst"].PropValue.item()
        CeilInsOrg = df_input_org.loc[df_input_org.PropKey == "R-CeilingInsulation"].PropValue.item()
        CeilInsEEM = df_input_EEM.loc[df_input_EEM.PropKey == "R-CeilingInsulation"].PropValue.item()
        
        df_MonthlyEndUse_EEM,EEMResults = EvalMeasure.CeilingInsulation(ExtRoofConst,CeilConst, CeilInsOrg, CeilInsEEM)
        dfMeasure = pd.concat([dfMeasure,pd.DataFrame([EEMResults])],ignore_index=True)
        dfSavings = dfSavings - (df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(NonEndUseCols)] - df_MonthlyEndUse_EEM.loc[:,~df_MonthlyEndUse_EEM.columns.isin(NonEndUseCols)])
        #print(dfSavings["EL-Space Cooling"])

    if Measures["WindowMatChange"]:
        WindowConstOrg = df_input_org.loc[df_input_org.PropKey == "WindowMaterial"].PropValue.item()
        WindowConstEEM = df_input_EEM.loc[df_input_EEM.PropKey == "WindowMaterial"].PropValue.item()
        
        df_MonthlyEndUse_EEM,EEMResults = EvalMeasure.WindowMaterial(WindowConstOrg,WindowConstEEM)
        dfMeasure = pd.concat([dfMeasure,pd.DataFrame([EEMResults])],ignore_index=True)
        dfSavings = dfSavings - (df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(NonEndUseCols)] - df_MonthlyEndUse_EEM.loc[:,~df_MonthlyEndUse_EEM.columns.isin(NonEndUseCols)])
    
    if Measures["OccupancySensorChange"]:
        df_MonthlyEndUse_EEM,EEMResults = EvalMeasure.OccupancySensor()
        dfMeasure = pd.concat([dfMeasure,pd.DataFrame([EEMResults])],ignore_index=True)
        dfSavings = dfSavings - (df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(NonEndUseCols)] - df_MonthlyEndUse_EEM.loc[:,~df_MonthlyEndUse_EEM.columns.isin(NonEndUseCols)])
    
    if Measures["LEDChange"]:
        pct_LED = df_input_org.loc[df_input_org.PropKey == "LEDCurrent"].PropValue.astype(float).iloc[0]
        pct_LED_EEM = df_input_EEM.loc[df_input_EEM.PropKey == "LEDECM"].PropValue.astype(float).iloc[0]
        
        df_MonthlyEndUse_EEM,EEMResults = EvalMeasure.ReplaceLighting(pct_LED,pct_LED_EEM)
        dfMeasure = pd.concat([dfMeasure,pd.DataFrame([EEMResults])],ignore_index=True)
        dfSavings = dfSavings - (df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(NonEndUseCols)] - df_MonthlyEndUse_EEM.loc[:,~df_MonthlyEndUse_EEM.columns.isin(NonEndUseCols)])
    
    if Measures["DaylightingChange"]:
        df_MonthlyEndUse_EEM,EEMResults = EvalMeasure.DaylightingSensor()
        dfMeasure = pd.concat([dfMeasure,pd.DataFrame([EEMResults])],ignore_index=True)
        dfSavings = dfSavings - (df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(NonEndUseCols)] - df_MonthlyEndUse_EEM.loc[:,~df_MonthlyEndUse_EEM.columns.isin(NonEndUseCols)])
    
    if Measures["EconomizerChange"]:
        bldg_address = df_input_org.loc[df_input_org.PropKey == "Location"].PropValue.item()
        df_MonthlyEndUse_EEM,EEMResults = EvalMeasure.Economizer(bldg_address)
        dfMeasure = pd.concat([dfMeasure,pd.DataFrame([EEMResults])],ignore_index=True)
        dfSavings = dfSavings - (df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(NonEndUseCols)] - df_MonthlyEndUse_EEM.loc[:,~df_MonthlyEndUse_EEM.columns.isin(NonEndUseCols)])
    
    if Measures["ReduceEquipmentLoadChange"]:
        ReduceEquipmentLoadEEM = df_input_EEM.loc[df_input_EEM.PropKey == "EquipLoadRed"].PropValue.item()
        df_MonthlyEndUse_EEM,EEMResults = EvalMeasure.ReduceEquipmentLoad(ReduceEquipmentLoadEEM)
        dfMeasure = pd.concat([dfMeasure,pd.DataFrame([EEMResults])],ignore_index=True)
        dfSavings = dfSavings - (df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(NonEndUseCols)] - df_MonthlyEndUse_EEM.loc[:,~df_MonthlyEndUse_EEM.columns.isin(NonEndUseCols)])
        
    if Measures["HoursofNightSetbackChange"] or Measures["NightSetbackChange"]:
        
        NightSetBackOrg = df_input_org.loc[df_input_org.PropKey == "NightSetback"].PropValue.item()
        NightSetBackEEM = df_input_EEM.loc[df_input_EEM.PropKey == "NightSetback"].PropValue.item()

        HoursofNightSetBackOrg = df_input_org.loc[df_input_org.PropKey == "nNightSetbackHours"].PropValue.item()
        HoursofNightSetBackEEM = df_input_EEM.loc[df_input_EEM.PropKey == "nNightSetbackHours"].PropValue.item()

        df_MonthlyEndUse_EEM,EEMResults = EvalMeasure.NightSetBack(NightSetBackOrg, HoursofNightSetBackOrg,NightSetBackEEM, HoursofNightSetBackEEM)

        dfMeasure = pd.concat([dfMeasure,pd.DataFrame([EEMResults])],ignore_index=True)
        dfSavings = dfSavings - (df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(NonEndUseCols)] - df_MonthlyEndUse_EEM.loc[:,~df_MonthlyEndUse_EEM.columns.isin(NonEndUseCols)])
        #print(dfSavings["EL-Space Cooling"])
    if Measures["CoolingEffChange"]:
        
        CoolingEqp = df_input_EEM.loc[df_input_EEM.PropKey == "CoolingEquipment"].PropValue.item().replace(" ","")
        if df_input_org.loc[df_input_org.PropKey == "CoolingEff"].PropValue.item() == "Other..":
            CoolingEffOrg = df_input_org.loc[df_input_org.PropKey == "CoolingEffCustom"].PropValue.astype(float).iloc[0]
        else:
            CoolingEffOrg = df_input_org.loc[df_input_org.PropKey == "CoolingEff"].PropValue.astype(float).iloc[0]
        CoolingEffEEM = df_input_EEM.loc[df_input_EEM.PropKey == "CoolingEff"].PropValue.astype(float).iloc[0]
        #print(CoolingEqp,CoolingEffOrg,CoolingEffEEM)

        df_MonthlyEndUse_EEM,EEMResults = EvalMeasure.CoolingEff(CoolingEqp,CoolingEffOrg, CoolingEffEEM)

        dfMeasure = pd.concat([dfMeasure,pd.DataFrame([EEMResults])],ignore_index=True)
        dfSavings -=( df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(NonEndUseCols)] - df_MonthlyEndUse_EEM.loc[:,~df_MonthlyEndUse_EEM.columns.isin(NonEndUseCols)])
        #print(dfMeasure)
    if Measures["HeatingEffChange"]:
        
        HeatingEqp = df_input_EEM.loc[df_input_EEM.PropKey == "HeatingEquipment"].PropValue.item().replace(" ","")
        if df_input_org.loc[df_input_org.PropKey == "HeatingEff"].PropValue.item() == "Other..":
            HeatingEffOrg = df_input_org.loc[df_input_org.PropKey == "HeatingEffCustom"].PropValue.astype(float).iloc[0]
        else:
            HeatingEffOrg = df_input_org.loc[df_input_org.PropKey == "HeatingEff"].PropValue.astype(float).iloc[0]
        HeatingEffEEM = df_input_EEM.loc[df_input_EEM.PropKey == "HeatingEff"].PropValue.astype(float).iloc[0]
        #print(HeatingEqp,HeatingEffOrg,HeatingEffEEM)
        df_MonthlyEndUse_EEM,EEMResults = EvalMeasure.HeatingEff(HeatingEqp,HeatingEffOrg, HeatingEffEEM)

        dfMeasure = pd.concat([dfMeasure,pd.DataFrame([EEMResults])],ignore_index=True)
        dfSavings = dfSavings - (df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(NonEndUseCols)] - df_MonthlyEndUse_EEM.loc[:,~df_MonthlyEndUse_EEM.columns.isin(NonEndUseCols)])
        
    # if Measures["Heating"]:
    #         CoolingEffOrg = df_input_org.loc[df_input_org.PropKey == "CoolingEff"].PropValue.astype(float).iloc[0]
    #         CoolingEffEEM = df_input_EEM.loc[df_input_EEM.PropKey == "CoolingEff"].PropValue.astype(float).iloc[0]
    #         HeatingEffOrg = df_input_org.loc[df_input_org.PropKey == "HeatingEff"].PropValue.astype(float).iloc[0]
    #         HeatingEffEEM = df_input_EEM.loc[df_input_EEM.PropKey == "HeatingEff"].PropValue.astype(float).iloc[0]
    
    #         df_MonthlyEndUse_EEM,EEMResults = EvalMeasure.HeatPumpAddition(CoolingEffOrg, CoolingEffEEM,HeatingEffOrg, HeatingEffEEM)
    
    #         dfMeasure = pd.concat([dfMeasure,pd.DataFrame([EEMResults])],ignore_index=True)
    #         dfSavings -= df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(NonEndUseCols)] - df_MonthlyEndUse_EEM.loc[:,~df_MonthlyEndUse_EEM.columns.isin(NonEndUseCols)]

    #print(dfSavings["EL-Space Cooling"])
    print(dfMeasure)
    #print("df_saving package measure", dfSavings)
    CumEEMResults = {}
    CumEEMResults["Measures"] = dfMeasure["Measure"].values.tolist()
    CumEEMResults["OrgPropValue"] = dfMeasure["OrgPropValue"].values.tolist()
    CumEEMResults["NewPropValue"] = dfMeasure["NewPropValue"].values.tolist()
    CumEEMResults["TIC"] = dfMeasure["InitFixedCost"].sum() + dfMeasure["InitVarCost"].sum()
    CumEEMResults["OrgTotalkWh"] = df_MonthlyEndUse.loc[:,df_MonthlyEndUse.columns.str.contains("EL-")].sum().sum()/3.41 # Convert to kWh
    CumEEMResults["OrgTotalTherm"] =df_MonthlyEndUse.loc[:,df_MonthlyEndUse.columns.str.contains("NG-")].sum().sum()/100 # Convert to Therms
    #print("Sum of EL", dfSavings.loc[:,dfSavings.columns.str.contains("EL")].sum().sum()/3.41)
    CumEEMResults["EEMTotalkWh"] = dfSavings.loc[:,dfSavings.columns.str.contains("EL-")].sum().sum()/3.41 # Convert to kWh
    CumEEMResults["EEMTotalTherm"] =dfSavings.loc[:,dfSavings.columns.str.contains("NG-")].sum().sum()/100 # Convert to Therms
    CumEEMResults["PctkWhSavings"] = 100*(CumEEMResults["OrgTotalkWh"] - CumEEMResults["EEMTotalkWh"])/CumEEMResults["OrgTotalkWh"] 
    if CumEEMResults["OrgTotalTherm"] == 0:
        CumEEMResults["PctThermSavings"] = np.nan
    else:
        CumEEMResults["PctThermSavings"] = 100*(CumEEMResults["OrgTotalTherm"] - CumEEMResults["EEMTotalTherm"])/CumEEMResults["OrgTotalTherm"]
    CumEEMResults["OrgAOC"] = CostData["kWhRate"]*CumEEMResults["OrgTotalkWh"] + CostData["ThermRate"]*CumEEMResults["OrgTotalTherm"]
    CumEEMResults["EEMAOC"] = CostData["kWhRate"]*CumEEMResults["EEMTotalkWh"] + CostData["ThermRate"]*CumEEMResults["EEMTotalTherm"]
    CumEEMResults["OrgTOC"] = CostData["USPW"]*CumEEMResults["OrgAOC"]
    CumEEMResults["EEMTOC"] = CostData["USPW"]*CumEEMResults["EEMAOC"]
    CumEEMResults["EEMLCC"] = CumEEMResults["TIC"] + CumEEMResults["EEMTOC"]
    # print(dfSavings)
    PltRes = PlotResults(True, ProjectPath)
    PltRes.PlotEndUseBreakdown(dfSavings)
    PltRes.PlotEEMEndUseComparison(df_MonthlyEndUse,dfSavings)

    return CumEEMResults
