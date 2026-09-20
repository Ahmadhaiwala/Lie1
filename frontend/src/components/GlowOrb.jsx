export default function GlowOrb({ className = "", color = "orange" }) {
  const colors = {
    orange: "bg-orange-500/15",
    white:  "bg-white/5",
    dark:   "bg-white/3",
  };
  return (
    <div
      className={`absolute rounded-full blur-3xl pointer-events-none ${colors[color] || colors.orange} ${className}`}
      aria-hidden="true"
    />
  );
}
