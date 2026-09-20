import { useState, useMemo, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard, Globe, MessageSquare, TrendingUp,
  Filter, RefreshCw, Download, CheckCircle,
  Clock, Mail, Phone, ExternalLink, Zap, ChevronDown,
  Star, AlertCircle, Wifi, WifiOff, Flame, ThumbsUp,
  XCircle, BarChart2, Shield, Info, Search,
} from "lucide-react";
import { mockLeads } from "../data/mockLeads";
import { fetchLeads, fetchLeadStats, updateLead } from "../api/leads";
import { checkBackendHealth } from "../api/client";
import GlowOrb from "../components/GlowOrb";
import SearchBar from "../components/SearchBar";

// ── Priority meta ─────────────────────────────────────────────────────────────
const PRIORITY_META = {
  high:       { label: "High Priority",  icon: Flame,     cls: "text-orange-400 bg-orange-500/10 border-orange-500/35", dot: "bg-orange-400",  bar: "from-orange-500 to-orange-300" },
  medium:     { label: "Medium Priority",icon: ThumbsUp,  cls: "text-white      bg-white/8       border-white/20",       dot: "bg-white",       bar: "from-white to-zinc-400"         },
  discard:    { label: "Discard",        icon: XCircle,   cls: "text-red-400    bg-red-500/8     border-red-500/25",     dot: "bg-red-400",     bar: "from-red-500 to-red-400"        },
  unfiltered: { label: "Not Evaluated",  icon: Info,      cls: "text-zinc-400   bg-white/4       border-white/8",        dot: "bg-zinc-500",    bar: "from-zinc-600 to-zinc-700"      },
};

// ── Service meta ──────────────────────────────────────────────────────────────
const SERVICE_META = {
  website:      { label: "Website",      icon: Globe,          color: "text-orange-400", bg: "bg-orange-500/10 border-orange-500/25", dot: "bg-orange-400" },
  whatsapp_bot: { label: "WhatsApp Bot", icon: MessageSquare,  color: "text-white",      bg: "bg-white/8       border-white/15",       dot: "bg-white"      },
  seo:          { label: "SEO",          icon: TrendingUp,     color: "text-orange-300", bg: "bg-orange-400/8  border-orange-400/20",  dot: "bg-orange-300" },
};

function scoreColor(s) {
  if (s >= 0.8)  return "from-orange-500 to-orange-300";
  if (s >= 0.65) return "from-white to-zinc-400";
  return "from-zinc-500 to-zinc-600";
}
function scoreTier(s) {
  if (s >= 0.8)  return { label: "Hot",  icon: Zap,         cls: "text-orange-400 bg-orange-500/10 border-orange-500/30" };
  if (s >= 0.65) return { label: "Warm", icon: Star,        cls: "text-white      bg-white/8       border-white/15"      };
  return               { label: "Cold", icon: AlertCircle,  cls: "text-zinc-400   bg-white/5       border-white/10"      };
}
function timeAgo(iso) {
  const diff = Date.now() - new Date(iso).getTime();
  const h = Math.floor(diff / 3600000);
  if (h < 1)  return "< 1h ago";
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

// ── Score bar ─────────────────────────────────────────────────────────────────
function ScoreBar({ label, value, max = 10 }) {
  if (value < 0) return null;
  const pct = Math.round((value / max) * 100);
  const grad = value >= 7 ? "from-orange-500 to-orange-300" : value >= 4 ? "from-white to-zinc-400" : "from-zinc-500 to-zinc-600";
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-zinc-500">{label}</span>
        <span className="text-zinc-300 font-medium">{value}/{max}</span>
      </div>
      <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className={`h-full rounded-full bg-gradient-to-r ${grad}`}
        />
      </div>
    </div>
  );
}

