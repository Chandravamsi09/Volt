/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#090d16",
        surface: "#111827",
        "surface-border": "#1f2937",
        brand: {
          50: "#eef2ff",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
        },
        volt: {
          cyan: "#06b6d4",
          purple: "#a855f7",
          amber: "#f59e0b",
          emerald: "#10b981",
        }
      },
    },
  },
  plugins: [],
};
