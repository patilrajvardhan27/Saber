import sys
import pandas as pd
from .GUI_Code import Ui_MainWindow
from .GUI_UtilityDataWindowCode import Ui_Form
from .AnalyzeUtilityData import *
from .PostProcessing import *
from .RunSimulationCase import *
from .MeasureClass import *
from .MeasurePackageClass import *
from .MeasureSort import *
from .RunSimulationCase import *

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QGraphicsScene, QTableWidgetItem, QGraphicsPixmapItem, QWidget, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QPixmap, QTransform
from PyQt5.QtCore import Qt, QTimer
from datetime import datetime
import numpy as np
import os 
import calendar
import shutil


class MyMainWindow(QMainWindow,Ui_MainWindow):

    def __init__(self):
        super().__init__()
        
        self.setupUi(self)

        _legend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'LegendFigs')
        self.label_35.setPixmap(QPixmap(os.path.join(_legend_dir, 'kWh_Labels.png')))
        self.label_43.setPixmap(QPixmap(os.path.join(_legend_dir, 'Therm_Labels.png')))
        self.label_42.setPixmap(QPixmap(os.path.join(_legend_dir, 'EEM_kWhLabels.png')))
        self.label_44.setPixmap(QPixmap(os.path.join(_legend_dir, 'EEM_ThermLabels.png')))
        self.PieChartLegend.setPixmap(QPixmap(os.path.join(_legend_dir, 'EndUseLegend.png')))

        self.df_input = pd.read_csv("Inputs/BldgPropInputsFileTemplate.csv")
        #%% Preferences
        self.BldgPropInputFile.setEnabled(False)
        self.UseExistingBldgPropInpFile.toggled.connect(self.SetUseExistingBldgPropInpFile)

        self.MainPath = os.getcwd()
        self.ProjectName.textChanged.connect(self.SetProjectName)
        self.NewBldgPropInpFile.toggled.connect(self.SetProjectPath)
        #%% Set Utility Data
        self.OpenUtilDataWindow.setEnabled(False)
        self.UtilDataSourceFile.setEnabled(False)
        self.UtilDataSourceFileTool.setEnabled(False)
        
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
        self.EEMCostTable.setCellWidget(11,1,self.ECMCoolingEqpCostOptions)
        self.EEMCostTable.setCellWidget(12,1,self.ECMCoolingEffCostOptions)
        self.EEMCostTable.setCellWidget(13,1,self.ECMHeatingEqpCostOptions)
        self.EEMCostTable.setCellWidget(14,1,self.ECMHeatingEffCostOptions)

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
        self.ECMCoolingEqpCostOptions.currentIndexChanged.connect(self.SetECMCoolingEqpCostOptions)
        self.ECMHeatingEqpCostOptions.currentIndexChanged.connect(self.SetECMHeatingEqpCostOptions)
        self.ECMHeatingEffCostOptions.currentIndexChanged.connect(self.SetECMHeatingEffCostOptions)

        self.SetCostData.clicked.connect(self.SetSetCostData) 
        self.ResetCostData.clicked.connect(self.SetResetCostData)
    #%% ECM Evaluation

        self.ECMEval.setCellWidget(0,3,self.ECMWallInsulation)
        self.ECMEval.setCellWidget(1,3,self.ECMInfiltration)
        self.ECMEval.setCellWidget(2,3,self.ECMCeilingInsulation)
        self.ECMEval.setCellWidget(3,3,self.ECMWindowMaterial)
        self.ECMEval.setCellWidget(4,3,self.ECMNightSetback)
        self.ECMEval.setCellWidget(5,3,self.ECMHoursNightSetback)
        self.ECMEval.setCellWidget(6,3,self.ECMDaylighting)
        self.ECMEval.setCellWidget(7,3,self.ECMEconomizer)
        self.ECMEval.setCellWidget(8,3,self.ECMOccSensor)
        self.ECMEval.setCellWidget(9,3,self.ECMPctLED)
        self.ECMEval.setCellWidget(10,3,self.ECMReduceEqpLoad)
        self.ECMEval.setCellWidget(11,3,self.ECMHeatingEquipment)
        self.ECMEval.setCellWidget(12,3,self.ECMCoolingEquipment)

        checkboxes = [
            self.ECMWallInsCheck,
            self.ECMInfiltrationCheck,
            self.ECMCeilInsCheck,
            self.ECMWindowMatCheck,
            self.ECMNightSetbackCheck,
            self.ECMHoursNightSetbackCheck,
            self.ECMDaylightingCheck,
            self.ECMEconomizerCheck,
            self.ECMOccSensorCheck,
            self.ECMPctLEDCheck,
            self.ECMReduceEqpLoadCheck,
            self.ECMHeatingEqpCheck,
            self.ECMCoolingEqpCheck
        ]

        # Assign each checkbox centered in column 1
        for i, checkbox in enumerate(checkboxes):
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            self.ECMEval.setCellWidget(i, 1, container)
        
        self.ECMWallInsulation.setEnabled(False)
        self.ECMInfiltration.setEnabled(False)
        self.ECMCeilingInsulation.setEnabled(False)
        self.ECMWindowMaterial.setEnabled(False)
        self.ECMNightSetback.setEnabled(False)
        self.ECMHoursNightSetback.setEnabled(False)
        self.ECMDaylighting.setEnabled(False)
        self.ECMEconomizer.setEnabled(False)
        self.ECMOccSensor.setEnabled(False)
        self.ECMPctLED.setEnabled(False)
        self.ECMReduceEqpLoad.setEnabled(False)
        self.ECMHeatingEquipment.setEnabled(False)
        self.ECMCoolingEquipment.setEnabled(False)

        self.ECMWallInsCheck.stateChanged.connect(self.SetECMWallInsCheck)
        self.ECMInfiltrationCheck.stateChanged.connect(self.SetECMInfiltrationCheck)
        self.ECMCeilInsCheck.stateChanged.connect(self.SetECMCeilInsCheck)
        self.ECMWindowMatCheck.stateChanged.connect(self.SetECMWindowMatCheck)
        self.ECMNightSetbackCheck.stateChanged.connect(self.SetECMNightSetbackCheck)
        self.ECMHoursNightSetbackCheck.stateChanged.connect(self.SetECMHoursNightSetbackCheck)
        self.ECMDaylightingCheck.stateChanged.connect(self.SetECMDaylightingCheck)
        self.ECMEconomizerCheck.stateChanged.connect(self.SetECMEconomizerCheck)
        self.ECMOccSensorCheck.stateChanged.connect(self.SetECMOccSensorCheck)
        self.ECMPctLEDCheck.stateChanged.connect(self.SetECMPctLEDCheck)
        self.ECMReduceEqpLoadCheck.stateChanged.connect(self.SetECMReduceEqpLoadCheck)
        self.ECMHeatingEqpCheck.stateChanged.connect(self.SetECMHeatingEqpCheck)
        self.ECMCoolingEqpCheck.stateChanged.connect(self.SetECMCoolingEqpCheck)

        self.ECMWallInsulation.currentTextChanged.connect(self.SetWallInsChange)
        self.ECMInfiltration.currentTextChanged.connect(self.SetInfilChange)
        self.ECMCeilingInsulation.currentTextChanged.connect(self.SetCeilInsChange)
        self.ECMWindowMaterial.currentTextChanged.connect(self.SetWindowMatChange)
        self.ECMNightSetback.currentTextChanged.connect(self.SetNightSetbackChange)
        self.ECMHoursNightSetback.currentTextChanged.connect(self.SetHoursNightSetbackChange)
        self.ECMDaylighting.currentTextChanged.connect(self.SetDaylightingChange)
        self.ECMEconomizer.currentTextChanged.connect(self.SetEconomizerChange)
        self.ECMOccSensor.currentTextChanged.connect(self.SetOccupancySensorChange)
        self.ECMPctLED.currentTextChanged.connect(self.SetLEDChange)
        self.ECMReduceEqpLoad.currentTextChanged.connect(self.SetReduceEquipmentLoadChange)
        self.ECMHeatingEquipment.currentTextChanged.connect(self.SetHeatingEqpChange)
        self.ECMCoolingEquipment.currentTextChanged.connect(self.SetCoolingEqpChange)

        self.EvaluateMeasures.clicked.connect(self.SetEvaluateMeasures)
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
        if not self.SetSetSelections():
            return
        self.CPT = BuildChangePointModel(self.ProjectPath,self.ProjectName.text(),self.df_input,self.df_weather)
        self.model_type_cooling, self.model_parameters_cooling,  self.model_type_heating, self.model_parameters_heating = self.CPT.BuildTemperatureBasedModel()
        self.sceneHeatingTempCPT = QGraphicsScene(self)
        self.HeatingTempResults.setScene(self.sceneHeatingTempCPT)
        imagePath = os.path.join(self.ProjectPath,"Results",f"Fossil Fuel_{self.model_type_heating}_TempBasedChngPtModel.png")
        self.ShowGUIImage(self.sceneHeatingTempCPT,self.HeatingTempResults,imagePath)

        self.sceneCoolingTempCPT = QGraphicsScene(self)
        self.CoolingTempResults.setScene(self.sceneCoolingTempCPT)
        imagePath = os.path.join(self.ProjectPath,"Results",f"Electricity_{self.model_type_cooling}_TempBasedChngPtModel.png")
        self.ShowGUIImage(self.sceneCoolingTempCPT,self.CoolingTempResults,imagePath)

    def GetMonthlyEndUseBreakdown(self):
        self.BestModelParams = self.CPT.ChooseBestModel(self.DDResults,self.model_parameters_heating,self.model_parameters_cooling,self.ProjectPath)

        GetMonthlyEndUseBreakdown(self.BestModelParams,self.df_weather,self.df_input,self.ProjectPath)

        self.CostData = pd.read_csv(os.path.join(self.ProjectPath,"CostData","BasicCostData.csv")).iloc[0].to_dict()
        GetSummaryResults(self.ProjectPath,self.CostData)   

        # print("End Use", self.df_MonthlyEndUse, "Total", self.df_MonthlyEndUse.loc[:,self.df_MonthlyEndUse.columns.str.contains("EL-")].sum())
        # self.BestModelParams["OrgTotalElectricity"] = self.df_MonthlyEndUse.loc[:,self.df_MonthlyEndUse.columns.str.contains("EL-")].sum().sum()/3.41 # Convert to kWh
        # self.BestModelParams["OrgTotalNaturalGas"] = self.df_MonthlyEndUse.loc[:,self.df_MonthlyEndUse.columns.str.contains("NG-")].sum().sum()/100 # Convert to Therms
        # self.BestModelParams["BLC_Heat_EL"] = self.df_MonthlyEndUse["BLC_Heat_EL"].mean()
        # self.BestModelParams["BLC_Heat_NG"] = self.df_MonthlyEndUse["BLC_Heat_NG"].mean()

        # self.BestModelParams["BLC_Cool_EL"] = self.df_MonthlyEndUse["BLC_Cool_EL"].mean()
        #print(self.BestModelParams)

        self.PltRes = PlotResults(True,self.ProjectPath)
        self.PltRes.PlotEndUseBreakdown(self.ProjectPath)
        self.PltRes.PlotInverseModelComparison(self.ProjectPath,self.dfutilDataSorted)

        self.sceneEndUseBreakdown = QGraphicsScene(self)
        self.ShowEndUseBreakdown.setScene(self.sceneEndUseBreakdown)
        imagePath = os.path.join(self.ProjectPath,"Results",f"EndUseBreakdown.png")
        self.ShowGUIImage(self.sceneEndUseBreakdown,self.ShowEndUseBreakdown,imagePath)

        self.scenekWhEndUseBreakdown = QGraphicsScene(self)
        self.kWhModelComparison.setScene(self.scenekWhEndUseBreakdown)
        imagePath = os.path.join(self.ProjectPath,"Results",f"ElectricityMonthlyBreakdown.png")
        self.ShowGUIImage(self.scenekWhEndUseBreakdown,self.kWhModelComparison,imagePath)

        self.sceneThermEndUseBreakdown = QGraphicsScene(self)
        self.ThermModelComparison.setScene(self.sceneThermEndUseBreakdown)
        imagePath = os.path.join(self.ProjectPath,"Results",f"NaturalGasMonthlyBreakdown.png")
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
        imagePath = os.path.join(self.ProjectPath,"Results",f"FossilFuel_Heating_DDBasedChngPtModel.png")
        self.ShowGUIImage(self.sceneHeatingDDCPT,self.HeatingDDResults,imagePath)
        
        self.sceneCoolingDDCPT = QGraphicsScene(self)
        self.CoolingDDResults.setScene(self.sceneCoolingDDCPT)
        imagePath = os.path.join(self.ProjectPath,"Results",f"Electricity_Cooling_DDBasedChngPtModel.png")
        self.ShowGUIImage(self.sceneCoolingDDCPT,self.CoolingDDResults,imagePath)

        self.GetMonthlyEndUseBreakdown()

    def SetGetWeatherData(self):
        ok, _ = self._validate_required_text(self.ProjectName.text(), "Project Name")
        if not ok:
            QMessageBox.warning(self, "Input Required", "Please enter a Project Name before fetching weather data.")
            return
        ok, _ = self._validate_required_text(self.Location.text(), "Location")
        if not ok:
            QMessageBox.warning(self, "Input Required", "Please enter a Location before fetching weather data.")
            return
        if not os.path.exists(self.ProjectPath):
            QMessageBox.warning(self, "Project Path", "Project path does not exist. Please set building properties first.")
            return
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
        imagePath = os.path.join(self.ProjectPath,"Results",f"WeatherPlot_{weather_station_name}.png")
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
        # view_width = self.ShowShape.width()
        # view_height = self.ShowShape.height()

        # # Scale the pixmap to fit the view's size while maintaining its aspect ratio
        # scaled_pixmap = pixmap.scaled(view_width, view_height, aspectRatioMode=True, transformMode=Qt.SmoothTransformation)
        self.sceneOrientation.clear()

        pixmapItem = QGraphicsPixmapItem(pixmap)
        self.sceneOrientation.addItem(pixmapItem)

        newBorder = pixmapItem.mapToScene(pixmapItem.boundingRect()).boundingRect()
        self.sceneOrientation.setSceneRect(newBorder)

        

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
        # self.ShowShape.setScene(self.sceneOrientation)
        QTimer.singleShot(0, lambda: self.ShowShape.fitInView(self.sceneOrientation.sceneRect(), mode=1))
        # self.ShowShape.fitInView(self.sceneOrientation.sceneRect(),mode=1)
        self.ShowShape.centerOn(self.sceneOrientation.sceneRect().center())
        # self.ShowShape.setRenderHint(QPainter.Antialiasing, True)
        # self.ShowShape.setRenderHint(QPainter.SmoothPixmapTransform, True)


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

        scene.clear()
        # Scale the pixmap to fit the view's size while maintaining its aspect ratio
        # scaled_pixmap = pixmap.scaled(view_width, view_height, aspectRatioMode=True, transformMode=Qt.SmoothTransformation)
        # view_size = self.ThermResults.viewport().size()
        # pixmap1 = pixmap.scaled(view_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        pixmapItem = QGraphicsPixmapItem(pixmap)
        pixmapItem.setTransformationMode(Qt.SmoothTransformation)
        scene.addItem(pixmapItem)

        newBorder = pixmapItem.mapToScene(pixmapItem.boundingRect()).boundingRect()
        scene.setSceneRect(newBorder)

        # Set the scene to the QGraphicsView

        QTimer.singleShot(0, lambda: view.fitInView(scene.sceneRect(), mode=1))

        # view.fitInView(scene.sceneRect(),Qt.KeepAspectRatio)#,mode=1)
        # view.setScene(scene)
        view.centerOn(scene.sceneRect().center())
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
        path = self.BldgPropInputFile.text().strip()
        if not path:
            QMessageBox.warning(self, "Input Required", "Please specify a building properties input file path.")
            return
        if not os.path.isfile(path):
            QMessageBox.warning(self, "File Not Found", f"The file was not found:\n{path}")
            return
        try:
            self.df_input = pd.read_pickle(path)
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Could not load the properties file:\n{str(e)}")
            return
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
        
        gpd_raw = self.df_input.loc[self.df_input.PropKey=="GPD","PropValue"].astype(str).item()
        self.GPD.setText("" if gpd_raw in ("nan", "") else gpd_raw)
        self.LPD.setText(self.df_input.loc[self.df_input.PropKey=="LPD","PropValue"].astype(str).item())
        epd_raw = self.df_input.loc[self.df_input.PropKey=="EPD","PropValue"].astype(str).item()
        self.EPD.setText("" if epd_raw in ("nan", "") else epd_raw)
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

    def _validate_numeric(self, text, field_name, allow_empty=False, allow_zero=True, min_val=None, max_val=None):
        """Validate numeric input. Returns (success: bool, value or error_message)."""
        text = str(text).strip() if text is not None else ""
        if not text:
            if allow_empty:
                return True, None
            return False, f"'{field_name}' cannot be blank."
        try:
            value = float(text)
        except ValueError:
            return False, f"'{field_name}' must be a valid number (got '{text}')."
        if not allow_zero and value == 0:
            return False, f"'{field_name}' cannot be zero."
        if min_val is not None and value < min_val:
            return False, f"'{field_name}' must be at least {min_val}."
        if max_val is not None and value > max_val:
            return False, f"'{field_name}' must be at most {max_val}."
        return True, value

    def _validate_required_text(self, text, field_name):
        """Validate required non-empty text. Returns (success: bool, value or error_message)."""
        text = str(text).strip() if text is not None else ""
        if not text:
            return False, f"'{field_name}' cannot be blank."
        return True, text

    def _get_table_cell_text(self, table, row, col, field_name):
        """Safely get table cell text. Returns (success, text or error_msg)."""
        item = table.item(row, col)
        if item is None:
            return False, f"Cost data for '{field_name}' (row {row}) is empty."
        text = item.text().strip() if item.text() else ""
        if not text:
            return False, f"Cost data for '{field_name}' (row {row}) cannot be blank."
        try:
            float(text)  # Must be numeric
        except ValueError:
            return False, f"Cost data for '{field_name}' (row {row}) must be a valid number."
        return True, text
    
    def SetSetSelections(self):
        errors = []

        # Project name and location
        ok, _ = self._validate_required_text(self.ProjectName.text(), "Project Name")
        if not ok:
            errors.append(_)
        ok, _ = self._validate_required_text(self.Location.text(), "Location")
        if not ok:
            errors.append(_)

        # Orientation and Shape must be selected
        if self.Orientation.currentItem() is None:
            errors.append("'Orientation' must be selected.")
        if self.ShapeType.currentItem() is None:
            errors.append("'Shape Type' must be selected.")
        if self.WindowMaterial.currentItem() is None:
            errors.append("'Window Material' must be selected.")

        # Numeric geometry fields (x1, y1 must be > 0 for division)
        for widget, name, allow_zero in [
            (self.FloorArea, "Floor Area", False),
            (self.FlrQty, "Floor Quantity", False),
            (self.WallHt, "Wall Height", False),
            (self.x1, "x1 (Shape dimension)", False),
            (self.x2, "x2 (Shape dimension)", True),
            (self.y1, "y1 (Shape dimension)", False),
            (self.y2, "y2 (Shape dimension)", True),
        ]:
            ok, _ = self._validate_numeric(widget.text(), name, allow_zero=allow_zero)
            if not ok:
                errors.append(_)

        # WWR, Overhang, Window dimensions
        for widget, name in [
            (self.WWR_Front, "WWR Front"), (self.WWR_Left, "WWR Left"),
            (self.WWR_Back, "WWR Back"), (self.WWR_Right, "WWR Right"),
            (self.Overhang, "Overhang"), (self.WindowHt, "Window Height"),
            (self.nWindow, "Number of Windows"),
        ]:
            ok, _ = self._validate_numeric(widget.text(), name, allow_empty=False, min_val=0)
            if not ok:
                errors.append(_)

        # HVAC and controls
        for widget, name in [
            (self.Tsph, "Heating setpoint"), (self.Tspc, "Cooling setpoint"),
            (self.DHWTankVol, "DHW Tank Volume"),
        ]:
            ok, _ = self._validate_numeric(widget.text(), name)
            if not ok:
                errors.append(_)
        ok, _ = self._validate_numeric(self.NightSetback.currentText(), "Night setback")
        if not ok:
            errors.append(_)
        ok, _ = self._validate_numeric(self.nNightSetbackHours.text(), "Night setback hours")
        if not ok:
            errors.append(_)

        # Lighting
        for widget, name in [
            (self.LPD, "Lighting Power Density"),
        ]:
            ok, _ = self._validate_numeric(widget.text(), name, min_val=0)
            if not ok:
                errors.append(_)
        ok, _ = self._validate_numeric(self.LED.currentText(), "LED percentage", min_val=0)
        if not ok:
            errors.append(_)
        if self.EPD.text().strip():
            ok, _ = self._validate_numeric(self.EPD.text(), "Equipment Power Density", min_val=0)
            if not ok:
                errors.append(_)
        if self.GPD.text().strip():
            ok, _ = self._validate_numeric(self.GPD.text(), "Gas Power Density", min_val=0)
            if not ok:
                errors.append(_)

        # Custom efficiency when "Other.." selected
        if self.CoolingEff.currentText() == "Other..":
            ok, _ = self._validate_numeric(self.CoolingEffCustom.text(), "Cooling efficiency (custom)", allow_zero=False)
            if not ok:
                errors.append(_)
        if self.HeatingEff.currentText() == "Other..":
            ok, _ = self._validate_numeric(self.HeatingEffCustom.text(), "Heating efficiency (custom)", allow_zero=False)
            if not ok:
                errors.append(_)

        if errors:
            QMessageBox.critical(
                self,
                "Input Validation Error",
                "Please correct the following:\n\n• " + "\n• ".join(errors)
            )
            return False

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
        
        self.SetGPD(self.GPD.text())
        self.SetLPD(self.LPD.text())
        self.SetDaylighting(self.Daylighting.currentText())
        self.SetLEDCurrent(self.LED.currentText())
        self.SetEPD(self.EPD.text())
        #no user input for Reduce Equipment Load only change is in EEMs

        self.df_input.to_pickle(os.path.join(self.ProjectPath,"BldgPropInputsFile.pkl"))
        ## Construct the required IDF file and save in Current Directory
        return True

        
    
    def SetOriginalBldgPropFile(self):
        if not self.SetSetSelections():
            return
        self.LoadCostData()
        self.df_input.to_pickle(os.path.join(self.ProjectPath,"BldgPropInputFile-Baseline.pkl"))

    def SetUseExistingUtilityData(self,checked):
        self.UtilDataSourceFile.setEnabled(checked)
        self.UtilDataSourceFileTool.setEnabled(checked)
        self.LoadUtilityData.setEnabled(checked)

    def SetOpenUtilityDataWindow(self):
        ok, _ = self._validate_required_text(self.ProjectName.text(), "Project Name")
        if not ok:
            QMessageBox.warning(self, "Input Required", "Please enter a Project Name before opening the utility data window.")
            return
        self.UtilityDataWindow = UtilityDataWindow(self.ProjectPath, self.ProjectName.text())
        self.UtilityDataWindow.show()

    def SetLoadUtilityData(self):
        ok, _ = self._validate_required_text(self.ProjectName.text(), "Project Name")
        if not ok:
            QMessageBox.warning(self, "Input Required", "Please enter a Project Name before loading utility data.")
            return
        path = self.UtilDataSourceFile.text().strip()
        if not path:
            QMessageBox.warning(self, "Input Required", "Please specify a utility data source file path.")
            return
        if not os.path.isfile(path):
            QMessageBox.warning(self, "File Not Found", f"The file was not found:\n{path}")
            return
        try:
            dfutildata = pd.read_csv(path, index_col=0)
            if "BillDays" in dfutildata.columns:
                dfutildata = dfutildata.drop(columns={"BillDays"})
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Could not load the utility data file:\n{str(e)}")
            return
        self.UtilityDataWindow = UtilityDataWindow(self.ProjectPath, self.ProjectName.text())
        self.UtilityDataWindow.show()
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
        if not os.path.exists(os.path.join(self.ProjectPath,"CostData")):
            self.CopyCostData()
        self.LoadCostData()

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
    
    def SetGPD(self, text):
        text = text.strip()
        self.df_input.loc[self.df_input.PropKey=="GPD","PropValue"] = float(text) if text else None
    
    def SetLPD(self,text):
        self.df_input.loc[self.df_input.PropKey=="LPD","PropValue"] = float(text)

    def SetEPD(self, text):
        text = text.strip()
        self.df_input.loc[self.df_input.PropKey=="EPD","PropValue"] = float(text) if text else None

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
        self.LoadCostData()

    def LoadCostData(self):
        self.SetBasicCostData()
        self.SetECMWallInsCostOptions()
        self.SetECMInfiltrationCostOptions()
        self.SetECMCeilingInsCostOptions()
        self.SetECMWindowMatCostOptions()
        self.SetECMNightSetbackCostOptions()
        self.SetECMHoursofNightSetbackCostOptions()
        if self.ECMDaylightingCostOptions.currentText() == "Yes":
            self.SetECMDaylightingCostOptions()
        
        if self.ECMEconCostOptions.currentText() == "Yes":
            self.SetECMEconomizerCostOptions()

        if self.ECMOccSensorCostOptions.currentText() == "Yes":
            self.SetECMOccSensorCostOptions()

        self.SetECMLEDLightingCostOptions()
        self.SetECMReduceEquipmentLoadCostOptions()
        # First add items and set default values 
        self.SetECMCoolingEqpCostOptions()
        self.SetECMCoolingEffCostOptions()
        
        self.SetECMHeatingEqpCostOptions()
        self.SetECMHeatingEffCostOptions()

    def SetBasicCostData(self):
        self.CostData = pd.read_csv(os.path.join(self.ProjectPath, "CostData","BasicCostData.csv")).iloc[0].to_dict()
        self.kWhCost.setText(str(self.CostData["kWhRate"]))
        self.ThermCost.setText(str(self.CostData["ThermRate"]))
        self.DiscountRate.setText(str(self.CostData["DiscountRate"]))
        self.Lifetime.setText(str(self.CostData["Lifetime"]))

        pd.DataFrame([self.CostData]).to_csv(os.path.join(self.ProjectPath,"CostData","BasicCostData.csv"),index=False)


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
        DaylightingFC = self.DaylightingCostOptions.loc[self.DaylightingCostOptions["Daylighting"].astype(str) == self.ECMDaylightingCostOptions.currentText()]["FixedCost"].astype(str).item()
        DaylightingVC = self.DaylightingCostOptions.loc[self.DaylightingCostOptions["Daylighting"].astype(str) == self.ECMDaylightingCostOptions.currentText()]["Costpersft"].astype(str).item()

        self.EEMCostTable.setItem(6,2,QTableWidgetItem(DaylightingFC))
        self.EEMCostTable.setItem(6,3,QTableWidgetItem(DaylightingVC))

    def SetECMEconomizerCostOptions(self):
        self.EconomizerCostOptions = pd.read_csv(os.path.join(self.ProjectPath, "CostData","System-Economizer.csv"))
        EconomizerFC = self.EconomizerCostOptions.loc[self.EconomizerCostOptions["Economizer"].astype(str) == self.ECMEconCostOptions.currentText()]["FixedCost"].astype(str).item()
        EconomizerVC = self.EconomizerCostOptions.loc[self.EconomizerCostOptions["Economizer"].astype(str) == self.ECMEconCostOptions.currentText()]["Costpersft"].astype(str).item()

        self.EEMCostTable.setItem(7,2,QTableWidgetItem(EconomizerFC))
        self.EEMCostTable.setItem(7,3,QTableWidgetItem(EconomizerVC))
    
    def SetECMOccSensorCostOptions(self):
        self.OccupancySensorCostOptions = pd.read_csv(os.path.join(self.ProjectPath, "CostData","Equipment-OccupancySensor.csv"))
        OccupancySensorFC = self.OccupancySensorCostOptions.loc[self.OccupancySensorCostOptions["OccupancySensor"].astype(str) == self.ECMOccSensorCostOptions.currentText()]["FixedCost"].astype(str).item()
        OccupancySensorVC = self.OccupancySensorCostOptions.loc[self.OccupancySensorCostOptions["OccupancySensor"].astype(str) == self.ECMOccSensorCostOptions.currentText()]["Costpersft"].astype(str).item()

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
            # self.CoolingEffCostOptions = pd.read_csv(os.path.join(self.ProjectPath, "CostData","System-"+self.CoolingEqp.currentText().replace(" ","")+".csv"))
            # print(self.CoolingEffCostOptions)
            # print(self.CoolingEffCostOptions["SEER"].astype(str).tolist())
            # self.ECMCoolingEffCostOptions.addItems(self.CoolingEffCostOptions["SEER"].astype(str).tolist())
            
            # print(self.ECMCoolingEffCostOptions.currentText())
            CoolingEffFC = self.CoolingEqpOptionsTable.loc[self.CoolingEqpOptionsTable["SEER"].astype(float) == float(self.ECMCoolingEffCostOptions.currentText()),"Costperunit"].astype(str).item()
            CoolingEffVC = self.CoolingEqpOptionsTable.loc[self.CoolingEqpOptionsTable["SEER"].astype(float) == float(self.ECMCoolingEffCostOptions.currentText()),"CostperkBtuh"].astype(str).item()

            self.EEMCostTable.setItem(12,2,QTableWidgetItem(CoolingEffFC))
            self.EEMCostTable.setItem(12,3,QTableWidgetItem(CoolingEffVC))

    def SetECMHeatingEffCostOptions(self):
        if "No" not in self.HeatingEqp.currentText():
            # self.GetHeatingSystemOptions(self.ECMHeatingEqpCostOptions.currentText().replace(" ",""))
            
            HeatingEffFC = self.HeatingEqpOptionsTable.loc[self.HeatingEqpOptionsTable["HeatingEff"].astype(float) == float(self.ECMHeatingEffCostOptions.currentText())]["Costperunit"].astype(str).item()
            HeatingEffVC = self.HeatingEqpOptionsTable.loc[self.HeatingEqpOptionsTable["HeatingEff"].astype(float) == float(self.ECMHeatingEffCostOptions.currentText())]["CostperkBtuh"].astype(str).item()

            self.EEMCostTable.setItem(14,2,QTableWidgetItem(HeatingEffFC))
            self.EEMCostTable.setItem(14,3,QTableWidgetItem(HeatingEffVC))
    
    def SetECMCoolingEqpCostOptions(self):
        self.GetCoolingSystemOptions(self.ECMCoolingEqpCostOptions.currentText().replace(" ",""))
        # 
        self.ECMCoolingEffCostOptions.blockSignals(True)
        self.ECMCoolingEffCostOptions.clear()
        self.ECMCoolingEffCostOptions.addItems(self.CoolingEqpOptionsTable["SEER"].astype(str).tolist())
        self.SetECMCoolingEffCostOptions()
        self.ECMCoolingEffCostOptions.blockSignals(False)

    def SetECMHeatingEqpCostOptions(self):
        self.GetHeatingSystemOptions(self.ECMHeatingEqpCostOptions.currentText().replace(" ",""))
        # 
        self.ECMHeatingEffCostOptions.blockSignals(True)
        self.ECMHeatingEffCostOptions.clear()
        self.ECMHeatingEffCostOptions.addItems(self.HeatingEqpOptionsTable["HeatingEff"].astype(str).tolist())
        self.SetECMHeatingEffCostOptions()
        self.ECMHeatingEffCostOptions.blockSignals(False)

        
    def SetSetCostData(self):
        errors = []
        for widget, name in [
            (self.kWhCost, "Electricity rate (kWh)"),
            (self.ThermCost, "Natural gas rate (Therm)"),
            (self.DiscountRate, "Discount rate"),
            (self.Lifetime, "Lifetime"),
        ]:
            ok, _ = self._validate_numeric(widget.text(), name, allow_zero=False)
            if not ok:
                errors.append(_)

        cost_table_fields = [
            (0, "Wall insulation"), (1, "Infiltration"), (2, "Ceiling insulation"),
            (3, "Window material"), (9, "LED"), (12, "Cooling efficiency"),
            (14, "Heating efficiency"),
        ]
        if self.ECMDaylightingCostOptions.currentText() == "Yes":
            cost_table_fields.append((6, "Daylighting"))
        if self.ECMEconCostOptions.currentText() == "Yes":
            cost_table_fields.append((7, "Economizer"))
        if self.ECMOccSensorCostOptions.currentText() == "Yes":
            cost_table_fields.append((8, "Occupancy sensor"))
        for row, name in cost_table_fields:
            ok, _ = self._get_table_cell_text(self.EEMCostTable, row, 2, name + " fixed cost")
            if not ok:
                errors.append(_)
            else:
                ok, _ = self._get_table_cell_text(self.EEMCostTable, row, 3, name + " variable cost")
                if not ok:
                    errors.append(_)

        if errors:
            QMessageBox.critical(self, "Cost Data Validation Error", "Please correct the following:\n\n• " + "\n• ".join(errors))
            return

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

        if self.ECMDaylightingCostOptions.currentText() == "Yes":
            self.DaylightingCostOptions.loc[self.DaylightingCostOptions["Daylighting"] == self.ECMDaylightingCostOptions.currentText(),"FixedCost"] = self.EEMCostTable.item(6,2).text()
            self.DaylightingCostOptions.loc[self.DaylightingCostOptions["Daylighting"] == self.ECMDaylightingCostOptions.currentText(),"Costpersft"] = self.EEMCostTable.item(6,3).text()
            self.DaylightingCostOptions.to_csv(os.path.join(self.ProjectPath, "CostData","Equipment-Daylighting.csv"),index=False)

        if self.ECMEconCostOptions.currentText() == "Yes":
            self.EconomizerCostOptions.loc[self.EconomizerCostOptions["Economizer"] == self.ECMEconCostOptions.currentText(),"FixedCost"] = self.EEMCostTable.item(7,2).text()
            self.EconomizerCostOptions.loc[self.EconomizerCostOptions["Economizer"] == self.ECMEconCostOptions.currentText(),"Costpersft"] = self.EEMCostTable.item(7,3).text()
            self.EconomizerCostOptions.to_csv(os.path.join(self.ProjectPath, "CostData","System-Economizer.csv"),index=False)

        if self.ECMOccSensorCostOptions.currentText() == "Yes":
            self.OccupancySensorCostOptions.loc[self.OccupancySensorCostOptions["OccupancySensor"] == self.ECMOccSensorCostOptions.currentText(),"FixedCost"] = self.EEMCostTable.item(8,2).text()
            self.OccupancySensorCostOptions.loc[self.OccupancySensorCostOptions["OccupancySensor"] == self.ECMOccSensorCostOptions.currentText(),"Costpersft"] = self.EEMCostTable.item(8,3).text()
            self.OccupancySensorCostOptions.to_csv(os.path.join(self.ProjectPath, "CostData","Equipment-OccupancySensor.csv"),index=False)

        self.LEDCostOptions.loc[self.LEDCostOptions["PercentageLED"] == self.ECMLEDCostOptions.currentText(),"FixedCost"] = self.EEMCostTable.item(9,2).text()
        self.LEDCostOptions.loc[self.LEDCostOptions["PercentageLED"] == self.ECMLEDCostOptions.currentText(),"Costpersft"] = self.EEMCostTable.item(9,3).text()
        self.GetCoolingSystemOptions(self.ECMCoolingEqpCostOptions.currentText().replace(" ",""))
        self.CoolingEqpOptionsTable.loc[self.CoolingEqpOptionsTable["SEER"].astype(float) == float(self.ECMCoolingEffCostOptions.currentText()),"Costperunit"] = self.EEMCostTable.item(12,2).text()
        self.CoolingEqpOptionsTable.loc[self.CoolingEqpOptionsTable["SEER"].astype(float) == float(self.ECMCoolingEffCostOptions.currentText()),"CostperkBtuh"] = self.EEMCostTable.item(12,3).text()
        self.GetHeatingSystemOptions(self.ECMHeatingEqpCostOptions.currentText().replace(" ",""))
        self.HeatingEqpOptionsTable.loc[self.HeatingEqpOptionsTable["HeatingEff"].astype(float) == float(self.ECMHeatingEffCostOptions.currentText()),"Costperunit"] = self.EEMCostTable.item(14,2).text()
        self.HeatingEqpOptionsTable.loc[self.HeatingEqpOptionsTable["HeatingEff"].astype(float) == float(self.ECMHeatingEffCostOptions.currentText()),"CostperkBtuh"] = self.EEMCostTable.item(14,3).text()
        
        self.WallInsCostOptions.to_csv(os.path.join(self.ProjectPath, "CostData","Materials-WallInsulation.csv"),index=False)
        self.InfiltrationCostOptions.to_csv(os.path.join(self.ProjectPath, "CostData","Infiltration.csv"),index=False)
        self.CeilingInsCostOptions.to_csv(os.path.join(self.ProjectPath, "CostData","Materials-CeilingInsulation.csv"),index=False)
        self.WindowMatCostOptions.to_csv(os.path.join(self.ProjectPath, "CostData","Materials-WindowMaterial.csv"),index=False)
        self.LEDCostOptions.to_csv(os.path.join(self.ProjectPath, "CostData","Equipment-LEDLighting.csv"),index=False)
        self.CoolingEqpOptionsTable.to_csv(os.path.join(self.ProjectPath, "CostData","System-"+self.ECMCoolingEqpCostOptions.currentText().replace(" ","")+".csv"),index=False)
        self.HeatingEqpOptionsTable.to_csv(os.path.join(self.ProjectPath, "CostData","System-"+self.ECMHeatingEqpCostOptions.currentText().replace(" ","")+".csv"),index=False)
        
        self.SetECMBaseProperty()

    def SetResetCostData(self):
        self.CopyCostData()

    def GetHeatingSystemOptions(self,HeatingEqp):
        self.HeatingEqpOptionsTable = pd.read_csv(os.path.join(self.ProjectPath,"CostData","System-"+HeatingEqp+".csv"))

    def GetCoolingSystemOptions(self,CoolingEqp):
        self.CoolingEqpOptionsTable = pd.read_csv(os.path.join(self.ProjectPath,"CostData","System-"+CoolingEqp+".csv"))

    def SetECMWallInsCheck(self):
        self.ECMWallInsulation.setEnabled(self.ECMWallInsCheck.isChecked())
        if not self.ECMWallInsCheck.isChecked():
            self.ECMMeasurePackage.PackageID["WallInsOptions"] = 0
            self.ECMWallInsulation.blockSignals(True)
            self.ECMWallInsulation.setCurrentText(self.WallInsulation.currentText())
            self.ECMWallInsulation.blockSignals(False)
    
    def SetECMInfiltrationCheck(self):
        self.ECMInfiltration.setEnabled(self.ECMInfiltrationCheck.isChecked())
        if not self.ECMInfiltrationCheck.isChecked():
            self.ECMMeasurePackage.PackageID["InfilOptions"] = 0
            self.ECMInfiltration.blockSignals(True)
            self.ECMInfiltration.setCurrentText(self.ACH50.currentText())
            self.ECMInfiltration.blockSignals(False)

    def SetECMCeilInsCheck(self):
        self.ECMCeilingInsulation.setEnabled(self.ECMCeilInsCheck.isChecked())
        if not self.ECMCeilInsCheck.isChecked():
            self.ECMMeasurePackage.PackageID["CeilInsOptions"] = 0
            self.ECMCeilingInsulation.blockSignals(True)
            self.ECMCeilingInsulation.setCurrentText(self.CeilingInsulation.currentText())
            self.ECMCeilingInsulation.blockSignals(False)
        

    def SetECMWindowMatCheck(self):
        self.ECMWindowMaterial.setEnabled(self.ECMWindowMatCheck.isChecked())
        if not self.ECMWindowMatCheck.isChecked():
            self.ECMMeasurePackage.PackageID["WindowMatOptions"] = 0
            self.ECMWindowMaterial.blockSignals(True)
            self.ECMWindowMaterial.setCurrentText(self.WindowMaterial.currentItem().text())
            self.ECMWindowMaterial.blockSignals(False)

    def SetECMNightSetbackCheck(self):
        self.ECMNightSetback.setEnabled(self.ECMNightSetbackCheck.isChecked())
        if not self.ECMNightSetbackCheck.isChecked():
            self.ECMMeasurePackage.PackageID["NightSetbackOptions"] = 0
            self.ECMNightSetback.blockSignals(True)
            self.ECMNightSetback.setCurrentText(self.NightSetback.currentText())
            self.ECMNightSetback.blockSignals(False)

    def SetECMHoursNightSetbackCheck(self):
        self.ECMHoursNightSetback.setEnabled(self.ECMHoursNightSetbackCheck.isChecked())
        if not self.ECMHoursNightSetbackCheck.isChecked():
            self.ECMMeasurePackage.PackageID["HoursNightSetbackOptions"] = 0
            self.ECMHoursNightSetback.blockSignals(True)
            self.ECMHoursNightSetback.setCurrentText(self.nNightSetbackHours.text())
            self.ECMHoursNightSetback.blockSignals(False)

    def SetECMDaylightingCheck(self):
        self.ECMDaylighting.setEnabled(self.ECMDaylightingCheck.isChecked())
        if not self.ECMDaylightingCheck.isChecked():
            self.ECMMeasurePackage.PackageID["DaylightingOptions"] = 0
            self.ECMDaylighting.blockSignals(True)
            self.ECMDaylighting.setCurrentText(self.Daylighting.currentText())
            self.ECMDaylighting.blockSignals(False)

    def SetECMEconomizerCheck(self):
        self.ECMEconomizer.setEnabled(self.ECMEconomizerCheck.isChecked())
        if not self.ECMEconomizerCheck.isChecked():
            self.ECMMeasurePackage.PackageID["EconomizerOptions"] = 0
            self.ECMEconomizer.blockSignals(True)
            self.ECMEconomizer.setCurrentText(self.Economizer.currentText())
            self.ECMEconomizer.blockSignals(False)

    def SetECMOccSensorCheck(self):
        self.ECMOccSensor.setEnabled(self.ECMOccSensorCheck.isChecked())
        if not self.ECMOccSensorCheck.isChecked():
           self.ECMMeasurePackage.PackageID["OccSensorOptions"] = 0
           self.ECMOccSensor.blockSignals(True)
           self.ECMOccSensor.setCurrentText("No")
           self.ECMOccSensor.blockSignals(False)

    def SetECMPctLEDCheck(self):
        self.ECMPctLED.setEnabled(self.ECMPctLEDCheck.isChecked())
        if not self.ECMPctLEDCheck.isChecked():
           self.ECMMeasurePackage.PackageID["PercentageLEDOptions"] = 0
           self.ECMPctLED.blockSignals(True)
           self.ECMPctLED.setCurrentText(self.LED.currentText())
           self.ECMPctLED.blockSignals(False)

    def SetECMReduceEqpLoadCheck(self):
        self.ECMReduceEqpLoad.setEnabled(self.ECMReduceEqpLoadCheck.isChecked())
        if not self.ECMReduceEqpLoadCheck.isChecked():
           self.ECMMeasurePackage.PackageID["ReduceEquipLoadOptions"] = 0
           self.ECMReduceEqpLoad.blockSignals(True)
           self.ECMReduceEqpLoad.setCurrentText("0")    
           self.ECMReduceEqpLoad.blockSignals(False)

    def SetECMHeatingEqpCheck(self):
        self.ECMHeatingEquipment.setEnabled(self.ECMHeatingEqpCheck.isChecked())
        if not self.ECMHeatingEqpCheck.isChecked():
            self.ECMMeasurePackage.PackageID["HeatingEqpOptions"] = 0
            self.ECMHeatingEquipment.blockSignals(True)
            self.ECMHeatingEquipment.setCurrentText(self.HeatingEqp.currentText())
            self.ECMHeatingEquipment.blockSignals(False)

    def SetECMCoolingEqpCheck(self):
        self.ECMCoolingEquipment.setEnabled(self.ECMCoolingEqpCheck.isChecked())
        if not self.ECMCoolingEqpCheck.isChecked():
            self.ECMMeasurePackage.PackageID["CoolingEqpOptions"] = 0
            self.ECMCoolingEquipment.blockSignals(True)
            self.ECMCoolingEquipment.setCurrentText(self.CoolingEqp.currentText())
            self.ECMCoolingEquipment.blockSignals(False)

    def GetECMHVACOptions(self):
        dfHeatingEqpOptions = pd.read_csv(os.path.join(self.MainPath,"Measures","System-HeatingEquipment.csv"))
        CurrentHeatingEqpIndex = dfHeatingEqpOptions.index[dfHeatingEqpOptions["System"] == self.df_input.loc[self.df_input["PropKey"] == "HeatingEquipment","PropValue"].item()].tolist()[0]
        dfHeatingEqpOptions = dfHeatingEqpOptions.iloc[CurrentHeatingEqpIndex:,:].copy()
        HeatingEqpItems = dfHeatingEqpOptions["System"].astype(str).values.tolist()
        
        self.HtgFullList = []
        for eqp in HeatingEqpItems:
            dfCurrentHeatingEqpOptions = pd.read_csv(os.path.join(self.MainPath,"Measures","System-"+eqp.replace(" ","")+".csv"))
            HtgEffItems = dfCurrentHeatingEqpOptions["HeatingEff"].astype(str).values.tolist()
            if eqp == self.df_input.loc[self.df_input["PropKey"] == "HeatingEquipment","PropValue"].item():
                if self.df_input.loc[self.df_input["PropKey"] == "HeatingEff","PropValue"].item() != "Other..":
                    CurrentHtgEff = self.df_input.loc[self.df_input["PropKey"] == "HeatingEff","PropValue"].item()
                    HtgEffItems = [item for item in HtgEffItems if float(item) >= float(CurrentHtgEff)]
                else:
                    CurrentHtgEff = self.df_input.loc[self.df_input["PropKey"] == "HeatingEffCustom","PropValue"].item()
                    HtgEffItems = [CurrentHtgEff] + [item for item in HtgEffItems if float(item) >= float(CurrentHtgEff)]

                
            # Append the appropriate unit to the heating efficiency values based on the equipment type
            if "GasFurnace" in eqp.replace(" ",""):
                HtgEffItems = [item + " (AFUE)" for item in HtgEffItems]
            elif "Electric" in eqp.replace(" ",""):
                HtgEffItems = [item + " (COP)" for item in HtgEffItems]
            elif "HeatPump" in eqp.replace(" ",""):
                HtgEffItems = [item + " (HSPF)" for item in HtgEffItems]
            # Append the heating efficiency list either abridged or full to the main list
            self.HtgFullList.append([eqp+" - "+eff for eff in HtgEffItems])


        # print(self.HtgFullList)

        dfCoolingEqpOptions = pd.read_csv(os.path.join(self.MainPath,"Measures","System-CoolingEquipment.csv"))
        CurrentCoolingEqpIndex = dfCoolingEqpOptions.index[dfCoolingEqpOptions["System"] == self.df_input.loc[self.df_input["PropKey"] == "CoolingEquipment","PropValue"].item()].tolist()[0]
        dfCoolingEqpOptions = dfCoolingEqpOptions.iloc[CurrentCoolingEqpIndex:,:].copy()
        CoolingEqpItems = dfCoolingEqpOptions["System"].astype(str).values.tolist()
        self.ClgFullList = []
        for eqp in CoolingEqpItems:
            dfCurrentCoolingEqpOptions = pd.read_csv(os.path.join(self.MainPath,"Measures","System-"+eqp.replace(" ","")+".csv"))
            ClgEffItems = dfCurrentCoolingEqpOptions["SEER"].astype(str).values.tolist()
            if eqp == self.df_input.loc[self.df_input["PropKey"] == "CoolingEquipment","PropValue"].item():
                if self.df_input.loc[self.df_input["PropKey"] == "CoolingEff","PropValue"].item() != "Other..":
                    CurrentClgEff = self.df_input.loc[self.df_input["PropKey"] == "CoolingEff","PropValue"].item()
                    ClgEffItems = [item for item in ClgEffItems if float(item) >= float(CurrentClgEff)]
                else:
                    CurrentClgEff = self.df_input.loc[self.df_input["PropKey"] == "CoolingEffCustom","PropValue"].item()
                    ClgEffItems = [CurrentClgEff] + [item for item in ClgEffItems if float(item) >= float(CurrentClgEff)]
                # ClgEffItems = [item for item in ClgEffItems if float(item) >= float(CurrentClgEff)]
            # Append the appropriate unit to the cooling efficiency values based on the equipment type
            ClgEffItems = [item + " (SEER)" for item in ClgEffItems]
            # Append the cooling efficiency list either abridged or full to the main list
            self.ClgFullList.append([eqp+" - "+eff for eff in ClgEffItems])
        # print(self.ClgFullList)
    
    def SetECMBaseProperty(self):

        # self.SetSetCostData()

        MeasureOpt = MeasureOptions(self.ProjectPath)
        
        MeasuresReference = {
            "WallInsOptions": MeasureOpt.WallInsulation, #1
            "CeilInsOptions": MeasureOpt.CeilingInsulation, #2
            "InfilOptions": MeasureOpt.Infiltration, #3
            "WindowMatOptions": MeasureOpt.WindowMaterial, #4
            "DaylightingOptions": MeasureOpt.DaylightingControls, #5
            "OccSensorOptions": MeasureOpt.OccupancySensorControls, #6
            "PercentageLEDOptions": MeasureOpt.PercentageLED, #7
            "ReduceEquipLoadOptions": MeasureOpt.ReduceEquipmentLoad, #8
            "EconomizerOptions": MeasureOpt.Economizer, #9
            "NightSetbackOptions": MeasureOpt.NightSetback, #10
            "HoursNightSetbackOptions": MeasureOpt.HoursNightSetback, #11
            "HeatingEqpOptions": MeasureOpt.HeatingEquipment, #12
            "CoolingEqpOptions": MeasureOpt.CoolingEquipment, #13
            "DHWEqpOptions": MeasureOpt.DHWEquipment, #14
        }
        
        self.MeasureTypes = {}
        for name, func in MeasuresReference.items():
            self.MeasureTypes[name] = VariableFilter(self.df_input, func())

        for key, value in self.MeasureTypes.items():
            self.MeasureTypes[key] = AddCurrentOptionasMeasure(self.df_input, MeasuresReference[key]()[0].PropName, value)

        # for key, value in self.MeasureTypes.items():
        #     print(f"{key}: {[measure.PropValue for measure in value]}")

        self.ECMMeasurePackage = MeasurePackage()
        self.ECMMeasurePackage.PackageID = {}
        for key in self.MeasureTypes.keys():
            self.ECMMeasurePackage.PackageID[key] = 0
        

        self.kWhPctChange.clear()
        self.ThermsPctChange.clear()
        self.TIC.clear()
        self.LCC.clear()

        self.GetECMHVACOptions()
        self.BaselineSumRes = pd.read_csv(os.path.join(self.ProjectPath,"SummaryResults.csv"))
        
        self.BaselinekWhConsumption.setText(str(round(self.BaselineSumRes["Electricity"].iloc[0])))
        self.BaselineThermConsumption.setText(str(round(self.BaselineSumRes["NaturalGas"].iloc[0])))
        self.BaselineAnnualOperatingCost.setText(str(round(self.BaselineSumRes["AnnualOperatingCost"].iloc[0])))
        self.BaselineLCC.setText(str(round(self.BaselineSumRes["TOC"].iloc[0])))

        self.ECMWallInsulation.blockSignals(True)
        self.ECMInfiltration.blockSignals(True)
        self.ECMCeilingInsulation.blockSignals(True)
        self.ECMWindowMaterial.blockSignals(True)
        self.ECMNightSetback.blockSignals(True)
        self.ECMHoursNightSetback.blockSignals(True)
        self.ECMDaylighting.blockSignals(True)
        self.ECMEconomizer.blockSignals(True)
        self.ECMHeatingEquipment.blockSignals(True)
        self.ECMCoolingEquipment.blockSignals(True)
        self.ECMOccSensor.blockSignals(True)

        self.ECMWallInsulation.setCurrentText(self.WallInsulation.currentText())
        self.ECMInfiltration.setCurrentText(self.ACH50.currentText())
        self.ECMCeilingInsulation.setCurrentText(self.CeilingInsulation.currentText())
        self.ECMWindowMaterial.setCurrentText(self.WindowMaterial.currentItem().text())
        self.ECMNightSetback.setCurrentText(self.NightSetback.currentText())
        self.ECMHoursNightSetback.setCurrentText(self.nNightSetbackHours.text())
        self.ECMDaylighting.setCurrentText(self.Daylighting.currentText())
        self.ECMEconomizer.setCurrentText(self.Economizer.currentText())
        self.ECMHeatingEquipment.addItems([item for sublist in self.HtgFullList for item in sublist])
        self.ECMCoolingEquipment.addItems([item for sublist in self.ClgFullList for item in sublist])

        self.ECMPctLED.blockSignals(True) # Prevent signals from being emitted while we modify the list
        AllLEDItems = [self.ECMPctLED.itemText(i) for i in range(self.ECMPctLED.count())]
        CurrentLEDItems = [item for item in AllLEDItems if float(item) >= float(self.LED.currentText())]
        self.ECMPctLED.clear()
        self.ECMPctLED.addItems(CurrentLEDItems)
        self.ECMPctLED.blockSignals(False)

        self.ECMOccSensor.setCurrentText(self.df_input.loc[self.df_input["PropKey"] == "OccupancySensor","PropValue"].item())
        
        self.ECMWallInsulation.blockSignals(False)
        self.ECMInfiltration.blockSignals(False)
        self.ECMCeilingInsulation.blockSignals(False)
        self.ECMWindowMaterial.blockSignals(False)
        self.ECMNightSetback.blockSignals(False)
        self.ECMHoursNightSetback.blockSignals(False)
        self.ECMDaylighting.blockSignals(False)
        self.ECMEconomizer.blockSignals(False)
        self.ECMHeatingEquipment.blockSignals(False)
        self.ECMCoolingEquipment.blockSignals(False)
        self.ECMOccSensor.blockSignals(False)



        self.ECMEval.setItem(0,2,QTableWidgetItem(self.WallInsulation.currentText()))
        self.ECMEval.setItem(1,2,QTableWidgetItem(self.ACH50.currentText()))
        self.ECMEval.setItem(2,2,QTableWidgetItem(self.CeilingInsulation.currentText()))
        self.ECMEval.setItem(3,2,QTableWidgetItem(self.WindowMaterial.currentItem().text()))
        self.ECMEval.setItem(4,2,QTableWidgetItem(self.NightSetback.currentText()))
        self.ECMEval.setItem(5,2,QTableWidgetItem(self.nNightSetbackHours.text()))
        self.ECMEval.setItem(6,2,QTableWidgetItem(self.Daylighting.currentText()))
        self.ECMEval.setItem(7,2,QTableWidgetItem(self.Economizer.currentText()))
        self.ECMEval.setItem(8,2,QTableWidgetItem(self.df_input.loc[self.df_input["PropKey"] == "OccupancySensor","PropValue"].item()))
        self.ECMEval.setItem(9,2,QTableWidgetItem(self.LED.currentText()))
        self.ECMEval.setItem(10,2,QTableWidgetItem(self.df_input.loc[self.df_input["PropKey"] == "EquipLoadRed","PropValue"].item()))
        if self.HeatingEff.currentText() != "Other..":
            CurrentHtgEff = self.HeatingEff.currentText()
        else:
            CurrentHtgEff = self.HeatingEffCustom.text()

        if "Gas Furnace" in self.HeatingEqp.currentText():
            self.ECMEval.setItem(11,2,QTableWidgetItem(self.HeatingEqp.currentText()+" - "+CurrentHtgEff+" (AFUE)"))
        elif "Electric Heater" in self.HeatingEqp.currentText():
            self.ECMEval.setItem(11,2,QTableWidgetItem(self.HeatingEqp.currentText()+" - "+CurrentHtgEff+" (COP)"))
        elif "Air Source Heat Pump" in self.HeatingEqp.currentText():
            self.ECMEval.setItem(11,2,QTableWidgetItem(self.HeatingEqp.currentText()+" - "+CurrentHtgEff+" (HSPF)"))
        
        if self.CoolingEff.currentText() != "Other..":
            CurrentClgEff = self.CoolingEff.currentText()
        else:
            CurrentClgEff = self.CoolingEffCustom.text()
        self.ECMEval.setItem(12,2,QTableWidgetItem(self.CoolingEqp.currentText()+" - "+CurrentClgEff+" (SEER)"))



    def SetWallInsChange(self):
        for i,measure in enumerate(self.MeasureTypes["WallInsOptions"]):
            if measure.PropValue == self.ECMWallInsulation.currentText():
                self.ECMMeasurePackage.PackageID["WallInsOptions"] = i
                break

    def SetInfilChange(self):
        for i,measure in enumerate(self.MeasureTypes["InfilOptions"]):
            if measure.PropValue == float(self.ECMInfiltration.currentText()):
                self.ECMMeasurePackage.PackageID["InfilOptions"] = i
                break

    def SetCeilInsChange(self):
        for i,measure in enumerate(self.MeasureTypes["CeilInsOptions"]):
            if measure.PropValue == self.ECMCeilingInsulation.currentText():
                self.ECMMeasurePackage.PackageID["CeilInsOptions"] = i
                break

    def SetWindowMatChange(self):
        for i,measure in enumerate(self.MeasureTypes["WindowMatOptions"]):
            if measure.PropValue == self.ECMWindowMaterial.currentText():
                self.ECMMeasurePackage.PackageID["WindowMatOptions"] = i
                break

    def SetNightSetbackChange(self):
        for i,measure in enumerate(self.MeasureTypes["NightSetbackOptions"]):
            if float(measure.PropValue) == float(self.ECMNightSetback.currentText()):
                self.ECMMeasurePackage.PackageID["NightSetbackOptions"] = i
                break
    
    def SetHoursNightSetbackChange(self):
        for i,measure in enumerate(self.MeasureTypes["HoursNightSetbackOptions"]):
            if float(measure.PropValue) == float(self.ECMHoursNightSetback.currentText()):
                self.ECMMeasurePackage.PackageID["HoursNightSetbackOptions"] = i
                break

    def SetDaylightingChange(self):
        for i,measure in enumerate(self.MeasureTypes["DaylightingOptions"]):
            if measure.PropValue == self.ECMDaylighting.currentText():
                self.ECMMeasurePackage.PackageID["DaylightingOptions"] = i
                break

    def SetReduceEquipmentLoadChange(self):
        for i,measure in enumerate(self.MeasureTypes["ReduceEquipLoadOptions"]):
            print(measure.PropValue, self.ECMReduceEqpLoad.currentText())
            if measure.PropValue == float(self.ECMReduceEqpLoad.currentText()):
                self.ECMMeasurePackage.PackageID["ReduceEquipLoadOptions"] = i
                break

    def SetEconomizerChange(self):
        for i,measure in enumerate(self.MeasureTypes["EconomizerOptions"]):
            if measure.PropValue == self.ECMEconomizer.currentText():
                self.ECMMeasurePackage.PackageID["EconomizerOptions"] = i
                break

    def SetOccupancySensorChange(self):
        for i,measure in enumerate(self.MeasureTypes["OccSensorOptions"]):
            if measure.PropValue == self.ECMOccSensor.currentText():
                self.ECMMeasurePackage.PackageID["OccSensorOptions"] = i
                break

    def SetLEDChange(self):
        for i,measure in enumerate(self.MeasureTypes["PercentageLEDOptions"]):
            if measure.PropValue == float(self.ECMPctLED.currentText()):
                self.ECMMeasurePackage.PackageID["PercentageLEDOptions"] = i
                break

    def SetHeatingEqpChange(self):
        HeatingEqpSplit = self.ECMHeatingEquipment.currentText().split(" - ")
        for i,measure in enumerate(self.MeasureTypes["HeatingEqpOptions"]):
            if HeatingEqpSplit[0].replace(" ","") in measure.PropName:
                if float(HeatingEqpSplit[1].replace(" (AFUE)","").replace(" (COP)","").replace(" (HSPF)","")) == float(measure.PropValue):
                    self.ECMMeasurePackage.PackageID["HeatingEqpOptions"] = i
                    break
        # self.SetHeatingEqp(HeatingEqpSplit[0])
        # if "Gas Furnace" in HeatingEqpSplit[0]:
        #     self.SetHeatingEff(HeatingEqpSplit[1].replace(" (AFUE)",""))
        # elif "Electric Heater" in HeatingEqpSplit[0]:
        #     self.SetHeatingEff(HeatingEqpSplit[1].replace(" (COP)",""))
        # elif "Air Source Heat Pump" in HeatingEqpSplit[0]:
        #     self.SetHeatingEff(HeatingEqpSplit[1].replace(" (HSPF)",""))
    
    def SetCoolingEqpChange(self):
        CoolingEqpSplit = self.ECMCoolingEquipment.currentText().split(" - ")
        for i,measure in enumerate(self.MeasureTypes["CoolingEqpOptions"]):
            if CoolingEqpSplit[0].replace(" ","") in measure.PropName:
                if float(CoolingEqpSplit[1].replace(" (SEER)","")) == float(measure.PropValue):
                    self.ECMMeasurePackage.PackageID["CoolingEqpOptions"] = i
                    break
        # self.SetCoolingEqp(CoolingEqpSplit[0])
        # self.SetCoolingEff(CoolingEqpSplit[1].replace(" (SEER)",""))

        
    #%%
    def SetEvaluateMeasures(self):
        PackageUtil = MeasurePackageUtilities(self.MeasureTypes)
        self.df_input = pd.read_pickle(os.path.join(self.ProjectPath,"BldgPropInputFile-Baseline.pkl"))
        self.ECMMeasurePackage = PackageUtil.CreateRunDirectory(self.ECMMeasurePackage,self.df_input,self.ProjectPath)
        PackageUtil.RunPackage(self.ECMMeasurePackage,self.CostData,self.df_weather)
        MeasureSumRes = PackageUtil.UpdatePackageResults(self.ECMMeasurePackage,self.BaselineSumRes)

        self.kWhPctChange.setText(str(round(MeasureSumRes["PctkWhChange"].iloc[0],2))+"%")
        self.ThermsPctChange.setText(str(round(MeasureSumRes["PctThermsChange"].iloc[0],2))+"%")
        self.TIC.setText(str(round(MeasureSumRes["TIC"].iloc[0],2)))
        self.LCC.setText(str(round(MeasureSumRes["LCC"].iloc[0],2)))
        # self.GetECMBaseline()

        df_MonthlyEndUse_EEM = pd.read_csv(os.path.join(self.ECMMeasurePackage.OutputDir, "MonthlyEndUseBreakdown.csv"))
        PltRes = PlotResults(True,self.ProjectPath)
        PltRes.PlotEEMEndUseComparison(self.ECMMeasurePackage.OutputDir,df_MonthlyEndUse_EEM) 
        self.ShowEEMResults()

    def ShowEEMResults(self):
        self.scenekWhEEMCompPlot = QGraphicsScene(self)
        self.kWhEEMCompPlot.setScene(self.scenekWhEEMCompPlot)
        imagePath = os.path.join(self.ECMMeasurePackage.OutputDir, "ElectricityMonthlyEEMComp.png")
        self.ShowGUIImage(self.scenekWhEEMCompPlot, self.kWhEEMCompPlot, imagePath)

        self.sceneThermEEMCompPlot = QGraphicsScene(self)
        self.ThermEEMCompPlot.setScene(self.sceneThermEEMCompPlot)
        imagePath = os.path.join(self.ECMMeasurePackage.OutputDir, "NaturalGasMonthlyEEMComp.png")
        self.ShowGUIImage(self.sceneThermEEMCompPlot, self.ThermEEMCompPlot, imagePath)

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
        errors = []
        for row in range(12):
            month_name = calendar.month_name[row + 1]
            for col in range(6):
                item = self.UtilityDataTable.item(row, col)
                text = item.text().strip() if item and item.text() else ""
                if not text:
                    col_names = ["Year 1 kWh", "Year 1 Therms", "Year 2 kWh", "Year 2 Therms", "Year 3 kWh", "Year 3 Therms"]
                    errors.append(f"Utility data: {month_name} - {col_names[col]} is blank.")
                else:
                    try:
                        float(text)
                    except ValueError:
                        errors.append(f"Utility data: {month_name} - column {col + 1} must be a number (got '{text}').")
        if errors:
            QMessageBox.critical(self, "Utility Data Error", "Please fill in all utility data cells with valid numbers:\n\n• " + "\n• ".join(errors[:15]) + ("\n..." if len(errors) > 15 else ""))
            return

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