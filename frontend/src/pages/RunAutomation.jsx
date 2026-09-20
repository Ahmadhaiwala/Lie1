import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Play, Globe, MessageSquare, TrendingUp,
  Zap, Clock, CheckCircle, Terminal,
  Settings, RefreshCw, ChevronRight, Wifi, WifiOff,
} from "lucide-react";
import { runJob, pollJobUntilDone, scheduleJob } from "../api/jobs";
import { checkBackendHealth } from "../api/client";
import GlowOrb from "../components/GlowOrb";

// ── Config ────────────────────────────────────────────────────────────────────
const JOBS = [
  { id: "website",      label: "Website Development", icon: Globe,          color: "from-brand-500 to-brand-600",    border: "border-brand-500/30",  selBg: "bg-brand-500/10"  },
  { id: "whatsapp_bot", label: "WhatsApp Bot",         icon: MessageSquare,  color: "from-neon/80 to-teal-500",       border: "border-neon/30",       selBg: "bg-neon/5"        },
  { id: "seo",          label: "SEO Services",          icon: TrendingUp,     color: "from-purple-500 to-pink-500",    border: "border-purple-500/30", selBg: "bg-purple-500/8"  },
];

const SCHEDULE_OPTS = [
  { value: "now",      label: "Run Once Now",             icon: Play,      mode: null },
  { value: "daily",    label: "Every Day at 9:00 AM",      icon: Clock,     mode: "daily" },
  { value: "every6",   label: "Every 6 Hours",             icon: RefreshCw, mode: "interval" },
  { value: "weekly",   label: "Every Monday at 8:00 AM",   icon: Settings,  mode: "weekly" },
];

// ── JobCard ───────────────────────────────────────────────────────────────────
function JobCard({ job, selected, onToggle }) {
  return (
    <motion.button
      onClick={onToggle}
      whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
      className={`w-full text-left glass rounded-2xl p-5 border transition-all duration-300 ${
        selected ? `${job.border} shadow-lg ${job.selBg}` : "border-white/5 hover:border-white/10"
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${job.color} flex items-center justify-center shrink-0`}>
            <job.icon className="w-5 h-5 text-white" strokeWidth={1.5} />
          </div>
          <div>
            <p className="font-semibold text-white text-sm">{job.label}</p>
            <p className="text-slate-500 text-xs mt-1">~2-4 min · 8 search queries</p>
          </div>
        </div>
        <div className={`w-5 h-5 rounded-md border flex items-center justify-center shrink-0 mt-0.5 transition-all duration-200 ${
          selected ? `bg-gradient-to-br ${job.color} border-transparent` : "border-white/20 bg-white/5"
        }`}>
          {selected && <CheckCircle className="w-3.5 h-3.5 text-white fill-white" />}
        </div>
      </div>
    </motion.button>
  );
}

