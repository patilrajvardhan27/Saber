
from .MeasureClass import *
from .MeasurePackageClass import *


# IDF.setiddname(os.path.join("/EnergyPlus-22.2.0-c249759bad-Linux-Ubuntu20.04-x86_64","Energy+.idd"))
# IDF.setiddname(os.path.join("C:\\","EnergyPlusV22-2-0","Energy+.idd"))



#%%
def AddCurrentOptionasMeasure(df_input,MeasureName,MeasureList):
    CurrentProp = Measure()
    CurrentProp.PropName = MeasureName
    if "HeatingEquipment" in MeasureName:
        CurrentProp.PropName = "HeatingEquipment " + df_input.loc[df_input["PropKey"] == "HeatingEquipment","PropValue"].item()
        CurrentProp.PropValue = df_input.loc[df_input["PropKey"] == "HeatingEff","PropValue"].iloc[0]
        CurrentProp.UnitValue = "autosize"
    elif "CoolingEquipment" in MeasureName:
        CurrentProp.PropName = "CoolingEquipment " + df_input.loc[df_input["PropKey"] == "CoolingEquipment","PropValue"].item()
        CurrentProp.PropValue = df_input.loc[df_input["PropKey"] == "CoolingEff","PropValue"].iloc[0]
        CurrentProp.UnitValue = "autosize"
    elif "DHWSystemType" in MeasureName:
        CurrentProp.PropName = "DHWSystemType " + df_input.loc[df_input["PropKey"] == "DHWSystemType","PropValue"].item()
        CurrentProp.PropValue = 1
        CurrentProp.UnitValue = df_input.loc[df_input["PropKey"] == "DHWTankVol","PropValue"].iloc[0]
        
    else:
        CurrentProp.PropValue = df_input.loc[df_input["PropKey"] == MeasureName,"PropValue"].iloc[0]
        CurrentProp.UnitValue = 0

    CurrentProp.FixedCost = 0
    CurrentProp.UnitVarCost = 0
    CurrentProp.Unit = "Dozen tamatar"
    
    MeasureList.append(CurrentProp)
    return [MeasureList[-1]] + MeasureList[:-1]
    
    
    
def VariableFilter(df_input,MeasureList):
    PopIndices = []
    for m in range(len(MeasureList)):
        #######-------------------____________________HeatING EQUIPMNET_____________________------------------------------------
        # If Heating equipment is in the measure list
        if "HeatingEquipment" in MeasureList[m].PropName:
            CurrentHeatingEqp = df_input.loc[df_input["PropKey"] == "HeatingEquipment", "PropValue"].item().replace(" ","")
            if "NoHeating" in CurrentHeatingEqp:
                if "NoHeating" in MeasureList[m].PropName:
                    if m>0: # Leave only one NoHeating value 
                        PopIndices.append(m)
                        
            elif "GasFurnace" in CurrentHeatingEqp:
                if "NoHeating" in MeasureList[m].PropName:
                    PopIndices.append(m)
                elif "GasFurnace" in MeasureList[m].PropName: 
                    CurrentHeatingEff = df_input.loc[df_input["PropKey"] == "HeatingEff", "PropValue"].iloc[0]
                    if CurrentHeatingEff =="Other..":
                        CurrentHeatingEff = float(df_input.loc[df_input.PropKey == "HeatingEffCustom"].PropValue.iloc[0])

                    if float(MeasureList[m].PropValue) < float(CurrentHeatingEff): # Assumption that no one will update the HVAC with same efficiency but higher capacity.
                        PopIndices.append(m)
                    elif float(MeasureList[m].PropValue) == float(CurrentHeatingEff): # If the heating efficiency is the same remove all options and add the current eqp as another measure but with 0 costs
                        PopIndices.append(m) #ADD THIS CASE
            
            elif "ElectricFurnace" in CurrentHeatingEqp:
                # If the current equipment is already electric don't degrade to a gas equipment
                if "NoHeating" in MeasureList[m].PropName or "GasFurnace" in MeasureList[m].PropName:
                    PopIndices.append(m) 
                elif "ElectricFurnace" in MeasureList[m].PropName:
                    PopIndices.append(m)  #ADD THIS CASE
                    # MeasureList = AddCurrentOptionasMeasure(df_input, MeasureList[m].PropName, MeasureList)
            
            elif "AirSourceHeatPumnp" in CurrentHeatingEqp:
                if "NoHeating" in MeasureList[m].PropName or "GasFurnace" in MeasureList[m].PropName or "ElectricFurnace" in MeasureList[m].PropName:
                    PopIndices.append(m)
                elif "AirSourceHeatPump" in MeasureList[m].PropName:
                    CurrentHeatingEff = df_input.loc[df_input["PropKey"] == "HeatingEff", "PropValue"].iloc[0]
                    if float(MeasureList[m].PropValue) < CurrentHeatingEff:  # NEED TO CHECK THIS IF CurrentHeatingEff is a list of COP  values
                        PopIndices.append(m)
                    elif float(MeasureList[m].PropValue) == CurrentHeatingEff:
                        PopIndices.append(m)
        #######-------------------____________________COOLING EQUIPMNET_____________________------------------------------------
        elif "CoolingEquipment" in MeasureList[m].PropName:
            CurrentCoolingEqp = df_input.loc[df_input["PropKey"] == "CoolingEquipment", "PropValue"].item().replace(" ","")
            if "NoCooling" in CurrentCoolingEqp:
                if "NoCooling" in MeasureList[m].PropName:
                    if m>0: # Leave only one NoHeating value 
                        PopIndices.append(m)
            
            elif "AirConditioner" in CurrentCoolingEqp:
                if "NoCooling" in MeasureList[m].PropName:
                    PopIndices.append(m)
                elif "AirConditioner" in MeasureList[m].PropName:
                    CurrentCoolingEff = df_input.loc[df_input["PropKey"] == "CoolingEff", "PropValue"].iloc[0]
                    if CurrentCoolingEff == "Other..":
                        CurrentCoolingEff = float(df_input.loc[df_input.PropKey == "CoolingEffCustom"].PropValue.iloc[0])

                    if float(MeasureList[m].PropValue) < float(CurrentCoolingEff): # Assumption that no one will update the HVAC with same efficiency but higher capacity.
                        PopIndices.append(m)
                    elif float(MeasureList[m].PropValue) == float(CurrentCoolingEff): # If the heating efficiency is the same remove all options and add the current eqp as another measure but with 0 costs
                        PopIndices.append(m) #ADD THIS CASE
                
            elif "AirSourceHeatPump" in CurrentCoolingEqp:
                if "NoCooling" in MeasureList[m].PropName or "AirConditioner" in MeasureList[m].PropName:
                    PopIndices.append(m)
                
                elif "AirSourceHeatPump" in MeasureList[m].PropName:
                    CurrentCoolingEff = df_input.loc[df_input["PropKey"] == "CoolingEff", "PropValue"].iloc[0]
                    if float(MeasureList[m].PropValue) < CurrentCoolingEff: # Assumption that no one will update the HVAC with same efficiency but higher capacity.
                        PopIndices.append(m)
                    elif float(MeasureList[m].PropValue) == CurrentCoolingEff: # If the heating efficiency is the same remove all options and add the current eqp as another measure but with 0 costs
                        PopIndices.append(m) #ADD THIS CASE
                
        #######-------------------____________________DHW EQUIPMNET_____________________------------------------------------
        elif "DHWSystemType" in MeasureList[m].PropName:
            CurrentDHWEqp = df_input.loc[df_input["PropKey"] == "DHWSystemType", "PropValue"].item().replace(" ","")
            if "NoBoiler" in CurrentDHWEqp:
                if "NoBoiler" in MeasureList[m].PropName:
                    if m > 0:
                        PopIndices.append(m)
            
            elif "GasBoiler" in CurrentDHWEqp:
                if "NoBoiler" in MeasureList[m].PropName:
                    PopIndices.append(m)
                
                elif "GasBoiler" in MeasureList[m].PropName:
                    PopIndices.append(m)
                
            elif "ElectricHeater" in CurrentDHWEqp:
                if "NoBoiler" in MeasureList[m].PropName or "GasBoiler" in MeasureList[m].PropName:
                    PopIndices.append(m)
                
                elif "ElectricHeater" in MeasureList[m].PropName:
                    PopIndices.append(m)
                   
        
        #######-------------------____________________ALL REMAINING MEASURES_____________________------------------------------------
        else: #Do this for all remaining Properties
            CurrentPropValue = df_input.loc[df_input["PropKey"] == MeasureList[m].PropName,"PropValue"].iloc[0]
            if str(MeasureList[m].PropValue) == str(CurrentPropValue):
                for i in range(0,m+1):
                    PopIndices.append(i)
                
    # Pop all indices that were collected.
    for i in sorted(PopIndices, reverse=True):
        MeasureList.pop(i)

    return MeasureList
