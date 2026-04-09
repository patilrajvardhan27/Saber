"use client";

import React from "react";
import { useForm } from "@/context/FormContext";

interface FormFieldProps {
  label: string;
  fieldKey?: string;
  required?: boolean;
  hint?: string;
  error?: string;
  children: React.ReactNode;
  className?: string;
}

export function FormField({
  label,
  fieldKey,
  required,
  hint,
  error,
  children,
  className = "",
}: FormFieldProps) {
  const { pklFields } = useForm();
  const autoFilled = !!(fieldKey && pklFields.includes(fieldKey));

  return (
    <div className={`flex flex-col gap-1 ${className}`}>
      <label className="form-label flex items-center gap-1.5">
        {label}
        {required && <span className="text-error">*</span>}
        {autoFilled && (
          <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-brand-100 text-brand-700 leading-none">
            <svg viewBox="0 0 10 10" fill="none" className="w-2.5 h-2.5">
              <path d="M2 5.5l2 2 4-4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            auto
          </span>
        )}
      </label>

      {/* Wrap children so autofill inputs get green styling via CSS */}
      <div className={autoFilled ? "autofill-field" : ""}>
        {children}
      </div>

      {hint && !error && <p className="text-xs text-app-text-light">{hint}</p>}
      {error && <p className="text-xs text-error">{error}</p>}
    </div>
  );
}
