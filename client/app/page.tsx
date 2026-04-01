"use client";

import React from "react";
import { FormProvider, useForm } from "@/context/FormContext";
import { ProjectInfoStep, BuildingPropertiesStep, UtilityDataStep } from "@/components/steps/PreferencesStep";
import { FloorPlanShapeStep, OrientationStep, DimensionsStep, CornersStep } from "@/components/steps/GeometryStep";
import { ExtWallsStep, RoofCeilingStep, FoundationStep, InfiltrationStep, WindowsStep, ShadingStep } from "@/components/steps/EnvelopeStep";
import { CoolingStep, HeatingStep, DHWStep, OtherHVACStep } from "@/components/steps/HVACStep";
import { KitchenStep, LaundryStep, PlugLoadsStep, LightingStep } from "@/components/steps/EquipmentStep";
import { WeatherDataStep, TempAnalysisStep, DegreeDayStep, EndUseStep, ModelComparisonStep } from "@/components/steps/AnalysisStep";
import { FinancialParamsStep, ECMCostDataStep, ECMSelectionStep, ECMResultsStep } from "@/components/steps/ECMStep";

const STEP_COMPONENTS: Record<number, React.ComponentType> = {
  1:  ProjectInfoStep,
  2:  BuildingPropertiesStep,
  3:  UtilityDataStep,
  4:  FloorPlanShapeStep,
  5:  OrientationStep,
  6:  DimensionsStep,
  7:  CornersStep,
  8:  ExtWallsStep,
  9:  RoofCeilingStep,
  10: FoundationStep,
  11: InfiltrationStep,
  12: WindowsStep,
  13: ShadingStep,
  14: CoolingStep,
  15: HeatingStep,
  16: DHWStep,
  17: OtherHVACStep,
  18: KitchenStep,
  19: LaundryStep,
  20: PlugLoadsStep,
  21: LightingStep,
  22: WeatherDataStep,
  23: TempAnalysisStep,
  24: DegreeDayStep,
  25: EndUseStep,
  26: ModelComparisonStep,
  27: FinancialParamsStep,
  28: ECMCostDataStep,
  29: ECMSelectionStep,
  30: ECMResultsStep,
};

function AppContent() {
  const { currentStep } = useForm();
  const StepComponent = STEP_COMPONENTS[currentStep] ?? ProjectInfoStep;
  return <StepComponent />;
}

export default function Home() {
  return (
    <FormProvider>
      <AppContent />
    </FormProvider>
  );
}
