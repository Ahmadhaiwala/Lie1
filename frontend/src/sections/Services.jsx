import { motion } from "framer-motion";
import { useInView } from "framer-motion";
import { useRef } from "react";
import { Globe, MessageSquare, TrendingUp, CheckCircle, ArrowRight } from "lucide-react";
import GlowOrb from "../components/GlowOrb";

const services = [
  {
    icon: Globe,
    title: "Website Development",
    tag: "website",
    color: "brand",
    gradient: "from-brand-500 to-purple-500",
    border: "hover:border-brand-500/50",
    glow: "group-hover:shadow-brand-500/20",
    description:
      "We automatically find businesses with no website, broken sites, or outdated designs — and generate ready-to-send outreach that converts.",
    targets: [
      "Local shops with Facebook-only presence",
      "Restaurants with no online ordering",
      "Freelancers without a portfolio site",
      "Startups needing a landing page",
    ],
    badge: "Most Popular",
    badgeColor: "bg-brand-500/20 text-brand-300 border border-brand-500/30",
  },
  {
    icon: MessageSquare,
    title: "WhatsApp Bot",
    tag: "whatsapp_bot",
    color: "neon",
    gradient: "from-neon to-teal-400",
    border: "hover:border-neon/50",
    glow: "group-hover:shadow-neon/20",
    description:
      "Finds businesses drowning in manual WhatsApp messages — clinics, restaurants, online stores — and pitches 24/7 automation that pays for itself.",
    targets: [
      "Clinics booking appointments manually",
      "Restaurants taking WhatsApp orders",
      "Online stores with high message volume",
      "Service businesses needing auto-replies",
    ],
    badge: "High Demand",
    badgeColor: "bg-neon/10 text-neon border border-neon/30",
  },
  {
    icon: TrendingUp,
    title: "SEO Services",
    tag: "seo",
    color: "purple",
    gradient: "from-purple-500 to-pink-500",
    border: "hover:border-purple-500/50",
    glow: "group-hover:shadow-purple-500/20",
    description:
      "Identifies businesses stuck on page 3+ of Google with high competition potential — dentists, lawyers, accountants — and generates SEO pitches.",
    targets: [
      "Dentists & clinics with zero ranking",
      "Law firms invisible on Google",
      "E-commerce with no organic traffic",
      "Local businesses losing to big chains",
    ],
    badge: "High Value",
    badgeColor: "bg-purple-500/20 text-purple-300 border border-purple-500/30",
  },
];

const cardVariants = {
  hidden: { opacity: 0, y: 60 },
  visible: (i) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.7, delay: i * 0.15, ease: [0.22, 1, 0.36, 1] },
  }),
};

export default function Services() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section id="services" ref={ref} className="relative z-10 py-28 overflow-hidden">
      <GlowOrb className="w-[600px] h-[600px] -right-64 top-0 opacity-50" color="purple" />

      <div className="max-w-7xl mx-auto px-4 sm:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
          className="text-center mb-16"
        >
          <span className="inline-block mb-4 text-xs font-semibold tracking-widest uppercase text-brand-400 bg-brand-500/10 border border-brand-500/20 rounded-full px-4 py-1.5">
            What We Automate
          </span>
          <h2 className="section-title mb-4">
            Three Services.{" "}
            <span className="gradient-text">One Engine.</span>
          </h2>
          <p className="section-sub mx-auto text-center">
            Our AI crawler targets businesses that genuinely need each service —
            no cold spraying, only warm qualified leads.
          </p>
        </motion.div>

        {/* Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8">
          {services.map((svc, i) => (
            <motion.div
              key={svc.tag}
              custom={i}
              variants={cardVariants}
              initial="hidden"
              animate={inView ? "visible" : "hidden"}
              className={`group relative glass rounded-2xl p-7 border border-white/5 ${svc.border} transition-all duration-500 hover:-translate-y-2 hover:shadow-2xl ${svc.glow} cursor-default`}
            >
              {/* Animated top gradient line */}
              <div className={`absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r ${svc.gradient} rounded-t-2xl scale-x-0 group-hover:scale-x-100 transition-transform duration-500`} />

              {/* Badge */}
              <span className={`badge mb-5 ${svc.badgeColor}`}>
                <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
                {svc.badge}
              </span>

              {/* Icon */}
              <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${svc.gradient} flex items-center justify-center mb-5 shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                <svc.icon className="w-7 h-7 text-white" strokeWidth={1.5} />
              </div>

              {/* Title */}
              <h3 className="font-display font-bold text-2xl text-white mb-3">
                {svc.title}
              </h3>

              {/* Description */}
              <p className="text-slate-400 text-sm leading-relaxed mb-6">
                {svc.description}
              </p>

              {/* Target list */}
              <ul className="space-y-2.5 mb-7">
                {svc.targets.map((t) => (
                  <li key={t} className="flex items-start gap-2.5 text-sm text-slate-300">
                    <CheckCircle className={`w-4 h-4 mt-0.5 shrink-0 bg-gradient-to-br ${svc.gradient} rounded-full p-0.5 text-white`} />
                    {t}
                  </li>
                ))}
              </ul>

              {/* CTA */}
              <a
                href="/dashboard"
                className={`inline-flex items-center gap-2 text-sm font-semibold bg-gradient-to-r ${svc.gradient} bg-clip-text text-transparent group-hover:gap-3 transition-all duration-300`}
              >
                See leads for this service
                <ArrowRight className={`w-4 h-4 bg-gradient-to-r ${svc.gradient} [&>*]:fill-none`} style={{ color: "transparent", stroke: "url(#g)" }} />
                <ArrowRight className="w-4 h-4 text-current opacity-0 -ml-6 group-hover:opacity-100 group-hover:ml-0 transition-all duration-300" />
              </a>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
