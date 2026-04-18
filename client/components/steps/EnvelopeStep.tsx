"use client";

import React from "react";
import { useForm } from "@/context/FormContext";
import { StepLayout } from "@/components/StepLayout";
import { FormField } from "@/components/ui/FormField";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { MultiSelect } from "@/components/ui/MultiSelect";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import {
  EXT_WALL_CONSTRUCTIONS,
  WALL_INSULATIONS,
  EXT_ROOF_CONSTRUCTIONS,
  CEILING_INSULATIONS,
  FOUNDATIONS,
  SLAB_INSULATIONS,
  ACH50_OPTIONS,
  WINDOW_MATERIALS,
} from "@/data/options";

const WALL_IMAGE_MAP: Record<string, string> = {
  "2x4 insulated wood stud with vinyl siding": "/envelope/2x4 insulated wood stud with vinyl siding.png",
  "2x4 insulated wood stud with brick finish":  "/envelope/2x4 insulated wood stud with brick finish.png",
  "Insulated 8in. Concrete":                    "/envelope/Insulated 8in. Concrete.png",
};

export function WallsRoofStep() {
  const { state, setField } = useForm();

  const wallImg   = state.extWallConst ? WALL_IMAGE_MAP[state.extWallConst] : null;
  const hasRoofInsulation = state.ceilingInsulation && state.ceilingInsulation !== "Uninsulated";
  const roofImg   = state.extRoofConst
    ? hasRoofInsulation
      ? "/envelope/Attic Insulation.png"
      : "/envelope/Asphalt Shingles.png"
    : null;

  const imagePanel = (
    <div className="flex flex-col gap-5 w-full h-full">
      {/* Wall diagram */}
      <div className="bg-white rounded-2xl shadow-md border border-brand-100 overflow-hidden w-full flex flex-col flex-1 min-h-0">
        <div className="px-4 pt-3 pb-1 border-b border-brand-100 flex-shrink-0">
          <p className="text-xs font-bold text-primary uppercase tracking-wider">Wall Construction</p>
          <p className="text-xs text-app-text-muted mt-0.5">
            {state.extWallConst || "Select a wall type to preview"}
          </p>
        </div>
        <div className="flex-1 min-h-0 flex items-center justify-center overflow-hidden">
          {wallImg ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={wallImg} alt={state.extWallConst} className="w-full h-full object-contain p-3" />
          ) : (
            <p className="text-xs text-app-text-muted">Select wall construction type</p>
          )}
        </div>
      </div>

      {/* Roof / Ceiling diagram */}
      <div className="bg-white rounded-2xl shadow-md border border-brand-100 overflow-hidden w-full flex flex-col flex-1 min-h-0">
        <div className="px-4 pt-3 pb-1 border-b border-brand-100 flex-shrink-0">
          <p className="text-xs font-bold text-primary uppercase tracking-wider">Roof / Ceiling</p>
          <p className="text-xs text-app-text-muted mt-0.5">
            {state.extRoofConst
              ? hasRoofInsulation
                ? `${state.extRoofConst} · ${state.ceilingInsulation}`
                : state.extRoofConst
              : "Select a roof type to preview"}
          </p>
        </div>
        <div className="flex-1 min-h-0 flex items-center justify-center overflow-hidden">
          {roofImg ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={roofImg} alt={state.extRoofConst} className="w-full h-full object-contain p-3" />
          ) : (
            <p className="text-xs text-app-text-muted">Select roof construction type</p>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <StepLayout imagePanel={imagePanel}>

      {/* ── Exterior Walls ── */}
      <Card>
        <SectionHeader
          title="Exterior Walls"
          description="Defines the thermal mass, layers, and insulation of the building envelope. The diagram on the right updates as you select."
        />
        <div className="flex flex-col gap-4">
          <FormField
            label="Wall Construction Type"
            fieldKey="extWallConst"
            required
            hint="Structural system and exterior finish material"
          >
            <Select
              options={EXT_WALL_CONSTRUCTIONS}
              placeholder="Select construction type…"
              value={state.extWallConst}
              onChange={(e) => setField("extWallConst", e.target.value)}
            />
          </FormField>

          <FormField
            label="Wall Insulation"
            fieldKey="wallInsulation"
            required
            hint="Cavity or continuous insulation R-value — higher R = better thermal resistance"
          >
            <Select
              options={WALL_INSULATIONS}
              placeholder="Select insulation level…"
              value={state.wallInsulation}
              onChange={(e) => setField("wallInsulation", e.target.value)}
            />
          </FormField>

          {/* Insulation status badge */}
          {state.wallInsulation && (
            <div className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium ${
              state.wallInsulation === "Uninsulated"
                ? "bg-red-50 border border-red-200 text-red-700"
                : "bg-brand-50 border border-brand-200 text-brand-800"
            }`}>
              <span className={`w-2 h-2 rounded-full flex-shrink-0 ${
                state.wallInsulation === "Uninsulated" ? "bg-red-400" : "bg-brand-500"
              }`} />
              {state.wallInsulation === "Uninsulated"
                ? "No insulation — high heat loss expected"
                : `${state.wallInsulation} installed — diagram shows insulated cross-section`}
            </div>
          )}
        </div>
      </Card>

      {/* ── Roof / Ceiling ── */}
      <Card>
        <SectionHeader
          title="Roof / Ceiling"
          description="Roof assembly and ceiling insulation together control heat gain and loss through the top of the building. Diagram switches to attic detail when insulation is selected."
        />
        <div className="flex flex-col gap-4">
          <FormField
            label="Roof Construction Type"
            fieldKey="extRoofConst"
            required
            hint="Exterior roofing material and structural assembly"
          >
            <Select
              options={EXT_ROOF_CONSTRUCTIONS}
              placeholder="Select roof type…"
              value={state.extRoofConst}
              onChange={(e) => setField("extRoofConst", e.target.value)}
            />
          </FormField>

          <FormField
            label="Ceiling Insulation"
            fieldKey="ceilingInsulation"
            required
            hint="Attic floor insulation R-value — higher R = less heat transfer through ceiling"
          >
            <Select
              options={CEILING_INSULATIONS}
              placeholder="Select insulation level…"
              value={state.ceilingInsulation}
              onChange={(e) => setField("ceilingInsulation", e.target.value)}
            />
          </FormField>

          {/* Insulation status badge */}
          {state.ceilingInsulation && (
            <div className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium ${
              state.ceilingInsulation === "Uninsulated"
                ? "bg-red-50 border border-red-200 text-red-700"
                : "bg-brand-50 border border-brand-200 text-brand-800"
            }`}>
              <span className={`w-2 h-2 rounded-full flex-shrink-0 ${
                state.ceilingInsulation === "Uninsulated" ? "bg-red-400" : "bg-brand-500"
              }`} />
              {state.ceilingInsulation === "Uninsulated"
                ? "No ceiling insulation — diagram shows bare roof assembly"
                : `${state.ceilingInsulation} attic insulation — diagram switches to insulated attic view`}
            </div>
          )}
        </div>
      </Card>

    </StepLayout>
  );
}

