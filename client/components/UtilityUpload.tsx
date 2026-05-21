"use client";

import React, { useRef, useState, DragEvent } from "react";
import { useForm } from "@/context/FormContext";
import type { UtilityData, UtilityRow } from "@/context/FormContext";
import { API } from "@/utils/api";

type Status = "idle" | "loading" | "success" | "error";

interface UtilityUploadProps {
  projectName?: string;
}

function parseUtilityCsv(text: string): UtilityData | null {
  const lines = text.trim().split(/\r?\n/);
  if (lines.length < 2) return null;

  const headers = lines[0].split(",");

  // Map "Year N" → column indices for kWh and Therms, plus the actual calendar year
  const slots: Record<number, { kwhIdx: number; thermIdx: number; calYear: number }> = {};

  headers.forEach((h, i) => {
    const slotMatch = h.match(/Year\s+(\d+)/i);
    const calYearMatch = h.match(/(\d{4})/);
    if (!slotMatch || !calYearMatch) return;
    const slot = parseInt(slotMatch[1]);     // 1, 2, or 3
    const calYear = parseInt(calYearMatch[0]);
    if (!slots[slot]) slots[slot] = { kwhIdx: -1, thermIdx: -1, calYear };
    if (h.includes("kWh"))   slots[slot].kwhIdx   = i;
    if (h.includes("Therms")) slots[slot].thermIdx = i;
  });

  if (!slots[1]) return null;

  const year1 = slots[1]?.calYear ?? new Date().getFullYear() - 1;
  const year2 = slots[2]?.calYear ?? year1;
  const year3 = slots[3]?.calYear ?? year1;

  const dataLines = lines.slice(1).filter(l => l.trim());
  const rows: UtilityRow[] = dataLines.slice(0, 12).map(line => {
    const cells = line.split(",");
    const get = (idx: number) => {
      if (idx < 0) return "";
      const v = cells[idx]?.trim();
      return (!v || v.toLowerCase() === "nan" || v === "") ? "" : v;
    };
    return {
      kwh1:    get(slots[1]?.kwhIdx ?? -1),
      therms1: get(slots[1]?.thermIdx ?? -1),
      kwh2:    get(slots[2]?.kwhIdx ?? -1),
      therms2: get(slots[2]?.thermIdx ?? -1),
      kwh3:    get(slots[3]?.kwhIdx ?? -1),
      therms3: get(slots[3]?.thermIdx ?? -1),
    };
  });

  while (rows.length < 12) {
    rows.push({ kwh1: "", therms1: "", kwh2: "", therms2: "", kwh3: "", therms3: "" });
  }

  return { year1, year2, year3, rows };
}

export function UtilityUpload({ projectName: projectNameProp }: UtilityUploadProps = {}) {
  const { state, pklProjectName, setUtilUploaded, setUtilityData, utilFileName } = useForm();
  const resolvedProjectName = projectNameProp || pklProjectName || state.projectName;
  const inputRef = useRef<HTMLInputElement>(null);
  const [status, setStatus] = useState<Status>(utilFileName ? "success" : "idle");
  const [fileName, setFileName] = useState<string>(utilFileName);
  const [errorMsg, setErrorMsg] = useState<string>("");
  const [dragging, setDragging] = useState(false);

  async function handleFile(file: File) {
    if (!file.name.endsWith(".csv")) {
      setStatus("error");
      setErrorMsg("Only CSV files are accepted (e.g. LakewoodTestCase_UtilityData.csv).");
      return;
    }

    if (!resolvedProjectName) {
      setStatus("error");
      setErrorMsg("Please set a project name first so the utility data can be saved.");
      return;
    }

    setFileName(file.name);
    setStatus("loading");
    setErrorMsg("");

    // Parse CSV content client-side so the data is available for the PDF export
    const csvText = await file.text();
    const parsed = parseUtilityCsv(csvText);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API}/upload-utility/${encodeURIComponent(resolvedProjectName)}`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(err.detail ?? "Upload failed");
      }

      setStatus("success");
      setUtilUploaded(file.name);
      if (parsed) setUtilityData(parsed);
    } catch (err: unknown) {
      setStatus("error");
      setErrorMsg(err instanceof Error ? err.message : "Upload failed");
    }
  }

  function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
    e.target.value = "";
  }

  function onDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  }

  function onDragOver(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragging(true);
  }

  function onDragLeave() {
    setDragging(false);
  }

  function reset() {
    setStatus("idle");
    setFileName("");
    setErrorMsg("");
  }

  return (
    <div>
      <input
        ref={inputRef}
        type="file"
        accept=".csv"
        className="hidden"
        onChange={onFileChange}
      />

      <div
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        className={`relative flex flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed px-6 py-5 text-center transition-all duration-200
          ${dragging
            ? "border-brand-500 bg-brand-50"
            : status === "success"
            ? "border-brand-400 bg-brand-50"
            : status === "error"
            ? "border-red-300 bg-red-50"
            : "border-border bg-bg-muted hover:border-brand-400 hover:bg-brand-50/60"
          }`}
      >
        {/* Icon */}
        {status === "success" ? (
          <div className="w-9 h-9 rounded-full bg-brand-100 flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5 text-brand-700">
              <path d="M5 13l4 4L19 7" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
        ) : status === "error" ? (
          <div className="w-9 h-9 rounded-full bg-red-100 flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5 text-red-500">
              <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </div>
        ) : status === "loading" ? (
          <div className="w-9 h-9 rounded-full bg-brand-100 flex items-center justify-center">
            <svg className="w-5 h-5 text-brand-600 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
            </svg>
          </div>
        ) : (
          <div className="w-9 h-9 rounded-full bg-brand-100 flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5 text-brand-500">
              <path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M16 10l-4-4-4 4M12 6v10" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
        )}

        {status === "idle" && (
          <div>
            <p className="text-sm font-semibold text-app-text">
              Drop a <span className="text-brand-600 font-mono">*_UtilityData.csv</span> file here, or{" "}
              <button
                type="button"
                onClick={() => inputRef.current?.click()}
                className="text-brand-600 underline underline-offset-2 hover:text-brand-700 font-semibold"
              >
                browse
              </button>
            </p>
            <p className="text-xs text-app-text-muted mt-1">
              Monthly utility data with kWh and Therms columns — e.g.{" "}
              <span className="font-mono">LakewoodTestCase_UtilityData.csv</span>
            </p>
          </div>
        )}

        {status === "loading" && (
          <p className="text-sm font-medium text-brand-700">
            Uploading <span className="font-semibold">{fileName}</span>…
          </p>
        )}

        {status === "success" && (
          <div className="space-y-1">
            <p className="text-sm font-semibold text-brand-700">
              Utility data uploaded — <span className="font-bold">{fileName || utilFileName}</span>
            </p>
            <p className="text-xs text-brand-500">
              Ready for analysis. Proceed to Results to run the energy model.
            </p>
          </div>
        )}

        {status === "error" && (
          <div className="space-y-1">
            <p className="text-sm font-semibold text-red-600">{errorMsg}</p>
            <button
              type="button"
              onClick={reset}
              className="text-xs text-red-400 hover:text-red-600 underline underline-offset-2"
            >
              Try again
            </button>
          </div>
        )}

        {status === "idle" && (
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            className="px-5 py-2 rounded-xl bg-brand-500 text-white text-sm font-semibold hover:bg-brand-600 transition-colors shadow-sm"
          >
            Browse *_UtilityData.csv
          </button>
        )}
      </div>
    </div>
  );
}
