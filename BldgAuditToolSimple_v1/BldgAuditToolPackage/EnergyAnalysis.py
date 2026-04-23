#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np

class Energy:
    def __init__(self, BestModelParams, df_weather,df_input,EEMEval):
        self.FloorArea = df_input.loc[df_input.PropKey=="FloorArea","PropValue"].astype(float).iloc[0]
        self.n_NightSetbackHours = df_input.loc[df_input.PropKey=="nNightSetbackHours","PropValue"].astype(float).iloc[0]
        self.SetbackValue = df_input.loc[df_input.PropKey=="NightSetback","PropValue"].astype(float).iloc[0]
        self.N_hours_lighting = df_input.loc[df_input.PropKey=="nHoursLighting","PropValue"].astype(float).iloc[0] # hours per day
        self.LPD = df_input.loc[df_input.PropKey=="LPD","PropValue"].astype(float).iloc[0] # W/sft
        
        
        
        _heat_val = df_input.loc[df_input.PropKey=="HeatingEff","PropValue"].iloc[0]
        if str(_heat_val) == "Other..":
            self.HeatingEff = df_input.loc[df_input.PropKey=="HeatingEffCustom","PropValue"].astype(float).iloc[0]
        elif pd.notna(_heat_val) and str(_heat_val) not in ("", "None", "nan"):
            self.HeatingEff = float(_heat_val)
        else:
            self.HeatingEff = 1

        # Leave cooling efficiency in SEER units
        _cool_val = df_input.loc[df_input.PropKey=="CoolingEff","PropValue"].iloc[0]
        if str(_cool_val) == "Other..":
            self.CoolingEff = df_input.loc[df_input.PropKey=="CoolingEffCustom","PropValue"].astype(float).iloc[0]
        elif pd.notna(_cool_val) and str(_cool_val) not in ("", "None", "nan"):
            self.CoolingEff = float(_cool_val)
        else:
            self.CoolingEff = 1  # NoCooling or efficiency not set — value cancels in baseline math
        
            
        HeatingEqp = df_input.loc[df_input.PropKey=="HeatingEquipment","PropValue"].astype(str).item()
           
        
        if "Heat Pump" in HeatingEqp:
            self.HeatingEff_EL = self.HeatingEff
        else:
            self.HeatingEff_EL = 1

        
        print(BestModelParams)


        self.baseload_ccp = BestModelParams["EL-CoolingBaseload"] #kBtu/sft
        self.ccp = BestModelParams["EL-CoolingChangePoint"]
        self.slope_ccp = BestModelParams["EL-CoolingSlope"]

        self.baseload_hcp_ng = BestModelParams["NG-HeatingBaseload"] #kBtu/sft
        self.hcp_ng = BestModelParams["NG-HeatingChangePoint"]
        self.slope_hcp_ng = BestModelParams["NG-HeatingSlope"] 

        self.baseload_hcp_el = BestModelParams["EL-HeatingBaseload"] #kBtu/sft
        self.hcp_el = BestModelParams["EL-HeatingChangePoint"]
        self.slope_hcp_el = BestModelParams["EL-HeatingSlope"] 


        self.df_month = df_weather.resample("M").mean()
        


        self.fDH_NG = 1
        self.fDH_EL = 1
        if self.hcp_ng:
            self.TempSetback_NG = self.hcp_ng - self.SetbackValue
            self.T_heating_mean = self.df_month.loc[self.df_month["Temp_F"]<=self.hcp_ng]["Temp_F"].mean()
            if self.T_heating_mean:
                self.fDH_NG = ((24-self.n_NightSetbackHours)/24) + ((self.n_NightSetbackHours/24)*((self.TempSetback_NG - self.T_heating_mean)/(self.hcp_ng - self.T_heating_mean)))
                print("fDH_NG", self.fDH_NG)
            
        
        if self.hcp_el:
            self.TempSetback_EL = self.hcp_el - self.SetbackValue
            self.T_heating_mean = self.df_month.loc[self.df_month["Temp_F"]<=self.hcp_el]["Temp_F"].mean()
            if self.T_heating_mean:
                self.fDH_EL = ((24-self.n_NightSetbackHours)/24) + ((self.n_NightSetbackHours/24)*((self.TempSetback_EL - self.T_heating_mean)/(self.hcp_el - self.T_heating_mean)))
                print("fDH_EL", self.fDH_EL)
        
        if not EEMEval:
            self.BLC_DD_Heat_NG = abs(BestModelParams["NG-HeatingSlope"])*self.HeatingEff*1000*self.FloorArea/(24*self.fDH_NG) #Btu/F-hr
            self.BLC_DD_Heat_EL = abs(BestModelParams["EL-HeatingSlope"])*self.HeatingEff_EL*1000*self.FloorArea/(24*self.fDH_EL) #Btu/F-hr
            self.BLC_DD_Cool_EL = (abs(BestModelParams["EL-CoolingSlope"])*self.CoolingEff*1000*self.FloorArea/24)/3.41 #Wh/F-hr to Btu/F-hr
            print ("BLC_DD_Heat_NG, BLC_DD_Heat_EL, BLC_DD_Cool_EL",self.BLC_DD_Heat_NG, self.BLC_DD_Heat_EL, self.BLC_DD_Cool_EL)
        else:
            self.BLC_DD_Heat_NG = BestModelParams["BLC_Heating_NG_adj"]
            self.BLC_DD_Heat_EL = BestModelParams["BLC_Heating_EL_adj"]
            self.BLC_DD_Cool_EL = BestModelParams["BLC_Cooling_EL_adj"]
            print ("BLC_DD_Heat_NG, BLC_DD_Heat_EL, BLC_DD_Cool_EL",self.BLC_DD_Heat_NG, self.BLC_DD_Heat_EL, self.BLC_DD_Cool_EL)

    def heating_energy_NG (self, df_day):
        if self.hcp_ng:
            df_day_hcp = df_day.copy()
            

            df_day_hcp.mask(df_day_hcp["Temp_F"] >= self.hcp_ng,0,inplace=True)


            self.DDh_NG = np.sum(self.hcp_ng - df_day_hcp.loc[df_day_hcp["Temp_F"]!=0]["Temp_F"].values)
            print("DDh_NG",self.DDh_NG)
            print("Heating Eff",self.HeatingEff)
            heating_energy = (24*self.BLC_DD_Heat_NG*self.DDh_NG*self.fDH_NG)/self.HeatingEff # By multiplying by fDh we are in fact getting lower heating energy consumption than what is predicted by the model. There will be a slight mismatch.
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
            return self.baseload_hcp_ng*self.FloorArea
        else:
            return 0
    
    def lighting_energy(self,df_day):
        # LPD = Lighting Power Density (W/ft^2)
        # FloorArea = Floor Area (ft^2)
        # N_hours = Number of hours the lights are on per day
        #print(df_day, self.LPD,self.FloorArea,self.N_hours_lighting)
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
        if self.DDh_EL > self.DDc:
            electric_eqp_energy = self.baseload_hcp_el*self.FloorArea - self.lighting_energy(df_day)
        elif self.DDh_EL == self.DDc:
            electric_eqp_energy = max(self.baseload_hcp_el,self.baseload_ccp)*self.FloorArea - self.lighting_energy(df_day)
        else:
            electric_eqp_energy = self.baseload_ccp*self.FloorArea - self.lighting_energy(df_day)

        return electric_eqp_energy #KbTU
    
    def EndUseBreakdown(self,df_day):
        EndUseBreakdown = {}
        EndUseBreakdown["BLC_Heat_EL"] = self.BLC_DD_Heat_EL
        EndUseBreakdown["BLC_Heat_NG"] = self.BLC_DD_Heat_NG
        EndUseBreakdown["BLC_Cool_EL"] = self.BLC_DD_Cool_EL
        EndUseBreakdown["NG-Space Heating"],EndUseBreakdown["HDD_NG"] = self.heating_energy_NG(df_day)
        EndUseBreakdown["EL-Space Heating"],EndUseBreakdown["HDD_EL"] = self.heating_energy_EL(df_day)
        EndUseBreakdown["EL-Space Cooling"],EndUseBreakdown["CDD"] = self.cooling_energy(df_day)
        EndUseBreakdown["EL-Lighting"] = self.lighting_energy(df_day)
        EndUseBreakdown["EL-Electric Equipment"] = self.ElectricEquipment(df_day)
        EndUseBreakdown["NG-DHW Heating"] = self.dhw_energy()
        return EndUseBreakdown


# In[ ]:




