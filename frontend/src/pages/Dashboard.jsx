import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard, Globe, MessageSquare, TrendingUp,
  Search, Filter, RefreshCw, Download, CheckCircle,
  Clock, Mail, Phone, ExternalLink, Zap, ChevronDown,
  Star, AlertCircle,
} from "lucide-react";
import { mockLeads } from "../data/mockLeads";
import GlowOrb from "../components/GlowOrb";

// ── helpers ──────────────────────────────────────────────────────────────────

const SERVICE_META = {
  website:      { label: "Website",      icon: Globe,          color: "text-brand-400",  bg: "bg-brand-500/15 border-brand-500/30",  dot: "bg-brand-400" },
  whatsapp_bot: { label: "WhatsApp Bot", icon: MessageSquare,  color: "text-neon",        bg: "bg-neon/10 border-neon/30",            dot: "bg-neon" },
  seo:          { label: "SEO",          icon: TrendingUp,     color: "text-purple-400", bg: "bg-purple-500/15 border-purple-500/30", dot: "bg-purple-400" },
};

function scoreColor(s) {
  if (s >= 0.8) return "from-neon to-teal-400";
  if (s >= 0.65) return "from-brand-400 to-brand-600";
  return "from-orange-400 to-amber-500";
}

function scoreTier(s) {
  if (s >= 0.8) return { label: "Hot",  icon: Zap,          cls: "text-neon  bg-neon/10  border-neon/30" };
  if (s >= 0.65) return { label: "Warm", icon: Star,         cls: "text-brand-400 bg-brand-500/10 border-brand-500/30" };
  return                 { label: "Cold", icon: AlertCircle, cls: "text-orange-400 bg-orange-500/10 border-orange-500/30" };
}

