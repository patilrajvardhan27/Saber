"use client";

import React from "react";
import { useForm } from "@/context/FormContext";
import { StepLayout } from "@/components/StepLayout";
import { FormField } from "@/components/ui/FormField";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { ECM_MEASURES, ECM_MEASURE_OPTIONS } from "@/data/options";
import type { FormField as FormFieldType } from "@/types/form";

const COST_ROWS = [
  { key: "wallInsulation",    label: "Wall Insulation" },
  { key: "infiltration",      label: "Infiltration Sealing" },
  { key: "ceilingInsulation", label: "Ceiling Insulation" },
  { key: "windowMaterial",    label: "Window Replacement" },
  { key: "nightSetback",      label: "Night Setback Thermostat" },
  { key: "daylighting",       label: "Daylighting Controls" },
  { key: "economizer",        label: "Economizer" },
  { key: "occupancySensor",   label: "Occupancy Sensors" },
  { key: "led",               label: "LED Lighting Upgrade" },
  { key: "equipLoad",         label: "Reduce Equipment Load" },
  { key: "coolingEff",        label: "Cooling Efficiency Upgrade" },
  { key: "heatingEqp",        label: "Heating Equipment Replacement" },
  { key: "heatingEff",        label: "Heating Efficiency Upgrade" },
];

export function FinancialsStep() {
  const { state, setField } = useForm();
  return (
    <StepLayout>
      {/* Financial Parameters */}
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

      {/* ECM Cost Data */}
      <Card>
        <div className="flex items-start justify-between gap-4 mb-4">
          <SectionHeader
            title="ECM Cost Data"
            description="Enter per-unit and fixed installed costs for each energy conservation measure."
            className="mb-0"
          />
          <div className="flex gap-2 flex-shrink-0">
            <Button variant="secondary" size="sm">Reset Defaults</Button>
            <Button variant="primary" size="sm">Set Cost Data</Button>
          </div>
        </div>
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg-muted border-b border-border">
                <th className="text-left px-4 py-2.5 font-semibold text-app-text text-xs w-52">Measure</th>
                <th className="text-left px-4 py-2.5 font-semibold text-app-text text-xs">Cost per Unit ($/ft²)</th>
                <th className="text-left px-4 py-2.5 font-semibold text-app-text text-xs">Fixed Cost ($)</th>
                <th className="text-left px-4 py-2.5 font-semibold text-app-text text-xs">Lifetime (yrs)</th>
              </tr>
            </thead>
            <tbody>
              {COST_ROWS.map((row, i) => (
                <tr key={row.key} className={i % 2 === 0 ? "bg-bg-card" : "bg-bg-muted"}>
                  <td className="px-4 py-2 font-medium text-app-text text-xs">{row.label}</td>
                  <td className="px-4 py-1.5">
                    <input type="number" placeholder="0.00" className="form-input !py-1 !text-xs w-28" />
                  </td>
                  <td className="px-4 py-1.5">
                    <input type="number" placeholder="0.00" className="form-input !py-1 !text-xs w-28" />
                  </td>
                  <td className="px-4 py-1.5">
                    <input type="number" placeholder="20" className="form-input !py-1 !text-xs w-20" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </StepLayout>
  );
}

export function ECMSelectionStep() {
  const { state, setField } = useForm();
  return (
    <StepLayout>
      <Card>
        <div className="flex items-start justify-between gap-4 mb-4">
          <SectionHeader
            title="ECM Selection"
            description="Select the upgraded option for each measure, then evaluate individual measures or the full package."
            className="mb-0"
          />
          <div className="flex gap-2 flex-shrink-0">
            <Button variant="secondary" size="sm">Evaluate Individual</Button>
            <Button variant="primary" size="sm">Evaluate Package</Button>
          </div>
        </div>
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg-muted border-b border-border">
                <th className="text-left px-4 py-2.5 font-semibold text-app-text text-xs w-56">Measure</th>
                <th className="text-left px-4 py-2.5 font-semibold text-app-text text-xs">Baseline</th>
                <th className="text-left px-4 py-2.5 font-semibold text-app-text text-xs">ECM Option</th>
              </tr>
            </thead>
            <tbody>
              {ECM_MEASURES.map((measure, i) => {
                const options = ECM_MEASURE_OPTIONS[measure.key] ?? [];
                return (
                  <tr key={measure.key} className={i % 2 === 0 ? "bg-bg-card" : "bg-bg-muted"}>
                    <td className="px-4 py-2 font-medium text-app-text text-xs">{measure.label}</td>
                    <td className="px-4 py-2 text-xs text-app-text-muted">Current setting</td>
                    <td className="px-4 py-1.5">
                      <Select
                        options={options}
                        placeholder="Select ECM option…"
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

export function ECMResultsStep() {
  const { state } = useForm();

  const metrics = [
    { label: "Package Life-Cycle Cost (LCC)", value: state.packageLCC,             unit: "$", color: "text-primary" },
    { label: "Total Installed Cost (TIC)",    value: state.packageTIC,             unit: "$", color: "text-warning" },
    { label: "Electricity Savings",           value: state.packageKWhPctChange,    unit: "%", color: "text-success" },
    { label: "Natural Gas Savings",           value: state.packageThermsPctChange, unit: "%", color: "text-accent"  },
  ];

  return (
    <StepLayout nextLabel="Save & Export">
      <Card>
        <SectionHeader
          title="Results Summary"
          description="Package-level energy and cost performance metrics after ECM evaluation."
        />
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-5">
          {metrics.map((m) => (
            <div key={m.label} className="card p-4 text-center">
              <p className={`text-2xl font-bold ${m.color}`}>
                {m.value ? `${m.value}${m.unit}` : "—"}
              </p>
              <p className="text-xs text-app-text-muted mt-1 leading-tight">{m.label}</p>
            </div>
          ))}
        </div>
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" size="sm">Save Individual Results</Button>
          <Button variant="primary" size="sm">Save Package Results</Button>
        </div>
      </Card>
    </StepLayout>
  );
}
