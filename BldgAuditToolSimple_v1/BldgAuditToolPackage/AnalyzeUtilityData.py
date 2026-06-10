import pandas as pd
import os

# from weather_station import WeatherStation
# from NOAA_Data import NOAAData
# from model import *
# from graph import *
# from degreeday import *
# from EnergyAnalysis import *
# from PostProcessing import *

from .weather_station import WeatherStation
from .NOAA_Data import NOAAData
from .model import *
from .graph import *
from .degreeday import *
from .EnergyAnalysis import *
from .PostProcessing import *


import plotly.graph_objects as go
import calendar

#%% PARSE UTILITY DATA TO GET STARTING AND ENDING TIMES
def ParseUtilityData(ProjectPath,ProjectName):
    dfutildata = pd.read_csv(os.path.join(ProjectPath,ProjectName+"_UtilityData.csv"),index_col=0)
    
    dfutildata["Month"] = range(1, 13)
    dfutildata = dfutildata.drop(columns=["BillDays"])
    # Melt the data for easier processing
    df_melted = dfutildata.melt(id_vars=["Month"], var_name="Year_Energy", value_name="Value")
    df_melted.dropna(subset=["Value"], inplace=True)
    
    # Extract Year from the column name
    df_melted["Year"] = df_melted["Year_Energy"].str[-4:].astype(int)
    
    start_row = df_melted.iloc[0]
    end_row = df_melted.iloc[-1]
    
    start_year, start_month = start_row["Year"], start_row["Month"]
    end_year, end_month = end_row["Year"], end_row["Month"]
    
    start_dates = pd.date_range(start=f"{start_year}-{start_month:02d}-01", 
                            end=f"{end_year}-{end_month:02d}-01", 
                            freq="MS").tolist()  # 'MS' = Month Start

    # Generate end dates (last day of each month)
    end_dates = pd.date_range(start=f"{start_year}-{start_month:02d}-01", 
                              end=f"{end_year + (end_month // 12)}-{(end_month % 12) + 1:02d}-01", 
                              freq="M").tolist()  # 'M' = Month End
    #print(start_dates, end_dates, end_month, start_month, len(start_dates), len(end_dates))
    
    return start_dates,end_dates,start_year,end_year
#%% DOWNLOAD WEATHER DATA FROM CLOSEST WEATHER STATION USING NOAA DATABASE
def GetWeather(ProjectPath,ProjectName,bldg_location):
    v_start_dates,v_end_dates,start_year,end_year = ParseUtilityData(ProjectPath,ProjectName)
    
    WeatherStat = WeatherStation(bldg_location)
    weather_station_list = WeatherStat.find_closest_weather_station()
    # print(weather_station_list)
    NOAADat = NOAAData(weather_station_list, start_year, end_year, v_start_dates, v_end_dates, "hour")
    df_new,weather_station_name = NOAADat.download_weather_NOAA()
    
    df_new = df_new.dropna()
    df_new.to_csv(os.path.join(ProjectPath,"WeatherData"+weather_station_name+".csv"))
    #print(df_new)
    return df_new,weather_station_name


#%% BUILD TEMPERATURE AND DD BASED CHANGE POINT MODELS 


