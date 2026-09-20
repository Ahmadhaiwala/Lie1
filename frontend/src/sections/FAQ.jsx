import { useState, useRef } from "react";
import { motion, useInView, AnimatePresence } from "framer-motion";
import { Plus, Minus } from "lucide-react";
import GlowOrb from "../components/GlowOrb";

const faqs = [
  {
    q: "How does the AI find leads?",
    a: "Our crawler fires targeted search queries on Google (e.g. 'local restaurant no website') and visits each result. The page content is then sent to an LLM that scores it for your service — checking for pain points like no website, manual WhatsApp support, or poor Google ranking. Only leads that score above your threshold make it to the dashboard.",
  },
  {
    q: "Do I need coding skills to run this?",
    a: "No. You copy your .env file with your API key, then run one command: python -m automation.scheduler --run-now. The dashboard shows all results. If you want a scheduled run, add --daily 09:00 and it runs every morning automatically.",
  },
  {
    q: "Which services can I find leads for?",
    a: "Three service types are built in: Website Development (businesses with no/outdated sites), WhatsApp Bot (businesses handling support manually via WhatsApp), and SEO (businesses with poor Google visibility). You can run all three at once or target a specific one.",
  },
  {
    q: "What does 'qualification score' mean?",
    a: "Each lead is scored 0–1 by the LLM based on how strong the buying signal is. A score of 0.8+ means the business clearly needs your service right now (Hot). 0.65–0.79 is Warm — solid opportunity. Below 0.65 is Cold — still valid but lower urgency. You can filter the dashboard by tier.",
  },
  {
    q: "Are the outreach messages personalised?",
    a: "Yes. For every qualified lead the AI writes three personalised drafts: an email (subject + body), a WhatsApp message, and a cold DM for LinkedIn or Instagram. Each draft references the specific pain points found on the business's page — not a generic template.",
  },
  {
    q: "How much does it cost to run?",
    a: "The core stack uses the free Llama 3.2 model via OpenRouter — so LLM costs are zero on the free tier. You'll need an OpenRouter API key (free to sign up). Browser crawling runs locally on your machine. The only cost is your time setting it up once.",
  },
  {
    q: "How often should I run the scheduler?",
    a: "Daily is ideal. Run it at 9am with --daily 09:00 and you'll have fresh leads ready by the time you start work. For high-volume prospecting, --every 6 runs it four times a day. The system deduplicates leads so you won't see the same business twice.",
  },
  {
    q: "Can I customise the search queries?",
    a: "Yes. Open backend/automation/jobs.py and edit the search_queries property on any job class. Add your city, industry, or niche — for example 'karachi dental clinic no website'. The more specific your queries, the more targeted your leads.",
  },
];

function FAQItem({ item, index, isOpen, onToggle }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.5 }}
      className={`glass rounded-xl border transition-all duration-300 overflow-hidden ${
        isOpen ? "border-brand-500/30 shadow-lg shadow-brand-500/10" : "border-white/5 hover:border-white/10"
      }`}
    >
      {/* Question row */}
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between gap-4 px-6 py-5 text-left group"
        aria-expanded={isOpen}
      >
        <span className={`font-semibold text-sm sm:text-base transition-colors duration-200 ${isOpen ? "text-white" : "text-slate-300 group-hover:text-white"}`}>
          {item.q}
        </span>
        <motion.div
          animate={{ rotate: isOpen ? 45 : 0 }}
          transition={{ duration: 0.25 }}
          className={`shrink-0 w-7 h-7 rounded-lg flex items-center justify-center transition-colors duration-200 ${
            isOpen ? "bg-brand-500/20 text-brand-400" : "bg-white/5 text-slate-500 group-hover:text-slate-300"
          }`}
        >
          <Plus className="w-4 h-4" />
        </motion.div>
      </button>

      {/* Answer */}
      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
          >
            <div className="px-6 pb-5 border-t border-white/5">
              <p className="text-slate-400 text-sm leading-relaxed pt-4">
                {item.a}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function FAQ() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });
  const [openIndex, setOpenIndex] = useState(0);

  return (
    <section ref={ref} className="relative z-10 py-28 overflow-hidden">
      <GlowOrb className="w-96 h-96 -right-32 top-1/2 -translate-y-1/2 opacity-20" color="brand" />

      <div className="max-w-4xl mx-auto px-4 sm:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
          className="text-center mb-14"
        >
          <span className="inline-block mb-4 text-xs font-semibold tracking-widest uppercase text-neon bg-neon/10 border border-neon/20 rounded-full px-4 py-1.5">
            FAQ
          </span>
          <h2 className="section-title mb-4">
            Common{" "}
            <span className="gradient-text">Questions</span>
          </h2>
          <p className="section-sub mx-auto text-center">
            Everything you need to know before you start automating your lead generation.
          </p>
        </motion.div>

        {/* FAQ list */}
        <div className="space-y-3">
          {faqs.map((item, i) => (
            <FAQItem
              key={i}
              item={item}
              index={i}
              isOpen={openIndex === i}
              onToggle={() => setOpenIndex(openIndex === i ? -1 : i)}
            />
          ))}
        </div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.6, duration: 0.7 }}
          className="mt-12 text-center"
        >
          <p className="text-slate-500 text-sm mb-4">Still have questions?</p>
          <a
            href="/#contact"
            className="btn-secondary inline-flex"
          >
            Ask Us Anything →
          </a>
        </motion.div>
      </div>
    </section>
  );
}
