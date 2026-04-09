"use client";

import React from "react";
import { useForm } from "@/context/FormContext";
import { StepLayout } from "@/components/StepLayout";
import { FormField } from "@/components/ui/FormField";
import { Input } from "@/components/ui/Input";
import { MultiSelect } from "@/components/ui/MultiSelect";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { SHAPE_TYPES, ORIENTATIONS } from "@/data/options";

function ShapeIcon({ shape, selected }: { shape: string; selected: boolean }) {
  return (
    <button
      type="button"
      className={`flex flex-col items-center gap-2 p-4 rounded-lg border-2 transition-colors duration-150 w-32
        ${selected ? "border-primary bg-primary-50" : "border-border hover:border-accent bg-bg-card"}`}
    >
      <div className={`${selected ? "text-primary" : "text-app-text-muted"}`}>
        {shape === "Rectangle" ? (
          <svg viewBox="0 0 40 30" className="w-10 h-8">
            <rect x="2" y="2" width="36" height="26" rx="2" fill="none" stroke="currentColor" strokeWidth="2.5" />
          </svg>
        ) : (
          <svg viewBox="0 0 40 40" className="w-10 h-10">
            <polygon
              points="2,38 2,15 15,15 15,2 38,2 38,22 22,22 22,38"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
            />
          </svg>
        )}
      </div>
      <span className={`text-xs font-medium ${selected ? "text-primary" : "text-app-text-muted"}`}>
        {shape}
      </span>
    </button>
  );
}

export function ShapeOrientationStep() {
  const { state, setField } = useForm();
  return (
    <StepLayout>
      {/* Floor Plan Shape */}
      <Card>
        <SectionHeader
          title="Floor Plan Shape"
          description="Select the floor plan shape of the building."
        />
        <div className="flex gap-4">
          {SHAPE_TYPES.map((shape) => (
            <div key={shape} onClick={() => setField("shapeType", shape)}>
              <ShapeIcon shape={shape} selected={state.shapeType === shape} />
            </div>
          ))}
        </div>
      </Card>

      {/* Building Orientation */}
      <Card>
        <SectionHeader
          title="Building Orientation"
          description="Select one or more orientations for the building's front facade."
        />
        <MultiSelect
          options={ORIENTATIONS}
          value={state.orientation}
          onChange={(v) => setField("orientation", v)}
          columns={3}
        />
        <p className="text-xs text-app-text-muted mt-1">Hold Ctrl / Cmd to select multiple.</p>
      </Card>
    </StepLayout>
  );
}

export function DimensionsStep() {
  const { state, setField } = useForm();
  return (
    <StepLayout>
      {/* Building Dimensions */}
      <Card>
        <SectionHeader
          title="Building Dimensions"
          description="Enter overall floor area and vertical dimensions."
        />
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
          <FormField label="Floor Area" fieldKey="floorArea" required hint="Above-ground conditioned area">
            <Input
              type="number"
              placeholder="2000"
              unit="ft²"
              value={state.floorArea}
              onChange={(e) => setField("floorArea", e.target.value)}
            />
          </FormField>
          <FormField label="Number of Floors" fieldKey="flrQty" required>
            <Input
              type="number"
              placeholder="1"
              value={state.flrQty}
              onChange={(e) => setField("flrQty", e.target.value)}
            />
          </FormField>
          <FormField label="Wall Height" fieldKey="wallHt" required>
            <Input
              type="number"
              placeholder="10"
              unit="ft"
              value={state.wallHt}
              onChange={(e) => setField("wallHt", e.target.value)}
            />
          </FormField>
        </div>
      </Card>

      {/* Corner Coordinates */}
      <Card>
        <SectionHeader
          title="Building Corner Coordinates"
          description={
            state.shapeType === "L-Shape"
              ? "For L-shaped floor plans, define the outer corner coordinates."
              : "For rectangular plans, x1/y1 and x2/y2 define opposite corners."
          }
        />
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <FormField label="x1" fieldKey="x1">
            <Input
              type="number"
              placeholder="0"
              unit="ft"
              value={state.x1}
              onChange={(e) => setField("x1", e.target.value)}
            />
          </FormField>
          <FormField label="x2" fieldKey="x2">
            <Input
              type="number"
              placeholder="40"
              unit="ft"
              value={state.x2}
              onChange={(e) => setField("x2", e.target.value)}
            />
          </FormField>
          <FormField label="y1" fieldKey="y1">
            <Input
              type="number"
              placeholder="0"
              unit="ft"
              value={state.y1}
              onChange={(e) => setField("y1", e.target.value)}
            />
          </FormField>
          <FormField label="y2" fieldKey="y2">
            <Input
              type="number"
              placeholder="50"
              unit="ft"
              value={state.y2}
              onChange={(e) => setField("y2", e.target.value)}
            />
          </FormField>
        </div>
      </Card>
    </StepLayout>
  );
}