class BuildChangePointModel:
    def __init__(self,ProjectPath,ProjectName,df_input,df_weather):

        self.ProjectPath = ProjectPath
        self.df_weather = df_weather.copy()
        self.df_month = self.df_weather.resample("M").mean()
        self.df_day = self.df_weather.resample("24H").mean()

        FloorArea = df_input.loc[df_input.PropKey=="FloorArea","PropValue"].astype(float).iloc[0]
        dfutildata = pd.read_csv(os.path.join(ProjectPath,ProjectName+"_UtilityData.csv"),index_col=0)
        dfutildata["Month"] = range(1, 13)
        
        # First sort out the electricity and fossil fuel data
        dfkWh = dfutildata.loc[:, dfutildata.columns.str.contains("kWh")].copy()
        dfTherm = dfutildata.loc[:, dfutildata.columns.str.contains("Therms")].copy()
        
        # Add Month and BillDays 
        dfkWh[["Month", "BillDays"]] = dfutildata.loc[:, ["Month", "BillDays"]].copy()
        dfTherm[["Month", "BillDays"]] = dfutildata.loc[:, ["Month", "BillDays"]].copy()

        # Melt the data frame so you get one column with kWh and Therm values
        dfkWhMelted = dfkWh.melt(id_vars=["Month", "BillDays"], var_name="Energy_Type", value_name="kWh")
        dfThermMelted = dfTherm.melt(id_vars=["Month", "BillDays"], var_name="Energy_Type", value_name="Therms")
        
        # Concatenate and align columns properly
        self.dfutilDataSorted = pd.concat([dfkWhMelted, dfThermMelted["Therms"]], axis=1)
        
        # Drop NaN values correctly (ensuring correct column names)
        self.dfutilDataSorted.dropna(subset=["kWh", "Therms"], inplace=True)
        
        # Get the year value
        self.dfutilDataSorted["Year"] = self.dfutilDataSorted["Energy_Type"].str[-4:].astype(int)
        
        
        self.dfutilDataSorted['Electricity/day'] = self.dfutilDataSorted['kWh']/self.dfutilDataSorted['BillDays']
        self.dfutilDataSorted['Fossil Fuel/day'] = self.dfutilDataSorted['Therms']/self.dfutilDataSorted['BillDays']*100
        self.dfutilDataSorted['Electricity/day/sqft'] = self.dfutilDataSorted['kWh']/self.dfutilDataSorted['BillDays']/FloorArea*3.41 #convert kwh to kbtu
        self.dfutilDataSorted['Fossil Fuel/day/sqft'] = self.dfutilDataSorted['Therms']/self.dfutilDataSorted['BillDays']/FloorArea*100 #convert therms to kbtu
        self.dfutilDataSorted['Electricity/sqft'] = self.dfutilDataSorted['kWh']/FloorArea*3.41 #convert kwh to kbtu
        self.dfutilDataSorted['Fossil Fuel/sqft'] = self.dfutilDataSorted['Therms']/FloorArea*100 #convert therms to kbtu

        self.start_dates,self.end_dates,self.start_year,self.end_year = ParseUtilityData(self.ProjectPath,ProjectName)

        return 

    def BuildTemperatureBasedModel(self):

        if (self.dfutilDataSorted['Electricity/day/sqft'] != 0).all():
            electricity_cp = InverseModel(self.df_month["Temp_F"].values, self.dfutilDataSorted['Electricity/day/sqft'], 'Electricity')
            """Edited to make the R2 value correct"""
            has_fit_cooling, model_type_cooling, model_parameters_cooling, model_r2 = electricity_cp.fit_model() #paramter order: hcp,ccp,base,hsl,csl
            """Edited to make the R2 value correct"""
            r_sq = model_r2
            """Edited to make the R2 value correct"""
            Plot_Matplotlib("Electricity", model_type_cooling, model_parameters_cooling, model_r2, self.df_month["Temp_F"].values,self.dfutilDataSorted['Electricity/day/sqft']).plot_graph_cp(self.ProjectPath)
            model_parameters_cooling = np.append(model_parameters_cooling, r_sq)  
        else:
           model_type_cooling = "No fit"
           model_parameters_cooling = np.array([0, 0, 0, 0, 0])
           has_fit_cooling = "No fit"
           r_sq = 0
           model_parameters_cooling = np.append(model_parameters_cooling, r_sq) 

        if (self.dfutilDataSorted['Fossil Fuel/day/sqft'] != 0).all():    
            fossilfuel_cp = InverseModel(self.df_month["Temp_F"].values, self.dfutilDataSorted['Fossil Fuel/day/sqft'], 'Fossil Fuel')
            """Edited to make the R2 value correct"""
            has_fit_heating, model_type_heating, model_parameters_heating, model_r2 = fossilfuel_cp.fit_model() #paramter order: hcp,ccp,base,hsl,csl
            """Edited to make the R2 value correct"""
            r_sq = model_r2
            """Edited to make the R2 value correct"""
            print("model_type_heating", model_type_heating, "model_parameters_heating", model_parameters_heating, "model_r2_heating", model_r2)
            Plot_Matplotlib("Fossil Fuel", model_type_heating, model_parameters_heating, model_r2, self.df_month["Temp_F"].values,self.dfutilDataSorted['Fossil Fuel/day/sqft']).plot_graph_cp(self.ProjectPath)
            model_parameters_heating = np.append(model_parameters_heating, r_sq)
        else:
            model_type_heating = 'No fit'
            model_parameters_heating = np.array([0, 0, 0, 0, 0])   
            has_fit_heating = "No fit" 
            r_sq = 0
            model_parameters_heating = np.append(model_parameters_heating, r_sq)
        #print("Cooling: ",has_fit_cooling, model_type_cooling, model_parameters_cooling)
        #print("Heating: ",has_fit_heating, model_type_heating, model_parameters_heating)


        return model_type_cooling, model_parameters_cooling,  model_type_heating, model_parameters_heating

    def BuildDegreeDayBasedModel(self,model_type_cooling, model_parameters_cooling,  model_type_heating, model_parameters_heating):
        DDResults = {}
        DDResults["NG-HeatingModelType"] = model_type_heating
        DDResults["NG-HeatingBaseload"] = np.nan #kBtu/sft
        DDResults["NG-HeatingChangePoint"] = np.nan
        DDResults["NG-HeatingSlope"] = np.nan
        DDResults["NG-HeatingR2"] = np.nan
        DDResults["EL-CoolingModelType"] = model_type_cooling
        DDResults["EL-CoolingBaseload"] = np.nan
        DDResults["EL-CoolingChangePoint"] = np.nan
        DDResults["EL-CoolingSlope"] = np.nan
        DDResults["EL-CoolingR2"] = np.nan
        DDResults["EL-HeatingModelType"] = model_type_cooling
        DDResults["EL-HeatingBaseload"] = np.nan
        DDResults["EL-HeatingChangePoint"] = np.nan
        DDResults["EL-HeatingSlope"] = np.nan
        DDResults["EL-HeatingR2"] = np.nan

        if model_parameters_heating[3] != 0:
            ddh = DegreeDay(self.dfutilDataSorted['Fossil Fuel/sqft'], self.df_day["Temp_F"].values, model_parameters_heating, self.df_day, self.start_dates, self.end_dates)
            #print(ddh)
            figure_hcp, baseload_hcp, hcp, slope_hcp, r_squared_hcp = ddh.heating_degree_day("NaturalGas")
            #print(baseload_hcp, hcp, slope_hcp)
            #figure_hcp.show()
            figure_hcp.savefig(os.path.join(self.ProjectPath,"Results","FossilFuel_Heating_DDBasedChngPtModel.png"), dpi=300)

            DDResults.update({"NG-HeatingBaseload": baseload_hcp}) #kBtu/sft
            DDResults.update({"NG-HeatingChangePoint": hcp})
            DDResults.update({"NG-HeatingSlope":slope_hcp})
            DDResults.update({"NG-HeatingR2":r_squared_hcp})
        else:
            baseload_hcp = 0 #baseload_hcp not defined if previous if is not True
            DDResults.update({"NG-HeatingBaseload": baseload_hcp}) #kBtu/sft
            

        if model_type_cooling == "3P Cooling":
            if model_parameters_cooling[4] != 0:
                ddc = DegreeDay(self.dfutilDataSorted['Electricity/sqft'], self.df_day["Temp_F"].values, model_parameters_cooling, self.df_day, self.start_dates, self.end_dates)
                figure_ccp, baseload_ccp, ccp, slope_ccp, r_squared_ccp = ddc.cooling_degree_day()
                #figure_ccp.show()
                figure_ccp.savefig(os.path.join(self.ProjectPath,"Results","Electricity_Cooling_DDBasedChngPtModel.png"), dpi=300)
                DDResults.update({"EL-CoolingBaseload":baseload_ccp}) #kBtu/sft
                DDResults.update({"EL-CoolingChangePoint": ccp})
                DDResults.update({"EL-CoolingSlope":slope_ccp})
                DDResults.update({"EL-CoolingR2":r_squared_ccp})
            

        elif model_type_cooling == "3P Heating":
            if model_parameters_cooling[3] != 0:
                ddh = DegreeDay(self.dfutilDataSorted['Electricity/sqft'], self.df_day["Temp_F"].values, model_parameters_cooling, self.df_day, self.start_dates, self.end_dates)
                figure_hcp, baseload_hcp, hcp, slope_hcp, r_squared_hcp = ddh.heating_degree_day("Electric")
                #figure_ccp.show()
                figure_hcp.savefig(os.path.join(self.ProjectPath,"Results","Electricity_Heating_DDBasedChngPtModel.png"), dpi = 300)
                DDResults.update({"EL-HeatingBaseload":baseload_hcp}) #kBtu/sft
                DDResults.update({"EL-HeatingChangePoint":hcp})
                DDResults.update({"EL-HeatingSlope":slope_hcp})
                DDResults.update({"EL-HeatingR2":r_squared_hcp})

            
        elif model_type_cooling != "No fit":
            if model_parameters_cooling[4] != 0:
                mask = self.df_month["Temp_F"].values >= model_parameters_cooling[0]
                #print(mask)
                ddc = DegreeDay(self.dfutilDataSorted['Electricity/sqft'], self.df_day["Temp_F"].values, model_parameters_cooling, self.df_day, self.start_dates, self.end_dates)
                figure_ccp, baseload_ccp, ccp, slope_ccp, r_squared_ccp = ddc.cooling_degree_day (mask = mask)
                #figure_ccp.show()
                figure_ccp.savefig(os.path.join(self.ProjectPath,"Results","Electricity_Cooling_DDBasedChngPtModel.png"), dpi = 300)
                DDResults.update({"EL-CoolingBaseload":baseload_ccp}) #kBtu/sft
                DDResults.update({"EL-CoolingChangePoint": ccp})
                DDResults.update({"EL-CoolingSlope":slope_ccp})
                DDResults.update({"EL-CoolingR2":r_squared_ccp})
            
            if model_parameters_cooling[3] != 0:
                mask = self.df_month["Temp_F"].values <= model_parameters_cooling[1]
                #print(mask)
                ddh = DegreeDay(self.dfutilDataSorted['Electricity/sqft'], self.df_day["Temp_F"].values, model_parameters_cooling, self.df_day, self.start_dates, self.end_dates)
                figure_hcp, baseload_hcp, hcp, slope_hcp, r_squared_hcp = ddh.heating_degree_day("Electric",mask = mask)
                #figure_ccp.show()
                figure_hcp.savefig(os.path.join(self.ProjectPath,"Results","Electricity_Heating_DDBasedChngPtModel.png"), dpi = 300)
                DDResults.update({"EL-HeatingBaseload": baseload_hcp}) #kBtu/sft
                DDResults.update({"EL-HeatingChangePoint": hcp})
                DDResults.update({"EL-HeatingSlope": slope_hcp})
                DDResults.update({"EL-HeatingR2": r_squared_hcp})

        DDResults = {key: 0 if isinstance(val, float) and np.isnan(val) else val for key, val in DDResults.items()} #replace nan with 0
        # print(DDResults,self.dfutilDataSorted.reset_index(drop=True))
        return DDResults,self.dfutilDataSorted.reset_index(drop=True)
    
    def ChooseBestModel(self,DDResults,model_parameters_heating,model_parameters_cooling,RunDir):  #paramter order: hcp,ccp,base,hsl,csl
        BestModel = DDResults.copy()
        print("MPC",model_parameters_cooling)
        print("MPH",model_parameters_heating)
        # if DDResults["NG-HeatingSlope"]:
        if DDResults["NG-HeatingR2"] < model_parameters_heating[-1]:
            BestModel["NG-HeatingChangePoint"] = model_parameters_heating[0]
            BestModel["NG-HeatingSlope"] = model_parameters_heating[3]
            BestModel["NG-HeatingR2"] = model_parameters_heating[-1]
            BestModel["NG-HeatingBaseload"] = model_parameters_heating[2]*30
        
        # if DDResults["EL-CoolingSlope"]:
        if DDResults["EL-CoolingR2"] < model_parameters_cooling[-1]:
            BestModel["EL-CoolingChangePoint"] = model_parameters_cooling[1]
            BestModel["EL-CoolingSlope"] = model_parameters_cooling[4]
            BestModel["EL-CoolingR2"] = model_parameters_cooling[-1]
            BestModel["EL-CoolingBaseload"] = model_parameters_cooling[2]*30
        
        # if DDResults["EL-HeatingSlope"]:
        if DDResults["EL-HeatingR2"] < model_parameters_cooling[-1]:
            BestModel["EL-HeatingChangePoint"] = model_parameters_cooling[0]
            BestModel["EL-HeatingSlope"] = model_parameters_cooling[3]
            BestModel["EL-HeatingR2"] = model_parameters_cooling[-1]
            BestModel["EL-HeatingBaseload"] = model_parameters_cooling[2]*30

        pd.DataFrame([BestModel]).to_csv(os.path.join(RunDir,"BestModelParams.csv"))
        return BestModel
        

