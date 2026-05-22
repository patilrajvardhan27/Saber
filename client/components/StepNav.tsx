"use client";

import React from "react";
import { useForm } from "@/context/FormContext";
import { SECTIONS, SUB_STEPS, TOTAL_STEPS } from "@/types/form";
import type { SectionConfig, SubStepConfig } from "@/types/form";

export function StepNav() {
  const { currentStep, goToStep } = useForm();

  return (
    <nav className="w-64 flex-shrink-0 bg-bg-sidebar h-full flex flex-col py-4 overflow-y-auto">
      <div className="px-4 mb-6">
        <p className="text-xs font-semibold uppercase tracking-widest text-app-text-sidebar-inactive">
          Audit Steps
        </p>
      </div>

      <ol className="flex flex-col px-2">
        {SECTIONS.map((section: SectionConfig) => {
          const isActive = currentStep >= section.firstStep && currentStep <= section.lastStep;
          const isCompleted = currentStep > section.lastStep;
          const sectionSubSteps = SUB_STEPS.filter((s: SubStepConfig) => s.section === section.id);
          const hasMultipleSubSteps = sectionSubSteps.length > 1;

          return (
            <li key={section.id}>
              {/* Section header row */}
              <button
                type="button"
                onClick={() => goToStep(section.firstStep)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-colors duration-150 group
                  ${isActive
                    ? "bg-bg-sidebar-active"
                    : "hover:bg-bg-sidebar-hover"
                  }`}
              >
                <span
                  className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold transition-colors
                    ${isActive
                      ? "bg-accent text-app-text-white"
                      : isCompleted
                      ? "bg-success text-app-text-white"
                      : "bg-bg-sidebar-hover text-app-text-sidebar-inactive group-hover:bg-bg-sidebar-active group-hover:text-app-text-white"
                    }`}
                >
                  {isCompleted ? (
                    <svg viewBox="0 0 16 16" fill="none" className="w-3.5 h-3.5">
                      <path d="M3 8l4 4 6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  ) : (
                    section.id
                  )}
                </span>
                <span className={`text-sm font-semibold leading-tight flex-1 min-w-0
                  ${isActive ? "text-app-text-white" : isCompleted ? "text-app-text-sidebar-inactive" : "text-app-text-sidebar-inactive group-hover:text-app-text-white"}`}
                >
                  {section.label}
                </span>
              </button>

              {/* Sub-step rows — styled like main steps, always visible when section has multiple */}
              {hasMultipleSubSteps && (
                <ol className="mt-0.5 mb-1.5 ml-3 pl-3 border-l-2 border-bg-sidebar-hover flex flex-col gap-0.5">
                  {sectionSubSteps.map((sub: SubStepConfig, idx: number) => {
                    const isSubActive = currentStep === sub.id;
                    const isSubDone = currentStep > sub.id;

                    return (
                      <li key={sub.id}>
                        <button
                          type="button"
                          onClick={() => goToStep(sub.id)}
                          className={`w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-left transition-colors duration-150 group/sub
                            ${isSubActive
                              ? "bg-bg-sidebar-hover"
                              : "hover:bg-bg-sidebar-hover"
                            }`}
                        >
                          {/* Sub-step badge — square/rounded to distinguish from section circles */}
                          <span
                            className={`w-5 h-5 rounded flex items-center justify-center flex-shrink-0 text-xs font-bold transition-colors
                              ${isSubActive
                                ? "bg-accent text-app-text-white"
                                : isSubDone
                                ? "bg-success text-app-text-white"
                                : "bg-bg-sidebar-hover text-app-text-sidebar-inactive group-hover/sub:bg-bg-sidebar-active group-hover/sub:text-app-text-white"
                              }`}
                          >
                            {isSubDone ? (
                              <svg viewBox="0 0 16 16" fill="none" className="w-3 h-3">
                                <path d="M3 8l4 4 6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                              </svg>
                            ) : (
                              idx + 1
                            )}
                          </span>
                          <span className={`text-xs font-medium leading-tight flex-1 min-w-0
                            ${isSubActive
                              ? "text-app-text-white"
                              : isSubDone
                              ? "text-app-text-sidebar-inactive"
                              : "text-app-text-sidebar-inactive group-hover/sub:text-app-text-white"
                            }`}
                          >
                            {sub.label}
                          </span>
                        </button>
                      </li>
                    );
                  })}
                </ol>
              )}
            </li>
          );
        })}
      </ol>

      {/* Progress bar at bottom */}
      <div className="mt-auto px-4 pb-2">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-xs text-app-text-sidebar-inactive">Progress</span>
          <span className="text-xs text-app-text-sidebar-inactive font-medium">
            {currentStep}/{TOTAL_STEPS}
          </span>
        </div>
        <div className="h-1.5 bg-bg-sidebar-hover rounded-full overflow-hidden">
          <div
            className="h-full bg-accent rounded-full transition-all duration-300"
            style={{ width: `${((currentStep - 1) / (TOTAL_STEPS - 1)) * 100}%` }}
          />
        </div>
      </div>
    </nav>
  );
}
