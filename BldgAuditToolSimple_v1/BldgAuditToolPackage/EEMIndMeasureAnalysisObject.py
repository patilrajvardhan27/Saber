

import pandas as pd
import geocoder
import os
# from AnalyzeUtilityData import *
# from PostProcessing import *
from .AnalyzeUtilityData import *
from .PostProcessing import *


class ImplementMeasures:
    def __init__(self,df_input,ProjectPath,BestModelParams):
        self.ProjectPath = ProjectPath
        self.BestModelParams = BestModelParams
        
        self.FloorArea, self.Volume, self.WallArea, self.ExtWallArea, self.WindowArea, self.CeilingArea = GetGeometryParameters(df_input)

    def WallInsulation(self,ExtWallConst,WallInsOrg,WallInsEEM):
        WallConstOptions = pd.read_csv(os.path.join("Inputs","InputCSVData","Construction-Wall.csv"))
        WallConstRvalue = WallConstOptions.loc[WallConstOptions.Construction==ExtWallConst,"Rvalue_IP"].astype(float).iloc[0] #hr-ft2-F/Btu

        WallInsProp = pd.read_csv(os.path.join("Measures","Materials-WallInsulation.csv"))
        if (WallInsOrg != "Uninsulated")&(WallInsOrg != "Unknown"):
            WallInsRvalue_org = WallInsProp.loc[WallInsProp.InsulationName==WallInsOrg,"Rvalue_IP"].astype(float).iloc[0] #hr-ft2-F/Btu

        if (WallInsEEM != "Uninsulated")&(WallInsEEM != "Unknown"):
            WallInsRvalue_EEM = WallInsProp.loc[WallInsProp.InsulationName==WallInsEEM,"Rvalue_IP"].astype(float).iloc[0] #hr-ft2-F/Btu
            
        Delta_BLC = 0

        if WallInsOrg == "Uninsulated": # Uninsulated case
            Delta_BLC = (self.ExtWallArea)*(1/(WallInsRvalue_EEM+WallConstRvalue) - 1/WallConstRvalue)
            BLC_wall_org = (self.ExtWallArea)*(1/WallConstRvalue)
        else:
            Delta_BLC = (self.ExtWallArea)*(1/(WallInsRvalue_EEM+WallConstRvalue) - 1/(WallInsRvalue_org+WallConstRvalue)) 
            BLC_wall_org = (self.ExtWallArea)*(1/(WallInsRvalue_org+WallConstRvalue))

        # Use these ratios only when the BLC calculated is lower than the changein UA value due to wall
        f_Savings = abs(Delta_BLC)/BLC_wall_org # Percentage reduction in BLC of element due to insulation
        f_WallArea = (self.ExtWallArea)/(self.ExtWallArea+self.WindowArea+2*self.FloorArea) # Percentage of wall area as fraction of total envelope area
        


        # Adjust the BLC values only if the savings are less than the BLC value
        # Delta_BLC is negative for a reduction in BLC. So the correction has to be done accordingly.
        if self.BestModelParams["BLC_Heating_NG"] > self.BestModelParams["BLC_Heating_EL"]:
            if self.BestModelParams["BLC_Heating_NG"] > abs(Delta_BLC):
                f_ActSavings = -(Delta_BLC)/self.BestModelParams["BLC_Heating_NG"]
            else:
                f_ActSavings = 1 - ((1-f_WallArea)*self.BestModelParams["BLC_Heating_NG"] + (1-f_Savings)*f_WallArea*self.BestModelParams["BLC_Heating_NG"])/self.BestModelParams["BLC_Heating_NG"]
            self.BestModelParams["NG-HeatingSlope"] = self.BestModelParams["NG-HeatingSlope"]*(1 - f_ActSavings)

        elif self.BestModelParams["BLC_Heating_NG"] < self.BestModelParams["BLC_Heating_EL"]:   
            if self.BestModelParams["BLC_Heating_EL"] > abs(Delta_BLC):
                f_ActSavings = -(Delta_BLC)/self.BestModelParams["BLC_Heating_EL"]
            else:
                f_ActSavings = 1 - ((1-f_WallArea)*self.BestModelParams["BLC_Heating_EL"] + (1-f_Savings)*f_WallArea*self.BestModelParams["BLC_Heating_EL"])/self.BestModelParams["BLC_Heating_EL"]
            self.BestModelParams["EL-HeatingSlope"] = self.BestModelParams["EL-HeatingSlope"]*(1 - f_ActSavings)

        if self.BestModelParams["BLC_Cooling_EL"] > abs(Delta_BLC):
            f_ActSavings = -(Delta_BLC)/self.BestModelParams["BLC_Cooling_EL"]
        else:
            f_ActSavings = 1 - ((1-f_WallArea)*self.BestModelParams["BLC_Cooling_EL"] + (1-f_Savings)*f_WallArea*self.BestModelParams["BLC_Cooling_EL"])/self.BestModelParams["BLC_Cooling_EL"]
        self.BestModelParams["EL-CoolingSlope"] = self.BestModelParams["EL-CoolingSlope"]*(1 - f_ActSavings)

        

        pd.DataFrame([self.BestModelParams]).to_csv(os.path.join(self.ProjectPath,"BestModelParams.csv"), index=False)
        return 
    
    def Infiltration(self,ACH50Org,ACH50EEM):
        # First convert into average infiltration values based on rule of thumb.
        # https://www.aivc.org/sites/default/files/airbase_3097.pdf
        ACHOrg = float(ACH50Org)/20
        ACHEEM = float(ACH50EEM)/20

        VinfOrg = ACHOrg*self.Volume # Convert to cubic ft per hour
        VinfEEM = ACHEEM*self.Volume # Convert to cubic ft per hour
        
        rho_air = 0.0752 # lb/ft3 at 20C and 1atm
        Cp = 0.2402 # Btu/lb-F at 20C and 1atm
        
        # Even though the change in heating BLC is the same you still have to do this separately to ensure that you are only changing an existing BLC
        Delta_BLC = rho_air*Cp*(VinfEEM - VinfOrg)
        
        f_Savings = abs(Delta_BLC)/(rho_air*Cp*VinfOrg) # Percentage reduction in BLC of element due to infiltration change
        # This needs a better estimate. For now, I am assuming that the infiltration is a percentage of the total inverse model BLC
        f_pct = 0.3# Straight up assume a percentage with no reference for this.

        if self.BestModelParams["BLC_Heating_NG"] > self.BestModelParams["BLC_Heating_EL"]:
            if self.BestModelParams["BLC_Heating_NG"] > abs(Delta_BLC):
                f_ActSavings = -Delta_BLC/self.BestModelParams["BLC_Heating_NG"]

            else:
                f_ActSavings = 1 - ((1-f_pct)*self.BestModelParams["BLC_Heating_NG"] + (1-f_Savings)*f_pct*self.BestModelParams["BLC_Heating_NG"])/self.BestModelParams["BLC_Heating_NG"]
            self.BestModelParams["NG-HeatingSlope"] = self.BestModelParams["NG-HeatingSlope"]*(1 - f_ActSavings)
        
        elif self.BestModelParams["BLC_Heating_NG"] < self.BestModelParams["BLC_Heating_EL"]:
            if self.BestModelParams["BLC_Heating_EL"] > abs(Delta_BLC):
                f_ActSavings = -Delta_BLC/self.BestModelParams["BLC_Heating_EL"]
            else:
                f_ActSavings = 1 - ((1-f_pct)*self.BestModelParams["BLC_Heating_EL"] + (1-f_Savings)*f_pct*self.BestModelParams["BLC_Heating_EL"])/self.BestModelParams["BLC_Heating_EL"]
            self.BestModelParams["EL-HeatingSlope"] = self.BestModelParams["EL-HeatingSlope"]*(1 - f_ActSavings)
        
        if self.BestModelParams["BLC_Cooling_EL"] > abs(Delta_BLC):
            f_ActSavings = -Delta_BLC/self.BestModelParams["BLC_Cooling_EL"]
        else:
            #print(f_Savings,f_pct)
            f_ActSavings = 1 - ((1-f_pct)*self.BestModelParams["BLC_Cooling_EL"] + (1-f_Savings)*f_pct*self.BestModelParams["BLC_Cooling_EL"])/self.BestModelParams["BLC_Cooling_EL"]
        self.BestModelParams["EL-CoolingSlope"] = self.BestModelParams["EL-CoolingSlope"]*(1 - f_ActSavings)
        pd.DataFrame([self.BestModelParams]).to_csv(os.path.join(self.ProjectPath,"BestModelParams.csv"), index=False)
        
        return 
        
    def CeilingInsulation(self,ExtRoofConst,CeilConst,CeilingInsOrg,CeilingInsEEM):
        
        RoofConstOptions = pd.read_csv(os.path.join("Inputs","InputCSVData","Construction-Roof.csv"))
        RoofConstRvalue = RoofConstOptions.loc[RoofConstOptions.Construction==ExtRoofConst,"Rvalue_IP"].astype(float).iloc[0] #hr-ft2-F/Btu
        
        CeilingConstOptions = pd.read_csv(os.path.join("Inputs","InputCSVData","Construction-Floor.csv"))
        CeilingConstRvalue = CeilingConstOptions.loc[CeilingConstOptions.Construction==CeilConst,"Rvalue_IP"].astype(float).iloc[0]

        CeilingInsProp = pd.read_csv(os.path.join("Measures","Materials-CeilingInsulation.csv"))
        if (CeilingInsOrg != "Uninsulated") & (CeilingInsOrg != "Unknown"):
            CeilingInsRvalueOrg = CeilingInsProp.loc[CeilingInsProp.InsulationName==CeilingInsOrg,"Rvalue_IP"].astype(float).iloc[0] #hr-ft2-F/Btu
        
        if (CeilingInsEEM != "Uninsulated") & (CeilingInsEEM != "Unknown"):
            CeilingInsRvalueEEM = CeilingInsProp.loc[CeilingInsProp.InsulationName==CeilingInsEEM,"Rvalue_IP"].astype(float).iloc[0] #hr-ft2-F/Btu
        
        Delta_BLC = 0

        if CeilingInsOrg == "Uninsulated": # Uninsulated case
            Delta_BLC = self.FloorArea*(1/(CeilingInsRvalueEEM+CeilingConstRvalue+RoofConstRvalue) - 1/(CeilingConstRvalue+RoofConstRvalue))
            BLC_Ceil_org = self.FloorArea*(1/(CeilingConstRvalue+RoofConstRvalue))
            
        else:
            
            Delta_BLC = self.FloorArea*(1/(CeilingInsRvalueEEM+CeilingConstRvalue+RoofConstRvalue) - 1/(CeilingInsRvalueOrg+CeilingConstRvalue+RoofConstRvalue)) 
            BLC_Ceil_org = self.FloorArea*(1/(CeilingInsRvalueOrg+CeilingConstRvalue+RoofConstRvalue))
        #print("Delta BLC",Delta_BLC)
        #print(self.BestModelParams)
        f_Savings = abs(Delta_BLC)/BLC_Ceil_org # Percentage reduction in BLC of element due to insulation
        f_CeilArea = self.FloorArea/(2*self.FloorArea+self.ExtWallArea+self.WindowArea) # Percentage of ceiling area as fraction of total envelope area

        if self.BestModelParams["BLC_Heating_NG"] > self.BestModelParams["BLC_Heating_EL"]:
            if self.BestModelParams["BLC_Heating_NG"] > abs(Delta_BLC):
                f_ActSavings = -Delta_BLC/self.BestModelParams["BLC_Heating_NG"]
            else:
                f_ActSavings = 1 - ((1-f_CeilArea)*self.BestModelParams["BLC_Heating_NG"] + (1-f_Savings)*f_CeilArea*self.BestModelParams["BLC_Heating_NG"])/self.BestModelParams["BLC_Heating_NG"]
                self.BestModelParams["NG-HeatingSlope"] = self.BestModelParams["NG-HeatingSlope"]*(1 - f_ActSavings)
        
        elif self.BestModelParams["BLC_Heating_NG"] < self.BestModelParams["BLC_Heating_EL"]:
            if self.BestModelParams["BLC_Heating_EL"] > abs(Delta_BLC):
                f_ActSavings = -Delta_BLC/self.BestModelParams["BLC_Heating_EL"]
            else:
                f_ActSavings = 1 - ((1-f_CeilArea)*self.BestModelParams["BLC_Heating_EL"] + (1-f_Savings)*f_CeilArea*self.BestModelParams["BLC_Heating_EL"])/self.BestModelParams["BLC_Heating_EL"]
            self.BestModelParams["EL-HeatingSlope"] = self.BestModelParams["EL-HeatingSlope"]*(1 - f_ActSavings)
        
        if self.BestModelParams["BLC_Cooling_EL"] > abs(Delta_BLC):
            f_ActSavings = -Delta_BLC/self.BestModelParams["BLC_Cooling_EL"]
        else:
            f_ActSavings = 1 - ((1-f_CeilArea)*self.BestModelParams["BLC_Cooling_EL"] + (1-f_Savings)*f_CeilArea*self.BestModelParams["BLC_Cooling_EL"])/self.BestModelParams["BLC_Cooling_EL"]
        self.BestModelParams["EL-CoolingSlope"] = self.BestModelParams["EL-CoolingSlope"]*(1-f_ActSavings)
        
        
        pd.DataFrame([self.BestModelParams]).to_csv(os.path.join(self.ProjectPath,"BestModelParams.csv"), index=False)
        
        return 
        
    def WindowMaterial(self,WindowConstOrg,WindowConstEEM):

        WindowConstOptions = pd.read_csv(os.path.join("Measures","Materials-WindowMaterial.csv"))
        WindowConstUvalueOrg = WindowConstOptions.loc[WindowConstOptions.WindowMaterial==WindowConstOrg,"Uvalue"].astype(float).iloc[0] #hr-ft2-F/Btu
        
        WindowInsUvalueEEM = WindowConstOptions.loc[WindowConstOptions.WindowMaterial==WindowConstEEM,"Uvalue"].astype(float).iloc[0] #hr-ft2-F/Btu
        
        
        Delta_BLC = (self.WindowArea)*(WindowInsUvalueEEM - WindowConstUvalueOrg) 
        BLC_Window_org = (self.WindowArea)*(WindowConstUvalueOrg)

        f_Savings = abs(Delta_BLC)/BLC_Window_org # Percentage reduction in BLC of element due to insulation
        f_WindowArea = (self.WindowArea)/(self.ExtWallArea+self.WindowArea+2*self.FloorArea)

        if self.BestModelParams["BLC_Heating_NG"] > self.BestModelParams["BLC_Heating_EL"]:
            if self.BestModelParams["BLC_Heating_NG"] > abs(Delta_BLC):
                f_ActSavings = -Delta_BLC/self.BestModelParams["BLC_Heating_NG"]
            else:
                f_ActSavings = 1-((1-f_WindowArea)*self.BestModelParams["BLC_Heating_NG"] + (1-f_Savings)*f_WindowArea*self.BestModelParams["BLC_Heating_NG"])/self.BestModelParams["BLC_Heating_NG"]
            self.BestModelParams["NG-HeatingSlope"] = self.BestModelParams["NG-HeatingSlope"]*(1-f_ActSavings)
        
        elif self.BestModelParams["BLC_Heating_NG"] < self.BestModelParams["BLC_Heating_EL"]:
            if self.BestModelParams["BLC_Heating_EL"] > abs(Delta_BLC):
                f_ActSavings = -Delta_BLC/self.BestModelParams["BLC_Heating_EL"]
            else:
                f_ActSavings = 1 - ((1-f_WindowArea)*self.BestModelParams["BLC_Heating_EL"] + (1-f_Savings)*f_WindowArea*self.BestModelParams["BLC_Heating_EL"])/self.BestModelParams["BLC_Heating_EL"]
            self.BestModelParams["EL-HeatingSlope"] = self.BestModelParams["EL-HeatingSlope"]*(1 - f_ActSavings)
        
        if self.BestModelParams["BLC_Cooling_EL"] > abs(Delta_BLC):
            f_ActSavings = -Delta_BLC/self.BestModelParams["BLC_Cooling_EL"]
        else:
            f_ActSavings = 1 - ((1-f_WindowArea)*self.BestModelParams["BLC_Cooling_EL"] + (1-f_Savings)*f_WindowArea*self.BestModelParams["BLC_Cooling_EL"])/self.BestModelParams["BLC_Cooling_EL"]
        self.BestModelParams["EL-CoolingSlope"] = self.BestModelParams["EL-CoolingSlope"]*(1 - f_ActSavings)
        
        
        pd.DataFrame([self.BestModelParams]).to_csv(os.path.join(self.ProjectPath,"BestModelParams.csv"), index=False)
        return 
    
    def OccupancySensorControls(self):
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
        
        
        return percentage_savings
    
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
        
        return lighting_savings
    
    def DaylightingControls(self):
            #%% Daylighting
        #Reference: https://www.aceee.org/files/proceedings/2006/data/papers/SS06_Panel3_Paper19.pdf
        
        daylight_savings = 0.32

        return daylight_savings

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
        elif state == "Utah":
            economizer_savings = .050
        elif state == "Wyoming":
            economizer_savings = .094
        elif state == "Idaho":
            economizer_savings = .091
        elif state == "Montana":
            economizer_savings = .108
        elif state  == None:
            economizer_savings = None    


        self.BestModelParams["EL-CoolingSlope"]  = (1-economizer_savings)*self.BestModelParams["EL-CoolingSlope"]
        pd.DataFrame([self.BestModelParams]).to_csv(os.path.join(self.ProjectPath,"BestModelParams.csv"), index=False)
        return 
    
    #%% Reduce Equipment Load
    def ReduceEquipmentLoad(self,EquipLoadRed):
          
        
        return EquipLoadRed/100
    
    def HeatingEquipment(self,HeatingEqpOrg,HeatingEqpEEM):
        if "HeatPump" in HeatingEqpEEM.replace(" ","") and "GasFurnace" in HeatingEqpOrg.replace(" ",""):
            self.BestModelParams["EL-HeatingChangePoint"] = min(self.BestModelParams["NG-HeatingChangePoint"],self.BestModelParams["EL-HeatingChangePoint"])
            self.BestModelParams["EL-HeatingSlope"] = max(abs(self.BestModelParams["EL-HeatingSlope"]),abs(self.BestModelParams["NG-HeatingSlope"]))
            self.BestModelParams["NG-HeatingSlope"] = 0
        elif "GasFurnace" in HeatingEqpEEM.replace(" ","") and "HeatPump" in HeatingEqpOrg.replace(" ",""):
            self.BestModelParams["NG-HeatingChangePoint"] = min(self.BestModelParams["NG-HeatingChangePoint"],self.BestModelParams["EL-HeatingChangePoint"])
            self.BestModelParams["NG-HeatingSlope"] = max(abs(self.BestModelParams["NG-HeatingSlope"]),abs(self.BestModelParams["EL-HeatingSlope"]))
            self.BestModelParams["EL-HeatingSlope"] = 0
        pd.DataFrame([self.BestModelParams]).to_csv(os.path.join(self.ProjectPath,"BestModelParams.csv"), index=False)
        return
 