/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  "#f0f4ff",
          100: "#e0e9ff",
          200: "#c7d6fe",
          300: "#a5b8fc",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
          800: "#3730a3",
          900: "#312e81",
        },
        neon: "#00f5d4",
        dark: {
          900: "#060612",
          800: "#0d0d1f",
          700: "#12122b",
          600: "#1a1a3e",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["'Space Grotesk'", "sans-serif"],
      },
      animation: {
        "float":        "float 6s ease-in-out infinite",
        "float-slow":   "float 9s ease-in-out infinite",
        "pulse-neon":   "pulseNeon 2s ease-in-out infinite",
        "gradient-x":   "gradientX 4s ease infinite",
        "slide-up":     "slideUp 0.6s ease forwards",
        "fade-in":      "fadeIn 0.8s ease forwards",
        "spin-slow":    "spin 12s linear infinite",
        "glow":         "glow 2s ease-in-out infinite alternate",
        "shimmer":      "shimmer 2.5s linear infinite",
        "typewriter":   "typewriter 3s steps(40) forwards",
        "blink":        "blink 1s step-end infinite",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%":      { transform: "translateY(-20px)" },
        },
        pulseNeon: {
          "0%, 100%": { boxShadow: "0 0 20px #00f5d4, 0 0 40px #00f5d440" },
          "50%":      { boxShadow: "0 0 40px #00f5d4, 0 0 80px #00f5d480" },
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
          from: { textShadow: "0 0 10px #6366f1, 0 0 20px #6366f180" },
          to:   { textShadow: "0 0 20px #6366f1, 0 0 40px #6366f1, 0 0 60px #6366f180" },
        },
        shimmer: {
          "0%":   { backgroundPosition: "-1000px 0" },
          "100%": { backgroundPosition: "1000px 0" },
        },
        typewriter: {
          from: { width: "0" },
          to:   { width: "100%" },
        },
        blink: {
          "0%, 100%": { borderColor: "transparent" },
          "50%":      { borderColor: "#00f5d4" },
        },
      },
      backgroundImage: {
        "grid-dark":
          "linear-gradient(rgba(99,102,241,0.07) 1px, transparent 1px), linear-gradient(90deg, rgba(99,102,241,0.07) 1px, transparent 1px)",
        "radial-glow":
          "radial-gradient(ellipse at center, rgba(99,102,241,0.15) 0%, transparent 70%)",
      },
      backgroundSize: {
        "grid": "60px 60px",
      },
    },
  },
  plugins: [],
};
