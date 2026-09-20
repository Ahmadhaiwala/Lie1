import { useRef, useState } from "react";
import { motion, useInView, AnimatePresence } from "framer-motion";
import { Star, Quote, ChevronLeft, ChevronRight } from "lucide-react";
import GlowOrb from "../components/GlowOrb";

const testimonials = [
  {
    id: 1,
    name: "Omar Farooq",
    role: "Owner, Farooq Web Solutions",
    avatar: "OF",
    avatarColor: "from-brand-500 to-purple-500",
    rating: 5,
    text: "Within 48 hours of running the website job, I had 23 qualified leads in my dashboard — all local businesses with no website. I closed 3 deals in the first week. This automation paid for itself 10x over.",
    service: "Website Development",
    serviceColor: "text-brand-400 bg-brand-500/10 border-brand-500/20",
    result: "3 deals in week 1",
  },
  {
    id: 2,
    name: "Sara Ahmed",
    role: "Founder, BotCraft Agency",
    avatar: "SA",
    avatarColor: "from-neon/80 to-teal-500",
    rating: 5,
    text: "The WhatsApp bot leads are insanely targeted. It found restaurants, clinics and boutiques that were literally drowning in manual messages. The outreach drafts it writes are so personalised I barely had to edit them.",
    service: "WhatsApp Bot",
    serviceColor: "text-neon bg-neon/10 border-neon/20",
    result: "18 hot leads first run",
  },
  {
    id: 3,
    name: "Bilal Hussain",
    role: "SEO Consultant, Lahore",
    avatar: "BH",
    avatarColor: "from-purple-500 to-pink-500",
    rating: 5,
    text: "I used to spend 3 hours a day finding SEO prospects manually. Now I run the scheduler every morning, check the dashboard over coffee, and I already have qualified contacts with their pain points listed. Game changer.",
    service: "SEO Services",
    serviceColor: "text-purple-400 bg-purple-500/10 border-purple-500/20",
    result: "3 hrs/day saved",
  },
  {
    id: 4,
    name: "Ayesha Malik",
    role: "Digital Agency Director",
    avatar: "AM",
    avatarColor: "from-orange-400 to-brand-500",
    rating: 5,
    text: "We run all three services and the leads from each job are perfectly targeted. The scoring system is accurate — 9 out of 10 hot leads actually converted to calls. Best investment for our agency's outbound pipeline.",
    service: "All Services",
    serviceColor: "text-orange-400 bg-orange-500/10 border-orange-500/20",
    result: "90% call conversion",
  },
  {
    id: 5,
    name: "Zain ul Abideen",
    role: "Freelance Developer",
    avatar: "ZA",
    avatarColor: "from-teal-400 to-brand-500",
    rating: 5,
    text: "As a solo freelancer I never had time for business development. This system does it for me. I set the scheduler to run every morning at 9am — fresh leads waiting when I wake up. It's like having a sales team.",
    service: "Website Development",
    serviceColor: "text-brand-400 bg-brand-500/10 border-brand-500/20",
    result: "2 new clients/month",
  },
];

function StarRating({ count = 5 }) {
  return (
    <div className="flex gap-0.5">
      {Array.from({ length: count }).map((_, i) => (
        <Star key={i} className="w-4 h-4 fill-amber-400 text-amber-400" />
      ))}
    </div>
  );
}

