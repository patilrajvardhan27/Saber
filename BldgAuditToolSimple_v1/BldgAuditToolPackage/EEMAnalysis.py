import pandas as pd
import geocoder
import numpy 
import matplotlib.pyplot as plt
import os
#from AnalyzeUtilityData import *
from AnalyzeUtilityData import *
from PostProcessing import *
from EEMIndMeasureAnalysisObject import *

#%%
MainPath = "C:\\Users\\phani\\OneDrive - UCB-O365\\Phani_Vadali\\Work\\EnergyModels\\BuildingAuditTool\\BldgAuditToolSimple_v1"
ProjectPath = MainPath + "\\Projects\\Grace United Methodist Church"
ProjectName = "Grace United Methodist Church"#"ChurchTestCase"#
df_input_org = pd.read_pickle(ProjectPath+"/BldgPropInputFile-Baseline.pkl")
df_input_EEM = pd.read_pickle(ProjectPath+"/BldgPropInputsFile.pkl")

df_input_org.loc[68,"PropValue"] = 0
# df_input_org.loc[40,"PropValue"] = 5
# df_input_org.loc[28,"PropValue"] = "Uninsulated"
# df_input_EEM.loc[37,"PropValue"] = "Low e Double Pane Medium SHGC Argon filled"
# df_input_EEM.loc[72,"PropValue"] = 100

# df_input_org = pd.concat([
#     df_input_org,
#     pd.DataFrame({"PropKey": ["nNightSetbackHours", "nHoursLighting"], "PropValue": [0, 6]})
# ], ignore_index=True)
# df_input_EEM = pd.concat([
#     df_input_EEM,
#     pd.DataFrame({"PropKey": ["nNightSetbackHours", "nHoursLighting"], "PropValue": [0, 6]})
# ], ignore_index=True)

# df_input_org.to_pickle(ProjectPath+"/BldgPropInputFile-Baseline.pkl")
# df_input_EEM.to_pickle(ProjectPath+"/BldgPropInputsFile.pkl")

bldg_location="Lakewood CO"

CostData = {}
CostData["kWhRate"] = 0.1433
CostData["ThermRate"] = 0.944
CostData["DiscountRate"] = 5
CostData["Lifetime"] = 15
CostData["USPW"] = (1-(1+CostData["DiscountRate"])**(-CostData["Lifetime"]))/CostData["DiscountRate"]

df_weather,weather_station_name = GetWeather(ProjectPath,ProjectName,bldg_location)

#%% BUILD CHANGE POINT MODEL USING TEMPERATUER AND DEGREE DAY BASED METHODS
CPT = BuildChangePointModel(ProjectPath,ProjectName,df_input_org,df_weather)
model_type_cooling, model_parameters_cooling,  model_type_heating, model_parameters_heating = CPT.BuildTemperatureBasedModel()
print(model_type_cooling, model_parameters_cooling,  model_type_heating, model_parameters_heating)
DDResults,dfutilDataSorted = CPT.BuildDegreeDayBasedModel(model_type_cooling, model_parameters_cooling,  model_type_heating, model_parameters_heating)


df_MonthlyEndUse = GetMonthlyEndUseBreakdown(DDResults,df_weather,df_input_org,False)
DDResults["OrgTotalElectricity"] = df_MonthlyEndUse.loc[:,df_MonthlyEndUse.columns.str.contains("EL")].sum().sum()/3.41 # Convert to kWh
DDResults["OrgTotalNaturalGas"] = df_MonthlyEndUse.loc[:,df_MonthlyEndUse.columns.str.contains("NG")].sum().sum()/100 # Convert to Therms
DDResults["BLC_Heat_EL"] = df_MonthlyEndUse["BLC_Heat_EL"].mean()
DDResults["BLC_Heat_NG"] = df_MonthlyEndUse["BLC_Heat_NG"].mean()

DDResults["BLC_Cool_EL"] = df_MonthlyEndUse["BLC_Cool_EL"].mean()

#%% PLOT END USE BREAKDOWN AND MODEL COMPARISON 
PltRes = PlotResults(True,ProjectPath)
PltRes.PlotEndUseBreakdown(df_MonthlyEndUse)
PltRes.PlotInverseModelComparison(df_MonthlyEndUse, dfutilDataSorted)

