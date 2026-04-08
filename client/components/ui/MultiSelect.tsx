"use client";

import React from "react";

interface MultiSelectProps {
  options: string[];
  value: string[];
  onChange: (value: string[]) => void;
  singleSelect?: boolean;
  columns?: 1 | 2 | 3;
}

export function MultiSelect({
  options,
  value,
  onChange,
  singleSelect = false,
}: MultiSelectProps) {
  if (singleSelect) {
    return (
      <div className="relative">
        <select
          className="form-select pr-8 w-full"
          value={value[0] ?? ""}
          onChange={(e) => onChange(e.target.value ? [e.target.value] : [])}
        >
          <option value="" disabled>
            Select an option
          </option>
          {options.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
          <svg className="h-4 w-4 text-app-text-light" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
    );
  }

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selected = Array.from(e.target.selectedOptions).map((o) => o.value);
    onChange(selected);
  };

  return (
    <select
      multiple
      className="form-select w-full min-h-[120px] pr-2"
      value={value}
      onChange={handleChange}
    >
      {options.map((opt) => (
        <option key={opt} value={opt}>
          {opt}
        </option>
      ))}
    </select>
  );
}
