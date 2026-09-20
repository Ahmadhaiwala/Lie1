import { motion } from "framer-motion";
import { useInView } from "framer-motion";
import { useRef } from "react";
import AnimatedCounter from "../components/AnimatedCounter";

const stats = [
  { value: 1200, suffix: "+", label: "Leads Found Daily",     color: "from-brand-500 to-purple-500" },
  { value: 98,   suffix: "%", label: "Qualification Accuracy", color: "from-neon to-brand-400" },
  { value: 3,    suffix: "",  label: "Services Automated",     color: "from-purple-500 to-pink-500" },
  { value: 24,   suffix: "/7",label: "Always Running",         color: "from-orange-400 to-brand-500" },
];

export default function Stats() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section ref={ref} className="relative z-10 py-16 overflow-hidden">
      {/* divider line top */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-brand-500/30 to-transparent" />

      <div className="max-w-7xl mx-auto px-4 sm:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-white/5 rounded-2xl overflow-hidden border border-white/5">
          {stats.map(({ value, suffix, label, color }, i) => (
            <motion.div
              key={label}
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: i * 0.1, duration: 0.6 }}
              className="relative glass p-8 flex flex-col items-center justify-center text-center group hover:bg-white/5 transition-all duration-300"
            >
              {/* gradient number */}
              <span className={`font-display font-extrabold text-4xl md:text-5xl bg-gradient-to-r ${color} bg-clip-text text-transparent`}>
                {inView ? <AnimatedCounter target={value} suffix={suffix} /> : `0${suffix}`}
              </span>
              <span className="mt-2 text-slate-400 text-sm font-medium">{label}</span>
              {/* hover glow line */}
              <div className={`absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r ${color} scale-x-0 group-hover:scale-x-100 transition-transform duration-500 rounded-b-2xl`} />
            </motion.div>
          ))}
        </div>
      </div>

      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-brand-500/30 to-transparent" />
    </section>
  );
}
