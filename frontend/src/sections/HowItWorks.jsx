import { motion } from "framer-motion";
import { useInView } from "framer-motion";
import { useRef } from "react";
import { Search, Brain, FileText, Send, ChevronRight } from "lucide-react";
import GlowOrb from "../components/GlowOrb";

const steps = [
  {
    step: "01",
    icon: Search,
    title: "AI Discovers Prospects",
    description:
      "Our crawler searches Google 24/7 using dozens of targeted queries. It finds real businesses that match your service — no bought lists, no guessing.",
    color: "from-brand-500 to-brand-600",
    glow: "shadow-brand-500/30",
  },
  {
    step: "02",
    icon: Brain,
    title: "LLM Qualifies Each Lead",
    description:
      "Every page is analysed by an LLM that scores pain points, need urgency, and contact quality. Only leads scoring 50%+ move forward.",
    color: "from-purple-500 to-brand-500",
    glow: "shadow-purple-500/30",
  },
  {
    step: "03",
    icon: FileText,
    title: "Personalised Outreach Written",
    description:
      "For each lead, the AI writes a custom email, WhatsApp message, and cold DM — referencing their specific pain points and your value proposition.",
    color: "from-neon/80 to-teal-500",
    glow: "shadow-neon/20",
  },
  {
    step: "04",
    icon: Send,
    title: "You Close the Deal",
    description:
      "Leads and messages land in your dashboard, sorted by score. Copy, send, and close. The machine keeps running while you focus on clients.",
    color: "from-pink-500 to-purple-500",
    glow: "shadow-pink-500/30",
  },
];

export default function HowItWorks() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section id="how-it-works" ref={ref} className="relative z-10 py-28 overflow-hidden">
      <GlowOrb className="w-[500px] h-[500px] -left-64 top-20 opacity-40" color="brand" />

      <div className="max-w-7xl mx-auto px-4 sm:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
          className="text-center mb-20"
        >
          <span className="inline-block mb-4 text-xs font-semibold tracking-widest uppercase text-neon bg-neon/10 border border-neon/20 rounded-full px-4 py-1.5">
            The Pipeline
          </span>
          <h2 className="section-title mb-4">
            How It{" "}
            <span className="gradient-text">Actually Works</span>
          </h2>
          <p className="section-sub mx-auto text-center">
            Four automated steps from zero to qualified lead with outreach ready to send.
          </p>
        </motion.div>

        {/* Steps */}
        <div className="relative">
          {/* Connector line — desktop */}
          <div className="hidden lg:block absolute top-20 left-[12.5%] right-[12.5%] h-0.5 bg-gradient-to-r from-brand-500 via-purple-500 to-pink-500 opacity-30 z-0" />

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-4">
            {steps.map((s, i) => (
              <motion.div
                key={s.step}
                initial={{ opacity: 0, y: 50 }}
                animate={inView ? { opacity: 1, y: 0 } : {}}
                transition={{ delay: i * 0.15, duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
                className="relative z-10 group"
              >
                <div className="glass rounded-2xl p-6 border border-white/5 hover:border-white/10 transition-all duration-300 hover:-translate-y-2 h-full flex flex-col">
                  {/* Step number */}
                  <div className="flex items-center justify-between mb-6">
                    <span className={`font-display font-black text-5xl bg-gradient-to-br ${s.color} bg-clip-text text-transparent opacity-40 group-hover:opacity-70 transition-opacity`}>
                      {s.step}
                    </span>
                    {i < steps.length - 1 && (
                      <ChevronRight className="hidden lg:block w-5 h-5 text-slate-700 absolute -right-3 top-8 z-20" />
                    )}
                  </div>

                  {/* Icon */}
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${s.color} flex items-center justify-center mb-4 shadow-lg ${s.glow} group-hover:scale-110 transition-transform duration-300`}>
                    <s.icon className="w-6 h-6 text-white" strokeWidth={1.5} />
                  </div>

                  {/* Title */}
                  <h3 className="font-display font-bold text-lg text-white mb-3">
                    {s.title}
                  </h3>

                  {/* Description */}
                  <p className="text-slate-400 text-sm leading-relaxed flex-1">
                    {s.description}
                  </p>

                  {/* Bottom gradient bar on hover */}
                  <div className={`mt-5 h-0.5 bg-gradient-to-r ${s.color} rounded-full scale-x-0 group-hover:scale-x-100 transition-transform duration-500 origin-left`} />
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.7, duration: 0.7 }}
          className="mt-16 text-center"
        >
          <div className="inline-flex flex-col sm:flex-row items-center gap-4 glass rounded-2xl px-8 py-6 border border-white/5 animated-border">
            <div className="text-left">
              <p className="font-semibold text-white">Ready to automate your pipeline?</p>
              <p className="text-slate-400 text-sm">Start finding leads in under 5 minutes.</p>
            </div>
            <motion.a
              href="/dashboard"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.97 }}
              className="btn-primary whitespace-nowrap"
            >
              Open Dashboard →
            </motion.a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
