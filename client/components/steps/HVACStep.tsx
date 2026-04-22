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

const COOLING_IMAGE_MAP: Record<string, string> = {
  "Air Conditioner":    "/hvac/cooling/Air Conditioner.png",
  "Air Source Heat Pump": "/hvac/cooling/Air Source Heat Pump.png",
};

const HEATING_IMAGE_MAP: Record<string, string> = {
  "Gas Furnace":          "/hvac/heating/Gas Furnace.png",
  "Air Source Heat Pump": "/hvac/heating/Air Source Heat Pump.png",
};

const DHW_IMAGE_MAP: Record<string, string> = {
  "Gas Boiler":     "/hvac/dhw/Gas Boiler.png",
  "Electric Heater": "/hvac/dhw/Electric Heater.png",
  "NoDHWSystem":    "/hvac/dhw/NoDHWSystem.png",
};

function EquipmentImageCard({
  label,
  subtitle,
  imgSrc,
  emptyText,
}: {
  label: string;
  subtitle?: string;
  imgSrc: string | null;
  emptyText: string;
}) {
  return (
    <div className="bg-white rounded-2xl shadow-md border border-brand-100 overflow-hidden w-full flex flex-col flex-1 min-h-0">
      <div className="px-4 pt-3 pb-1 border-b border-brand-100 flex-shrink-0">
        <p className="text-xs font-bold text-primary uppercase tracking-wider">{label}</p>
        {subtitle && <p className="text-xs text-app-text-muted mt-0.5 truncate">{subtitle}</p>}
      </div>
      <div className="flex-1 min-h-0 flex items-center justify-center overflow-hidden">
        {imgSrc ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={imgSrc} alt={label} className="w-full h-full object-contain p-4" />
        ) : (
          <div className="flex flex-col items-center justify-center gap-2 text-app-text-muted w-full h-full">
            <svg viewBox="0 0 40 40" fill="none" className="w-8 h-8 opacity-30">
              <rect x="8" y="8" width="24" height="24" rx="4" stroke="currentColor" strokeWidth="2"/>
              <path d="M14 20h12M20 14v12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            <p className="text-xs">{emptyText}</p>
          </div>
        )}
      </div>
    </div>
  );
}

const ASHP = "Air Source Heat Pump";

