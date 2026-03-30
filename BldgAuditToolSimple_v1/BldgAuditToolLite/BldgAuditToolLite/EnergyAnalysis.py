#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np

class Energy:
    def __init__(self, DDResults, df_weather):
        self.n_NightSetbackHours = 0
        self.SetbackValue = 0
        self.N_hours_lighting = 6 # hours per day
        self.LPD = 1.072 # W/sft
        self.TempSetback = DDResults["HeatingChangePoint"] - self.SetbackValue

        self.baseload_ccp = DDResults["CoolingBaseload"] #kBtu/sft
        self.ccp = DDResults["CoolingChangePoint"]
        self.slope_ccp = DDResults["CoolingSlope"]
        self.baseload_hcp = DDResults["HeatingBaseload"] #kBtu/sft
        self.hcp = DDResults["HeatingChangePoint"]
        self.slope_hcp = DDResults["HeatingSlope"] 

        self.df_month = self.df_weather.resample("M").mean()
        self.df_day = self.df_weather.resample("24H").mean()
        self.T_heating_mean = self.df_month.loc[self.df_month["Temp_F"]<=self.hcp]["Temp_F"].mean()


    def heating_energy (self, hcp, BLC, efficiency, oat, df_new):
        self.fDH = ((24-self.n_NightSetbackHours)/24) + ((self.n_NightSetbackHours/24)*((self.TempSetback - oat)/(self.hcp - oat)))
        df_DDh = []
        df_DDh = pd.DataFrame({"OAT": oat})
        df_DDh["hcp"] = hcp
        
    
        column_name = "Degree Day Heating"
        df_DDh[column_name] = np.where(df_DDh["hcp"] - df_DDh["OAT"] < 0, 0, df_DDh["hcp"] - df_DDh["OAT"])

        DDh = df_DDh[column_name].sum()
        
        heating_energy = (24*BLC*DDh*self.fDH)/efficiency

        return heating_energy
        
    def cooling_energy (self, ccp, BLC, efficiency, oat, df_new):
        df_DDc = []
        df_DDc = pd.DataFrame({"OAT": oat})
        df_DDc["ccp"] = ccp
        df_DDc["Dates"] = df_new["Date"]
    
        column_name = "Degree Day Cooling"
        df_DDc[column_name] = np.where(df_DDc["OAT"] - df_DDc["ccp"] < 0, 0, df_DDc["OAT"] - df_DDc["ccp"])

        DDc = df_DDc[column_name].sum()
                
        cooling_energy = (24*BLC*DDc*self)/efficiency

        return cooling_energy

    def EndUseBreakDown(self):
        

        EndUseBreakdown = {}
        # Annual Energy End Use Breakdown
        EndUseBreakdown["Space Heating"] = self.heating_energy(hcp,BLC_DD,HeatingEff,df_day)/1000 #kBtu
        EndUseBreakdown["DHW Heating"] = baseload_hcp*FloorArea*12 #kBtu

        EndUseBreakdown["Space Cooling"] = (self.cooling_energy(ccp,BLC_DD,CoolingEff,df_day)/1000)*3.41 #Using eff in SEER you get ouptut in kWh so you multiply by 3.4121 to get kBtu


        EndUseBreakdown["Lighting"] = (self.lighting_energy(LPD, FloorArea, N_hours_lighting))*3.41 # You get output in kWh so convert into kBtu

        EndUseBreakdown["Electric Equipment"] = baseload_ccp*FloorArea*12 - EndUseBreakdown["Lighting"]

# In[ ]:




