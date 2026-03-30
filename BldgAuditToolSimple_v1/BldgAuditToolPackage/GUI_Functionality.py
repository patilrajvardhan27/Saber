import sys
import pandas as pd
from .GUI_Code import Ui_MainWindow
from .GUI_UtilityDataWindowCode import Ui_Form
from .AnalyzeUtilityData import *
from .PostProcessing import *
from .EEMPackageMeasureAnalysisObject import MeasurePackageAnalysis

from PyQt5.QtWidgets import QMainWindow, QFileDialog,QGraphicsScene, QTableWidgetItem, QGraphicsPixmapItem, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QTransform
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtCore import pyqtSlot
import pickle
from datetime import datetime
import numpy as np
import os 
import calendar
import shutil


class MyMainWindow(QMainWindow,Ui_MainWindow):

    def __init__(self):
        super().__init__()
        
        self.setupUi(self)
        self.df_input = pd.read_csv("Inputs/BldgPropInputsFileTemplate.csv")
        #%% Preferences
        self.BldgPropInputFile.setEnabled(False)
        self.UseExistingBldgPropInpFile.toggled.connect(self.SetUseExistingBldgPropInpFile)

        self.MainPath = os.getcwd()
        self.ProjectName.textChanged.connect(self.SetProjectName)
        
        #%% Set Utility Data
        self.OpenUtilDataWindow.setEnabled(False)
        self.UtilDataSourceFile.setEnabled(False)
        self.UtilDataSourceFileTool.setEnabled(False)
        self.NewBldgPropInpFile.toggled.connect(self.SetProjectPath)
        self.LoadUtilityData.setEnabled(False)
        self.EnterUtilData.toggled.connect(self.SetEnterUtilData)
        self.UseExistingUtilityData.toggled.connect(self.SetUseExistingUtilityData)
        
        self.OpenUtilDataWindow.clicked.connect(self.SetOpenUtilityDataWindow)

        self.LoadUtilityData.clicked.connect(self.SetLoadUtilityData)

        self.UtilDataSourceFileTool.clicked.connect(lambda: self.SetPathToFile(self.UtilDataSourceFile))

        
        #%%
        self.CoolingEffCustom.setEnabled(False)
        self.HeatingEffCustom.setEnabled(False)

        self.CoolingEqp.currentIndexChanged.connect(self.SetCoolingEffOptions)
        self.HeatingEqp.currentIndexChanged.connect(self.SetHeatingEffOptions)
        
        self.CoolingEff.currentIndexChanged.connect(self.SetCoolingEffChanged)
        self.HeatingEff.currentIndexChanged.connect(self.SetHeatingEffChanged)


        self.LoadData.clicked.connect(self.SetLoadData)
        self.SetSelections.clicked.connect(self.SetOriginalBldgPropFile)
    #%% SET EEM COST OPTIONS
        
        self.EEMCostTable.setCellWidget(0,1,self.ECMWallInsCostOptions)
        self.EEMCostTable.setCellWidget(1,1,self.ECMInfilCostOptions)
        self.EEMCostTable.setCellWidget(2,1,self.ECMCeilInsCostOptions)
        self.EEMCostTable.setCellWidget(3,1,self.ECMWindowMatCostOptions)
        self.EEMCostTable.setCellWidget(4,1,self.ECMNightSetbackCostOptions)
        self.EEMCostTable.setCellWidget(5,1,self.ECMHoursofNightSetbackCostOptions)
        self.EEMCostTable.setCellWidget(6,1,self.ECMDaylightingCostOptions)
        self.EEMCostTable.setCellWidget(7,1,self.ECMEconCostOptions)
        self.EEMCostTable.setCellWidget(8,1,self.ECMOccSensorCostOptions)
        self.EEMCostTable.setCellWidget(9,1,self.ECMLEDCostOptions)
        self.EEMCostTable.setCellWidget(10,1,self.ECMReduceEquipmentLoadCostOptions)
        self.EEMCostTable.setCellWidget(11,1,self.ECMCoolingEffCostOptions)
        self.EEMCostTable.setCellWidget(13,1,self.ECMHeatingEffCostOptions)
        self.EEMCostTable.setCellWidget(12,1,self.ECMHeatingEqpCostOptions)

        self.ECMWallInsCostOptions.currentIndexChanged.connect(self.SetECMWallInsCostOptions)
        self.ECMInfilCostOptions.currentIndexChanged.connect(self.SetECMInfiltrationCostOptions)
        self.ECMCeilInsCostOptions.currentIndexChanged.connect(self.SetECMCeilingInsCostOptions)
        self.ECMWindowMatCostOptions.currentIndexChanged.connect(self.SetECMWindowMatCostOptions)
        self.ECMNightSetbackCostOptions.currentIndexChanged.connect(self.SetECMNightSetbackCostOptions)
        self.ECMHoursofNightSetbackCostOptions.currentIndexChanged.connect(self.SetECMHoursofNightSetbackCostOptions)
        self.ECMDaylightingCostOptions.currentIndexChanged.connect(self.SetECMDaylightingCostOptions)
        self.ECMEconCostOptions.currentIndexChanged.connect(self.SetECMEconomizerCostOptions)
        self.ECMOccSensorCostOptions.currentIndexChanged.connect(self.SetECMOccSensorCostOptions)
        self.ECMLEDCostOptions.currentIndexChanged.connect(self.SetECMLEDLightingCostOptions)
        self.ECMReduceEquipmentLoadCostOptions.currentIndexChanged.connect(self.SetECMReduceEquipmentLoadCostOptions)
        self.ECMCoolingEffCostOptions.currentIndexChanged.connect(self.SetECMCoolingEffCostOptions)
        
        self.ECMHeatingEqpCostOptions.currentIndexChanged.connect(self.SetECMHeatingEqpCostOptions)
        self.ECMHeatingEffCostOptions.currentIndexChanged.connect(self.SetECMHeatingEffCostOptions)

        self.SetCostData.clicked.connect(self.SetSetCostData) 
        self.ResetCostData.clicked.connect(self.SetResetCostData)
    #%% ECM Evaluation

        

        self.ECMEval.setCellWidget(0,2,self.ECMWallInsOptions)
        self.ECMEval.setCellWidget(1,2,self.ECMInfilOptions)
        self.ECMEval.setCellWidget(2,2,self.ECMCeilInsOptions)
        self.ECMEval.setCellWidget(3,2,self.ECMWindowMatOptions)
        self.ECMEval.setCellWidget(4,2,self.ECMNightSetbackOptions)
        self.ECMEval.setCellWidget(5,2,self.ECMHoursofNightSetbackOptions)
        self.ECMEval.setCellWidget(6,2,self.ECMDaylightingOptions)
        self.ECMEval.setCellWidget(7,2,self.ECMEconOptions)
        self.ECMEval.setCellWidget(8,2,self.ECMOccSensorOptions)
        self.ECMEval.setCellWidget(9,2,self.ECMLEDOptions)
        self.ECMEval.setCellWidget(10,2,self.ECMReduceEquipmentLoadOptions)
        self.ECMEval.setCellWidget(11,2,self.ECMCoolingEffOptions)
        self.ECMEval.setCellWidget(12,2,self.ECMHeatingEqpOptions)
        self.ECMEval.setCellWidget(13,2,self.ECMHeatingEffOptions)

        self.ECMWallInsOptions.currentTextChanged.connect(self.SetWallInsChange)
        self.ECMInfilOptions.currentTextChanged.connect(self.SetInfilChange)
        self.ECMCeilInsOptions.currentTextChanged.connect(self.SetCeilInsChange)
        self.ECMWindowMatOptions.currentTextChanged.connect(self.SetWindowMatChange)
        self.ECMNightSetbackOptions.currentTextChanged.connect(self.SetNightSetbackChange)
        self.ECMHoursofNightSetbackOptions.textChanged.connect(self.SetHoursofNightSetbackChange)
        self.ECMDaylightingOptions.currentTextChanged.connect(self.SetDaylightingChange)
        self.ECMEconOptions.currentTextChanged.connect(self.SetEconomizerChange)
        self.ECMOccSensorOptions.currentTextChanged.connect(self.SetOccupancySensorChange)
        self.ECMLEDOptions.currentTextChanged.connect(self.SetLEDChange)
        self.ECMReduceEquipmentLoadOptions.currentTextChanged.connect(self.SetReduceEquipmentLoadChange)
        self.ECMCoolingEffOptions.currentTextChanged.connect(self.SetCoolingEffChange)
        self.ECMHeatingEffOptions.currentTextChanged.connect(self.SetHeatingEffChange)
        self.ECMHeatingEqpOptions.currentTextChanged.connect(self.SetHeatingEqpChange)

        self.EvaluateIndMeasures.clicked.connect(self.SetEvaluateIndMeasure)
        self.EvaluateMeasurePackage.clicked.connect(self.SetEvaluateMeasurePackage)
        self.SaveIndECMResults.clicked.connect(self.SetSaveIndECMResults)       
        self.SaveECMPackageResults.clicked.connect(self.SetSaveECMPackageResults)
        #%%
        self.SetShowBuildingType()
        self.BuildingType.currentIndexChanged.connect(self.SetShowBuildingType)

        self.ShapeType.itemClicked.connect(self.SetShowShape)
        self.Orientation.itemClicked.connect(self.SetShowOrientation)

        self.SetShowExtWall()
        self.ExtWallConst.currentIndexChanged.connect(self.SetShowExtWall)

        self.SetShowExtRoof()   
        self.ExtRoofConst.currentIndexChanged.connect(self.SetShowExtRoof)

        self.SetShowFoundation()
        self.Foundation.currentIndexChanged.connect(self.SetShowFoundation)

        self.WindowMaterial.itemClicked.connect(self.SetShowWindowMaterial)
        self.SetShowShading()

        self.SetShowCoolingEqp()
        self.CoolingEqp.currentIndexChanged.connect(self.SetShowCoolingEqp)

        self.SetShowHeatingEqp()
        self.HeatingEqp.currentIndexChanged.connect(self.SetShowHeatingEqp)

        self.SetShowDHWSystemType()

        #%%
        self.DHWSystemType.currentIndexChanged.connect(self.SetShowDHWSystemType)

        self.GetWeatherData.clicked.connect(self.SetGetWeatherData)

        self.RunTempChangePointAnalysis.clicked.connect(self.SetRunTempChangePointAnalysis)

        self.RunDegreeDayAnalysis.clicked.connect(self.SetRunDegreeDayAnalysis)
    #%%
    def SetRunTempChangePointAnalysis(self):
        self.SetSetSelections()
        self.CPT = BuildChangePointModel(self.ProjectPath,self.ProjectName.text(),self.df_input,self.df_weather)
        self.model_type_cooling, self.model_parameters_cooling,  self.model_type_heating, self.model_parameters_heating = self.CPT.BuildTemperatureBasedModel()
        self.sceneHeatingTempCPT = QGraphicsScene(self)
        self.HeatingTempResults.setScene(self.sceneHeatingTempCPT)
        imagePath = os.path.join(self.ProjectPath,f"Fossil Fuel_{self.model_type_heating}_TempBasedChngPtModel.png")
        self.ShowGUIImage(self.sceneHeatingTempCPT,self.HeatingTempResults,imagePath)

        self.sceneCoolingTempCPT = QGraphicsScene(self)
        self.CoolingTempResults.setScene(self.sceneCoolingTempCPT)
        imagePath = os.path.join(self.ProjectPath,f"Electricity_{self.model_type_cooling}_TempBasedChngPtModel.png")
        self.ShowGUIImage(self.sceneCoolingTempCPT,self.CoolingTempResults,imagePath)

    def GetMonthlyEndUseBreakdown(self):
        ECMEval = False
        self.BestModelParams = self.CPT.ChooseBestModel(self.DDResults,self.model_parameters_heating,self.model_parameters_cooling)
        #print(self.BestModelParams)
        self.df_MonthlyEndUse = GetMonthlyEndUseBreakdown(self.BestModelParams,self.df_weather,self.df_input,ECMEval)
        # print("End Use", self.df_MonthlyEndUse, "Total", self.df_MonthlyEndUse.loc[:,self.df_MonthlyEndUse.columns.str.contains("EL-")].sum())
        self.BestModelParams["OrgTotalElectricity"] = self.df_MonthlyEndUse.loc[:,self.df_MonthlyEndUse.columns.str.contains("EL-")].sum().sum()/3.41 # Convert to kWh
        self.BestModelParams["OrgTotalNaturalGas"] = self.df_MonthlyEndUse.loc[:,self.df_MonthlyEndUse.columns.str.contains("NG-")].sum().sum()/100 # Convert to Therms
        self.BestModelParams["BLC_Heat_EL"] = self.df_MonthlyEndUse["BLC_Heat_EL"].mean()
        self.BestModelParams["BLC_Heat_NG"] = self.df_MonthlyEndUse["BLC_Heat_NG"].mean()

        self.BestModelParams["BLC_Cool_EL"] = self.df_MonthlyEndUse["BLC_Cool_EL"].mean()
        #print(self.BestModelParams)

        self.PltRes = PlotResults(True,self.ProjectPath)
        self.PltRes.PlotEndUseBreakdown(self.df_MonthlyEndUse)
        self.PltRes.PlotInverseModelComparison(self.df_MonthlyEndUse, self.dfutilDataSorted)

        self.sceneEndUseBreakdown = QGraphicsScene(self)
        self.ShowEndUseBreakdown.setScene(self.sceneEndUseBreakdown)
        imagePath = os.path.join(self.ProjectPath,f"EndUseBreakdown.png")
        self.ShowGUIImage(self.sceneEndUseBreakdown,self.ShowEndUseBreakdown,imagePath)

        self.scenekWhEndUseBreakdown = QGraphicsScene(self)
        self.kWhModelComparison.setScene(self.scenekWhEndUseBreakdown)
        imagePath = os.path.join(self.ProjectPath,f"ElectricityMonthlyBreakdown.png")
        self.ShowGUIImage(self.scenekWhEndUseBreakdown,self.kWhModelComparison,imagePath)

        self.sceneThermEndUseBreakdown = QGraphicsScene(self)
        self.ThermModelComparison.setScene(self.sceneThermEndUseBreakdown)
        imagePath = os.path.join(self.ProjectPath,f"NaturalGasMonthlyBreakdown.png")
        self.ShowGUIImage(self.sceneThermEndUseBreakdown,self.ThermModelComparison,imagePath)


    def SetRunDegreeDayAnalysis(self):

        # Check if temperature based analysis is run and correspoding attribtues exist. If not run it first
        if (not hasattr(self, 'model_type_cooling') or self.model_type_cooling is None) and \
            (not hasattr(self, 'model_parameters_cooling') or self.model_parameters_cooling is None) and \
            (not hasattr(self, 'model_type_heating') or self.model_type_heating is None) and \
            (not hasattr(self, 'model_parameters_heating') or self.model_parameters_heating is None):
            self.SetRunTempChangePointAnalysis()
        self.DDResults,self.dfutilDataSorted = self.CPT.BuildDegreeDayBasedModel(self.model_type_cooling, self.model_parameters_cooling,  self.model_type_heating, self.model_parameters_heating)

        self.sceneHeatingDDCPT = QGraphicsScene(self)
        self.HeatingDDResults.setScene(self.sceneHeatingDDCPT)
        imagePath = os.path.join(self.ProjectPath,f"FossilFuel_Heating_DDBasedChngPtModel.png")
        self.ShowGUIImage(self.sceneHeatingDDCPT,self.HeatingDDResults,imagePath)
        
        self.sceneCoolingDDCPT = QGraphicsScene(self)
        self.CoolingDDResults.setScene(self.sceneCoolingDDCPT)
        imagePath = os.path.join(self.ProjectPath,f"Electricity_Cooling_DDBasedChngPtModel.png")
        self.ShowGUIImage(self.sceneCoolingDDCPT,self.CoolingDDResults,imagePath)

        self.GetMonthlyEndUseBreakdown()

    def SetGetWeatherData(self):
        if any(f.startswith("WeatherData") and f.endswith(".csv") for f in os.listdir(self.ProjectPath)):
            self.df_weather = pd.read_csv(os.path.join(self.ProjectPath,[f for f in os.listdir(self.ProjectPath) if f.startswith("WeatherData") and f.endswith(".csv")][0]))
            self.df_weather = self.df_weather.set_index("Datetime")
            self.df_weather.index = pd.to_datetime(self.df_weather.index)
            weather_station_name = [f for f in os.listdir(self.ProjectPath) if f.startswith("WeatherData") and f.endswith(".csv")][0].replace("WeatherData","").replace(".csv","")
        else:
            self.df_weather,weather_station_name = GetWeather(self.ProjectPath,self.ProjectName.text(),self.Location.text())
        
        PltRes = PlotResults(True,self.ProjectPath)
        PltRes.PlotWeather(self.df_weather,weather_station_name)
        self.sceneWeather = QGraphicsScene(self)
        self.ShowWeatherData.setScene(self.sceneWeather)
        imagePath = os.path.join(self.ProjectPath,f"WeatherPlot_{weather_station_name}.png")
        self.ShowGUIImage(self.sceneWeather,self.ShowWeatherData,imagePath)

#%%
    def SetShowBuildingType(self):
        self.sceneBuildingType = QGraphicsScene(self)
        self.ShowBuildingType.setScene(self.sceneBuildingType)
        imagePath = os.path.join("Inputs/ShapeFigures/",self.BuildingType.currentText())
        self.ShowGUIImage(self.sceneBuildingType,self.ShowBuildingType,imagePath)

    def SetShowShape(self):
        self.sceneShape = QGraphicsScene(self)
        self.ShowShape.setScene(self.sceneShape)
        imagePath = os.path.join("Inputs/ShapeFigures/",self.ShapeType.currentItem().text())
        self.ShowGUIImage(self.sceneShape,self.ShowShape,imagePath)

    def SetShowOrientation(self):
        Omap = {"North":0,"South":180,"West":270,"East":90,"North East":45,"South East":135,"South West":225,"North West":315}
        self.sceneOrientation = QGraphicsScene(self)
        self.ShowShape.setScene(self.sceneOrientation)
        image = os.path.join("Inputs/ShapeFigures/",self.ShapeType.currentItem().text())
        
        pixmap = QPixmap(image)
        view_width = self.ShowShape.width()
        view_height = self.ShowShape.height()

        # Scale the pixmap to fit the view's size while maintaining its aspect ratio
        scaled_pixmap = pixmap.scaled(view_width, view_height, aspectRatioMode=True, transformMode=Qt.SmoothTransformation)
        self.sceneOrientation.clear()

        pixmapItem = QGraphicsPixmapItem(scaled_pixmap)
        self.sceneOrientation.addItem(pixmapItem)

        self.sceneOrientation.setSceneRect(pixmapItem.boundingRect())
        border = pixmapItem.boundingRect()

        centerX = border.width() / 2
        centerY = border.height() / 2

        transform = QTransform()
        transform.translate(centerX,centerY)
        transform.rotate(Omap[self.Orientation.currentItem().text()])
        transform.translate(-centerX,-centerY)

        pixmapItem.setTransform(transform)
        rotatedBorder = pixmapItem.mapToScene(pixmapItem.boundingRect()).boundingRect()
        self.sceneOrientation.setSceneRect(rotatedBorder)

        # Set the scene to the QGraphicsView
        self.ShowShape.setScene(self.sceneOrientation)
        self.ShowShape.centerOn(self.sceneOrientation.sceneRect().center())
        self.ShowShape.setRenderHint(QPainter.Antialiasing, True)
        self.ShowShape.setRenderHint(QPainter.SmoothPixmapTransform, True)

    def SetShowExtWall(self):
        self.sceneExtWall = QGraphicsScene(self)
        self.ShowExtWall.setScene(self.sceneExtWall)
        imagePath = os.path.join("Inputs/ShapeFigures/",self.ExtWallConst.currentText())
        self.ShowGUIImage(self.sceneExtWall,self.ShowExtWall,imagePath)
    
    def SetShowExtRoof(self):
        self.sceneExtRoof = QGraphicsScene(self)
        self.ShowExtRoof.setScene(self.sceneExtRoof)
        imagePath = os.path.join("Inputs/ShapeFigures/",self.ExtRoofConst.currentText())
        self.ShowGUIImage(self.sceneExtRoof,self.ShowExtRoof,imagePath)

    def SetShowFoundation(self):
        self.sceneFoundation = QGraphicsScene(self)
        self.ShowFoundation.setScene(self.sceneFoundation)
        imagePath = os.path.join("Inputs/ShapeFigures/",self.Foundation.currentText())
        self.ShowGUIImage(self.sceneFoundation,self.ShowFoundation,imagePath)

    def SetShowWindowMaterial(self):
        self.sceneWindowMaterial = QGraphicsScene(self)
        self.ShowWindowMaterial.setScene(self.sceneWindowMaterial)
        imagePath = os.path.join("Inputs/ShapeFigures/",self.WindowMaterial.currentItem().text())
        self.ShowGUIImage(self.sceneWindowMaterial,self.ShowWindowMaterial,imagePath)

    def SetShowShading(self):
        self.sceneShading = QGraphicsScene(self)
        self.ShowShading.setScene(self.sceneShading)
        imagePath = os.path.join("Inputs/ShapeFigures/","Shading Overhang")
        self.ShowGUIImage(self.sceneShading,self.ShowShading,imagePath)

    def SetShowCoolingEqp(self):
        self.sceneCoolingEqp = QGraphicsScene(self)
        self.ShowCoolingEqp.setScene(self.sceneCoolingEqp)
        imagePath = os.path.join("Inputs/ShapeFigures/CoolingEqp/",self.CoolingEqp.currentText())
        self.ShowGUIImage(self.sceneCoolingEqp,self.ShowCoolingEqp,imagePath)

    def SetShowHeatingEqp(self):
        self.sceneHeatingEqp = QGraphicsScene(self)
        self.ShowHeatingEqp.setScene(self.sceneHeatingEqp)
        imagePath = os.path.join("Inputs/ShapeFigures/HeatingEqp/",self.HeatingEqp.currentText())
        self.ShowGUIImage(self.sceneHeatingEqp,self.ShowHeatingEqp,imagePath)
    
    def SetShowDHWSystemType(self):
        self.sceneDHWSystemType = QGraphicsScene(self)
        self.ShowDHWSystemType.setScene(self.sceneDHWSystemType)
        imagePath = os.path.join("Inputs/ShapeFigures/DHWEqp/",self.DHWSystemType.currentText())
        self.ShowGUIImage(self.sceneDHWSystemType,self.ShowDHWSystemType,imagePath)

    def ShowGUIImage(self,scene,view,image):
        pixmap = QPixmap(image)
        view_width = view.width()
        view_height = view.height()

        # Scale the pixmap to fit the view's size while maintaining its aspect ratio
        scaled_pixmap = pixmap.scaled(view_width, view_height, aspectRatioMode=True, transformMode=Qt.SmoothTransformation)
        scene.clear()

        pixmapItem = QGraphicsPixmapItem(scaled_pixmap)
        scene.addItem(pixmapItem)

        scene.setSceneRect(pixmapItem.boundingRect())

        # Set the scene to the QGraphicsView
        view.setScene(scene)
        view.centerOn(scene.sceneRect().center())
        view.setRenderHint(QPainter.Antialiasing, True)
        view.setRenderHint(QPainter.SmoothPixmapTransform, True)
#%%
    def SetPathToFile(self, line_edit):
        """
        Opens a file selection dialog and sets the chosen path to the provided QLineEdit.
    
        Args:
            self (QtWidgets): The object instance calling the function (usually a window or widget).
            line_edit (QLineEdit): The QLineEdit object to set the path in.
        """
    
        options = QFileDialog.Options()
        # Consider adding options like QFileDialog.ReadOnly or QFileDialog.DontUseNativeDialog
        # based on your specific requirements.
    
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*.*)", options=options)
    
        if file_path:
            # Validate the selected path (optional)
            if os.path.isfile(file_path):
                line_edit.setText(file_path)
            else:
                # Handle invalid path (e.g., show a warning message)
                print("Selected path is not a valid file.")
        else:
            # Handle user cancellation (optional)
            print("No file selected.")
    
    def SetPathFolder(self,Name):
        options =  QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        folder_path = QFileDialog.getExistingDirectory(self)
        if folder_path:
            Name.setText(folder_path)
    
            
    def SetLoadData(self):
        try:
            self.df_input = pd.read_pickle(self.BldgPropInputFile.text())
            
        except:
            print("Please enter a valid properties input file.")
        self.BuildingType.setCurrentText(self.df_input.loc[self.df_input.PropKey=="BuildingType","PropValue"].item())
        self.SetShowBuildingType()
        self.Location.setText(self.df_input.loc[self.df_input.PropKey=="Location","PropValue"].item())
        
        self.FloorArea.setText(self.df_input.loc[self.df_input.PropKey=="FloorArea","PropValue"].astype(str).item())
        self.FlrQty.setText(self.df_input.loc[self.df_input.PropKey=="FloorQty","PropValue"].astype(str).item())
        self.WallHt.setText(self.df_input.loc[self.df_input.PropKey=="WallHeight","PropValue"].astype(str).item())
        self.x1.setText(self.df_input.loc[self.df_input.PropKey=="x1","PropValue"].astype(str).iloc[0])
        self.x2.setText(self.df_input.loc[self.df_input.PropKey=="x2","PropValue"].astype(str).iloc[0])
        self.y1.setText(self.df_input.loc[self.df_input.PropKey=="y1","PropValue"].astype(str).iloc[0])
        self.y2.setText(self.df_input.loc[self.df_input.PropKey=="y2","PropValue"].astype(str).iloc[0])
        
        self.MatchListItem(self.ShapeType,self.df_input.loc[self.df_input.PropKey=="Shape","PropValue"].item())
        self.SetShowShape()
        self.MatchListItem (self.Orientation,self.df_input.loc[self.df_input.PropKey=="Orientation","PropValue"].item())
        self.SetShowOrientation()

        self.WallInsulation.setCurrentText(self.df_input.loc[self.df_input.PropKey=="R-WallInsulation","PropValue"].item())
        self.ExtWallConst.setCurrentText(self.df_input.loc[self.df_input.PropKey=="ExtWallConst","PropValue"].item())
        self.SetShowExtWall()
        self.ExtRoofConst.setCurrentText(self.df_input.loc[self.df_input.PropKey=="ExtRoofConst","PropValue"].item())
        self.SetShowExtRoof()
        self.CeilingInsulation.setCurrentText(self.df_input.loc[self.df_input.PropKey=="R-CeilingInsulation","PropValue"].item())
        self.SlabInsulation.setCurrentText(self.df_input.loc[self.df_input.PropKey=="R-SlabInsulation","PropValue"].item())
        self.Foundation.setCurrentText(self.df_input.loc[self.df_input.PropKey=="Foundation","PropValue"].item())
        self.SetShowFoundation()
        self.ACH50.setCurrentText(self.df_input.loc[self.df_input.PropKey=="ACH50","PropValue"].astype(str).item())
        self.MatchListItem(self.WindowMaterial,self.df_input.loc[self.df_input.PropKey=="WindowMaterial","PropValue"].item())
        self.SetShowWindowMaterial()
        self.WWR_Front.setText(self.df_input.loc[self.df_input.PropKey=="WWR_Front","PropValue"].astype(str).item())
        self.WWR_Left.setText(self.df_input.loc[self.df_input.PropKey=="WWR_Left","PropValue"].astype(str).item())
        self.WWR_Back.setText(self.df_input.loc[self.df_input.PropKey=="WWR_Back","PropValue"].astype(str).item())
        self.WWR_Right.setText(self.df_input.loc[self.df_input.PropKey=="WWR_Right","PropValue"].astype(str).item())
        self.Overhang.setText(self.df_input.loc[self.df_input.PropKey=="overhangdepth","PropValue"].astype(str).item())
        self.SetShowShading()
        self.WindowHt.setText(self.df_input.loc[self.df_input.PropKey=="WindowHeight","PropValue"].astype(str).item())
        self.nWindow.setText(self.df_input.loc[self.df_input.PropKey=="nWindow","PropValue"].astype(str).item())
        self.SetShowWindowMaterial()

        self.CoolingEqp.setCurrentText(self.df_input.loc[self.df_input.PropKey=="CoolingEquipment","PropValue"].astype(str).item()) 
        self.SetShowCoolingEqp()
        self.SetCoolingEffOptions()
        self.CoolingEff.setCurrentText(str(self.df_input.loc[self.df_input.PropKey=="CoolingEff","PropValue"].iloc[0]))
        self.SetCoolingEffChanged()
        if self.CoolingEffCustom.isEnabled():
            self.CoolingEffCustom.setText(str(self.df_input.loc[self.df_input.PropKey=="CoolingEffCustom","PropValue"].iloc[0]))

        self.HeatingEqp.setCurrentText(self.df_input.loc[self.df_input.PropKey=="HeatingEquipment","PropValue"].astype(str).item())
        self.SetShowHeatingEqp()
        self.SetHeatingEffOptions()
        self.HeatingEff.setCurrentText(str(self.df_input.loc[self.df_input.PropKey=="HeatingEff","PropValue"].iloc[0]))
        self.SetHeatingEffChanged()
        if self.HeatingEffCustom.isEnabled():
            self.HeatingEffCustom.setText(str(self.df_input.loc[self.df_input.PropKey=="HeatingEffCustom","PropValue"].iloc[0]))



        self.Economizer.setCurrentText(self.df_input.loc[self.df_input.PropKey=="Economizer","PropValue"].astype(str).item())
        self.SwampCooler.setCurrentText(self.df_input.loc[self.df_input.PropKey=="SwampCooler","PropValue"].astype(str).item())

        self.Tsph.setText(self.df_input.loc[self.df_input.PropKey=="Tsph","PropValue"].astype(str).item())
        self.Tspc.setText(self.df_input.loc[self.df_input.PropKey=="Tspc","PropValue"].astype(str).item())
        
        self.NightSetback.setCurrentText(self.df_input.loc[self.df_input.PropKey=="NightSetback","PropValue"].astype(str).item())
        # self.CoolingSetback.setCurrentText(self.df_input.loc[self.df_input.PropKey=="CoolingSetback","PropValue"].astype(str).item())
        self.nNightSetbackHours.setText(self.df_input.loc[self.df_input.PropKey=="nNightSetbackHours","PropValue"].astype(str).item())

        self.DHWSystemType.setCurrentText(self.df_input.loc[self.df_input.PropKey=="DHWSystemType","PropValue"].item()) 
        self.DHWTankVol.setText(self.df_input.loc[self.df_input.PropKey=="DHWTankVol","PropValue"].astype(str).item())
        
        self.CookingFuelType.setCurrentText(self.df_input.loc[self.df_input.PropKey=="CookingFuelType","PropValue"].item())
        self.CookingRating.setText(self.df_input.loc[self.df_input.PropKey=="CookingRangeRating","PropValue"].astype(str).item())
        self.DishWasherRating.setText(self.df_input.loc[self.df_input.PropKey=="DishwasherRating","PropValue"].astype(str).item())
        self.FridgeRating.setText(self.df_input.loc[self.df_input.PropKey=="FridgeRating","PropValue"].astype(str).item())
        self.WasherRating.setText(self.df_input.loc[self.df_input.PropKey=="WasherRating","PropValue"].astype(str).item())
        self.DryerRating.setText(self.df_input.loc[self.df_input.PropKey=="DryerRating","PropValue"].astype(str).item())
        self.TVRating.setText(self.df_input.loc[self.df_input.PropKey=="MiscTVRating","PropValue"].astype(str).item())
        self.OfficeEqpRating.setText(self.df_input.loc[self.df_input.PropKey=="OfficeEqpRating","PropValue"].astype(str).item())
        self.MiscPlugLoadRating.setText(self.df_input.loc[self.df_input.PropKey=="MiscPlugLoadRating","PropValue"].astype(str).item())
        self.LPD.setText(self.df_input.loc[self.df_input.PropKey=="LPD","PropValue"].astype(str).item())
        self.nHoursLighting.setText(self.df_input.loc[self.df_input.PropKey=="nHoursLighting","PropValue"].astype(str).item())
        self.Daylighting.setCurrentText(self.df_input.loc[self.df_input.PropKey=="Daylighting","PropValue"].astype(str).item())
        if self.df_input.loc[self.df_input.PropKey=="LEDECM","PropValue"].astype(float).item() < self.df_input.loc[self.df_input.PropKey=="LEDCurrent","PropValue"].astype(float).item():
            self.LED.setCurrentText(self.df_input.loc[self.df_input.PropKey=="LEDCurrent","PropValue"].astype(str).item())
        else:
            self.LED.setCurrentText(self.df_input.loc[self.df_input.PropKey=="LEDECM","PropValue"].astype(str).item())    
        #self.EquipLoadRed.setText(self.df_input.loc[self.df_input.PropKey=="EquipLoadRed","PropValue"].astype(str).item())
        
        
        
    def MatchListItem(self,listwidget,matchstring):
        for index in range(listwidget.count()):
            item = listwidget.item(index)
            if item.text() == matchstring:
                listwidget.setCurrentItem(item)
                break
    
    def SetSetSelections(self):
        self.df_input = pd.read_csv("Inputs/BldgPropInputsFileTemplate.csv")
        self.SetProjectPath()
        self.SetResultFolder()
        self.SetBuildingType(self.BuildingType.currentText())
        
        self.SetLocation(self.Location.text())
        self.SetOrientation(self.Orientation.currentItem())
        self.SetFloorArea(self.FloorArea.text())
        self.SetFloorQty(self.FlrQty.text())
        self.SetWallHeight(self.WallHt.text())
        self.Setx1(self.x1.text())
        self.Setx2(self.x2.text())
        self.Sety1(self.y1.text())
        self.Sety2(self.y2.text())
        self.SetShapeP1()
        self.SetShapeP2()
        self.SetAspectRatio()
        self.SetShapeType(self.ShapeType.currentItem())
        
        self.SetWallInsulation(self.WallInsulation.currentText())
        self.SetExtWallConst(self.ExtWallConst.currentText())
        self.SetExtRoofConst(self.ExtRoofConst.currentText())
        self.SetCeilingInsulation(self.CeilingInsulation.currentText())
        self.SetSlabInsulation(self.SlabInsulation.currentText())
        self.SetFoundation(self.Foundation.currentText())
        self.SetInfiltration(self.ACH50.currentText())
        self.SetWindowMaterial(self.WindowMaterial.currentItem())
        
        self.WWR = {}
        self.SetWWRFront(self.WWR_Front.text())
        self.SetWWRLeft(self.WWR_Left.text())
        self.SetWWRBack(self.WWR_Back.text())
        self.SetWWRRight(self.WWR_Right.text())
        self.SetWWR()
        self.SetOverhang(self.Overhang.text())
        self.SetWindowHeight(self.WindowHt.text())
        self.SetnWindows(self.nWindow.text())
        
        self.SetCoolingEqp(self.CoolingEqp.currentText())
        self.SetCoolingEff(self.CoolingEff.currentText())
        if self.CoolingEff.currentText() == "Other..":
            self.SetCoolingEffCustom(self.CoolingEffCustom.text())
        self.SetHeatingEqp(self.HeatingEqp.currentText())
        self.SetHeatingEff(self.HeatingEff.currentText())
        if self.HeatingEff.currentText() == "Other..":
            self.SetHeatingEffCustom(self.HeatingEffCustom.text())
        
        self.SetEconomizer(self.Economizer.currentText())
        self.SetSwampCooler(self.SwampCooler.currentText())


        self.SetTsph(self.Tsph.text())
        self.SetTspc(self.Tspc.text())
        self.SetNightSetback(self.NightSetback.currentText())
        self.SetNightSetbackHours(self.nNightSetbackHours.text())
        # self.SetCoolingSetback(self.CoolingSetback.currentText())
        self.SetDHWSystemType(self.DHWSystemType.currentText())
        self.SetDHWTankVol(self.DHWTankVol.text())
        
        self.SetCookingFuelType(self.CookingFuelType.currentText())
        self.SetCookingRating(self.CookingRating.text())
        self.SetFridgeRating(self.FridgeRating.text())
        self.SetDishWasherRating(self.DishWasherRating.text())
        self.SetWasherRating(self.WasherRating.text())
        self.SetDryerRating(self.DryerRating.text())
        self.SetTVRating(self.TVRating.text())
        self.SetOfficeEqpRating(self.OfficeEqpRating.text())
        self.SetMiscPlugLoadRating(self.MiscPlugLoadRating.text())
        self.SetLPD(self.LPD.text())
        self.SetLightingHours(self.nHoursLighting.text())
        self.SetDaylighting(self.Daylighting.currentText())
        self.SetLEDCurrent(self.LED.currentText())
        #no user input for Reduce Equipment Load only change is in EEMs

        self.df_input.to_pickle(os.path.join(self.ProjectPath,"BldgPropInputsFile.pkl"))
        ## Construct the required IDF file and save in Current Directory

        
    
    def SetOriginalBldgPropFile(self):
        self.SetSetSelections()
        self.CopyCostData()
        self.df_input.to_pickle(os.path.join(self.ProjectPath,"BldgPropInputFile-Baseline.pkl"))

    def SetUseExistingUtilityData(self,checked):
        self.UtilDataSourceFile.setEnabled(checked)
        self.UtilDataSourceFileTool.setEnabled(checked)
        self.LoadUtilityData.setEnabled(checked)

    def SetOpenUtilityDataWindow(self):
        self.UtilityDataWindow = UtilityDataWindow(self.ProjectPath,self.ProjectName.text())
        self.UtilityDataWindow.show()

    def SetLoadUtilityData(self):
        self.UtilityDataWindow = UtilityDataWindow(self.ProjectPath,self.ProjectName.text())
        self.UtilityDataWindow.show()
        dfutildata = pd.read_csv(self.UtilDataSourceFile.text(),index_col=0)
        dfutildata = dfutildata.drop(columns={"BillDays"})
        for row in range(len(dfutildata)):
            for col in range(len(dfutildata.columns)):
                self.UtilityDataWindow.UtilityDataTable.setItem(row, col, QTableWidgetItem(str(dfutildata.iat[row, col])))
        
        Year1 = str(dfutildata.columns[0]).replace("Year 1 - kWh","")
        Year2 = str(dfutildata.columns[2]).replace("Year 2 - kWh","")
        Year3 = str(dfutildata.columns[4]).replace("Year 3 - kWh","")
        self.UtilityDataWindow.Year1.setCurrentText(Year1)
        self.UtilityDataWindow.Year2.setCurrentText(Year2)
        self.UtilityDataWindow.Year3.setCurrentText(Year3)

    def SetResultFolder(self):
        if not os.path.exists(os.path.join(self.ProjectPath, "Results")):
            # Create the folder
            os.makedirs(os.path.join(self.ProjectPath, "Results"))


        
    def SetUseExistingBldgPropInpFile(self,checked):
        self.BldgPropInputFile.setEnabled(checked)
        self.BldgPropInputFileTool.clicked.connect(lambda: self.SetPathToFile(self.BldgPropInputFile))

    def SetEnterUtilData(self,checked):
        self.OpenUtilDataWindow.setEnabled(checked)

    def SetProjectName(self):
        self.ProjectPath = os.path.join(self.MainPath, "Projects", self.ProjectName.text())
        
    def SetProjectPath(self):
        os.makedirs(self.ProjectPath,exist_ok=True)
        
        self.SetResultFolder()
        self.CopyCostData()

    def SetLocation(self,text):
        self.df_input.loc[self.df_input.PropKey=="Location","PropValue"] = text

    def SetBuildingType(self,text):
        self.df_input.loc[self.df_input.PropKey=="BuildingType","PropValue"] = text
    
        
    def SetOrientation(self,item):
        # Odeg = self.Orientation.row(item)
        # Odeg = 45*Odeg
        self.df_input.loc[self.df_input.PropKey=="Orientation","PropValue"] = item.text()
        
    def SetFloorArea(self,text):
        self.df_input.loc[self.df_input.PropKey=="FloorArea","PropValue"] = float(text)
        
    def SetFloorQty(self,text):
        self.df_input.loc[self.df_input.PropKey=="FloorQty","PropValue"] = float(text)
        
    def SetWallHeight(self,text):
        self.df_input.loc[self.df_input.PropKey=="WallHeight","PropValue"] = float(text)
    
    def Setx1(self,text):
        self.df_input.loc[self.df_input.PropKey=="x1","PropValue"] = float(text)
    
    def Setx2(self,text):
        self.df_input.loc[self.df_input.PropKey=="x2","PropValue"] = float(text)

    def Sety1(self,text):
        self.df_input.loc[self.df_input.PropKey=="y1","PropValue"] = float(text)
    
    def Sety2(self,text):
        self.df_input.loc[self.df_input.PropKey=="y2","PropValue"] = float(text)

    def SetShapeP1(self):
        self.df_input.loc[self.df_input.PropKey=="P1","PropValue"] = float(self.x2.text())/float(self.x1.text())
        
    def SetShapeP2(self):
        self.df_input.loc[self.df_input.PropKey=="P2","PropValue"] = float(self.y2.text())/float(self.y1.text())
        
    def SetAspectRatio(self):
        self.df_input.loc[self.df_input.PropKey=="AR","PropValue"] = float(self.x1.text())/float(self.y1.text())
    
    def SetShapeType(self,item):
        self.df_input.loc[self.df_input.PropKey=="Shape","PropValue"] = item.text()

    def SetWallInsulation(self,text):
        
        self.df_input.loc[self.df_input.PropKey=="R-WallInsulation","PropValue"] = text# float(WallIns["Rvalue_IP"].iloc[self.WallInsulation.row(item)-1])
    
    def SetExtWallConst(self,text):
        self.df_input.loc[self.df_input.PropKey=="ExtWallConst","PropValue"] = text

    def SetExtRoofConst(self,text):
        self.df_input.loc[self.df_input.PropKey=="ExtRoofConst","PropValue"] = text

    def SetCeilingInsulation(self,text):
        
        self.df_input.loc[self.df_input.PropKey=="R-CeilingInsulation","PropValue"] = text #float(CeilIns["Rvalue_IP"].iloc[self.CeilingInsulation.row(item)-1])
        
    def SetSlabInsulation(self,text):
        
        # SlabIns = pd.read_csv("Measures/Materials-SlabInsulation.csv")
        self.df_input.loc[self.df_input.PropKey=="R-SlabInsulation","PropValue"] = text#float(SlabIns["Rvalue_IP"].iloc[self.SlabInsulation.row(item)-1])
        
    def SetFoundation(self,text):
        self.df_input.loc[self.df_input.PropKey=="Foundation","PropValue"] = text
    
    def SetInfiltration(self,text):
        self.df_input.loc[self.df_input.PropKey=="ACH50","PropValue"] = text #float(self.ACH50.currentText().replace(" ACH50",""))
        
    def SetWindowMaterial(self,item):
        try:
            self.df_input.loc[self.df_input.PropKey=="WindowMaterial","PropValue"] = item.text() #WindowMat["WindowMaterial"].iloc[self.WindowMaterial.row(item)]
        except:
            self.df_input.loc[self.df_input.PropKey=="WindowMaterial","PropValue"] = item 
        
    def SetWWRFront(self,text):
        self.df_input.loc[self.df_input.PropKey=="WWR_Front","PropValue"] = float(text)
        self.WWR["Front"] = float(text)

    def SetWWRLeft(self,text):
        self.df_input.loc[self.df_input.PropKey=="WWR_Left","PropValue"] = float(text)
        self.WWR["Left"] = float(text)

    def SetWWRBack(self,text):
        self.df_input.loc[self.df_input.PropKey=="WWR_Back","PropValue"] = float(text)
        self.WWR["Back"] = float(text)

    def SetWWRRight(self,text):
        self.df_input.loc[self.df_input.PropKey=="WWR_Right","PropValue"] = float(text)
        self.WWR["Right"] = float(text)

    def SetWWR(self):
        self.df_input.loc[self.df_input.PropKey=="WWR","PropValue"] = [self.WWR]
    
    def SetOverhang(self,text):
        self.df_input.loc[self.df_input.PropKey=="overhangdepth","PropValue"] = float(text)
    
    def SetWindowHeight(self,text):
        self.df_input.loc[self.df_input.PropKey=="WindowHeight","PropValue"] = float(text)
    
    def SetnWindows(self,text):
        self.df_input.loc[self.df_input.PropKey=="nWindow","PropValue"] = float(text)
    
    def SetCoolingEqp(self,text):
        self.df_input.loc[self.df_input.PropKey=="CoolingEquipment","PropValue"] = text
    
    def SetCoolingEffOptions(self):
        if "No" not in self.CoolingEqp.currentText():
            self.CoolingEqpOptions = pd.read_csv(os.path.join(self.ProjectPath, "CostData","System-"+self.CoolingEqp.currentText().replace(" ","")+".csv"))
            CoolingEffOptions = self.CoolingEqpOptions["SEER"].astype(str).tolist() + ["Other.."]
        else:
            self.CoolingEqpOptions = pd.read_csv(os.path.join(self.ProjectPath, "CostData","System-"+self.CoolingEqp.currentText().replace(" ","")+".csv"))
            CoolingEffOptions = self.CoolingEqpOptions["SEER"].astype(str).tolist() + ["Other.."]

        if "Air Source Heat Pump" in self.CoolingEqp.currentText():
            self.HeatingEqp.setCurrentText(self.CoolingEqp.currentText())
        
        self.CoolingEff.clear()
        self.CoolingEff.addItems(CoolingEffOptions)

    def SetCoolingEffChanged(self):
        
        # If "Other..." is selected, make combobox editable
        if self.CoolingEff.currentText() == "Other..":
            self.CoolingEffCustom.setEnabled(True)

        if "Air Source Heat Pump" in self.HeatingEqp.currentText() and "Air Source Heat Pump" in self.CoolingEqp.currentText():
            self.GetHeatingSystemOptions(self.HeatingEqp.currentText().replace(" ",""))
            SEERItems = self.HeatingEqpOptions["SEER"].astype(str).tolist() + ["Other.."]
            HSPFItems = self.HeatingEqpOptions["HeatingEff"].astype(str).tolist() + ["Other.."] #Ashit: the column name in the df (self.HeatingEqpOptions) has changed from HSPF to HeatingEff
            if self.CoolingEff.currentText() in SEERItems:
                CoolingEffIndex = SEERItems.index(self.CoolingEff.currentText())
                self.HeatingEff.setCurrentText(HSPFItems[CoolingEffIndex])
            

    def SetCoolingEff(self,text):
        self.df_input.loc[self.df_input.PropKey=="CoolingEff","PropValue"] = text
    
    def SetCoolingEffCustom(self,text):
        self.df_input.loc[self.df_input.PropKey=="CoolingEffCustom","PropValue"] = text

    def SetHeatingEqp(self,text):
        self.df_input.loc[self.df_input.PropKey=="HeatingEquipment","PropValue"] = text
    
    def SetHeatingEffOptions(self):
        if "No" not in self.HeatingEqp.currentText():
            self.HeatingEqpOptions = pd.read_csv(os.path.join(self.ProjectPath, "CostData","System-"+self.HeatingEqp.currentText().replace(" ","")+".csv"))
            #print(self.HeatingEqpOptions)
            HeatingEffOptions = self.HeatingEqpOptions["HeatingEff"].astype(str).tolist() + ["Other.."]
        else:
            HeatingEffOptions = ["None"]
        
        if "Air Source Heat Pump" in self.HeatingEqp.currentText():
            self.CoolingEqp.setCurrentText(self.HeatingEqp.currentText())
        
        self.HeatingEff.clear()
        self.HeatingEff.addItems(HeatingEffOptions)

    def SetHeatingEffChanged(self):
        # If "Other..." is selected, make combobox editable
        if self.HeatingEff.currentText() == "Other..":
            self.HeatingEffCustom.setEnabled(True)
        
        if "Air Source Heat Pump" in self.CoolingEqp.currentText() and "Air Source Heat Pump" in self.HeatingEqp.currentText():
            self.GetHeatingSystemOptions(self.HeatingEqp.currentText().replace(" ",""))
            SEERItems = self.HeatingEqpOptions["SEER"].astype(str).tolist() + ["Other.."]
            HSPFItems = self.HeatingEqpOptions["HeatingEff"].astype(str).tolist() + ["Other.."] #Ashit: the column name in the df (self.HeatingEqpOptions) has changed from HSPF to HeatingEff
            if self.HeatingEff.currentText() in HSPFItems:
                HeatingEffIndex = HSPFItems.index(self.HeatingEff.currentText())
                self.CoolingEff.setCurrentText(SEERItems[HeatingEffIndex])

    def SetHeatingEff(self,text):
        self.df_input.loc[self.df_input.PropKey=="HeatingEff","PropValue"] = text
    
    def SetHeatingEffCustom(self,text):
        self.df_input.loc[self.df_input.PropKey=="HeatingEffCustom","PropValue"] = text
    
    def SetEconomizer(self,text):
        self.df_input.loc[self.df_input.PropKey=="Economizer","PropValue"] = text    
    
    def SetSwampCooler(self,text):
        self.df_input.loc[self.df_input.PropKey=="SwampCooler","PropValue"] = text   
    
    def SetTsph(self,text):
        self.df_input.loc[self.df_input.PropKey=="Tsph","PropValue"] = float(text)
    
    def SetTspc(self,text):
        self.df_input.loc[self.df_input.PropKey=="Tspc","PropValue"] = float(text)

    #Inputing the Night Setback Value from GUI to df_input 
    def SetNightSetback(self,text):
        self.df_input.loc[self.df_input.PropKey=="NightSetback","PropValue"] = float(text)      

    def SetNightSetbackHours(self,text):
        self.df_input.loc[self.df_input.PropKey=="nNightSetbackHours","PropValue"] = float(text)        
    
    def SetCoolingSetback(self,text):
        self.df_input.loc[self.df_input.PropKey=="CoolingSetback","PropValue"] = float(text)   

    def SetDHWSystemType(self,text):
        self.df_input.loc[self.df_input.PropKey=="DHWSystemType","PropValue"] = text
    
    def SetDHWTankVol(self,text):
        self.df_input.loc[self.df_input.PropKey=="DHWTankVol","PropValue"] = float(text)
    
    def SetCookingFuelType(self,text):
        self.df_input.loc[self.df_input.PropKey=="CookingFuelType","PropValue"] = text
    
    def SetCookingRating(self,text):
        self.df_input.loc[self.df_input.PropKey=="CookingRangeRating","PropValue"] = float(text)
    
    def SetFridgeRating(self,text):
        self.df_input.loc[self.df_input.PropKey=="FridgeRating","PropValue"] = float(text)
    
    def SetDishWasherRating(self,text):
        self.df_input.loc[self.df_input.PropKey=="DishwasherRating","PropValue"] = float(text)
    
    def SetWasherRating(self,text):
        self.df_input.loc[self.df_input.PropKey=="WasherRating","PropValue"] = float(text)
    
    def SetDryerRating(self,text):
        self.df_input.loc[self.df_input.PropKey=="DryerRating","PropValue"] = float(text)
    
    def SetTVRating(self,text):
        self.df_input.loc[self.df_input.PropKey=="MiscTVRating","PropValue"] = float(text)
    
    def SetOfficeEqpRating(self,text):
        self.df_input.loc[self.df_input.PropKey=="OfficeEqpRating","PropValue"] = float(text)
    
    def SetMiscPlugLoadRating(self,text):
        self.df_input.loc[self.df_input.PropKey=="MiscPlugLoadRating","PropValue"] = float(text)
    
    def SetLPD(self,text):
        self.df_input.loc[self.df_input.PropKey=="LPD","PropValue"] = float(text)
    
    def SetLightingHours(self,text):
        self.df_input.loc[self.df_input.PropKey=="nHoursLighting","PropValue"] = float(text)

    def SetDaylighting(self,text):
        self.df_input.loc[self.df_input.PropKey=="Daylighting","PropValue"] = text    
    
    def SetLEDCurrent(self,text):
        self.df_input.loc[self.df_input.PropKey=="LEDCurrent","PropValue"] = float(text)

    def SetLEDECM(self,text):
        self.df_input.loc[self.df_input.PropKey=="LEDECM","PropValue"] = float(text)    

    def SetOccupancySensor(self,text):
        self.df_input.loc[self.df_input.PropKey=="OccupancySensor","PropValue"] = text 

    def SetReduceEquipmentLoad(self,text):
        self.df_input.loc[self.df_input.PropKey=="EquipLoadRed","PropValue"] = float(text)  
