from .EnergyAnalysis import Energy, DisaggregateElectricBaseload, DisaggregateNGBaseload
import pandas as pd
import numpy as np
import os

#%% GET MONTHLY ENERGY END USE BREAKDOWN. This is basically running the energy simulation.
def GetMonthlyEndUseBreakdown(BestModelParams,df_weather,df_input,RunDir):
    # If nHoursLighting has not yet been disaggregated (first baseline run),
    # compute it now from the regression baseload so lighting energy is non-zero
    # throughout all 12 monthly simulations that follow.
    if not BestModelParams.get("nHoursLighting") or (
            isinstance(BestModelParams.get("nHoursLighting"), float)
            and np.isnan(BestModelParams["nHoursLighting"])):

        el_hcp = BestModelParams.get("EL-HeatingBaseload") or 0
        el_ccp = BestModelParams.get("EL-CoolingBaseload") or 0
        # Baseloads are kBtu/sft/month; divide by 30 to get daily rate
        monthly_baseload = max(el_hcp, el_ccp)
        total_daily_baseload = monthly_baseload / 30.0  # kBtu/sft/day

        building_type = df_input.loc[df_input.PropKey == "BuildingType", "PropValue"].item()
        try:
            LPD = float(df_input.loc[df_input.PropKey == "LPD", "PropValue"].iloc[0])
        except (ValueError, TypeError):
            LPD = None
        try:
            EPD_W = float(df_input.loc[df_input.PropKey == "EPD", "PropValue"].iloc[0])
        except (ValueError, TypeError):
            EPD_W = None

        nHoursLighting, nHoursEquipment, EPD_kBtu = DisaggregateElectricBaseload(
            total_daily_baseload, LPD, EPD_W, building_type)

        if nHoursLighting is not None:
            BestModelParams["nHoursLighting"]  = nHoursLighting
            BestModelParams["nHoursEquipment"] = nHoursEquipment
            BestModelParams["EPD"]             = EPD_kBtu

    # ── NG pre-disaggregation: DHW vs gas cooking ──────────────────────────────
    # Only runs when GPD > 0 and NG_DHW_fraction not yet stored (first baseline run).
    if not BestModelParams.get("NG_DHW_fraction") or (
            isinstance(BestModelParams.get("NG_DHW_fraction"), float)
            and np.isnan(BestModelParams["NG_DHW_fraction"])):

        try:
            GPD_W = float(df_input.loc[df_input.PropKey == "GPD", "PropValue"].iloc[0])
        except (ValueError, TypeError):
            GPD_W = None

        if GPD_W and GPD_W > 0:
            ng_baseload = BestModelParams.get("NG-HeatingBaseload") or 0
            ng_daily    = ng_baseload / 30.0  # kBtu/sft/day
            building_type = df_input.loc[df_input.PropKey == "BuildingType", "PropValue"].item()

            dhw_frac, nHoursCooking = DisaggregateNGBaseload(ng_daily, GPD_W, building_type)
            BestModelParams["NG_DHW_fraction"] = dhw_frac
            if nHoursCooking is not None:
                BestModelParams["nHoursCooking"] = nHoursCooking

    EnergyEndUse = Energy(BestModelParams,df_weather,df_input)
    #print("AnalyzedUtilityData.py line 74", df_weather.isna().any().any())
    
    df_MonthlyEndUse = pd.DataFrame(columns=["NG-Space Heating","EL-Space Heating","NG-DHW Heating","NG-Gas Cooking","EL-Space Cooling","EL-Lighting","EL-Electric Equipment","EPD","HDD_EL","HDD_NG","CDD"])
    for m in set(df_weather.index.month):
        df_day_i = df_weather.loc[df_weather.index.month == m].resample("24H").mean()
        #print("AnalyzedUtilityData.py line 78", df_day_i)
        df_MonthlyEndUse = pd.concat([df_MonthlyEndUse,pd.DataFrame([EnergyEndUse.EndUseBreakdown(df_day_i)],columns=df_MonthlyEndUse.columns)])
    
    # ensure output directory exists
    os.makedirs(RunDir, exist_ok=True)

    df_MonthlyEndUse = df_MonthlyEndUse.astype(float).reset_index(drop=True)
    print("Electricity and natural gas end use breakdown by month:", df_MonthlyEndUse)
    df_MonthlyEndUse.to_csv(os.path.join(RunDir, "MonthlyEndUseBreakdown.csv"), index=False)
    EnergyEndUse.GetAllModelParams(RunDir,df_MonthlyEndUse["EPD"].mean())
    
    return

def GetSummaryResults(RunDir,CostMetrics):
    df_MonthlyEndUse = pd.read_csv(os.path.join(RunDir, "MonthlyEndUseBreakdown.csv"))
    BestModelParams = pd.read_csv(os.path.join(RunDir,"BestModelParams.csv")).iloc[0].to_dict()

    BestModelParams["Electricity"] = df_MonthlyEndUse.loc[:,df_MonthlyEndUse.columns.str.contains("EL-")].sum().sum()/3.41 # Convert to kWh
    BestModelParams["NaturalGas"] = df_MonthlyEndUse.loc[:,df_MonthlyEndUse.columns.str.contains("NG-")].sum().sum()/100 # Convert to Therms
    BestModelParams["TSE"] = (BestModelParams["Electricity"] + BestModelParams["NaturalGas"]*100/3.41)
    BestModelParams["TotalSourceEnergy"] = BestModelParams["Electricity"]*3.167 + BestModelParams["NaturalGas"]*100*1.092/3.41
    BestModelParams["AnnualOperatingCost"] = (BestModelParams["Electricity"]*CostMetrics["kWhRate"])+(BestModelParams["NaturalGas"]*CostMetrics["ThermRate"])
    BestModelParams["TOC"] = BestModelParams["AnnualOperatingCost"]*CostMetrics.get("USPW", 1)
    # print("Summary results for this measure package:", BestModelParams)
    pd.DataFrame([BestModelParams]).to_csv(os.path.join(RunDir, "SummaryResults.csv"), index=False)

    return 