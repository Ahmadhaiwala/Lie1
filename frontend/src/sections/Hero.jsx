import { motion } from "framer-motion";
import { Zap, ArrowRight, Play, Globe, MessageSquare, TrendingUp } from "lucide-react";
import Mascot from "../components/Mascot";

const fadeUp = (delay = 0) => ({
  initial:    { opacity: 0, y: 40 },
  animate:    { opacity: 1, y: 0  },
  transition: { duration: 0.7, delay, ease: [0.22, 1, 0.36, 1] },
});

const services = [
  { icon: Globe,         label: "Website Development", color: "text-orange-400" },
  { icon: MessageSquare, label: "WhatsApp Bots",        color: "text-white"      },
  { icon: TrendingUp,    label: "SEO Services",          color: "text-orange-300" },
];

const stats = [
  { value: "1,200+", label: "Leads/day"    },
  { value: "98%",    label: "Accuracy"     },
  { value: "3",      label: "Services"     },
  { value: "24/7",   label: "Runs Always"  },
];

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
      {/* Grid bg */}
      <div className="absolute inset-0 bg-grid-dark bg-grid opacity-100" aria-hidden="true" />
      <div className="absolute inset-0 bg-radial-glow"                   aria-hidden="true" />

      {/* Ambient blobs */}
      <div className="absolute w-[500px] h-[500px] rounded-full bg-orange-500/8 blur-3xl -top-40 -left-40 pointer-events-none" />
      <div className="absolute w-72 h-72 rounded-full bg-orange-400/6 blur-3xl bottom-20 -right-20 pointer-events-none" />

      <div className="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-8 py-20">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20 items-center">

          {/* ── LEFT — copy ─────────────────────────────────────────────── */}
          <div>
            {/* Badge */}
            <motion.div {...fadeUp(0.1)} className="inline-flex items-center gap-2 mb-8">
              <span className="bg-orange-500/12 border border-orange-500/30 rounded-full px-5 py-2 text-sm font-medium text-orange-300 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-orange-400 animate-pulse" />
                AI-Powered Lead Generation
              </span>
            </motion.div>

            {/* Headline */}
            <motion.h1
              {...fadeUp(0.2)}
              className="font-display font-extrabold text-5xl sm:text-6xl lg:text-7xl text-white leading-[1.05] mb-6"
            >
              Find Clients
              <br />
              <span className="gradient-text">Who Need You</span>
              <br />
              <span className="text-zinc-400 text-4xl sm:text-5xl font-bold">
                — Automatically
              </span>
            </motion.h1>

            {/* Sub */}
            <motion.p
              {...fadeUp(0.3)}
              className="text-zinc-300 text-lg sm:text-xl max-w-xl mb-8 leading-relaxed"
            >
              Our AI crawls the web 24/7 finding businesses that need
              websites, WhatsApp bots, or SEO. Each lead comes with
              contact details and a personalised outreach draft.
              <strong className="text-white"> You just close the deals.</strong>
            </motion.p>

            {/* Service pills */}
            <motion.div {...fadeUp(0.4)} className="flex flex-wrap gap-2 mb-10">
              {services.map(({ icon: Icon, label, color }) => (
                <span key={label}
                  className={`flex items-center gap-2 bg-white/5 border border-white/10 rounded-full px-4 py-2 text-sm font-medium ${color}`}>
                  <Icon className="w-4 h-4" />
                  {label}
                </span>
              ))}
            </motion.div>

            {/* CTA buttons */}
            <motion.div {...fadeUp(0.5)} className="flex flex-col sm:flex-row gap-4 mb-12">
              <motion.a
                href="/dashboard"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.97 }}
                className="btn-primary text-base px-8 py-4 shadow-2xl shadow-orange-500/20 group"
              >
                <Zap className="w-5 h-5 group-hover:rotate-12 transition-transform" />
                View Dashboard
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </motion.a>
              <motion.a
                href="/#how-it-works"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.97 }}
                className="btn-secondary text-base px-8 py-4"
              >
                <Play className="w-5 h-5 fill-orange-400" />
                How It Works
              </motion.a>
            </motion.div>

            {/* Mini stats row */}
            <motion.div
              {...fadeUp(0.6)}
              className="grid grid-cols-4 gap-4 border-t border-white/8 pt-8"
            >
              {stats.map(({ value, label }) => (
                <div key={label} className="text-center">
                  <p className="font-display font-bold text-2xl text-orange-400">{value}</p>
                  <p className="text-zinc-500 text-xs mt-0.5">{label}</p>
                </div>
              ))}
            </motion.div>
          </div>

          {/* ── RIGHT — mascot ──────────────────────────────────────────── */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
            className="flex flex-col items-center justify-center gap-6"
          >
            {/* Mascot with glow */}
            <div className="relative flex items-center justify-center">
              {/* Big outer glow */}
              <div className="absolute w-80 h-80 rounded-full bg-orange-500/10 blur-3xl" />
              {/* Dashed orbit ring */}
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                className="absolute w-72 h-72 rounded-full border border-dashed border-orange-500/20"
              />
              {/* Solid ring */}
              <motion.div
                animate={{ scale: [1, 1.04, 1], opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 3, repeat: Infinity }}
                className="absolute w-60 h-60 rounded-full border-2 border-orange-500/40"
              />

              <Mascot size={220} animate ring />
            </div>

            {/* Floating info cards around mascot */}
            <div className="grid grid-cols-2 gap-3 w-full max-w-xs">
              {[
                { label: "Leads found today",  value: "247",    icon: "🎯", color: "border-orange-500/30 bg-orange-500/5" },
                { label: "High priority",       value: "89",     icon: "🔥", color: "border-white/15 bg-white/3"           },
                { label: "Outreach ready",      value: "156",    icon: "✉️", color: "border-white/15 bg-white/3"           },
                { label: "Filter accuracy",     value: "98%",    icon: "✅", color: "border-orange-500/25 bg-orange-500/5" },
              ].map(({ label, value, icon, color }) => (
                <motion.div
                  key={label}
                  whileHover={{ scale: 1.04, y: -2 }}
                  className={`rounded-xl p-3 border ${color} text-center transition-all duration-200`}
                >
                  <span className="text-lg">{icon}</span>
                  <p className="font-bold text-white text-lg mt-1">{value}</p>
                  <p className="text-zinc-500 text-xs">{label}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>

        </div>
      </div>

      {/* Scroll hint */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
      >
        <span className="text-zinc-600 text-xs uppercase tracking-widest">Scroll</span>
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="w-5 h-8 rounded-full border border-zinc-700 flex items-start justify-center pt-1.5"
        >
          <div className="w-1 h-2 rounded-full bg-orange-400" />
        </motion.div>
      </motion.div>
    </section>
  );
}
