"use client";
import React from "react";
import { useForm } from "@/context/FormContext";
import { SECTIONS, SUB_STEPS, TOTAL_STEPS } from "@/types/form";
import { Footer } from "@/components/Footer";

interface StepLayoutProps {
  children: React.ReactNode;
  imagePanel?: React.ReactNode;
  onNext?: () => void;
  onPrev?: () => void;
  nextLabel?: string;
  prevLabel?: string;
  nextDisabled?: boolean;
  rightAction?: React.ReactNode;
}

export function StepLayout({
  children,
  imagePanel,
  onNext,
  onPrev,
  nextLabel,
  prevLabel,
  nextDisabled = false,
  rightAction,
}: StepLayoutProps) {
  const { currentStep, nextStep, prevStep, goToStep, pklFileName, pklFieldCount } = useForm();

  const subStep = SUB_STEPS[currentStep - 1];
  const section = SECTIONS.find((s) => s.id === subStep?.section)!;
  const sectionTotalSubSteps = section.lastStep - section.firstStep + 1;
  const sectionSubSteps = SUB_STEPS.filter((s) => s.section === section.id);

  const isFirst = currentStep === 1;
  const isLast = currentStep === TOTAL_STEPS;

  const handleNext = onNext ?? nextStep;
  const handlePrev = onPrev ?? prevStep;

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center p-6 py-10">
      <div className="w-full max-w-7xl">
        <div
          className="bg-white rounded-3xl overflow-hidden flex"
          style={{ boxShadow: "0 8px 40px rgba(12,61,0,0.12)" }}
        >
          {/* Main content */}
          <div className="flex-1 flex flex-col p-10 min-h-[800px]">

            {/* Section progress bar */}
            <div className="flex items-start mb-10">
              {SECTIONS.map((sec, i) => {
                const isCompleted = currentStep > sec.lastStep;
                const isActive =
                  currentStep >= sec.firstStep && currentStep <= sec.lastStep;
                return (
                  <React.Fragment key={sec.id}>
                    <div className="flex flex-col items-center flex-shrink-0">
                      <button
                        type="button"
                        onClick={() => goToStep(sec.firstStep)}
                        className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold transition-all cursor-pointer ${
                          isCompleted
                            ? "bg-brand-500 text-white hover:bg-brand-600"
                            : isActive
                            ? "bg-primary text-white"
                            : "bg-brand-50 text-brand-700 border-2 border-brand-200 hover:border-brand-400 hover:bg-brand-100"
                        }`}
                      >
                        {isCompleted ? (
                          <svg viewBox="0 0 16 16" fill="none" className="w-4 h-4">
                            <path
                              d="M3 8.5l3.5 3.5 6.5-7"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />
                          </svg>
                        ) : (
                          sec.id
                        )}
                      </button>
                      <span
                        className={`text-xs mt-1.5 font-medium whitespace-nowrap ${
                          isActive ? "text-primary" : "text-app-text-muted"
                        }`}
                      >
                        {sec.shortLabel}
                      </span>
                    </div>
                    {i < SECTIONS.length - 1 && (
                      <div
                        className={`flex-1 h-0.5 mt-[18px] mx-1 ${
                          isCompleted ? "bg-brand-500" : "bg-brand-100"
                        }`}
                      />
                    )}
                  </React.Fragment>
                );
              })}
            </div>

            {/* PKL import banner */}
            {pklFileName && currentStep > 1 && (
              <div className="flex items-center gap-2 px-3 py-2 mb-4 rounded-lg bg-brand-50 border border-brand-200 text-xs text-brand-800">
                <svg viewBox="0 0 16 16" fill="none" className="w-3.5 h-3.5 flex-shrink-0 text-brand-500">
                  <path d="M8 1v9M5 7l3 3 3-3" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M2 11v2a1 1 0 001 1h10a1 1 0 001-1v-2" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
                </svg>
                <span>
                  <span className="font-semibold">{pklFieldCount} fields</span> auto-populated from{" "}
                  <span className="font-mono font-medium">{pklFileName}</span> — review and adjust as needed
                </span>
              </div>
            )}

            {/* Step title */}
            <div className="mb-4">
              <h1 className="text-2xl font-bold text-primary tracking-tight">{subStep?.label}</h1>
              {sectionTotalSubSteps === 1 && (
                <p className="text-sm text-app-text-muted mt-1">{section?.shortLabel}</p>
              )}
            </div>

            <div className="border-b border-brand-100 mb-5" />

            {/* Sub-step navigation — after divider, square pill buttons */}
            {sectionTotalSubSteps > 1 && (
              <div className="flex justify-center gap-2 mb-6">
                {sectionSubSteps.map((sub, i) => {
                  const isSubActive = currentStep === sub.id;
                  const isSubDone = currentStep > sub.id;
                  return (
                    <button
                      key={sub.id}
                      type="button"
                      onClick={() => goToStep(sub.id)}
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold transition-all border ${
                        isSubActive
                          ? "bg-primary text-white border-primary shadow-sm"
                          : isSubDone
                          ? "bg-brand-50 text-brand-700 border-brand-300 hover:bg-brand-100"
                          : "bg-white text-app-text-muted border-brand-100 hover:border-brand-300 hover:text-brand-700"
                      }`}
                    >
                      <span className={`w-4 h-4 rounded flex items-center justify-center text-[10px] font-bold flex-shrink-0 ${
                        isSubActive
                          ? "bg-white text-primary"
                          : isSubDone
                          ? "bg-brand-500 text-white"
                          : "bg-brand-100 text-brand-500"
                      }`}>
                        {isSubDone ? (
                          <svg viewBox="0 0 16 16" fill="none" className="w-2.5 h-2.5">
                            <path d="M3 8.5l3.5 3.5 6.5-7" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
                          </svg>
                        ) : (
                          i + 1
                        )}
                      </span>
                      {sub.label}
                    </button>
                  );
                })}
              </div>
            )}

            {/* Scrollable form content */}
            <div className="flex-1 overflow-y-auto pr-1 -mr-1">
              <div className="flex flex-col gap-5">{children}</div>
            </div>

            {/* Navigation */}
            <div className="flex items-center justify-between pt-6 mt-4 border-t border-brand-100">
              <button
                onClick={handlePrev}
                disabled={isFirst}
                className={`flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold transition-all ${
                  isFirst
                    ? "text-app-text-muted cursor-not-allowed bg-bg-muted border border-border"
                    : "text-primary bg-brand-50 hover:bg-brand-100 border border-brand-200"
                }`}
              >
                <svg viewBox="0 0 16 16" fill="none" className="w-4 h-4">
                  <path
                    d="M10 4l-4 4 4 4"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                {prevLabel ?? "Back"}
              </button>

              {rightAction ?? (
                <button
                  onClick={handleNext}
                  disabled={nextDisabled}
                  className={`flex items-center gap-2 px-8 py-3 rounded-xl text-sm font-semibold transition-all ${
                    nextDisabled
                      ? "bg-bg-muted text-app-text-muted cursor-not-allowed"
                      : "bg-brand-500 text-white hover:bg-brand-600 shadow-md hover:shadow-lg"
                  }`}
                >
                  {isLast ? (nextLabel ?? "Finish") : (nextLabel ?? "Next")}
                  <svg viewBox="0 0 16 16" fill="none" className="w-4 h-4">
                    <path
                      d="M6 4l4 4-4 4"
                      stroke="currentColor"
                      strokeWidth="1.8"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </button>
              )}
            </div>
          </div>

          {/* Right: image / preview panel */}
          {imagePanel && (
            <div className="w-[420px] xl:w-[500px] bg-brand-50 border-l border-brand-100 flex-shrink-0 flex flex-col p-8">
              {imagePanel}
            </div>
          )}
        </div>
        <Footer />
      </div>
    </div>
  );
}
