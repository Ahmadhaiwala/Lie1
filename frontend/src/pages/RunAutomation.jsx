import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Play, Globe, MessageSquare, TrendingUp,
  Zap, Clock, CheckCircle, Terminal, X,
  Settings, RefreshCw, ChevronRight, Wifi, WifiOff,
} from "lucide-react";
import { runJob, pollJobUntilDone, scheduleJob } from "../api/jobs";
import { checkBackendHealth } from "../api/client";
import GlowOrb from "../components/GlowOrb";

const JOBS = [
  { id: "website",      label: "Website Development", icon: Globe,          desc: "Finds businesses with no/outdated website",       iconBg: "bg-orange-500",  border: "border-orange-500/30" },
  { id: "whatsapp_bot", label: "WhatsApp Bot",         icon: MessageSquare,  desc: "Targets businesses handling WhatsApp manually",   iconBg: "bg-white",       border: "border-white/15"      },
  { id: "seo",          label: "SEO Services",          icon: TrendingUp,     desc: "Identifies businesses with poor Google ranking",  iconBg: "bg-orange-400",  border: "border-orange-400/25" },
];

const SCHEDULE_OPTS = [
  { value: "now",    label: "Run Once Now",            icon: Play,      mode: null       },
  { value: "daily",  label: "Every Day at 9:00 AM",    icon: Clock,     mode: "daily"    },
  { value: "every6", label: "Every 6 Hours",            icon: RefreshCw, mode: "interval" },
  { value: "weekly", label: "Every Monday at 8:00 AM", icon: Settings,  mode: "weekly"   },
];

const DEMO_LOGS = [
  "[INFO]  Starting WebsiteLeadJob…",
  "[INFO]  Query 1/8: 'small business no website'",
  "[INFO]  Found 5 results, crawling pages…",
  "[INFO]  ✓ Lead: Al-Noor Dental Clinic (score=0.91) → High Priority",
  "[INFO]  Query 2/8: 'local restaurant facebook only no website'",
  "[INFO]  ✓ Lead: Spice Route Restaurant (score=0.83) → High Priority",
  "[INFO]  Starting WhatsAppBotLeadJob…",
  "[INFO]  ✓ Lead: City Physio Center (score=0.82) → High Priority",
  "[INFO]  Starting SEOLeadJob…",
  "[INFO]  ✓ Lead: Karachi Law Associates (score=0.79) → High Priority",
  "[INFO]  Running business filter…",
  "[INFO]  Hassan Chai Stall (score=0.22) → DISCARDED (street food stall)",
  "[INFO]  Qualifying 4 leads, composing outreach…",
  "[SUCCESS] Run complete — 4 qualified leads (4 high, 0 medium, 1 discarded)",
];

function JobCard({ job, selected, onToggle }) {
  return (
    <motion.button onClick={onToggle} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
      className={`w-full text-left bg-[#1a1a1a] rounded-2xl p-5 border transition-all duration-300 ${
        selected ? `${job.border} shadow-lg` : "border-white/6 hover:border-white/10"
      }`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className={`w-10 h-10 rounded-xl ${job.iconBg} flex items-center justify-center shrink-0`}>
            <job.icon className="w-5 h-5 text-black" strokeWidth={2} />
          </div>
          <div>
            <p className="font-semibold text-white text-sm">{job.label}</p>
            <p className="text-zinc-500 text-xs mt-0.5">{job.desc}</p>
          </div>
        </div>
        <div className={`w-5 h-5 rounded-md border flex items-center justify-center shrink-0 mt-0.5 transition-all ${
          selected ? "bg-orange-500 border-orange-500" : "border-white/15 bg-white/4"
        }`}>
          {selected && <CheckCircle className="w-3.5 h-3.5 text-black fill-black" />}
        </div>
      </div>
    </motion.button>
  );
}

function LogTerminal({ lines, running }) {
  const bottomRef = useRef(null);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [lines]);

  const color = (line) => {
    if (line.includes("[SUCCESS]") || line.includes("✓")) return "text-orange-400";
    if (line.includes("[ERROR]") || line.includes("FAIL"))  return "text-red-400";
    if (line.includes("DISCARD") || line.includes("[WARN]")) return "text-zinc-400";
    return "text-zinc-500";
  };

  return (
    <div className="bg-black rounded-xl border border-white/6 p-4 font-mono text-xs h-64 overflow-y-auto">
      <div className="flex items-center gap-1.5 mb-3 pb-3 border-b border-white/5">
        <span className="w-3 h-3 rounded-full bg-red-500/60" />
        <span className="w-3 h-3 rounded-full bg-yellow-500/60" />
        <span className="w-3 h-3 rounded-full bg-green-500/60" />
        <span className="ml-2 text-zinc-700">leadbot — automation engine</span>
      </div>
      {lines.length === 0 && <p className="text-zinc-700">$ python main.py</p>}
      {lines.map((l, i) => <p key={i} className={color(l)}>{l}</p>)}
      {running && (
        <motion.p animate={{ opacity: [1, 0, 1] }} transition={{ duration: 1, repeat: Infinity }} className="text-orange-500">▋</motion.p>
      )}
      <div ref={bottomRef} />
    </div>
  );
}

