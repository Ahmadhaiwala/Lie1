import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  BarChart2, TrendingUp, Globe, MessageSquare,
  Zap, CheckCircle, Flame, ThumbsUp, XCircle,
  RefreshCw, Wifi, WifiOff, Users, Target,
  ArrowUpRight, ArrowDownRight, Clock,
} from "lucide-react";
import { fetchLeads, fetchLeadStats } from "../api/leads";
import { checkBackendHealth } from "../api/client";
import { mockLeads } from "../data/mockLeads";
import GlowOrb from "../components/GlowOrb";
import Mascot from "../components/Mascot";

// ── helpers ───────────────────────────────────────────────────────────────────
function pct(part, total) {
  if (!total) return 0;
  return Math.round((part / total) * 100);
}

// ── Bar chart (pure CSS) ──────────────────────────────────────────────────────
function BarRow({ label, value, max, color = "bg-orange-500", textColor = "text-orange-400" }) {
  const width = max ? pct(value, max) : 0;
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-zinc-300 font-medium">{label}</span>
        <span className={`font-bold ${textColor}`}>{value}</span>
      </div>
      <div className="h-2.5 bg-white/5 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${width}%` }}
          transition={{ duration: 0.9, ease: "easeOut" }}
          className={`h-full rounded-full ${color}`}
        />
      </div>
    </div>
  );
}

// ── Donut chart (SVG) ─────────────────────────────────────────────────────────
function Donut({ segments, size = 120, stroke = 18 }) {
  const r   = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const cx = cy = size / 2;

  const colors = ["#f97316", "#ffffff", "#6b7280", "#374151"];
  let offset = 0;

  const total = segments.reduce((s, seg) => s + seg.value, 0) || 1;

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="#1a1a1a" strokeWidth={stroke} />
      {segments.map((seg, i) => {
        const dash    = (seg.value / total) * circ;
        const gap     = circ - dash;
        const el = (
          <circle
            key={i}
            cx={cx} cy={cy} r={r}
            fill="none"
            stroke={colors[i % colors.length]}
            strokeWidth={stroke}
            strokeDasharray={`${dash} ${gap}`}
            strokeDashoffset={-offset * (circ / total)}
            transform={`rotate(-90 ${cx} ${cy})`}
            strokeLinecap="butt"
          />
        );
        offset += seg.value;
        return el;
      })}
      {/* Centre text */}
      <text x="50%" y="50%" textAnchor="middle" dy="0.35em"
        fontSize={size * 0.18} fontWeight="bold" fill="#ffffff">
        {total}
      </text>
    </svg>
  );
}

// ── KPI card ──────────────────────────────────────────────────────────────────
function KPICard({ icon: Icon, label, value, sub, trend, accent = "border-white/8", delay = 0 }) {
  const trendUp = trend > 0;
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      className={`bg-[#1a1a1a] rounded-2xl p-5 border ${accent} hover:border-orange-500/25 transition-all duration-300`}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="w-10 h-10 rounded-xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center">
          <Icon className="w-5 h-5 text-orange-400" />
        </div>
        {trend !== undefined && (
          <span className={`flex items-center gap-1 text-xs font-semibold ${trendUp ? "text-green-400" : "text-red-400"}`}>
            {trendUp ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
            {Math.abs(trend)}%
          </span>
        )}
      </div>
      <p className="font-display font-bold text-3xl text-white">{value}</p>
      <p className="text-zinc-400 text-sm mt-1 font-medium">{label}</p>
      {sub && <p className="text-zinc-600 text-xs mt-0.5">{sub}</p>}
    </motion.div>
  );
}

// ── Section wrapper ───────────────────────────────────────────────────────────
function Section({ title, icon: Icon, children, delay = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.6 }}
      className="bg-[#1a1a1a] rounded-2xl border border-white/6 overflow-hidden"
    >
      <div className="flex items-center gap-2.5 px-6 py-4 border-b border-white/6">
        <Icon className="w-5 h-5 text-orange-400" />
        <h3 className="font-display font-semibold text-white">{title}</h3>
      </div>
      <div className="p-6">{children}</div>
    </motion.div>
  );
}

