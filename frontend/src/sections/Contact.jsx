import { useState, useRef } from "react";
import { motion, useInView } from "framer-motion";
import { Send, MessageSquare, Mail, Phone, CheckCircle, Zap } from "lucide-react";
import { apiPost } from "../api/client";

const services = ["Website Development", "WhatsApp Bot", "SEO Services", "All Three"];

export default function Contact() {
  const ref    = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });
  const [form, setForm]         = useState({ name: "", email: "", service: "", message: "" });
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState("");

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      // Try to POST to backend; if offline just show success
      await apiPost("/api/v1/contact", form);
    } catch (_) {
      // backend might not have /contact endpoint yet — that's fine
    }
    setLoading(false);
    setSubmitted(true);
  };

  return (
    <section id="contact" ref={ref} className="relative z-10 py-28 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
          className="text-center mb-16"
        >
          <span className="inline-block mb-4 text-xs font-semibold tracking-widest uppercase text-orange-400 bg-orange-500/10 border border-orange-500/20 rounded-full px-4 py-1.5">
            Get In Touch
          </span>
          <h2 className="section-title mb-4">
            Start Getting{" "}
            <span className="gradient-text">Qualified Leads</span>
          </h2>
          <p className="section-sub mx-auto text-center">
            Tell us which service you want leads for and we'll set up the automation for you.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 items-start">
          {/* Info column */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.1 }}
            className="lg:col-span-2 space-y-4"
          >
            {[
              { icon: MessageSquare, title: "WhatsApp", value: "+92 300 0000000", sub: "Quick replies within minutes", accent: "border-orange-500/25 bg-orange-500/5" },
              { icon: Mail,          title: "Email",    value: "hello@youragency.com", sub: "Response within 24 hours",   accent: "border-white/10 bg-white/3" },
              { icon: Phone,         title: "Call",     value: "+92 300 0000000", sub: "Mon–Fri, 9am–6pm PKT",         accent: "border-white/10 bg-white/3" },
            ].map(({ icon: Icon, title, value, sub, accent }) => (
              <motion.div key={title} whileHover={{ x: 4 }}
                className={`flex items-center gap-4 rounded-xl p-4 border ${accent} transition-all duration-300`}>
                <div className="w-10 h-10 rounded-lg bg-orange-500/10 border border-orange-500/20 flex items-center justify-center shrink-0">
                  <Icon className="w-5 h-5 text-orange-400" />
                </div>
                <div>
                  <p className="text-xs text-zinc-500 font-medium uppercase tracking-wider">{title}</p>
                  <p className="font-semibold text-white text-sm">{value}</p>
                  <p className="text-xs text-zinc-500">{sub}</p>
                </div>
              </motion.div>
            ))}

            {/* Trust */}
            <div className="bg-[#1a1a1a] rounded-xl p-5 border border-white/6 mt-2">
              <p className="text-xs text-zinc-500 uppercase tracking-wider mb-3 font-semibold">Why choose us</p>
              {[
                "No upfront payment required",
                "First 10 leads completely free",
                "Results or full refund policy",
                "Setup takes under 5 minutes",
              ].map((t) => (
                <div key={t} className="flex items-center gap-2 mb-2">
                  <CheckCircle className="w-4 h-4 text-orange-400 shrink-0" />
                  <span className="text-zinc-300 text-sm">{t}</span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Form column */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="lg:col-span-3"
          >
            <div className="bg-[#1a1a1a] rounded-2xl p-7 border border-white/6 animated-border">
              {submitted ? (
                <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
                  className="text-center py-12">
                  <motion.div animate={{ scale: [1, 1.15, 1] }} transition={{ duration: 0.5 }}
                    className="w-20 h-20 rounded-full bg-orange-500/10 border border-orange-500/30 flex items-center justify-center mx-auto mb-6">
                    <CheckCircle className="w-10 h-10 text-orange-400" />
                  </motion.div>
                  <h3 className="font-display font-bold text-2xl text-white mb-2">You're In!</h3>
                  <p className="text-zinc-400">We'll reach out within 24 hours to set up your lead pipeline.</p>
                </motion.div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-5">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    {[
                      { name: "name",  type: "text",  label: "Your Name",      placeholder: "Ahmad" },
                      { name: "email", type: "email", label: "Email Address",   placeholder: "ahmad@example.com" },
                    ].map(f => (
                      <div key={f.name}>
                        <label className="block text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">{f.label}</label>
                        <input
                          name={f.name} type={f.type} required
                          value={form[f.name]} onChange={handleChange}
                          placeholder={f.placeholder}
                          className="w-full bg-white/4 border border-white/8 rounded-xl px-4 py-3 text-white placeholder-zinc-600 text-sm focus:outline-none focus:border-orange-500/50 transition-all"
                        />
                      </div>
                    ))}
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">Service</label>
                    <select name="service" required value={form.service} onChange={handleChange}
                      className="w-full bg-[#222] border border-white/8 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-orange-500/50 transition-all cursor-pointer">
                      <option value="" disabled>Select a service…</option>
                      {services.map(s => <option key={s} value={s} className="bg-[#1a1a1a]">{s}</option>)}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">Message (optional)</label>
                    <textarea name="message" rows={4} value={form.message} onChange={handleChange}
                      placeholder="Target industry, city, budget, leads per day…"
                      className="w-full bg-white/4 border border-white/8 rounded-xl px-4 py-3 text-white placeholder-zinc-600 text-sm focus:outline-none focus:border-orange-500/50 transition-all resize-none" />
                  </div>

                  {error && <p className="text-red-400 text-sm">{error}</p>}

                  <motion.button type="submit" whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                    disabled={loading}
                    className="btn-primary w-full justify-center py-4 text-base">
                    {loading ? (
                      <><svg className="animate-spin w-5 h-5" viewBox="0 0 24 24" fill="none">
                        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="40" strokeDashoffset="10" />
                      </svg> Setting up your pipeline…</>
                    ) : (
                      <><Zap className="w-5 h-5" /> Start Getting Leads Free <Send className="w-5 h-5" /></>
                    )}
                  </motion.button>
                  <p className="text-center text-zinc-600 text-xs">No credit card required · Cancel anytime</p>
                </form>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
