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
import { PreviewCard } from "@/components/ui/PreviewCard";
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

function WallIllustration({ insulation }: { insulation: string }) {
  const hasInsulation = insulation && insulation !== "Uninsulated";
  return (
    <svg viewBox="0 0 120 100" className="w-full h-full" fill="none">
      <rect x="10" y="10" width="100" height="80" rx="4" fill="#d1d5db" />
      {[20, 40, 60].map((y) =>
        [10, 50].map((x) => (
          <rect key={`${x}-${y}`} x={x} y={y} width="35" height="18" rx="1" fill="#9ca3af" opacity="0.5" />
        ))
      )}
      {hasInsulation && (
        <rect x="10" y="10" width="26" height="80" fill="#bef264" opacity="0.8" rx="2" />
      )}
      <text x="60" y="97" textAnchor="middle" fontSize="7" fill="#6b7280">
        {hasInsulation ? "Insulated Wall" : "Uninsulated Wall"}
      </text>
    </svg>
  );
}

export function WallsRoofStep() {
  const { state, setField } = useForm();

  const imagePanel = (
    <PreviewCard
      image={<WallIllustration insulation={state.wallInsulation} />}
      title={state.extWallConst || "Wall Construction"}
      subtitle={state.wallInsulation || "Select insulation level"}
    />
  );

  return (
    <StepLayout imagePanel={imagePanel}>
      {/* Exterior Walls */}
      <Card>
        <SectionHeader
          title="Exterior Walls"
          description="Define the wall construction type and insulation level."
        />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField label="Wall Construction Type" fieldKey="extWallConst" required>
            <Select
              options={EXT_WALL_CONSTRUCTIONS}
              placeholder="Select construction type…"
              value={state.extWallConst}
              onChange={(e) => setField("extWallConst", e.target.value)}
            />
          </FormField>
          <FormField label="Wall Insulation" fieldKey="wallInsulation" required>
            <Select
              options={WALL_INSULATIONS}
              placeholder="Select insulation level…"
              value={state.wallInsulation}
              onChange={(e) => setField("wallInsulation", e.target.value)}
            />
          </FormField>
        </div>
      </Card>

      {/* Roof / Ceiling */}
      <Card>
        <SectionHeader
          title="Roof / Ceiling"
          description="Specify the roof construction and ceiling insulation."
        />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField label="Roof Construction Type" fieldKey="extRoofConst" required>
            <Select
              options={EXT_ROOF_CONSTRUCTIONS}
              placeholder="Select roof type…"
              value={state.extRoofConst}
              onChange={(e) => setField("extRoofConst", e.target.value)}
            />
          </FormField>
          <FormField label="Ceiling Insulation" fieldKey="ceilingInsulation" required>
            <Select
              options={CEILING_INSULATIONS}
              placeholder="Select insulation level…"
              value={state.ceilingInsulation}
              onChange={(e) => setField("ceilingInsulation", e.target.value)}
            />
          </FormField>
        </div>
      </Card>
    </StepLayout>
  );
}

export function FoundationInfiltrationStep() {
  const { state, setField } = useForm();
  return (
    <StepLayout>
      {/* Foundation */}
      <Card>
        <SectionHeader
          title="Foundation"
          description="Select the foundation type and any slab insulation."
        />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
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
          description="Air changes per hour at 50 Pascal pressure. Lower = tighter building."
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

export function WindowsShadingStep() {
  const { state, setField } = useForm();
  return (
    <StepLayout>
      {/* Windows */}
      <Card>
        <SectionHeader
          title="Windows"
          description="Select glazing type and window-to-wall ratios by facade."
        />
        <div className="space-y-5">
          <div>
            <p className="form-label mb-2">Window Material (select one or more)</p>
            <MultiSelect
              options={WINDOW_MATERIALS}
              value={state.windowMaterial}
              onChange={(v) => setField("windowMaterial", v)}
              columns={2}
            />
            <p className="text-xs text-app-text-muted mt-1">Hold Ctrl / Cmd to select multiple.</p>
          </div>
          <div>
            <p className="form-label mb-3">Window-to-Wall Ratio by Facade (%)</p>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <FormField label="Front" fieldKey="wwrFront">
                <Input
                  type="number"
                  placeholder="30"
                  unit="%"
                  value={state.wwrFront}
                  onChange={(e) => setField("wwrFront", e.target.value)}
                />
              </FormField>
              <FormField label="Left" fieldKey="wwrLeft">
                <Input
                  type="number"
                  placeholder="15"
                  unit="%"
                  value={state.wwrLeft}
                  onChange={(e) => setField("wwrLeft", e.target.value)}
                />
              </FormField>
              <FormField label="Back" fieldKey="wwrBack">
                <Input
                  type="number"
                  placeholder="20"
                  unit="%"
                  value={state.wwrBack}
                  onChange={(e) => setField("wwrBack", e.target.value)}
                />
              </FormField>
              <FormField label="Right" fieldKey="wwrRight">
                <Input
                  type="number"
                  placeholder="15"
                  unit="%"
                  value={state.wwrRight}
                  onChange={(e) => setField("wwrRight", e.target.value)}
                />
              </FormField>
            </div>
          </div>
        </div>
      </Card>

      {/* Shading */}
      <Card>
        <SectionHeader
          title="Shading"
          description="Configure overhang depth and window geometry for solar shading calculations."
        />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <FormField label="Overhang Depth" fieldKey="overhang" hint="Horizontal projection above windows">
            <Input
              type="number"
              placeholder="0"
              unit="ft"
              value={state.overhang}
              onChange={(e) => setField("overhang", e.target.value)}
            />
          </FormField>
          <FormField label="Window Height" fieldKey="windowHt">
            <Input
              type="number"
              placeholder="4"
              unit="ft"
              value={state.windowHt}
              onChange={(e) => setField("windowHt", e.target.value)}
            />
          </FormField>
          <FormField label="Windows per Wall" fieldKey="nWindow">
            <Input
              type="number"
              placeholder="3"
              value={state.nWindow}
              onChange={(e) => setField("nWindow", e.target.value)}
            />
          </FormField>
        </div>
      </Card>
    </StepLayout>
  );
}
