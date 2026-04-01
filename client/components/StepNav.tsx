"use client";

import React from "react";
import { useForm } from "@/context/FormContext";
import { SECTIONS, TOTAL_STEPS } from "@/types/form";
import type { SectionConfig } from "@/types/form";

export function StepNav() {
  const { currentStep, goToStep } = useForm();

  return (
    <nav className="w-64 flex-shrink-0 bg-bg-sidebar h-full flex flex-col py-4 overflow-y-auto">
      <div className="px-4 mb-6">
        <p className="text-xs font-semibold uppercase tracking-widest text-app-text-sidebar-inactive">
          Audit Steps
        </p>
      </div>

      <ol className="flex flex-col gap-1 px-2">
        {SECTIONS.map((section: SectionConfig) => {
          const isActive = currentStep >= section.firstStep && currentStep <= section.lastStep;
          const isCompleted = currentStep > section.lastStep;

          return (
            <li key={section.id}>
              <button
                type="button"
                onClick={() => goToStep(section.firstStep)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-colors duration-150 group
                  ${isActive
                    ? "bg-bg-sidebar-active text-app-text-white"
                    : "text-app-text-sidebar-inactive hover:bg-bg-sidebar-hover hover:text-app-text-white"
                  }`}
              >
                {/* Section indicator */}
                <span
                  className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold transition-colors
                    ${isActive
                      ? "bg-accent text-app-text-white"
                      : isCompleted
                      ? "bg-success text-app-text-white"
                      : "bg-bg-sidebar-hover text-app-text-sidebar-inactive group-hover:bg-bg-sidebar-active"
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

                <div className="min-w-0">
                  <p className={`text-sm font-medium leading-tight ${isActive ? "text-app-text-white" : ""}`}>
                    {section.label}
                  </p>
                </div>
              </button>
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
