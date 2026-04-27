"use client";

import React, { useState, useCallback } from "react";
import { useForm } from "@/context/FormContext";
import { API } from "@/utils/api";

const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

const THIS_YEAR = new Date().getFullYear();
const YEAR_OPTIONS = Array.from({ length: 20 }, (_, i) => THIS_YEAR - 1 - i);

interface RowData {
  kwh1: string; therms1: string;
  kwh2: string; therms2: string;
  kwh3: string; therms3: string;
}

const emptyRow = (): RowData => ({ kwh1: "", therms1: "", kwh2: "", therms2: "", kwh3: "", therms3: "" });

type SaveStatus = "idle" | "saving" | "saved" | "error";

export function UtilityDataEntry() {
  const { state, setUtilUploaded, setUtilityData } = useForm();
  const projectName = state.projectName.trim();

  const [year1, setYear1] = useState(THIS_YEAR - 1);
  const [year2, setYear2] = useState(THIS_YEAR - 1);
  const [year3, setYear3] = useState(THIS_YEAR - 1);
  const [rows, setRows] = useState<RowData[]>(() => MONTHS.map(emptyRow));
  const [saveStatus, setSaveStatus] = useState<SaveStatus>("idle");
  const [errorMsg, setErrorMsg] = useState("");

  const updateCell = useCallback((monthIdx: number, field: keyof RowData, value: string) => {
    setRows((prev) => {
      const next = [...prev];
      next[monthIdx] = { ...next[monthIdx], [field]: value };
      return next;
    });
  }, []);

  async function handleSave() {
    if (!projectName) {
      setErrorMsg("Enter a project name above before saving utility data.");
      setSaveStatus("error");
      return;
    }

    setSaveStatus("saving");
    setErrorMsg("");

    try {
      const res = await fetch(
        `${API}/save-utility-data/${encodeURIComponent(projectName)}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ year1, year2, year3, rows }),
        }
      );

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(err.detail ?? "Save failed");
      }

      setSaveStatus("saved");
      setUtilUploaded(`${projectName}_UtilityData.csv`);
      setUtilityData({ year1, year2, year3, rows });
    } catch (err: unknown) {
      setSaveStatus("error");
      setErrorMsg(err instanceof Error ? err.message : "Save failed");
    }
  }

  return (
    <div className="space-y-4">
      {/* Year selectors */}
      <div className="grid grid-cols-3 gap-3">
        {([
          ["Year 1", year1, setYear1],
          ["Year 2", year2, setYear2],
          ["Year 3", year3, setYear3],
        ] as [string, number, (v: number) => void][]).map(([label, val, setter]) => (
          <div key={label}>
            <label className="block text-xs font-semibold text-app-text-muted mb-1">{label}</label>
            <select
              value={val}
              onChange={(e) => setter(Number(e.target.value))}
              className="w-full rounded-lg border border-border bg-white px-3 py-2 text-sm text-app-text focus:outline-none focus:ring-2 focus:ring-brand-300"
            >
              {YEAR_OPTIONS.map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </div>
        ))}
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-border">
        <table className="min-w-full text-xs">
          <thead className="bg-brand-50">
            <tr>
              <th className="px-3 py-2 text-left font-semibold text-app-text-muted w-24">Month</th>
              <th className="px-2 py-2 text-center font-semibold text-brand-700">Y1 kWh</th>
              <th className="px-2 py-2 text-center font-semibold text-brand-700">Y1 Therms</th>
              <th className="px-2 py-2 text-center font-semibold text-app-text-muted border-l border-border">Y2 kWh</th>
              <th className="px-2 py-2 text-center font-semibold text-app-text-muted">Y2 Therms</th>
              <th className="px-2 py-2 text-center font-semibold text-app-text-muted border-l border-border">Y3 kWh</th>
              <th className="px-2 py-2 text-center font-semibold text-app-text-muted">Y3 Therms</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-brand-50">
            {MONTHS.map((month, i) => (
              <tr key={month} className="hover:bg-brand-50/40 transition-colors">
                <td className="px-3 py-1.5 font-medium text-app-text whitespace-nowrap">{month}</td>
                {(["kwh1", "therms1", "kwh2", "therms2", "kwh3", "therms3"] as (keyof RowData)[]).map((field, fi) => (
                  <td key={field} className={`px-1.5 py-1 ${fi === 2 || fi === 4 ? "border-l border-border" : ""}`}>
                    <input
                      type="number"
                      min="0"
                      step="any"
                      placeholder="–"
                      value={rows[i][field]}
                      onChange={(e) => updateCell(i, field, e.target.value)}
                      className="w-full min-w-[64px] rounded-md border border-transparent bg-transparent px-2 py-1 text-center text-app-text
                        focus:border-brand-300 focus:bg-white focus:outline-none focus:ring-1 focus:ring-brand-200
                        hover:border-border transition-all placeholder-app-text-muted/40"
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Save button + status */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={handleSave}
          disabled={saveStatus === "saving" || !projectName}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all shadow-sm
            ${saveStatus === "saving" || !projectName
              ? "bg-bg-muted text-app-text-muted cursor-not-allowed"
              : saveStatus === "saved"
              ? "bg-brand-500 text-white hover:bg-brand-600"
              : "bg-primary text-white hover:bg-primary/90"
            }`}
        >
          {saveStatus === "saving" ? (
            <>
              <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
              </svg>
              Saving…
            </>
          ) : saveStatus === "saved" ? (
            <>
              <svg viewBox="0 0 24 24" fill="none" className="w-4 h-4">
                <path d="M5 13l4 4L19 7" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              Saved
            </>
          ) : (
            "Save Utility Data"
          )}
        </button>

        {saveStatus === "error" && (
          <p className="text-xs text-red-600 font-medium">{errorMsg}</p>
        )}
        {saveStatus === "saved" && (
          <p className="text-xs text-brand-600">
            Utility data saved as <span className="font-mono font-semibold">{projectName}_UtilityData.csv</span>
          </p>
        )}
        {!projectName && saveStatus !== "saving" && (
          <p className="text-xs text-app-text-muted">Set a project name first</p>
        )}
      </div>
    </div>
  );
}
