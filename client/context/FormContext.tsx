"use client";

import React, { createContext, useContext, useReducer, useCallback } from "react";
import { FormState, initialFormState, FormField, SECTIONS, TOTAL_STEPS } from "@/types/form";

export interface UtilityRow {
  kwh1: string; therms1: string;
  kwh2: string; therms2: string;
  kwh3: string; therms3: string;
}

export interface UtilityData {
  year1: number;
  year2: number;
  year3: number;
  rows: UtilityRow[];
}

export interface EcmMetrics {
  tic: number;
  lcc: number;
  org_lcc: number;
  kwh_pct_savings: number;
  therms_pct_savings: number;
  org_kwh: number;
  eem_kwh: number;
  org_therms: number;
  eem_therms: number;
}

export interface EcmPlots {
  elec_monthly_comp: string | null;
  ng_monthly_comp: string | null;
}

export interface AnalysisPlots {
  weather: string | null;
  elec_temp_model: string | null;
  ff_temp_model: string | null;
  ff_dd_model: string | null;
  elec_dd_model: string | null;
  end_use: string | null;
  ng_monthly: string | null;
  elec_monthly: string | null;
}

interface FormContextValue {
  state: FormState;
  currentStep: number;
  currentSection: number;
  pklFileName: string;
  pklFieldCount: number;
  pklFields: string[];
  pklProjectName: string;
  utilFileName: string;
  analysisStatus: "idle" | "running" | "done" | "error";
  analysisPlots: AnalysisPlots | null;
  analysisWeatherStation: string;
  analysisError: string;
  utilityData: UtilityData | null;
  setUtilityData: (data: UtilityData) => void;
  setPklMeta: (fileName: string, fieldCount: number, projectName: string) => void;
  setPklFields: (fields: string[]) => void;
  setUtilUploaded: (fileName: string) => void;
  setAnalysisRunning: () => void;
  setAnalysisDone: (plots: AnalysisPlots, weatherStation: string) => void;
  setAnalysisError: (message: string) => void;
  ecmStatus: "idle" | "running" | "done" | "error";
  ecmMetrics: EcmMetrics | null;
  ecmPlots: EcmPlots | null;
  ecmError: string;
  setEcmRunning: () => void;
  setEcmDone: (metrics: EcmMetrics, plots: EcmPlots) => void;
  setEcmError: (message: string) => void;
  setField: (field: FormField, value: FormState[FormField]) => void;
  setFields: (fields: Partial<FormState>) => void;
  goToStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  totalSteps: number;
}

type Action =
  | { type: "SET_FIELD"; field: FormField; value: FormState[FormField] }
  | { type: "SET_FIELDS"; fields: Partial<FormState> }
  | { type: "SET_STEP"; step: number }
  | { type: "SET_PKL_META"; fileName: string; fieldCount: number; projectName: string }
  | { type: "SET_PKL_FIELDS"; fields: string[] }
  | { type: "SET_UTIL_UPLOADED"; fileName: string }
  | { type: "SET_UTILITY_DATA"; data: UtilityData }
  | { type: "SET_ANALYSIS_RUNNING" }
  | { type: "SET_ANALYSIS_DONE"; plots: AnalysisPlots; weatherStation: string }
  | { type: "SET_ANALYSIS_ERROR"; message: string }
  | { type: "SET_ECM_RUNNING" }
  | { type: "SET_ECM_DONE"; metrics: EcmMetrics; plots: EcmPlots }
  | { type: "SET_ECM_ERROR"; message: string };

interface State {
  form: FormState;
  currentStep: number;
  pklFileName: string;
  pklFieldCount: number;
  pklFields: string[];
  pklProjectName: string;
  utilFileName: string;
  utilityData: UtilityData | null;
  analysisStatus: "idle" | "running" | "done" | "error";
  analysisPlots: AnalysisPlots | null;
  analysisWeatherStation: string;
  analysisError: string;
  ecmStatus: "idle" | "running" | "done" | "error";
  ecmMetrics: EcmMetrics | null;
  ecmPlots: EcmPlots | null;
  ecmError: string;
}

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "SET_FIELD":
      return {
        ...state,
        form: { ...state.form, [action.field]: action.value },
        pklFields: state.pklFields.filter((f) => f !== action.field),
      };
    case "SET_FIELDS":
      return { ...state, form: { ...state.form, ...action.fields } };
    case "SET_STEP":
      return { ...state, currentStep: Math.max(1, Math.min(action.step, TOTAL_STEPS)) };
    case "SET_PKL_META":
      return {
        ...state,
        pklFileName: action.fileName,
        pklFieldCount: action.fieldCount,
        pklProjectName: action.projectName,
      };
    case "SET_PKL_FIELDS":
      return { ...state, pklFields: action.fields };
    case "SET_UTIL_UPLOADED":
      return { ...state, utilFileName: action.fileName };
    case "SET_UTILITY_DATA":
      return { ...state, utilityData: action.data };
    case "SET_ANALYSIS_RUNNING":
      return { ...state, analysisStatus: "running", analysisError: "" };
    case "SET_ANALYSIS_DONE":
      return { ...state, analysisStatus: "done", analysisPlots: action.plots, analysisWeatherStation: action.weatherStation, analysisError: "" };
    case "SET_ANALYSIS_ERROR":
      return { ...state, analysisStatus: "error", analysisError: action.message };
    case "SET_ECM_RUNNING":
      return { ...state, ecmStatus: "running", ecmError: "" };
    case "SET_ECM_DONE":
      return { ...state, ecmStatus: "done", ecmMetrics: action.metrics, ecmPlots: action.plots, ecmError: "" };
    case "SET_ECM_ERROR":
      return { ...state, ecmStatus: "error", ecmError: action.message };
    default:
      return state;
  }
}

