"use client";

import React from "react";
import { useForm } from "@/context/FormContext";
import { StepLayout } from "@/components/StepLayout";
import { FormField } from "@/components/ui/FormField";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import {
  COOLING_EQUIPMENT,
  COOLING_EFF_OPTIONS,
  HEATING_EQUIPMENT,
  HEATING_EFF_OPTIONS,
  DHW_SYSTEM_TYPES,
  NIGHT_SETBACK_OPTIONS,
  YES_NO,
} from "@/data/options";

export function HeatingCoolingStep() {
  const { state, setField } = useForm();
  const coolingEffOptions = COOLING_EFF_OPTIONS[state.coolingEqp] ?? [];
  const heatingEffOptions = HEATING_EFF_OPTIONS[state.heatingEqp] ?? [];
  const showCoolingCustom = state.coolingEff === "Other..";
  const showHeatingCustom = state.heatingEff === "Other..";

  return (
    <StepLayout>
      {/* Cooling */}
      <Card>
        <SectionHeader
          title="Cooling"
          description="Define the cooling equipment type, efficiency, and thermostat setpoint."
        />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField label="Cooling Equipment" fieldKey="coolingEqp" required>
            <Select
              options={COOLING_EQUIPMENT}
              placeholder="Select cooling equipment…"
              value={state.coolingEqp}
              onChange={(e) => {
                setField("coolingEqp", e.target.value);
                setField("coolingEff", "");
              }}
            />
          </FormField>

          {state.coolingEqp && state.coolingEqp !== "NoCooling" && (
            <FormField label="Cooling Efficiency (SEER2)" fieldKey="coolingEff">
              <Select
                options={coolingEffOptions}
                placeholder="Select efficiency…"
                value={state.coolingEff}
                onChange={(e) => setField("coolingEff", e.target.value)}
              />
            </FormField>
          )}

          {showCoolingCustom && (
            <FormField label="Custom SEER2 Value" fieldKey="coolingEffCustom" hint="Enter the SEER2 rating manually">
              <Input
                type="number"
                placeholder="15.0"
                value={state.coolingEffCustom}
                onChange={(e) => setField("coolingEffCustom", e.target.value)}
              />
            </FormField>
          )}

          <FormField label="Cooling Setpoint" fieldKey="tspc" hint="Indoor thermostat cooling set temperature">
            <Input
              type="number"
              placeholder="75"
              unit="°F"
              value={state.tspc}
              onChange={(e) => setField("tspc", e.target.value)}
            />
          </FormField>
        </div>
      </Card>

      {/* Heating */}
      <Card>
        <SectionHeader
          title="Heating"
          description="Define the heating equipment type, efficiency, setpoint, and night setback."
        />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField label="Heating Equipment" fieldKey="heatingEqp" required>
            <Select
              options={HEATING_EQUIPMENT}
              placeholder="Select heating equipment…"
              value={state.heatingEqp}
              onChange={(e) => {
                setField("heatingEqp", e.target.value);
                setField("heatingEff", "");
              }}
            />
          </FormField>

          {state.heatingEqp && state.heatingEqp !== "NoHeating" && (
            <FormField label="Heating Efficiency" fieldKey="heatingEff">
              <Select
                options={heatingEffOptions}
                placeholder="Select efficiency…"
                value={state.heatingEff}
                onChange={(e) => setField("heatingEff", e.target.value)}
              />
            </FormField>
          )}

          {showHeatingCustom && (
            <FormField label="Custom Efficiency Value" fieldKey="heatingEffCustom">
              <Input
                type="number"
                placeholder="92.0"
                value={state.heatingEffCustom}
                onChange={(e) => setField("heatingEffCustom", e.target.value)}
              />
            </FormField>
          )}

          <FormField label="Heating Setpoint" fieldKey="tsph">
            <Input
              type="number"
              placeholder="70"
              unit="°F"
              value={state.tsph}
              onChange={(e) => setField("tsph", e.target.value)}
            />
          </FormField>

          <FormField label="Night Setback" fieldKey="nightSetback" hint="Temperature offset during setback period">
            <Select
              options={NIGHT_SETBACK_OPTIONS}
              value={state.nightSetback}
              onChange={(e) => setField("nightSetback", e.target.value)}
            />
          </FormField>

          <FormField label="Night Setback Hours" fieldKey="nNightSetbackHours" hint="Hours per day with setback active">
            <Input
              type="number"
              placeholder="8"
              unit="hrs/day"
              value={state.nNightSetbackHours}
              onChange={(e) => setField("nNightSetbackHours", e.target.value)}
            />
          </FormField>
        </div>
      </Card>
    </StepLayout>
  );
}

export function HotWaterOtherStep() {
  const { state, setField } = useForm();
  return (
    <StepLayout>
      {/* Domestic Hot Water */}
      <Card>
        <SectionHeader
          title="Domestic Hot Water (DHW)"
          description="Specify the hot water system type and storage tank size."
        />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField label="DHW System Type" fieldKey="dhwSystemType" required>
            <Select
              options={DHW_SYSTEM_TYPES}
              placeholder="Select DHW system…"
              value={state.dhwSystemType}
              onChange={(e) => setField("dhwSystemType", e.target.value)}
            />
          </FormField>

          {state.dhwSystemType && state.dhwSystemType !== "NoDHWSystem" && (
            <FormField label="Tank Volume" fieldKey="dhwTankVol" hint="Domestic hot water storage tank size">
              <Input
                type="number"
                placeholder="50"
                unit="gal"
                value={state.dhwTankVol}
                onChange={(e) => setField("dhwTankVol", e.target.value)}
              />
            </FormField>
          )}
        </div>
      </Card>

      {/* Other Mechanical Equipment */}
      <Card>
        <SectionHeader
          title="Other Mechanical Equipment"
          description="Additional mechanical systems that affect building energy use."
        />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField label="Economizer" fieldKey="economizer" hint="Air-side economizer for free cooling">
            <Select
              options={YES_NO}
              value={state.economizer}
              onChange={(e) => setField("economizer", e.target.value)}
            />
          </FormField>

          <FormField label="Swamp Cooler (Evaporative)" fieldKey="swampCooler" hint="Evaporative cooling system">
            <Select
              options={["No"]}
              value={state.swampCooler}
              onChange={(e) => setField("swampCooler", e.target.value)}
            />
          </FormField>
        </div>
      </Card>
    </StepLayout>
  );
}
