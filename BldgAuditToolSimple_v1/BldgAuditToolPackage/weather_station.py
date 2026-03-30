#!/usr/bin/env python
# coding: utf-8

# In[7]:


import pandas as pd
import geocoder
# from constants import *
from .constants import *
import numpy as np


# In[8]:


class WeatherStation:

    def __init__(self, address):
        #extracting longitude and latitude of the building location
        self.bldg_geo_coder = geocoder.google(address)
        if (self.bldg_geo_coder.latlng is None):
            self.bldg_geo_coder = geocoder.arcgis(address)
        if (self.bldg_geo_coder.latlng is None):
            self.bldg_geo_coder = geocoder.bing(address)
        if (self.bldg_geo_coder.latlng is None):
            self.bldg_geo_coder = geocoder.baidu(address)
            
        self.bldg_coord = self.bldg_geo_coder.latlng
        self.bldg_latitude, self.bldg_longitude = self.bldg_coord
        self.bldg_geo_address = self.bldg_geo_coder.address
        #weather station details. NOAA weather station list
        self.weather_stations = Constants.df_us_weather_station
        #weather_stations = self.find_closest_weather_station()
        #return(weather_stations)

    # In[9]:
    
    #calculating great circle distance between weather station and bulidng location
    def haversine_distance(lat1, lon1, lat2, lon2):
        # Get radians from decimals
        r_lat1, r_lon1, r_lat2, r_lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
        # Calculate the distance between the two locations
        temp = np.sin((r_lat2 - r_lat1) / 2) ** 2 + np.cos(r_lat1) * np.cos(r_lat2) * np.sin((r_lon2 - r_lon1) / 2) ** 2
        distance = 2 * Constants.earth_radius * np.arcsin(np.sqrt(temp))
        return (distance)
    
    # In[11]:
    
    # Find the closest, second, adn third closest weather station
    def find_closest_weather_station(self):
        self.coord = np.asarray(self.weather_stations[['latitude', 'longitude']].values)
        self.distance = [WeatherStation.haversine_distance(self.bldg_latitude, self.bldg_longitude, coord[0], coord[1])
                      for coord in self.coord]
        self.closest_index = np.argmin(self.distance)
        self.second_closest_index = np.argpartition(self.distance, 2)[2]
        self.third_closest_index = np.argpartition(self.distance, 3)[3]
    
        self.closest_weather_station_ID = self.weather_stations.loc[self.closest_index, 'station_ID']
        self.closest_weather_station_name = self.weather_stations.loc[self.closest_index, 'station_name']
        self.second_closest_weather_station_ID = self.weather_stations.loc[self.second_closest_index, 'station_ID']
        self.second_closest_weather_station_name = self.weather_stations.loc[self.second_closest_index, 'station_name']
        self.third_closest_weather_station_ID = self.weather_stations.loc[self.third_closest_index, 'station_ID']
        self.third_closest_weather_station_name = self.weather_stations.loc[self.third_closest_index, 'station_name']
    
        return([self.closest_weather_station_ID,self.closest_weather_station_name, self.second_closest_weather_station_ID, self.second_closest_weather_station_name, self.third_closest_weather_station_ID, self.third_closest_weather_station_name])


# In[ ]:




