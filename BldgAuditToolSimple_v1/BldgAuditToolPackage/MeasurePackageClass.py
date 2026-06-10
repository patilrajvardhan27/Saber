import pandas as pd
import numpy as np
import shutil 
import os

from .MeasureClass import *

class MeasurePackage:
    def __init__(self):
        self.PackageID = None
        self.OutputDir = None
        self.LCC = None
        self.SourceEnergy = None
        self.PctSourceSavings = None
        self.Slope_LCC_PctSS = None

class MeasurePackageUtilities:
    def __init__(self,MeasureTypes):
        self.MeasureTypes = MeasureTypes

    
    def CreateRunDirectory(self,Package, df_input,ProjectPath):
        # Build the directory name based on Package.PackageID
        outputdirectory = "".join(f"P{i}_{value}" for i, value in enumerate(Package.PackageID.values()))

        # Make the directory inside "OutputDirectory"
        run_dir = os.path.join(ProjectPath, "MeasureEvaluation", outputdirectory)
        Package.OutputDir = run_dir
        os.makedirs(run_dir, exist_ok=True)

        # Save df_input inside this run directory
        df_input.to_pickle(os.path.join(run_dir, "BldgPropInputsFile.pkl"))

        shutil.copy(os.path.join(ProjectPath,"BestModelParams.csv"), Package.OutputDir)

        return Package

    def RunPackage(self,Package,CostMetrics,df_weather):
        
        MeasureUtils = MeasureUtilities(Package.OutputDir)
        CurrentMeasureList = []
        MeasureTypesCopy = self.MeasureTypes.copy()
        for name in MeasureTypesCopy.keys():
            if Package.PackageID[name] > 0:
                print("Running Measure:", name, "Option:", Package.PackageID[name])
                option = MeasureTypesCopy[name][Package.PackageID[name]]
                MeasureUtils.SetMeasure(option,MeasureTypesCopy)
                MeasureUtils.RunMeasure(CostMetrics,df_weather) # You have to run this every iteration to update the BestModelParams.csv file. This will avoid negative savings issues.
                CurrentMeasureList.append(option)
            else:
                continue

        # for CurrentMeasure in CurrentMeasureList:
        #     MeasureUtils.UpdateMeasureInputParams(CurrentMeasure)


        
        MeasureUtils.GetMeasurePackageResults(CurrentMeasureList)
        
        return

    def UpdatePackageResults(self, Package, BaselineSumRes):
        dfRes = pd.read_csv(os.path.join(Package.OutputDir, "RunResults.csv"))

        # Handle division by zero for full electrification
        if BaselineSumRes["NaturalGas"].iloc[0] == 0:
            dfRes.loc[0, "PctThermsChange"] = 0
        else:
            dfRes.loc[0, "PctThermsChange"] = 100 * (
                (dfRes.loc[0, "NaturalGas"] - BaselineSumRes["NaturalGas"].iloc[0])
                / BaselineSumRes["NaturalGas"].iloc[0]
            )

        dfRes.loc[0, "PctkWhChange"] = 100 * (
            (dfRes.loc[0, "Electricity"] - BaselineSumRes["Electricity"].iloc[0])
            / BaselineSumRes["Electricity"].iloc[0]
        )
        dfRes.loc[0, "PctTSEChange"] = 100 * (
            (dfRes.loc[0, "TSE"] - BaselineSumRes["TSE"].iloc[0])
            / BaselineSumRes["TSE"].iloc[0]
        )
        dfRes.loc[0, "PctSourceChange"] = 100 * (
            (dfRes.loc[0, "TotalSourceEnergy"] - BaselineSumRes["TotalSourceEnergy"].iloc[0])
            / BaselineSumRes["TotalSourceEnergy"].iloc[0]
        )

        dfRes.loc[0, "OperatingCostChange"] = (
            BaselineSumRes["AnnualOperatingCost"].iloc[0] - dfRes.loc[0, "AnnualOperatingCost"]
        )

        if dfRes.loc[0, "OperatingCostChange"] != 0:
            dfRes.loc[0, "SPP"] = dfRes.loc[0, "TIC"] / dfRes.loc[0, "OperatingCostChange"]
        else:
            dfRes.loc[0, "SPP"] = 0

        dfRes.loc[0, "NPV"] = (
            -dfRes.loc[0, "TIC"]
            + BaselineSumRes["TOC"].iloc[0]
            - dfRes.loc[0, "TOC"]
        )

        if dfRes.loc[0, "TIC"] == 0:
            dfRes.loc[0, "ROI"] = 0
        else:
            dfRes.loc[0, "ROI"] = 100 * (
                (BaselineSumRes["TOC"].iloc[0] - dfRes.loc[0, "TOC"] - dfRes.loc[0, "TIC"])
                / dfRes.loc[0, "TIC"]
            )

        dfRes.to_csv(os.path.join(Package.OutputDir, "RunResults.csv"), index=False)

        Package.LCC = dfRes.loc[0, "LCC"]
        Package.SourceEnergy = dfRes.loc[0, "TotalSourceEnergy"]

        return dfRes



    def ComparePackageResults(self,Package, LastBestPackage,BasePackage):
        # Percentage savings are calculated based on the original base package
        # Slope calculation is with respect to the last best package
        if Package.SourceEnergy == LastBestPackage.SourceEnergy:
            Package.PctSourceSavings = 0
            Package.Slope_LCC_PctSS = 0
        else:
            Package.PctSourceSavings = 100*(BasePackage.SourceEnergy - Package.SourceEnergy)/BasePackage.SourceEnergy
            Package.Slope_LCC_PctSS = np.round((Package.LCC - LastBestPackage.LCC)/(Package.PctSourceSavings - LastBestPackage.PctSourceSavings), 2)
        return Package