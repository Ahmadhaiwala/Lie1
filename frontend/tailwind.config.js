/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Primary accent — orange
        orange: {
          50:  "#fff7ed",
          100: "#ffedd5",
          200: "#fed7aa",
          300: "#fdba74",
          400: "#fb923c",
          500: "#f97316",   // main orange
          600: "#ea580c",
          700: "#c2410c",
          800: "#9a3412",
          900: "#7c2d12",
        },
        // Dark backgrounds
        dark: {
          950: "#0a0a0a",   // pure near-black
          900: "#111111",   // page bg
          800: "#1a1a1a",   // card bg
          700: "#222222",   // input bg
          600: "#2a2a2a",   // border
          500: "#333333",   // subtle divider
        },
        // Keep neon as orange-glow alias
        neon: "#f97316",
      },
      fontFamily: {
        sans:    ["Inter", "system-ui", "sans-serif"],
        display: ["'Space Grotesk'", "sans-serif"],
      },
      animation: {
        "float":       "float 6s ease-in-out infinite",
        "float-slow":  "float 9s ease-in-out infinite",
        "pulse-neon":  "pulseNeon 2s ease-in-out infinite",
        "gradient-x":  "gradientX 4s ease infinite",
        "slide-up":    "slideUp 0.6s ease forwards",
        "fade-in":     "fadeIn 0.8s ease forwards",
        "spin-slow":   "spin 12s linear infinite",
        "glow":        "glow 2s ease-in-out infinite alternate",
        "shimmer":     "shimmer 2.5s linear infinite",
        "blink":       "blink 1s step-end infinite",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%":      { transform: "translateY(-20px)" },
        },
        pulseNeon: {
          "0%, 100%": { boxShadow: "0 0 20px #f97316, 0 0 40px #f9731640" },
          "50%":      { boxShadow: "0 0 40px #f97316, 0 0 80px #f9731680" },
        },
        gradientX: {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%":      { backgroundPosition: "100% 50%" },
        },
        slideUp: {
          from: { opacity: 0, transform: "translateY(40px)" },
          to:   { opacity: 1, transform: "translateY(0)" },
        },
        fadeIn: {
          from: { opacity: 0 },
          to:   { opacity: 1 },
        },
        glow: {
          from: { textShadow: "0 0 10px #f97316, 0 0 20px #f9731680" },
          to:   { textShadow: "0 0 20px #f97316, 0 0 40px #f97316, 0 0 60px #f9731680" },
        },
        shimmer: {
          "0%":   { backgroundPosition: "-1000px 0" },
          "100%": { backgroundPosition: "1000px 0" },
        },
        blink: {
          "0%, 100%": { borderColor: "transparent" },
          "50%":      { borderColor: "#f97316" },
        },
      },
      backgroundImage: {
        "grid-dark":
          "linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)",
        "radial-glow":
          "radial-gradient(ellipse at center, rgba(249,115,22,0.08) 0%, transparent 70%)",
      },
      backgroundSize: {
        "grid": "60px 60px",
      },
    },
  },
  plugins: [],
};
