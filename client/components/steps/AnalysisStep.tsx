"use client";

import React from "react";
import { useForm } from "@/context/FormContext";
import { StepLayout } from "@/components/StepLayout";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";

const API = "http://localhost:8000";

function plotUrl(projectName: string, filename: string): string {
  return `${API}/results/${encodeURIComponent(projectName)}/plot/${encodeURIComponent(filename)}`;
}

function PlaceholderChart({ label }: { label: string }) {
  return (
    <div className="h-56 rounded-lg border-2 border-dashed border-border flex flex-col items-center justify-center gap-2 bg-bg-muted">
      <svg viewBox="0 0 48 48" fill="none" className="w-10 h-10 text-app-text-light">
        <rect x="4"  y="28" width="8"  height="16" rx="2" fill="currentColor" opacity="0.4" />
        <rect x="14" y="20" width="8"  height="24" rx="2" fill="currentColor" opacity="0.6" />
        <rect x="24" y="10" width="8"  height="34" rx="2" fill="currentColor" opacity="0.8" />
        <rect x="34" y="16" width="8"  height="28" rx="2" fill="currentColor" opacity="0.5" />
      </svg>
      <p className="text-sm text-app-text-light font-medium">{label}</p>
      <p className="text-xs text-app-text-light">Run analysis to generate chart</p>
    </div>
  );
}

function LoadingChart({ label }: { label: string }) {
  return (
    <div className="h-56 rounded-lg border-2 border-brand-200 flex flex-col items-center justify-center gap-3 bg-brand-50">
      <svg className="w-8 h-8 text-brand-400 animate-spin" viewBox="0 0 24 24" fill="none">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
      </svg>
      <p className="text-sm text-brand-600 font-medium">{label}</p>
      <p className="text-xs text-brand-400">Analysis running…</p>
    </div>
  );
}

function PlotOrState({
  projectName,
  filename,
  label,
  isRunning,
}: {
  projectName: string;
  filename: string | null | undefined;
  label: string;
  isRunning: boolean;
}) {
  if (isRunning) return <LoadingChart label={label} />;
  if (!filename) return <PlaceholderChart label={label} />;
  return (
    <img
      src={plotUrl(projectName, filename)}
      alt={label}
      className="w-full h-auto rounded-lg border border-brand-100 object-contain bg-white"
    />
  );
}

// ── Analysis status banner ────────────────────────────────────────────────────
function AnalysisBanner() {
  const { analysisStatus, analysisError, pklProjectName } = useForm();

  if (analysisStatus === "running") {
    return (
      <div className="flex items-center gap-3 px-4 py-3 mb-4 rounded-lg bg-brand-50 border border-brand-200 text-sm text-brand-800">
        <svg className="w-4 h-4 animate-spin flex-shrink-0 text-brand-500" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
        </svg>
        Downloading weather data and running energy models for{" "}
        <span className="font-semibold">{pklProjectName}</span> — this may take up to a minute…
      </div>
    );
  }
  if (analysisStatus === "error") {
    return (
      <div className="flex items-start gap-2 px-3 py-2 mb-4 rounded-lg bg-red-50 border border-red-200 text-xs text-red-700">
        <span className="w-2 h-2 rounded-full bg-red-400 flex-shrink-0 mt-0.5" />
        <span><span className="font-semibold">Analysis error:</span> {analysisError}</span>
      </div>
    );
  }
  if (analysisStatus === "done") {
    return (
      <div className="flex items-center gap-2 px-3 py-2 mb-4 rounded-lg bg-brand-50 border border-brand-200 text-xs text-brand-800">
        <svg viewBox="0 0 16 16" fill="none" className="w-3.5 h-3.5 flex-shrink-0 text-brand-500">
          <path d="M3 8.5l3.5 3.5 6.5-7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        Analysis complete for <span className="font-semibold mx-1">{pklProjectName}</span>
      </div>
    );
  }
  return null;
}