// ── LogTerminal ───────────────────────────────────────────────────────────────
function LogTerminal({ lines, running }) {
  const bottomRef = useRef(null);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [lines]);

  const lineColor = (line) => {
    if (line.includes("[SUCCESS]") || line.includes("✓"))   return "text-neon";
    if (line.includes("[ERROR]")  || line.includes("FAIL"))  return "text-red-400";
    if (line.includes("Skipped")  || line.includes("[WARN]")) return "text-orange-400";
    if (line.includes("[INFO]"))                              return "text-slate-400";
    return "text-slate-300";
  };

  return (
    <div className="bg-dark-900 rounded-xl border border-white/5 p-4 font-mono text-xs h-64 overflow-y-auto">
      <div className="flex items-center gap-1.5 mb-3 pb-3 border-b border-white/5">
        <span className="w-3 h-3 rounded-full bg-red-500/70" />
        <span className="w-3 h-3 rounded-full bg-yellow-500/70" />
        <span className="w-3 h-3 rounded-full bg-green-500/70" />
        <span className="ml-2 text-slate-600">leadbot — automation</span>
      </div>
      {lines.length === 0 && (
        <p className="text-slate-700">$ python main.py  # uvicorn running on :8000</p>
      )}
      {lines.map((line, i) => (
        <p key={i} className={lineColor(line)}>{line}</p>
      ))}
      {running && (
        <motion.p animate={{ opacity: [1, 0, 1] }} transition={{ duration: 1, repeat: Infinity }} className="text-brand-400">▋</motion.p>
      )}
      <div ref={bottomRef} />
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function RunAutomation() {
  const [selected,   setSelected]   = useState(["website", "whatsapp_bot", "seo"]);
  const [schedule,   setSchedule]   = useState("now");
  const [minScore,   setMinScore]   = useState(0.5);
  const [status,     setStatus]     = useState("idle");   // idle|running|done|failed
  const [logLines,   setLogLines]   = useState([]);
  const [leadsFound, setLeadsFound] = useState(0);
  const [progress,   setProgress]   = useState(0);
  const [jobId,      setJobId]      = useState(null);
  const [jobError,   setJobError]   = useState(null);
  const [isLive,     setIsLive]     = useState(false);
  const [checking,   setChecking]   = useState(true);

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth().then(ok => {
      setIsLive(ok);
      setChecking(false);
    });
  }, []);

  const toggleJob = (id) =>
    setSelected(prev => prev.includes(id) ? prev.filter(j => j !== id) : [...prev, id]);

  // ── REAL run via API ──────────────────────────────────────────────────────
  const startRealRun = async () => {
    if (selected.length === 0) return;
    setStatus("running");
    setLogLines(["[INFO] Connecting to backend…"]);
    setLeadsFound(0);
    setProgress(5);
    setJobError(null);

    // Resolve service param
    const service = selected.length === 1 ? selected[0] : null;

    const { data, error } = await runJob({ service, min_score: minScore });
    if (error) {
      setLogLines(prev => [...prev, `[ERROR] ${error}`]);
      setStatus("failed");
      setJobError(error);
      return;
    }

    const jid = data.job_id;
    setJobId(jid);
    setLogLines(prev => [...prev, `[INFO] Job ${jid} started`, "[INFO] Polling for updates…"]);

    try {
      const final = await pollJobUntilDone(
        jid,
        (record) => {
          // Update progress and log from live job record
          setProgress(record.progress || 0);
          if (record.log_lines?.length) {
            setLogLines(record.log_lines);
          }
          if (record.result?.qualified_leads !== undefined) {
            setLeadsFound(record.result.qualified_leads);
          }
        },
        { intervalMs: 1500, timeoutMs: 600000 }
      );

      if (final.status === "done") {
        setStatus("done");
        setProgress(100);
        setLeadsFound(final.result?.qualified_leads || 0);
        setLogLines(prev => [
          ...prev,
          `[SUCCESS] Run complete — ${final.result?.qualified_leads || 0} qualified leads (${final.result?.hot_leads || 0} hot)`,
        ]);
      } else {
        setStatus("failed");
        setJobError(final.error || "Job failed");
        setLogLines(prev => [...prev, `[ERROR] ${final.error || "Job failed"}`]);
      }
    } catch (err) {
      setStatus("failed");
      setJobError(err.message);
      setLogLines(prev => [...prev, `[ERROR] ${err.message}`]);
    }
  };

  // ── DEMO run (backend offline) ────────────────────────────────────────────
  const DEMO_LOGS = [
    "[INFO]  Starting WebsiteLeadJob…",
    "[INFO]  Query 1/8: 'small business no website need web design'",
    "[INFO]  Found 5 results, crawling pages…",
    "[INFO]  ✓ Lead: Al-Noor Dental Clinic (score=0.91)",
    "[INFO]  Query 2/8: 'local restaurant no website facebook'",
    "[INFO]  ✓ Lead: Spice Route Restaurant (score=0.83)",
    "[INFO]  Starting WhatsAppBotLeadJob…",
    "[INFO]  ✓ Lead: City Physio Center (score=0.82)",
    "[INFO]  Starting SEOLeadJob…",
    "[INFO]  ✓ Lead: Karachi Law Associates (score=0.79)",
    "[INFO]  Qualifying and enriching leads…",
    "[INFO]  Composing personalised outreach for 4 leads…",
    "[SUCCESS] Run complete — 4 qualified leads (3 hot, 1 warm)",
  ];

  const startDemoRun = async () => {
    setStatus("running");
    setLogLines([]);
    setLeadsFound(0);
    setProgress(5);
    for (let i = 0; i < DEMO_LOGS.length; i++) {
      await new Promise(r => setTimeout(r, 320 + Math.random() * 380));
      setLogLines(prev => [...prev, DEMO_LOGS[i]]);
      setProgress(Math.round(((i + 1) / DEMO_LOGS.length) * 95));
      if (DEMO_LOGS[i].includes("✓")) setLeadsFound(n => n + 1);
    }
    setProgress(100);
    setStatus("done");
  };

  const handleRun = () => (isLive ? startRealRun() : startDemoRun());

  // ── Schedule ──────────────────────────────────────────────────────────────
  const handleSchedule = async (val) => {
    setSchedule(val);
    if (val === "now" || !isLive) return;

    const opt = SCHEDULE_OPTS.find(o => o.value === val);
    if (!opt?.mode) return;

    const body = { mode: opt.mode, service: selected.length === 1 ? selected[0] : null, min_score: minScore };
    if (opt.mode === "daily")    { body.hour = 9;  body.minute = 0; }
    if (opt.mode === "interval") { body.hours = 6; }
    if (opt.mode === "weekly")   { body.day_of_week = "mon"; body.hour = 8; body.minute = 0; }

    const { error } = await scheduleJob(body);
    if (error) setLogLines(prev => [...prev, `[WARN] Schedule API error: ${error}`]);
    else       setLogLines(prev => [...prev, `[INFO] Schedule set: ${opt.label}`]);
  };

  const handleReset = () => {
    setStatus("idle"); setLogLines([]); setLeadsFound(0);
    setProgress(0); setJobId(null); setJobError(null);
  };

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="relative min-h-screen pt-24 pb-20 overflow-hidden">
      <GlowOrb className="w-96 h-96 -top-20 -right-32 opacity-30" color="brand" />
      <GlowOrb className="w-80 h-80 bottom-20 -left-20 opacity-20" color="neon" />

      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-8">

        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-10">
          <div className="flex items-center gap-2 mb-1">
            <Zap className="w-6 h-6 text-brand-400" />
            <h1 className="font-display font-bold text-3xl text-white">Run Automation</h1>
          </div>
          <div className="flex items-center gap-3 mt-1">
            <p className="text-slate-400 text-sm">Trigger lead generation jobs from the browser.</p>
            {!checking && (
              <span className={`flex items-center gap-1.5 text-xs px-3 py-1 rounded-full border font-medium ${
                isLive
                  ? "bg-green-500/10 border-green-500/25 text-green-400"
                  : "bg-orange-500/10 border-orange-500/25 text-orange-400"
              }`}>
                {isLive ? <Wifi className="w-3.5 h-3.5" /> : <WifiOff className="w-3.5 h-3.5" />}
                {isLive ? "Backend Online — Real Runs" : "Backend Offline — Demo Mode"}
              </span>
            )}
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* ── Left panel ── */}
          <div className="lg:col-span-2 space-y-4">

            {/* Job selection */}
            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }}
              className="glass rounded-2xl p-5 border border-white/5">
              <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-4 flex items-center gap-2">
                <Settings className="w-3.5 h-3.5" /> Select Jobs
              </p>
              <div className="space-y-3">
                {JOBS.map(job => (
                  <JobCard key={job.id} job={job} selected={selected.includes(job.id)} onToggle={() => toggleJob(job.id)} />
                ))}
              </div>
            </motion.div>

            {/* Schedule */}
            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.15 }}
              className="glass rounded-2xl p-5 border border-white/5">
              <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-4 flex items-center gap-2">
                <Clock className="w-3.5 h-3.5" /> Schedule
              </p>
              <div className="space-y-2">
                {SCHEDULE_OPTS.map(({ value, label, icon: Icon }) => (
                  <button key={value} onClick={() => handleSchedule(value)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm transition-all text-left font-medium ${
                      schedule === value
                        ? "bg-brand-500/20 border border-brand-500/40 text-brand-300"
                        : "bg-white/3 border border-white/5 text-slate-400 hover:text-slate-300 hover:bg-white/5"
                    }`}>
                    <Icon className="w-4 h-4 shrink-0" />
                    {label}
                    {value !== "now" && !isLive && <span className="ml-auto text-orange-400 text-xs">needs backend</span>}
                  </button>
                ))}
              </div>
            </motion.div>

            {/* Min score slider */}
            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}
              className="glass rounded-2xl p-5 border border-white/5">
              <div className="flex items-center justify-between mb-3">
                <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Min Qualification Score</p>
                <span className="font-bold text-brand-400 text-sm">{Math.round(minScore * 100)}%</span>
              </div>
              <input type="range" min={0.3} max={0.9} step={0.05} value={minScore}
                onChange={e => setMinScore(parseFloat(e.target.value))}
                className="w-full accent-brand-500 cursor-pointer" />
              <div className="flex justify-between text-xs text-slate-600 mt-1">
                <span>30% (more leads)</span><span>90% (top only)</span>
              </div>
            </motion.div>
          </div>

          {/* ── Right panel ── */}
          <div className="lg:col-span-3 space-y-4">

            {/* Run control */}
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }}
              className="glass rounded-2xl p-6 border border-white/5">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                  <p className="font-semibold text-white mb-1">
                    {selected.length === 0 ? "Select at least one job" : `Run ${selected.length} job${selected.length > 1 ? "s" : ""}`}
                  </p>
                  <p className="text-slate-500 text-sm">Min score: {Math.round(minScore * 100)}% · Est. {selected.length * 3} min</p>
                </div>
                <div className="flex gap-3">
                  {(status === "done" || status === "failed") && (
                    <motion.button initial={{ scale: 0 }} animate={{ scale: 1 }}
                      onClick={handleReset} className="btn-secondary text-sm py-2.5">
                      <RefreshCw className="w-4 h-4" /> Reset
                    </motion.button>
                  )}
                  <motion.button
                    onClick={status === "idle" ? handleRun : undefined}
                    whileHover={status === "idle" ? { scale: 1.05 } : {}}
                    whileTap={status === "idle" ? { scale: 0.97 } : {}}
                    disabled={status === "running" || selected.length === 0}
                    className={`btn-primary text-sm py-2.5 ${status === "running" ? "opacity-60 cursor-not-allowed" : ""}`}>
                    {status === "running" ? (
                      <><svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="40" strokeDashoffset="10" /></svg> Running…</>
                    ) : status === "done" ? (
                      <><CheckCircle className="w-4 h-4" /> Done</>
                    ) : status === "failed" ? (
                      <><RefreshCw className="w-4 h-4" /> Retry</>
                    ) : (
                      <><Play className="w-4 h-4 fill-white" /> {isLive ? "Start Real Run" : "Start Demo"}</>
                    )}
                  </motion.button>
                </div>
              </div>

              {/* Progress bar */}
              <AnimatePresence>
                {status === "running" && (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="mt-4">
                    <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                      <motion.div
                        animate={{ width: `${progress}%` }}
                        transition={{ duration: 0.5, ease: "easeOut" }}
                        className="h-full bg-gradient-to-r from-brand-500 to-neon rounded-full"
                      />
                    </div>
                    <p className="text-xs text-slate-600 mt-1 text-right">{progress}%</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Stats row */}
            <AnimatePresence>
              {status !== "idle" && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                  className="grid grid-cols-3 gap-3">
                  {[
                    { label: "Leads Found",  value: leadsFound,                         color: "text-neon" },
                    { label: "Jobs Active",  value: status === "running" ? selected.length : 0, color: "text-brand-400" },
                    { label: "Status",       value: status === "done" ? "Complete" : status === "failed" ? "Failed" : "Running",
                      color: status === "done" ? "text-green-400" : status === "failed" ? "text-red-400" : "text-amber-400" },
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
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}
              className="glass rounded-2xl p-5 border border-white/5">
              <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-4 flex items-center gap-2">
                <Terminal className="w-3.5 h-3.5" /> Live Output
                {jobId && <span className="text-slate-700 font-normal normal-case ml-auto">job: {jobId.slice(0, 8)}…</span>}
              </p>
              <LogTerminal lines={logLines} running={status === "running"} />
            </motion.div>

            {/* Error banner */}
            <AnimatePresence>
              {jobError && status === "failed" && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                  className="glass rounded-xl p-4 border border-red-500/25 bg-red-500/5 text-red-400 text-sm flex items-start gap-3">
                  <span className="text-red-400 font-bold shrink-0">✗</span>
                  <div>
                    <p className="font-medium">Job failed</p>
                    <p className="text-red-400/70 text-xs mt-1">{jobError}</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Done CTA */}
            <AnimatePresence>
              {status === "done" && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                  className="glass rounded-2xl p-5 border border-neon/20 shadow-lg shadow-neon/5">
                  <div className="flex items-center justify-between flex-wrap gap-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-neon/10 flex items-center justify-center">
                        <CheckCircle className="w-5 h-5 text-neon" />
                      </div>
                      <div>
                        <p className="font-semibold text-white text-sm">{leadsFound} leads added to your dashboard</p>
                        <p className="text-slate-500 text-xs">Outreach drafts generated for each lead.</p>
                      </div>
                    </div>
                    <motion.a href="/dashboard" whileHover={{ scale: 1.05 }} className="btn-primary text-sm py-2.5">
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