export function HeatingCoolingStep() {
  const { state, setField } = useForm();
  const coolingEffOptions = COOLING_EFF_OPTIONS[state.coolingEqp] ?? [];
  const heatingEffOptions = HEATING_EFF_OPTIONS[state.heatingEqp] ?? [];
  const showCoolingCustom = state.coolingEff === "Other..";
  const showHeatingCustom = state.heatingEff === "Other..";

  const coolingImg = state.coolingEqp ? (COOLING_IMAGE_MAP[state.coolingEqp] ?? null) : null;
  const heatingImg = state.heatingEqp ? (HEATING_IMAGE_MAP[state.heatingEqp] ?? null) : null;

  const ashpMismatch =
    (state.coolingEqp === ASHP && state.heatingEqp && state.heatingEqp !== ASHP && state.heatingEqp !== "NoHeating") ||
    (state.heatingEqp === ASHP && state.coolingEqp && state.coolingEqp !== ASHP && state.coolingEqp !== "NoCooling");

  function handleCoolingChange(val: string) {
    setField("coolingEqp", val);
    setField("coolingEff", "");
    if (val === ASHP) {
      setField("heatingEqp", ASHP);
      setField("heatingEff", "");
    }
  }

  function handleHeatingChange(val: string) {
    setField("heatingEqp", val);
    setField("heatingEff", "");
    if (val === ASHP) {
      setField("coolingEqp", ASHP);
      setField("coolingEff", "");
    }
  }

  const imagePanel = (
    <div className="flex flex-col gap-5 w-full h-full">
      <EquipmentImageCard
        label="Cooling System"
        subtitle={
          state.coolingEqp === "NoCooling"
            ? "No cooling system"
            : state.coolingEqp
              ? state.coolingEff
                ? `${state.coolingEqp} · ${state.coolingEff}`
                : state.coolingEqp
              : undefined
        }
        imgSrc={coolingImg}
        emptyText="Select cooling equipment to preview"
      />
      <EquipmentImageCard
        label="Heating System"
        subtitle={
          state.heatingEqp === "NoHeating"
            ? "No heating system"
            : state.heatingEqp
              ? state.heatingEff
                ? `${state.heatingEqp} · ${state.heatingEff}`
                : state.heatingEqp
              : undefined
        }
        imgSrc={heatingImg}
        emptyText="Select heating equipment to preview"
      />
    </div>
  );

  return (
    <StepLayout imagePanel={imagePanel}>

      {ashpMismatch && (
        <div className="flex items-start gap-2 px-3 py-2.5 mb-1 rounded-lg bg-amber-50 border border-amber-300 text-xs text-amber-800">
          <svg className="w-3.5 h-3.5 flex-shrink-0 mt-0.5 text-amber-500" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
          </svg>
          <span><span className="font-semibold">Equipment mismatch:</span> An Air Source Heat Pump provides both heating and cooling. Selecting different equipment for each system may produce inconsistent simulation results.</span>
        </div>
      )}

      {/* ── Cooling ── */}
      <Card>
        <SectionHeader
          title="Cooling"
          description="Define the cooling equipment type, efficiency rating, and thermostat setpoint."
        />
        <div className="flex flex-col gap-4">
          <FormField label="Cooling Equipment" fieldKey="coolingEqp" required>
            <Select
              options={COOLING_EQUIPMENT}
              placeholder="Select cooling equipment…"
              value={state.coolingEqp}
              onChange={(e) => handleCoolingChange(e.target.value)}
            />
          </FormField>

          {state.coolingEqp && state.coolingEqp !== "NoCooling" && (
            <div className="grid grid-cols-2 gap-3">
              <FormField label="Cooling Efficiency (SEER2)" fieldKey="coolingEff" hint="Higher SEER2 = more efficient">
                <Select
                  options={coolingEffOptions}
                  placeholder="Select efficiency…"
                  value={state.coolingEff}
                  onChange={(e) => setField("coolingEff", e.target.value)}
                />
              </FormField>

              {showCoolingCustom ? (
                <FormField label="Custom SEER2 Value" fieldKey="coolingEffCustom">
                  <Input
                    type="number"
                    placeholder="15.0"
                    value={state.coolingEffCustom}
                    onChange={(e) => setField("coolingEffCustom", e.target.value)}
                  />
                </FormField>
              ) : (
                <FormField label="Cooling Setpoint" fieldKey="tspc" hint="Thermostat cooling set temperature">
                  <Input
                    type="number"
                    placeholder="75"
                    unit="°F"
                    value={state.tspc}
                    onChange={(e) => setField("tspc", e.target.value)}
                  />
                </FormField>
              )}
            </div>
          )}

          {state.coolingEqp && state.coolingEqp !== "NoCooling" && showCoolingCustom && (
            <FormField label="Cooling Setpoint" fieldKey="tspc" hint="Thermostat cooling set temperature">
              <Input
                type="number"
                placeholder="75"
                unit="°F"
                value={state.tspc}
                onChange={(e) => setField("tspc", e.target.value)}
              />
            </FormField>
          )}

          {state.coolingEqp === "NoCooling" && (
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-blue-50 border border-blue-200 text-xs text-blue-700">
              <span className="w-2 h-2 rounded-full bg-blue-400 flex-shrink-0" />
              No mechanical cooling — building relies on natural ventilation
            </div>
          )}
        </div>
      </Card>

      {/* ── Heating ── */}
      <Card>
        <SectionHeader
          title="Heating"
          description="Define the heating equipment type, efficiency, setpoint, and night setback schedule."
        />
        <div className="flex flex-col gap-4">
          <FormField label="Heating Equipment" fieldKey="heatingEqp" required>
            <Select
              options={HEATING_EQUIPMENT}
              placeholder="Select heating equipment…"
              value={state.heatingEqp}
              onChange={(e) => handleHeatingChange(e.target.value)}
            />
          </FormField>

          {state.heatingEqp && state.heatingEqp !== "NoHeating" && (
            <div className="grid grid-cols-2 gap-3">
              <FormField label="Heating Efficiency" fieldKey="heatingEff" hint="AFUE / COP / HSPF2 rating">
                <Select
                  options={heatingEffOptions}
                  placeholder="Select efficiency…"
                  value={state.heatingEff}
                  onChange={(e) => setField("heatingEff", e.target.value)}
                />
              </FormField>

              {showHeatingCustom ? (
                <FormField label="Custom Efficiency Value" fieldKey="heatingEffCustom">
                  <Input
                    type="number"
                    placeholder="92.0"
                    value={state.heatingEffCustom}
                    onChange={(e) => setField("heatingEffCustom", e.target.value)}
                  />
                </FormField>
              ) : (
                <FormField label="Heating Setpoint" fieldKey="tsph" hint="Thermostat heating set temperature">
                  <Input
                    type="number"
                    placeholder="70"
                    unit="°F"
                    value={state.tsph}
                    onChange={(e) => setField("tsph", e.target.value)}
                  />
                </FormField>
              )}
            </div>
          )}

          {state.heatingEqp && state.heatingEqp !== "NoHeating" && showHeatingCustom && (
            <FormField label="Heating Setpoint" fieldKey="tsph">
              <Input
                type="number"
                placeholder="70"
                unit="°F"
                value={state.tsph}
                onChange={(e) => setField("tsph", e.target.value)}
              />
            </FormField>
          )}

          {state.heatingEqp && state.heatingEqp !== "NoHeating" && (
            <div className="grid grid-cols-2 gap-3">
              <FormField label="Night Setback" fieldKey="nightSetback" hint="Temperature offset during setback">
                <Select
                  options={NIGHT_SETBACK_OPTIONS}
                  value={state.nightSetback}
                  onChange={(e) => setField("nightSetback", e.target.value)}
                />
              </FormField>
              <FormField label="Setback Hours" fieldKey="nNightSetbackHours" hint="Hours per day active">
                <Input
                  type="number"
                  placeholder="8"
                  unit="hrs/day"
                  value={state.nNightSetbackHours}
                  onChange={(e) => setField("nNightSetbackHours", e.target.value)}
                />
              </FormField>
            </div>
          )}

          {state.heatingEqp === "NoHeating" && (
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-orange-50 border border-orange-200 text-xs text-orange-700">
              <span className="w-2 h-2 rounded-full bg-orange-400 flex-shrink-0" />
              No heating system — high energy loss risk in cold climates
            </div>
          )}
        </div>
      </Card>

    </StepLayout>
  );
}

export function HotWaterOtherStep() {
  const { state, setField } = useForm();

  const dhwImg = state.dhwSystemType ? (DHW_IMAGE_MAP[state.dhwSystemType] ?? null) : null;

  const imagePanel = (
    <div className="flex flex-col gap-5 w-full h-full">
      <EquipmentImageCard
        label="DHW System"
        subtitle={
          state.dhwSystemType === "NoDHWSystem"
            ? "No DHW system"
            : state.dhwSystemType
              ? state.dhwTankVol
                ? `${state.dhwSystemType} · ${state.dhwTankVol} gal`
                : state.dhwSystemType
              : undefined
        }
        imgSrc={dhwImg}
        emptyText="Select DHW system to preview"
      />
    </div>
  );

  return (
    <StepLayout imagePanel={imagePanel}>
      {/* Domestic Hot Water */}
      <Card>
        <SectionHeader
          title="Domestic Hot Water (DHW)"
          description="Specify the hot water system type and storage tank size."
        />
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
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
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
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