// ── Recent lead row ───────────────────────────────────────────────────────────
function RecentLeadRow({ lead, index }) {
  const pri = lead.filter_priority || "unfiltered";
  const priColor = pri === "high" ? "text-orange-400" : pri === "medium" ? "text-white" : "text-zinc-500";
  const svcIcon  = { website: Globe, whatsapp_bot: MessageSquare, seo: TrendingUp }[lead.service_needed] || Globe;
  const SvcIcon  = svcIcon;

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      className="flex items-center gap-3 py-3 border-b border-white/4 last:border-0 hover:bg-white/2 rounded-lg px-2 transition-all"
    >
      <div className="w-8 h-8 rounded-lg bg-orange-500/10 border border-orange-500/15 flex items-center justify-center shrink-0">
        <SvcIcon className="w-4 h-4 text-orange-400" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-white text-sm font-medium truncate">{lead.business_name}</p>
        <p className="text-zinc-500 text-xs truncate">
          {lead.contact_email?.[0] || lead.contact_phone?.[0] || "No contact"}
        </p>
      </div>
      <div className="text-right shrink-0">
        <p className={`text-xs font-semibold ${priColor} capitalize`}>{pri}</p>
        <p className="text-zinc-600 text-xs">{Math.round((lead.qualification_score || 0) * 100)}%</p>
      </div>
      {lead.outreach_sent && (
        <CheckCircle className="w-4 h-4 text-green-400 shrink-0" />
      )}
    </motion.div>
  );
}

