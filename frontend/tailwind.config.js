/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#ecfaf6",
          100: "#d2f3ea",
          200: "#a8e6d5",
          300: "#6fd4bb",
          400: "#36b89a",
          500: "#1a9a80",
          600: "#0f7a67",
          700: "#0d6254",
          800: "#0f4e44",
          900: "#0f4039",
        },
        ink: {
          DEFAULT: "var(--ink)",
          muted: "var(--ink-muted)",
          soft: "var(--ink-soft)",
        },
        surface: {
          DEFAULT: "var(--surface)",
          raised: "var(--raised)",
          sunken: "var(--surface-sunken)",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "system-ui", "sans-serif"],
        sans: ["var(--font-body)", "system-ui", "sans-serif"],
      },
      boxShadow: {
        soft: "var(--shadow-soft)",
        lift: "var(--shadow-lift)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "pulse-line": {
          "0%, 100%": { opacity: "0.4" },
          "50%": { opacity: "1" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.45s ease-out both",
        "fade-up-delay": "fade-up 0.5s ease-out 0.08s both",
        "fade-up-late": "fade-up 0.55s ease-out 0.16s both",
        "pulse-line": "pulse-line 1.6s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
