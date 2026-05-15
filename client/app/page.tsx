"use client";

import React from "react";
import { FormProvider, useForm } from "@/context/FormContext";
import { ProjectSetupStep } from "@/components/steps/PreferencesStep";
import { ShapeOrientationStep, DimensionsStep } from "@/components/steps/GeometryStep";
import { WallsRoofStep, FoundationInfiltrationStep, WindowsShadingStep } from "@/components/steps/EnvelopeStep";
import { HeatingCoolingStep, HotWaterOtherStep } from "@/components/steps/HVACStep";
import { AppliancesStep, LightingPlugLoadsStep } from "@/components/steps/EquipmentStep";
import { AnalysisResultsStep } from "@/components/steps/AnalysisStep";
import { FinancialsStep, ECMSelectionStep, ECMOptionCostStep, ECMResultsStep } from "@/components/steps/ECMStep";

const STEP_COMPONENTS: Record<number, React.ComponentType> = {
  1:  ProjectSetupStep,
  2:  ShapeOrientationStep,
  3:  DimensionsStep,
  4:  WallsRoofStep,
  5:  FoundationInfiltrationStep,
  6:  WindowsShadingStep,
  7:  AppliancesStep,
  8:  LightingPlugLoadsStep,
  9:  HeatingCoolingStep,
  10: HotWaterOtherStep,
  11: AnalysisResultsStep,
  12: FinancialsStep,
  13: ECMSelectionStep,
  14: ECMOptionCostStep,
  15: ECMResultsStep,
};

function AppContent() {
  const { currentStep } = useForm();
  const StepComponent = STEP_COMPONENTS[currentStep] ?? ProjectSetupStep;
  return <StepComponent />;
}

export default function Home() {
  return (
    <FormProvider>
      <AppContent />
    </FormProvider>
  );
}
