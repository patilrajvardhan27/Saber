"use client";

import React from "react";
import { useForm } from "@/context/FormContext";
import { StepLayout } from "@/components/StepLayout";
import { FormField } from "@/components/ui/FormField";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { RadioGroup } from "@/components/ui/RadioGroup";
import { BUILDING_TYPES } from "@/data/options";
import { PklUpload } from "@/components/PklUpload";
import { UtilityUpload } from "@/components/UtilityUpload";
import { UtilityDataEntry } from "@/components/UtilityDataEntry";

export function ProjectSetupStep() {
  const { state, setField } = useForm();

  return (
    <StepLayout nextDisabled={!state.projectName.trim()}>
      {/* Building Baseline File */}
      <Card>
        <SectionHeader
          title="Building Baseline File"
          description="Pre-fill all building properties from a saved baseline, or enter properties manually in the following steps."
        />
        <div className="mb-4">
          <RadioGroup
            name="inputMethod"
            direction="row"
            value={state.inputMethod}
            onChange={(v) => setField("inputMethod", v as "new" | "existing")}
            options={[
              {
                value: "new",
                label: "Enter manually",
                description: "Fill in building properties step by step",
              },
              {
                value: "existing",
                label: "Upload baseline file",
                description: "Upload a .pkl file to auto-populate fields",
              },
            ]}
          />
        </div>
        {state.inputMethod === "existing" && <PklUpload />}
      </Card>

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
          <FormField label="Location / Address" fieldKey="location" className="sm:col-span-2" hint="Used to find the nearest NOAA weather station for energy analysis">
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

      {/* Utility Data */}
      <Card>
        <SectionHeader
          title="Utility Data"
          description="Provide 12 months of electricity (kWh) and natural gas (Therms) consumption. Up to 3 years can be entered for a stronger energy model."
        />

        <div className="mb-4">
          <RadioGroup
            name="utilDataSource"
            direction="row"
            value={state.utilDataSource}
            onChange={(v) => setField("utilDataSource", v as "enter" | "existing")}
            options={[
              {
                value: "enter",
                label: "Enter utility data",
                description: "Type monthly kWh and Therms directly",
              },
              {
                value: "existing",
                label: "Use existing file",
                description: "Upload a previously saved *_UtilityData.csv",
              },
            ]}
          />
        </div>

        {state.utilDataSource === "enter" ? (
          <UtilityDataEntry />
        ) : (
          <UtilityUpload />
        )}
      </Card>
    </StepLayout>
  );
}
