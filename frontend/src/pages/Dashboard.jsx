import { useState, useMemo, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard, Globe, MessageSquare, TrendingUp,
  Search, Filter, RefreshCw, Download, CheckCircle,
  Clock, Mail, Phone, ExternalLink, Zap, ChevronDown,
  Star, AlertCircle, Wifi, WifiOff,
} from "lucide-react";
import { mockLeads } from "../data/mockLeads";
import { fetchLeads, fetchLeadStats, updateLead } from "../api/leads";
import { checkBackendHealth } from "../api/client";
import GlowOrb from "../components/GlowOrb";

// ── helpers ──────────────────────────────────────────────────────────────────
const SERVICE_META = {
  website:      { label: "Website",      icon: Globe,          color: "text-brand-400",  bg: "bg-brand-500/15 border-brand-500/30",  dot: "bg-brand-400" },
  whatsapp_bot: { label: "WhatsApp Bot", icon: MessageSquare,  color: "text-neon",        bg: "bg-neon/10 border-neon/30",            dot: "bg-neon" },
  seo:          { label: "SEO",          icon: TrendingUp,     color: "text-purple-400", bg: "bg-purple-500/15 border-purple-500/30", dot: "bg-purple-400" },
};

function scoreColor(s) {
  if (s >= 0.8)  return "from-neon to-teal-400";
  if (s >= 0.65) return "from-brand-400 to-brand-600";
  return "from-orange-400 to-amber-500";
}

function scoreTier(s) {
  if (s >= 0.8)  return { label: "Hot",  icon: Zap,          cls: "text-neon  bg-neon/10  border-neon/30" };
  if (s >= 0.65) return { label: "Warm", icon: Star,         cls: "text-brand-400 bg-brand-500/10 border-brand-500/30" };
  return               { label: "Cold", icon: AlertCircle,   cls: "text-orange-400 bg-orange-500/10 border-orange-500/30" };
}

