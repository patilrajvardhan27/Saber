"use client";

import React from "react";
import { useForm } from "@/context/FormContext";
import { StepLayout } from "@/components/StepLayout";
import { FormField } from "@/components/ui/FormField";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { YES_NO, LED_OPTIONS } from "@/data/options";

export function AppliancesStep() {
  const { state, setField } = useForm();
  return (
    <StepLayout>
      <Card>
        <SectionHeader
          title="Equipment Power Density"
          description="Total installed equipment power per unit floor area. EPD covers all electric plug loads — appliances, office equipment, and miscellaneous devices. GPD covers gas cooking equipment; leave it blank if there is no gas cooking. Default EPD of 1.0 W/ft² is appropriate for most residential and small commercial buildings."
        />
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <FormField
            label="Equipment Power Density (EPD)"
            fieldKey="epd"
            hint="Sum of all electric plug loads normalised by floor area"
          >
            <Input
              type="number"
              placeholder="1.0"
              unit="W/ft²"
              value={state.epd}
              onChange={(e) => setField("epd", e.target.value)}
            />
          </FormField>
          <FormField
            label="Gas Power Density (GPD)"
            fieldKey="gpd"
            hint="Gas cooking equipment power per floor area — leave blank if none"
          >
            <Input
              type="number"
              placeholder="0"
              unit="W/ft²"
              value={state.gpd}
              onChange={(e) => setField("gpd", e.target.value)}
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
      <Card>
        <SectionHeader
          title="Lighting"
          description="Define installed lighting parameters."
        />
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <FormField label="Lighting Power Density" fieldKey="lpd" hint="Total installed lighting power per unit area">
            <Input
              type="number"
              placeholder="1.5"
              unit="W/ft²"
              value={state.lpd}
              onChange={(e) => setField("lpd", e.target.value)}
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
    </StepLayout>
  );
}
