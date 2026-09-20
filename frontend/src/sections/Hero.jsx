import { motion } from "framer-motion";
import { Zap, ArrowRight, Play, Globe, MessageSquare, TrendingUp } from "lucide-react";
import GlowOrb from "../components/GlowOrb";

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

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
      {/* Grid + radial glow */}
      <div className="absolute inset-0 bg-grid-dark bg-grid opacity-100" aria-hidden="true" />
      <div className="absolute inset-0 bg-radial-glow"                   aria-hidden="true" />

      {/* Orbs */}
      <GlowOrb className="w-[500px] h-[500px] -top-40 -left-40"  color="orange" />
      <GlowOrb className="w-80    h-80    top-1/3  -right-20"    color="white"  />
      <GlowOrb className="w-64    h-64    bottom-10 left-1/4"    color="dark"   />

      {/* Floating badges */}
      <motion.div
        animate={{ y: [0, -12, 0] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
        className="absolute top-28 left-6 md:left-24 hidden sm:block"
      >
        <div className="bg-black/70 border border-orange-500/30 rounded-xl px-4 py-2.5 flex items-center gap-2 text-sm backdrop-blur-sm">
          <span className="w-2 h-2 rounded-full bg-orange-400 animate-pulse" />
          <span className="text-zinc-200">247 leads found today</span>
        </div>
      </motion.div>

      <motion.div
        animate={{ y: [0, 10, 0] }}
        transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 1 }}
        className="absolute top-40 right-6 md:right-24 hidden sm:block"
      >
        <div className="bg-black/70 border border-white/10 rounded-xl px-4 py-2.5 flex items-center gap-2 text-sm backdrop-blur-sm">
          <Zap className="w-4 h-4 text-orange-400 fill-orange-400" />
          <span className="text-zinc-200">AI-powered automation</span>
        </div>
      </motion.div>

      <motion.div
        animate={{ y: [0, -8, 0] }}
        transition={{ duration: 6, repeat: Infinity, ease: "easeInOut", delay: 2 }}
        className="absolute bottom-32 right-10 md:right-32 hidden md:block"
      >
        <div className="bg-black/70 border border-white/10 rounded-xl px-4 py-2.5 flex items-center gap-2 text-sm backdrop-blur-sm">
          <span className="text-orange-400 font-bold text-xs">98%</span>
          <span className="text-zinc-200">qualify rate</span>
        </div>
      </motion.div>

      {/* Main content */}
      <div className="relative z-10 text-center px-4 sm:px-6 max-w-5xl mx-auto">

        {/* Pill */}
        <motion.div {...fadeUp(0.1)} className="inline-flex items-center gap-2 mb-8">
          <span className="bg-orange-500/10 border border-orange-500/30 rounded-full px-5 py-2 text-sm font-medium text-orange-300 flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-orange-400 animate-pulse" />
            Automated Lead Generation · Powered by AI
          </span>
        </motion.div>

        {/* Headline */}
        <motion.h1
          {...fadeUp(0.2)}
          className="font-display font-extrabold text-5xl sm:text-6xl md:text-7xl lg:text-8xl text-white leading-[1.05] mb-6"
        >
          Find Clients Who
          <br />
          <span className="gradient-text">Need Your Services</span>
          <br />
          <span className="text-zinc-500 text-4xl sm:text-5xl md:text-6xl font-bold">
            On Autopilot
          </span>
        </motion.h1>

        {/* Subheading */}
        <motion.p
          {...fadeUp(0.35)}
          className="text-zinc-400 text-lg sm:text-xl max-w-2xl mx-auto mb-8 leading-relaxed"
        >
          Our AI crawls the web 24/7, finds businesses that need websites,
          WhatsApp bots, or SEO — and drafts personalised outreach for each one.
          You just close the deals.
        </motion.p>

        {/* Service pills */}
        <motion.div {...fadeUp(0.45)} className="flex flex-wrap justify-center gap-3 mb-10">
          {services.map(({ icon: Icon, label, color }) => (
            <span
              key={label}
              className={`flex items-center gap-2 bg-white/5 border border-white/8 rounded-full px-4 py-2 text-sm font-medium ${color}`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </span>
          ))}
        </motion.div>

        {/* CTAs */}
        <motion.div
          {...fadeUp(0.55)}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <motion.a
            href="/dashboard"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.97 }}
            className="btn-primary text-base px-8 py-4 shadow-2xl shadow-orange-500/25 group"
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

        {/* Scroll indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className="mt-20 flex flex-col items-center gap-2"
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
      </div>
    </section>
  );
}