function timeAgo(iso) {
  const diff = Date.now() - new Date(iso).getTime();
  const h = Math.floor(diff / 3600000);
  if (h < 1)  return "< 1h ago";
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

// ── StatCard ─────────────────────────────────────────────────────────────────
function StatCard({ icon: Icon, label, value, sub, color, delay }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      className="glass rounded-2xl p-5 border border-white/5 hover:border-white/10 transition-all duration-300"
    >
      <div className="flex items-start justify-between mb-3">
        <div className={`w-10 h-10 rounded-xl ${color} flex items-center justify-center`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        <span className="text-slate-600 text-xs">{sub}</span>
      </div>
      <p className="font-display font-bold text-3xl text-white">{value}</p>
      <p className="text-slate-400 text-sm mt-1">{label}</p>
    </motion.div>
  );
}

// ── LeadCard ─────────────────────────────────────────────────────────────────
function LeadCard({ lead, index, onMarkSent }) {
  const [expanded, setExpanded] = useState(false);
  const [sending,  setSending]  = useState(false);
  const svc  = SERVICE_META[lead.service_needed] || SERVICE_META.website;
  const tier = scoreTier(lead.qualification_score);
  const TierIcon = tier.icon;

  const handleMarkSent = async (e) => {
    e.stopPropagation();
    setSending(true);
    await onMarkSent(lead.id);
    setSending(false);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.5 }}
      layout
      className="glass rounded-2xl border border-white/5 hover:border-white/10 transition-all duration-300 overflow-hidden"
    >
      {/* Header row */}
      <div className="p-5 cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3 min-w-0">
            <div className={`w-10 h-10 rounded-xl ${svc.bg} border flex items-center justify-center shrink-0 mt-0.5`}>
              <svc.icon className={`w-5 h-5 ${svc.color}`} />
            </div>
            <div className="min-w-0">
              <p className="font-semibold text-white truncate">{lead.business_name}</p>
              <div className="flex items-center gap-2 mt-1 flex-wrap">
                <span className={`badge ${svc.bg} border ${svc.color} text-xs`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${svc.dot}`} />
                  {svc.label}
                </span>
                <span className={`badge border text-xs ${tier.cls}`}>
                  <TierIcon className="w-3 h-3" />
                  {tier.label}
                </span>
                {lead.outreach_sent && (
                  <span className="badge bg-green-500/10 border border-green-500/30 text-green-400 text-xs">
                    <CheckCircle className="w-3 h-3" /> Sent
                  </span>
                )}
              </div>
            </div>
          </div>
          <div className="flex flex-col items-end gap-1 shrink-0">
            <span className={`font-bold text-lg bg-gradient-to-r ${scoreColor(lead.qualification_score)} bg-clip-text text-transparent`}>
              {Math.round(lead.qualification_score * 100)}%
            </span>
            <span className="text-slate-600 text-xs flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {lead.discovered_at ? timeAgo(lead.discovered_at) : "—"}
            </span>
            <motion.div animate={{ rotate: expanded ? 180 : 0 }} transition={{ duration: 0.2 }}>
              <ChevronDown className="w-4 h-4 text-slate-600" />
            </motion.div>
          </div>
        </div>
        {/* Score bar */}
        <div className="mt-4 h-1.5 bg-white/5 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${lead.qualification_score * 100}%` }}
            transition={{ delay: 0.3, duration: 1, ease: "easeOut" }}
            className={`h-full rounded-full bg-gradient-to-r ${scoreColor(lead.qualification_score)}`}
          />
        </div>
      </div>

      {/* Expanded detail */}
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
              {/* Pain points */}
              {lead.pain_points?.length > 0 && (
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-2">Pain Points</p>
                  <div className="flex flex-wrap gap-2">
                    {lead.pain_points.map((p) => (
                      <span key={p} className="text-xs bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg px-2.5 py-1">{p}</span>
                    ))}
                  </div>
                </div>
              )}
              {/* Contact */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {lead.contact_email?.length > 0 && (
                  <div className="flex items-center gap-2 text-sm">
                    <Mail className="w-4 h-4 text-brand-400 shrink-0" />
                    <span className="text-slate-300 truncate">{lead.contact_email[0]}</span>
                  </div>
                )}
                {lead.contact_phone?.length > 0 && (
                  <div className="flex items-center gap-2 text-sm">
                    <Phone className="w-4 h-4 text-neon shrink-0" />
                    <span className="text-slate-300">{lead.contact_phone[0]}</span>
                  </div>
                )}
                {lead.website && (
                  <a href={lead.website} target="_blank" rel="noopener noreferrer"
                    className="flex items-center gap-2 text-sm text-brand-400 hover:text-brand-300 transition-colors">
                    <ExternalLink className="w-4 h-4 shrink-0" />
                    <span className="truncate">{lead.website}</span>
                  </a>
                )}
              </div>
              {/* Notes */}
              {lead.notes && (
                <p className="text-xs text-slate-500 bg-white/3 rounded-lg px-3 py-2 border border-white/5">{lead.notes}</p>
              )}
              {/* Actions */}
              <div className="flex gap-2 flex-wrap pt-1">
                {!lead.outreach_sent && (
                  <motion.button
                    whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
                    onClick={handleMarkSent}
                    disabled={sending}
                    className="btn-primary text-xs py-2 px-4"
                  >
                    {sending
                      ? <><svg className="animate-spin w-3.5 h-3.5" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="40" strokeDashoffset="10" /></svg> Saving…</>
                      : <><CheckCircle className="w-3.5 h-3.5" /> Mark Outreach Sent</>
                    }
                  </motion.button>
                )}
                <button className="btn-secondary text-xs py-2 px-4">
                  <Mail className="w-3.5 h-3.5" /> Copy Email Draft
                </button>
                <button className="btn-secondary text-xs py-2 px-4">
                  <MessageSquare className="w-3.5 h-3.5" /> WhatsApp Draft
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// ── Main Dashboard ────────────────────────────────────────────────────────────
export default function Dashboard() {
  const [leads,         setLeads]         = useState([]);
  const [stats,         setStats]         = useState(null);
  const [loading,       setLoading]       = useState(true);
  const [isLive,        setIsLive]        = useState(false);   // backend reachable?
  const [search,        setSearch]        = useState("");
  const [filterService, setFilterService] = useState("all");
  const [filterTier,    setFilterTier]    = useState("all");
  const [isRefreshing,  setIsRefreshing]  = useState(false);
  const [apiError,      setApiError]      = useState(null);

  // ── Load data ──────────────────────────────────────────────────────────────
  const loadLeads = useCallback(async () => {
    setIsRefreshing(true);
    setApiError(null);

    // 1. Check if backend is up
    const healthy = await checkBackendHealth();
    setIsLive(healthy);

    if (healthy) {
      // 2a. Fetch real data from API
      const [leadsRes, statsRes] = await Promise.all([
        fetchLeads({ limit: 500 }),
        fetchLeadStats(),
      ]);

      if (leadsRes.error) {
        setApiError(leadsRes.error);
        setLeads(mockLeads);   // graceful fallback
      } else {
        setLeads(leadsRes.data || []);
      }

      if (!statsRes.error && statsRes.data) {
        setStats(statsRes.data);
      }
    } else {
      // 2b. Backend offline — use mock data with a notice
      setLeads(mockLeads);
      setApiError("Backend offline — showing demo data. Start the server to see real leads.");
    }

    setLoading(false);
    setIsRefreshing(false);
  }, []);

  useEffect(() => { loadLeads(); }, [loadLeads]);

  // ── Mark outreach sent ────────────────────────────────────────────────────
  const handleMarkSent = async (leadId) => {
    if (isLive) {
      const { data, error } = await updateLead(leadId, { outreach_sent: true });
      if (!error && data) {
        setLeads(prev => prev.map(l => l.id === leadId ? { ...l, outreach_sent: true } : l));
        return;
      }
    }
    // Offline fallback — optimistic update
    setLeads(prev => prev.map(l => l.id === leadId ? { ...l, outreach_sent: true } : l));
  };

  // ── Client-side filter ────────────────────────────────────────────────────
  const filtered = useMemo(() => {
    const tierOf = (s) => s >= 0.8 ? "hot" : s >= 0.65 ? "warm" : "cold";
    return leads
      .filter(l => {
        const matchSearch  = !search || l.business_name?.toLowerCase().includes(search.toLowerCase()) || l.contact_email?.some(e => e.toLowerCase().includes(search.toLowerCase()));
        const matchService = filterService === "all" || l.service_needed === filterService;
        const matchTier    = filterTier    === "all" || tierOf(l.qualification_score) === filterTier;
        return matchSearch && matchService && matchTier;
      })
      .sort((a, b) => b.qualification_score - a.qualification_score);
  }, [leads, search, filterService, filterTier]);

  // ── Stats derived from loaded leads ───────────────────────────────────────
  const displayStats = stats || {
    total:       leads.length,
    hot:         leads.filter(l => l.qualification_score >= 0.8).length,
    outreach_sent: leads.filter(l => l.outreach_sent).length,
    by_service:  leads.reduce((acc, l) => { acc[l.service_needed] = (acc[l.service_needed] || 0) + 1; return acc; }, {}),
  };

  // ── Export CSV ───────────────────────────────────────────────────────────
  const exportCSV = () => {
    const header = ["id","business_name","service_needed","qualification_score","contact_email","contact_phone","website","outreach_sent","discovered_at"];
    const rows = filtered.map(l => header.map(k => {
      const v = l[k];
      if (Array.isArray(v)) return `"${v.join("; ")}"`;
      if (typeof v === "string" && v.includes(",")) return `"${v}"`;
      return v ?? "";
    }).join(","));
    const csv = [header.join(","), ...rows].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href = url; a.download = "leads.csv"; a.click();
    URL.revokeObjectURL(url);
  };

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="relative min-h-screen pt-24 pb-20 overflow-hidden">
      <GlowOrb className="w-96 h-96 -top-20 -right-32 opacity-30" color="brand" />
      <GlowOrb className="w-80 h-80 bottom-20 -left-20 opacity-20" color="neon" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-8">

        {/* Page header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}
          className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-10"
        >
          <div>
            <div className="flex items-center gap-2 mb-1">
              <LayoutDashboard className="w-6 h-6 text-brand-400" />
              <h1 className="font-display font-bold text-3xl text-white">Lead Dashboard</h1>
            </div>
            <p className="text-slate-400 text-sm">
              {isLive
                ? "Live data from backend · sorted by qualification score"
                : "Demo data — start the backend to see real leads"}
            </p>
          </div>
          <div className="flex items-center gap-3">
            {/* Backend status pill */}
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium border ${isLive ? "bg-green-500/10 border-green-500/25 text-green-400" : "bg-orange-500/10 border-orange-500/25 text-orange-400"}`}>
              {isLive ? <Wifi className="w-3.5 h-3.5" /> : <WifiOff className="w-3.5 h-3.5" />}
              {isLive ? "Backend Online" : "Backend Offline"}
            </div>
            <motion.button onClick={loadLeads} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
              className="glass border border-white/10 rounded-xl px-4 py-2.5 text-sm text-slate-300 flex items-center gap-2 hover:border-white/20 transition-all">
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin text-brand-400" : ""}`} />
              Refresh
            </motion.button>
            <motion.button onClick={exportCSV} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="btn-primary text-sm py-2.5">
              <Download className="w-4 h-4" /> Export CSV
            </motion.button>
          </div>
        </motion.div>

        {/* API error banner */}
        <AnimatePresence>
          {apiError && (
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="mb-6 flex items-center gap-3 bg-orange-500/10 border border-orange-500/25 rounded-xl px-4 py-3 text-orange-300 text-sm">
              <WifiOff className="w-4 h-4 shrink-0" />
              {apiError}
              <a href="/run" className="ml-auto text-brand-400 hover:text-brand-300 whitespace-nowrap">Run a job →</a>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Stat cards */}
        {loading ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-8">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="glass rounded-2xl p-5 border border-white/5 h-28 animate-pulse bg-white/3" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-8">
            <StatCard icon={Zap}           label="Total Leads"    value={displayStats.total}                       sub="all time" color="bg-brand-500"    delay={0} />
            <StatCard icon={Star}          label="Hot Leads"      value={displayStats.hot}                         sub="≥80%"     color="bg-neon/70"     delay={0.05} />
            <StatCard icon={CheckCircle}   label="Outreach Sent"  value={displayStats.outreach_sent}               sub="drafted"  color="bg-green-600"   delay={0.1} />
            <StatCard icon={Globe}         label="Website"        value={displayStats.by_service?.website || 0}    sub="leads"    color="bg-brand-600"   delay={0.15} />
            <StatCard icon={MessageSquare} label="WhatsApp Bot"   value={displayStats.by_service?.whatsapp_bot||0} sub="leads"    color="bg-teal-600"    delay={0.2} />
            <StatCard icon={TrendingUp}    label="SEO"            value={displayStats.by_service?.seo || 0}        sub="leads"    color="bg-purple-600"  delay={0.25} />
          </div>
        )}

        {/* Filters */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          className="glass rounded-2xl p-4 border border-white/5 mb-6 flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-600" />
            <input value={search} onChange={e => setSearch(e.target.value)}
              placeholder="Search leads by name or email…"
              className="w-full bg-white/5 border border-white/10 rounded-xl pl-9 pr-4 py-2.5 text-white placeholder-slate-600 text-sm focus:outline-none focus:border-brand-500/60 transition-all" />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-600 shrink-0" />
            <select value={filterService} onChange={e => setFilterService(e.target.value)}
              className="bg-dark-700 border border-white/10 rounded-xl px-3 py-2.5 text-slate-300 text-sm focus:outline-none focus:border-brand-500/60 transition-all cursor-pointer">
              <option value="all">All Services</option>
              <option value="website">Website</option>
              <option value="whatsapp_bot">WhatsApp Bot</option>
              <option value="seo">SEO</option>
            </select>
          </div>
          <select value={filterTier} onChange={e => setFilterTier(e.target.value)}
            className="bg-dark-700 border border-white/10 rounded-xl px-3 py-2.5 text-slate-300 text-sm focus:outline-none focus:border-brand-500/60 transition-all cursor-pointer">
            <option value="all">All Tiers</option>
            <option value="hot">🔥 Hot ≥80%</option>
            <option value="warm">⭐ Warm 65–79%</option>
            <option value="cold">❄️ Cold &lt;65%</option>
          </select>
        </motion.div>

        {/* Results count */}
        <div className="flex items-center justify-between mb-4">
          <p className="text-slate-500 text-sm">
            Showing <span className="text-white font-semibold">{filtered.length}</span> of {leads.length} leads
          </p>
          <div className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${isLive ? "bg-green-400 animate-pulse" : "bg-orange-400"}`} />
            <span className="text-slate-500 text-xs">{isLive ? "Live · updates every refresh" : "Demo mode"}</span>
          </div>
        </div>

        {/* Lead cards */}
        <motion.div layout className="space-y-3">
          <AnimatePresence mode="popLayout">
            {loading ? (
              [...Array(4)].map((_, i) => (
                <div key={i} className="glass rounded-2xl border border-white/5 h-24 animate-pulse bg-white/3" />
              ))
            ) : filtered.length === 0 ? (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                className="glass rounded-2xl p-16 border border-white/5 text-center">
                <Search className="w-10 h-10 text-slate-700 mx-auto mb-3" />
                <p className="text-slate-400 font-medium">No leads match your filters</p>
                <p className="text-slate-600 text-sm mt-1">Try adjusting the search or filter criteria, or <a href="/run" className="text-brand-400">run a new job</a></p>
              </motion.div>
            ) : (
              filtered.map((lead, i) => (
                <LeadCard key={lead.id} lead={lead} index={i} onMarkSent={handleMarkSent} />
              ))
            )}
          </AnimatePresence>
        </motion.div>

      </div>
    </div>
  );
}
