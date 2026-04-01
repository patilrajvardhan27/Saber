import React from "react";

export function Header() {
  return (
    <header className="h-14 bg-bg-sidebar flex items-center px-6 shadow-sidebar flex-shrink-0">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-md bg-accent flex items-center justify-center">
          <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5 text-app-text-white" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
              d="M3 12l9-9 9 9M5 10v9a1 1 0 001 1h4v-5h4v5h4a1 1 0 001-1v-9" />
          </svg>
        </div>
        <div>
          <h1 className="text-sm font-bold text-app-text-white leading-none">Building Audit Tool</h1>
          <p className="text-xs text-app-text-sidebar-inactive leading-none mt-0.5">Energy Efficiency Evaluation</p>
        </div>
      </div>
    </header>
  );
}
