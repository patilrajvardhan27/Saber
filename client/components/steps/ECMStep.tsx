"use client";

import React from "react";
import { useForm } from "@/context/FormContext";
import type { EcmMetrics, EcmPlots, EcmMeasureRow } from "@/context/FormContext";
import { StepLayout } from "@/components/StepLayout";
import { FormField } from "@/components/ui/FormField";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import {
  ECM_MEASURES, ECM_MEASURE_OPTIONS, COOLING_EFF_OPTIONS, HEATING_EFF_OPTIONS,
  WALL_INSULATIONS, CEILING_INSULATIONS, WINDOW_MATERIALS,
} from "@/data/options";
import type { FormField as FormFieldType, FormState } from "@/types/form";

// A retrofit option should only be offered when it actually improves on the building's
// current value. The analysis engine can't reliably filter numeric options, so the UI
// hides non-improvements (e.g. a higher ACH50 than baseline, which is leakier, not better).
function upgradeOptions(key: string, options: string[], state: FormState): string[] {
  const afterInList = (list: string[], baseline: string) => {
    const bi = list.indexOf(baseline);
    return bi < 0 ? options : options.filter((o) => list.indexOf(o) > bi);
  };
  const greaterThan = (baseline: string) => {
    const b = parseFloat(baseline);
    return Number.isNaN(b) ? options : options.filter((o) => parseFloat(o) > b);
  };
  const lessThan = (baseline: string) => {
    const b = parseFloat(baseline);
    return Number.isNaN(b) ? options : options.filter((o) => parseFloat(o) < b);
  };
  switch (key) {
    case "ecmWallInsulation":    return afterInList(WALL_INSULATIONS, state.wallInsulation);
    case "ecmCeilingInsulation": return afterInList(CEILING_INSULATIONS, state.ceilingInsulation);
    case "ecmWindowMaterial":    return afterInList(WINDOW_MATERIALS, state.windowMaterial?.[0] ?? "");
    case "ecmInfiltration":      return lessThan(state.ach50);                 // lower ACH50 is tighter
    case "ecmLED":               return greaterThan(state.led || "0");         // more LEDs is better
    case "ecmNightSetback":      return greaterThan(state.nightSetback || "0");
    case "ecmNightSetbackHours": return greaterThan(state.nNightSetbackHours || "0");
    case "ecmReduceEquipLoad":   return greaterThan("0");                      // baseline is always 0%
    default:                     return options;
  }
}
import { ExportDropdown } from "@/components/ExportDropdown";
import { API } from "@/utils/api";


// ── Step 14: Financials & Costs ───────────────────────────────────────────────
export function FinancialsStep() {
  const { state, setField } = useForm();
  return (
    <StepLayout>
      <Card>
        <SectionHeader
          title="Financial Parameters"
          description="Set utility rates and analysis parameters used for life-cycle cost calculations."
        />
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <FormField label="Cost per Therm" hint="$/therm">
            <Input
              type="number"
              placeholder="1.20"
              unit="$/therm"
              value={state.thermCost}
              onChange={(e) => setField("thermCost", e.target.value)}
            />
          </FormField>
          <FormField label="Cost per kWh" hint="$/kWh">
            <Input
              type="number"
              placeholder="0.12"
              unit="$/kWh"
              value={state.kWhCost}
              onChange={(e) => setField("kWhCost", e.target.value)}
            />
          </FormField>
          <FormField label="Discount Rate" hint="Annual discount rate">
            <Input
              type="number"
              placeholder="3.0"
              unit="%"
              value={state.discountRate}
              onChange={(e) => setField("discountRate", e.target.value)}
            />
          </FormField>
          <FormField label="Measure Lifetime" hint="Analysis period in years">
            <Input
              type="number"
              placeholder="20"
              unit="yrs"
              value={state.lifetime}
              onChange={(e) => setField("lifetime", e.target.value)}
            />
          </FormField>
        </div>
      </Card>
    </StepLayout>
  );
}

// ── Step 15: ECM Selection ────────────────────────────────────────────────────
const ECM_FIELD_KEYS = ECM_MEASURES.map((m) => m.key) as import("@/types/form").FormField[];

