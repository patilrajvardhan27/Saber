"use client";

import React from "react";
import { StepLayout } from "@/components/StepLayout";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { SectionHeader } from "@/components/ui/SectionHeader";

function PlaceholderChart({ label }: { label: string }) {
  return (
    <div className="h-56 rounded-lg border-2 border-dashed border-border flex flex-col items-center justify-center gap-2 bg-bg-muted">
      <svg viewBox="0 0 48 48" fill="none" className="w-10 h-10 text-app-text-light">
        <rect x="4"  y="28" width="8" height="16" rx="2" fill="currentColor" opacity="0.4" />
        <rect x="14" y="20" width="8" height="24" rx="2" fill="currentColor" opacity="0.6" />
        <rect x="24" y="10" width="8" height="34" rx="2" fill="currentColor" opacity="0.8" />
        <rect x="34" y="16" width="8" height="28" rx="2" fill="currentColor" opacity="0.5" />
      </svg>
      <p className="text-sm text-app-text-light font-medium">{label}</p>
      <p className="text-xs text-app-text-light">Run analysis to generate chart</p>
    </div>
  );
}

export function WeatherDataStep() {
  return (
    <StepLayout>
      <Card>
        <div className="flex items-start justify-between gap-4 mb-4">
          <SectionHeader
            title="Weather Data"
            description="Retrieve weather data from the nearest NOAA weather station based on the building location."
            className="mb-0"
          />
          <Button variant="accent" size="sm" className="flex-shrink-0">
            Get Weather Data
          </Button>
        </div>
        <PlaceholderChart label="Annual Temperature Profile" />
      </Card>
    </StepLayout>
  );
}

export function TempAnalysisStep() {
  return (
    <StepLayout>
      <Card>
        <SectionHeader
          title="Temperature Analysis"
          description="Temperature-based change-point model showing heating and cooling energy as a function of outdoor temperature."
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-semibold text-primary mb-2">Heating Model</p>
            <PlaceholderChart label="Heating Change-Point Analysis" />
          </div>
          <div>
            <p className="text-xs font-semibold text-primary mb-2">Cooling Model</p>
            <PlaceholderChart label="Cooling Change-Point Analysis" />
          </div>
        </div>
      </Card>
    </StepLayout>
  );
}

export function DegreeDayStep() {
  return (
    <StepLayout>
      <Card>
        <SectionHeader
          title="Degree Day Analysis"
          description="Degree-day based energy model correlating consumption with heating and cooling degree days."
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-semibold text-primary mb-2">HDD-Based Model</p>
            <PlaceholderChart label="Heating Degree Day Analysis" />
          </div>
          <div>
            <p className="text-xs font-semibold text-primary mb-2">CDD-Based Model</p>
            <PlaceholderChart label="Cooling Degree Day Analysis" />
          </div>
        </div>
      </Card>
    </StepLayout>
  );
}

export function EndUseStep() {
  return (
    <StepLayout>
      <Card>
        <SectionHeader
          title="End-Use Energy Breakdown"
          description="Estimated annual energy end-use breakdown based on building inputs."
        />
        <PlaceholderChart label="End-Use Energy Breakdown" />
      </Card>
    </StepLayout>
  );
}

export function ModelComparisonStep() {
  return (
    <StepLayout nextLabel="Proceed to ECM Evaluation">
      <Card>
        <SectionHeader
          title="Model Comparison"
          description="Comparison of simulated vs. metered energy for model validation."
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-semibold text-primary mb-2">Electricity (kWh)</p>
            <PlaceholderChart label="kWh Model vs. Meter" />
          </div>
          <div>
            <p className="text-xs font-semibold text-primary mb-2">Natural Gas (Therms)</p>
            <PlaceholderChart label="Therms Model vs. Meter" />
          </div>
        </div>
      </Card>
    </StepLayout>
  );
}