const FormContext = createContext<FormContextValue | null>(null);

export function FormProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(reducer, {
    form: initialFormState,
    currentStep: 1,
    pklFileName: "",
    pklFieldCount: 0,
    pklFields: [],
    pklProjectName: "",
    utilFileName: "",
    utilityData: null,
    analysisStatus: "idle",
    analysisPlots: null,
    analysisWeatherStation: "",
    analysisError: "",
    ecmStatus: "idle",
    ecmMetrics: null,
    ecmPlots: null,
    ecmError: "",
  });

  const setField = useCallback(
    (field: FormField, value: FormState[FormField]) =>
      dispatch({ type: "SET_FIELD", field, value }),
    []
  );

  const setFields = useCallback(
    (fields: Partial<FormState>) => dispatch({ type: "SET_FIELDS", fields }),
    []
  );

  const goToStep = useCallback(
    (step: number) => dispatch({ type: "SET_STEP", step }),
    []
  );

  const nextStep = useCallback(
    () => dispatch({ type: "SET_STEP", step: state.currentStep + 1 }),
    [state.currentStep]
  );

  const prevStep = useCallback(
    () => dispatch({ type: "SET_STEP", step: state.currentStep - 1 }),
    [state.currentStep]
  );

  const setPklMeta = useCallback(
    (fileName: string, fieldCount: number, projectName: string) =>
      dispatch({ type: "SET_PKL_META", fileName, fieldCount, projectName }),
    []
  );

  const setPklFields = useCallback(
    (fields: string[]) => dispatch({ type: "SET_PKL_FIELDS", fields }),
    []
  );

  const setUtilUploaded = useCallback(
    (fileName: string) => dispatch({ type: "SET_UTIL_UPLOADED", fileName }),
    []
  );

  const setUtilityData = useCallback(
    (data: UtilityData) => dispatch({ type: "SET_UTILITY_DATA", data }),
    []
  );

  const setAnalysisRunning = useCallback(
    () => dispatch({ type: "SET_ANALYSIS_RUNNING" }),
    []
  );

  const setAnalysisDone = useCallback(
    (plots: AnalysisPlots, weatherStation: string) =>
      dispatch({ type: "SET_ANALYSIS_DONE", plots, weatherStation }),
    []
  );

  const setAnalysisError = useCallback(
    (message: string) => dispatch({ type: "SET_ANALYSIS_ERROR", message }),
    []
  );

  const setEcmRunning = useCallback(() => dispatch({ type: "SET_ECM_RUNNING" }), []);

  const setEcmDone = useCallback(
    (metrics: EcmMetrics, plots: EcmPlots) => dispatch({ type: "SET_ECM_DONE", metrics, plots }),
    []
  );

  const setEcmError = useCallback(
    (message: string) => dispatch({ type: "SET_ECM_ERROR", message }),
    []
  );

  const currentSection =
    SECTIONS.find(
      (s) => state.currentStep >= s.firstStep && state.currentStep <= s.lastStep
    )?.id ?? 1;

  return (
    <FormContext.Provider
      value={{
        state: state.form,
        currentStep: state.currentStep,
        currentSection,
        pklFileName: state.pklFileName,
        pklFieldCount: state.pklFieldCount,
        pklFields: state.pklFields,
        pklProjectName: state.pklProjectName,
        utilFileName: state.utilFileName,
        utilityData: state.utilityData,
        setUtilityData,
        analysisStatus: state.analysisStatus,
        analysisPlots: state.analysisPlots,
        analysisWeatherStation: state.analysisWeatherStation,
        analysisError: state.analysisError,
        setPklMeta,
        setPklFields,
        setUtilUploaded,
        setAnalysisRunning,
        setAnalysisDone,
        setAnalysisError,
        ecmStatus: state.ecmStatus,
        ecmMetrics: state.ecmMetrics,
        ecmPlots: state.ecmPlots,
        ecmError: state.ecmError,
        setEcmRunning,
        setEcmDone,
        setEcmError,
        setField,
        setFields,
        goToStep,
        nextStep,
        prevStep,
        totalSteps: TOTAL_STEPS,
      }}
    >
      {children}
    </FormContext.Provider>
  );
}

export function useForm() {
  const ctx = useContext(FormContext);
  if (!ctx) throw new Error("useForm must be used within FormProvider");
  return ctx;
}