#%%  
WallInsulationMeasure = 0
InfiltrationMeasure = 0
CeilInsulationMeasure = 0
WindowMaterialMeasure = 0
OccupancySensorMeasure = 0
ReplaceLightingMeasure = 0
DaylightingMeasure = 0
EconomizerMeasure = 0

EvalMeasure = EvaluateMeasure(df_input_EEM,df_weather, MainPath, ProjectPath, DDResults)
dfMeasure = pd.DataFrame()
dfSavings = df_MonthlyEndUse.copy()
NonEndUseCols = ['BLC_Heat_NG', 'BLC_Heat_EL', 'BLC_Cool_EL', 'HDD_EL', 'HDD_NG', 'CDD','AL-Space Heating']

if WallInsulationMeasure:
    ExtWallConst = df_input_org.loc[df_input_org.PropKey == "ExtWallConst"].PropValue.item()
    WallInsOrg = df_input_org.loc[df_input_org.PropKey == "R-WallInsulation"].PropValue.item()
    WallInsEEM = df_input_EEM.loc[df_input_EEM.PropKey == "R-WallInsulation"].PropValue.item()
    
    df_MonthlyEndUse_EEM,EEMResults = EvalMeasure.WallInsulation(ExtWallConst, WallInsOrg, WallInsEEM)
    dfMeasure = pd.concat([dfMeasure,pd.DataFrame([EEMResults])],ignore_index=True)
    
    dfSavings -= df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(NonEndUseCols)] - df_MonthlyEndUse_EEM.loc[:,~df_MonthlyEndUse_EEM.columns.isin(NonEndUseCols)]

if InfiltrationMeasure:
    ACH50Org = df_input_org.loc[df_input_org.PropKey == "ACH50"].PropValue.astype(float).iloc[0]
    ACH50EEM = df_input_EEM.loc[df_input_org.PropKey == "ACH50"].PropValue.astype(float).iloc[0]
    
    df_MonthlyEndUse_EEM,EEMResults = EvalMeasure.Infiltration(ACH50Org, ACH50EEM)
    dfMeasure = pd.concat([dfMeasure,pd.DataFrame([EEMResults])],ignore_index=True)
    dfSavings -= df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(NonEndUseCols)] - df_MonthlyEndUse_EEM.loc[:,~df_MonthlyEndUse_EEM.columns.isin(NonEndUseCols)]

if CeilInsulationMeasure:
    ExtRoofConst = df_input_org.loc[df_input_org.PropKey == "ExtRoofConst"].PropValue.item()
    CeilConst = df_input_org.loc[df_input_org.PropKey == "CeilingConst"].PropValue.item()
    CeilInsOrg = df_input_org.loc[df_input_org.PropKey == "R-CeilingInsulation"].PropValue.item()
    CeilInsEEM = df_input_EEM.loc[df_input_EEM.PropKey == "R-CeilingInsulation"].PropValue.item()
    
    df_MonthlyEndUse_EEM,EEMResults = EvalMeasure.CeilingInsulation(ExtRoofConst,CeilConst, CeilInsOrg, CeilInsEEM)
    dfMeasure = pd.concat([dfMeasure,pd.DataFrame([EEMResults])],ignore_index=True)
    dfSavings -= df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(NonEndUseCols)] - df_MonthlyEndUse_EEM.loc[:,~df_MonthlyEndUse_EEM.columns.isin(NonEndUseCols)]

if WindowMaterialMeasure:
    WindowConstOrg = df_input_org.loc[df_input_org.PropKey == "WindowMaterial"].PropValue.item()
    WindowConstEEM = df_input_EEM.loc[df_input_EEM.PropKey == "WindowMaterial"].PropValue.item()
    
    df_MonthlyEndUse_EEM,EEMResults = EvalMeasure.WindowMaterial(WindowConstOrg,WindowConstEEM)
    dfMeasure = pd.concat([dfMeasure,pd.DataFrame([EEMResults])],ignore_index=True)
    dfSavings -= df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(NonEndUseCols)] - df_MonthlyEndUse_EEM.loc[:,~df_MonthlyEndUse_EEM.columns.isin(NonEndUseCols)]