# ProjectPath = "C:/Users/phani/OneDrive - UCB-O365/Phani_Vadali/Work/EnergyModels/BuildingAuditTool/BldgAuditToolSimple_v1/Projects/LakewoodTestCase"
# ProjectName = "LakewoodTestCase"
# df_input = pd.read_pickle(ProjectPath+"/BldgPropInputFile-Baseline.pkl")
# bldg_location="Lakewood CO"
# df_weather,weather_station_name = GetWeather(ProjectPath,ProjectName,bldg_location)

# CPT = BuildChangePointModel(ProjectPath,ProjectName,df_input,df_weather)
# model_type_cooling, model_parameters_cooling,  model_type_heating, model_parameters_heating = CPT.BuildTemperatureBasedModel()
# DDResults,dfutilDataSorted = CPT.BuildDegreeDayBasedModel(model_type_cooling, model_parameters_cooling,  model_type_heating, model_parameters_heating)


# EnergyEndUse = Energy(DDResults,df_weather,df_input)

# df_MonthlyEndUse = pd.DataFrame(columns=["Space Heating","DHW Heating","Space Cooling","Lighting","Electric Equipment","BLC","BLC_C","HDD","CDD"])
# for m in set(df_weather.index.month):
#     df_day_i = df_weather.loc[df_weather.index.month == m].resample("24H").mean()
#     df_MonthlyEndUse = pd.concat([df_MonthlyEndUse,pd.DataFrame([EnergyEndUse.EndUseBreakdown(df_day_i)],columns=df_MonthlyEndUse.columns)])

# df_MonthlyEndUse = df_MonthlyEndUse.astype(float).reset_index(drop=True)

# PltRes = PlotResults(ProjectPath,False)
# PltRes.PlotEndUseBreakdown(df_MonthlyEndUse)
# PltRes.PlotInverseModelComparison(df_MonthlyEndUse, dfutilDataSorted)







