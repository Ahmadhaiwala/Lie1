import { useRef, useState } from "react";
import { motion, useInView, AnimatePresence } from "framer-motion";
import { Star, ChevronLeft, ChevronRight } from "lucide-react";

const testimonials = [
  {
    id: 1, name: "Omar Farooq",  role: "Owner, Farooq Web Solutions",  avatar: "OF",
    rating: 5, service: "Website Dev",  result: "3 deals in week 1",
    text: "Within 48 hours I had 23 qualified leads — all local businesses with no website. Closed 3 deals in the first week. Paid for itself 10x over.",
  },
  {
    id: 2, name: "Sara Ahmed",   role: "Founder, BotCraft Agency",     avatar: "SA",
    rating: 5, service: "WhatsApp Bot", result: "18 hot leads first run",
    text: "The WhatsApp bot leads are insanely targeted. Found restaurants and clinics drowning in manual messages. Outreach drafts barely needed editing.",
  },
  {
    id: 3, name: "Bilal Hussain",role: "SEO Consultant, Lahore",       avatar: "BH",
    rating: 5, service: "SEO",          result: "3 hrs/day saved",
    text: "I used to spend 3 hours finding SEO prospects manually. Now I run the scheduler every morning and have qualified contacts with pain points listed.",
  },
  {
    id: 4, name: "Ayesha Malik", role: "Digital Agency Director",      avatar: "AM",
    rating: 5, service: "All Services", result: "90% call conversion",
    text: "The scoring system is accurate — 9 out of 10 hot leads converted to calls. Best investment for our agency's outbound pipeline.",
  },
  {
    id: 5, name: "Zain ul Abideen", role: "Freelance Developer",       avatar: "ZA",
    rating: 5, service: "Website Dev",  result: "2 new clients/month",
    text: "As a solo freelancer I never had time for BD. Set the scheduler at 9am — fresh leads waiting every morning. Like having a sales team.",
  },
];

function Card({ t, active }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: active ? 1 : 0.35, scale: active ? 1 : 0.93 }}
      transition={{ duration: 0.35 }}
      className={`relative bg-[#1a1a1a] rounded-2xl p-6 border h-full flex flex-col transition-all duration-300 ${
        active ? "border-orange-500/30 shadow-xl shadow-orange-500/5" : "border-white/5"
      }`}
    >
      {active && <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-orange-500 to-orange-300 rounded-t-2xl" />}

      {/* Stars */}
      <div className="flex gap-0.5 mb-4">
        {Array.from({ length: t.rating }).map((_, i) => (
          <Star key={i} className="w-4 h-4 fill-orange-400 text-orange-400" />
        ))}
      </div>

      {/* Text */}
      <p className="text-zinc-300 text-sm leading-relaxed flex-1 italic">"{t.text}"</p>

      {/* Result */}
      <div className="mt-4 inline-flex items-center gap-2 bg-orange-500/8 border border-orange-500/20 rounded-lg px-3 py-1.5">
        <span className="text-orange-400 text-xs font-bold">✓</span>
        <span className="text-zinc-300 text-xs">{t.result}</span>
      </div>

      {/* Author */}
      <div className="mt-4 flex items-center gap-3 pt-4 border-t border-white/5">
        <div className="w-9 h-9 rounded-full bg-orange-500 flex items-center justify-center text-black font-bold text-sm shrink-0">
          {t.avatar}
        </div>
        <div>
          <p className="text-white font-semibold text-sm">{t.name}</p>
          <p className="text-zinc-500 text-xs">{t.role}</p>
        </div>
        <span className="ml-auto text-xs text-orange-400 bg-orange-500/10 border border-orange-500/20 px-2 py-0.5 rounded-full">
          {t.service}
        </span>
      </div>
    </motion.div>
  );
}

export default function Testimonials() {
  const ref    = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });
  const [active, setActive] = useState(0);
  const n = testimonials.length;

  const prev = () => setActive(a => (a === 0 ? n - 1 : a - 1));
  const next = () => setActive(a => (a === n - 1 ? 0 : a + 1));

  const visible = [
    (active - 1 + n) % n,
    active,
    (active + 1) % n,
  ];

  return (
    <section ref={ref} className="relative z-10 py-28 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
          className="text-center mb-16"
        >
          <span className="inline-block mb-4 text-xs font-semibold tracking-widest uppercase text-orange-400 bg-orange-500/10 border border-orange-500/20 rounded-full px-4 py-1.5">
            Real Results
          </span>
          <h2 className="section-title mb-4">
            What Clients{" "}
            <span className="gradient-text">Are Saying</span>
          </h2>
          <p className="section-sub mx-auto text-center">
            Agencies and freelancers filling their pipelines every day.
          </p>
        </motion.div>

        {/* Desktop 3-col */}
        <div className="hidden md:grid grid-cols-3 gap-5">
          {visible.map((idx, pos) => (
            <Card key={testimonials[idx].id} t={testimonials[idx]} active={pos === 1} />
          ))}
        </div>

        {/* Mobile single */}
        <div className="md:hidden">
          <AnimatePresence mode="wait">
            <motion.div key={active}
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -40 }}
              transition={{ duration: 0.3 }}
            >
              <Card t={testimonials[active]} active />
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-center gap-4 mt-10">
          <motion.button onClick={prev} whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }}
            aria-label="Previous"
            className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-zinc-400 hover:text-white hover:border-orange-500/40 transition-all">
            <ChevronLeft className="w-5 h-5" />
          </motion.button>
          <div className="flex gap-2">
            {testimonials.map((_, i) => (
              <button key={i} onClick={() => setActive(i)} aria-label={`Testimonial ${i + 1}`}
                className={`rounded-full transition-all duration-300 ${
                  i === active ? "w-6 h-2 bg-orange-400" : "w-2 h-2 bg-zinc-700 hover:bg-zinc-500"
                }`} />
            ))}
          </div>
          <motion.button onClick={next} whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }}
            aria-label="Next"
            className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-zinc-400 hover:text-white hover:border-orange-500/40 transition-all">
            <ChevronRight className="w-5 h-5" />
          </motion.button>
        </div>

        {/* Summary strip */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.5 }}
          className="mt-14 grid grid-cols-3 gap-4"
        >
          {[
            { value: "500+",    label: "Happy Clients"    },
            { value: "4.9★",   label: "Average Rating"   },
            { value: "12,000+", label: "Leads Generated"  },
          ].map(({ value, label }) => (
            <div key={label} className="bg-[#1a1a1a] border border-white/5 rounded-xl p-4 text-center hover:border-orange-500/20 transition-all">
              <p className="font-display font-bold text-2xl gradient-text">{value}</p>
              <p className="text-zinc-500 text-xs mt-1">{label}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
