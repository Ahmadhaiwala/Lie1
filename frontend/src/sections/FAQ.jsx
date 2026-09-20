import { useState, useRef } from "react";
import { motion, useInView, AnimatePresence } from "framer-motion";
import { Plus } from "lucide-react";

const faqs = [
  { q: "How does the AI find leads?",
    a: "Our crawler fires targeted search queries on Google and visits each result. The page content is sent to an LLM that scores it for your service — checking for pain points like no website, manual WhatsApp support, or poor Google ranking. Only leads scoring above your threshold reach the dashboard." },
  { q: "Do I need coding skills?",
    a: "No. Copy your .env file with your API key, run: python main.py — the API starts on port 8000, the dashboard shows all results. For a scheduled run, use POST /api/v1/jobs/schedule from the Run Jobs page." },
  { q: "Which services can I find leads for?",
    a: "Three service types are built in: Website Development (no/outdated sites), WhatsApp Bot (manual support via WhatsApp), and SEO (poor Google visibility). Run all three at once or target a specific one." },
  { q: "What does the qualification score mean?",
    a: "Each lead is scored 0–1 by the LLM. 0.8+ = Hot (clear need right now). 0.65–0.79 = Warm (solid opportunity). Below 0.65 = Cold. Filter the dashboard by tier to focus on the best leads first." },
  { q: "What is the business filter?",
    a: "After qualification, a second LLM pass scores each business on Online Presence (0–10) and Digital Suitability (0–10). Businesses like chai stalls, roadside vendors, and cash-only shops are automatically discarded. Everyone else gets a High or Medium priority tag." },
  { q: "Are outreach messages personalised?",
    a: "Yes. For every lead the AI writes three drafts: an email (subject + body), a WhatsApp message, and a cold DM. Each references the specific pain points found on the business page — not a generic template." },
  { q: "How much does it cost?",
    a: "The stack uses the free Llama 3.2 model via OpenRouter — zero LLM costs on the free tier. You need a free OpenRouter API key. Browser crawling runs locally. The only cost is setup time." },
  { q: "Can I customise the search queries?",
    a: "Yes. Open backend/automation/jobs.py and edit the search_queries property on any job class. Add your city, niche, or industry — e.g. 'karachi dental clinic no website'." },
];

function FAQItem({ item, isOpen, onToggle, index }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04, duration: 0.5 }}
      className={`bg-[#1a1a1a] rounded-xl border overflow-hidden transition-all duration-300 ${
        isOpen ? "border-orange-500/30" : "border-white/6 hover:border-white/10"
      }`}
    >
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between gap-4 px-6 py-5 text-left group"
        aria-expanded={isOpen}
      >
        <span className={`font-medium text-sm sm:text-base transition-colors ${isOpen ? "text-white" : "text-zinc-300 group-hover:text-white"}`}>
          {item.q}
        </span>
        <motion.div
          animate={{ rotate: isOpen ? 45 : 0 }}
          transition={{ duration: 0.2 }}
          className={`shrink-0 w-7 h-7 rounded-lg flex items-center justify-center transition-colors ${
            isOpen ? "bg-orange-500/20 text-orange-400" : "bg-white/5 text-zinc-500 group-hover:text-zinc-300"
          }`}
        >
          <Plus className="w-4 h-4" />
        </motion.div>
      </button>

      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="px-6 pb-5 border-t border-white/5">
              <p className="text-zinc-400 text-sm leading-relaxed pt-4">{item.a}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function FAQ() {
  const ref    = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });
  const [open, setOpen] = useState(0);

  return (
    <section ref={ref} className="relative z-10 py-28 overflow-hidden">
      <div className="max-w-4xl mx-auto px-4 sm:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
          className="text-center mb-14"
        >
          <span className="inline-block mb-4 text-xs font-semibold tracking-widest uppercase text-orange-400 bg-orange-500/10 border border-orange-500/20 rounded-full px-4 py-1.5">
            FAQ
          </span>
          <h2 className="section-title mb-4">
            Common{" "}
            <span className="gradient-text">Questions</span>
          </h2>
          <p className="section-sub mx-auto text-center">
            Everything you need to know before you start automating.
          </p>
        </motion.div>

        <div className="space-y-3">
          {faqs.map((item, i) => (
            <FAQItem
              key={i} item={item} index={i}
              isOpen={open === i}
              onToggle={() => setOpen(open === i ? -1 : i)}
            />
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 0.6 }}
          className="mt-10 text-center"
        >
          <p className="text-zinc-600 text-sm mb-3">Still have questions?</p>
          <a href="/#contact" className="btn-secondary inline-flex text-sm">
            Ask Us Anything →
          </a>
        </motion.div>
      </div>
    </section>
  );
}
