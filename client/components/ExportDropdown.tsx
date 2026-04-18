"use client";

import React, { useState, useRef, useEffect } from "react";
import { useForm } from "@/context/FormContext";
import { exportPdf } from "@/utils/exportPdf";
import { exportPkl } from "@/utils/exportPkl";

export function ExportDropdown() {
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState<"idle" | "pdf" | "pkl">("idle");
  const [error, setError] = useState("");
  const ref = useRef<HTMLDivElement>(null);
  const { state, pklProjectName, analysisPlots, ecmMetrics, ecmPlots } = useForm();

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  async function handlePdf() {
    setOpen(false);
    setError("");
    setStatus("pdf");
    try {
      await exportPdf({ state, pklProjectName, analysisPlots, ecmMetrics, ecmPlots });
    } catch (e) {
      setError(e instanceof Error ? e.message : "PDF export failed");
    } finally {
      setStatus("idle");
    }
  }

  async function handlePkl() {
    setOpen(false);
    setError("");
    setStatus("pkl");
    try {
      await exportPkl(state, pklProjectName);
    } catch (e) {
      setError(e instanceof Error ? e.message : "PKL export failed");
    } finally {
      setStatus("idle");
    }
  }

  const busy = status !== "idle";

  return (
    <div className="flex flex-col items-end gap-2" ref={ref}>
      {error && (
        <p className="text-xs text-red-600 font-medium px-1">{error}</p>
      )}

      <div className="relative">
        {/* Main button */}
        <button
          type="button"
          onClick={() => !busy && setOpen((o) => !o)}
          disabled={busy}
          className={`flex items-center gap-2 px-7 py-3 rounded-xl text-sm font-semibold transition-all select-none ${
            busy
              ? "bg-bg-muted text-app-text-muted cursor-not-allowed border border-border"
              : "bg-brand-500 text-white hover:bg-brand-600 shadow-md hover:shadow-lg"
          }`}
        >
          {busy ? (
            <>
              <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
              </svg>
              {status === "pdf" ? "Generating PDF…" : "Exporting PKL…"}
            </>
          ) : (
            <>
              Save &amp; Export
              <svg
                viewBox="0 0 16 16"
                fill="none"
                className={`w-4 h-4 transition-transform ${open ? "rotate-180" : ""}`}
              >
                <path d="M4 6l4 4 4-4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </>
          )}
        </button>

        {/* Dropdown */}
        {open && !busy && (
          <div className="absolute right-0 bottom-full mb-2 z-50 bg-white rounded-xl border border-brand-100 shadow-xl overflow-hidden min-w-[210px]">
            <button
              type="button"
              onClick={handlePdf}
              className="w-full flex items-center gap-3 px-4 py-3 text-sm text-app-text hover:bg-brand-50 transition-colors text-left border-b border-brand-50"
            >
              {/* PDF icon */}
              <svg viewBox="0 0 20 20" fill="none" className="w-5 h-5 flex-shrink-0 text-red-500">
                <rect x="3" y="1" width="11" height="15" rx="1.5" stroke="currentColor" strokeWidth="1.5"/>
                <path d="M11 1v4.5h3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M6 10h5M6 13h3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                <rect x="2" y="11" width="7" height="8" rx="1" fill="#ef4444" opacity="0.9"/>
                <text x="5.5" y="17.5" fontSize="4.5" fill="white" fontFamily="Arial" fontWeight="bold" textAnchor="middle">PDF</text>
              </svg>
              <div>
                <p className="font-semibold">Export as PDF</p>
                <p className="text-xs text-app-text-muted">Full audit report with charts</p>
              </div>
            </button>

            <button
              type="button"
              onClick={handlePkl}
              className="w-full flex items-center gap-3 px-4 py-3 text-sm text-app-text hover:bg-brand-50 transition-colors text-left"
            >
              {/* PKL / archive icon */}
              <svg viewBox="0 0 20 20" fill="none" className="w-5 h-5 flex-shrink-0 text-brand-600">
                <rect x="2" y="5" width="16" height="12" rx="1.5" stroke="currentColor" strokeWidth="1.5"/>
                <path d="M2 8h16" stroke="currentColor" strokeWidth="1.5"/>
                <path d="M7.5 5V3.5a.5.5 0 01.5-.5h4a.5.5 0 01.5.5V5" stroke="currentColor" strokeWidth="1.5"/>
                <path d="M8 12l2 2 2-2M10 14v-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <div>
                <p className="font-semibold">Export as PKL</p>
                <p className="text-xs text-app-text-muted">Re-uploadable input file</p>
              </div>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
