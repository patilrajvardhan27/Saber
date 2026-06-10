#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np
import os

# Ratio of lighting energy to electric-equipment energy by building type.
# Tuple format: (lighting_parts, equipment_parts).
_LIGHTING_EQUIP_RATIO = {
    "Single Family Residential Building": (1, 3),
    "Places of Religious Worship":        (4, 1),
}
_DEFAULT_LIGHTING_EQUIP_RATIO = (1, 1)

# Ratio of DHW energy to gas-cooking energy by building type.
# Tuple format: (dhw_parts, cooking_parts).
_DHW_COOKING_RATIO = {
    "Single Family Residential Building": (2, 1),
    "Places of Religious Worship":        (8, 1),
}
_DEFAULT_DHW_COOKING_RATIO = (4, 1)


def DisaggregateElectricBaseload(total_baseload_kBtu_sft_day, LPD_W_sft, EPD_W_sft, building_type):
    """Split total EL baseload (kBtu/sft/day) into lighting and equipment using a
    building-type ratio, then back-calculate operating hours from power densities.

    Returns (nHoursLighting, nHoursEquipment, EPD_kBtu_sft_day) or (None, None, None)
    when inputs are insufficient.
    """
    if (not LPD_W_sft or not EPD_W_sft
            or np.isnan(float(LPD_W_sft)) or np.isnan(float(EPD_W_sft))
            or float(LPD_W_sft) <= 0 or float(EPD_W_sft) <= 0
            or total_baseload_kBtu_sft_day <= 0):
        return None, None, None

    R_L, R_E = _LIGHTING_EQUIP_RATIO.get(building_type, _DEFAULT_LIGHTING_EQUIP_RATIO)
    lighting_density = total_baseload_kBtu_sft_day * R_L / (R_L + R_E)  # kBtu/sft/day
    equip_density    = total_baseload_kBtu_sft_day * R_E / (R_L + R_E)  # kBtu/sft/day

    W_to_kBtu_per_hr = 3.41 / 1000  # kBtu per W per hour
    nHoursLighting  = min(lighting_density / (float(LPD_W_sft) * W_to_kBtu_per_hr), 24.0)
    nHoursEquipment = min(equip_density    / (float(EPD_W_sft) * W_to_kBtu_per_hr), 24.0)

    return nHoursLighting, nHoursEquipment, equip_density


def DisaggregateNGBaseload(total_ng_daily_kBtu_sft, GPD_W_sft, building_type):
    """Split NG baseload (kBtu/sft/day) into DHW and gas-cooking shares using a
    building-type ratio, then back-calculate cooking operating hours from GPD.

    Only called when GPD > 0 (gas cooking is present).
    Returns (dhw_fraction, nHoursCooking) or (1.0, None) when inputs are invalid.
    """
    if (not GPD_W_sft or np.isnan(float(GPD_W_sft)) or float(GPD_W_sft) <= 0
            or total_ng_daily_kBtu_sft <= 0):
        return 1.0, None

    R_DHW, R_Cook = _DHW_COOKING_RATIO.get(building_type, _DEFAULT_DHW_COOKING_RATIO)
    dhw_fraction     = R_DHW  / (R_DHW + R_Cook)
    cooking_density  = total_ng_daily_kBtu_sft * R_Cook / (R_DHW + R_Cook)  # kBtu/sft/day

    W_to_kBtu_per_hr = 3.41 / 1000
    nHoursCooking = min(cooking_density / (float(GPD_W_sft) * W_to_kBtu_per_hr), 24.0)

    return dhw_fraction, nHoursCooking


