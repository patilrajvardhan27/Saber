import React from "react";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  unit?: string;
}

export function Input({ unit, className = "", ...props }: InputProps) {
  if (unit) {
    return (
      <div className="flex items-center">
        <input className={`form-input rounded-r-none border-r-0 ${className}`} {...props} />
        <span className="inline-flex items-center px-3 py-2 text-xs text-app-text-muted bg-bg-muted border border-border rounded-r-md whitespace-nowrap">
          {unit}
        </span>
      </div>
    );
  }
  return <input className={`form-input ${className}`} {...props} />;
}