function timeAgo(iso) {
  const diff = Date.now() - new Date(iso).getTime();
  const h = Math.floor(diff / 3600000);
  if (h < 1) return "< 1h ago";
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

// ── sub-components ────────────────────────────────────────────────────────────

function StatCard({ icon: Icon, label, value, sub, color, delay }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      className="glass rounded-2xl p-5 border border-white/5 hover:border-white/10 transition-all duration-300 group"
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

function LeadCard({ lead, index }) {
  const [expanded, setExpanded] = useState(false);
  const svc = SERVICE_META[lead.service_needed];
  const tier = scoreTier(lead.qualification_score);
  const TierIcon = tier.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06, duration: 0.5 }}
      layout
      className="glass rounded-2xl border border-white/5 hover:border-white/10 transition-all duration-300 overflow-hidden group"
    >
      {/* Top bar */}
      <div
        className="p-5 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
        role="button"
        aria-expanded={expanded}
      >
        <div className="flex items-start justify-between gap-3">
          {/* Left */}
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

          {/* Right — score + time */}
          <div className="flex flex-col items-end gap-2 shrink-0">
            <div className="flex items-center gap-1.5">
              <span className={`font-bold text-lg bg-gradient-to-r ${scoreColor(lead.qualification_score)} bg-clip-text text-transparent`}>
                {Math.round(lead.qualification_score * 100)}%
              </span>
            </div>
            <span className="text-slate-600 text-xs flex items-center gap-1">
              <Clock className="w-3 h-3" /> {timeAgo(lead.discovered_at)}
            </span>
            <motion.div
              animate={{ rotate: expanded ? 180 : 0 }}
              transition={{ duration: 0.2 }}
            >
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
              {lead.pain_points.length > 0 && (
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-2">Pain Points</p>
                  <div className="flex flex-wrap gap-2">
                    {lead.pain_points.map((p) => (
                      <span key={p} className="text-xs bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg px-2.5 py-1">
                        {p}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Contact */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {lead.contact_email.length > 0 && (
                  <div className="flex items-center gap-2 text-sm">
                    <Mail className="w-4 h-4 text-brand-400 shrink-0" />
                    <span className="text-slate-300 truncate">{lead.contact_email[0]}</span>
                  </div>
                )}
                {lead.contact_phone.length > 0 && (
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
                <p className="text-xs text-slate-500 bg-white/3 rounded-lg px-3 py-2 border border-white/5">
                  {lead.notes}
                </p>
              )}

              {/* Action buttons */}
              <div className="flex gap-2 flex-wrap pt-1">
                <button className="btn-primary text-xs py-2 px-4">
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
  const [search, setSearch] = useState("");
  const [filterService, setFilterService] = useState("all");
  const [filterTier, setFilterTier] = useState("all");
  const [isRefreshing, setIsRefreshing] = useState(false);

  const filtered = useMemo(() => {
    return mockLeads
      .filter((l) => {
        const matchSearch =
          l.business_name.toLowerCase().includes(search.toLowerCase()) ||
          l.contact_email.some((e) => e.toLowerCase().includes(search.toLowerCase()));
        const matchService = filterService === "all" || l.service_needed === filterService;
        const matchTier =
          filterTier === "all" ||
          (filterTier === "hot"  && l.qualification_score >= 0.8) ||
          (filterTier === "warm" && l.qualification_score >= 0.65 && l.qualification_score < 0.8) ||
          (filterTier === "cold" && l.qualification_score < 0.65);
        return matchSearch && matchService && matchTier;
      })
      .sort((a, b) => b.qualification_score - a.qualification_score);
  }, [search, filterService, filterTier]);

  const stats = useMemo(() => ({
    total:   mockLeads.length,
    hot:     mockLeads.filter((l) => l.qualification_score >= 0.8).length,
    sent:    mockLeads.filter((l) => l.outreach_sent).length,
    website: mockLeads.filter((l) => l.service_needed === "website").length,
    whatsapp:mockLeads.filter((l) => l.service_needed === "whatsapp_bot").length,
    seo:     mockLeads.filter((l) => l.service_needed === "seo").length,
  }), []);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1500);
  };

  return (
    <div className="relative min-h-screen pt-24 pb-20 overflow-hidden">
      <GlowOrb className="w-96 h-96 -top-20 -right-32 opacity-30" color="brand" />
      <GlowOrb className="w-80 h-80 bottom-20 -left-20 opacity-20" color="neon" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-8">
        {/* Page header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-10"
        >
          <div>
            <div className="flex items-center gap-2 mb-1">
              <LayoutDashboard className="w-6 h-6 text-brand-400" />
              <h1 className="font-display font-bold text-3xl text-white">Lead Dashboard</h1>
            </div>
            <p className="text-slate-400 text-sm">
              Live feed of AI-discovered leads · sorted by qualification score
            </p>
          </div>
          <div className="flex items-center gap-3">
            <motion.button
              onClick={handleRefresh}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="glass border border-white/10 rounded-xl px-4 py-2.5 text-sm text-slate-300 flex items-center gap-2 hover:border-white/20 transition-all"
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin text-brand-400" : ""}`} />
              Refresh
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="btn-primary text-sm py-2.5"
            >
              <Download className="w-4 h-4" /> Export CSV
            </motion.button>
          </div>
        </motion.div>

        {/* Stat cards */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-8">
          <StatCard icon={Zap}          label="Total Leads"     value={stats.total}    sub="all time" color="bg-brand-500"    delay={0} />
          <StatCard icon={Star}         label="Hot Leads"       value={stats.hot}      sub="≥80%"     color="bg-neon/70"     delay={0.05} />
          <StatCard icon={CheckCircle}  label="Outreach Sent"   value={stats.sent}     sub="drafted"  color="bg-green-600"   delay={0.1} />
          <StatCard icon={Globe}        label="Website"         value={stats.website}  sub="leads"    color="bg-brand-600"   delay={0.15} />
          <StatCard icon={MessageSquare}label="WhatsApp Bot"    value={stats.whatsapp} sub="leads"    color="bg-teal-600"    delay={0.2} />
          <StatCard icon={TrendingUp}   label="SEO"             value={stats.seo}      sub="leads"    color="bg-purple-600"  delay={0.25} />
        </div>

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass rounded-2xl p-4 border border-white/5 mb-6 flex flex-col sm:flex-row gap-3"
        >
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-600" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search leads by name or email…"
              className="w-full bg-white/5 border border-white/10 rounded-xl pl-9 pr-4 py-2.5 text-white placeholder-slate-600 text-sm focus:outline-none focus:border-brand-500/60 transition-all"
            />
          </div>

          {/* Service filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-600 shrink-0" />
            <select
              value={filterService}
              onChange={(e) => setFilterService(e.target.value)}
              className="bg-dark-700 border border-white/10 rounded-xl px-3 py-2.5 text-slate-300 text-sm focus:outline-none focus:border-brand-500/60 transition-all cursor-pointer"
            >
              <option value="all">All Services</option>
              <option value="website">Website</option>
              <option value="whatsapp_bot">WhatsApp Bot</option>
              <option value="seo">SEO</option>
            </select>
          </div>

          {/* Tier filter */}
          <select
            value={filterTier}
            onChange={(e) => setFilterTier(e.target.value)}
            className="bg-dark-700 border border-white/10 rounded-xl px-3 py-2.5 text-slate-300 text-sm focus:outline-none focus:border-brand-500/60 transition-all cursor-pointer"
          >
            <option value="all">All Tiers</option>
            <option value="hot">🔥 Hot ≥80%</option>
            <option value="warm">⭐ Warm 65–79%</option>
            <option value="cold">❄️ Cold &lt;65%</option>
          </select>
        </motion.div>

        {/* Results count */}
        <div className="flex items-center justify-between mb-4">
          <p className="text-slate-500 text-sm">
            Showing <span className="text-white font-semibold">{filtered.length}</span> of {mockLeads.length} leads
          </p>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-neon animate-pulse" />
            <span className="text-slate-500 text-xs">Live · updates every 30s</span>
          </div>
        </div>

        {/* Lead cards */}
        <motion.div layout className="space-y-3">
          <AnimatePresence mode="popLayout">
            {filtered.length === 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="glass rounded-2xl p-16 border border-white/5 text-center"
              >
                <Search className="w-10 h-10 text-slate-700 mx-auto mb-3" />
                <p className="text-slate-400 font-medium">No leads match your filters</p>
                <p className="text-slate-600 text-sm mt-1">Try adjusting the search or filter criteria</p>
              </motion.div>
            ) : (
              filtered.map((lead, i) => (
                <LeadCard key={lead.id} lead={lead} index={i} />
              ))
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  );
}
