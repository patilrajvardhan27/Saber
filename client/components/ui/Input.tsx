import React from "react";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  unit?: string;
}

export function Input({ unit, className = "", ...props }: InputProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (
      props.type === "number" &&
      !String(props.value ?? "") &&
      props.placeholder &&
      (e.key === "ArrowUp" || e.key === "ArrowDown")
    ) {
      const base = parseFloat(props.placeholder as string);
      if (!isNaN(base)) {
        e.preventDefault();
        const step = Number(props.step ?? 1);
        const next = e.key === "ArrowUp" ? base : Math.max(0, base - step);
        props.onChange?.({ target: { value: String(next) } } as React.ChangeEvent<HTMLInputElement>);
        return;
      }
    }
    props.onKeyDown?.(e);
  };

  if (unit) {
    return (
      <div className="flex items-center">
        <input
          className={`form-input rounded-r-none border-r-0 ${className}`}
          {...props}
          onKeyDown={handleKeyDown}
        />
        <span className="inline-flex items-center px-3 py-2 text-xs text-app-text-muted bg-bg-muted border border-border rounded-r-md whitespace-nowrap">
          {unit}
        </span>
      </div>
    );
  }
  return <input className={`form-input ${className}`} {...props} onKeyDown={handleKeyDown} />;
}
