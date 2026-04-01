"use client";

import React, { useState } from "react";

interface Tab {
  id: string;
  label: string;
  content: React.ReactNode;
}

interface InnerTabsProps {
  tabs: Tab[];
  defaultTab?: string;
  /** Controlled active tab */
  activeTab?: string;
  /** Called when tab changes (makes component controlled when provided) */
  onTabChange?: (id: string) => void;
}

export function InnerTabs({ tabs, defaultTab, activeTab, onTabChange }: InnerTabsProps) {
  const [internalActive, setInternalActive] = useState(defaultTab ?? tabs[0]?.id);

  const active = activeTab ?? internalActive;
  const setActive = (id: string) => {
    if (onTabChange) {
      onTabChange(id);
    } else {
      setInternalActive(id);
    }
  };

  return (
    <div>
      <div className="flex border-b border-border overflow-x-auto gap-0.5 mb-5">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActive(tab.id)}
            className={active === tab.id ? "tab-btn-active" : "tab-btn-inactive"}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div>
        {tabs.find((t) => t.id === active)?.content}
      </div>
    </div>
  );
}
