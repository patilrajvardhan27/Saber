"use client";
import React from "react";
import { useForm } from "@/context/FormContext";
import { SECTIONS, SUB_STEPS, TOTAL_STEPS } from "@/types/form";

interface StepLayoutProps {
  children: React.ReactNode;
  imagePanel?: React.ReactNode;
  onNext?: () => void;
  onPrev?: () => void;
  nextLabel?: string;
  prevLabel?: string;
  nextDisabled?: boolean;
}

export function StepLayout({
  children,
  imagePanel,
  onNext,
  onPrev,
  nextLabel,
  prevLabel,
  nextDisabled = false,
}: StepLayoutProps) {
  const { currentStep, nextStep, prevStep } = useForm();

  const subStep = SUB_STEPS[currentStep - 1];
  const section = SECTIONS.find((s) => s.id === subStep?.section)!;
  const sectionSubStepIndex = currentStep - section.firstStep + 1;
  const sectionTotalSubSteps = section.lastStep - section.firstStep + 1;

  const isFirst = currentStep === 1;
  const isLast = currentStep === TOTAL_STEPS;

  const handleNext = onNext ?? nextStep;
  const handlePrev = onPrev ?? prevStep;

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-6 py-10">
      <div className="w-full max-w-5xl">
        <div
          className="bg-white rounded-3xl overflow-hidden flex"
          style={{ boxShadow: "0 8px 40px rgba(0,0,0,0.12)" }}
        >
          {/* Left: form content */}
          <div className="flex-1 flex flex-col p-10 min-h-[640px]">
            {/* Section progress bar — 7 circles */}
            <div className="flex items-start mb-10">
              {SECTIONS.map((sec, i) => {
                const isCompleted = currentStep > sec.lastStep;
                const isActive =
                  currentStep >= sec.firstStep && currentStep <= sec.lastStep;
                return (
                  <React.Fragment key={sec.id}>
                    <div className="flex flex-col items-center flex-shrink-0">
                      <div
                        className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold transition-all ${
                          isCompleted
                            ? "bg-teal-500 text-white"
                            : isActive
                            ? "bg-teal-500 text-white"
                            : "bg-gray-100 text-gray-400 border-2 border-gray-200"
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
                      </div>
                      <span
                        className={`text-xs mt-1.5 font-medium whitespace-nowrap ${
                          isActive ? "text-teal-600" : "text-gray-400"
                        }`}
                      >
                        {sec.shortLabel}
                      </span>
                    </div>
                    {i < SECTIONS.length - 1 && (
                      <div
                        className={`flex-1 h-0.5 mt-[18px] mx-1 ${
                          isCompleted ? "bg-teal-500" : "bg-gray-200"
                        }`}
                      />
                    )}
                  </React.Fragment>
                );
              })}
            </div>

            {/* Step title + sub-step indicator */}
            <div className="mb-3">
              <h1 className="text-2xl font-bold text-gray-800">{subStep?.label}</h1>
              <p className="text-sm text-gray-400 mt-1">
                {section?.shortLabel} · {sectionSubStepIndex} of {sectionTotalSubSteps}
              </p>
            </div>
            <div className="border-b border-gray-100 mb-6" />

            {/* Scrollable form content */}
            <div className="flex-1 overflow-y-auto pr-1 -mr-1">{children}</div>

            {/* Navigation */}
            <div className="flex items-center justify-between pt-6 mt-4 border-t border-gray-100">
              <button
                onClick={handlePrev}
                disabled={isFirst}
                className={`flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold transition-all ${
                  isFirst
                    ? "text-gray-300 cursor-not-allowed bg-gray-50 border border-gray-100"
                    : "text-gray-600 bg-gray-100 hover:bg-gray-200 border border-transparent"
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

              <button
                onClick={handleNext}
                disabled={nextDisabled}
                className={`flex items-center gap-2 px-8 py-3 rounded-xl text-sm font-semibold transition-all ${
                  nextDisabled
                    ? "bg-gray-100 text-gray-300 cursor-not-allowed"
                    : "bg-teal-500 text-white hover:bg-teal-600 shadow-md hover:shadow-lg"
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
            </div>
          </div>

          {/* Right: image / preview panel */}
          {imagePanel && (
            <div className="w-80 xl:w-96 bg-gray-100 flex-shrink-0 flex items-center justify-center p-8">
              {imagePanel}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