def GetGeometryParameters(df_input):
    FloorQty = df_input.loc[df_input.PropKey == "FloorQty"].PropValue.astype(float).iloc[0]
    FloorArea = df_input.loc[df_input.PropKey == "FloorArea"].PropValue.astype(float).iloc[0]
    WWR = df_input.loc[df_input.PropKey == "WWR"].PropValue.iloc[0].copy()
    ShapeType = df_input.loc[df_input.PropKey == "Shape"].PropValue.item()
    WallHeight = df_input.loc[df_input.PropKey == "WallHeight"].PropValue.astype(float).iloc[0]
    Volume = FloorArea*WallHeight*FloorQty
    WindowHeight = df_input.loc[df_input.PropKey == "WindowHeight"].PropValue.astype(float).iloc[0]
    x1 = df_input.loc[df_input.PropKey == "x1"].PropValue.astype(float).iloc[0]
    x2 = df_input.loc[df_input.PropKey == "x2"].PropValue.astype(float).iloc[0]
    y1 = df_input.loc[df_input.PropKey == "y1"].PropValue.astype(float).iloc[0]
    y2 = df_input.loc[df_input.PropKey == "y2"].PropValue.astype(float).iloc[0]
    
    if ShapeType == "Rectangle":
        CeilingArea = x1*y1
        WallArea = {}
        WallArea["Front"] = x1*WallHeight*FloorQty
        WallArea["Left"] = y1*WallHeight*FloorQty
        WallArea["Right"] = y1*WallHeight*FloorQty
        WallArea["Back"] = x1*WallHeight*FloorQty

        WindowArea = {}
        WindowArea["Front"] = WWR["Front"]/100*WallArea["Front"]
        WindowArea["Left"] = WWR["Left"]/100*WallArea["Left"]
        WindowArea["Right"] = WWR["Right"]/100*WallArea["Right"]
        WindowArea["Back"] = WWR["Back"]/100*WallArea["Back"]

        ExtWallArea = {}
        for face in WallArea.keys():
            ExtWallArea[face] = WallArea[face] - WindowArea[face]

    return FloorArea, Volume, WallArea, sum(ExtWallArea.values()), sum(WindowArea.values()), CeilingArea