// ── Main Analytics Page ───────────────────────────────────────────────────────
export default function Analytics() {
  const [leads,        setLeads]        = useState([]);
  const [stats,        setStats]        = useState(null);
  const [loading,      setLoading]      = useState(true);
  const [isLive,       setIsLive]       = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const load = useCallback(async () => {
    setIsRefreshing(true);
    const healthy = await checkBackendHealth();
    setIsLive(healthy);

    if (healthy) {
      const [lr, sr] = await Promise.all([fetchLeads({ limit: 500 }), fetchLeadStats()]);
      if (!lr.error) setLeads(lr.data || []);
      else           setLeads(mockLeads);
      if (!sr.error) setStats(sr.data);
    } else {
      setLeads(mockLeads);
    }
    setLoading(false);
    setIsRefreshing(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  // Derived analytics from leads list
  const total     = leads.length;
  const st        = stats || {
    total,
    hot:           leads.filter(l => l.qualification_score >= 0.8).length,
    warm:          leads.filter(l => l.qualification_score >= 0.65 && l.qualification_score < 0.8).length,
    cold:          leads.filter(l => l.qualification_score < 0.65).length,
    outreach_sent: leads.filter(l => l.outreach_sent).length,
    by_service:    leads.reduce((a, l) => { a[l.service_needed] = (a[l.service_needed]||0)+1; return a; }, {}),
    by_priority:   leads.reduce((a, l) => { const p = l.filter_priority||"unfiltered"; a[p]=(a[p]||0)+1; return a; }, {}),
    avg_online_score:     null,
    avg_suitability:      null,
    evaluated_count:      leads.filter(l => (l.filter_online_score||0) >= 0).length,
  };

  const high      = st.by_priority?.high    || 0;
  const medium    = st.by_priority?.medium  || 0;
  const discard   = st.by_priority?.discard || 0;
  const website   = st.by_service?.website      || 0;
  const whatsapp  = st.by_service?.whatsapp_bot || 0;
  const seo       = st.by_service?.seo          || 0;
  const sent      = st.outreach_sent            || 0;

  const convRate  = total ? pct(high + medium, total) : 0;
  const sentRate  = (high + medium) ? pct(sent, high + medium) : 0;

  const recentLeads = [...leads]
    .sort((a, b) => new Date(b.discovered_at||0) - new Date(a.discovered_at||0))
    .slice(0, 8);

  return (
    <div className="relative min-h-screen pt-24 pb-20 overflow-hidden bg-[#111]">
      <GlowOrb className="w-96 h-96 -top-20 -right-32 opacity-15" color="orange" />
      <GlowOrb className="w-64 h-64 bottom-20 -left-16 opacity-10" color="orange" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-8">

        {/* ── Header ── */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-10"
        >
          <div className="flex items-center gap-4">
            <Mascot size={56} animate ring={false} />
            <div>
              <h1 className="font-display font-bold text-3xl text-white">Analytics</h1>
              <p className="text-zinc-400 text-sm mt-0.5">
                {isLive ? "Live data from backend" : "Demo data — start backend for live stats"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium border ${
              isLive ? "bg-green-500/8 border-green-500/20 text-green-400" : "bg-orange-500/8 border-orange-500/20 text-orange-400"
            }`}>
              {isLive ? <Wifi className="w-3.5 h-3.5" /> : <WifiOff className="w-3.5 h-3.5" />}
              {isLive ? "Live" : "Demo"}
            </div>
            <motion.button
              onClick={load}
              whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
              className="bg-white/5 border border-white/8 rounded-xl px-4 py-2.5 text-sm text-zinc-300 flex items-center gap-2 hover:border-white/15 transition-all"
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin text-orange-400" : ""}`} />
              Refresh
            </motion.button>
          </div>
        </motion.div>

        {/* ── KPI Grid ── */}
        {loading ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="bg-[#1a1a1a] rounded-2xl border border-white/5 h-28 animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
            <KPICard icon={Users}       label="Total Leads"      value={total}     sub="all time"        accent="border-orange-500/20" delay={0}    />
            <KPICard icon={Flame}       label="High Priority"    value={high}      sub="ready to pursue" accent="border-orange-500/15" delay={0.05} trend={12} />
            <KPICard icon={ThumbsUp}    label="Medium Priority"  value={medium}    sub="worth trying"    delay={0.1} />
            <KPICard icon={XCircle}     label="Discarded"        value={discard}   sub="filtered out"    delay={0.15} />
            <KPICard icon={CheckCircle} label="Outreach Sent"    value={sent}      sub="messages drafted" accent="border-green-500/15" delay={0.2} trend={8} />
            <KPICard icon={Target}      label="Filter Rate"      value={`${convRate}%`} sub="pass filter" delay={0.25} />
            <KPICard icon={Zap}         label="Send Rate"        value={`${sentRate}%`} sub="of qualified" delay={0.3} />
            <KPICard icon={Clock}       label="Evaluated"        value={st.evaluated_count || 0} sub="by filter AI" delay={0.35} />
          </div>
        )}

        {/* ── Charts Row ── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">

          {/* Priority donut */}
          <Section title="Priority Breakdown" icon={Flame} delay={0.1}>
            <div className="flex items-center gap-6">
              <Donut
                size={130}
                stroke={20}
                segments={[
                  { label: "High",   value: high    },
                  { label: "Medium", value: medium  },
                  { label: "Cold",   value: discard },
                  { label: "Unfilt", value: st.by_priority?.unfiltered || 0 },
                ]}
              />
              <div className="space-y-3 flex-1">
                {[
                  { label: "High",       value: high,    color: "bg-orange-500", text: "text-orange-400" },
                  { label: "Medium",     value: medium,  color: "bg-white",      text: "text-white"      },
                  { label: "Discard",    value: discard, color: "bg-zinc-600",   text: "text-zinc-400"   },
                  { label: "Unfiltered", value: st.by_priority?.unfiltered||0, color: "bg-zinc-800", text: "text-zinc-500" },
                ].map(({ label, value, color, text }) => (
                  <div key={label} className="flex items-center gap-2 text-xs">
                    <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${color}`} />
                    <span className="text-zinc-300 flex-1">{label}</span>
                    <span className={`font-bold ${text}`}>{value}</span>
                    <span className="text-zinc-600">({pct(value, total)}%)</span>
                  </div>
                ))}
              </div>
            </div>
          </Section>

          {/* Service breakdown bars */}
          <Section title="By Service" icon={BarChart2} delay={0.15}>
            <div className="space-y-5">
              <BarRow label="Website Dev"  value={website}  max={total} color="bg-orange-500" textColor="text-orange-400" />
              <BarRow label="WhatsApp Bot" value={whatsapp} max={total} color="bg-white"      textColor="text-white"      />
              <BarRow label="SEO"          value={seo}      max={total} color="bg-orange-300" textColor="text-orange-300" />
            </div>
            {/* Tiny donut for service */}
            <div className="mt-6 flex justify-center">
              <Donut
                size={100}
                stroke={16}
                segments={[
                  { value: website  },
                  { value: whatsapp },
                  { value: seo      },
                ]}
              />
            </div>
          </Section>

          {/* Score averages */}
          <Section title="Filter Scores" icon={Target} delay={0.2}>
            <div className="space-y-5">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-zinc-300">Avg Online Presence</span>
                  <span className="font-bold text-orange-400">
                    {st.avg_online_score !== null ? `${st.avg_online_score}/10` : "—"}
                  </span>
                </div>
                <div className="h-2.5 bg-white/5 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: st.avg_online_score ? `${(st.avg_online_score / 10) * 100}%` : "0%" }}
                    transition={{ duration: 1, ease: "easeOut" }}
                    className="h-full rounded-full bg-gradient-to-r from-orange-600 to-orange-400"
                  />
                </div>
                <p className="text-zinc-600 text-xs mt-1">Lower = more opportunity for our services</p>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-zinc-300">Avg Digital Suitability</span>
                  <span className="font-bold text-white">
                    {st.avg_suitability !== null ? `${st.avg_suitability}/10` : "—"}
                  </span>
                </div>
                <div className="h-2.5 bg-white/5 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: st.avg_suitability ? `${(st.avg_suitability / 10) * 100}%` : "0%" }}
                    transition={{ duration: 1, ease: "easeOut", delay: 0.2 }}
                    className="h-full rounded-full bg-gradient-to-r from-white/40 to-white/80"
                  />
                </div>
                <p className="text-zinc-600 text-xs mt-1">Higher = stronger buying signal</p>
              </div>

              {/* Score insight */}
              <div className="mt-4 bg-orange-500/5 border border-orange-500/15 rounded-xl p-4">
                <p className="text-xs text-orange-300 font-semibold mb-1">💡 Insight</p>
                <p className="text-xs text-zinc-400 leading-relaxed">
                  {high > 0
                    ? `${high} high-priority lead${high > 1 ? "s" : ""} ready for immediate outreach. Focus on these first.`
                    : "Run a job to generate leads and see filter insights here."}
                </p>
              </div>
            </div>
          </Section>
        </div>

        {/* ── Outreach funnel ── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <Section title="Outreach Funnel" icon={TrendingUp} delay={0.25}>
            <div className="space-y-4">
              {[
                { label: "Total Leads Discovered", value: total,           color: "bg-zinc-600",   width: 100        },
                { label: "Passed Qualification",    value: st.hot + st.warm + st.cold, color: "bg-zinc-500", width: pct(total, total) },
                { label: "Passed Business Filter",  value: high + medium,  color: "bg-orange-600", width: pct(high + medium, total) },
                { label: "High Priority",           value: high,           color: "bg-orange-500", width: pct(high, total)          },
                { label: "Outreach Sent",           value: sent,           color: "bg-green-500",  width: pct(sent, total)          },
              ].map(({ label, value, color, width }) => (
                <div key={label} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-zinc-300">{label}</span>
                    <span className="text-white font-semibold">{value}</span>
                  </div>
                  <div className="h-6 bg-white/5 rounded-lg overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.max(width, value > 0 ? 4 : 0)}%` }}
                      transition={{ duration: 0.8, ease: "easeOut" }}
                      className={`h-full rounded-lg ${color} flex items-center justify-end pr-2`}
                    >
                      {width > 10 && (
                        <span className="text-white text-xs font-bold">{width}%</span>
                      )}
                    </motion.div>
                  </div>
                </div>
              ))}
            </div>
          </Section>

          {/* Recent leads */}
          <Section title="Recent Leads" icon={Users} delay={0.3}>
            {recentLeads.length === 0 ? (
              <div className="text-center py-8">
                <Mascot size={80} animate ring={false} className="mx-auto mb-3" />
                <p className="text-zinc-500 text-sm">No leads yet</p>
                <p className="text-zinc-600 text-xs mt-1">
                  <a href="/run" className="text-orange-400 hover:text-orange-300">Run a job</a> to start finding leads
                </p>
              </div>
            ) : (
              <div>
                {recentLeads.map((lead, i) => (
                  <RecentLeadRow key={lead.id} lead={lead} index={i} />
                ))}
                <div className="pt-3">
                  <a href="/dashboard"
                    className="text-xs text-orange-400 hover:text-orange-300 flex items-center gap-1 transition-colors">
                    View all {total} leads →
                  </a>
                </div>
              </div>
            )}
          </Section>
        </div>

        {/* ── Quick actions ── */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="grid grid-cols-1 sm:grid-cols-3 gap-4"
        >
          {[
            { href: "/run",       label: "Run New Job",        sub: "Discover fresh leads now",        icon: Zap,        btn: "btn-primary"   },
            { href: "/dashboard", label: "View Dashboard",     sub: "Browse and filter all leads",     icon: BarChart2,  btn: "btn-secondary" },
            { href: "/#contact",  label: "Get Help",           sub: "Talk to us about your pipeline",  icon: MessageSquare, btn: "btn-secondary" },
          ].map(({ href, label, sub, icon: Icon, btn }) => (
            <motion.a
              key={label}
              href={href}
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              className="bg-[#1a1a1a] border border-white/6 rounded-2xl p-5 flex items-center gap-4 hover:border-orange-500/25 transition-all duration-300 group"
            >
              <div className="w-12 h-12 rounded-xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center shrink-0 group-hover:bg-orange-500/20 transition-colors">
                <Icon className="w-6 h-6 text-orange-400" />
              </div>
              <div>
                <p className="text-white font-semibold text-sm">{label}</p>
                <p className="text-zinc-500 text-xs mt-0.5">{sub}</p>
              </div>
              <ArrowUpRight className="w-4 h-4 text-zinc-600 ml-auto group-hover:text-orange-400 transition-colors" />
            </motion.a>
          ))}
        </motion.div>

      </div>
    </div>
  );
}
