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
        <div className="flex gap-3">
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

  const isLShape = state.shapeType === "L-Shape";
  const imageSrc = isLShape ? "/shapes/L-Shape.png" : "/shapes/Rectangle.png";
  const imageAlt = isLShape ? "L-Shape floor plan — x1, x2, y1, y2 corner coordinates" : "Rectangle floor plan — x1 width, y1 depth, corner coordinates";

  const imagePanel = (
    <div className="flex flex-col gap-4 w-full h-full">
      {/* Shape diagram */}
      <div className="bg-white rounded-2xl shadow-md border border-brand-100 overflow-hidden w-full flex flex-col flex-1 min-h-0">
        <div className="flex-1 min-h-0 flex items-center justify-center overflow-hidden">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={imageSrc}
            alt={imageAlt}
            className="w-full h-full object-contain p-4"
          />
        </div>
      </div>
      {/* Dimension legend */}
      <div className="bg-white/70 rounded-xl border border-brand-100 px-5 py-3 w-full flex-shrink-0">
        <p className="text-xs font-bold text-primary uppercase tracking-wider mb-2">Coordinate Reference</p>
        <div className={`grid gap-x-6 gap-y-1 text-xs text-app-text-muted ${isLShape ? "grid-cols-2" : "grid-cols-2"}`}>
          <span><span className="font-semibold text-primary">x1</span> — full width</span>
          <span><span className="font-semibold text-primary">y1</span> — full depth</span>
          {isLShape && (
            <>
              <span><span className="font-semibold text-primary">x2</span> — inner notch width</span>
              <span><span className="font-semibold text-primary">y2</span> — inner notch depth</span>
            </>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <StepLayout imagePanel={imagePanel}>
      {/* Building Dimensions */}
      <Card>
        <SectionHeader
          title="Building Dimensions"
          description="Enter overall floor area and vertical dimensions."
        />
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
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
          title="Building Dimensions"
          description={
            isLShape
              ? "For L-shaped floor plans, enter the full width (x1), notch width (x2), full depth (y1), and notch depth (y2)."
              : "Enter the width (x1) and depth (y1) of the rectangular floor plan."
          }
        />
        <div className={`grid gap-3 ${isLShape ? "grid-cols-2 sm:grid-cols-4" : "grid-cols-2"}`}>
          <FormField label="x1" fieldKey="x1">
            <Input
              type="number"
              placeholder="40"
              unit="ft"
              value={state.x1}
              onChange={(e) => setField("x1", e.target.value)}
            />
          </FormField>
          {isLShape && (
            <FormField label="x2" fieldKey="x2">
              <Input
                type="number"
                placeholder="20"
                unit="ft"
                value={state.x2}
                onChange={(e) => setField("x2", e.target.value)}
              />
            </FormField>
          )}
          <FormField label="y1" fieldKey="y1">
            <Input
              type="number"
              placeholder="50"
              unit="ft"
              value={state.y1}
              onChange={(e) => setField("y1", e.target.value)}
            />
          </FormField>
          {isLShape && (
            <FormField label="y2" fieldKey="y2">
              <Input
                type="number"
                placeholder="25"
                unit="ft"
                value={state.y2}
                onChange={(e) => setField("y2", e.target.value)}
              />
            </FormField>
          )}
        </div>
      </Card>
    </StepLayout>
  );
}
