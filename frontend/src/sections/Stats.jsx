import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import AnimatedCounter from "../components/AnimatedCounter";

const stats = [
  { value: 1200, suffix: "+",  label: "Leads Found Daily",      grad: "from-orange-500 to-orange-300" },
  { value: 98,   suffix: "%",  label: "Qualification Accuracy",  grad: "from-white to-zinc-300"        },
  { value: 3,    suffix: "",   label: "Services Automated",      grad: "from-orange-400 to-white"      },
  { value: 24,   suffix: "/7", label: "Always Running",          grad: "from-orange-300 to-orange-500" },
];

export default function Stats() {
  const ref    = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section ref={ref} className="relative z-10 py-16 overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-orange-500/25 to-transparent" />

      <div className="max-w-7xl mx-auto px-4 sm:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-white/5 rounded-2xl overflow-hidden border border-white/5">
          {stats.map(({ value, suffix, label, grad }, i) => (
            <motion.div
              key={label}
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: i * 0.1, duration: 0.6 }}
              className="relative bg-[#111] p-8 flex flex-col items-center justify-center text-center group hover:bg-white/3 transition-all duration-300"
            >
              <span className={`font-display font-extrabold text-4xl md:text-5xl bg-gradient-to-r ${grad} bg-clip-text text-transparent`}>
                {inView ? <AnimatedCounter target={value} suffix={suffix} /> : `0${suffix}`}
              </span>
              <span className="mt-2 text-zinc-500 text-sm font-medium">{label}</span>
              <div className={`absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r ${grad} scale-x-0 group-hover:scale-x-100 transition-transform duration-500`} />
            </motion.div>
          ))}
        </div>
      </div>

      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-orange-500/25 to-transparent" />
    </section>
  );
}
