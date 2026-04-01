import React from "react";

interface Option {
  value: string;
  label: string;
  description?: string;
}

interface RadioGroupProps {
  name: string;
  options: Option[];
  value: string;
  onChange: (value: string) => void;
  direction?: "row" | "col";
}

export function RadioGroup({
  name,
  options,
  value,
  onChange,
  direction = "col",
}: RadioGroupProps) {
  return (
    <div className={`flex ${direction === "row" ? "flex-row gap-6" : "flex-col gap-3"}`}>
      {options.map((opt) => (
        <label
          key={opt.value}
          className={`flex items-start gap-3 cursor-pointer group`}
        >
          <input
            type="radio"
            name={name}
            value={opt.value}
            checked={value === opt.value}
            onChange={() => onChange(opt.value)}
            className="mt-0.5 accent-primary"
          />
          <div>
            <span className="text-sm font-medium text-app-text group-hover:text-primary transition-colors">
              {opt.label}
            </span>
            {opt.description && (
              <p className="text-xs text-app-text-muted mt-0.5">{opt.description}</p>
            )}
          </div>
        </label>
      ))}
    </div>
  );
}
