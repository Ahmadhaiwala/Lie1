export default function GlowOrb({ className = "", color = "brand" }) {
  const colors = {
    brand: "bg-brand-500/20",
    neon:  "bg-neon/10",
    purple:"bg-purple-500/20",
  };
  return (
    <div
      className={`absolute rounded-full blur-3xl pointer-events-none ${colors[color]} ${className}`}
      aria-hidden="true"
    />
  );
}
