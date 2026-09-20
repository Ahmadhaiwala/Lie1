import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { Search, Brain, FileText, Send } from "lucide-react";
import GlowOrb from "../components/GlowOrb";

const steps = [
  {
    step: "01", icon: Search,   title: "AI Discovers Prospects",
    desc:  "Crawler searches Google 24/7 with targeted queries. Finds real businesses that match your service — no bought lists.",
    accent: "border-orange-500/30", num: "text-orange-500", iconBg: "bg-orange-500",
  },
  {
    step: "02", icon: Brain,    title: "LLM Qualifies Leads",
    desc:  "Every page is analysed by an LLM that scores pain points, online presence, and need urgency. Only 50%+ leads move forward.",
    accent: "border-white/10",  num: "text-white",        iconBg: "bg-white",
  },
  {
    step: "03", icon: FileText, title: "Filter & Prioritise",
    desc:  "Business model check — discards food stalls, cash-only vendors. Classifies remaining leads as High or Medium priority.",
    accent: "border-orange-400/25", num: "text-orange-400", iconBg: "bg-orange-400",
  },
  {
    step: "04", icon: Send,     title: "You Close the Deal",
    desc:  "Personalised email, WhatsApp, and DM drafts land in your dashboard. Copy, send, and close.",
    accent: "border-white/10",  num: "text-zinc-300",     iconBg: "bg-zinc-300",
  },
];

export default function HowItWorks() {
  const ref    = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section id="how-it-works" ref={ref} className="relative z-10 py-28 overflow-hidden">
      <GlowOrb className="w-[450px] h-[450px] -left-48 top-20 opacity-30" color="orange" />

      <div className="max-w-7xl mx-auto px-4 sm:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
          className="text-center mb-20"
        >
          <span className="inline-block mb-4 text-xs font-semibold tracking-widest uppercase text-orange-400 bg-orange-500/10 border border-orange-500/20 rounded-full px-4 py-1.5">
            The Pipeline
          </span>
          <h2 className="section-title mb-4">
            How It{" "}
            <span className="gradient-text">Actually Works</span>
          </h2>
          <p className="section-sub mx-auto text-center">
            Four automated steps from zero to a qualified lead with outreach ready to send.
          </p>
        </motion.div>

        {/* Steps */}
        <div className="relative">
          {/* Connector line desktop */}
          <div className="hidden lg:block absolute top-[72px] left-[12%] right-[12%] h-px bg-gradient-to-r from-orange-500 via-white/20 to-orange-400 opacity-20" />

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-4">
            {steps.map((s, i) => (
              <motion.div
                key={s.step}
                initial={{ opacity: 0, y: 50 }}
                animate={inView ? { opacity: 1, y: 0 } : {}}
                transition={{ delay: i * 0.15, duration: 0.7 }}
                className="relative z-10 group"
              >
                <div className={`bg-[#1a1a1a] rounded-2xl p-6 border ${s.accent} hover:border-orange-500/30 transition-all duration-300 hover:-translate-y-2 h-full flex flex-col`}>
                  {/* Number */}
                  <span className={`font-display font-black text-5xl ${s.num} opacity-30 group-hover:opacity-60 transition-opacity mb-5 block`}>
                    {s.step}
                  </span>

                  {/* Icon */}
                  <div className={`w-11 h-11 rounded-xl ${s.iconBg} flex items-center justify-center mb-4 shadow-md group-hover:scale-110 transition-transform duration-300`}>
                    <s.icon className="w-5 h-5 text-black" strokeWidth={2} />
                  </div>

                  <h3 className="font-display font-bold text-base text-white mb-2">{s.title}</h3>
                  <p className="text-zinc-400 text-sm leading-relaxed flex-1">{s.desc}</p>

                  {/* Bottom line */}
                  <div className="mt-5 h-px bg-gradient-to-r from-orange-500 to-orange-300 scale-x-0 group-hover:scale-x-100 transition-transform duration-500 origin-left" />
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
          <div className="inline-flex flex-col sm:flex-row items-center gap-6 bg-[#1a1a1a] border border-orange-500/20 rounded-2xl px-8 py-6 animated-border">
            <div className="text-left">
              <p className="font-semibold text-white">Ready to automate your pipeline?</p>
              <p className="text-zinc-400 text-sm mt-0.5">Start finding leads in under 5 minutes.</p>
            </div>
            <motion.a href="/dashboard" whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.97 }}
              className="btn-primary whitespace-nowrap">
              Open Dashboard →
            </motion.a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
