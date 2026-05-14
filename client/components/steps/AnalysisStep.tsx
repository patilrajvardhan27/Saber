"use client";

import React from "react";
import { useForm } from "@/context/FormContext";
import type { AnalysisPlots } from "@/context/FormContext";
import { StepLayout } from "@/components/StepLayout";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { API } from "@/utils/api";

// Fixed-size image box — all charts render inside this consistent container
function ChartBox({ children }: { children: React.ReactNode }) {
  return (
    <div className="w-full h-64 rounded-lg border border-brand-100 bg-white overflow-hidden flex items-center justify-center">
      {children}
    </div>
  );
}

function LoadingChart({ label }: { label: string }) {
  return (
    <ChartBox>
      <div className="flex flex-col items-center justify-center gap-3 text-brand-600">
        <svg className="w-8 h-8 text-brand-400 animate-spin" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
        </svg>
        <p className="text-sm font-medium">{label}</p>
        <p className="text-xs text-brand-400">Analysis running…</p>
      </div>
    </ChartBox>
  );
}

function PlotOrState({
  filename,
  label,
  isRunning,
}: {
  filename: string | null | undefined;
  label: string;
  isRunning: boolean;
}) {
  if (isRunning) return <LoadingChart label={label} />;
  if (!filename) return null;
  return (
    <ChartBox>
      <img
        src={filename}
        alt={label}
        className="w-full h-full object-contain"
      />
    </ChartBox>
  );
}