#%% SET COST OPTIONS FOR ECMs

    def CopyCostData(self):
        os.makedirs(os.path.join(self.ProjectPath, "CostData"),exist_ok=True)
        for file in os.listdir(os.path.join(self.MainPath,"Measures")):
            if file.endswith(".csv"):
                shutil.copy(os.path.join(self.MainPath,"Measures",file),os.path.join(self.ProjectPath, "CostData",file))
        
        self.SetECMWallInsCostOptions()
        self.SetECMInfiltrationCostOptions()
        self.SetECMCeilingInsCostOptions()
        self.SetECMWindowMatCostOptions()
        self.SetECMNightSetbackCostOptions()
        self.SetECMHoursofNightSetbackCostOptions()
        self.SetECMDaylightingCostOptions()
        self.SetECMEconomizerCostOptions()
        self.SetECMOccSensorCostOptions()
        self.SetECMLEDLightingCostOptions()
        self.SetECMReduceEquipmentLoadCostOptions()
        # First add items and set default values 
        self.SetECMCoolingEffCostOptions()
        
        self.SetECMHeatingEqpCostOptions()
        self.SetECMHeatingEffCostOptions()

    def SetECMWallInsCostOptions(self):
        self.WallInsCostOptions = pd.read_csv(os.path.join(self.ProjectPath, "CostData","Materials-WallInsulation.csv"))
        WallInsFC = self.WallInsCostOptions.loc[self.WallInsCostOptions["InsulationName"] == self.ECMWallInsCostOptions.currentText()]["FixedCost"].astype(str).item()
        WallInsVC = self.WallInsCostOptions.loc[self.WallInsCostOptions["InsulationName"] == self.ECMWallInsCostOptions.currentText()]["Costpersft"].astype(str).item()

        self.EEMCostTable.setItem(0,2,QTableWidgetItem(WallInsFC))
        self.EEMCostTable.setItem(0,3,QTableWidgetItem(WallInsVC))

    
    def SetECMInfiltrationCostOptions(self):
        self.InfiltrationCostOptions = pd.read_csv(os.path.join(self.ProjectPath, "CostData","Infiltration.csv"))
        InfiltrationFC = self.InfiltrationCostOptions.loc[self.InfiltrationCostOptions["ACH50"].astype(str) == self.ECMInfilCostOptions.currentText()]["FixedCost"].astype(str).item()
        InfiltrationVC = self.InfiltrationCostOptions.loc[self.InfiltrationCostOptions["ACH50"].astype(str) == self.ECMInfilCostOptions.currentText()][["Costpersft", "CostperACHsft"]].sum(axis=1).iloc[0]

        self.EEMCostTable.setItem(1,2,QTableWidgetItem(InfiltrationFC))
        self.EEMCostTable.setItem(1,3,QTableWidgetItem(str(InfiltrationVC)))

    def SetECMCeilingInsCostOptions(self):
        self.CeilingInsCostOptions = pd.read_csv(os.path.join(self.ProjectPath, "CostData","Materials-CeilingInsulation.csv"))
        CeilingInsFC = self.CeilingInsCostOptions.loc[self.CeilingInsCostOptions["InsulationName"] == self.ECMCeilInsCostOptions.currentText()]["FixedCost"].astype(str).item()
        CeilingInsVC = self.CeilingInsCostOptions.loc[self.CeilingInsCostOptions["InsulationName"] == self.ECMCeilInsCostOptions.currentText()]["Costpersft"].astype(str).item()

        self.EEMCostTable.setItem(2,2,QTableWidgetItem(CeilingInsFC))
        self.EEMCostTable.setItem(2,3,QTableWidgetItem(CeilingInsVC)) 

    def SetECMWindowMatCostOptions(self):
        self.WindowMatCostOptions = pd.read_csv(os.path.join(self.ProjectPath, "CostData","Materials-WindowMaterial.csv"))
        WindowMatFC = self.WindowMatCostOptions.loc[self.WindowMatCostOptions["WindowMaterial"] == self.ECMWindowMatCostOptions.currentText()]["FixedCost"].astype(str).item()
        WindowMatVC = self.WindowMatCostOptions.loc[self.WindowMatCostOptions["WindowMaterial"] == self.ECMWindowMatCostOptions.currentText()]["Costpersft"].astype(str).item()

        self.EEMCostTable.setItem(3,2,QTableWidgetItem(WindowMatFC))
        self.EEMCostTable.setItem(3,3,QTableWidgetItem(WindowMatVC))

    def SetECMNightSetbackCostOptions(self):
        self.EEMCostTable.setItem(4,2,QTableWidgetItem(0))
        self.EEMCostTable.setItem(4,3,QTableWidgetItem(0))

    def SetECMHoursofNightSetbackCostOptions(self):
        self.EEMCostTable.setItem(5,2,QTableWidgetItem(0))
        self.EEMCostTable.setItem(5,3,QTableWidgetItem(0)) 

    def SetECMDaylightingCostOptions(self):
        self.DaylightingCostOptions = pd.read_csv(os.path.join(self.ProjectPath, "CostData","Equipment-Daylighting.csv"))
        DaylightingFC = self.DaylightingCostOptions.loc[self.DaylightingCostOptions["Daylighting"] == self.ECMDaylightingCostOptions.currentText()]["FixedCost"].astype(str).item()
        DaylightingVC = self.DaylightingCostOptions.loc[self.DaylightingCostOptions["Daylighting"] == self.ECMDaylightingCostOptions.currentText()]["Costpersft"].astype(str).item()

        self.EEMCostTable.setItem(6,2,QTableWidgetItem(DaylightingFC))
        self.EEMCostTable.setItem(6,3,QTableWidgetItem(DaylightingVC))

    def SetECMEconomizerCostOptions(self):
        self.EconomizerCostOptions = pd.read_csv(os.path.join(self.ProjectPath, "CostData","System-Economizer.csv"))
        EconomizerFC = self.EconomizerCostOptions.loc[self.EconomizerCostOptions["Economizer"] == self.ECMEconCostOptions.currentText()]["FixedCost"].astype(str).item()
        EconomizerVC = self.EconomizerCostOptions.loc[self.EconomizerCostOptions["Economizer"] == self.ECMEconCostOptions.currentText()]["Costpersft"].astype(str).item()

        self.EEMCostTable.setItem(7,2,QTableWidgetItem(EconomizerFC))
        self.EEMCostTable.setItem(7,3,QTableWidgetItem(EconomizerVC))
    
    def SetECMOccSensorCostOptions(self):
        self.OccupancySensorCostOptions = pd.read_csv(os.path.join(self.ProjectPath, "CostData","Equipment-OccupancySensor.csv"))
        OccupancySensorFC = self.OccupancySensorCostOptions.loc[self.OccupancySensorCostOptions["OccupancySensor"] == self.ECMOccSensorCostOptions.currentText()]["FixedCost"].astype(str).item()
        OccupancySensorVC = self.OccupancySensorCostOptions.loc[self.OccupancySensorCostOptions["OccupancySensor"] == self.ECMOccSensorCostOptions.currentText()]["Costpersft"].astype(str).item()

        self.EEMCostTable.setItem(8,2,QTableWidgetItem(OccupancySensorFC))
        self.EEMCostTable.setItem(8,3,QTableWidgetItem(OccupancySensorVC))
    
    def SetECMLEDLightingCostOptions(self):
        self.LEDCostOptions = pd.read_csv(os.path.join(self.ProjectPath, "CostData","Equipment-LED.csv"))
        LEDFC = self.LEDCostOptions.loc[self.LEDCostOptions["PercentageLED"].astype(float) == float(self.ECMLEDCostOptions.currentText())]["FixedCost"].astype(str).item()
        LEDVC = self.LEDCostOptions.loc[self.LEDCostOptions["PercentageLED"].astype(float) == float(self.ECMLEDCostOptions.currentText())]["Costpersft"].astype(str).item()

        self.EEMCostTable.setItem(9,2,QTableWidgetItem(LEDFC))
        self.EEMCostTable.setItem(9,3,QTableWidgetItem(LEDVC))

    def SetECMReduceEquipmentLoadCostOptions(self):
        self.EEMCostTable.setItem(10,2,QTableWidgetItem(0))
        self.EEMCostTable.setItem(10,3,QTableWidgetItem(0))

    def SetECMCoolingEffCostOptions(self):
        if "No" not in self.CoolingEqp.currentText():
            # print(self.Cool◙ingEqp.currentText())
            self.CoolingEffCostOptions = pd.read_csv(os.path.join(self.ProjectPath, "CostData","System-"+self.CoolingEqp.currentText().replace(" ","")+".csv"))
            # print(self.CoolingEffCostOptions)
            # print(self.CoolingEffCostOptions["SEER"].astype(str).tolist())
            self.ECMCoolingEffCostOptions.addItems(self.CoolingEffCostOptions["SEER"].astype(str).tolist())
            
            # print(self.ECMCoolingEffCostOptions.currentText())
            CoolingEffFC = self.CoolingEffCostOptions.loc[self.CoolingEffCostOptions["SEER"].astype(float) == float(self.ECMCoolingEffCostOptions.currentText())]["Costperunit"].astype(str).item()
            CoolingEffVC = self.CoolingEffCostOptions.loc[self.CoolingEffCostOptions["SEER"].astype(float) == float(self.ECMCoolingEffCostOptions.currentText())]["CostperkBtuh"].astype(str).item()

            self.EEMCostTable.setItem(11,2,QTableWidgetItem(CoolingEffFC))
            self.EEMCostTable.setItem(11,3,QTableWidgetItem(CoolingEffVC))
        else:
            self.CoolingEffCostOptions = pd.read_csv(os.path.join(self.ProjectPath, "CostData","System-"+self.CoolingEqp.currentText().replace(" ","")+".csv"))
            self.ECMCoolingEffCostOptions.addItems(self.CoolingEffCostOptions["SEER"].astype(str).tolist())

            CoolingEffFC = self.CoolingEffCostOptions.loc[self.CoolingEffCostOptions["SEER"].astype(float) == float(self.ECMCoolingEffCostOptions.currentText())]["Costperunit"].astype(str).item()
            CoolingEffVC = self.CoolingEffCostOptions.loc[self.CoolingEffCostOptions["SEER"].astype(float) == float(self.ECMCoolingEffCostOptions.currentText())]["CostperkBtuh"].astype(str).item()

            self.EEMCostTable.setItem(11,2,QTableWidgetItem(CoolingEffFC))
            self.EEMCostTable.setItem(11,3,QTableWidgetItem(CoolingEffVC)) 

    def SetECMHeatingEffCostOptions(self):
        if "No" not in self.HeatingEqp.currentText():
            # self.GetHeatingSystemOptions(self.ECMHeatingEqpCostOptions.currentText().replace(" ",""))
            
            HeatingEffFC = self.HeatingEqpOptionsTable.loc[self.HeatingEqpOptionsTable["HeatingEff"].astype(float) == float(self.ECMHeatingEffCostOptions.currentText())]["Costperunit"].astype(str).item()
            HeatingEffVC = self.HeatingEqpOptionsTable.loc[self.HeatingEqpOptionsTable["HeatingEff"].astype(float) == float(self.ECMHeatingEffCostOptions.currentText())]["CostperkBtuh"].astype(str).item()

            self.EEMCostTable.setItem(13,2,QTableWidgetItem(HeatingEffFC))
            self.EEMCostTable.setItem(13,3,QTableWidgetItem(HeatingEffVC))
    
    def SetECMHeatingEqpCostOptions(self):
        self.GetHeatingSystemOptions(self.ECMHeatingEqpCostOptions.currentText().replace(" ",""))
        # 
        self.ECMHeatingEffCostOptions.blockSignals(True)
        self.ECMHeatingEffCostOptions.clear()
        self.ECMHeatingEffCostOptions.addItems(self.HeatingEqpOptionsTable["HeatingEff"].astype(str).tolist())
        self.SetECMHeatingEffCostOptions()
        self.ECMHeatingEffCostOptions.blockSignals(False)

        
    def SetSetCostData(self):
        self.CostData = {}
        self.CostData["kWhRate"] = float(self.kWhCost.text())
        self.CostData["ThermRate"] = float(self.ThermCost.text())
        self.CostData["DiscountRate"] = float(self.DiscountRate.text())
        self.CostData["Lifetime"] = float(self.Lifetime.text())
        self.CostData["USPW"] = (1-(1+((self.CostData["DiscountRate"])/100))**(-(self.CostData["Lifetime"])))/((self.CostData["DiscountRate"])/100)

        pd.DataFrame([self.CostData]).to_csv(os.path.join(self.ProjectPath,"CostData","BasicCostData.csv"),index=False)

        self.WallInsCostOptions.loc[self.WallInsCostOptions["InsulationName"] == self.ECMWallInsCostOptions.currentText(),"FixedCost"] = self.EEMCostTable.item(0,2).text()
        self.WallInsCostOptions.loc[self.WallInsCostOptions["InsulationName"] == self.ECMWallInsCostOptions.currentText(),"Costpersft"] = self.EEMCostTable.item(0,3).text()
        self.InfiltrationCostOptions.loc[self.InfiltrationCostOptions["ACH50"] == self.ECMInfilCostOptions.currentText(),"FixedCost"] = self.EEMCostTable.item(1,2).text()
        self.InfiltrationCostOptions.loc[self.InfiltrationCostOptions["ACH50"] == self.ECMInfilCostOptions.currentText(),"Costpersft"] = self.EEMCostTable.item(1,3).text()
        self.CeilingInsCostOptions.loc[self.CeilingInsCostOptions["InsulationName"] == self.ECMCeilInsCostOptions.currentText(),"FixedCost"] = self.EEMCostTable.item(2,2).text()
        self.CeilingInsCostOptions.loc[self.CeilingInsCostOptions["InsulationName"] == self.ECMCeilInsCostOptions.currentText(),"Costpersft"] = self.EEMCostTable.item(2,3).text()
        self.WindowMatCostOptions.loc[self.WindowMatCostOptions["WindowMaterial"] == self.ECMWindowMatCostOptions.currentText(),"FixedCost"] = self.EEMCostTable.item(3,2).text()
        self.WindowMatCostOptions.loc[self.WindowMatCostOptions["WindowMaterial"] == self.ECMWindowMatCostOptions.currentText(),"Costpersft"] = self.EEMCostTable.item(3,3).text()
        self.DaylightingCostOptions.loc[self.DaylightingCostOptions["Daylighting"] == self.ECMDaylightingCostOptions.currentText(),"FixedCost"] = self.EEMCostTable.item(5,2).text()
        self.DaylightingCostOptions.loc[self.DaylightingCostOptions["Daylighting"] == self.ECMDaylightingCostOptions.currentText(),"Costpersft"] = self.EEMCostTable.item(5,3).text()
        self.EconomizerCostOptions.loc[self.EconomizerCostOptions["Economizer"] == self.ECMEconCostOptions.currentText(),"FixedCost"] = self.EEMCostTable.item(6,2).text()
        self.EconomizerCostOptions.loc[self.EconomizerCostOptions["Economizer"] == self.ECMEconCostOptions.currentText(),"Costpersft"] = self.EEMCostTable.item(6,3).text()
        self.OccupancySensorCostOptions.loc[self.OccupancySensorCostOptions["OccupancySensor"] == self.ECMOccSensorCostOptions.currentText(),"FixedCost"] = self.EEMCostTable.item(7,2).text()
        self.OccupancySensorCostOptions.loc[self.OccupancySensorCostOptions["OccupancySensor"] == self.ECMOccSensorCostOptions.currentText(),"Costpersft"] = self.EEMCostTable.item(7,3).text()
        self.LEDCostOptions.loc[self.LEDCostOptions["PercentageLED"] == self.ECMLEDCostOptions.currentText(),"FixedCost"] = self.EEMCostTable.item(8,2).text()
        self.LEDCostOptions.loc[self.LEDCostOptions["PercentageLED"] == self.ECMLEDCostOptions.currentText(),"Costpersft"] = self.EEMCostTable.item(8,3).text()
        self.CoolingEffCostOptions.loc[self.CoolingEffCostOptions["SEER"] == self.ECMCoolingEffCostOptions.currentText(),"Costperunit"] = self.EEMCostTable.item(11,2).text()
        self.CoolingEffCostOptions.loc[self.CoolingEffCostOptions["SEER"] == self.ECMCoolingEffCostOptions.currentText(),"CostperkBtuh"] = self.EEMCostTable.item(11,3).text()
        self.GetHeatingSystemOptions(self.ECMHeatingEqpCostOptions.currentText().replace(" ",""))
        self.HeatingEqpOptionsTable.loc[self.HeatingEqpOptionsTable["HeatingEff"] == self.ECMHeatingEffCostOptions.currentText(),"Costperunit"] = self.EEMCostTable.item(13,2).text()
        self.HeatingEqpOptionsTable.loc[self.HeatingEqpOptionsTable["HeatingEff"] == self.ECMHeatingEffCostOptions.currentText(),"CostperkBtuh"] = self.EEMCostTable.item(13,3).text()
        
        self.WallInsCostOptions.to_csv(os.path.join(self.ProjectPath, "CostData","Materials-WallInsulation.csv"),index=False)
        self.InfiltrationCostOptions.to_csv(os.path.join(self.ProjectPath, "CostData","Infiltration.csv"),index=False)
        self.CeilingInsCostOptions.to_csv(os.path.join(self.ProjectPath, "CostData","Materials-CeilingInsulation.csv"),index=False)
        self.WindowMatCostOptions.to_csv(os.path.join(self.ProjectPath, "CostData","Materials-WindowMaterial.csv"),index=False)
        self.DaylightingCostOptions.to_csv(os.path.join(self.ProjectPath, "CostData","Equipment-Daylighting.csv"),index=False)
        self.EconomizerCostOptions.to_csv(os.path.join(self.ProjectPath, "CostData","System-Economizer.csv"),index=False)
        self.OccupancySensorCostOptions.to_csv(os.path.join(self.ProjectPath, "CostData","Equipment-OccupancySensor.csv"),index=False)
        self.LEDCostOptions.to_csv(os.path.join(self.ProjectPath, "CostData","Equipment-LEDLighting.csv"),index=False)
        self.CoolingEffCostOptions.to_csv(os.path.join(self.ProjectPath, "CostData","System-"+self.CoolingEqp.currentText().replace(" ","")+".csv"),index=False)
        self.HeatingEqpOptionsTable.to_csv(os.path.join(self.ProjectPath, "CostData","System-"+self.ECMHeatingEqpCostOptions.currentText().replace(" ","")+".csv"),index=False)
        

        self.SetECMBaseProperty()

    def SetResetCostData(self):
        self.CopyCostData()

    def GetHeatingSystemOptions(self,HeatingEqp):
        self.HeatingEqpOptionsTable = pd.read_csv(os.path.join(self.ProjectPath,"CostData","System-"+HeatingEqp+".csv"))

   
    def ShowECMTableResults(self,ECMTabIndex,EEMResults):
        # self.GetECMBaseline()
        # Calculate the percentage change in electricity and natural gas consumption with respect to the specified baseline
        
        
        # ECM Evaluation table
        i = ECMTabIndex
        self.ECMEval.setItem(i,3,QTableWidgetItem(str(round(EEMResults["PctkWhSavings"],2))+"%"))
        self.ECMEval.setItem(i,4,QTableWidgetItem(str(round(EEMResults["PctThermSavings"],2))+"%"))
        self.ECMEval.setItem(i,5,QTableWidgetItem(str(round(EEMResults["TIC"]))))
        self.ECMEval.setItem(i,6,QTableWidgetItem(str(round(EEMResults["EEMLCC"]))))
    
    
    def SetECMBaseProperty(self):

        self.Measures = {}
        

        for i in range(0,9):
            for j in range(3,7):
                self.ECMEval.setItem(i,j,QTableWidgetItem(""))

        self.BestModelParams["AnnualOperatingCost"] = self.BestModelParams["OrgTotalElectricity"]*float(self.kWhCost.text()) + self.BestModelParams["OrgTotalNaturalGas"]*float(self.ThermCost.text())
        self.BestModelParams["TOC"] = self.BestModelParams["AnnualOperatingCost"]*self.CostData["USPW"]
        
        self.ECMBaselineMetrics.setItem(0,0,QTableWidgetItem(str(round(self.BestModelParams["OrgTotalElectricity"]))))
        self.ECMBaselineMetrics.setItem(0,1,QTableWidgetItem(str(round(self.BestModelParams["OrgTotalNaturalGas"]))))
        self.ECMBaselineMetrics.setItem(0,2,QTableWidgetItem(str(round(self.BestModelParams["AnnualOperatingCost"]))))
        self.ECMBaselineMetrics.setItem(0,3,QTableWidgetItem(str(round(self.BestModelParams["TOC"]))))

        self.ECMWallInsOptions.setCurrentText(self.WallInsulation.currentText())
        self.ECMInfilOptions.setCurrentText(self.ACH50.currentText())
        self.ECMCeilInsOptions.setCurrentText(self.CeilingInsulation.currentText())
        self.ECMWindowMatOptions.setCurrentText(self.WindowMaterial.currentItem().text())
        self.ECMNightSetbackOptions.setCurrentText(self.NightSetback.currentText())
        self.ECMHoursofNightSetbackOptions.setText(self.nNightSetbackHours.text())
        self.ECMDaylightingOptions.setCurrentText(self.Daylighting.currentText())
        self.ECMEconOptions.setCurrentText(self.Economizer.currentText())
        self.ECMLEDOptions.setCurrentText(self.LED.currentText())
        self.ECMOccSensorOptions.setCurrentText(self.df_input.loc[self.df_input["PropKey"] == "OccupancySensor","PropValue"].item())
        self.ECMReduceEquipmentLoadOptions.setCurrentText(self.df_input.loc[self.df_input["PropKey"] == "EquipLoadRed","PropValue"].item())
        if "No" not in self.CoolingEqp.currentText():
            self.ECMCoolingEffOptions.addItems(self.CoolingEffCostOptions["SEER"].astype(str).tolist())
            self.ECMCoolingEffOptions.setCurrentText(self.CoolingEff.currentText())
        self.ECMHeatingEqpOptions.setCurrentText(self.HeatingEqp.currentText())
        if "Gas" in self.ECMHeatingEqpOptions.currentText():
            self.GetHeatingSystemOptions(self.ECMHeatingEqpOptions.currentText().replace(" ",""))
            self.ECMHeatingEffOptions.addItems(self.HeatingEqpOptionsTable["HeatingEff"].astype(str).tolist())
            if self.HeatingEqp.currentText() == self.ECMHeatingEqpOptions.currentText():
                self.ECMHeatingEffOptions.setCurrentText(self.HeatingEff.currentText())
                


        self.ECMEval.setItem(0,1,QTableWidgetItem(self.WallInsulation.currentText()))
        self.ECMEval.setItem(1,1,QTableWidgetItem(self.ACH50.currentText()))
        self.ECMEval.setItem(2,1,QTableWidgetItem(self.CeilingInsulation.currentText()))
        self.ECMEval.setItem(3,1,QTableWidgetItem(self.WindowMaterial.currentItem().text()))
        self.ECMEval.setItem(4,1,QTableWidgetItem(self.NightSetback.currentText()))
        self.ECMEval.setItem(5,1,QTableWidgetItem(self.nNightSetbackHours.text()))
        self.ECMEval.setItem(6,1,QTableWidgetItem(self.Daylighting.currentText()))
        self.ECMEval.setItem(7,1,QTableWidgetItem(self.Economizer.currentText()))
        self.ECMEval.setItem(8,1,QTableWidgetItem(self.df_input.loc[self.df_input["PropKey"] == "OccupancySensor","PropValue"].item()))
        self.ECMEval.setItem(9,1,QTableWidgetItem(self.LED.currentText()))
        self.ECMEval.setItem(10,1,QTableWidgetItem(self.df_input.loc[self.df_input["PropKey"] == "EquipLoadRed","PropValue"].item()))
        self.ECMEval.setItem(11,1,QTableWidgetItem(self.CoolingEff.currentText()))
        self.ECMEval.setItem(12,1,QTableWidgetItem(self.HeatingEqp.currentText()))
        self.ECMEval.setItem(13,1,QTableWidgetItem(self.HeatingEff.currentText()))
        

        self.Measures["WallInsChange"] = False
        self.Measures["CeilInsChange"] = False
        self.Measures["InfilChange"] = False
        self.Measures["WindowMatChange"] = False
        self.Measures["NightSetbackChange"] = False
        self.Measures["HoursofNightSetbackChange"] = False
        self.Measures["DaylightingChange"] = False
        self.Measures["EconomizerChange"] = False
        self.Measures["OccupancySensorChange"] = False
        self.Measures["LEDChange"] = False
        self.Measures["ReduceEquipmentLoadChange"] = False
        self.Measures["CoolingEffChange"] = False
        self.Measures["HeatingEffChange"] = False
        self.Measures["HeatingEqpChange"] = False

        # Declare an empty df to store all results for every ECM
        self.dfIndECMResults = pd.DataFrame()
        self.npackages = 0

    def SetWallInsChange(self):
        self.Measures["WallInsChange"] = True
        self.SetWallInsulation(self.ECMWallInsOptions.currentText())
    
    def SetInfilChange(self):
        self.Measures["InfilChange"] = True
        self.SetInfiltration(self.ECMInfilOptions.currentText())

    def SetCeilInsChange(self):
        self.Measures["CeilInsChange"] = True
        self.SetCeilingInsulation(self.ECMCeilInsOptions.currentText())

    def SetWindowMatChange(self):
        self.Measures["WindowMatChange"] = True
        self.SetWindowMaterial(self.ECMWindowMatOptions.currentText())

    def SetNightSetbackChange(self):
        self.Measures["NightSetbackChange"] = True
        self.SetNightSetback(self.ECMNightSetbackOptions.currentText())

    def SetHoursofNightSetbackChange(self):
        self.Measures["HoursofNightSetbackChange"] = True
        self.SetNightSetbackHours(self.ECMHoursofNightSetbackOptions.text())

    def SetDaylightingChange(self):
        self.Measures["DaylightingChange"] = True
        self.SetDaylighting(self.ECMDaylightingOptions.currentText()) 

    def SetEconomizerChange(self):
        self.Measures["EconomizerChange"] = True
        self.SetEconomizer(self.ECMEconOptions.currentText())

    def SetOccupancySensorChange(self):
        self.Measures["OccupancySensorChange"] = True
        self.SetOccupancySensor(self.ECMOccSensorOptions.currentText())

    def SetLEDChange(self):
        self.Measures["LEDChange"] = True
        self.SetLEDECM(self.ECMLEDOptions.currentText())    

    def SetReduceEquipmentLoadChange(self):
        self.Measures["ReduceEquipmentLoadChange"] = True
        self.SetReduceEquipmentLoad(self.ECMReduceEquipmentLoadOptions.currentText())  

    def SetCoolingEffChange(self):
        self.Measures["CoolingEffChange"] = True
        self.SetCoolingEff(self.ECMCoolingEffOptions.currentText())   

    def SetHeatingEffChange(self):
        self.Measures["HeatingEffChange"] = True
        self.SetHeatingEff(self.ECMHeatingEffOptions.currentText())                        
    
    def SetHeatingEqpChange(self):
        self.Measures["HeatingEqpChange"] = True
        self.SetHeatingEqp(self.ECMHeatingEqpOptions.currentText())
        self.GetHeatingSystemOptions(self.ECMHeatingEqpOptions.currentText().replace(" ",""))
        self.ECMHeatingEffOptions.blockSignals(True)
        self.ECMHeatingEffOptions.clear()
        self.ECMHeatingEffOptions.addItems(self.HeatingEqpOptionsTable["HeatingEff"].astype(str).tolist())
        self.ECMHeatingEffOptions.blockSignals(False)

        
    #%%
    def SetEvaluateIndMeasure(self):
        self.df_input.to_pickle(os.path.join(self.ProjectPath,"BldgPropInputsFile.pkl"))

        IndEEMResults = MeasurePackageAnalysis(self.Measures,self.df_MonthlyEndUse,self.BestModelParams,self.CostData,self.MainPath,self.ProjectPath,self.df_weather)
        
        IndEEMResults["OperatingCostChange"] = IndEEMResults["OrgAOC"] - IndEEMResults["EEMAOC"]
        if IndEEMResults["OperatingCostChange"] == 0:
            IndEEMResults["SPP"] = "NA"
        else:
            IndEEMResults["SPP"] = IndEEMResults["TIC"]/IndEEMResults["OperatingCostChange"]
        IndEEMResults["NPV"] = -IndEEMResults["TIC"]  + IndEEMResults["OrgTOC"] - IndEEMResults["EEMTOC"] # difference in annual operating cost times the USPW minus the total inital cost of the project
        if IndEEMResults["TIC"] == 0:
            IndEEMResults["ROI"] = 0
        else:
            IndEEMResults["ROI"] = 100*(IndEEMResults["OrgTOC"] - IndEEMResults["EEMTOC"] - IndEEMResults["TIC"])/IndEEMResults["TIC"]

        self.dfIndECMResults = pd.concat([self.dfIndECMResults,pd.DataFrame([IndEEMResults])],axis=0)


        if self.Measures["WallInsChange"]:

            self.ShowECMTableResults(0,IndEEMResults)
        
        if self.Measures["InfilChange"]:
            self.ShowECMTableResults(1,IndEEMResults)
        
        if self.Measures["CeilInsChange"]:
            self.ShowECMTableResults(2,IndEEMResults)
        
        if self.Measures["WindowMatChange"]:
            self.ShowECMTableResults(3,IndEEMResults)
        
        if self.Measures["NightSetbackChange"]:
            self.ShowECMTableResults(4,IndEEMResults)

        if self.Measures["HoursofNightSetbackChange"]:
            self.ShowECMTableResults(5,IndEEMResults)
        
        if self.Measures["DaylightingChange"]:
            self.ShowECMTableResults(6,IndEEMResults)
        
        if self.Measures["EconomizerChange"]:
            self.ShowECMTableResults(7,IndEEMResults)
        
        if self.Measures["OccupancySensorChange"]:
            self.ShowECMTableResults(8,IndEEMResults)
        
        if self.Measures["LEDChange"]:
            self.ShowECMTableResults(9,IndEEMResults)

        if self.Measures["ReduceEquipmentLoadChange"]:
            self.ShowECMTableResults(10,IndEEMResults)    

        if self.Measures["CoolingEffChange"]:
            self.ShowECMTableResults(11,IndEEMResults)   

        if self.Measures["HeatingEffChange"]:
            self.ShowECMTableResults(13,IndEEMResults)        

        # if self.Measures["HeatingEqpChange"]:
        #     self.ShowECMTableResults(12,IndEEMResults)

        for i in self.Measures.keys():
            self.Measures[i] = False
        
        self.df_input = pd.read_pickle(os.path.join(self.ProjectPath,"BldgPropInputFile-Baseline.pkl"))
        self.ShowEEMResults()

    def SetEvaluateMeasurePackage(self):
        self.npackages += 1
        
        if self.df_input.loc[self.df_input["PropKey"] == "R-WallInsulation","PropValue"].item() != self.ECMWallInsOptions.currentText():
            self.SetWallInsChange()

        if self.df_input.loc[self.df_input["PropKey"] == "ACH50","PropValue"].astype(float).iloc[0] != float(self.ECMInfilOptions.currentText()):
            self.SetInfilChange()

        if self.df_input.loc[self.df_input["PropKey"] == "R-CeilingInsulation","PropValue"].item() != self.ECMCeilInsOptions.currentText():
            self.SetCeilInsChange()

        if self.df_input.loc[self.df_input["PropKey"] == "WindowMaterial","PropValue"].item() != self.ECMWindowMatOptions.currentText():
            self.SetWindowMatChange()
        
        #print(self.nNightSetbackHours.text())
        #print(self.ECMHoursofNightSetbackOptions.text())
        if float(self.NightSetback.currentText()) != float(self.ECMNightSetbackOptions.currentText()):
            self.SetNightSetbackChange()

        if float(self.nNightSetbackHours.text()) != float(self.ECMHoursofNightSetbackOptions.text()):
            self.SetHoursofNightSetbackChange()    

        if self.df_input.loc[self.df_input["PropKey"] == "Daylighting","PropValue"].item() != self.ECMDaylightingOptions.currentText():
            self.SetDaylightingChange()   
        
        if self.df_input.loc[self.df_input["PropKey"] == "Economizer","PropValue"].item() != self.ECMEconOptions.currentText():
            self.SetEconomizerChange()

        if self.df_input.loc[self.df_input["PropKey"] == "OccupancySensor","PropValue"].item() != self.ECMOccSensorOptions.currentText():
            self.SetOccupancySensorChange() 

        if (self.df_input.loc[self.df_input["PropKey"] == "LEDCurrent","PropValue"].item() != self.ECMLEDOptions.currentText()) and (self.df_input.loc[self.df_input["PropKey"] == "LEDCurrent","PropValue"].item() < float(self.ECMLED.currentText())):
            self.SetLEDChange()  

        if self.df_input.loc[self.df_input["PropKey"] == "EquipLoadRed","PropValue"].astype(float).iloc[0] != float(self.ECMReduceEquipmentLoadOptions.currentText()):
            self.SetReduceEquipmentLoadChange()  

        # if self.df_input.loc[self.df_input["PropKey"] == "CoolingEff","PropValue"].item() != self.ECMCoolingEffOptions.currentText():
        #     self.SetCoolingEffChange()   

        # if self.df_input.loc[self.df_input["PropKey"] == "HeatingEff","PropValue"].item() != self.ECMHeatingEffOptions.currentText():
        #     self.SetHeatingEffChange()                                   
        # if (self.df_input.loc[self.df_input["PropKey"] == "LEDCurrent","PropValue"].item() != self.ECMLEDOptions.currentText()) and (self.df_input.loc[self.df_input["PropKey"] == "LEDCurrent","PropValue"].astype(float).iloc[0] < float(self.ECMLED.currentText())):
        #     self.SetLEDChange()                          

        self.df_input.to_pickle(os.path.join(self.ProjectPath,"BldgPropInputsFile.pkl"))
        self.runkey = "EvaluateMeasurePackage" + str(self.npackages)
        
        PackageEEMResults = MeasurePackageAnalysis(self.Measures,self.df_MonthlyEndUse,self.BestModelParams,self.CostData,self.MainPath,self.ProjectPath,self.df_weather)
        #print(PackageEEMResults)
        PackageEEMResults["OperatingCostChange"] = PackageEEMResults["OrgAOC"] - PackageEEMResults["EEMAOC"]
        if PackageEEMResults["OperatingCostChange"] == 0:
            PackageEEMResults["SPP"] = "NA"
        else:
            PackageEEMResults["SPP"] = PackageEEMResults["TIC"]/PackageEEMResults["OperatingCostChange"]
        PackageEEMResults["NPV"] = -PackageEEMResults["TIC"]  + PackageEEMResults["OrgTOC"] - PackageEEMResults["EEMTOC"] # difference in annual operating cost times the USPW minus the total inital cost of the project
        if PackageEEMResults["TIC"] == 0:
            PackageEEMResults["ROI"] = 0
        else:
            PackageEEMResults["ROI"] = 100*(PackageEEMResults["OrgTOC"] - PackageEEMResults["EEMTOC"] - PackageEEMResults["TIC"])/PackageEEMResults["TIC"]

        self.dfECMPackageResults = pd.DataFrame([PackageEEMResults])
        self.runkey = "EvaluateMeasurePackage" + str(self.npackages)

        self.PackagekWhPctChange.setText(str(round(PackageEEMResults["PctkWhSavings"],2))+"%")
        self.PackageThermsPctChange.setText(str(round(PackageEEMResults["PctThermSavings"],2))+"%")
        self.PackageTIC.setText(str(round(PackageEEMResults["TIC"])))
        self.PackageLCC.setText(str(round(PackageEEMResults["EEMLCC"])))

        for i in self.Measures.keys():
            self.Measures[i] = False
        self.df_input = pd.read_pickle(os.path.join(self.ProjectPath,"BldgPropInputFile-Baseline.pkl"))

        self.ShowEEMResults()


    def SetSaveIndECMResults(self):
        self.dfIndECMResults = self.dfIndECMResults.dropna(how="all")
        os.makedirs(os.path.join(self.ProjectPath,"Results","EvaluateMeasure"),exist_ok=True)
        self.dfIndECMResults.to_csv(os.path.join(self.ProjectPath,"Results","EvaluateMeasure","IndividualECMResults"+".csv"),index=False)
    
    
    def SetSaveECMPackageResults(self):
        self.dfECMPackageResults = self.dfECMPackageResults.dropna()
        os.makedirs(os.path.join(self.ProjectPath,"Results",self.runkey),exist_ok=True)
        self.dfECMPackageResults.to_csv(os.path.join(self.ProjectPath,"Results",self.runkey,"ECMPackageResults"+".csv"),index=False)

    def ShowEEMResults(self):
        self.scenekWhEEMCompPlot = QGraphicsScene(self)
        self.kWhEEMCompPlot.setScene(self.scenekWhEEMCompPlot)
        imagePath = os.path.join(self.ProjectPath,f"ElectricityMonthlyEEMComp.png")
        self.ShowGUIImage(self.scenekWhEEMCompPlot,self.kWhEEMCompPlot,imagePath)

        self.sceneThermEEMCompPlot = QGraphicsScene(self)
        self.ThermEEMCompPlot.setScene(self.sceneThermEEMCompPlot)
        imagePath = os.path.join(self.ProjectPath,f"NaturalGasMonthlyEEMComp.png")
        self.ShowGUIImage(self.sceneThermEEMCompPlot,self.ThermEEMCompPlot,imagePath)

