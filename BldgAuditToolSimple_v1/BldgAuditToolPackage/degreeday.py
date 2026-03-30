#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import plotly.graph_objects as go
import statsmodels.api as sm
from scipy.stats import linregress
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

#pd.set_option('display.max_rows', None)  # Show all rows
#pd.set_option('display.max_columns', None)  # Show all columns
#pd.set_option('display.width', None)  # Adjust width to prevent line breaks
#pd.set_option('display.max_colwidth', None)  # Show full content in each cell

# In[2]:


class DegreeDay:
    def __init__(self, eui, oat, model_parameters, df_new, v_start_dates, v_end_dates):
        self.hcp = model_parameters[0]
        self.ccp = model_parameters[1]
        self.base = model_parameters[2]
        self.hsl = model_parameters[3]
        self.csl = model_parameters[4]
        self.eui = eui
        self.oat = oat
        self.df_new = df_new
        self.df_date_range = pd.DataFrame()
        self.df_date_range ["Start Date"] = v_start_dates
        #print(self.df_date_range, v_end_dates, len(self.df_date_range), len(v_end_dates) )
        self.df_date_range ["End Date"] = v_end_dates
        
    def heating_degree_day(self,heatingtype, mask = None):
        df_DDh = []
        df_DDh = pd.DataFrame({"OAT": self.oat})
        df_DDh["hcp"] = self.hcp
        df_DDh["Dates"] = self.df_new.index.values 

        # Define range of heating change points (hcp-10 to hcp+10 at 1-degree intervals)
        hcp_range = np.arange(self.hcp - 10, self.hcp + 11, 1)  # Includes hcp+10

        # Dictionary to store generated column names
        degree_day_cols = []
        
        # Compute HDD for each heating change point in the range
        for hcp in hcp_range:
            column_name = f"Degree Day Heating {hcp:.2f}"
            df_DDh[column_name] = np.where(hcp - df_DDh["OAT"] < 0, 0, hcp - df_DDh["OAT"])
            degree_day_cols.append(column_name)  # Store column name
            
        '''
        column_name = f"Degree Day Heating {self.hcp:.2f}"  # Use first hcp value for naming
        df_DDh[column_name] = np.where(df_DDh["hcp"] - df_DDh["OAT"] < 0, 0, df_DDh["hcp"] - df_DDh["OAT"])
    
        self.step_minus10 = self.hcp - 10
        column_name = f"Degree Day Heating {self.step_minus10:.2f}"
        df_DDh[column_name] = np.where(self.step_minus10 - df_DDh["OAT"] < 0, 0, self.step_minus10 - df_DDh["OAT"])
    
        self.step_minus5 = self.hcp - 5
        column_name = f"Degree Day Heating {self.step_minus5:.2f}"
        df_DDh[column_name] = np.where(self.step_minus5 - df_DDh["OAT"] < 0, 0, self.step_minus5 - df_DDh["OAT"])
    
        self.step_plus5 = self.hcp + 5
        column_name = f"Degree Day Heating {self.step_plus5:.2f}"
        df_DDh[column_name] = np.where(self.step_plus5 - df_DDh["OAT"] < 0, 0, self.step_plus5 - df_DDh["OAT"])
    
        self.step_plus10 = self.hcp + 10
        column_name = f"Degree Day Heating {self.step_plus10:.2f}"
        df_DDh[column_name] = np.where(self.step_plus10 - df_DDh["OAT"] < 0, 0, self.step_plus10 - df_DDh["OAT"])
        '''
    
        df_DDh["Dates"] = pd.to_datetime(df_DDh["Dates"]).dt.date
        self.df_date_range ["Start Date"] = pd.to_datetime(self.df_date_range ["Start Date"]).dt.date
        self.df_date_range ["End Date"] = pd.to_datetime(self.df_date_range ["End Date"]).dt.date
        #print(df_DDh["Dates"], self.df_date_range ["Start Date"], self.df_date_range ["End Date"])

        '''
        # List of columns to sum
        degree_day_cols = [
            f"Degree Day Heating {self.hcp:.2f}", 
            f"Degree Day Heating {self.step_minus10:.2f}", 
            f"Degree Day Heating {self.step_minus5:.2f}", 
            f"Degree Day Heating {self.step_plus5:.2f}", 
            f"Degree Day Heating {self.step_plus10:.2f}"
        ]
        '''
        
        # Group by start and end date and sum the degree day heating values
        for value_col in degree_day_cols:
            sum_values = []
            for _, row in self.df_date_range.iterrows():
                start_date, end_date = row["Start Date"], row["End Date"]
                
                # Sum values from df_values where Date is within the range
                total_sum = df_DDh[(df_DDh["Dates"] >= start_date) & (df_DDh["Dates"] <= end_date)][value_col].sum()
        
                sum_values.append(total_sum)
        
            self.df_date_range[f"{value_col}"] = sum_values

        if mask is not None:
            self.df_date_range = self.df_date_range.reset_index(drop=True)
            self.df_date_range = self.df_date_range[mask].reset_index(drop=True)
            self.eui = self.eui.reset_index(drop=True)
            self.eui = self.eui[mask].reset_index(drop=True)
        #print(self.df_date_range)
        #self.df_monthly = df_DDh.groupby("Year_Month")[degree_day_cols].sum().reset_index(drop = True)
        #print("df_DDh", df_DDh)
    
        # Define month order for correct sorting
        #month_order = [
        #    "January", "February", "March", "April", "May", "June", 
        #    "July", "August", "September", "October", "November", "December"
        #]
        
        # Sort DataFrame by chronological order of months
        #self.df_monthly["Month"] = pd.Categorical(self.df_monthly["Month"], categories=month_order, ordered=True)
        #self.df_monthly = self.df_monthly.sort_values("Month")
        #self.df_monthly = self.df_monthly.reset_index(drop=True)
    
        # Define colors for consistency between data points and lines
        #num_colors = len(np.arange(self.hcp - 10, self.hcp + 11, 1))  # Count of heating change points
        #colors = [mcolors.to_hex(plt.cm.tab10(i % 10)) for i in range(num_colors)]  # Convert to HEX
    
        # Plot using Matplotlib
        fig, ax = plt.subplots(figsize=(8, 6))

        '''
        # List of Degree Day Heating columns and their corresponding numeric values
        degree_day_cols = [
            f"Degree Day Heating {self.hcp:.2f}", 
            f"Degree Day Heating {self.step_minus10:.2f}", 
            f"Degree Day Heating {self.step_minus5:.2f}", 
            f"Degree Day Heating {self.step_plus5:.2f}", 
            f"Degree Day Heating {self.step_plus10:.2f}"
        ]
        '''
        col_numeric_values = np.arange(self.hcp - 10, self.hcp + 11, 1).tolist()
    
        # Variables to track the highest R² regression
        best_r_squared = -1
        best_intercept = None
        best_numeric = None
        best_slope = None
        best_X = None
        best_col = None
        best_Y = None
        
        # Loop through each Degree Day Heating column
        for i, col in enumerate(degree_day_cols):
            # Filter out rows where the degree day value or self.eui is zero
            #mask = (self.df_date_range[col] != 0) & (self.eui != 0)
            #mask = (self.df_date_range[col] > 1) & (self.eui > 1)
            #X = self.df_date_range[col][mask].values  # Independent variable (Degree Day Heating)
            #Y = self.eui[mask].values  # Dependent variable
            X = self.df_date_range[col].values  # Independent variable (Degree Day Heating)
            #print("X", X.shape)
            Y = self.eui.values  # Dependent variable
            #print("Y", Y.shape, Y)
            #print("mask", mask, "eui", self.eui, "DD", self.df_date_range)
            
            # Compute mean and standard deviation of X
            #X_mean = np.mean(X)
            #X_std = np.std(X)
        
            # Define the valid range (within 1 standard deviation)
            #lower_bound = X_mean - X_std
            #upper_bound = X_mean + X_std
        
            # Create mask to keep values within 1 standard deviation
            #std_mask = (X >= lower_bound) & (X <= upper_bound)

            #print("heating mask", std_mask)
            
            # Apply the mask to X and Y
            #X_filtered = X[std_mask]
            #Y_filtered = Y[std_mask]

            #print(X_filtered.shape, Y_filtered.shape, X.shape, Y.shape)
       
            #print("X",X)
            if X.size == 0 or Y.size == 0:
                continue
            # Add constant for regression
            X_const = sm.add_constant(X)
    
            #print("Y", Y.shape)
            #print("X_const", X_const.shape)
            # Fit linear regression model
            model = sm.OLS(Y, X_const).fit()
            intercept, slope = model.params
    
            # Compute R-squared value
            r_squared = model.rsquared
        
            # Update best regression if current r_squared is higher
            if r_squared > best_r_squared and intercept > 0:
                best_r_squared = r_squared
                best_intercept = intercept
                best_slope = slope
                best_numeric = col_numeric_values[i]
                best_X = X
                best_Y = Y
                best_col = col
                #print("X",X)

        # Scatter plot for actual data points
        ax.scatter(best_X.flatten(), best_Y.flatten(), c= "#000000", alpha=0.7)
        
        # Generate trendline values, ensuring it extends to the y-axis
        x_vals = np.linspace(0, max(best_X) * 1.1, 100)  # Extend slightly beyond max X
        y_vals = best_intercept + best_slope * x_vals
       
        # Add best-fit line
        ax.plot(x_vals.flatten(), y_vals.flatten(), label=f"{best_col}°F\nIntercept={best_intercept:.5e} $\\frac{{\\text{{kBtu}}}}{{\\text{{ft}}^2}}$, R²={best_r_squared:.2f}, Slope ={best_slope:.5f} $\\frac{{\\text{{kBtu}}}}{{\\text{{ft}}^2\\text{{day}}\\text{{°F}}}}$", linestyle='solid', linewidth=2, color='black')
        # Customize plot
        if heatingtype == "NaturalGas":
            ax.set_title("Best Degree Day Heating vs Fossil Fuel Consumption")
            ax.set_ylabel("Fossil Fuel/sqft")
        elif heatingtype == "Electric":
            ax.set_title("Best Degree Day Heating vs Electricity Consumption")
            ax.set_ylabel("Electricity/sqft")
        ax.set_xlabel("Degree Day Heating")
        
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.6)
    
        # Return the figure, the y-intercept, the numeric value from the column header,
        # and the slope of the best-fit line (i.e., with the highest R²)
        return fig, best_intercept, best_numeric, best_slope, best_r_squared


    def cooling_degree_day(self, mask = None):
        df_DDc = []
        df_DDc = pd.DataFrame({"OAT": self.oat})
        df_DDc["ccp"] = self.ccp
        df_DDc["Dates"] = self.df_new.index.values 
        #print(self.df_new["Date"], df_DDc["Dates"])

        # Define range of heating change points (ccp-10 to ccp+10 at 1-degree intervals)
        ccp_range = np.arange(self.ccp - 10, self.ccp + 11, 1)  # Includes hcp+10

        # Dictionary to store generated column names
        degree_day_cols = []
        
        # Compute HDD for each heating change point in the range
        for ccp in ccp_range:
            column_name = f"Degree Day Cooling {ccp:.2f}"
            df_DDc[column_name] = np.where(df_DDc["OAT"] - ccp  < 0, 0, df_DDc["OAT"] - ccp)
            degree_day_cols.append(column_name)  # Store column name
            
        '''
        column_name = f"Degree Day Cooling {self.ccp:.2f}"  # Use first ccp value for naming
        df_DDc[column_name] = df_DDc["OAT"] - df_DDc["ccp"] 
        #filtered_df = df_DDc[df_DDc["Dates"].astype(str).str.contains("2022-11")]
        #print(filtered_df[[column_name, "Dates"]])
    
        self.step_minus10 = self.ccp - 10
        column_name = f"Degree Day Cooling {self.step_minus10:.2f}"
        df_DDc[column_name] = df_DDc["OAT"] - self.step_minus10 
    
        self.step_minus5 = self.ccp - 5
        column_name = f"Degree Day Cooling {self.step_minus5:.2f}"
        df_DDc[column_name] = df_DDc["OAT"] - self.step_minus5 
    
        self.step_plus5 = self.ccp + 5
        column_name = f"Degree Day Cooling {self.step_plus5:.2f}"
        df_DDc[column_name] = df_DDc["OAT"] - self.step_plus5 
    
        self.step_plus10 = self.ccp + 10
        column_name = f"Degree Day Cooling {self.step_plus10:.2f}"
        df_DDc[column_name] = df_DDc["OAT"] - self.step_plus10 
        '''
    
        df_DDc["Dates"] = pd.to_datetime(df_DDc["Dates"]).dt.date
        self.df_date_range ["Start Date"] = pd.to_datetime(self.df_date_range ["Start Date"]).dt.date
        self.df_date_range ["End Date"] = pd.to_datetime(self.df_date_range ["End Date"]).dt.date
        #print(df_DDc)

        '''
        # List of columns to sum
        degree_day_cols = [
            f"Degree Day Cooling {self.ccp:.2f}", 
            f"Degree Day Cooling {self.step_minus10:.2f}", 
            f"Degree Day Cooling {self.step_minus5:.2f}", 
            f"Degree Day Cooling {self.step_plus5:.2f}", 
            f"Degree Day Cooling {self.step_plus10:.2f}"
        ]
        '''

        #df_DDc = df_DDc.groupby("Dates", as_index=False)[degree_day_cols].sum()

        #df_DDc[degree_day_cols] = df_DDc[degree_day_cols].clip(lower=0)
        #print("DDc", df_DDc)
        
        # Group by start and end date and sum the degree day heating values
        for value_col in degree_day_cols:
            sum_values = []
            for _, row in self.df_date_range.iterrows():
                start_date, end_date = row["Start Date"], row["End Date"]
                
                # Sum values from df_values where Date is within the range
                total_sum = df_DDc[(df_DDc["Dates"] >= start_date) & (df_DDc["Dates"] <= end_date)][value_col].sum()
        
                sum_values.append(total_sum)
        
            self.df_date_range[f"{value_col}"] = sum_values

        if mask is not None:
            self.df_date_range = self.df_date_range.reset_index(drop=True)
            self.df_date_range = self.df_date_range[mask].reset_index(drop=True)
            self.eui = self.eui.reset_index(drop=True)
            self.eui = self.eui[mask].reset_index(drop=True)
        #print(self.df_date_range)
        #print(self.eui)
        #print(self.oat)
        # Group by month and sum the degree day cooling values
        #self.df_monthly = df_DDc.groupby("Year_Month")[degree_day_cols].sum().reset_index(drop = True)
        #print("df_monhly", self.df_monthly)
        
        # Define month order for correct sorting
        #month_order = [
        #    "January", "February", "March", "April", "May", "June", 
        #    "July", "August", "September", "October", "November", "December"
        #]
        
        # Sort DataFrame by chronological order of months
        #self.df_monthly["Month"] = pd.Categorical(self.df_monthly["Month"], categories=month_order, ordered=True)
        #self.df_monthly = self.df_monthly.sort_values("Month")
        #self.df_monthly = self.df_monthly.reset_index(drop=True)
    
        # Define colors for consistency between data points and lines
        #num_colors = len(np.arange(self.ccp - 10, self.ccp + 11, 1))  # Count of heating change points
        #colors = [mcolors.to_hex(plt.cm.tab10(i % 10)) for i in range(num_colors)]  # Convert to HEX
    
        # Plot using Matplotlib
        fig, ax = plt.subplots(figsize=(8, 6))
    
        '''
        # List of Degree Day Cooling columns and their corresponding numeric values
        degree_day_cols = [
            f"Degree Day Cooling {self.ccp:.2f}", 
            f"Degree Day Cooling {self.step_minus10:.2f}", 
            f"Degree Day Cooling {self.step_minus5:.2f}", 
            f"Degree Day Cooling {self.step_plus5:.2f}", 
            f"Degree Day Cooling {self.step_plus10:.2f}"
        ]
        col_numeric_values = [self.ccp, self.step_minus10, self.step_minus5, self.step_plus5, self.step_plus10]
        '''
        col_numeric_values = np.arange(self.ccp - 10, self.ccp + 11, 1).tolist()
    
        # Variables to track the highest R² regression
        best_r_squared = -1
        best_intercept = None
        best_numeric = None
        best_slope = None
        best_X = None
        best_col = None
        best_Y = None
    
        # Loop through each Degree Day Cooling column
        for i, col in enumerate(degree_day_cols):
            # Filter out rows where the degree day value is zero
            #mask = (self.df_date_range[col] != 0) & (self.eui != 0)
            #X = self.df_date_range[col][mask].values  # Independent variable (Degree Day Cooling)
            X = self.df_date_range[col].values  # Independent variable (Degree Day Cooling)
            #print("X", X.shape)
            #print("mask", mask, "eui", self.eui)
            #Y = self.eui[mask].values  # Dependent variable
            Y = self.eui.values  # Dependent variable
            #print("Y", Y.shape, Y)
            #print(Y)

            # Compute mean and standard deviation of X
            #X_mean = np.mean(X)
            #X_std = np.std(X)
        
            # Define the valid range (within 1 standard deviation)
            #lower_bound = X_mean - X_std
            #upper_bound = X_mean + X_std
        
            # Create mask to keep values within 1 standard deviation
            #std_mask = (X >= lower_bound) & (X <= upper_bound)

            #print("cooling mask", std_mask)
        
            # Apply the mask to X and Y
            #X_filtered = X[std_mask]
            #Y_filtered = Y[std_mask]

            #print(X_filtered.shape, Y_filtered.shape, X.shape, Y.shape)
            
            # Add constant for regression
            X_const = sm.add_constant(X)
    
            # Fit linear regression model
            #print("Y", Y.shape)
            #print("X_const", X_const.shape)
            model = sm.OLS(Y, X_const).fit()
            intercept, slope = model.params
    
            # Compute R-squared value
            r_squared = model.rsquared
    
            # Update best regression if current r_squared is higher
            if r_squared > best_r_squared  and intercept > 0:
                best_r_squared = r_squared
                best_intercept = intercept
                best_slope = slope
                best_numeric = col_numeric_values[i]
                best_X = X
                best_col = col
                best_Y = Y

        # Scatter plot for actual data points
        ax.scatter(best_X.flatten(), best_Y.flatten(), c= "#000000", alpha=0.7)
    
        # Generate trendline values, ensuring it extends to the y-axis
        x_vals = np.linspace(0, max(best_X) * 1.1, 100)
        y_vals = best_intercept + best_slope * x_vals
        
        # Add best-fit line
        ax.plot(x_vals.flatten(), y_vals.flatten(), label=f"{best_col}°F\nIntercept={best_intercept:.5e} $\\frac{{\\text{{kBtu}}}}{{\\text{{ft}}^2}}$, R²={best_r_squared:.3f}, Slope ={best_slope:.5e} $\\frac{{\\text{{kBtu}}}}{{\\text{{ft}}^2\\text{{day}}\\text{{°F}}}}$", linestyle='solid', linewidth=2, color='black')    
        # Customize plot
        ax.set_title("Best Degree Day Cooling vs Electricity Consumption")
        ax.set_xlabel("Degree Day Cooling")
        ax.set_ylabel("Electricity/sqft")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.6)
    
        # Return the figure, the y-intercept, the numeric value from the column header,
        # and the slope of the best-fit line (i.e., with the highest R²)
        return fig, best_intercept, best_numeric, best_slope, best_r_squared


# In[3]:





# In[ ]:




