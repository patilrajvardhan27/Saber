#!/usr/bin/env python
# coding: utf-8

# In[2]:


from ish_parser import ish_report, ish_reportException
from ftplib import FTP
import gzip
import os
import pandas as pd
import numpy as np


# In[ ]:


class NOAAData:
    def __init__(self, weather_station_list, start_year, end_year, v_start_dates, v_end_dates, frequency):
        self.weather_station_list = weather_station_list
        self.start_year = start_year
        self.end_year = end_year
        self.v_start_dates = v_start_dates
        self.v_end_dates = v_end_dates
        self.frequency = frequency
        
    #Download weather file from NOAA
    def download_weather_NOAA(self):
        print("Downloading weather data...")
        try:
            self.weather_station_ID = self.weather_station_list[0]
            self.weather_station_name = self.weather_station_list[1]
            self.df_new = self.process_downloaded_weather(self.weather_station_ID,self.start_year,self.end_year,self.v_start_dates,self.v_end_dates)
            self.df_temp = self.df_new.copy()
            #print("................", self.df_new.columns)

            # Ensure the index is datetime (in case it's not already)
            self.df_temp.index = pd.to_datetime(self.df_temp.index)

            # Extract the date part from the index
            self.df_temp['DateOnly'] = self.df_temp.index.date

            # Unique actual dates present
            actual_dates = pd.Series(self.df_temp['DateOnly'].unique())

            # Expected full date range
            expected_dates = pd.date_range(
                start=actual_dates.min(),
                end=actual_dates.max(),
                freq='D'
            ).date  # extract just the date part

            missing_dates = sorted(set(expected_dates) - set(actual_dates))
            #print("missing_dates", missing_dates)

            if missing_dates:
                raise ValueError(f"❌ Missing {len(missing_dates)} full dates in df_new: {missing_dates}")

            print("All calendar dates are present in df_new.")

        except Exception as e:
            print("⚠️ Error in first try block:")
            print(e)
            try:
                print("Weather from the closest weather station not available...")
                print("Trying to download the second weather data from the second closest weather station.")
                self.weather_station_ID = self.weather_station_list[2]
                self.weather_station_name = self.weather_station_list[3]
                self.df_new = self.process_downloaded_weather(self.weather_station_ID,self.start_year,self.end_year,self.v_start_dates,self.v_end_dates)
                self.df_temp = self.df_new.copy()

                # Ensure the index is datetime (in case it's not already)
                self.df_temp.index = pd.to_datetime(self.df_temp.index)

                # Extract the date part from the index
                self.df_temp['DateOnly'] = self.df_temp.index.date

                # Unique actual dates present
                actual_dates = pd.Series(self.df_temp['DateOnly'].unique())

                # Expected full date range
                expected_dates = pd.date_range(
                    start=actual_dates.min(),
                    end=actual_dates.max(),
                    freq='D'
                ).date  # extract just the date part

                missing_dates = sorted(set(expected_dates) - set(actual_dates))

                if missing_dates:
                    raise ValueError(f"❌ Missing {len(missing_dates)} full dates in df_new: {missing_dates}")

                print("All calendar dates are present in df_new.")    

            except Exception as e2:
                print("⚠️ Second try block also failed:")
                print(e2)
                print("Weather from the second closest weather station not available...")
                print("Trying to download the third weather data from the third closest weather station.")
                self.weather_station_ID = self.weather_station_list[4]
                self.weather_station_name = self.weather_station_list[5]
                self.df_new = self.process_downloaded_weather(self.weather_station_ID, self.start_year, self.end_year, self.v_start_dates, self.v_end_dates)


        #print("weather data", self.df_new)        
        return self.df_new, self.weather_station_name
        
    def process_downloaded_weather(self,weather_station_ID,start_year,end_year,v_start_dates,v_end_dates):
    
        # Helper functions
        def download_sub_hourly_weather(station_ID, year):
            ftp = FTP('ftp.ncdc.noaa.gov')
            ftp.login()
            ftp_path = '/pub/data/noaa/' + str(year)  # Hourly
            ftp.cwd(ftp_path)
            # Save gz files locally
            file_name_noaa = 'RETR ' + station_ID + '-' + str(year) + '.gz'
            file_name_local = station_ID + '-' + str(year) + '.gz'
            ftp.retrbinary(file_name_noaa, open(file_name_local, 'wb').write)
    
        def save_as_csv(stationID, year):
            file_name_gz = stationID + '-' + str(year) + '.gz'
            file_name_csv = stationID + '-' + str(year) + '.csv'
            with gzip.open(file_name_gz, 'rb') as infile:
                with open(file_name_csv, 'wb') as outfile:
                    for line in infile:
                        outfile.write(line)
            os.remove(file_name_gz)
    
        def get_ish_report_helper(raw_rpt):
            return (ish_report().loads(raw_rpt))
    
        def get_ish_report_datetime_helper(raw_rpt):
            return (raw_rpt.datetime)
    
        def get_ish_report_temperature_helper(raw_rpt):
            return (raw_rpt.air_temperature.get_fahrenheit())
        
        for year in range(start_year, end_year + 1):
            print("--->" + str(year))
            download_sub_hourly_weather(weather_station_ID, year)
            save_as_csv(weather_station_ID, year)
            raw_csv = weather_station_ID + '-' + str(year) + '.csv'
            if (year == start_year):
                df_raw = pd.read_csv(raw_csv, names=['Old'])
            else:
                df_raw = pd.concat([df_raw, pd.read_csv(raw_csv, names=['Old'])], ignore_index=True)
            # Cleaning up
            os.remove(raw_csv)
        # Parse ish text data to readable weather data
        print("Processing downloaded data...")
        v_rpt = list(map(get_ish_report_helper, df_raw['Old']))
        v_noaa_datetime = np.array(list(map(get_ish_report_datetime_helper, v_rpt)))
        v_noaa_temperature_F = np.array(list(map(get_ish_report_temperature_helper, v_rpt)))
        # Sanitize the array
        v_noaa_temperature_F = pd.to_numeric(v_noaa_temperature_F, errors='coerce')
        df_new = pd.DataFrame({'Datetime': v_noaa_datetime, 'Temperature': v_noaa_temperature_F})
        # df_new['Date'] = df_new['Datetime'].dt.date
        #print(df_new)

        # Convert input dates and dataframe column to datetime format
        v_start_dates = np.array(v_start_dates, dtype=np.datetime64)
        v_end_dates = np.array(v_end_dates, dtype=np.datetime64)
        df_new['Datetime'] = np.array(df_new['Datetime'], dtype=np.datetime64)
        #print(df_new, v_start_dates, v_end_dates)
        
    
        # Filter df_daily within the min and max range of given dates
        df_new = df_new.loc[(df_new['Datetime'] >= min(v_start_dates)) &
                                (df_new['Datetime'] <= max(v_end_dates))]
        
        df_new = df_new.set_index('Datetime')
        df_new["Temp_C"] = (df_new["Temperature"] - 32) / 1.8
        df_new = df_new.rename(columns={"Temperature": "Temp_F"})
        # print("df_new", df_new)
        return df_new
        
        
        # if self.frequency == "month":
        #     v_T_F, v_T_C, data = self.aggregate_weather_month(df_new,v_start_dates,v_end_dates)
        # elif self.frequency == "day":
        #     v_T_F, v_T_C, data = self.aggregate_weather_day(df_new,v_start_dates,v_end_dates)
        # elif self.frequency == "hour":
        #     v_T_F, v_T_C, data = self.aggregate_weather_hour(df_new,v_start_dates,v_end_dates)
        # return(v_T_F,v_T_C,data)
    
    #Aggregate NOAA temperateure date to produce monthly average
    def aggregate_weather_month(self, df_daily, v_start_dates, v_end_dates):
        # Initialize arrays to store results
        v_avg_period_T_F = np.empty(0, dtype=float)
        months = []  # Store corresponding months
    
        v_temp_datetime = np.array(df_daily['Datetime'], dtype=np.datetime64)
    
        # Loop over billing periods to compute average temperatures
        for i in range(len(v_start_dates)):
            df_temp = df_daily.loc[(v_temp_datetime >= v_start_dates[i]) &
                                   (v_temp_datetime <= v_end_dates[i])]
            
            avg_temp_f = df_temp['Temperature'].mean()
            v_avg_period_T_F = np.append(v_avg_period_T_F, avg_temp_f)
            
            # Extract the month from the start date of the period
            months.append(pd.to_datetime(v_start_dates[i]).strftime('%B'))  
    
        # Convert Fahrenheit to Celsius
        v_avg_period_T_C = (v_avg_period_T_F - 32) / 1.8
    
        # Create a DataFrame with "Month", "Avg_Temperature_F", and "Avg_Temperature_C"
        df_monthly_avg = pd.DataFrame({
            "Month": months,
            "Avg_Temperature_F": v_avg_period_T_F,
            "Avg_Temperature_C": v_avg_period_T_C
        })

        
    
        # Sort by month order to maintain correct chronological order
        #month_order = [
        #    "January", "February", "March", "April", "May", "June",
        #    "July", "August", "September", "October", "November", "December"
        #]
        #df_monthly_avg["Month"] = pd.Categorical(df_monthly_avg["Month"], categories=month_order, ordered=True)
        #df_monthly_avg = df_monthly_avg.sort_values("Month")
        return (v_avg_period_T_F, v_avg_period_T_C, df_monthly_avg)

    #Aggregate NOAA temperateure date to produce daily average
    def aggregate_weather_day(self, df_daily,v_start_dates, v_end_dates):    
        df_temp = pd.DataFrame()
        df_temp["Temperature"] = df_daily["Temperature"]
        df_temp["Date"] = df_daily["Date"]
        # Compute daily average temperature
        df_daily_avg = df_temp.groupby(['Date'], as_index=False)['Temperature'].mean()
        df_daily_avg.rename(columns={'Temperature': 'Avg_Temperature_F'}, inplace=True)
        # Convert to Celsius
        df_daily_avg['Avg_Temperature_C'] = (df_daily_avg['Avg_Temperature_F'] - 32) / 1.8
        return (np.array(df_daily_avg['Avg_Temperature_F']), np.array(df_daily_avg['Avg_Temperature_C']),df_daily_avg)    

        #Aggregate NOAA temperateure date to produce hourly average
    def aggregate_weather_hour(self, df_daily,v_start_dates, v_end_dates):    
        df_temp = pd.DataFrame()
        df_temp["Temperature"] = df_daily["Temperature"]
        df_temp["Date"] = df_daily["Date"]
        # Compute daily average temperature
        df_temp.rename(columns={'Temperature': 'Avg_Temperature_F'}, inplace=True)
        # Convert to Celsius
        df_temp['Avg_Temperature_C'] = (df_temp['Avg_Temperature_F'] - 32) / 1.8
        return (np.array(df_temp['Avg_Temperature_F']), np.array(df_temp['Avg_Temperature_C']), df_daily)  