class Energy:
    def __init__(self, BestModelParams, df_weather,df_input):
        # print("Running simulation for measure with inputs:", df_input.loc[df_input["PropKey"].isin(["HeatingEquipment","HeatingEff","HeatingCap","CoolingEquipment","CoolingEff","CoolingCap"]), ["PropKey","PropValue"]])

        self.BestModelParams = BestModelParams
        self.df_input = df_input
        self.FloorArea = self.df_input.loc[self.df_input.PropKey=="FloorArea","PropValue"].astype(float).iloc[0]
        self.n_NightSetbackHours = self.df_input.loc[self.df_input.PropKey=="nNightSetbackHours","PropValue"].astype(float).iloc[0]
        self.SetbackValue = self.df_input.loc[self.df_input.PropKey=="NightSetback","PropValue"].astype(float).iloc[0]
        # Prefer disaggregated value stored in BestModelParams (set after first baseline run).
        # Falls back to user-provided df_input value for the initial baseline simulation.
        _n_hours_params = BestModelParams.get("nHoursLighting")
        if _n_hours_params is not None and not (isinstance(_n_hours_params, float) and np.isnan(_n_hours_params)) and float(_n_hours_params) > 0:
            self.N_hours_lighting = float(_n_hours_params)
        else:
            self.N_hours_lighting = self.df_input.loc[self.df_input.PropKey=="nHoursLighting","PropValue"].astype(float).iloc[0]
        self.LPD = self.df_input.loc[self.df_input.PropKey=="LPD","PropValue"].astype(float).iloc[0] # W/sft
        self.f_Load = 1 - self.df_input.loc[self.df_input.PropKey=="EquipLoadRed","PropValue"].astype(float).iloc[0]/100


        if self.df_input.loc[self.df_input.PropKey=="HeatingEff","PropValue"].item() == "Other..":
            self.HeatingEff = self.df_input.loc[self.df_input.PropKey=="HeatingEffCustom","PropValue"].astype(float).iloc[0]
        else:
            self.HeatingEff = self.df_input.loc[self.df_input.PropKey=="HeatingEff","PropValue"].astype(float).iloc[0]
        # Leave cooling efficiecny in SEER

        if self.df_input.loc[self.df_input.PropKey=="CoolingEff","PropValue"].item() == "Other..":
            self.CoolingEff = self.df_input.loc[self.df_input.PropKey=="CoolingEffCustom","PropValue"].astype(float).iloc[0]/3.41 # Convert SEER to COP
        elif self.df_input.loc[self.df_input.PropKey=="CoolingEff","PropValue"].iloc[0] != "None": #Ashit: changed else condition to elif
            #print("Check by Ashit", df_input.loc[df_input.PropKey=="CoolingEff","PropValue"].iloc[0])
            self.CoolingEff = self.df_input.loc[self.df_input.PropKey=="CoolingEff","PropValue"].astype(float).iloc[0]/3.41
        else: #Ashit: Added else statemet to trivialize energy calculation if NoCooling
            self.CoolingEff = 1


        HeatingEqp = self.df_input.loc[self.df_input.PropKey=="HeatingEquipment","PropValue"].astype(str).item()
           
        
        if "HeatPump" in HeatingEqp.replace(" ",""):
            self.HeatingEff_EL = self.HeatingEff/3.41 # Convert to COP for heat pumps
        else:
            self.HeatingEff_EL = 1

        # print(self.BestModelParams)

        self.baseload_ccp = self.BestModelParams["EL-CoolingBaseload"] #kBtu/sft
        self.ccp = self.BestModelParams["EL-CoolingChangePoint"]
        self.slope_ccp = self.BestModelParams["EL-CoolingSlope"] #kBtu/sft-day-F

        self.baseload_hcp_ng = self.BestModelParams["NG-HeatingBaseload"] #kBtu/sft
        self.hcp_ng = self.BestModelParams["NG-HeatingChangePoint"]
        self.slope_hcp_ng = self.BestModelParams["NG-HeatingSlope"]   #kBtu/sft-day-F

        # Fraction of NG baseload allocated to DHW (remainder goes to gas cooking).
        # Pre-disaggregation in RunSimulationCase injects NG_DHW_fraction into
        # BestModelParams when GPD > 0, so it is available here for every run.
        _ng_dhw_frac = BestModelParams.get("NG_DHW_fraction")
        if (_ng_dhw_frac is not None
                and not (isinstance(_ng_dhw_frac, float) and np.isnan(_ng_dhw_frac))):
            self.NG_DHW_fraction = float(_ng_dhw_frac)
        else:
            self.NG_DHW_fraction = 1.0  # default: all NG baseload = DHW

        self.baseload_hcp_el = self.BestModelParams["EL-HeatingBaseload"] #kBtu/sft
        self.hcp_el = self.BestModelParams["EL-HeatingChangePoint"]
        self.slope_hcp_el = self.BestModelParams["EL-HeatingSlope"]  #kBtu/sft-day-F


        self.df_month = df_weather.resample("M").mean()
        


        self.fDH_NG = 1
        self.fDH_EL = 1
        if self.hcp_ng:
            self.TempSetback_NG = self.hcp_ng - self.SetbackValue
            self.T_heating_mean = self.df_month.loc[self.df_month["Temp_F"]<=self.hcp_ng]["Temp_F"].mean()
            if self.T_heating_mean:
                self.fDH_NG = ((24-self.n_NightSetbackHours)/24) + ((self.n_NightSetbackHours/24)*((self.TempSetback_NG - self.T_heating_mean)/(self.hcp_ng - self.T_heating_mean)))
                print("Night Setback", self.n_NightSetbackHours, "hours, SetbackValue", self.SetbackValue )
                print("fDH_NG", self.fDH_NG)
            
        
        if self.hcp_el:
            self.TempSetback_EL = self.hcp_el - self.SetbackValue
            self.T_heating_mean = self.df_month.loc[self.df_month["Temp_F"]<=self.hcp_el]["Temp_F"].mean()
            if self.T_heating_mean:
                self.fDH_EL = ((24-self.n_NightSetbackHours)/24) + ((self.n_NightSetbackHours/24)*((self.TempSetback_EL - self.T_heating_mean)/(self.hcp_el - self.T_heating_mean)))
                print("fDH_EL", self.fDH_EL)
        
        # if not EEMEval:
        # self.BLC_DD_Heat_NG = abs(BestModelParams["NG-HeatingSlope"])*self.HeatingEff*1000*self.FloorArea/(24*self.fDH_NG) #Btu/F-hr
        # self.BLC_DD_Heat_EL = abs(BestModelParams["EL-HeatingSlope"])*self.HeatingEff_EL*1000*self.FloorArea/(24*self.fDH_EL) #Btu/F-hr
        # self.BLC_DD_Cool_EL = (abs(BestModelParams["EL-CoolingSlope"])*self.CoolingEff*1000*self.FloorArea/24)/3.41 #Wh/F-hr to Btu/F-hr
        
        
        self.BLC_DD_Heat_NG = abs(BestModelParams["NG-HeatingSlope"])*1000*self.FloorArea/(24) #Btu/F-hr
        self.BLC_DD_Heat_EL = abs(BestModelParams["EL-HeatingSlope"])*1000*self.FloorArea/(24) #Btu/F-hr
        self.BLC_DD_Cool_EL = (abs(BestModelParams["EL-CoolingSlope"])*1000*self.FloorArea)/(24) #Wh/F-hr to Btu/F-hr

        print ("BLC_DD_Heat_NG, BLC_DD_Heat_EL, BLC_DD_Cool_EL",self.BLC_DD_Heat_NG, self.BLC_DD_Heat_EL, self.BLC_DD_Cool_EL)
        # else:
        #     self.BLC_DD_Heat_NG = BestModelParams["BLC_Heating_NG_adj"]
        #     self.BLC_DD_Heat_EL = BestModelParams["BLC_Heating_EL_adj"]
        #     self.BLC_DD_Cool_EL = BestModelParams["BLC_Cooling_EL_adj"]
        #     print ("BLC_DD_Heat_NG, BLC_DD_Heat_EL, BLC_DD_Cool_EL",self.BLC_DD_Heat_NG, self.BLC_DD_Heat_EL, self.BLC_DD_Cool_EL)

    def heating_energy_NG (self, df_day):
        if self.hcp_ng:
            df_day_hcp = df_day.copy()
            

            df_day_hcp.mask(df_day_hcp["Temp_F"] >= self.hcp_ng,0,inplace=True)


            self.DDh_NG = np.sum(self.hcp_ng - df_day_hcp.loc[df_day_hcp["Temp_F"]!=0]["Temp_F"].values)
            # print("DDh_NG",self.DDh_NG)
            # print("Heating Eff",self.HeatingEff)
            heating_energy = (24*self.BLC_DD_Heat_NG*self.fDH_NG*self.DDh_NG)/self.HeatingEff # By multiplying by fDh we are in fact getting lower heating energy consumption than what is predicted by the model. There will be a slight mismatch.
            print("Heating energy NG (kBtu)", heating_energy/1000,"BLC_DD_Heat_NG", self.BLC_DD_Heat_NG, "DDh_NG", self.DDh_NG, "fDH_NG", self.fDH_NG)
        else:
            heating_energy = 0
            self.DDh_NG = 0
        return heating_energy/1000,self.DDh_NG #KbTU
    
    def heating_energy_EL (self, df_day):
        if self.hcp_el:
            df_day_hcp = df_day.copy()

            df_day_hcp.mask(df_day_hcp["Temp_F"] >= self.hcp_el,0,inplace=True)


            self.DDh_EL = np.sum(self.hcp_el - df_day_hcp.loc[df_day_hcp["Temp_F"]!=0]["Temp_F"].values)
            
            heating_energy = (24*self.BLC_DD_Heat_EL*self.DDh_EL*self.fDH_EL)/self.HeatingEff_EL
        else:
            heating_energy = 0
            self.DDh_EL = 0
        return heating_energy/1000,self.DDh_EL #KbTU
    
    def dhw_energy(self):
        if self.baseload_hcp_ng:
            return self.NG_DHW_fraction * self.baseload_hcp_ng * self.FloorArea
        return 0

    def cooking_energy_ng(self):
        """Gas cooking energy (kBtu/month). Non-zero only when GPD > 0."""
        if self.baseload_hcp_ng and self.NG_DHW_fraction < 1.0:
            return (1.0 - self.NG_DHW_fraction) * self.baseload_hcp_ng * self.FloorArea
        return 0.0
    
    def lighting_energy(self,df_day):
        # LPD = Lighting Power Density (W/ft^2)
        # FloorArea = Floor Area (ft^2)
        # N_hours = Number of hours the lights are on per day
        if not self.N_hours_lighting or np.isnan(self.N_hours_lighting) or self.N_hours_lighting <= 0:
            # nHoursLighting not yet determined (pre-disaggregation baseline run).
            # Return 0 so the full regression baseload is treated as equipment energy,
            # which GetAllModelParams will then split correctly via disaggregation.
            return 0.0
        lighting_energy = self.LPD*self.FloorArea*self.N_hours_lighting*df_day.shape[0]/1000
        return lighting_energy*3.41 #KbTU

    def cooling_energy (self, df_day):
        if self.ccp:
            df_day_ccp = df_day.copy()
            
            df_day_ccp.mask(df_day_ccp["Temp_F"] <= self.ccp,0,inplace=True)
            self.DDc = np.sum(df_day_ccp.loc[df_day_ccp["Temp_F"]!=0]["Temp_F"].values - self.ccp)
            cooling_energy_value = (24*self.BLC_DD_Cool_EL*self.DDc)/self.CoolingEff
        else:
            cooling_energy_value = 0
            self.DDc = 0

        return (cooling_energy_value/1000)*3.41,self.DDc #KbTU

    def ElectricEquipment(self,df_day):
        # Need to do this to account for ECM evaluation to keep the electric equipment energy same as basecase if there is lighting measures.
        epd_val = None
        
        try:
            epd_val = self.BestModelParams["EPD"]
        except Exception:
            epd_val = None

        if epd_val is not None and not (isinstance(epd_val, float) and np.isnan(epd_val)) and epd_val > 0:
            electric_eqp_energy = float(epd_val) * self.FloorArea * df_day.shape[0] #kBtu
            EPD = float(epd_val) #kBtu/sft-day
        else:
            if self.DDh_EL > self.DDc:
                electric_eqp_energy = self.baseload_hcp_el*self.FloorArea - self.lighting_energy(df_day)
            elif self.DDh_EL == self.DDc:
                electric_eqp_energy = max(self.baseload_hcp_el,self.baseload_ccp)*self.FloorArea - self.lighting_energy(df_day)
            else:
                electric_eqp_energy = self.baseload_ccp*self.FloorArea - self.lighting_energy(df_day)
            
            EPD = electric_eqp_energy/(self.FloorArea*df_day.shape[0]) #kBtu/sft-day

        return self.f_Load*electric_eqp_energy,EPD #KbTU
        
    def EndUseBreakdown(self,df_day):
        EndUseBreakdown = {}
        # EndUseBreakdown["BLC_Heat_EL"] = self.BLC_DD_Heat_EL
        # EndUseBreakdown["BLC_Heat_NG"] = self.BLC_DD_Heat_NG
        # EndUseBreakdown["BLC_Cool_EL"] = self.BLC_DD_Cool_EL
        EndUseBreakdown["NG-Space Heating"],EndUseBreakdown["HDD_NG"] = self.heating_energy_NG(df_day)
        EndUseBreakdown["EL-Space Heating"],EndUseBreakdown["HDD_EL"] = self.heating_energy_EL(df_day)
        EndUseBreakdown["EL-Space Cooling"],EndUseBreakdown["CDD"] = self.cooling_energy(df_day)
        EndUseBreakdown["EL-Lighting"] = self.lighting_energy(df_day)
        EndUseBreakdown["EL-Electric Equipment"],EndUseBreakdown["EPD"] = self.ElectricEquipment(df_day)
        EndUseBreakdown["NG-DHW Heating"]  = self.dhw_energy()
        EndUseBreakdown["NG-Gas Cooking"]  = self.cooking_energy_ng()
        return EndUseBreakdown

    def GetAllModelParams(self, RunDir, EPD):
        self.BestModelParams["BLC_Heating_NG"] = self.BLC_DD_Heat_NG
        self.BestModelParams["BLC_Heating_EL"] = self.BLC_DD_Heat_EL
        self.BestModelParams["BLC_Cooling_EL"] = self.BLC_DD_Cool_EL
        self.BestModelParams["FloorArea"] = self.FloorArea

        self.BestModelParams["FloorArea"], self.BestModelParams["Volume"], self.BestModelParams["WallArea"], self.BestModelParams["ExtWallArea"], self.BestModelParams["WindowArea"], self.BestModelParams["CeilingArea"] = GetGeometryParameters(self.df_input)

        # Disaggregate total EL baseload (equipment EPD + lighting EPD) into
        # lighting and equipment shares using the building-type energy ratio,
        # then back-calculate operating hours from the user-supplied power densities.
        building_type = self.df_input.loc[self.df_input.PropKey == "BuildingType", "PropValue"].item()
        LPD = self.LPD  # W/sft (already loaded in __init__)

        epd_w_val = self.df_input.loc[self.df_input.PropKey == "EPD", "PropValue"].iloc[0]
        try:
            EPD_W_input = float(epd_w_val)
        except (ValueError, TypeError):
            EPD_W_input = None

        # Reconstruct total EL baseload: simulation-derived equipment EPD + lighting EPD.
        # N_hours_lighting is 0 on the very first baseline run (pre-disaggregation), so
        # EPD already equals the full regression baseload/day in that case.
        n_hours = self.N_hours_lighting if (self.N_hours_lighting and not np.isnan(self.N_hours_lighting) and self.N_hours_lighting > 0) else 0.0
        lighting_epd = LPD * n_hours * 3.41 / 1000  # kBtu/sft/day
        total_baseload = EPD + lighting_epd           # kBtu/sft/day

        nHoursLighting, nHoursEquipment, EPD_kBtu = DisaggregateElectricBaseload(
            total_baseload, LPD, EPD_W_input, building_type)

        if nHoursLighting is not None:
            self.BestModelParams["nHoursLighting"]  = nHoursLighting
            self.BestModelParams["nHoursEquipment"] = nHoursEquipment
            self.BestModelParams["EPD"]             = EPD_kBtu
        else:
            self.BestModelParams["EPD"] = EPD  # fallback: keep simulation-derived value

        # ── NG disaggregation: DHW vs gas cooking ──────────────────────────────
        gpd_w_val = self.df_input.loc[self.df_input.PropKey == "GPD", "PropValue"].iloc[0]
        try:
            GPD_W_input = float(gpd_w_val)
        except (ValueError, TypeError):
            GPD_W_input = None

        if GPD_W_input and GPD_W_input > 0 and self.baseload_hcp_ng:
            # Use daily NG baseload (monthly ÷ 30) for disaggregation
            ng_daily = self.baseload_hcp_ng / 30.0
            dhw_frac, nHoursCooking = DisaggregateNGBaseload(
                ng_daily, GPD_W_input, building_type)
            self.BestModelParams["NG_DHW_fraction"] = dhw_frac
            if nHoursCooking is not None:
                self.BestModelParams["nHoursCooking"] = nHoursCooking

        pd.DataFrame([self.BestModelParams]).to_csv(os.path.join(RunDir, "BestModelParams.csv"), index=False)
        return