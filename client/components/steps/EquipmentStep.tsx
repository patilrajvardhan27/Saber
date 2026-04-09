"use client";

import React from "react";
import { useForm } from "@/context/FormContext";
import { StepLayout } from "@/components/StepLayout";
import { FormField } from "@/components/ui/FormField";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { COOKING_FUEL_TYPES, YES_NO, LED_OPTIONS } from "@/data/options";

export function AppliancesStep() {
  const { state, setField } = useForm();
  return (
    <StepLayout>
      {/* Kitchen */}
      <Card>
        <SectionHeader
          title="Kitchen Appliances"
          description="Enter rated wattage for kitchen equipment."
        />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField label="Cooking Range Fuel Type" fieldKey="cookingFuelType">
            <Select
              options={COOKING_FUEL_TYPES}
              placeholder="Select fuel type…"
              value={state.cookingFuelType}
              onChange={(e) => setField("cookingFuelType", e.target.value)}
            />
          </FormField>
          <FormField label="Cooking Range Rating" fieldKey="cookingRating">
            <Input
              type="number"
              placeholder="3500"
              unit="W"
              value={state.cookingRating}
              onChange={(e) => setField("cookingRating", e.target.value)}
            />
          </FormField>
          <FormField label="Refrigerator Rating" fieldKey="fridgeRating">
            <Input
              type="number"
              placeholder="150"
              unit="W"
              value={state.fridgeRating}
              onChange={(e) => setField("fridgeRating", e.target.value)}
            />
          </FormField>
          <FormField label="Dishwasher Rating" fieldKey="dishWasherRating">
            <Input
              type="number"
              placeholder="1200"
              unit="W"
              value={state.dishWasherRating}
              onChange={(e) => setField("dishWasherRating", e.target.value)}
            />
          </FormField>
        </div>
      </Card>

      {/* Laundry */}
      <Card>
        <SectionHeader title="Laundry Equipment" />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField label="Clothes Washer Rating" fieldKey="washerRating">
            <Input
              type="number"
              placeholder="500"
              unit="W"
              value={state.washerRating}
              onChange={(e) => setField("washerRating", e.target.value)}
            />
          </FormField>
          <FormField label="Clothes Dryer Rating" fieldKey="dryerRating">
            <Input
              type="number"
              placeholder="5000"
              unit="W"
              value={state.dryerRating}
              onChange={(e) => setField("dryerRating", e.target.value)}
            />
          </FormField>
        </div>
      </Card>
    </StepLayout>
  );
}

export function LightingPlugLoadsStep() {
  const { state, setField } = useForm();
  return (
    <StepLayout>
      {/* Lighting */}
      <Card>
        <SectionHeader
          title="Lighting"
          description="Define installed lighting parameters."
        />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField label="Lighting Power Density" fieldKey="lpd" hint="Total installed lighting power per unit area">
            <Input
              type="number"
              placeholder="1.5"
              unit="W/ft²"
              value={state.lpd}
              onChange={(e) => setField("lpd", e.target.value)}
            />
          </FormField>
          <FormField label="Annual Lighting Hours" fieldKey="nHoursLighting" hint="Hours per year that lighting is used">
            <Input
              type="number"
              placeholder="2920"
              unit="hrs/yr"
              value={state.nHoursLighting}
              onChange={(e) => setField("nHoursLighting", e.target.value)}
            />
          </FormField>
          <FormField label="Daylighting Controls" fieldKey="daylighting" hint="Is daylighting sensor/control system installed?">
            <Select
              options={YES_NO}
              value={state.daylighting}
              onChange={(e) => setField("daylighting", e.target.value)}
            />
          </FormField>
          <FormField label="LED Percentage" fieldKey="led" hint="Fraction of installed lamps that are LED">
            <Select
              options={LED_OPTIONS}
              value={state.led}
              onChange={(e) => setField("led", e.target.value)}
            />
          </FormField>
        </div>
      </Card>

      {/* Plug Loads */}
      <Card>
        <SectionHeader
          title="Other Plug Loads"
          description="Enter rated wattage for electronics and miscellaneous equipment."
        />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <FormField label="TV Rating" fieldKey="tvRating">
            <Input
              type="number"
              placeholder="200"
              unit="W"
              value={state.tvRating}
              onChange={(e) => setField("tvRating", e.target.value)}
            />
          </FormField>
          <FormField label="Office Equipment Rating" fieldKey="officeEqpRating">
            <Input
              type="number"
              placeholder="300"
              unit="W"
              value={state.officeEqpRating}
              onChange={(e) => setField("officeEqpRating", e.target.value)}
            />
          </FormField>
          <FormField label="Miscellaneous Plug Loads" fieldKey="miscPlugLoadRating">
            <Input
              type="number"
              placeholder="500"
              unit="W"
              value={state.miscPlugLoadRating}
              onChange={(e) => setField("miscPlugLoadRating", e.target.value)}
            />
          </FormField>
        </div>
      </Card>
    </StepLayout>
  );
}
