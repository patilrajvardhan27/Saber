"use client";

import React from "react";
import { useForm } from "@/context/FormContext";
import { StepLayout } from "@/components/StepLayout";
import { FormField } from "@/components/ui/FormField";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { BUILDING_TYPES } from "@/data/options";
import { PklUpload } from "@/components/PklUpload";

export function ProjectSetupStep() {
  const { state, setField } = useForm();
  return (
    <StepLayout>
      <PklUpload />

      {/* Project Information */}
      <Card>
        <SectionHeader
          title="Project Information"
          description="Provide basic details about the building audit project."
        />
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <FormField label="Project Name" fieldKey="projectName" required>
            <Input
              placeholder="e.g. Community Church Audit 2024"
              value={state.projectName}
              onChange={(e) => setField("projectName", e.target.value)}
            />
          </FormField>
          <FormField label="Building Type" fieldKey="buildingType" required>
            <Select
              options={BUILDING_TYPES}
              placeholder="Select building type…"
              value={state.buildingType}
              onChange={(e) => setField("buildingType", e.target.value)}
            />
          </FormField>
          <FormField label="Location / Address" fieldKey="location" className="sm:col-span-2">
            <Input
              placeholder="e.g. 123 Main St, Denver, CO"
              value={state.location}
              onChange={(e) => setField("location", e.target.value)}
            />
          </FormField>
        </div>
      </Card>

      {/* Utility Rates */}
      <Card>
        <SectionHeader
          title="Utility Rates"
          description="Enter the energy costs used for financial calculations."
        />
        <div className="grid grid-cols-2 gap-3">
          <FormField label="Cost per Therm" fieldKey="thermCost" hint="Natural gas rate ($/therm)">
            <Input
              type="number"
              placeholder="0.00"
              unit="$/therm"
              value={state.thermCost}
              onChange={(e) => setField("thermCost", e.target.value)}
            />
          </FormField>
          <FormField label="Cost per kWh" fieldKey="kWhCost" hint="Electricity rate ($/kWh)">
            <Input
              type="number"
              placeholder="0.00"
              unit="$/kWh"
              value={state.kWhCost}
              onChange={(e) => setField("kWhCost", e.target.value)}
            />
          </FormField>
        </div>
      </Card>
    </StepLayout>
  );
}
