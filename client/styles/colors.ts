/**
 * Single source of truth for all application colors.
 * All color references MUST come from this file — no hardcoded hex values elsewhere.
 * Tailwind config consumes this to generate utility classes.
 */
export const colors = {
  primary: {
    DEFAULT: "#1e3c72",
    light: "#2a5298",
    lighter: "#3b6bbf",
    hover: "#162d57",
    50: "#eef2ff",
    100: "#e0e7ff",
    200: "#c7d2fe",
  },
  accent: {
    DEFAULT: "#0891b2",
    hover: "#0e7490",
    light: "#e0f7fa",
    200: "#a5f3fc",
  },
  success: {
    DEFAULT: "#16a34a",
    light: "#dcfce7",
    hover: "#15803d",
  },
  warning: {
    DEFAULT: "#d97706",
    light: "#fef3c7",
    hover: "#b45309",
  },
  error: {
    DEFAULT: "#dc2626",
    light: "#fee2e2",
    hover: "#b91c1c",
  },
  bg: {
    DEFAULT: "#f8fafc",
    card: "#ffffff",
    muted: "#f1f5f9",
    sidebar: "#0f2240",
    "sidebar-hover": "#1a3558",
    "sidebar-active": "#2a5298",
  },
  border: {
    DEFAULT: "#e2e8f0",
    focus: "#0891b2",
    dark: "#cbd5e1",
  },
  text: {
    DEFAULT: "#1e293b",
    muted: "#64748b",
    light: "#94a3b8",
    white: "#ffffff",
    "sidebar-inactive": "#94a3b8",
    "sidebar-active": "#ffffff",
  },
} as const;

export type Colors = typeof colors;