if OccupancySensorMeasure:
    df_MonthlyEndUse_EEM,EEMResults = EvalMeasure.OccupancySensor()
    dfMeasure = pd.concat([dfMeasure,pd.DataFrame([EEMResults])],ignore_index=True)
    dfSavings -= df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(NonEndUseCols)] - df_MonthlyEndUse_EEM.loc[:,~df_MonthlyEndUse_EEM.columns.isin(NonEndUseCols)]

if ReplaceLightingMeasure:
    pct_LED = df_input_org.loc[df_input_org.PropKey == "LEDCurrent"].PropValue.astype(float).iloc[0]
    pct_LED_EEM = df_input_EEM.loc[df_input_EEM.PropKey == "LEDECM"].PropValue.astype(float).iloc[0]
    
    df_MonthlyEndUse_EEM,EEMResults = EvalMeasure.ReplaceLighting(pct_LED,pct_LED_EEM)
    dfMeasure = pd.concat([dfMeasure,pd.DataFrame([EEMResults])],ignore_index=True)
    dfSavings -= df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(NonEndUseCols)] - df_MonthlyEndUse_EEM.loc[:,~df_MonthlyEndUse_EEM.columns.isin(NonEndUseCols)]

if DaylightingMeasure:
    df_MonthlyEndUse_EEM,EEMResults = EvalMeasure.DaylightingSensor()
    dfMeasure = pd.concat([dfMeasure,pd.DataFrame([EEMResults])],ignore_index=True)
    dfSavings -= df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(NonEndUseCols)] - df_MonthlyEndUse_EEM.loc[:,~df_MonthlyEndUse_EEM.columns.isin(NonEndUseCols)]

if EconomizerMeasure:
    bldg_address = df_input_org.loc[df_input_org.PropKey == "Location"].PropValue.item()
    df_MonthlyEndUse_EEM,EEMResults = EvalMeasure.Economizer(bldg_address)
    dfMeasure = pd.concat([dfMeasure,pd.DataFrame([EEMResults])],ignore_index=True)
    dfSavings -= df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(NonEndUseCols)] - df_MonthlyEndUse_EEM.loc[:,~df_MonthlyEndUse_EEM.columns.isin(NonEndUseCols)]


# CumEEMResults = {}
# CumEEMResults["TIC"] = dfMeasure["InitFixedCost"].sum() + dfMeasure["InitVarCost"].sum()
# CumEEMResults["OrgTotalkWh"] = df_MonthlyEndUse.loc[:,df_MonthlyEndUse.columns.str.contains("EL")].sum().sum()/3.41 # Convert to kWh
# CumEEMResults["OrgTotalTherm"] =df_MonthlyEndUse.loc[:,df_MonthlyEndUse.columns.str.contains("NG")].sum().sum()/100 # Convert to Therms
# CumEEMResults["EEMTotalkWh"] = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("EL")].sum().sum()/3.41 # Convert to kWh
# CumEEMResults["EEMTotalTherm"] =df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("NG")].sum().sum()/100 # Convert to Therms
# CumEEMResults["PctkWhSavings"] = 100*(CumEEMResults["OrgTotalkWh"] - CumEEMResults["EEMTotalkWh"])/CumEEMResults["OrgTotalkWh"] 
# CumEEMResults["PctThermSavings"] = 100*(CumEEMResults["OrgTotalTherm"] - CumEEMResults["EEMTotalTherm"])/CumEEMResults["OrgTotalTherm"]
# CumEEMResults["OrgAOC"] = CostData["kWhRate"]*CumEEMResults["OrgTotalkWh"] + CostData["ThermRate"]*CumEEMResults["OrgTotalTherm"]
# CumEEMResults["EEMAOC"] = CostData["kWhRate"]*CumEEMResults["EEMTotalkWh"] + CostData["ThermRate"]*CumEEMResults["EEMTotalTherm"]
# CumEEMResults["OrgTOC"] = CostData["USPW"]*CumEEMResults["OrgAOC"]
# CumEEMResults["EEMTOC"] = CostData["USPW"]*CumEEMResults["EEMAOC"]
# CumEEMResults["EEMLCC"] = CumEEMResults["TIC"] + CumEEMResults["EEMTOC"]


# PltRes.PlotEndUseBreakdown(dfSavings)
# PltRes.PlotEEMEndUseComparison(df_MonthlyEndUse,dfSavings)