export default function RunAutomation() {
  const [selected,   setSelected]   = useState(["website", "whatsapp_bot", "seo"]);
  const [schedule,   setSchedule]   = useState("now");
  const [minScore,   setMinScore]   = useState(0.5);
  const [keywords,   setKeywords]   = useState([]);
  const [keywordInput, setKeywordInput] = useState("");
  const [status,     setStatus]     = useState("idle");
  const [logLines,   setLogLines]   = useState([]);
  const [leadsFound, setLeadsFound] = useState(0);
  const [progress,   setProgress]   = useState(0);
  const [jobId,      setJobId]      = useState(null);
  const [jobError,   setJobError]   = useState(null);
  const [isLive,     setIsLive]     = useState(false);
  const [checking,   setChecking]   = useState(true);

  useEffect(() => {
    checkBackendHealth().then(ok => { setIsLive(ok); setChecking(false); });
  }, []);

  const toggle = id => setSelected(p => p.includes(id) ? p.filter(j => j !== id) : [...p, id]);

  const pendingKeywords = () => keywordInput.split(/[\n,]/).map(k => k.trim()).filter(Boolean);
  const addKeywords = () => {
    const additions = pendingKeywords();
    if (!additions.length) return;
    setKeywords(current => [...new Set([...current, ...additions])].slice(0, 10));
    setKeywordInput("");
  };
  const removeKeyword = keyword => setKeywords(current => current.filter(k => k !== keyword));

  const startReal = async () => {
    if (!selected.length) return;
    setStatus("running"); setLogLines(["[INFO] Connecting to backend…"]);
    setLeadsFound(0); setProgress(5); setJobError(null);

    const service = selected.length === 1 ? selected[0] : null;
    const runKeywords = [...new Set([...keywords, ...pendingKeywords()])].slice(0, 10);
    setKeywords(runKeywords);
    setKeywordInput("");
    const { data, error } = await runJob({ service, min_score: minScore, keywords: runKeywords });
    if (error) { setLogLines(p => [...p, `[ERROR] ${error}`]); setStatus("failed"); setJobError(error); return; }

    const jid = data.job_id;
    setJobId(jid);
    setLogLines(p => [...p, `[INFO] Job ${jid} queued`, "[INFO] Polling for updates…"]);

    try {
      const final = await pollJobUntilDone(jid, rec => {
        setProgress(rec.progress || 0);
        if (rec.log_lines?.length) setLogLines(rec.log_lines);
        if (rec.result?.qualified_leads !== undefined) setLeadsFound(rec.result.qualified_leads);
      });
      if (final.status === "done") {
        setStatus("done"); setProgress(100);
        setLeadsFound(final.result?.qualified_leads || 0);
        setLogLines(p => [...p, `[SUCCESS] ${final.result?.qualified_leads || 0} leads (${final.result?.high_priority || 0} high priority, ${final.result?.discarded || 0} discarded)`]);
      } else {
        setStatus("failed"); setJobError(final.error || "Job failed");
        setLogLines(p => [...p, `[ERROR] ${final.error}`]);
      }
    } catch (e) {
      const message = e.message || "Job status could not be retrieved";
      setStatus("failed");
      setJobError(message);
      setLogLines(p => [...p, `[ERROR] ${message}`]);
    }
  };

  const startDemo = async () => {
    setStatus("running"); setLogLines([]); setLeadsFound(0); setProgress(5);
    for (let i = 0; i < DEMO_LOGS.length; i++) {
      await new Promise(r => setTimeout(r, 300 + Math.random() * 350));
      setLogLines(p => [...p, DEMO_LOGS[i]]);
      setProgress(Math.round(((i + 1) / DEMO_LOGS.length) * 95));
      if (DEMO_LOGS[i].includes("✓")) setLeadsFound(n => n + 1);
    }
    setProgress(100); setStatus("done");
  };

  const handleRun = () => isLive ? startReal() : startDemo();

  const handleSchedule = async val => {
    setSchedule(val);
    if (val === "now" || !isLive) return;
    const opt = SCHEDULE_OPTS.find(o => o.value === val);
    if (!opt?.mode) return;
    const body = { mode: opt.mode, service: selected.length === 1 ? selected[0] : null, min_score: minScore };
    if (opt.mode === "daily")    { body.hour = 9;  body.minute = 0; }
    if (opt.mode === "interval") { body.hours = 6; }
    if (opt.mode === "weekly")   { body.day_of_week = "mon"; body.hour = 8; body.minute = 0; }
    const { error } = await scheduleJob(body);
    setLogLines(p => [...p, error ? `[WARN] Schedule error: ${error}` : `[INFO] Schedule set: ${opt.label}`]);
  };

  const reset = () => { setStatus("idle"); setLogLines([]); setLeadsFound(0); setProgress(0); setJobId(null); setJobError(null); };

  return (
    <div className="relative min-h-screen pt-24 pb-20 overflow-hidden bg-[#111]">
      <GlowOrb className="w-96 h-96 -top-20 -right-32 opacity-20" color="orange" />

      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-8">

        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-10">
          <div className="flex items-center gap-2 mb-1">
            <Zap className="w-6 h-6 text-orange-400" />
            <h1 className="font-display font-bold text-3xl text-white">Run Automation</h1>
          </div>
          <div className="flex items-center gap-3 mt-1">
            <p className="text-zinc-500 text-sm">Trigger lead generation jobs from the browser.</p>
            {!checking && (
              <span className={`flex items-center gap-1.5 text-xs px-3 py-1 rounded-full border font-medium ${
                isLive ? "bg-green-500/8 border-green-500/20 text-green-400" : "bg-orange-500/8 border-orange-500/20 text-orange-400"
              }`}>
                {isLive ? <Wifi className="w-3.5 h-3.5" /> : <WifiOff className="w-3.5 h-3.5" />}
                {isLive ? "Backend Online — Real Runs" : "Backend Offline — Demo Mode"}
              </span>
            )}
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">

          {/* Left */}
          <div className="lg:col-span-2 space-y-4">
            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }}
              className="bg-[#1a1a1a] rounded-2xl p-5 border border-white/6">
              <p className="text-xs text-zinc-500 uppercase tracking-wider font-semibold mb-4">Select Jobs</p>
              <div className="space-y-3">
                {JOBS.map(job => <JobCard key={job.id} job={job} selected={selected.includes(job.id)} onToggle={() => toggle(job.id)} />)}
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.15 }}
              className="bg-[#1a1a1a] rounded-2xl p-5 border border-white/6">
              <div className="flex items-center justify-between gap-3 mb-2">
                <p className="text-xs text-zinc-500 uppercase tracking-wider font-semibold">Business Search Keywords</p>
                <span className="text-xs text-zinc-600">Optional · up to 10</span>
              </div>
              <p className="text-zinc-600 text-xs mb-3">Add a business type, service, or location. These replace the default search terms for this run.</p>
              <div className="flex gap-2">
                <input
                  value={keywordInput}
                  onChange={e => setKeywordInput(e.target.value)}
                  onKeyDown={e => { if (e.key === "Enter") { e.preventDefault(); addKeywords(); } }}
                  placeholder="e.g. dental clinics in Mumbai"
                  maxLength={160}
                  className="min-w-0 flex-1 rounded-lg border border-white/10 bg-black px-3 py-2 text-sm text-white outline-none placeholder:text-zinc-700 focus:border-orange-500/60"
                />
                <button type="button" onClick={addKeywords} disabled={!keywordInput.trim()}
                  className="rounded-lg bg-orange-500 px-3 py-2 text-xs font-semibold text-black disabled:cursor-not-allowed disabled:opacity-40">
                  Add
                </button>
              </div>
              {keywords.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {keywords.map(keyword => (
                    <span key={keyword} className="inline-flex max-w-full items-center gap-1 rounded-full border border-orange-500/30 bg-orange-500/10 px-2.5 py-1 text-xs text-orange-200">
                      <span className="truncate">{keyword}</span>
                      <button type="button" onClick={() => removeKeyword(keyword)} aria-label={`Remove ${keyword}`} className="text-orange-300 hover:text-white">
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </motion.div>

            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.18 }}
              className="bg-[#1a1a1a] rounded-2xl p-5 border border-white/6">
              <p className="text-xs text-zinc-500 uppercase tracking-wider font-semibold mb-4">Schedule</p>
              <div className="space-y-2">
                {SCHEDULE_OPTS.map(({ value, label, icon: Icon }) => (
                  <button key={value} onClick={() => handleSchedule(value)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm transition-all text-left ${
                      schedule === value
                        ? "bg-orange-500/10 border border-orange-500/30 text-orange-300"
                        : "bg-white/3 border border-white/5 text-zinc-400 hover:text-zinc-200 hover:bg-white/5"
                    }`}>
                    <Icon className="w-4 h-4 shrink-0" /> {label}
                  </button>
                ))}
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}
              className="bg-[#1a1a1a] rounded-2xl p-5 border border-white/30">
              <div className="flex items-center justify-between mb-4">
                <p className="text-xs text-zinc-300 uppercase tracking-wider font-semibold">Min Score</p>
                <span className="font-bold text-orange-400 text-sm">{Math.round(minScore * 100)}%</span>
              </div>
              <input type="range" min={0.3} max={0.9} step={0.05} value={minScore}
                onChange={e => setMinScore(parseFloat(e.target.value))}
                className="w-full accent-orange-500 cursor-pointer h-2 rounded-lg appearance-none bg-gradient-to-r from-zinc-700 to-zinc-600" />
              <div className="flex justify-between text-xs text-zinc-600 mt-2">
                <span>30% (more leads)</span><span>90% (top only)</span>
              </div>
            </motion.div>
          </div>

          {/* Right */}
          <div className="lg:col-span-3 space-y-4">
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }}
              className="bg-[#1a1a1a] rounded-2xl p-6 border border-white/6">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                  <p className="font-semibold text-white mb-1">
                    {selected.length === 0 ? "Select at least one job" : `Run ${selected.length} job${selected.length > 1 ? "s" : ""}`}
                  </p>
                  <p className="text-zinc-600 text-sm">Min score {Math.round(minScore * 100)}% · Est. ~{selected.length * 3} min</p>
                </div>
                <div className="flex gap-3">
                  {(status === "done" || status === "failed") && (
                    <motion.button initial={{ scale: 0 }} animate={{ scale: 1 }} onClick={reset} className="btn-secondary text-sm py-2.5">
                      <RefreshCw className="w-4 h-4" /> Reset
                    </motion.button>
                  )}
                  <motion.button
                    onClick={status === "idle" || status === "failed" ? handleRun : undefined}
                    whileHover={status !== "running" ? { scale: 1.05 } : {}}
                    whileTap={status  !== "running" ? { scale: 0.97 } : {}}
                    disabled={status === "running" || selected.length === 0}
                    className={`btn-primary text-sm py-2.5 ${status === "running" ? "opacity-60 cursor-not-allowed" : ""}`}>
                    {status === "running"
                      ? <><svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="40" strokeDashoffset="10" /></svg> Running…</>
                      : status === "done"
                        ? <><CheckCircle className="w-4 h-4" /> Done</>
                        : <><Play className="w-4 h-4 fill-black" /> {isLive ? "Start Real Run" : "Start Demo"}</>
                    }
                  </motion.button>
                </div>
              </div>

              <AnimatePresence>
                {status === "running" && (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="mt-4">
                    <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                      <motion.div animate={{ width: `${progress}%` }} transition={{ duration: 0.5 }}
                        className="h-full bg-gradient-to-r from-orange-500 to-orange-300 rounded-full" />
                    </div>
                    <p className="text-xs text-zinc-600 mt-1 text-right">{progress}%</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            <AnimatePresence>
              {status !== "idle" && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="grid grid-cols-3 gap-3">
                  {[
                    { label: "Leads Found",  value: leadsFound,                                                   color: "text-orange-400" },
                    { label: "Jobs Active",  value: status === "running" ? selected.length : 0,                  color: "text-white"      },
                    { label: "Status",       value: status === "done" ? "Complete" : status === "failed" ? "Failed" : "Running",
                      color: status === "done" ? "text-green-400" : status === "failed" ? "text-red-400" : "text-orange-400" },
                  ].map(({ label, value, color }) => (
                    <div key={label} className="bg-[#1a1a1a] rounded-xl p-4 border border-white/6 text-center">
                      <p className={`font-bold text-xl ${color}`}>{value}</p>
                      <p className="text-zinc-600 text-xs mt-1">{label}</p>
                    </div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>

            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}
              className="bg-[#1a1a1a] rounded-2xl p-5 border border-white/6">
              <p className="text-xs text-zinc-500 uppercase tracking-wider font-semibold mb-4 flex items-center gap-2">
                <Terminal className="w-3.5 h-3.5 text-orange-400" /> Live Output
                {jobId && <span className="text-zinc-700 font-normal normal-case ml-auto">job: {jobId.slice(0,8)}…</span>}
              </p>
              <LogTerminal lines={logLines} running={status === "running"} />
            </motion.div>

            {jobError && status === "failed" && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                className="bg-red-500/5 border border-red-500/20 rounded-xl p-4 text-red-400 text-sm">
                <p className="font-medium mb-1">Job failed</p>
                <p className="text-red-400/70 text-xs">{jobError}</p>
              </motion.div>
            )}

            <AnimatePresence>
              {status === "done" && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                  className="bg-[#1a1a1a] rounded-2xl p-5 border border-orange-500/20 animated-border">
                  <div className="flex items-center justify-between flex-wrap gap-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center">
                        <CheckCircle className="w-5 h-5 text-orange-400" />
                      </div>
                      <div>
                        <p className="font-semibold text-white text-sm">{leadsFound} leads added to dashboard</p>
                        <p className="text-zinc-600 text-xs">Outreach drafts generated for each lead.</p>
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
