/**
 * Single source of truth for all application colors.
 * Palette derived from best-iucrc.org (Blocksy theme palette).
 * All color references MUST come from this file — no hardcoded hex values elsewhere.
 * Tailwind config consumes this to generate utility classes.
 */
export const colors = {
  // Primary: deep forest green (#0C3D00) — headers, sidebar, main text emphasis
  primary: {
    DEFAULT: "#0C3D00",
    light:   "#126000",
    lighter: "#1c8000",
    hover:   "#092e00",
    50:      "#f0f7ee",
    100:     "#dceedd",
    200:     "#b9deb8",
  },

  // Accent: vibrant medium green (#00964F) — buttons, links, active states
  accent: {
    DEFAULT: "#00964F",
    hover:   "#007a3f",
    light:   "#e6f7ef",
    200:     "#99d9be",
  },

  // Muted teal from palette-color-3 — secondary accent, borders
  teal: {
    DEFAULT: "#327674",
    hover:   "#275f5e",
    light:   "#eaf4f4",
    200:     "#a8cece",
  },

  success: {
    DEFAULT: "#126000",
    light:   "#d4edda",
    hover:   "#0C3D00",
  },
  warning: {
    DEFAULT: "#96650C",
    light:   "#fef3d0",
    hover:   "#7a500a",
  },
  error: {
    DEFAULT: "#dc2626",
    light:   "#fee2e2",
    hover:   "#b91c1c",
  },

  bg: {
    DEFAULT:          "#f8faf8",
    card:             "#ffffff",
    muted:            "#f2f6f2",
    sidebar:          "#0C3D00",
    "sidebar-hover":  "#126000",
    "sidebar-active": "#00964F",
  },

  border: {
    DEFAULT: "#d4e4d4",
    focus:   "#00964F",
    dark:    "#b0c8b0",
  },

  text: {
    DEFAULT:            "#1a2e1a",
    muted:              "#767171",
    light:              "#9aaa9a",
    white:              "#ffffff",
    "sidebar-inactive": "#b9deb8",
    "sidebar-active":   "#ffffff",
  },
} as const;

export type Colors = typeof colors;
