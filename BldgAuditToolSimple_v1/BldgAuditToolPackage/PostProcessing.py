import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

import plotly.graph_objects as go
import calendar

class PlotResults:
    def __init__(self,save,ProjectPath):
        self.save = save
        self.ProjectPath = ProjectPath
        
    def PlotWeather(self,df_weather,weather_station_name):

        df_weather['month'] = df_weather.index.month
        monthly_stats = df_weather.groupby('month')['Temp_C'].agg(['mean', 'std'])

        # Compute upper and lower limits
        monthly_stats['upper'] = monthly_stats['mean'] + monthly_stats['std']
        monthly_stats['lower'] = monthly_stats['mean'] - monthly_stats['std']

        fig, ax = plt.subplots(figsize=(10, 5))

        # Plot mean temperature
        ax.plot(monthly_stats.index, monthly_stats['mean'], marker='o', linestyle='-', color='b', label='Mean Temperature')

        # Fill between upper and lower limits
        ax.fill_between(monthly_stats.index, monthly_stats['upper'], monthly_stats['lower'], color='lightblue', alpha=0.4, label='Variation (±1 Std Dev)')

        # Customize plot
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
        ax.set_xlabel("Month")
        ax.set_ylabel("Temperature (°C)")
        # ax.set_title("Mean Monthly Temperature with Variation")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.set_title(f"Station: {weather_station_name}")
        fig.tight_layout()
        if self.save:
            fig.savefig(os.path.join(self.ProjectPath,"Results",f"WeatherPlot_{weather_station_name}.png"),dpi=300)
        # Show plot
        plt.close()
        return

    def PlotEndUseBreakdown(self,RunDir):
        #%%
        
        df_MonthlyEndUse = pd.read_csv(os.path.join(RunDir, "MonthlyEndUseBreakdown.csv"))
        print(df_MonthlyEndUse)
        df_MonthlyEndUse["AL-Space Heating"] = df_MonthlyEndUse["EL-Space Heating"] + df_MonthlyEndUse["NG-Space Heating"]
        df_MonthlyEndUse = df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(['EL-Space Heating','NG-Space Heating','BLC_Heat_NG', 'BLC_Heat_EL', 'BLC_Cool_EL', 'HDD_EL', 'HDD_NG', 'CDD'])]
        # Assuming EndUseBreakdown is already defined
        
        #Ashit: updaing code to use column name for only non zero sum
        #labels = list(df_MonthlyEndUse.columns.str[3:])
        #sizes = list(df_MonthlyEndUse.sum(axis=0))
        sizes_raw = df_MonthlyEndUse.sum()
        filtered = sizes_raw[sizes_raw != 0]
        labels = filtered.index.map(lambda x: str(x)[3:]).tolist()
        sizes = filtered.values.tolist()

        fig, ax = plt.subplots(figsize=(5, 5))
        print (sizes, labels)
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=['red', 'blue', 'green', 'orange', 'purple','yellow'])
        ax.set_title("Annual Energy End Use Breakdown (kBtu)")
        fig.tight_layout()
        if self.save:
            fig.savefig(os.path.join(self.ProjectPath,"Results","EndUseBreakdown.png"),dpi=300)
        plt.close()
        return

    def PlotInverseModelComparison(self,RunDir,dfutilDataSorted):
        #%%
        df_MonthlyEndUse = pd.read_csv(os.path.join(RunDir, "MonthlyEndUseBreakdown.csv"))
        df_MonthlyEndUse = df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(['BLC_Heat_NG', 'BLC_Heat_EL', 'BLC_Cool_EL', 'HDD_EL', 'HDD_NG', 'CDD'])]
        
        ThermRes = df_MonthlyEndUse.loc[:,df_MonthlyEndUse.columns.str.contains("NG")]
        ThermRes = ThermRes[sorted(ThermRes.columns)]
        ElecRes = df_MonthlyEndUse.loc[:,df_MonthlyEndUse.columns.str.contains("EL")]
        ElecRes = ElecRes[sorted(ElecRes.columns)]
        ThermRes.columns = ThermRes.columns.str[3:]
        ElecRes.columns = ElecRes.columns.str[3:]
        ThermRes = ThermRes/100
        ElecRes = ElecRes/3.41
        #%%
        df = dfutilDataSorted.copy()  # Keeping original DataFrame

        # Get the total number of rows
        n_rows = len(df)
        
        # Initialize result Series with NaNs
        ThermMean = []
        ElecMean = []
        # Compute means for first 12 rows
        for i in range(min(12, n_rows)):  # Ensure we don't exceed available rows
            if i + 12 < n_rows:
                ThermMean.append((df.loc[i, 'Therms'] + df.loc[i + 12, 'Therms']) / 2)
                ElecMean.append((df.loc[i, 'kWh'] + df.loc[i + 12, 'Therms']) / 2)
            else:
                ThermMean.append(df.loc[i, 'Therms'])  # For rows beyond 12, keep as is
                ElecMean.append(df.loc[i, 'kWh'])  # For rows beyond 12, keep as is
        #%%
        ThermPred = ThermRes.sum(axis=1).values
        ThermErr = 100*(ThermPred - np.array(ThermMean))/np.array(ThermMean)
        ElecPred = ElecRes.sum(axis=1).values
        ElecErr = 100*(ElecPred - np.array(ElecMean))/np.array(ElecMean)
        
        #%%
        ThermPred = ThermRes.sum(axis=1).values
        print("ThermPred: ",ThermPred)
        print("ThermAct: ",ThermMean)
        ThermResidual = ThermMean - ThermPred
        ThermRMSE = np.sqrt(np.mean(ThermResidual**2))
        ThermCVRMSE = ThermRMSE/np.mean(ThermMean)*100
        print("Therm CVRMSE: ",ThermCVRMSE)
        ThermNMBE = np.mean(ThermResidual)/np.mean(ThermMean)*100
        print("Therm NMBE: ",ThermNMBE)
        NGColorMap = {"Gas Equipment":"tab:green","DHW Heating":"tab:orange","Space Heating":"red"}
        abbreviated_months = [calendar.month_abbr[i] for i in range(1, 13)]
        fig, ax = plt.subplots(figsize=(8,4))

        # Plot the timeseries data
        ax.plot(np.arange(0,len(ThermMean)), np.array(ThermMean), marker="s", color="k", label="Utility Data")  # Add label for clarity

        # Plot the stacked bar chart on the same axes
        colors = [NGColorMap.get(col, "gray") for col in ThermRes.columns]  # Default to "gray" if not in NGColorMap
        Thermbars = ThermRes.plot(kind='bar', stacked=True, ax=ax, color=colors,edgecolor='black')
        ax.get_legend().remove()
        
        for i, (height, err) in enumerate(zip(ThermPred, ThermErr)):
            ax.text(i,  height + ThermPred.max()/20, f'{err:.1f}%', ha='center', fontsize=10, color='black')


        ax.set_ylabel('Natural Gas (Therms)')
        

        # ax.legend(ncol=2, title="End Uses")
        ax.set_title("CV-RMSE: "+str(round(ThermCVRMSE,1))+"%, NMBE: "+str(round(ThermNMBE,1))+"%")
        ax.set_xticks(range(len(ThermRes.index)))
        ax.set_xticklabels(abbreviated_months, rotation=45)
        ax.set_xlabel('')
        ax.set_ylim([0,max(max(ThermMean),ThermPred.max())+max(max(ThermMean),ThermPred.max())/5])
        # Adjust layout to prevent overlapping elements
        fig.tight_layout()
        if self.save:
            fig.savefig(os.path.join(self.ProjectPath,"Results","NaturalGasMonthlyBreakdown.png"),dpi=300)
        plt.close()
        #### Print the legend box only
        # Extract legend handles/labels before removing from axes
        # handles, labels = ax.get_legend_handles_labels()
        # ng_handles = handles[:len(ThermRes.columns)*2]
        # ng_labels = labels[:len(ThermRes.columns)*2]
        # fig_legend = plt.figure(figsize=(6, 0.7))
        # fig_legend.legend(ng_handles, ng_labels, title="End Uses", ncol=4, loc='center', frameon=True)
        # fig_legend.tight_layout()
        # if self.save:
        #     fig_legend.savefig(os.path.join(RunDir,"NaturalGasLegend.png"), dpi=150, bbox_inches='tight')

        
        #%%
        ElecPred = ElecRes.sum(axis=1).values
        print("ElecPred: ",ElecPred)
        print("ElecAct: ",ElecMean)
        ElecResidual = ElecMean - ElecPred
        ElecRMSE = np.sqrt(np.mean(ElecResidual**2))
        ElecCVRMSE = ElecRMSE/np.mean(ElecMean)*100
        print("Elec CVRMSE: ",ElecCVRMSE)
        ElecNMBE = np.mean(ElecResidual)/np.mean(ElecMean)*100
        print("Elec NMBE: ",ElecNMBE)
        ElecColorMap = {"Electric Equipment":"tab:green","Lighting":"yellow","Space Cooling":"blue","Space Heating":"red","DHW Heating":"tab:orange"}
        abbreviated_months = [calendar.month_abbr[i] for i in range(1, 13)]
        fig, ax = plt.subplots(figsize=(8,4))
        ax.plot(np.arange(0,len(ElecMean)),ElecMean,marker="s",color="k", label="Utility Data")
        colors = [ElecColorMap.get(col, "gray") for col in ElecRes.columns]  # Default to "gray" if not in NGColorMap
        Elecbars = ElecRes.plot(kind='bar', stacked=True, ax=ax, color=colors,edgecolor='black')
        ax.get_legend().remove()
        
        for i, (height, err) in enumerate(zip(ElecPred, ElecErr)):
            ax.text(i, height +  ElecPred.max()/20, f'{err:.1f}%', ha='center', fontsize=10, color='black')
            
        ax.set_ylabel('Electricity (kWh)')
        # ax.legend(ncol=2, title="End Uses")

        
        ax.set_title("CV-RMSE: "+str(round(ElecCVRMSE,1))+"%, NMBE: "+str(round(ElecNMBE,1))+"%")

        ax.set_xticks(range(len(ThermRes.index)))
        ax.set_xticklabels(abbreviated_months, rotation=45)
        ax.set_xlabel('')
        ax.set_ylim([0,max(max(ElecMean),ElecPred.max())+max(max(ElecMean),ElecPred.max())/5])
        fig.tight_layout()
        if self.save:
            fig.savefig(os.path.join(self.ProjectPath,"Results","ElectricityMonthlyBreakdown.png"),dpi=300)
        plt.close()

            #### Print the legend box only
        # Extract legend handles/labels before removing from axes
        # handles, labels = ax.get_legend_handles_labels()
        # elec_handles = handles[:len(ElecRes.columns)*2]
        # elec_labels = labels[:len(ElecRes.columns)*2]
        # fig_legend = plt.figure(figsize=(6, 0.7))
        # fig_legend.legend(elec_handles, elec_labels, title="End Uses", ncol=5, loc='center', frameon=True)
        # fig_legend.tight_layout()
        # if self.save:
        #     fig_legend.savefig(os.path.join(RunDir,"ElectricityLegend.png"), dpi=150, bbox_inches='tight')

        
        return 

    def PlotEEMEndUseComparison(self,RunDir,df_MonthlyEndUse_EEM):
        df_MonthlyEndUse = pd.read_csv(os.path.join(self.ProjectPath, "MonthlyEndUseBreakdown.csv"))
        df_MonthlyEndUse = df_MonthlyEndUse.loc[:,~df_MonthlyEndUse.columns.isin(['BLC_Heat_NG', 'BLC_Heat_EL', 'BLC_Cool_EL', 'HDD_EL', 'HDD_NG', 'CDD'])]
        
        ThermRes = df_MonthlyEndUse.loc[:,df_MonthlyEndUse.columns.str.contains("NG")]
        ThermRes = ThermRes[sorted(ThermRes.columns)]
        ElecRes = df_MonthlyEndUse.loc[:,df_MonthlyEndUse.columns.str.contains("EL")]
        ElecRes = ElecRes[sorted(ElecRes.columns)]
        ThermRes.columns = ThermRes.columns.str[3:]
        ElecRes.columns = ElecRes.columns.str[3:]
        ThermRes = ThermRes/100
        ElecRes = ElecRes/3.41
        
        #%%
        df_MonthlyEndUse_EEM = df_MonthlyEndUse_EEM.loc[:,~df_MonthlyEndUse_EEM.columns.isin(['BLC_Heat_NG', 'BLC_Heat_EL', 'BLC_Cool_EL', 'HDD_EL', 'HDD_NG', 'CDD'])]
        
        ThermRes_EEM = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("NG")]
        ThermRes_EEM = ThermRes_EEM[sorted(ThermRes_EEM.columns)]
        ElecRes_EEM = df_MonthlyEndUse_EEM.loc[:,df_MonthlyEndUse_EEM.columns.str.contains("EL")]
        ElecRes_EEM = ElecRes_EEM[sorted(ElecRes_EEM.columns)]
        ThermRes_EEM.columns = ThermRes_EEM.columns.str[3:]
        ElecRes_EEM.columns = ElecRes_EEM.columns.str[3:]
        ThermRes_EEM = ThermRes_EEM/100
        ElecRes_EEM = ElecRes_EEM/3.41
        
        #%%
        ThermPred = ThermRes.sum(axis=1).values
        ThermPred_EEM = ThermRes_EEM.sum(axis=1).values
        ThermErr = 100*(ThermPred - ThermPred_EEM)/ThermPred
        ElecPred = ElecRes.sum(axis=1).values
        ElecPred_EEM = ElecRes_EEM.sum(axis=1).values
        ElecErr = 100*(ElecPred - ElecPred_EEM)/np.array(ElecPred)
        
        #%%
        NGColorMap = {"Gas Equipment":"tab:green","DHW Heating":"tab:orange","Space Heating":"red"}
        abbreviated_months = [calendar.month_abbr[i] for i in range(1, 13)]
        fig, ax = plt.subplots(figsize=(8, 4))

        # Define bar width
        width = 0.4  
        
        # Create positions for side-by-side comparison
        x = np.arange(len(ThermRes))
        
        # Assign colors to each category
        colors = [NGColorMap.get(col, "gray") for col in ThermRes.columns]
        
        
        bottom_baseline = np.zeros(len(ThermRes))
        bottom_eem = np.zeros(len(ThermRes_EEM))
        
        # Stack Baseline (shifted left)
        for col in ThermRes.columns:
            ax.bar(x - width/2, ThermRes[col], width=width, label=f'Baseline - {col}', 
                   color=NGColorMap.get(col, "gray"), edgecolor='black', bottom=bottom_baseline)
            bottom_baseline += ThermRes[col].values  # Update bottom for stacking
        
        # Stack EEM (shifted right)
        for col in ThermRes_EEM.columns:
            ax.bar(x + width/2, ThermRes_EEM[col], width=width, label=f'EEM - {col}', 
                   color=NGColorMap.get(col, "gray"), edgecolor='black', alpha=0.7, bottom=bottom_eem,hatch='//')
            bottom_eem += ThermRes_EEM[col].values  # Update bottom for stacking
            
        # Add error values above each bar
        for i, (height, err) in enumerate(zip(ThermPred, ThermErr)):
            ax.text(i, height + ThermPred.max()/20, f'{err:.1f}%', ha='center', fontsize=10, color='black')
        
        # Labels and Titles
        ax.set_ylabel('Natural Gas (Therms)')
        ax.set_xticks(x)
        ax.set_xticklabels(abbreviated_months, rotation=45)
        ax.set_xlabel('')
        ax.set_ylim([0, ThermPred.max() + ThermPred.max()/5])
        
        

        # Adjust layout to prevent overlapping
        fig.tight_layout()

        if self.save:
            fig.savefig(os.path.join(RunDir,"NaturalGasMonthlyEEMComp.png"), dpi=150, bbox_inches='tight')

        plt.close()

        # Save NG legend as a separate image
        # Extract legend handles/labels before removing from axes
        # handles, labels = ax.get_legend_handles_labels()
        # ng_handles = handles[:len(ThermRes.columns)*2]
        # ng_labels = labels[:len(ThermRes.columns)*2]
        # fig_legend = plt.figure(figsize=(6, 0.7))
        # fig_legend.legend(ng_handles, ng_labels, title="End Uses", ncol=3, loc='center', frameon=True)
        # fig_legend.tight_layout()
        # if self.save:
        #     fig_legend.savefig(os.path.join(RunDir,"NaturalGasLegend.png"), dpi=150, bbox_inches='tight')
        # plt.close(fig_legend)
        #%%
        ElecColorMap = {"Electric Equipment":"tab:green","Lighting":"yellow","Space Cooling":"blue","Space Heating":"red","DHW Heating":"tab:orange"}
        abbreviated_months = [calendar.month_abbr[i] for i in range(1, 13)]
        fig, ax = plt.subplots(figsize=(8,4))
        # Define bar width
        width = 0.4  
        
        # Create positions for side-by-side comparison
        x = np.arange(len(ElecRes))
        colors = [ElecColorMap.get(col, "gray") for col in ElecRes.columns]  # Default to "gray" if not in NGColorMap
        bottom_baseline = np.zeros(len(ThermRes))
        bottom_eem = np.zeros(len(ThermRes_EEM))
        
        # Stack Baseline (shifted left)
        for col in ElecRes.columns:
            ax.bar(x - width/2, ElecRes[col], width=width, label=f'Baseline - {col}', 
                   color=ElecColorMap.get(col, "gray"), edgecolor='black', bottom=bottom_baseline)
            bottom_baseline += ElecRes[col].values  # Update bottom for stacking
        
        # Stack EEM (shifted right)
        for col in ElecRes_EEM.columns:
            ax.bar(x + width/2, ElecRes_EEM[col], width=width, label=f'EEM - {col}', 
                   color=ElecColorMap.get(col, "gray"), edgecolor='black', alpha=0.7, bottom=bottom_eem,hatch='//')
            bottom_eem += ElecRes_EEM[col].values  # Update bottom for stacking
            
        
        # Add error values above each bar
        for i, (height, err) in enumerate(zip(ElecPred, ElecErr)):
            ax.text(i, height + ElecPred.max()/20, f'{err:.1f}%', ha='center', fontsize=10, color='black')
        
        # Labels and Titles
        ax.set_ylabel('Electricity (kWh)')
        ax.set_xticks(x)
        ax.set_xticklabels(abbreviated_months, rotation=45)
        ax.set_xlabel('')
        ax.set_ylim([0, max(ElecPred.max(),ElecPred_EEM.max()) + max(ElecPred.max(),ElecPred_EEM.max())/5])
        
       

        # Adjust layout to prevent overlapping
        fig.tight_layout()
        if self.save:
            fig.savefig(os.path.join(RunDir,"ElectricityMonthlyEEMComp.png"), dpi=150, bbox_inches='tight')
        plt.close()

        # Save electricity legend as a separate image
         # Extract legend handles/labels before removing from axes
        # handles, labels = ax.get_legend_handles_labels()
        # elec_handles = handles[:len(ElecRes.columns)*2]
        # elec_labels = labels[:len(ElecRes.columns)*2]
        # fig_legend = plt.figure(figsize=(8, 0.7))
        # fig_legend.legend(elec_handles, elec_labels, title="End Uses", ncol=4, loc='center', frameon=True)
        # fig_legend.tight_layout()
        # if self.save:
        #     fig_legend.savefig(os.path.join(RunDir,"ElectricityLegend.png"), dpi=150, bbox_inches='tight')
        # plt.close(fig_legend)
        return