export function ECMSelectionStep() {
  const {
    state, setField, setFields,
    pklProjectName,
    ecmStatus, ecmError,
    setEcmRunning, setEcmDone, setEcmError,
    goToStep,
  } = useForm();

  const isRunning = ecmStatus === "running";

  function resetSelections() {
    const cleared = Object.fromEntries(ECM_FIELD_KEYS.map((k) => [k, ""]));
    setFields(cleared);
  }

  // Baseline display value for each ECM key
  const baselineMap: Record<string, string> = {
    ecmWallInsulation:    state.wallInsulation   || "—",
    ecmInfiltration:      state.ach50            || "—",
    ecmCeilingInsulation: state.ceilingInsulation|| "—",
    ecmWindowMaterial:    state.windowMaterial?.[0] || "—",
    ecmNightSetback:      state.nightSetback      || "—",
    ecmNightSetbackHours: state.nNightSetbackHours|| "—",
    ecmDaylighting:       state.daylighting       || "No",
    ecmEconomizer:        state.economizer        || "No",
    ecmOccupancySensor:   "No",
    ecmLED:               state.led               || "0",
    ecmReduceEquipLoad:   "0%",
    ecmCoolingEff:        state.coolingEff        || "—",
    ecmHeatingEqp:        state.heatingEqp        || "—",
    ecmHeatingEff:        state.heatingEff        || "—",
  };

  async function evaluatePackage() {
    if (!pklProjectName || isRunning) return;
    setEcmRunning();

    const body = {
      ecm_wall_insulation:    state.ecmWallInsulation    || "",
      ecm_infiltration:       state.ecmInfiltration      || "",
      ecm_ceiling_insulation: state.ecmCeilingInsulation || "",
      ecm_window_material:    state.ecmWindowMaterial    || "",
      ecm_occupancy_sensor:   state.ecmOccupancySensor   || "No",
      ecm_led:                state.ecmLED               || "",
      ecm_daylighting:        state.ecmDaylighting        || "No",
      ecm_economizer:         state.ecmEconomizer         || "No",
      ecm_cooling_eff:        state.ecmCoolingEff         || "",
      ecm_heating_eff:        state.ecmHeatingEff         || "",
      kwh_rate:    parseFloat(state.kWhCost)    || 0.12,
      therm_rate:  parseFloat(state.thermCost)  || 1.20,
      discount_rate: parseFloat(state.discountRate) || 3.0,
      lifetime:    parseInt(state.lifetime)     || 20,
      form_data:   state,
    };

    try {
      const res = await fetch(`${API}/run-ecm/${encodeURIComponent(pklProjectName)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(err.detail ?? "ECM evaluation failed");
      }
      const data = await res.json();
      setEcmDone(data.metrics as EcmMetrics, data.plots as EcmPlots, (data.measures ?? []) as EcmMeasureRow[]);
      setTimeout(() => goToStep(14), 800);
    } catch (err: unknown) {
      setEcmError(err instanceof Error ? err.message : "ECM evaluation failed");
    }
  }

  return (
    <StepLayout>
      <Card>
        <div className="flex items-start justify-between gap-4 mb-4">
          <SectionHeader
            title="Retrofit Analysis"
            description="Select the upgraded option for each measure, then evaluate the full package."
            className="mb-0"
          />
          <div className="flex items-center gap-2 flex-shrink-0">
            <button
              type="button"
              onClick={resetSelections}
              disabled={isRunning}
              title="Clear all ECM selections"
              className={`flex items-center gap-1.5 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all border ${
                isRunning
                  ? "bg-bg-muted text-app-text-muted cursor-not-allowed border-border"
                  : "bg-white text-app-text border-border hover:border-red-300 hover:text-red-600 hover:bg-red-50"
              }`}
            >
              <svg viewBox="0 0 16 16" fill="none" className="w-3.5 h-3.5">
                <path d="M2 4h12M5 4V2.5a.5.5 0 01.5-.5h5a.5.5 0 01.5.5V4M6 7v4M10 7v4M3 4l.8 8.5a.5.5 0 00.5.5h7.4a.5.5 0 00.5-.5L13 4"
                  stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              Reset
            </button>
            <button
              type="button"
              onClick={evaluatePackage}
              disabled={!pklProjectName || isRunning}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                !pklProjectName || isRunning
                  ? "bg-bg-muted text-app-text-muted cursor-not-allowed border border-border"
                  : "bg-brand-500 text-white hover:bg-brand-600 shadow-sm"
              }`}
            >
              {isRunning ? (
                <>
                  <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                  </svg>
                  Evaluating…
                </>
              ) : "Evaluate Package"}
            </button>
          </div>
        </div>

        {ecmStatus === "error" && (
          <div className="flex items-start gap-2 px-3 py-2 mb-3 rounded-lg bg-red-50 border border-red-200 text-xs text-red-700">
            <span className="w-2 h-2 rounded-full bg-red-400 flex-shrink-0 mt-0.5" />
            <span><span className="font-semibold">Error:</span> {ecmError}</span>
          </div>
        )}

        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg-muted border-b border-border">
                <th className="text-left px-4 py-2.5 font-semibold text-app-text text-xs w-52">Measure</th>
                <th className="text-left px-4 py-2.5 font-semibold text-app-text text-xs">Baseline</th>
                <th className="text-left px-4 py-2.5 font-semibold text-app-text text-xs">ECM Option</th>
              </tr>
            </thead>
            <tbody>
              {ECM_MEASURES.map((measure, i) => {
                // Cooling/heating efficiency options depend on the building's installed
                // equipment so the values always match the backend's measure database.
                let options = ECM_MEASURE_OPTIONS[measure.key] ?? [];
                if (measure.key === "ecmCoolingEff") {
                  options = (COOLING_EFF_OPTIONS[state.coolingEqp] ?? []).filter((o) => o !== "Other..");
                } else if (measure.key === "ecmHeatingEff") {
                  options = (HEATING_EFF_OPTIONS[state.heatingEqp] ?? []).filter((o) => o !== "Other..");
                } else {
                  // Only offer options that improve on the building's current value.
                  options = upgradeOptions(measure.key, options, state);
                }
                return (
                  <tr key={measure.key} className={i % 2 === 0 ? "bg-bg-card" : "bg-bg-muted"}>
                    <td className="px-4 py-2 font-medium text-app-text text-xs">{measure.label}</td>
                    <td className="px-4 py-2 text-xs text-app-text-muted font-mono">
                      {baselineMap[measure.key]}
                    </td>
                    <td className="px-4 py-1.5">
                      <Select
                        options={options}
                        placeholder="No change"
                        value={(state as unknown as Record<string, string>)[measure.key] ?? ""}
                        onChange={(e) => setField(measure.key as FormFieldType, e.target.value)}
                        className="!text-xs !py-1 w-64"
                      />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>
    </StepLayout>
  );
}

// ── Step 14: ECM Options & Cost ───────────────────────────────────────────────
const MEASURE_LABELS: Record<string, string> = {
  WallInsulation:      "Wall Insulation",
  Infiltration:        "Infiltration",
  CeilingInsulation:   "Ceiling Insulation",
  WindowMaterial:      "Window Material",
  NightSetBack:        "Night Setback",
  DaylightingSensor:   "Daylighting",
  Economizer:          "Economizer",
  OccupancySensor:     "Occupancy Sensor",
  LEDLighting:         "LED Lighting",
  ReduceEquipmentLoad: "Reduce Equipment Load",
  CoolingEff:          "Cooling Efficiency",
  HeatingEff:          "Heating Efficiency",
  HeatPumpAddition:    "Heat Pump Addition",
};

export function ECMOptionCostStep() {
  const { ecmStatus, ecmMeasures, ecmMetrics, ecmError, goToStep } = useForm();
  const isDone = ecmStatus === "done";
  const isRunning = ecmStatus === "running";

  const fmt = (n: number, decimals = 0) =>
    n.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });

  const fmtCost = (n: number) =>
    n === 0 ? "—" : `$${fmt(n, 0)}`;

  return (
    <StepLayout>
      {isRunning && (
        <div className="flex items-center gap-3 px-4 py-3 mb-4 rounded-lg bg-brand-50 border border-brand-200 text-sm text-brand-800">
          <svg className="w-4 h-4 animate-spin flex-shrink-0 text-brand-500" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
          </svg>
          Running ECM evaluation…
        </div>
      )}
      {ecmStatus === "error" && (
        <div className="flex items-start gap-2 px-3 py-2 mb-4 rounded-lg bg-red-50 border border-red-200 text-xs text-red-700">
          <span className="w-2 h-2 rounded-full bg-red-400 flex-shrink-0 mt-0.5" />
          <span><span className="font-semibold">Error:</span> {ecmError}</span>
        </div>
      )}

      <Card>
        <div className="flex items-start justify-between gap-4 mb-4">
          <SectionHeader
            title="ECM Options & Cost Breakdown"
            description="Per-measure cost and energy savings for the evaluated retrofit package."
            className="mb-0"
          />
          <button
            type="button"
            onClick={() => goToStep(15)}
            className="flex-shrink-0 flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold bg-brand-500 text-white hover:bg-brand-600 shadow-sm"
          >
            View Results
            <svg viewBox="0 0 16 16" fill="none" className="w-3.5 h-3.5">
              <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>

        {!isDone || ecmMeasures.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center gap-3">
            <svg viewBox="0 0 48 48" fill="none" className="w-10 h-10 text-app-text-light">
              <rect x="8" y="8" width="32" height="32" rx="4" stroke="currentColor" strokeWidth="2" />
              <path d="M16 24h16M16 30h10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              <path d="M16 18h8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
            <p className="text-sm text-app-text-muted">
              No evaluation results yet. Select ECM options on the previous step and click{" "}
              <span className="font-semibold text-app-text">Evaluate Package</span>.
            </p>
            <button
              type="button"
              onClick={() => goToStep(13)}
              className="mt-1 px-4 py-2 rounded-xl text-sm font-semibold border border-border hover:border-brand-300 hover:text-brand-700 hover:bg-brand-50 transition-all"
            >
              Go to Retrofit Analysis
            </button>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto rounded-lg border border-border">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-bg-muted border-b border-border">
                    <th className="text-left px-4 py-2.5 font-semibold text-app-text text-xs">Measure</th>
                    <th className="text-left px-4 py-2.5 font-semibold text-app-text text-xs">Baseline</th>
                    <th className="text-left px-4 py-2.5 font-semibold text-app-text text-xs">Selected Option</th>
                    <th className="text-right px-4 py-2.5 font-semibold text-app-text text-xs">Fixed Cost</th>
                    <th className="text-right px-4 py-2.5 font-semibold text-app-text text-xs">Var. Cost</th>
                    <th className="text-right px-4 py-2.5 font-semibold text-app-text text-xs">Total Cost</th>
                    <th className="text-right px-4 py-2.5 font-semibold text-app-text text-xs">Elec. Savings</th>
                    <th className="text-right px-4 py-2.5 font-semibold text-app-text text-xs">Gas Savings</th>
                  </tr>
                </thead>
                <tbody>
                  {ecmMeasures.map((row, i) => {
                    const elecSavings = row.OrgTotalElectricity - row.EEMTotalElectricity;
                    const gasSavings  = row.OrgTotalNaturalGas  - row.EEMTotalNaturalGas;
                    const totalCost   = row.InitFixedCost + row.InitVarCost;
                    return (
                      <tr key={i} className={i % 2 === 0 ? "bg-bg-card" : "bg-bg-muted"}>
                        <td className="px-4 py-2 font-medium text-app-text text-xs">
                          {MEASURE_LABELS[row.Measure] ?? row.Measure}
                        </td>
                        <td className="px-4 py-2 text-xs text-app-text-muted font-mono">
                          {String(row.OrgPropValue)}
                        </td>
                        <td className="px-4 py-2 text-xs text-primary font-medium">
                          {String(row.NewPropValue)}
                        </td>
                        <td className="px-4 py-2 text-xs text-right font-mono text-app-text">
                          {fmtCost(row.InitFixedCost)}
                        </td>
                        <td className="px-4 py-2 text-xs text-right font-mono text-app-text">
                          {fmtCost(row.InitVarCost)}
                        </td>
                        <td className="px-4 py-2 text-xs text-right font-mono font-semibold text-app-text">
                          {fmtCost(totalCost)}
                        </td>
                        <td className={`px-4 py-2 text-xs text-right font-mono ${elecSavings > 0 ? "text-success" : "text-app-text-muted"}`}>
                          {elecSavings > 0 ? `${fmt(elecSavings, 0)} kWh` : "—"}
                        </td>
                        <td className={`px-4 py-2 text-xs text-right font-mono ${gasSavings > 0 ? "text-accent" : "text-app-text-muted"}`}>
                          {gasSavings > 0 ? `${fmt(gasSavings, 1)} therms` : "—"}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
                {ecmMeasures.length > 1 && ecmMetrics && (
                  <tfoot>
                    <tr className="border-t-2 border-border bg-bg-muted">
                      <td colSpan={5} className="px-4 py-2.5 text-xs font-semibold text-app-text">
                        Package Total
                      </td>
                      <td className="px-4 py-2.5 text-xs text-right font-mono font-bold text-warning">
                        ${fmt(ecmMetrics.tic, 0)}
                      </td>
                      <td className="px-4 py-2.5 text-xs text-right font-mono font-semibold text-success">
                        {fmt(ecmMetrics.org_kwh - ecmMetrics.eem_kwh, 0)} kWh
                      </td>
                      <td className="px-4 py-2.5 text-xs text-right font-mono font-semibold text-accent">
                        {fmt(ecmMetrics.org_therms - ecmMetrics.eem_therms, 1)} therms
                      </td>
                    </tr>
                  </tfoot>
                )}
              </table>
            </div>

            <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="rounded-xl border border-border bg-bg-muted p-3 text-center">
                <p className="text-xs text-app-text-muted">Measures Selected</p>
                <p className="text-lg font-bold text-app-text mt-0.5">{ecmMeasures.length}</p>
              </div>
              <div className="rounded-xl border border-border bg-bg-muted p-3 text-center">
                <p className="text-xs text-app-text-muted">Total Installed Cost</p>
                <p className="text-lg font-bold text-warning mt-0.5">${fmt(ecmMetrics?.tic ?? 0, 0)}</p>
              </div>
              <div className="rounded-xl border border-border bg-bg-muted p-3 text-center">
                <p className="text-xs text-app-text-muted">Elec. Savings</p>
                <p className="text-lg font-bold text-success mt-0.5">
                  {fmt(ecmMetrics ? ecmMetrics.kwh_pct_savings : 0, 1)}%
                </p>
              </div>
              <div className="rounded-xl border border-border bg-bg-muted p-3 text-center">
                <p className="text-xs text-app-text-muted">Gas Savings</p>
                <p className="text-lg font-bold text-accent mt-0.5">
                  {fmt(ecmMetrics ? ecmMetrics.therms_pct_savings : 0, 1)}%
                </p>
              </div>
            </div>
          </>
        )}
      </Card>
    </StepLayout>
  );
}

// ── Step 15: Results Summary ──────────────────────────────────────────────────
function MetricCard({ label, value, sub, color }: { label: string; value: string; sub?: string; color: string }) {
  return (
    <div className="rounded-2xl border border-brand-100 bg-white p-5 flex flex-col items-center text-center shadow-sm">
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
      {sub && <p className="text-xs text-app-text-muted mt-0.5">{sub}</p>}
      <p className="text-xs text-app-text-muted mt-2 leading-tight">{label}</p>
    </div>
  );
}

const ECM_DESCRIPTIONS: Record<string, (baseline: string, selected: string) => string> = {
  ecmWallInsulation:    (b, s) => `Wall insulation upgraded from ${b} to ${s}.`,
  ecmInfiltration:      (b, s) => `Air leakage reduced from ${b} ACH50 to ${s} ACH50.`,
  ecmCeilingInsulation: (b, s) => `Ceiling insulation upgraded from ${b} to ${s}.`,
  ecmWindowMaterial:    (b, s) => `Windows upgraded from ${b} to ${s}.`,
  ecmNightSetback:      (b, s) => `Night setback temperature set to ${s}°F (baseline: ${b}°F).`,
  ecmNightSetbackHours: (b, s) => `Night setback extended to ${s} hrs/day (baseline: ${b} hrs).`,
  ecmDaylighting:       (_b, _s) => "Daylighting controls added to reduce lighting energy use.",
  ecmEconomizer:        (_b, _s) => "Air-side economizer added for free cooling during mild weather.",
  ecmOccupancySensor:   (_b, _s) => "Occupancy sensors installed to cut lighting when spaces are unoccupied.",
  ecmLED:               (b, s) => `LED fraction increased from ${b}% to ${s}%.`,
  ecmReduceEquipLoad:   (_b, s) => `Plug load reduction of ${s} applied through equipment scheduling.`,
  ecmCoolingEff:        (b, s) => `Cooling efficiency upgraded from ${b} to ${s} SEER2.`,
  ecmHeatingEqp:        (b, s) => `Heating equipment replaced: ${b} → ${s}.`,
  ecmHeatingEff:        (b, s) => `Heating efficiency upgraded from ${b} to ${s}.`,
};

export function ECMResultsStep() {
  const { state, pklProjectName, ecmStatus, ecmMetrics, ecmPlots, ecmError } = useForm();
  const isDone = ecmStatus === "done";
  const isRunning = ecmStatus === "running";

  const fmt = (n: number, decimals = 0) =>
    n.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });

  const baselineMap: Record<string, string> = {
    ecmWallInsulation:    state.wallInsulation    || "Uninsulated",
    ecmInfiltration:      state.ach50             || "—",
    ecmCeilingInsulation: state.ceilingInsulation || "Uninsulated",
    ecmWindowMaterial:    state.windowMaterial?.[0] || "—",
    ecmNightSetback:      state.nightSetback      || "0",
    ecmNightSetbackHours: state.nNightSetbackHours|| "0",
    ecmDaylighting:       state.daylighting       || "No",
    ecmEconomizer:        state.economizer        || "No",
    ecmOccupancySensor:   "No",
    ecmLED:               state.led               || "0",
    ecmReduceEquipLoad:   "0%",
    ecmCoolingEff:        state.coolingEff        || "—",
    ecmHeatingEqp:        state.heatingEqp        || "—",
    ecmHeatingEff:        state.heatingEff        || "—",
  };

  const activeMeasures = ECM_MEASURES.filter((m) => {
    const val = (state as unknown as Record<string, string>)[m.key];
    return val && val !== "No change" && val !== "" && val !== "No";
  }).map((m) => ({
    label: m.label,
    description: ECM_DESCRIPTIONS[m.key]?.(
      baselineMap[m.key],
      (state as unknown as Record<string, string>)[m.key]
    ) ?? `${m.label} changed to ${(state as unknown as Record<string, string>)[m.key]}.`,
  }));

  return (
    <StepLayout rightAction={<ExportDropdown />}>

      {/* Status banner */}
      {isRunning && (
        <div className="flex items-center gap-3 px-4 py-3 mb-4 rounded-lg bg-brand-50 border border-brand-200 text-sm text-brand-800">
          <svg className="w-4 h-4 animate-spin flex-shrink-0 text-brand-500" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
          </svg>
          Running ECM evaluation…
        </div>
      )}
      {ecmStatus === "error" && (
        <div className="flex items-start gap-2 px-3 py-2 mb-4 rounded-lg bg-red-50 border border-red-200 text-xs text-red-700">
          <span className="w-2 h-2 rounded-full bg-red-400 flex-shrink-0 mt-0.5" />
          <span><span className="font-semibold">Error:</span> {ecmError}</span>
        </div>
      )}

      {/* Key metrics */}
      <Card>
        <SectionHeader
          title="Package Performance Summary"
          description="Life-cycle cost and energy savings for the selected ECM package."
        />
        {isDone && ecmMetrics ? (
          <>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-4">
              <MetricCard
                label="Baseline Life-Cycle Cost"
                value={`$${fmt(ecmMetrics.org_lcc)}`}
                color="text-app-text-muted"
              />
              <MetricCard
                label="ECM Package Life-Cycle Cost"
                value={`$${fmt(ecmMetrics.lcc)}`}
                color="text-primary"
              />
              <MetricCard
                label="Total Installed Cost"
                value={`$${fmt(ecmMetrics.tic)}`}
                color="text-warning"
              />
            </div>
            <div className="grid grid-cols-2 gap-4 mb-5">
              <MetricCard
                label="Electricity Savings"
                value={`${fmt(ecmMetrics.kwh_pct_savings, 1)}%`}
                sub={`${fmt(ecmMetrics.org_kwh)} → ${fmt(ecmMetrics.eem_kwh)} kWh`}
                color="text-success"
              />
              <MetricCard
                label="Natural Gas Savings"
                value={`${fmt(ecmMetrics.therms_pct_savings, 1)}%`}
                sub={`${fmt(ecmMetrics.org_therms)} → ${fmt(ecmMetrics.eem_therms)} therms`}
                color="text-accent"
              />
            </div>
          </>
        ) : (
          <><div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-4">
              {["Baseline Life-Cycle Cost", "ECM Package Life-Cycle Cost", "Total Installed Cost"].map((label) => (
                <div key={label} className="rounded-2xl border border-border bg-bg-muted p-5 flex flex-col items-center text-center">
                  <p className="text-2xl font-bold text-app-text-light">—</p>
                  <p className="text-xs text-app-text-muted mt-2 leading-tight">{label}</p>
                </div>
              ))}
            </div><div className="grid grid-cols-2 gap-4 mb-5">
                {["Electricity Savings", "Natural Gas Savings"].map((label) => (
                  <div key={label} className="rounded-2xl border border-border bg-bg-muted p-5 flex flex-col items-center text-center">
                    <p className="text-2xl font-bold text-app-text-light">—</p>
                    <p className="text-xs text-app-text-muted mt-2 leading-tight">{label}</p>
                  </div>
                ))}
              </div></>
        )}
      </Card>

      {/* Selected measures summary */}
      {activeMeasures.length > 0 && (
        <Card>
          <SectionHeader
            title="Applied ECM Measures"
            description="Summary of changes made relative to the baseline building."
          />
          <ul className="flex flex-col gap-2">
            {activeMeasures.map((m) => (
              <li key={m.label} className="flex items-start gap-2.5">
                <span className="mt-1 w-2 h-2 rounded-full bg-brand-400 flex-shrink-0" />
                <span className="text-sm text-app-text leading-snug">
                  <span className="font-semibold text-primary">{m.label}:</span>{" "}
                  {m.description}
                </span>
              </li>
            ))}
          </ul>
        </Card>
      )}

      {/* Comparison charts */}
      {(isRunning || ecmPlots?.elec_monthly_comp || ecmPlots?.ng_monthly_comp) && (
        <Card>
          <SectionHeader
            title="Monthly Energy Comparison"
            description="Baseline vs. ECM package monthly energy use by end use."
          />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {(isRunning || ecmPlots?.elec_monthly_comp) && (
              <div>
                <p className="text-xs font-semibold text-primary mb-2">Electricity (kWh)</p>
                {isRunning ? (
                  <div className="h-56 rounded-lg border border-brand-100 flex items-center justify-center bg-bg-muted">
                    <svg className="w-6 h-6 text-brand-400 animate-spin" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                    </svg>
                  </div>
                ) : (
                  <img
                    src={ecmPlots!.elec_monthly_comp!}
                    alt="Electricity EEM Comparison"
                    className="w-full h-auto rounded-lg border border-brand-100 object-contain bg-white"
                  />
                )}
              </div>
            )}
            {(isRunning || ecmPlots?.ng_monthly_comp) && (
              <div>
                <p className="text-xs font-semibold text-primary mb-2">Natural Gas (Therms)</p>
                {isRunning ? (
                  <div className="h-56 rounded-lg border border-brand-100 flex items-center justify-center bg-bg-muted">
                    <svg className="w-6 h-6 text-brand-400 animate-spin" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                    </svg>
                  </div>
                ) : (
                  <img
                    src={ecmPlots!.ng_monthly_comp!}
                    alt="Natural Gas EEM Comparison"
                    className="w-full h-auto rounded-lg border border-brand-100 object-contain bg-white"
                  />
                )}
              </div>
            )}
          </div>
        </Card>
      )}

    </StepLayout>
  );
}
