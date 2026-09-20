import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Play, Square, Globe, MessageSquare, TrendingUp,
  Zap, Clock, CheckCircle, AlertCircle, Terminal,
  Settings, RefreshCw, Download, ChevronRight,
} from "lucide-react";
import GlowOrb from "../components/GlowOrb";

// ── mock job runner (simulates backend calls) ─────────────────────────────

const JOBS = [
  {
    id: "website",
    label: "Website Development",
    icon: Globe,
    color: "from-brand-500 to-brand-600",
    border: "border-brand-500/30",
    glow: "shadow-brand-500/20",
    description: "Finds businesses with no website or outdated designs.",
    estimatedTime: "~2-4 min",
    queries: 8,
  },
  {
    id: "whatsapp_bot",
    label: "WhatsApp Bot",
    icon: MessageSquare,
    color: "from-neon/80 to-teal-500",
    border: "border-neon/30",
    glow: "shadow-neon/20",
    description: "Targets businesses handling WhatsApp manually.",
    estimatedTime: "~2-4 min",
    queries: 8,
  },
  {
    id: "seo",
    label: "SEO Services",
    icon: TrendingUp,
    color: "from-purple-500 to-pink-500",
    border: "border-purple-500/30",
    glow: "shadow-purple-500/20",
    description: "Identifies businesses with poor Google visibility.",
    estimatedTime: "~2-4 min",
    queries: 8,
  },
];

const SCHEDULE_OPTIONS = [
  { value: "now",    label: "Run Once Now",           icon: Play },
  { value: "daily",  label: "Every Day at 9:00 AM",   icon: Clock },
  { value: "every6", label: "Every 6 Hours",           icon: RefreshCw },
  { value: "weekly", label: "Every Monday at 8:00 AM", icon: Settings },
];

const LOG_LINES = [
  "[INFO]  Starting WebsiteLeadJob...",
  "[INFO]  Query 1/8: 'small business no website need web design'",
  "[INFO]  Found 5 results, crawling pages...",
  "[INFO]  ✓ Lead: Al-Noor Dental Clinic (score=0.91)",
  "[INFO]  Query 2/8: 'local restaurant no website contact us facebook'",
  "[INFO]  Found 5 results, crawling pages...",
  "[INFO]  ✓ Lead: Spice Route Restaurant (score=0.83)",
  "[INFO]  Query 3/8: 'startup needs website development affordable'",
  "[INFO]  Found 3 results, crawling pages...",
  "[INFO]  Skipped: low score (0.32)",
  "[INFO]  ✓ Lead: Ahmed Photography Studio (score=0.71)",
  "[INFO]  Job complete: 3 leads found in 47s",
  "[INFO]  Qualifying and enriching leads...",
  "[INFO]  Composing outreach for 3 leads...",
  "[SUCCESS] Run complete — 3 qualified leads saved to dashboard",
];

// ── components ────────────────────────────────────────────────────────────