// ── Generate Result section (always shown on results page) ───────────────────
function GenerateResultSection() {
  const {
    state, pklProjectName,
    setAnalysisRunning, setAnalysisDone, setAnalysisError,
    analysisStatus, setPklMeta,
  } = useForm();

  const manualName = state.projectName.trim();
  const effectiveProject = pklProjectName || manualName;
  const canGenerate = !!effectiveProject && analysisStatus !== "running";

  async function handleGenerate() {
    if (!canGenerate) return;
    setPklMeta(pklProjectName ? pklProjectName : "", 0, effectiveProject);
    setAnalysisRunning();
    try {
      const res = await fetch(`${API}/run-analysis-manual/${encodeURIComponent(effectiveProject)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ form_data: state }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(err.detail ?? "Analysis failed");
      }
      const data = await res.json();
      setPklMeta(pklProjectName ? pklProjectName : "", 0, data.project_name ?? effectiveProject);
      setAnalysisDone(data.plots as AnalysisPlots, data.weather_station ?? "");
    } catch (err: unknown) {
      setAnalysisError(err instanceof Error ? err.message : "Analysis failed");
    }
  }

  return (
    <Card>
      <SectionHeader
        title="Generate Result"
        description="Run the energy analysis using current field values — works whether inputs were loaded from a PKL file or entered manually."
      />
      <div className="space-y-4">
        {!effectiveProject && (
          <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
            Set a project name on Step 1 before generating results.
          </p>
        )}
        <button
          type="button"
          onClick={handleGenerate}
          disabled={!canGenerate}
          className={`w-full flex items-center justify-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold transition-all ${
            canGenerate
              ? "bg-brand-500 text-white hover:bg-brand-600 shadow-md hover:shadow-lg"
              : "bg-bg-muted text-app-text-muted cursor-not-allowed"
          }`}
        >
          {analysisStatus === "running" ? (
            <>
              <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
              </svg>
              Running Analysis…
            </>
          ) : (
            <>
              <svg viewBox="0 0 24 24" fill="none" className="w-4 h-4">
                <path d="M5 3l14 9-14 9V3z" fill="currentColor" />
              </svg>
              Generate Result
            </>
          )}
        </button>
      </div>
    </Card>
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

// ── Combined Results Step ─────────────────────────────────────────────────────
export function AnalysisResultsStep() {
  const { pklProjectName, analysisStatus, analysisPlots, analysisWeatherStation } = useForm();
  const isRunning = analysisStatus === "running";
  const isDone = analysisStatus === "done";

  return (
    <StepLayout nextLabel="Proceed to Retrofit Analysis">
      <GenerateResultSection />
      <AnalysisBanner />

      {/* Weather Data */}
      {(isRunning || analysisPlots?.weather) && (
        <Card>
          <SectionHeader
            title="Weather Data"
            description={
              analysisWeatherStation
                ? `NOAA weather station: ${analysisWeatherStation} — hourly data used for all energy calculations.`
                : "Location field is used to find the nearest NOAA weather station. The station name appears here after analysis runs."
            }
          />
          <PlotOrState
            filename={isDone ? analysisPlots?.weather : null}
            label="Annual Temperature Profile"
            isRunning={isRunning}
          />
        </Card>
      )}

      {/* Temperature-Based Change-Point Models */}
      {(isRunning || analysisPlots?.elec_temp_model || analysisPlots?.ff_temp_model) && (
        <Card>
          <SectionHeader
            title="Temperature-Based Change-Point Models"
            description="Electricity and fossil-fuel consumption as a function of outdoor temperature."
          />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {(isRunning || analysisPlots?.elec_temp_model) && (
              <div>
                <p className="text-xs font-semibold text-primary mb-2">Electricity (Cooling)</p>
                <PlotOrState
                  filename={isDone ? analysisPlots?.elec_temp_model : null}
                  label="Electricity Temp-Based Model"
                  isRunning={isRunning}
                />
              </div>
            )}
            {(isRunning || analysisPlots?.ff_temp_model) && (
              <div>
                <p className="text-xs font-semibold text-primary mb-2">Fossil Fuel (Heating)</p>
                <PlotOrState
                  filename={isDone ? analysisPlots?.ff_temp_model : null}
                  label="Fossil Fuel Temp-Based Model"
                  isRunning={isRunning}
                />
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Degree-Day Models */}
      {(isRunning || analysisPlots?.ff_dd_model || analysisPlots?.elec_dd_model) && (
        <Card>
          <SectionHeader
            title="Degree-Day Models"
            description="Heating and cooling energy correlated with HDD and CDD."
          />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {(isRunning || analysisPlots?.ff_dd_model) && (
              <div>
                <p className="text-xs font-semibold text-primary mb-2">Heating Degree Days (Fossil Fuel)</p>
                <PlotOrState
                  filename={isDone ? analysisPlots?.ff_dd_model : null}
                  label="HDD-Based Heating Model"
                  isRunning={isRunning}
                />
              </div>
            )}
            {(isRunning || analysisPlots?.elec_dd_model) && (
              <div>
                <p className="text-xs font-semibold text-primary mb-2">Cooling Degree Days (Electricity)</p>
                <PlotOrState
                  filename={isDone ? analysisPlots?.elec_dd_model : null}
                  label="CDD-Based Cooling Model"
                  isRunning={isRunning}
                />
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Annual End-Use Breakdown */}
      {(isRunning || analysisPlots?.end_use) && (
        <Card>
          <SectionHeader
            title="Annual End-Use Energy Breakdown"
            description="Estimated annual energy breakdown (kBtu) from the calibrated energy model."
          />
          <PlotOrState
            filename={isDone ? analysisPlots?.end_use : null}
            label="End-Use Energy Breakdown"
            isRunning={isRunning}
          />
        </Card>
      )}

      {/* Monthly Model vs. Meter */}
      {(isRunning || analysisPlots?.elec_monthly || analysisPlots?.ng_monthly) && (
        <Card>
          <SectionHeader
            title="Monthly Model vs. Meter Comparison"
            description="Simulated energy by end use vs. metered utility data. Percentage error shown above each bar."
          />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {(isRunning || analysisPlots?.elec_monthly) && (
              <div>
                <p className="text-xs font-semibold text-primary mb-2">Electricity (kWh)</p>
                <PlotOrState
                  filename={isDone ? analysisPlots?.elec_monthly : null}
                  label="Electricity Monthly Breakdown"
                  isRunning={isRunning}
                />
              </div>
            )}
            {(isRunning || analysisPlots?.ng_monthly) && (
              <div>
                <p className="text-xs font-semibold text-primary mb-2">Natural Gas (Therms)</p>
                <PlotOrState
                  filename={isDone ? analysisPlots?.ng_monthly : null}
                  label="Natural Gas Monthly Breakdown"
                  isRunning={isRunning}
                />
              </div>
            )}
          </div>
        </Card>
      )}
    </StepLayout>
  );
}