// ── Step 11: Weather Data ─────────────────────────────────────────────────────
export function WeatherDataStep() {
  const { pklProjectName, analysisStatus, analysisPlots } = useForm();
  const isRunning = analysisStatus === "running";
  const isDone = analysisStatus === "done";

  return (
    <StepLayout>
      <Card>
        <SectionHeader
          title="Weather Data"
          description="Hourly weather data from the nearest NOAA station, automatically fetched when the PKL file is uploaded."
        />
        <AnalysisBanner />
        {isDone && analysisPlots?.weather ? (
          <img
            src={plotUrl(pklProjectName, analysisPlots.weather)}
            alt="Annual Temperature Profile"
            className="w-full h-auto rounded-lg border border-brand-100 object-contain bg-white"
          />
        ) : (
          <PlotOrState
            projectName={pklProjectName}
            filename={null}
            label="Annual Temperature Profile"
            isRunning={isRunning}
          />
        )}
      </Card>
    </StepLayout>
  );
}

// ── Step 12: Energy Models ────────────────────────────────────────────────────
export function EnergyModelsStep() {
  const { pklProjectName, analysisStatus, analysisPlots } = useForm();
  const isRunning = analysisStatus === "running";
  const isDone = analysisStatus === "done";

  return (
    <StepLayout>
      <Card>
        <SectionHeader
          title="Temperature-Based Change-Point Models"
          description="Electricity and fossil-fuel consumption as a function of outdoor temperature."
        />
        <AnalysisBanner />
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-semibold text-primary mb-2">Electricity (Cooling)</p>
            <PlotOrState
              projectName={pklProjectName}
              filename={isDone ? analysisPlots?.elec_temp_model : null}
              label="Electricity Temp-Based Model"
              isRunning={isRunning}
            />
          </div>
          <div>
            <p className="text-xs font-semibold text-primary mb-2">Fossil Fuel (Heating)</p>
            <PlotOrState
              projectName={pklProjectName}
              filename={isDone ? analysisPlots?.ff_temp_model : null}
              label="Fossil Fuel Temp-Based Model"
              isRunning={isRunning}
            />
          </div>
        </div>
      </Card>

      <Card>
        <SectionHeader
          title="Degree-Day Models"
          description="Heating and cooling energy correlated with HDD and CDD."
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-semibold text-primary mb-2">Heating Degree Days (Fossil Fuel)</p>
            <PlotOrState
              projectName={pklProjectName}
              filename={isDone ? analysisPlots?.ff_dd_model : null}
              label="HDD-Based Heating Model"
              isRunning={isRunning}
            />
          </div>
          <div>
            <p className="text-xs font-semibold text-primary mb-2">Cooling Degree Days (Electricity)</p>
            <PlotOrState
              projectName={pklProjectName}
              filename={isDone ? analysisPlots?.elec_dd_model : null}
              label="CDD-Based Cooling Model"
              isRunning={isRunning}
            />
          </div>
        </div>
      </Card>
    </StepLayout>
  );
}

// ── Step 13: Analysis Results ─────────────────────────────────────────────────
export function AnalysisResultsStep() {
  const { pklProjectName, analysisStatus, analysisPlots } = useForm();
  const isRunning = analysisStatus === "running";
  const isDone = analysisStatus === "done";

  return (
    <StepLayout nextLabel="Proceed to ECM Evaluation">
      <Card>
        <SectionHeader
          title="Annual End-Use Energy Breakdown"
          description="Estimated annual energy breakdown (kBtu) from the calibrated energy model."
        />
        <AnalysisBanner />
        <PlotOrState
          projectName={pklProjectName}
          filename={isDone ? analysisPlots?.end_use : null}
          label="End-Use Energy Breakdown"
          isRunning={isRunning}
        />
      </Card>

      <Card>
        <SectionHeader
          title="Monthly Model vs. Meter Comparison"
          description="Simulated energy by end use vs. metered utility data. Percentage error shown above each bar."
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-semibold text-primary mb-2">Electricity (kWh)</p>
            <PlotOrState
              projectName={pklProjectName}
              filename={isDone ? analysisPlots?.elec_monthly : null}
              label="Electricity Monthly Breakdown"
              isRunning={isRunning}
            />
          </div>
          <div>
            <p className="text-xs font-semibold text-primary mb-2">Natural Gas (Therms)</p>
            <PlotOrState
              projectName={pklProjectName}
              filename={isDone ? analysisPlots?.ng_monthly : null}
              label="Natural Gas Monthly Breakdown"
              isRunning={isRunning}
            />
          </div>
        </div>
      </Card>
    </StepLayout>
  );
}
