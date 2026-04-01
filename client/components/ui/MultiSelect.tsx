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
  columns = 1,
}: MultiSelectProps) {
  const toggle = (opt: string) => {
    if (singleSelect) {
      onChange([opt]);
      return;
    }
    if (value.includes(opt)) {
      onChange(value.filter((v) => v !== opt));
    } else {
      onChange([...value, opt]);
    }
  };

  const gridClass = columns === 3 ? "grid-cols-3" : columns === 2 ? "grid-cols-2" : "grid-cols-1";

  return (
    <div className={`grid ${gridClass} gap-1.5`}>
      {options.map((opt) => {
        const selected = value.includes(opt);
        return (
          <button
            key={opt}
            type="button"
            onClick={() => toggle(opt)}
            className={`text-left px-3 py-2 text-sm rounded-md border transition-colors duration-100
              ${
                selected
                  ? "bg-primary-100 border-primary text-primary font-medium"
                  : "bg-bg-card border-border text-app-text hover:border-accent hover:bg-accent-light"
              }`}
          >
            <span className="flex items-center gap-2">
              <span
                className={`inline-block w-3.5 h-3.5 rounded-sm border flex-shrink-0 transition-colors
                  ${selected ? "bg-primary border-primary" : "border-border-dark bg-bg-muted"}`}
              >
                {selected && (
                  <svg viewBox="0 0 12 12" fill="none" className="w-3.5 h-3.5">
                    <path d="M2 6l3 3 5-5" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
              </span>
              {opt}
            </span>
          </button>
        );
      })}
    </div>
  );
}