function JobCard({ job, selected, onToggle }) {
  const Icon = job.icon;
  return (
    <motion.button
      onClick={onToggle}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={`w-full text-left glass rounded-2xl p-5 border transition-all duration-300 ${
        selected
          ? `${job.border} shadow-lg ${job.glow}`
          : "border-white/5 hover:border-white/10"
      }`}
      aria-pressed={selected}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${job.color} flex items-center justify-center shrink-0 shadow-lg`}>
            <Icon className="w-5 h-5 text-white" strokeWidth={1.5} />
          </div>
          <div>
            <p className="font-semibold text-white text-sm">{job.label}</p>
            <p className="text-slate-500 text-xs mt-1">{job.description}</p>
            <div className="flex items-center gap-3 mt-2">
              <span className="text-xs text-slate-600 flex items-center gap-1">
                <Clock className="w-3 h-3" /> {job.estimatedTime}
              </span>
              <span className="text-xs text-slate-600 flex items-center gap-1">
                <Terminal className="w-3 h-3" /> {job.queries} queries
              </span>
            </div>
          </div>
        </div>
        {/* Checkbox */}
        <div className={`w-5 h-5 rounded-md border flex items-center justify-center shrink-0 transition-all duration-200 mt-0.5 ${
          selected
            ? `bg-gradient-to-br ${job.color} border-transparent`
            : "border-white/20 bg-white/5"
        }`}>
          {selected && <CheckCircle className="w-3.5 h-3.5 text-white fill-white" />}
        </div>
      </div>
    </motion.button>
  );
}

function LogTerminal({ lines, running }) {
  return (
    <div className="bg-dark-900 rounded-xl border border-white/5 p-4 font-mono text-xs h-64 overflow-y-auto space-y-1">
      {/* Terminal header */}
      <div className="flex items-center gap-1.5 mb-3 pb-3 border-b border-white/5">
        <span className="w-3 h-3 rounded-full bg-red-500/70" />
        <span className="w-3 h-3 rounded-full bg-yellow-500/70" />
        <span className="w-3 h-3 rounded-full bg-green-500/70" />
        <span className="ml-2 text-slate-600">leadbot — scheduler</span>
      </div>

      {lines.length === 0 && (
        <p className="text-slate-700">$ python -m automation.scheduler --run-now</p>
      )}

      {lines.map((line, i) => (
        <motion.p
          key={i}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.2 }}
          className={
            line.includes("[SUCCESS]") ? "text-neon" :
            line.includes("[INFO]")    ? "text-slate-400" :
            line.includes("✓")        ? "text-green-400" :
            line.includes("Skipped")  ? "text-orange-400" :
            "text-slate-300"
          }
        >
          {line}
        </motion.p>
      ))}

      {running && (
        <motion.p
          animate={{ opacity: [1, 0, 1] }}
          transition={{ duration: 1, repeat: Infinity }}
          className="text-brand-400"
        >
          ▋
        </motion.p>
      )}
    </div>
  );
}

// ── main page ─────────────────────────────────────────────────────────────

export default function RunAutomation() {
  const [selected, setSelected] = useState(["website", "whatsapp_bot", "seo"]);
  const [schedule, setSchedule] = useState("now");
  const [minScore, setMinScore] = useState(0.5);
  const [status, setStatus] = useState("idle"); // idle | running | done | error
  const [logLines, setLogLines] = useState([]);
  const [leadsFound, setLeadsFound] = useState(0);

  const toggleJob = (id) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((j) => j !== id) : [...prev, id]
    );
  };

  const handleRun = async () => {
    if (selected.length === 0) return;
    setStatus("running");
    setLogLines([]);
    setLeadsFound(0);

    // Simulate log output line by line
    for (let i = 0; i < LOG_LINES.length; i++) {
      await new Promise((r) => setTimeout(r, 300 + Math.random() * 400));
      setLogLines((prev) => [...prev, LOG_LINES[i]]);
      if (LOG_LINES[i].includes("✓ Lead:")) {
        setLeadsFound((n) => n + 1);
      }
    }
    setStatus("done");
  };

  const handleReset = () => {
    setStatus("idle");
    setLogLines([]);
    setLeadsFound(0);
  };

  return (
    <div className="relative min-h-screen pt-24 pb-20 overflow-hidden">
      <GlowOrb className="w-96 h-96 -top-20 -right-32 opacity-30" color="brand" />
      <GlowOrb className="w-80 h-80 bottom-20 -left-20 opacity-20" color="neon" />

      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-10"
        >
          <div className="flex items-center gap-2 mb-1">
            <Zap className="w-6 h-6 text-brand-400" />
            <h1 className="font-display font-bold text-3xl text-white">Run Automation</h1>
          </div>
          <p className="text-slate-400 text-sm">
            Configure and trigger lead generation jobs directly from the browser.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* Left panel — config */}
          <div className="lg:col-span-2 space-y-5">
            {/* Job selection */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="glass rounded-2xl p-5 border border-white/5"
            >
              <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-4 flex items-center gap-2">
                <Settings className="w-3.5 h-3.5" /> Select Jobs
              </p>
              <div className="space-y-3">
                {JOBS.map((job) => (
                  <JobCard
                    key={job.id}
                    job={job}
                    selected={selected.includes(job.id)}
                    onToggle={() => toggleJob(job.id)}
                  />
                ))}
              </div>
            </motion.div>

            {/* Schedule */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.15 }}
              className="glass rounded-2xl p-5 border border-white/5"
            >
              <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-4 flex items-center gap-2">
                <Clock className="w-3.5 h-3.5" /> Schedule
              </p>
              <div className="grid grid-cols-1 gap-2">
                {SCHEDULE_OPTIONS.map(({ value, label, icon: Icon }) => (
                  <button
                    key={value}
                    onClick={() => setSchedule(value)}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm transition-all duration-200 text-left ${
                      schedule === value
                        ? "bg-brand-500/20 border border-brand-500/40 text-brand-300"
                        : "bg-white/3 border border-white/5 text-slate-400 hover:text-slate-300 hover:bg-white/5"
                    }`}
                  >
                    <Icon className="w-4 h-4 shrink-0" />
                    {label}
                  </button>
                ))}
              </div>
            </motion.div>

            {/* Min score */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="glass rounded-2xl p-5 border border-white/5"
            >
              <div className="flex items-center justify-between mb-3">
                <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">
                  Min Qualification Score
                </p>
                <span className="font-bold text-brand-400 text-sm">
                  {Math.round(minScore * 100)}%
                </span>
              </div>
              <input
                type="range"
                min={0.3}
                max={0.9}
                step={0.05}
                value={minScore}
                onChange={(e) => setMinScore(parseFloat(e.target.value))}
                className="w-full accent-brand-500 cursor-pointer"
              />
              <div className="flex justify-between text-xs text-slate-600 mt-1">
                <span>30% (more leads)</span>
                <span>90% (top only)</span>
              </div>
            </motion.div>
          </div>

          {/* Right panel — run + terminal */}
          <div className="lg:col-span-3 space-y-5">
            {/* Run button */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="glass rounded-2xl p-6 border border-white/5"
            >
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                  <p className="font-semibold text-white mb-1">
                    {selected.length === 0
                      ? "Select at least one job"
                      : `Run ${selected.length} job${selected.length > 1 ? "s" : ""} · ${SCHEDULE_OPTIONS.find(s => s.value === schedule)?.label}`}
                  </p>
                  <p className="text-slate-500 text-sm">
                    Min score: {Math.round(minScore * 100)}% · Est. {selected.length * 3} min
                  </p>
                </div>

                <div className="flex gap-3">
                  {status === "done" && (
                    <motion.button
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      onClick={handleReset}
                      className="btn-secondary text-sm py-2.5"
                    >
                      <RefreshCw className="w-4 h-4" /> Reset
                    </motion.button>
                  )}

                  <motion.button
                    onClick={status === "idle" ? handleRun : undefined}
                    whileHover={status === "idle" ? { scale: 1.05 } : {}}
                    whileTap={status === "idle" ? { scale: 0.97 } : {}}
                    disabled={status === "running" || selected.length === 0}
                    className={`btn-primary text-sm py-2.5 ${
                      status === "running" ? "opacity-60 cursor-not-allowed" : ""
                    }`}
                  >
                    {status === "running" ? (
                      <>
                        <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                          <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="40" strokeDashoffset="10" />
                        </svg>
                        Running…
                      </>
                    ) : status === "done" ? (
                      <>
                        <CheckCircle className="w-4 h-4" /> Done
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 fill-white" /> Start Jobs
                      </>
                    )}
                  </motion.button>
                </div>
              </div>

              {/* Progress bar */}
              <AnimatePresence>
                {status === "running" && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="mt-4"
                  >
                    <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                      <motion.div
                        animate={{ width: ["0%", "90%"] }}
                        transition={{ duration: LOG_LINES.length * 0.35, ease: "linear" }}
                        className="h-full bg-gradient-to-r from-brand-500 to-neon rounded-full"
                      />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Stats row */}
            <AnimatePresence>
              {status !== "idle" && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="grid grid-cols-3 gap-3"
                >
                  {[
                    { label: "Leads Found", value: leadsFound, color: "text-neon" },
                    { label: "Jobs Running", value: status === "running" ? selected.length : 0, color: "text-brand-400" },
                    { label: "Status", value: status === "done" ? "Complete" : "Running", color: status === "done" ? "text-green-400" : "text-amber-400" },
                  ].map(({ label, value, color }) => (
                    <div key={label} className="glass rounded-xl p-4 border border-white/5 text-center">
                      <p className={`font-bold text-xl ${color}`}>{value}</p>
                      <p className="text-slate-500 text-xs mt-1">{label}</p>
                    </div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Terminal */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="glass rounded-2xl p-5 border border-white/5"
            >
              <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-4 flex items-center gap-2">
                <Terminal className="w-3.5 h-3.5" /> Live Output
              </p>
              <LogTerminal lines={logLines} running={status === "running"} />
            </motion.div>

            {/* Done CTA */}
            <AnimatePresence>
              {status === "done" && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="glass rounded-2xl p-5 border border-neon/20 shadow-lg shadow-neon/5"
                >
                  <div className="flex items-center justify-between flex-wrap gap-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-neon/10 flex items-center justify-center">
                        <CheckCircle className="w-5 h-5 text-neon" />
                      </div>
                      <div>
                        <p className="font-semibold text-white text-sm">
                          {leadsFound} leads added to your dashboard
                        </p>
                        <p className="text-slate-500 text-xs">Outreach drafts have been generated for each lead.</p>
                      </div>
                    </div>
                    <motion.a
                      href="/dashboard"
                      whileHover={{ scale: 1.05 }}
                      className="btn-primary text-sm py-2.5"
                    >
                      View Dashboard <ChevronRight className="w-4 h-4" />
                    </motion.a>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}
