import type { Config } from "tailwindcss";
import { colors } from "./styles/colors";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./context/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: colors.primary,
        accent:  colors.accent,
        "app-teal": colors.teal,
        success: colors.success,
        warning: colors.warning,
        error:   colors.error,
        bg:      colors.bg,
        border:  colors.border,
        "app-text": colors.text,

        // Brand green scale — replaces Tailwind's teal throughout components
        brand: {
          50:  "#f0f9f4",
          100: "#d8f0e4",
          200: "#b9deb8",
          300: "#7cbf9e",
          400: "#3da571",
          500: "#00964F",
          600: "#007a3f",
          700: "#126000",
          800: "#0C3D00",
          900: "#082800",
        },
      },
      fontFamily: {
        sans: ["Work Sans", "system-ui", "sans-serif"],
      },
      fontSize: {
        xs:    ["0.75rem",  { lineHeight: "1.4" }],
        sm:    ["0.875rem", { lineHeight: "1.6" }],
        base:  ["1rem",     { lineHeight: "1.6" }],
        lg:    ["1.125rem", { lineHeight: "1.6" }],
        xl:    ["1.25rem",  { lineHeight: "1.5" }],
        "2xl": ["1.5rem",   { lineHeight: "1.4" }],
        "3xl": ["1.875rem", { lineHeight: "1.3" }],
      },
      letterSpacing: {
        tight:  "-0.01em",
        normal: "0em",
        wide:   "0.015em",
        wider:  "0.03em",
      },
      boxShadow: {
        card:       "0 1px 3px 0 rgba(0,0,0,0.08), 0 1px 2px -1px rgba(0,0,0,0.06)",
        "card-hover":"0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.06)",
        sidebar:    "2px 0 8px rgba(0,0,0,0.15)",
      },
    },
  },
  plugins: [],
};

export default config;