// ── Stat card ─────────────────────────────────────────────────────────────────
function StatCard({ icon: Icon, label, value, sub, accent, delay = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      className={`bg-[#1a1a1a] rounded-2xl p-5 border ${accent} hover:border-orange-500/30 transition-all duration-300`}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="w-9 h-9 rounded-xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center">
          <Icon className="w-4 h-4 text-orange-400" />
        </div>
        <span className="text-zinc-600 text-xs">{sub}</span>
      </div>
      <p className="font-display font-bold text-3xl text-white">{value}</p>
      <p className="text-zinc-500 text-sm mt-1">{label}</p>
    </motion.div>
  );
}

// ── Lead card ─────────────────────────────────────────────────────────────────
function LeadCard({ lead, index, onMarkSent }) {
  const [expanded, setExpanded] = useState(false);
  const [sending,  setSending]  = useState(false);

  const svc      = SERVICE_META[lead.service_needed] || SERVICE_META.website;
  const tier     = scoreTier(lead.qualification_score);
  const TierIcon = tier.icon;
  const priority = lead.filter_priority || "unfiltered";
  const pri      = PRIORITY_META[priority] || PRIORITY_META.unfiltered;
  const PriIcon  = pri.icon;
  const isDiscard = priority === "discard";

  const handleMarkSent = async (e) => {
    e.stopPropagation();
    setSending(true);
    await onMarkSent(lead.id);
    setSending(false);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04, duration: 0.45 }}
      layout
      className={`bg-[#1a1a1a] rounded-2xl border overflow-hidden transition-all duration-300 ${
        isDiscard ? "border-red-500/10 opacity-55" : "border-white/6 hover:border-orange-500/25"
      }`}
    >
      {/* Priority top bar */}
      <div className={`h-0.5 w-full bg-gradient-to-r ${pri.bar}`} />

      {/* Header */}
      <div className="p-5 cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <div className="flex items-start justify-between gap-3">
          {/* Left */}
          <div className="flex items-start gap-3 min-w-0">
            <div className={`w-10 h-10 rounded-xl ${svc.bg} border flex items-center justify-center shrink-0 mt-0.5`}>
              <svc.icon className={`w-5 h-5 ${svc.color}`} />
            </div>
            <div className="min-w-0">
              <p className="font-semibold text-white truncate">{lead.business_name}</p>
              <div className="flex items-center gap-1.5 mt-1.5 flex-wrap">
                <span className={`badge border text-xs ${pri.cls}`}>
                  <PriIcon className="w-3 h-3" /> {pri.label}
                </span>
                <span className={`badge ${svc.bg} border ${svc.color} text-xs`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${svc.dot}`} /> {svc.label}
                </span>
                <span className={`badge border text-xs ${tier.cls}`}>
                  <TierIcon className="w-3 h-3" /> {tier.label}
                </span>
                {lead.outreach_sent && (
                  <span className="badge bg-orange-500/10 border border-orange-500/25 text-orange-400 text-xs">
                    <CheckCircle className="w-3 h-3" /> Sent
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Right */}
          <div className="flex flex-col items-end gap-1 shrink-0">
            <span className={`font-bold text-lg bg-gradient-to-r ${scoreColor(lead.qualification_score)} bg-clip-text text-transparent`}>
              {Math.round(lead.qualification_score * 100)}%
            </span>
            <span className="text-zinc-600 text-xs flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {lead.discovered_at ? timeAgo(lead.discovered_at) : "—"}
            </span>
            <motion.div animate={{ rotate: expanded ? 180 : 0 }} transition={{ duration: 0.2 }}>
              <ChevronDown className="w-4 h-4 text-zinc-600" />
            </motion.div>
          </div>
        </div>

        {/* Score bar */}
        <div className="mt-4 h-1 bg-white/5 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${lead.qualification_score * 100}%` }}
            transition={{ delay: 0.3, duration: 0.9, ease: "easeOut" }}
            className={`h-full rounded-full bg-gradient-to-r ${scoreColor(lead.qualification_score)}`}
          />
        </div>

        {/* Justification preview */}
        {lead.filter_justification && (
          <p className="mt-2.5 text-xs text-zinc-600 line-clamp-1">
            <span className="text-zinc-500 font-medium">Filter: </span>
            {lead.filter_justification}
          </p>
        )}
      </div>

      {/* Expanded */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 border-t border-white/5 pt-4 space-y-4">

              {/* Filter scores */}
              {(lead.filter_online_score >= 0 || lead.filter_suitability_score >= 0) && (
                <div className="space-y-2.5">
                  <p className="text-xs text-zinc-500 uppercase tracking-wider font-semibold flex items-center gap-1.5">
                    <BarChart2 className="w-3.5 h-3.5 text-orange-400" /> Filter Scores
                  </p>
                  <ScoreBar label="Online Presence" value={lead.filter_online_score} />
                  <ScoreBar label="Digital Suitability" value={lead.filter_suitability_score} />
                </div>
              )}

              {/* Filter reasoning */}
              {lead.filter_reasoning && (
                <div>
                  <p className="text-xs text-zinc-500 uppercase tracking-wider font-semibold mb-1.5 flex items-center gap-1.5">
                    <Shield className="w-3.5 h-3.5 text-orange-400" /> Reasoning
                  </p>
                  <p className="text-sm text-zinc-400 leading-relaxed bg-white/3 rounded-xl px-3 py-2.5 border border-white/5">
                    {lead.filter_reasoning}
                  </p>
                </div>
              )}

              {/* Recommended services */}
              {lead.filter_recommended?.length > 0 && (
                <div>
                  <p className="text-xs text-zinc-500 uppercase tracking-wider font-semibold mb-2">Recommended</p>
                  <div className="flex flex-wrap gap-2">
                    {lead.filter_recommended.map(s => {
                      const m = SERVICE_META[s]; if (!m) return null;
                      return (
                        <span key={s} className={`badge ${m.bg} border ${m.color} text-xs`}>
                          <m.icon className="w-3 h-3" /> {m.label}
                        </span>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Pain points */}
              {lead.pain_points?.length > 0 && (
                <div>
                  <p className="text-xs text-zinc-500 uppercase tracking-wider font-semibold mb-2">Pain Points</p>
                  <div className="flex flex-wrap gap-2">
                    {lead.pain_points.map(p => (
                      <span key={p} className="text-xs bg-red-500/8 border border-red-500/15 text-red-400 rounded-lg px-2.5 py-1">{p}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Contact */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {lead.contact_email?.length > 0 && (
                  <div className="flex items-center gap-2 text-sm">
                    <Mail className="w-4 h-4 text-orange-400 shrink-0" />
                    <span className="text-zinc-300 truncate">{lead.contact_email[0]}</span>
                  </div>
                )}
                {lead.contact_phone?.length > 0 && (
                  <div className="flex items-center gap-2 text-sm">
                    <Phone className="w-4 h-4 text-white shrink-0" />
                    <span className="text-zinc-300">{lead.contact_phone[0]}</span>
                  </div>
                )}
                {lead.website && (
                  <a href={lead.website} target="_blank" rel="noopener noreferrer"
                    className="flex items-center gap-2 text-sm text-orange-400 hover:text-orange-300 transition-colors">
                    <ExternalLink className="w-4 h-4 shrink-0" />
                    <span className="truncate">{lead.website}</span>
                  </a>
                )}
              </div>

              {lead.notes && (
                <p className="text-xs text-zinc-600 bg-white/3 rounded-lg px-3 py-2 border border-white/5">{lead.notes}</p>
              )}

              {!isDiscard && (
                <div className="flex gap-2 flex-wrap pt-1">
                  {!lead.outreach_sent && (
                    <motion.button whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
                      onClick={handleMarkSent} disabled={sending} className="btn-primary text-xs py-2 px-4">
                      {sending
                        ? <><svg className="animate-spin w-3.5 h-3.5" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="40" strokeDashoffset="10" /></svg> Saving…</>
                        : <><CheckCircle className="w-3.5 h-3.5" /> Mark Sent</>}
                    </motion.button>
                  )}
                  <button className="btn-secondary text-xs py-2 px-4">
                    <Mail className="w-3.5 h-3.5" /> Email Draft
                  </button>
                  <button className="btn-secondary text-xs py-2 px-4">
                    <MessageSquare className="w-3.5 h-3.5" /> WhatsApp Draft
                  </button>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// ── Main ──────────────────────────────────────────────────────────────────────
export default function Dashboard() {
  const [leads,          setLeads]          = useState([]);
  const [stats,          setStats]          = useState(null);
  const [loading,        setLoading]        = useState(true);
  const [isLive,         setIsLive]         = useState(false);
  const [search,         setSearch]         = useState("");
  const [filterService,  setFilterService]  = useState("all");
  const [filterTier,     setFilterTier]     = useState("all");
  const [filterPriority, setFilterPriority] = useState("all");
  const [showDiscard,    setShowDiscard]    = useState(false);
  const [isRefreshing,   setIsRefreshing]   = useState(false);
  const [apiError,       setApiError]       = useState(null);

  const loadLeads = useCallback(async () => {
    setIsRefreshing(true);
    setApiError(null);
    const healthy = await checkBackendHealth();
    setIsLive(healthy);
    if (healthy) {
      const [leadsRes, statsRes] = await Promise.all([fetchLeads({ limit: 500 }), fetchLeadStats()]);
      if (leadsRes.error) { setApiError(leadsRes.error); setLeads(mockLeads); }
      else                setLeads(leadsRes.data || []);
      if (!statsRes.error && statsRes.data) setStats(statsRes.data);
    } else {
      setLeads(mockLeads);
      setApiError("Backend offline — showing demo data. Run: cd backend && python main.py");
    }
    setLoading(false);
    setIsRefreshing(false);
  }, []);

  useEffect(() => { loadLeads(); }, [loadLeads]);

  const handleMarkSent = async (id) => {
    if (isLive) {
      const { data, error } = await updateLead(id, { outreach_sent: true });
      if (!error && data) { setLeads(prev => prev.map(l => l.id === id ? { ...l, outreach_sent: true } : l)); return; }
    }
    setLeads(prev => prev.map(l => l.id === id ? { ...l, outreach_sent: true } : l));
  };

  const filtered = useMemo(() => {
    const tierOf = s => s >= 0.8 ? "hot" : s >= 0.65 ? "warm" : "cold";
    return leads
      .filter(l => {
        const pri = l.filter_priority || "unfiltered";
        if (pri === "discard" && !showDiscard) return false;
        const ms = !search || l.business_name?.toLowerCase().includes(search.toLowerCase()) || l.contact_email?.some(e => e.toLowerCase().includes(search.toLowerCase()));
        const sv = filterService  === "all" || l.service_needed === filterService;
        const tr = filterTier     === "all" || tierOf(l.qualification_score) === filterTier;
        const pr = filterPriority === "all" || pri === filterPriority;
        return ms && sv && tr && pr;
      })
      .sort((a, b) => {
        const o = { high: 0, medium: 1, unfiltered: 2, discard: 3 };
        const d = (o[a.filter_priority || "unfiltered"] ?? 2) - (o[b.filter_priority || "unfiltered"] ?? 2);
        return d !== 0 ? d : b.qualification_score - a.qualification_score;
      });
  }, [leads, search, filterService, filterTier, filterPriority, showDiscard]);

  const ds = stats || {
    total: leads.length,
    hot: leads.filter(l => l.qualification_score >= 0.8).length,
    outreach_sent: leads.filter(l => l.outreach_sent).length,
    by_service: leads.reduce((a, l) => { a[l.service_needed] = (a[l.service_needed] || 0) + 1; return a; }, {}),
    by_priority: leads.reduce((a, l) => { const p = l.filter_priority || "unfiltered"; a[p] = (a[p] || 0) + 1; return a; }, {}),
  };

  const exportCSV = () => {
    const cols = ["id","business_name","service_needed","filter_priority","qualification_score","contact_email","website","outreach_sent"];
    const rows = filtered.map(l => cols.map(k => { const v = l[k]; if (Array.isArray(v)) return `"${v.join("; ")}"`;  if (typeof v === "string" && v.includes(",")) return `"${v}"`; return v ?? ""; }).join(","));
    const blob = new Blob([[cols.join(","), ...rows].join("\n")], { type: "text/csv" });
    const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(blob), download: "leads.csv" });
    a.click(); URL.revokeObjectURL(a.href);
  };

  return (
    <div className="relative min-h-screen pt-24 pb-20 overflow-hidden bg-[#111]">
      <GlowOrb className="w-96 h-96 -top-20 -right-32 opacity-20" color="orange" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-8">

        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}
          className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-10">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <LayoutDashboard className="w-6 h-6 text-orange-400" />
              <h1 className="font-display font-bold text-3xl text-white">Lead Dashboard</h1>
            </div>
            <p className="text-zinc-500 text-sm">
              {isLive ? "Live data from backend · AI-filtered by business model" : "Demo data — start the backend for real leads"}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium border ${isLive ? "bg-green-500/8 border-green-500/20 text-green-400" : "bg-orange-500/8 border-orange-500/20 text-orange-400"}`}>
              {isLive ? <Wifi className="w-3.5 h-3.5" /> : <WifiOff className="w-3.5 h-3.5" />}
              {isLive ? "Backend Online" : "Backend Offline"}
            </div>
            <motion.button onClick={loadLeads} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
              className="bg-white/5 border border-white/8 rounded-xl px-4 py-2.5 text-sm text-zinc-300 flex items-center gap-2 hover:border-white/15 transition-all">
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin text-orange-400" : ""}`} /> Refresh
            </motion.button>
            <motion.button onClick={exportCSV} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="btn-primary text-sm py-2.5">
              <Download className="w-4 h-4" /> Export CSV
            </motion.button>
          </div>
        </motion.div>

        {/* Error banner */}
        <AnimatePresence>
          {apiError && (
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="mb-6 flex items-center gap-3 bg-orange-500/8 border border-orange-500/20 rounded-xl px-4 py-3 text-orange-300 text-sm">
              <WifiOff className="w-4 h-4 shrink-0" /> {apiError}
              <a href="/run" className="ml-auto text-orange-400 hover:text-orange-300 whitespace-nowrap">Run a job →</a>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Stat cards */}
        {!loading && (
          <>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-3">
              <StatCard icon={Zap}           label="Total Leads"   value={ds.total}                       sub="all time" accent="border-orange-500/20" delay={0}    />
              <StatCard icon={Star}          label="Hot Leads"     value={ds.hot}                         sub="≥80%"     accent="border-white/8"       delay={0.05} />
              <StatCard icon={CheckCircle}   label="Sent"          value={ds.outreach_sent}               sub="outreach" accent="border-white/8"       delay={0.1}  />
              <StatCard icon={Globe}         label="Website"       value={ds.by_service?.website      ||0} sub="leads"   accent="border-white/8"       delay={0.15} />
              <StatCard icon={MessageSquare} label="WhatsApp Bot"  value={ds.by_service?.whatsapp_bot ||0} sub="leads"   accent="border-white/8"       delay={0.2}  />
              <StatCard icon={TrendingUp}    label="SEO"           value={ds.by_service?.seo          ||0} sub="leads"   accent="border-white/8"       delay={0.25} />
            </div>
            {/* Priority row */}
            <div className="grid grid-cols-3 gap-3 mb-8">
              {[
                { icon: Flame,    label: "High Priority",   value: ds.by_priority?.high    || 0, cls: "border-orange-500/20 bg-orange-500/5" },
                { icon: ThumbsUp, label: "Medium Priority", value: ds.by_priority?.medium  || 0, cls: "border-white/8       bg-white/3"       },
                { icon: XCircle,  label: "Discarded",       value: ds.by_priority?.discard || 0, cls: "border-red-500/15    bg-red-500/3"     },
              ].map(({ icon: Icon, label, value, cls }) => (
                <motion.div key={label}
                  initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                  className={`rounded-2xl p-4 border ${cls} flex items-center gap-3`}>
                  <Icon className="w-5 h-5 text-orange-400" />
                  <div>
                    <p className="font-bold text-2xl text-white">{value}</p>
                    <p className="text-xs text-zinc-500">{label}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </>
        )}

        {/* Filters */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          className="bg-[#1a1a1a] border border-white/6 rounded-2xl p-4 mb-6 flex flex-col sm:flex-row gap-3">
          <SearchBar
            value={search}
            onChange={e => setSearch(e.target.value)}
            onClear={() => setSearch("")}
            placeholder="Search by name or email…"
            className="flex-1"
          />
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-zinc-600 shrink-0" />
            <select value={filterPriority} onChange={e => setFilterPriority(e.target.value)}
              className="bg-[#222] border border-white/8 rounded-xl px-3 py-2.5 text-zinc-300 text-sm focus:outline-none focus:border-orange-500/40 cursor-pointer">
              <option value="all">All Priorities</option>
              <option value="high">🔥 High</option>
              <option value="medium">👍 Medium</option>
              <option value="unfiltered">⬜ Not Evaluated</option>
            </select>
          </div>
          <select value={filterService} onChange={e => setFilterService(e.target.value)}
            className="bg-[#222] border border-white/8 rounded-xl px-3 py-2.5 text-zinc-300 text-sm focus:outline-none focus:border-orange-500/40 cursor-pointer">
            <option value="all">All Services</option>
            <option value="website">Website</option>
            <option value="whatsapp_bot">WhatsApp Bot</option>
            <option value="seo">SEO</option>
          </select>
          <select value={filterTier} onChange={e => setFilterTier(e.target.value)}
            className="bg-[#222] border border-white/8 rounded-xl px-3 py-2.5 text-zinc-300 text-sm focus:outline-none focus:border-orange-500/40 cursor-pointer">
            <option value="all">All Tiers</option>
            <option value="hot">🔥 Hot ≥80%</option>
            <option value="warm">⭐ Warm</option>
            <option value="cold">❄️ Cold</option>
          </select>
        </motion.div>

        {/* Results bar */}
        <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
          <p className="text-zinc-600 text-sm">
            Showing <span className="text-white font-semibold">{filtered.length}</span> of {leads.length} leads
          </p>
          <div className="flex items-center gap-4">
            <button onClick={() => setShowDiscard(v => !v)}
              className={`flex items-center gap-2 text-xs px-3 py-1.5 rounded-lg border transition-all ${showDiscard ? "bg-red-500/8 border-red-500/25 text-red-400" : "bg-white/4 border-white/8 text-zinc-500 hover:text-zinc-300"}`}>
              <XCircle className="w-3.5 h-3.5" />
              {showDiscard ? "Hiding" : "Show"} discarded ({ds.by_priority?.discard || 0})
            </button>
            <div className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${isLive ? "bg-green-400 animate-pulse" : "bg-orange-400"}`} />
              <span className="text-zinc-600 text-xs">{isLive ? "Live" : "Demo"}</span>
            </div>
          </div>
        </div>

        {/* Lead cards */}
        <motion.div layout className="space-y-3">
          <AnimatePresence mode="popLayout">
            {loading
              ? [...Array(4)].map((_, i) => <div key={i} className="bg-[#1a1a1a] rounded-2xl border border-white/5 h-24 animate-pulse" />)
              : filtered.length === 0
                ? (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    className="bg-[#1a1a1a] rounded-2xl p-16 border border-white/5 text-center">
                    <Search className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
                    <p className="text-zinc-400 font-medium">No leads match your filters</p>
                    <p className="text-zinc-600 text-sm mt-1">
                      Try different filters or <a href="/run" className="text-orange-400">run a new job</a>
                    </p>
                  </motion.div>
                )
                : filtered.map((lead, i) => (
                  <LeadCard key={lead.id} lead={lead} index={i} onMarkSent={handleMarkSent} />
                ))
            }
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  );
}
