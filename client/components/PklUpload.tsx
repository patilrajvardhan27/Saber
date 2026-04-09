"use client";

import React, { useRef, useState, DragEvent } from "react";
import { useForm } from "@/context/FormContext";
import type { FormState } from "@/types/form";

type Status = "idle" | "loading" | "success" | "error";

export function PklUpload() {
  const { setFields, setPklMeta, setPklFields, goToStep } = useForm();
  const inputRef = useRef<HTMLInputElement>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [fileName, setFileName] = useState<string>("");
  const [fieldCount, setFieldCount] = useState<number>(0);
  const [errorMsg, setErrorMsg] = useState<string>("");
  const [dragging, setDragging] = useState(false);

  async function handleFile(file: File) {
    if (!file.name.toLowerCase().endsWith(".pkl")) {
      setStatus("error");
      setErrorMsg("Only .pkl files are supported.");
      return;
    }

    setFileName(file.name);
    setStatus("loading");
    setErrorMsg("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/upload-pkl", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(err.detail ?? "Upload failed");
      }

      const data = await res.json();
      setFields(data.fields as Partial<FormState>);
      const count = data.count ?? 0;
      setFieldCount(count);
      setStatus("success");
      setPklMeta(file.name, count);
      // Track which specific field keys were populated so inputs can show autofill styling
      const populatedKeys = (data.populated_keys as string[]) ?? [];
      setPklFields(populatedKeys);

      // Auto-advance to step 2 after brief success display
      setTimeout(() => goToStep(2), 1200);
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
    setFieldCount(0);
    setErrorMsg("");
  }

  return (
    <div className="mb-6">
      <input
        ref={inputRef}
        type="file"
        accept=".pkl"
        className="hidden"
        onChange={onFileChange}
      />

      {/* Drop zone */}
      <div
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        className={`relative flex flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed px-6 py-8 text-center transition-all duration-200
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
          <div className="w-12 h-12 rounded-full bg-brand-100 flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6 text-brand-700">
              <path d="M5 13l4 4L19 7" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
        ) : status === "error" ? (
          <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6 text-red-500">
              <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </div>
        ) : status === "loading" ? (
          <div className="w-12 h-12 rounded-full bg-brand-100 flex items-center justify-center">
            <svg className="w-6 h-6 text-brand-600 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
            </svg>
          </div>
        ) : (
          <div className="w-12 h-12 rounded-full bg-brand-100 flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6 text-brand-500">
              <path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M16 10l-4-4-4 4M12 6v10" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
        )}

        {status === "idle" && (
          <div>
            <p className="text-sm font-semibold text-app-text">
              Drop a <span className="text-brand-600">.pkl</span> file here, or{" "}
              <button
                type="button"
                onClick={() => inputRef.current?.click()}
                className="text-brand-600 underline underline-offset-2 hover:text-brand-700 font-semibold"
              >
                browse
              </button>
            </p>
            <p className="text-xs text-app-text-muted mt-1">
              Loads a saved BldgAuditTool properties file and auto-fills all fields
            </p>
          </div>
        )}

        {status === "loading" && (
          <p className="text-sm font-medium text-brand-700">
            Parsing <span className="font-semibold">{fileName}</span>…
          </p>
        )}

        {status === "success" && (
          <div className="space-y-1">
            <p className="text-sm font-semibold text-brand-700">
              {fieldCount} fields populated from{" "}
              <span className="font-bold">{fileName}</span>
            </p>
            <p className="text-xs text-brand-500">
              Advancing to review… adjust any values as needed.
            </p>
            <button
              type="button"
              onClick={reset}
              className="mt-2 text-xs text-app-text-muted hover:text-app-text underline underline-offset-2"
            >
              Upload a different file
            </button>
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
            Browse .pkl file
          </button>
        )}
      </div>

      {status !== "success" && (
        <div className="flex items-center gap-3 mt-5 mb-1">
          <div className="flex-1 h-px bg-border" />
          <span className="text-xs text-app-text-muted font-medium">or fill in manually below</span>
          <div className="flex-1 h-px bg-border" />
        </div>
      )}
    </div>
  );
}
