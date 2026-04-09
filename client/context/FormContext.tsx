"use client";

import React, { createContext, useContext, useReducer, useCallback } from "react";
import { FormState, initialFormState, FormField, SECTIONS, TOTAL_STEPS } from "@/types/form";

interface FormContextValue {
  state: FormState;
  currentStep: number;
  currentSection: number;
  pklFileName: string;
  pklFieldCount: number;
  pklFields: string[];
  setPklMeta: (fileName: string, fieldCount: number) => void;
  setPklFields: (fields: string[]) => void;
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
  | { type: "SET_PKL_META"; fileName: string; fieldCount: number }
  | { type: "SET_PKL_FIELDS"; fields: string[] };

interface State {
  form: FormState;
  currentStep: number;
  pklFileName: string;
  pklFieldCount: number;
  pklFields: string[];
}

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "SET_FIELD":
      return {
        ...state,
        form: { ...state.form, [action.field]: action.value },
        // Remove from autofill set when user manually edits
        pklFields: state.pklFields.filter((f) => f !== action.field),
      };
    case "SET_FIELDS":
      return { ...state, form: { ...state.form, ...action.fields } };
    case "SET_STEP":
      return { ...state, currentStep: Math.max(1, Math.min(action.step, TOTAL_STEPS)) };
    case "SET_PKL_META":
      return { ...state, pklFileName: action.fileName, pklFieldCount: action.fieldCount };
    case "SET_PKL_FIELDS":
      return { ...state, pklFields: action.fields };
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
    (fileName: string, fieldCount: number) =>
      dispatch({ type: "SET_PKL_META", fileName, fieldCount }),
    []
  );

  const setPklFields = useCallback(
    (fields: string[]) => dispatch({ type: "SET_PKL_FIELDS", fields }),
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
        setPklMeta,
        setPklFields,
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
