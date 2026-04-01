"use client";

import React, { createContext, useContext, useReducer, useCallback } from "react";
import { FormState, initialFormState, FormField, SECTIONS, TOTAL_STEPS } from "@/types/form";

interface FormContextValue {
  state: FormState;
  currentStep: number;
  currentSection: number;
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
  | { type: "SET_STEP"; step: number };

interface State {
  form: FormState;
  currentStep: number;
}

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "SET_FIELD":
      return { ...state, form: { ...state.form, [action.field]: action.value } };
    case "SET_FIELDS":
      return { ...state, form: { ...state.form, ...action.fields } };
    case "SET_STEP":
      return { ...state, currentStep: Math.max(1, Math.min(action.step, TOTAL_STEPS)) };
    default:
      return state;
  }
}

const FormContext = createContext<FormContextValue | null>(null);

export function FormProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(reducer, {
    form: initialFormState,
    currentStep: 1,
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