const FOUNDATION_IMAGE_MAP: Record<string, string> = {
  "Slab on grade": "/foundation/Slab on grade.png",
  "Crawlspace":    "/foundation/Crawlspace.png",
  "Basement":      "/foundation/Basement.png",
};

// ACH50 tightness scale for the infiltration reference card
const ACH50_SCALE = [
  { range: "≤ 3",    label: "Very Tight",  color: "bg-brand-500" },
  { range: "4 – 7",  label: "Tight",       color: "bg-brand-400" },
  { range: "8 – 15", label: "Average",     color: "bg-yellow-400" },
  { range: "≥ 20",   label: "Leaky",       color: "bg-red-400" },
];

export function FoundationInfiltrationStep() {
  const { state, setField } = useForm();

  const foundationImg = state.foundation ? (FOUNDATION_IMAGE_MAP[state.foundation] ?? null) : null;

  const imagePanel = (
    <div className="flex flex-col gap-5 w-full h-full">
      {/* Foundation diagram */}
      <div className="bg-white rounded-2xl shadow-md border border-brand-100 overflow-hidden w-full flex flex-col flex-1 min-h-0">
        <div className="px-4 pt-3 pb-1 border-b border-brand-100 flex-shrink-0">
          <p className="text-xs font-bold text-primary uppercase tracking-wider">Foundation Type</p>
          <p className="text-xs text-app-text-muted mt-0.5">
            {state.foundation || "Select a foundation type to preview"}
          </p>
        </div>
        <div className="flex-1 min-h-0 flex items-center justify-center overflow-hidden">
          {foundationImg ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={foundationImg} alt={state.foundation} className="w-full h-full object-contain p-3" />
          ) : (
            <p className="text-xs text-app-text-muted">Select foundation type</p>
          )}
        </div>
      </div>

      {/* ACH50 reference card */}
      <div className="bg-white rounded-2xl shadow-md border border-brand-100 overflow-hidden w-full flex flex-col flex-shrink-0">
        <div className="px-4 pt-3 pb-1 border-b border-brand-100">
          <p className="text-xs font-bold text-primary uppercase tracking-wider">Air Leakage Reference</p>
          <p className="text-xs text-app-text-muted mt-0.5">
            {state.ach50 ? `ACH50 = ${state.ach50} — see scale below` : "ACH50 tightness scale"}
          </p>
        </div>
        <div className="p-4 flex flex-col gap-2">
          {ACH50_SCALE.map(({ range, label, color }) => {
            const selected = (() => {
              const v = parseFloat(state.ach50 || "0");
              if (label === "Very Tight") return v <= 3;
              if (label === "Tight")      return v >= 4 && v <= 7;
              if (label === "Average")    return v >= 8 && v <= 15;
              if (label === "Leaky")      return v >= 20;
              return false;
            })();
            return (
              <div
                key={label}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-all ${
                  selected ? "bg-brand-50 border border-brand-200" : "border border-transparent"
                }`}
              >
                <span className={`w-3 h-3 rounded-full flex-shrink-0 ${color}`} />
                <span className="text-xs font-semibold text-primary w-20">{label}</span>
                <span className="text-xs text-app-text-muted font-mono">{range} ACH50</span>
                {selected && (
                  <span className="ml-auto text-xs font-bold text-brand-600">← selected</span>
                )}
              </div>
            );
          })}
          <p className="text-xs text-app-text-muted mt-2 px-1 leading-relaxed">
            Measured by a blower door test at 50 Pascal depressurization. Lower values indicate a tighter, better-sealed building envelope.
          </p>
        </div>
      </div>
    </div>
  );

  return (
    <StepLayout imagePanel={imagePanel}>
      {/* Foundation */}
      <Card>
        <SectionHeader
          title="Foundation"
          description="Select the foundation type and any slab insulation. The diagram on the right updates with your selection."
        />
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <FormField label="Foundation Type" fieldKey="foundation" required>
            <Select
              options={FOUNDATIONS}
              placeholder="Select foundation type…"
              value={state.foundation}
              onChange={(e) => setField("foundation", e.target.value)}
            />
          </FormField>
          <FormField label="Slab Insulation" fieldKey="slabInsulation">
            <Select
              options={SLAB_INSULATIONS}
              value={state.slabInsulation}
              onChange={(e) => setField("slabInsulation", e.target.value)}
            />
          </FormField>
        </div>
      </Card>

      {/* Air Infiltration */}
      <Card>
        <SectionHeader
          title="Air Infiltration"
          description="Air changes per hour at 50 Pascal pressure. Lower = tighter building. The scale on the right shows where your value falls."
        />
        <div className="max-w-xs">
          <FormField label="Air Leakage — ACH50" fieldKey="ach50" required>
            <Select
              options={ACH50_OPTIONS}
              placeholder="Select ACH50 value…"
              value={state.ach50}
              onChange={(e) => setField("ach50", e.target.value)}
            />
          </FormField>
        </div>
      </Card>
    </StepLayout>
  );
}

const WINDOW_IMAGE_MAP: Record<string, string> = {
  "Single Pane Clear":                          "/windows/single-pane-clear.png",
  "Double Pane Clear":                          "/windows/double-pane-clear.png",
  "Low-e Double Pane Clear Air Filled":         "/windows/low-e-double-pane-air.png",
  "Low-e Double Pane Clear Argon Filled":       "/windows/low-e-double-pane-argon.png",
  "Low-e Double Pane Insulated Air Filled":     "/windows/low-e-double-pane-air-insulated.png",
  "Low-e Double Pane Insulated Argon Filled":   "/windows/low-e-double-pane-argon-insulated.png",
  "Low-e Triple Pane Clear Air Filled":         "/windows/low-e-triple-pane-air.png",
  "Low-e Triple Pane Clear Argon Filled":       "/windows/low-e-triple-pane-argon.png",
  "Low-e Triple Pane Insulated Air Filled":     "/windows/low-e-triple-pane-air-insulated.png",
  "Low-e Triple Pane Insulated Argon Filled":   "/windows/low-e-triple-pane-argon-insulated.png",
};

export function WindowsShadingStep() {
  const { state, setField } = useForm();

  // Show diagram for the first selected window material
  const firstMaterial = state.windowMaterial?.[0] ?? null;
  const windowImg = firstMaterial ? (WINDOW_IMAGE_MAP[firstMaterial] ?? null) : null;
  const multipleSelected = (state.windowMaterial?.length ?? 0) > 1;

  const imagePanel = (
    <div className="flex flex-col gap-5 w-full h-full">

      {/* Window glazing diagram */}
      <div className="bg-white rounded-2xl shadow-md border border-brand-100 overflow-hidden w-full flex flex-col flex-1 min-h-0">
        <div className="px-4 pt-3 pb-1 border-b border-brand-100 flex-shrink-0">
          <p className="text-xs font-bold text-primary uppercase tracking-wider">Window Glazing</p>
          <p className="text-xs text-app-text-muted mt-0.5">
            {firstMaterial
              ? multipleSelected
                ? `${firstMaterial} (+${state.windowMaterial.length - 1} more)`
                : firstMaterial
              : "Select a window material to preview"}
          </p>
        </div>
        <div className="flex-1 min-h-0 flex items-center justify-center overflow-hidden">
          {windowImg ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={windowImg} alt={firstMaterial ?? ""} className="w-full h-full object-contain p-3" />
          ) : (
            <div className="flex flex-col items-center justify-center gap-2 text-app-text-muted w-full h-full">
              <svg viewBox="0 0 40 40" fill="none" className="w-8 h-8 opacity-30">
                <rect x="4" y="4" width="32" height="32" rx="3" stroke="currentColor" strokeWidth="2"/>
                <line x1="20" y1="4" x2="20" y2="36" stroke="currentColor" strokeWidth="1.5"/>
                <line x1="4" y1="20" x2="36" y2="20" stroke="currentColor" strokeWidth="1.5"/>
              </svg>
              <p className="text-xs">Select window material to preview</p>
            </div>
          )}
        </div>
      </div>

      {/* Shading overhang diagram — always visible */}
      <div className="bg-white rounded-2xl shadow-md border border-brand-100 overflow-hidden w-full flex flex-col flex-1 min-h-0">
        <div className="px-4 pt-3 pb-1 border-b border-brand-100 flex-shrink-0">
          <p className="text-xs font-bold text-primary uppercase tracking-wider">Shading Overhang</p>
          <p className="text-xs text-app-text-muted mt-0.5">
            {state.overhang
              ? `Overhang depth: ${state.overhang} ft · Window height: ${state.windowHt || "—"} ft`
              : "Horizontal projection above windows"}
          </p>
        </div>
        <div className="flex-1 min-h-0 flex items-center justify-center overflow-hidden">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/windows/shading-overhang.png"
            alt="Shading overhang depth and window height reference"
            className="w-full h-full object-contain p-3"
          />
        </div>
      </div>

    </div>
  );

  return (
    <StepLayout imagePanel={imagePanel}>

      {/* ── Windows ── */}
      <Card>
        <SectionHeader
          title="Windows"
          description="Select glazing type and set window-to-wall ratios per facade. The cross-section diagram on the right shows the selected glazing assembly."
        />
        <div className="flex flex-col gap-4">
          <div>
            <p className="form-label mb-2">Window Material <span className="text-app-text-muted font-normal">(select one or more)</span></p>
            <MultiSelect
              options={WINDOW_MATERIALS}
              value={state.windowMaterial}
              onChange={(v) => setField("windowMaterial", v)}
              columns={2}
            />
            {multipleSelected && (
              <p className="text-xs text-app-text-muted mt-1.5">
                Diagram shows <span className="font-medium text-primary">{firstMaterial}</span> — first selected type.
              </p>
            )}
          </div>

          <div>
            <p className="form-label mb-2">Window-to-Wall Ratio by Facade (%)</p>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <FormField label="Front" fieldKey="wwrFront">
                <Input type="number" placeholder="30" unit="%" value={state.wwrFront}
                  onChange={(e) => setField("wwrFront", e.target.value)} />
              </FormField>
              <FormField label="Left" fieldKey="wwrLeft">
                <Input type="number" placeholder="15" unit="%" value={state.wwrLeft}
                  onChange={(e) => setField("wwrLeft", e.target.value)} />
              </FormField>
              <FormField label="Back" fieldKey="wwrBack">
                <Input type="number" placeholder="20" unit="%" value={state.wwrBack}
                  onChange={(e) => setField("wwrBack", e.target.value)} />
              </FormField>
              <FormField label="Right" fieldKey="wwrRight">
                <Input type="number" placeholder="15" unit="%" value={state.wwrRight}
                  onChange={(e) => setField("wwrRight", e.target.value)} />
              </FormField>
            </div>
          </div>
        </div>
      </Card>

      {/* ── Shading ── */}
      <Card>
        <SectionHeader
          title="Shading"
          description="Overhang depth, window height, and count determine how much direct solar gain is blocked. The diagram on the right shows the Depth and Height labels."
        />
        <div className="grid grid-cols-3 gap-3">
          <FormField label="Overhang Depth" fieldKey="overhang" hint="Horizontal projection above windows (ft)">
            <Input type="number" placeholder="0" unit="ft" value={state.overhang}
              onChange={(e) => setField("overhang", e.target.value)} />
          </FormField>
          <FormField label="Window Height" fieldKey="windowHt" hint="Vertical window dimension (ft)">
            <Input type="number" placeholder="4" unit="ft" value={state.windowHt}
              onChange={(e) => setField("windowHt", e.target.value)} />
          </FormField>
          <FormField label="Windows per Wall" fieldKey="nWindow" hint="Number of windows on each facade">
            <Input type="number" placeholder="3" value={state.nWindow}
              onChange={(e) => setField("nWindow", e.target.value)} />
          </FormField>
        </div>
      </Card>

    </StepLayout>
  );
}