function TestimonialCard({ t, isActive }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: isActive ? 1 : 0.4, scale: isActive ? 1 : 0.92 }}
      transition={{ duration: 0.4 }}
      className={`relative glass rounded-2xl p-7 border transition-all duration-500 h-full flex flex-col ${
        isActive ? "border-white/10 shadow-2xl" : "border-white/5"
      }`}
    >
      {/* Big quote icon */}
      <Quote className="absolute top-5 right-6 w-10 h-10 text-brand-500/10 rotate-180" />

      {/* Stars */}
      <StarRating count={t.rating} />

      {/* Text */}
      <p className="mt-4 text-slate-300 text-sm leading-relaxed flex-1 italic">
        "{t.text}"
      </p>

      {/* Service badge */}
      <span className={`mt-5 inline-flex items-center gap-1.5 badge border text-xs ${t.serviceColor}`}>
        <span className="w-1.5 h-1.5 rounded-full bg-current" />
        {t.service}
      </span>

      {/* Result pill */}
      <div className="mt-3 inline-flex items-center gap-2 bg-neon/5 border border-neon/20 rounded-lg px-3 py-1.5">
        <span className="text-neon text-xs font-bold">✓ Result:</span>
        <span className="text-slate-300 text-xs">{t.result}</span>
      </div>

      {/* Author */}
      <div className="mt-5 flex items-center gap-3 pt-4 border-t border-white/5">
        <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${t.avatarColor} flex items-center justify-center text-white font-bold text-sm shrink-0`}>
          {t.avatar}
        </div>
        <div>
          <p className="text-white font-semibold text-sm">{t.name}</p>
          <p className="text-slate-500 text-xs">{t.role}</p>
        </div>
      </div>
    </motion.div>
  );
}

export default function Testimonials() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });
  const [active, setActive] = useState(0);

  const prev = () => setActive((a) => (a === 0 ? testimonials.length - 1 : a - 1));
  const next = () => setActive((a) => (a === testimonials.length - 1 ? 0 : a + 1));

  // Show 3 cards on desktop, 1 on mobile
  const visibleIndices = [
    (active - 1 + testimonials.length) % testimonials.length,
    active,
    (active + 1) % testimonials.length,
  ];

  return (
    <section ref={ref} className="relative z-10 py-28 overflow-hidden">
      <GlowOrb className="w-[500px] h-[500px] left-1/2 -translate-x-1/2 top-0 opacity-20" color="purple" />

      <div className="max-w-7xl mx-auto px-4 sm:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
          className="text-center mb-16"
        >
          <span className="inline-block mb-4 text-xs font-semibold tracking-widest uppercase text-amber-400 bg-amber-500/10 border border-amber-500/20 rounded-full px-4 py-1.5">
            Real Results
          </span>
          <h2 className="section-title mb-4">
            What Our Clients{" "}
            <span className="gradient-text">Are Saying</span>
          </h2>
          <p className="section-sub mx-auto text-center">
            Agencies and freelancers using LeadBot AI to fill their pipelines every single day.
          </p>
        </motion.div>

        {/* Desktop: 3-card carousel */}
        <div className="hidden md:grid grid-cols-3 gap-5">
          {visibleIndices.map((idx, pos) => (
            <TestimonialCard
              key={testimonials[idx].id}
              t={testimonials[idx]}
              isActive={pos === 1}
            />
          ))}
        </div>

        {/* Mobile: single card */}
        <div className="md:hidden">
          <AnimatePresence mode="wait">
            <motion.div
              key={active}
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -40 }}
              transition={{ duration: 0.35 }}
            >
              <TestimonialCard t={testimonials[active]} isActive />
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-center gap-4 mt-10">
          <motion.button
            onClick={prev}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            aria-label="Previous"
            className="w-10 h-10 rounded-full glass border border-white/10 flex items-center justify-center text-slate-400 hover:text-white hover:border-brand-500/40 transition-all"
          >
            <ChevronLeft className="w-5 h-5" />
          </motion.button>

          <div className="flex gap-2">
            {testimonials.map((_, i) => (
              <button
                key={i}
                onClick={() => setActive(i)}
                className={`rounded-full transition-all duration-300 ${
                  i === active
                    ? "w-6 h-2 bg-brand-400"
                    : "w-2 h-2 bg-slate-700 hover:bg-slate-500"
                }`}
                aria-label={`Go to testimonial ${i + 1}`}
              />
            ))}
          </div>

          <motion.button
            onClick={next}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            aria-label="Next"
            className="w-10 h-10 rounded-full glass border border-white/10 flex items-center justify-center text-slate-400 hover:text-white hover:border-brand-500/40 transition-all"
          >
            <ChevronRight className="w-5 h-5" />
          </motion.button>
        </div>

        {/* Summary strip */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.5, duration: 0.7 }}
          className="mt-14 grid grid-cols-3 gap-4"
        >
          {[
            { value: "500+", label: "Happy Clients" },
            { value: "4.9★", label: "Average Rating" },
            { value: "12,000+", label: "Leads Generated" },
          ].map(({ value, label }) => (
            <div
              key={label}
              className="glass rounded-xl p-4 border border-white/5 text-center hover:border-white/10 transition-all"
            >
              <p className="font-display font-bold text-2xl gradient-text">{value}</p>
              <p className="text-slate-500 text-xs mt-1">{label}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
