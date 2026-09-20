import { useState } from "react";
import { motion } from "framer-motion";
import { useInView } from "framer-motion";
import { useRef } from "react";
import { Send, MessageSquare, Mail, Phone, CheckCircle, Zap } from "lucide-react";
import GlowOrb from "../components/GlowOrb";

const services = ["Website Development", "WhatsApp Bot", "SEO Services", "All Three"];

export default function Contact() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });
  const [form, setForm] = useState({ name: "", email: "", service: "", message: "" });
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    // Simulate API call
    await new Promise((r) => setTimeout(r, 1400));
    setLoading(false);
    setSubmitted(true);
  };

  return (
    <section id="contact" ref={ref} className="relative z-10 py-28 overflow-hidden">
      <GlowOrb className="w-[600px] h-[600px] -right-48 bottom-0 opacity-30" color="neon" />
      <GlowOrb className="w-96 h-96 -left-32 top-0 opacity-30" color="brand" />

      <div className="max-w-7xl mx-auto px-4 sm:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
          className="text-center mb-16"
        >
          <span className="inline-block mb-4 text-xs font-semibold tracking-widest uppercase text-purple-400 bg-purple-500/10 border border-purple-500/20 rounded-full px-4 py-1.5">
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
          {/* Left info cards */}
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.1 }}
            className="lg:col-span-2 space-y-4"
          >
            {[
              {
                icon: MessageSquare,
                title: "WhatsApp",
                value: "+92 300 0000000",
                sub: "Quick replies within minutes",
                color: "text-neon",
                bg: "bg-neon/10 border-neon/20",
              },
              {
                icon: Mail,
                title: "Email",
                value: "hello@youragency.com",
                sub: "We respond within 24 hours",
                color: "text-brand-400",
                bg: "bg-brand-500/10 border-brand-500/20",
              },
              {
                icon: Phone,
                title: "Call",
                value: "+92 300 0000000",
                sub: "Mon–Fri, 9am–6pm PKT",
                color: "text-purple-400",
                bg: "bg-purple-500/10 border-purple-500/20",
              },
            ].map(({ icon: Icon, title, value, sub, color, bg }) => (
              <motion.div
                key={title}
                whileHover={{ scale: 1.02, x: 4 }}
                className={`flex items-center gap-4 rounded-xl p-4 border ${bg} glass transition-all duration-300`}
              >
                <div className={`w-10 h-10 rounded-lg ${bg} flex items-center justify-center shrink-0`}>
                  <Icon className={`w-5 h-5 ${color}`} />
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wider">{title}</p>
                  <p className={`font-semibold ${color} text-sm`}>{value}</p>
                  <p className="text-xs text-slate-500">{sub}</p>
                </div>
              </motion.div>
            ))}

            {/* Trust badges */}
            <div className="glass rounded-xl p-5 border border-white/5 mt-2">
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-3 font-medium">Why choose us</p>
              {[
                "No upfront payment required",
                "First 10 leads completely free",
                "Results or full refund policy",
                "Setup takes under 5 minutes",
              ].map((t) => (
                <div key={t} className="flex items-center gap-2 mb-2">
                  <CheckCircle className="w-4 h-4 text-neon shrink-0" />
                  <span className="text-slate-300 text-sm">{t}</span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Right form */}
          <motion.div
            initial={{ opacity: 0, x: 40 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="lg:col-span-3"
          >
            <div className="glass rounded-2xl p-7 border border-white/5 animated-border">
              {submitted ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="text-center py-12"
                >
                  <motion.div
                    animate={{ scale: [1, 1.15, 1] }}
                    transition={{ duration: 0.5 }}
                    className="w-20 h-20 rounded-full bg-neon/10 border border-neon/30 flex items-center justify-center mx-auto mb-6"
                  >
                    <CheckCircle className="w-10 h-10 text-neon" />
                  </motion.div>
                  <h3 className="font-display font-bold text-2xl text-white mb-2">You're In!</h3>
                  <p className="text-slate-400">We'll reach out within 24 hours to set up your lead pipeline.</p>
                </motion.div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-5">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                        Your Name
                      </label>
                      <input
                        name="name"
                        required
                        value={form.name}
                        onChange={handleChange}
                        placeholder="Ahmad"
                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-600 text-sm focus:outline-none focus:border-brand-500/60 focus:bg-white/8 transition-all duration-200"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                        Email Address
                      </label>
                      <input
                        name="email"
                        type="email"
                        required
                        value={form.email}
                        onChange={handleChange}
                        placeholder="ahmad@example.com"
                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-600 text-sm focus:outline-none focus:border-brand-500/60 transition-all duration-200"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                      Service You Need Leads For
                    </label>
                    <select
                      name="service"
                      required
                      value={form.service}
                      onChange={handleChange}
                      className="w-full bg-dark-700 border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-brand-500/60 transition-all duration-200 appearance-none cursor-pointer"
                    >
                      <option value="" disabled>Select a service…</option>
                      {services.map((s) => (
                        <option key={s} value={s} className="bg-dark-800">{s}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                      Tell Us More (optional)
                    </label>
                    <textarea
                      name="message"
                      rows={4}
                      value={form.message}
                      onChange={handleChange}
                      placeholder="Target industry, location, budget range, how many leads per day…"
                      className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-600 text-sm focus:outline-none focus:border-brand-500/60 transition-all duration-200 resize-none"
                    />
                  </div>

                  <motion.button
                    type="submit"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    disabled={loading}
                    className="btn-primary w-full justify-center py-4 text-base"
                  >
                    {loading ? (
                      <>
                        <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24" fill="none">
                          <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="40" strokeDashoffset="10" />
                        </svg>
                        Setting up your pipeline…
                      </>
                    ) : (
                      <>
                        <Zap className="w-5 h-5 fill-white" />
                        Start Getting Leads Free
                        <Send className="w-5 h-5" />
                      </>
                    )}
                  </motion.button>

                  <p className="text-center text-slate-600 text-xs">
                    No credit card required · Cancel anytime · GDPR compliant
                  </p>
                </form>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
