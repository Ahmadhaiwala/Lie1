import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { Globe, MessageSquare, TrendingUp, CheckCircle, ArrowRight } from "lucide-react";
import GlowOrb from "../components/GlowOrb";

const services = [
  {
    icon: Globe,
    title: "Website Development",
    tag: "website",
    accent: "border-orange-500/40 shadow-orange-500/10",
    iconBg: "bg-orange-500",
    badge: "Most Popular",
    badgeCls: "bg-orange-500/15 text-orange-300 border border-orange-500/25",
    cta: "text-orange-400",
    bar: "from-orange-500 to-orange-300",
    description: "Automatically finds businesses with no website, broken sites, or outdated designs — and generates ready-to-send outreach.",
    targets: [
      "Local shops with Facebook-only presence",
      "Restaurants with no online ordering",
      "Freelancers without a portfolio site",
      "Startups needing a landing page",
    ],
  },
  {
    icon: MessageSquare,
    title: "WhatsApp Bot",
    tag: "whatsapp_bot",
    accent: "border-white/15 shadow-white/5",
    iconBg: "bg-white",
    badge: "High Demand",
    badgeCls: "bg-white/10 text-white border border-white/15",
    cta: "text-white",
    bar: "from-white to-zinc-400",
    description: "Finds businesses drowning in manual WhatsApp messages — clinics, restaurants, online stores — and pitches 24/7 automation.",
    targets: [
      "Clinics booking appointments manually",
      "Restaurants taking WhatsApp orders",
      "Online stores with high message volume",
      "Service businesses needing auto-replies",
    ],
  },
  {
    icon: TrendingUp,
    title: "SEO Services",
    tag: "seo",
    accent: "border-orange-300/30 shadow-orange-300/10",
    iconBg: "bg-orange-400",
    badge: "High Value",
    badgeCls: "bg-orange-400/15 text-orange-200 border border-orange-400/25",
    cta: "text-orange-300",
    bar: "from-orange-400 to-orange-200",
    description: "Identifies businesses stuck on page 3+ of Google with high competition potential — dentists, lawyers, accountants.",
    targets: [
      "Dentists & clinics with zero ranking",
      "Law firms invisible on Google",
      "E-commerce with no organic traffic",
      "Local businesses losing to big chains",
    ],
  },
];

const cardVariants = {
  hidden:   { opacity: 0, y: 60 },
  visible: (i) => ({
    opacity: 1, y: 0,
    transition: { duration: 0.7, delay: i * 0.15, ease: [0.22, 1, 0.36, 1] },
  }),
};

export default function Services() {
  const ref    = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section id="services" ref={ref} className="relative z-10 py-28 overflow-hidden">
      <GlowOrb className="w-[500px] h-[500px] -right-48 top-0 opacity-40" color="orange" />

      <div className="max-w-7xl mx-auto px-4 sm:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
          className="text-center mb-16"
        >
          <span className="inline-block mb-4 text-xs font-semibold tracking-widest uppercase text-orange-400 bg-orange-500/10 border border-orange-500/20 rounded-full px-4 py-1.5">
            What We Automate
          </span>
          <h2 className="section-title mb-4">
            Three Services.{" "}
            <span className="gradient-text">One Engine.</span>
          </h2>
          <p className="section-sub mx-auto text-center">
            Our AI targets businesses that genuinely need each service —
            no cold spraying, only warm qualified leads.
          </p>
        </motion.div>

        {/* Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {services.map((svc, i) => (
            <motion.div
              key={svc.tag}
              custom={i}
              variants={cardVariants}
              initial="hidden"
              animate={inView ? "visible" : "hidden"}
              className={`group relative bg-[#1a1a1a] rounded-2xl p-7 border ${svc.accent} hover:-translate-y-2 transition-all duration-500 hover:shadow-2xl`}
            >
              {/* Top colour bar */}
              <div className={`absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r ${svc.bar} rounded-t-2xl`} />

              {/* Badge */}
              <span className={`badge mb-5 ${svc.badgeCls}`}>
                <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
                {svc.badge}
              </span>

              {/* Icon */}
              <div className={`w-12 h-12 rounded-xl ${svc.iconBg} flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300 shadow-lg`}>
                <svc.icon className="w-6 h-6 text-black" strokeWidth={2} />
              </div>

              {/* Title */}
              <h3 className="font-display font-bold text-xl text-white mb-3">{svc.title}</h3>

              {/* Description */}
              <p className="text-zinc-400 text-sm leading-relaxed mb-6">{svc.description}</p>

              {/* Targets */}
              <ul className="space-y-2.5 mb-7">
                {svc.targets.map((t) => (
                  <li key={t} className="flex items-start gap-2.5 text-sm text-zinc-300">
                    <CheckCircle className="w-4 h-4 mt-0.5 shrink-0 text-orange-400" />
                    {t}
                  </li>
                ))}
              </ul>

              {/* CTA */}
              <a href="/dashboard"
                className={`inline-flex items-center gap-1.5 text-sm font-semibold ${svc.cta} hover:gap-3 transition-all duration-300`}>
                See leads
                <ArrowRight className="w-4 h-4" />
              </a>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
