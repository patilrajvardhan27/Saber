#!/usr/bin/env python
# coding: utf-8

# In[1]:


import plotly.graph_objects as go
import statsmodels.api as sm
import numpy as np

class Plot:
    def __init__(self, energy_type, model_type, model_parameters, OAT, utility_data_EUI):
        # Parameter order: hcp, ccp, base, hsl, csl
        self.energy_type = energy_type
        self.model_type = model_type
        self.hcp = model_parameters[0]
        self.ccp = model_parameters[1]
        self.base = model_parameters[2]
        self.hsl = model_parameters[3]
        self.csl = model_parameters[4]
        self.OAT = OAT
        self.utility_data_EUI = utility_data_EUI

    def plot_graph_cp(self):
        """Generate an interactive plotly graph with heating, cooling, and baseline segments."""
        # Generate a range of Outside Air Temperatures (°F) for the model
        outside_air_temp = np.linspace(self.OAT.min(), self.OAT.max(), 100)

        # Create figure object
        fig = go.Figure()

        eui_values = None  # Placeholder for model-generated values

        # 3P Heating Model
        if self.model_type == "3P Heating" and self.energy_type == "Fossil Fuel":
            def heating_model(temp, hcp, base, hsl):
                return np.piecewise(temp,
                                    [temp < hcp, temp >= hcp],
                                    [lambda temp: hsl * (temp - hcp) + base,  
                                     lambda temp: base])  

            eui_values = heating_model(outside_air_temp, self.hcp, self.base, self.hsl)
            color = 'red'

        # 3P Cooling Model
        elif self.model_type == "3P Cooling" and self.energy_type == "Electricity":
            def cooling_model(temp, ccp, base, csl):
                return np.piecewise(temp,
                                    [temp <= ccp, temp > ccp],
                                    [lambda temp: base,  
                                     lambda temp: csl * (temp - ccp) + base])

            eui_values = cooling_model(outside_air_temp, self.ccp, self.base, self.csl)
            color = 'blue'

        # 4P Model
        elif self.model_type == "4P":
            def four_point_model(temp, hcp, ccp, base, hsl, csl):
                return np.piecewise(temp,
                                    [temp < hcp, (temp >= hcp) & (temp <= ccp), temp > ccp],
                                    [lambda temp: hsl * (temp - hcp) + base,  
                                     lambda temp: base,  
                                     lambda temp: csl * (temp - ccp) + base])  

            eui_values = four_point_model(outside_air_temp, self.hcp, self.ccp, self.base, self.hsl, self.csl)
            color = 'purple'

        # 5P Model
        elif self.model_type == "5P":
            def five_point_model(temp, hcp, ccp, base, hsl, csl):
                return np.piecewise(temp,
                                    [temp < hcp, (temp >= hcp) & (temp <= ccp), temp > ccp],
                                    [lambda temp: hsl * (temp - hcp) + base,  
                                     lambda temp: base,  
                                     lambda temp: csl * (temp - ccp) + base])  

            eui_values = five_point_model(outside_air_temp, self.hcp, self.ccp, self.base, self.hsl, self.csl)
            color = 'orange'

        if eui_values is not None:
            # Perform regression analysis to get R² value
            X = sm.add_constant(outside_air_temp.reshape(-1, 1))  # Adding intercept term
            model = sm.OLS(eui_values, X).fit()
            r_squared = model.rsquared

            # Add Model Data to Plot
            fig.add_trace(go.Scatter(
                x=outside_air_temp, 
                y=eui_values, 
                mode='lines', 
                name=f"{self.model_type} Model (R²={r_squared:.3f})", 
                line=dict(color=color)
            ))

        # Add Measured Data Points
        fig.add_trace(go.Scatter(
            x=self.OAT, 
            y=self.utility_data_EUI, 
            mode='markers', 
            name="Measured Data", 
            marker=dict(color='black', size=8)
        ))

        # Update Layout
        fig.update_layout(
            title=f"{self.model_type} Change Point Model", 
            xaxis_title="Outside Air Temp (°F)", 
            yaxis_title="EUI (kBtu/day/sqft)", 
            template="plotly_white"
        )

        return fig  # Returning the figure instead of displaying it

# Example Usage:
# model_params = [hcp_value, ccp_value, base_value, hsl_value, csl_value]
# plot_instance = Plot("Fossil Fuel", "3P Heating", model_params, OAT_data, utility_data_EUI)
# fig = plot_instance.plot_graph_cp()  # This will return the figure object

