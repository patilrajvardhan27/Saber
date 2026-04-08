"use client";

import React from "react";
import { useForm } from "@/context/FormContext";
import { StepLayout } from "@/components/StepLayout";
import { FormField } from "@/components/ui/FormField";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { RadioGroup } from "@/components/ui/RadioGroup";
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
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField label="Project Name" required>
            <Input
              placeholder="e.g. Community Church Audit 2024"
              value={state.projectName}
              onChange={(e) => setField("projectName", e.target.value)}
            />
          </FormField>
          <FormField label="Building Type" required>
            <Select
              options={BUILDING_TYPES}
              placeholder="Select building type…"
              value={state.buildingType}
              onChange={(e) => setField("buildingType", e.target.value)}
            />
          </FormField>
          <FormField label="Location / Address" className="sm:col-span-2">
            <Input
              placeholder="e.g. 123 Main St, Denver, CO"
              value={state.location}
              onChange={(e) => setField("location", e.target.value)}
            />
          </FormField>
        </div>
      </Card>

      {/* Building Properties */}
      <Card>
        <SectionHeader
          title="Building Properties Input"
          description="Choose how to provide building property data."
        />
        <RadioGroup
          name="inputMethod"
          value={state.inputMethod}
          onChange={(v) => setField("inputMethod", v as "new" | "existing")}
          options={[
            {
              value: "new",
              label: "Provide New Inputs",
              description: "Enter building properties manually using the step wizard.",
            },
            {
              value: "existing",
              label: "Use Existing Input File",
              description: "Load a previously saved building properties CSV or pickle file.",
            },
          ]}
        />
        {state.inputMethod === "existing" && (
          <div className="mt-4">
            <FormField
              label="Building Properties File Path"
              hint="Provide the absolute path to your .csv or .pkl building properties file."
            >
              <Input
                placeholder="/path/to/BldgProperties.csv"
                value={state.bldgPropInputFile}
                onChange={(e) => setField("bldgPropInputFile", e.target.value)}
              />
            </FormField>
          </div>
        )}
      </Card>

      {/* Utility Data */}
      <Card>
        <SectionHeader
          title="Utility Data Source"
          description="Specify how monthly utility consumption data will be provided."
        />
        <RadioGroup
          name="utilDataSource"
          value={state.utilDataSource}
          onChange={(v) => setField("utilDataSource", v as "enter" | "existing")}
          options={[
            {
              value: "enter",
              label: "Enter Utility Data Manually",
              description: "Input monthly kWh and therm consumption values.",
            },
            {
              value: "existing",
              label: "Use Existing Utility Data File",
              description: "Load a CSV file with historical utility consumption data.",
            },
          ]}
        />
        {state.utilDataSource === "existing" && (
          <div className="mt-4">
            <FormField
              label="Utility Data File Path"
              hint="CSV file with columns for date, kWh, and therms."
            >
              <Input
                placeholder="/path/to/UtilityData.csv"
                value={state.utilDataSourceFile}
                onChange={(e) => setField("utilDataSourceFile", e.target.value)}
              />
            </FormField>
          </div>
        )}
        {state.utilDataSource === "enter" && (
          <div className="mt-4 grid grid-cols-2 gap-4">
            <FormField label="Cost per Therm" hint="Natural gas rate ($/therm)">
              <Input
                type="number"
                placeholder="0.00"
                unit="$/therm"
                value={state.thermCost}
                onChange={(e) => setField("thermCost", e.target.value)}
              />
            </FormField>
            <FormField label="Cost per kWh" hint="Electricity rate ($/kWh)">
              <Input
                type="number"
                placeholder="0.00"
                unit="$/kWh"
                value={state.kWhCost}
                onChange={(e) => setField("kWhCost", e.target.value)}
              />
            </FormField>
          </div>
        )}
      </Card>
    </StepLayout>
  );
}