class UtilityDataWindow(QWidget,Ui_Form):
    def __init__(self,ProjectPath,ProjectName):
        super().__init__()
        self.ProjectPath = ProjectPath
        self.ProjectName = ProjectName
        self.setupUi(self)
        self.SetUtilityData.clicked.connect(self.SetUtilityDataFile)


        CurrentYear = datetime.now().year
        self.Year1.addItems(np.arange(CurrentYear,CurrentYear-10,-1).astype(str))
        self.Year2.addItems(np.arange(CurrentYear,CurrentYear-10,-1).astype(str))
        self.Year3.addItems(np.arange(CurrentYear,CurrentYear-10,-1).astype(str))
    
    def SetUtilityDataFile(self):
        df = pd.DataFrame(index=range(1,13),columns=["Year 1 - kWh","Year 1 - Therms","Year 2 - kWh","Year 2 - Therms","Year 3 - kWh","Year 3 - Therms"])
        df["BillDays"] = [calendar.monthrange(int(self.Year1.currentText()), month)[1] for month in range(1, 13)]

        for row in range(12):
            for col in range(6):
                item = self.UtilityDataTable.item(row, col)
                if item:  
                    df.iloc[row, col] = item.text()
        
        df = df.rename(columns={"Year 1 - kWh":"Year 1 - kWh"+str(self.Year1.currentText()),"Year 1 - Therms":"Year 1 - Therms"+str(self.Year1.currentText())})
        df = df.rename(columns={"Year 2 - kWh":"Year 2 - kWh"+str(self.Year2.currentText()),"Year 2 - Therms":"Year 2 - Therms"+str(self.Year2.currentText())})
        df = df.rename(columns={"Year 3 - kWh":"Year 3 - kWh"+str(self.Year3.currentText()),"Year 3 - Therms":"Year 3 - Therms"+str(self.Year3.currentText())})

        df.to_csv(os.path.join(self.ProjectPath,self.ProjectName+"_UtilityData.csv"))
