/** @type {import('tailwindcss').Config} */
module.exports = {
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
          DEFAULT: "#10231f",
          muted: "#5a6f69",
          soft: "#8a9e97",
        },
        surface: {
          DEFAULT: "#f7fbf9",
          raised: "#ffffff",
          sunken: "#eef5f2",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "system-ui", "sans-serif"],
        sans: ["var(--font-body)", "system-ui", "sans-serif"],
      },
      boxShadow: {
        soft: "0 1px 2px rgba(16, 35, 31, 0.04), 0 8px 24px rgba(16, 35, 31, 0.06)",
        lift: "0 4px 20px rgba(15, 122, 103, 0.12)",
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
