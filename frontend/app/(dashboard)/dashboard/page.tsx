"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { analyticsApi, agentApi, applicationsApi, jobsApi, quotasApi } from "@/lib/api";
import { useSubscription } from "@/lib/subscription";
import { getPlanAnalyzeBudget } from "@/lib/subscription";
import { useAuth } from "@/lib/auth";
import { useAgentStatus } from "@/lib/agent-status";
import { motion, useSpring } from "framer-motion";
import { cn, formatDate, getStatusClass, getStatusLabel, getMatchBadgeClass, timeAgo } from "@/lib/utils";
import {
  Briefcase, FileText, Send, TrendingUp, Clock, Zap,
  AlertCircle, Star, ChevronRight, Play, Pause, RefreshCw, CheckCircle,
  Activity, Target, Rocket, Lock, ExternalLink
  , Loader2
} from "lucide-react";
import { toast } from "sonner";
import Link from "next/link";
import { useEffect, useState } from "react";

function AnimatedNumber({ value, suffix = "" }: { value: number; suffix?: string }) {
  const spring = useSpring(0, { mass: 0.8, stiffness: 75, damping: 15 });
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    spring.set(value);
  }, [value, spring]);

  useEffect(() => {
    const unsub = spring.on("change", (v) => setDisplay(Math.round(v)));
    return unsub;
  }, [spring]);

  return <span>{display.toLocaleString()}{suffix}</span>;
}

function StatCard({ icon: Icon, label, value, sub, color, delay = 0, isLocked = false }: { icon: any; label: string; value: any; sub?: string; color?: string; delay?: number; isLocked?: boolean }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      whileHover={isLocked ? {} : { y: -4, scale: 1.01 }}
      className={cn(
        "bg-[#1c1c1e] border border-zinc-800 rounded-2xl p-5 group cursor-default relative overflow-hidden transition-all",
        !isLocked && "hover:border-white/25 hover:shadow-[0_0_0_1px_rgba(255,255,255,0.14),0_20px_40px_rgba(0,0,0,0.45)]"
      )}
    >
      <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-white/10 via-white/5 to-transparent rounded-full -mr-12 -mt-12 group-hover:scale-150 transition-transform duration-500" />

      {isLocked && (
        <div className="absolute inset-0 bg-[#1c1c1e]/60 backdrop-blur-[2px] z-20 flex flex-col items-center justify-center p-4 text-center">
          <div className="bg-white/10 p-2 rounded-full mb-2 border border-white/10">
            <Lock className="w-3.5 h-3.5 text-white" />
          </div>
          <p className="text-[10px] font-black uppercase tracking-widest text-white mb-2">Upgrade to Pro</p>
          <Link href="/subscription" className="px-3 py-1 bg-white text-black text-[9px] font-black uppercase tracking-tighter rounded-md hover:scale-105 transition-transform">
            Unlock
          </Link>
        </div>
      )}

      <div className={cn("flex flex-col h-full justify-between relative z-10", isLocked && "opacity-20 grayscale")}>
        <div className="flex items-center justify-between mb-3">
          <div className="w-10 h-10 rounded-xl bg-[#222222] flex items-center justify-center transition-all group-hover:scale-110">
            <Icon className="w-5 h-5 text-zinc-400 group-hover:text-white transition-colors" />
          </div>
          {sub && (
            <span className="text-[9px] font-bold uppercase tracking-wider text-zinc-400 bg-[#1c1c1e] px-2 py-0.5 rounded-md">
              {sub.split(' ')[1]}
            </span>
          )}
        </div>
        <div>
          <p className="text-[11px] font-medium text-zinc-400 mb-1">{label}</p>
          <h4 className="text-3xl font-bold tracking-tighter text-white">
            <AnimatedNumber value={value ?? 0} />
          </h4>
          {sub && <p className="text-[10px] text-zinc-400 mt-2 font-medium">{sub.split(' ')[0]}</p>}
        </div>
      </div>
    </motion.div>
  );
}

function QuotaRing({ used, limit }: { used: number; limit: number }) {
  const pct = limit > 0 ? Math.min((used / limit) * 100, 100) : 0;
  const r = 38; const circ = 2 * Math.PI * r;
  const strokeColor = pct >= 90 ? "#ffffff" : pct >= 70 ? "#e4e4e7" : "#d4d4d8"; // monochrome shades

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-[#1c1c1e] border border-white/10 rounded-2xl p-6 flex flex-col items-center justify-center relative overflow-hidden group"
    >
      <p className="text-[11px] font-bold uppercase tracking-widest text-zinc-400 mb-4 relative z-10">Daily Quota</p>
      <div className="relative z-10">
        <svg width="100" height="100" viewBox="0 0 100 100">
          {/* Base invisible ring for dark theme */}
          <circle cx="50" cy="50" r={r} fill="none" strokeWidth="6" stroke="#1a1a1a" />
          <motion.circle
            cx="50" cy="50" r={r} fill="none" strokeWidth="6" stroke={strokeColor}
            strokeDasharray={circ}
            initial={{ strokeDashoffset: circ }}
            animate={{ strokeDashoffset: circ - (circ * pct) / 100 }}
            transition={{ duration: 1.5, ease: "circOut" }}
            strokeLinecap="round" transform="rotate(-90 50 50)"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-xl font-bold tracking-tighter text-white">{Math.round(pct)}%</span>
        </div>
      </div>
      <div className="mt-4 text-center">
        <p className="text-[13px] font-bold text-white">{used} <span className="text-zinc-400 font-medium">/ {limit}</span></p>
        <p className="text-[10px] text-zinc-400 uppercase tracking-widest mt-1">Applications</p>
      </div>
    </motion.div>
  );
}

function AnalyzeTokenCard({ budget }: { budget: any }) {
  const isUnlimited = Boolean(budget?.is_unlimited);
  const usedDay = Number(budget?.used_day_tokens || 0);
  const dailyPlan = Number(budget?.daily_plan_tokens || 0);
  const used = Number(budget?.used_month_tokens || 0);
  const limit = Number(budget?.monthly_limit_tokens || 0);
  const remaining = Number(budget?.remaining_month_tokens || 0);
  const runLimit = Number(budget?.run_limit_tokens || 0);
  const dailyVisualCap = isUnlimited
    ? Math.max(1000, Math.ceil((Math.max(usedDay, 1) * 1.2) / 1000) * 1000)
    : dailyPlan;
  const monthlyVisualCap = isUnlimited
    ? Math.max(30000, Math.ceil((Math.max(used, 1) * 1.2) / 10000) * 10000)
    : limit;
  const dailyPct = dailyVisualCap > 0 ? Math.min((usedDay / dailyVisualCap) * 100, 100) : 0;
  const pct = monthlyVisualCap > 0 ? Math.min((used / monthlyVisualCap) * 100, 100) : 0;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-[#1c1c1e] border border-white/10 rounded-2xl p-6 relative overflow-hidden"
    >
      <p className="text-[11px] font-bold uppercase tracking-widest text-zinc-400 mb-3">Analyze Tokens</p>
      <div className="space-y-2">
        <p className="text-[13px] font-bold text-white">
          {isUnlimited ? "Unlimited" : `${(used / 1000).toFixed(1)}k / ${(limit / 1000).toFixed(0)}k`}
        </p>
        <p className="text-[10px] text-zinc-400 uppercase tracking-wider">
          {isUnlimited
            ? `Today: ${(usedDay / 1000).toFixed(1)}k used`
            : `Today: ${(usedDay / 1000).toFixed(1)}k / ${(dailyVisualCap / 1000).toFixed(1)}k`}
        </p>
        <div className="h-1.5 rounded-full bg-white/10 overflow-hidden">
          <div className="h-full bg-white" style={{ width: `${Math.max(0, Math.min(100, dailyPct))}%` }} />
        </div>
        <p className="text-[10px] text-zinc-400 uppercase tracking-wider">
          {isUnlimited ? `${(used / 1000).toFixed(1)}k used this month` : `${(used / 1000).toFixed(1)}k used • ${(remaining / 1000).toFixed(1)}k remaining this month`}
        </p>
        <div className="h-2 rounded-full bg-white/10 overflow-hidden">
          <div className="h-full bg-white" style={{ width: `${Math.max(0, Math.min(100, pct))}%` }} />
        </div>
        {isUnlimited && (
          <p className="text-[10px] text-zinc-500 uppercase tracking-wider">
            No monthly cap on your plan (visual scale is based on your usage)
          </p>
        )}
        <p className="text-[10px] text-zinc-500 uppercase tracking-wider">
          Run limit: {isUnlimited ? "Unlimited" : `${(runLimit / 1000).toFixed(0)}k tokens`}
        </p>
      </div>
    </motion.div>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const { quota, subscription, canAccess } = useSubscription();
  const greeting = (() => {
    const hour = new Date().getHours();
    if (hour < 12) return "morning";
    if (hour < 17) return "afternoon";
    return "evening";
  })();

  const { data: dashboard, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => analyticsApi.dashboard().then((r) => r.data),
    staleTime: 30000,
    refetchOnWindowFocus: false,
  });
  const { status: agentStatus, isWorking, currentTask, runTask } = useAgentStatus();

  const { data: queueStatus } = useQuery({
    queryKey: ["queue-status"],
    queryFn: () => applicationsApi.queueStatus().then((r) => r.data),
    staleTime: 30000,
  });

  const { data: analyzeBudget } = useQuery({
    queryKey: ["analyze-budget", user?.id],
    queryFn: () => quotasApi.analyzeBudget().then((r) => r.data),
    staleTime: 30000,
    enabled: !!user?.id,
  });

  const { data: topJobs } = useQuery({
    queryKey: ["top-jobs"],
    queryFn: () => jobsApi.list({ sort_by: "match_score", page: 1, page_size: 5 }).then((r) => r.data),
    staleTime: 60000,
  });


  const safeDashboard = dashboard ?? {
    total_jobs: 0,
    jobs_today: 0,
    high_match_jobs: 0,
    total_applications: 0,
    applications_today: 0,
    pending_approval: 0,
    interviews_scheduled: 0,
    offers_received: 0,
    response_rate: 0,
  };

  const stats = [
    { icon: Briefcase, label: "Total Jobs", value: safeDashboard.total_jobs, sub: `${safeDashboard.jobs_today} today`, href: "/jobs" },
    { icon: TrendingUp, label: "High Match Jobs", value: safeDashboard.high_match_jobs, sub: "≥75% match score", href: "/jobs?min_match_score=75" },
    { icon: Send, label: "Applied jobs", value: safeDashboard.total_applications, sub: `${safeDashboard.applications_today} today`, href: "/applications?status=applied" },
    { icon: FileText, label: "Pending Approval", value: safeDashboard.pending_approval, sub: "awaiting your review", href: "/applications?status=pending_approval" },
    { icon: Star, label: "Interviews", value: safeDashboard.interviews_scheduled, sub: "scheduled missions", href: "/interviews", isLocked: !canAccess("interviews") },
    { icon: CheckCircle, label: "Offers", value: safeDashboard.offers_received, sub: "received", href: "/applications?status=offer_received", isLocked: !canAccess("interviews") },
  ];

  const safeQuota = quota ?? {
    used: 0,
    limit: 0,
  };

  const safeAnalyzeBudget = analyzeBudget ?? {
    is_unlimited: false,
    used_day_tokens: 0,
    daily_plan_tokens: 0,
    used_month_tokens: 0,
    monthly_limit_tokens: 0,
    remaining_month_tokens: 0,
    run_limit_tokens: 0,
  };

  const planAnalyzeBudget = getPlanAnalyzeBudget(subscription?.plan);
  const resolvedAnalyzeBudget = safeAnalyzeBudget.monthly_limit_tokens > 0 || !planAnalyzeBudget
    ? safeAnalyzeBudget
    : {
        allowed: true,
        is_unlimited: false,
        plan: subscription?.plan ?? "none",
        used_day_tokens: 0,
        daily_plan_tokens: planAnalyzeBudget.daily_plan_tokens,
        used_month_tokens: 0,
        monthly_limit_tokens: planAnalyzeBudget.monthly_limit_tokens,
        remaining_month_tokens: planAnalyzeBudget.monthly_limit_tokens,
        run_limit_tokens: planAnalyzeBudget.run_limit_tokens,
        reason: null,
      };

  // Agent action UI helpers (now powered by global context)

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 p-1 md:p-4 min-h-[90vh]">

      {/* Header Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
        <h2 className="text-xl font-bold tracking-tight text-white/90 hidden md:block">System Overview</h2>
        <div className="flex flex-wrap items-center justify-end gap-3 w-full md:w-auto">
          <button
            onClick={() => runTask("scrape_jobs")}
            disabled={isWorking}
            className="flex items-center gap-2 px-5 py-2.5 bg-[#171717] hover:bg-[#222222] text-white rounded-xl text-sm font-medium transition-colors border border-[#262626] disabled:opacity-50"
          >
            {isWorking && currentTask === "scrape_jobs" ? (
              <><RefreshCw className="w-4 h-4 animate-spin text-white" /> Scraping...</>
            ) : (
              <><Play className="w-4 h-4 text-zinc-400" /> Scrape</>
            )}
          </button>
          <button
            onClick={() => runTask("analyze_jobs")}
            disabled={isWorking}
            className="flex items-center gap-2 px-5 py-2.5 bg-[#171717] hover:bg-[#222222] text-white rounded-xl text-sm font-medium transition-colors border border-[#262626] disabled:opacity-50"
          >
            {isWorking && currentTask === "analyze_jobs" ? (
              <><RefreshCw className="w-4 h-4 animate-spin text-white" /> Analyzing...</>
            ) : (
              <><Zap className="w-4 h-4 text-zinc-400 fill-zinc-400" /> Analyze</>
            )}
          </button>
          <button
            onClick={() => runTask("queue_jobs")}
            disabled={isWorking}
            className="flex items-center gap-2 px-5 py-2.5 bg-[#171717] hover:bg-[#222222] text-white rounded-xl text-sm font-medium transition-colors border border-[#262626] disabled:opacity-50"
          >
            {isWorking && currentTask === "queue_jobs" ? (
              <><RefreshCw className="w-4 h-4 animate-spin text-white" /> Queueing...</>
            ) : (
              <><Activity className="w-4 h-4 text-zinc-400" /> Queue</>
            )}
          </button>
          <button
            onClick={() => runTask("apply_queued")}
            disabled={isWorking}
            className="flex items-center gap-2 px-4 py-2 bg-[#1c1c1e] hover:bg-[#2a2a2a] text-sm font-medium text-white transition-all rounded-lg border border-[#2a2a2a]"
          >
            {isWorking && (currentTask === "apply_queued" || currentTask === "apply_jobs") ? (
              <><RefreshCw className="w-4 h-4 animate-spin" /> Deploying...</>
            ) : (
              <><Send className="w-4 h-4" /> Deploy</>
            )}
          </button>
        </div>
      </div>

      {/* Pending approval banner */}
      {(queueStatus?.pendingApproval ?? 0) > 0 && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 p-4 bg-indigo-500/10 border border-indigo-500/30 rounded-xl">
          <AlertCircle className="w-5 h-5 text-indigo-400 shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-medium text-indigo-400">
              {queueStatus.pendingApproval} application{queueStatus.pendingApproval > 1 ? "s" : ""} awaiting your approval
            </p>
            <p className="text-xs text-indigo-400/70">Review and approve before the bot applies</p>
          </div>
          <Link href="/applications?status=pending_approval"
            className="px-4 py-1.5 bg-white text-black text-xs font-bold uppercase tracking-widest rounded-lg hover:bg-zinc-200 transition-colors whitespace-nowrap">
            Review →
          </Link>
        </motion.div>
      )}


      {/* Stats grid */}
      {isLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {[...Array(6)].map((_, i) => <div key={i} className="shimmer h-32 rounded-2xl" />)}
        </div>
      ) : (
        <motion.div
          variants={{
            hidden: { opacity: 0 },
            show: {
              opacity: 1,
              transition: { staggerChildren: 0.1 }
            }
          }}
          initial="hidden"
          animate="show"
          className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4"
        >
          {stats.map((s, i) => (
            <motion.div
              key={s.label}
              variants={{
                hidden: { opacity: 0, y: 20 },
                show: { opacity: 1, y: 0 }
              }}
              transition={{ delay: i * 0.08 }}
            >
              {s.href && !s.isLocked ? (
                <Link href={s.href}>
                  <StatCard {...s} delay={i * 0.08} />
                </Link>
              ) : (
                <StatCard {...s} delay={i * 0.08} />
              )}
            </motion.div>
          ))}
        </motion.div>
      )}


      {/* Quota + Agent status row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        {/* Quota ring */}
        <QuotaRing used={safeQuota.used} limit={safeQuota.limit} />

        {/* Analyze token budget */}
        <AnalyzeTokenCard budget={resolvedAnalyzeBudget} />

        {/* Agent status - Premium */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-[#242424] border border-white/[0.08] rounded-2xl p-5 md:col-span-2 shadow-sm hover:shadow-md transition-shadow"
        >
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-3">
              <div className={cn("w-3 h-3 rounded-full", agentStatus?.is_running ? "bg-emerald-400" : "bg-zinc-300")}>
                {agentStatus?.is_running && (
                  <motion.div
                    className="w-full h-full rounded-full bg-emerald-400"
                    animate={{ scale: [1, 1.5, 1], opacity: [1, 0.5, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                )}
              </div>
              <h3 className="font-bold text-sm text-white">Automation Agent</h3>
              <div className={cn("flex items-center gap-1.5 text-[10px] px-2.5 py-1 rounded-full font-medium",
                agentStatus?.is_running ? "bg-emerald-500/15 text-emerald-600" : "bg-white/10 text-zinc-400")}>
                {agentStatus?.is_running ? "Active" : "Idle"}
              </div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <motion.div whileHover={{ scale: 1.02 }} className="p-3 bg-[#1d1d1d] rounded-xl border border-white/[0.08]">
              <p className="text-[10px] font-bold uppercase tracking-wider text-zinc-400 mb-1">Last Run</p>
              <p className="text-sm font-semibold text-white">{agentStatus?.last_run ? timeAgo(agentStatus.last_run) : "Never"}</p>
            </motion.div>
            <motion.div whileHover={{ scale: 1.02 }} className="p-3 bg-[#1d1d1d] rounded-xl border border-white/[0.08]">
              <p className="text-[10px] font-bold uppercase tracking-wider text-zinc-400 mb-1">Jobs Found</p>
              <p className="text-sm font-semibold text-white"><AnimatedNumber value={agentStatus?.jobs_found_today ?? 0} /></p>
            </motion.div>
            <motion.div whileHover={{ scale: 1.02 }} className="p-3 bg-[#1d1d1d] rounded-xl border border-white/[0.08]">
              <p className="text-[10px] font-bold uppercase tracking-wider text-zinc-400 mb-1">Applied</p>
              <p className="text-sm font-semibold text-white"><AnimatedNumber value={agentStatus?.applications_today ?? 0} /></p>
            </motion.div>
            <motion.div whileHover={{ scale: 1.02 }} className="p-3 bg-[#1d1d1d] rounded-xl border border-white/[0.08]">
              <p className="text-[10px] font-bold uppercase tracking-wider text-zinc-400 mb-1">Match Rate</p>
              <p className="text-sm font-semibold text-white">{(dashboard?.response_rate ?? 0).toFixed(1)}%</p>
            </motion.div>
          </div>
        </motion.div>
      </div>

      {/* Top job matches */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-[#242424] border border-white/[0.08] rounded-2xl p-6"
      >
        <div className="flex items-center justify-between mb-6">
          <h3 className="font-bold text-lg tracking-tight">Top Job Matches</h3>
          <Link href="/jobs" className="text-xs font-bold text-white hover:underline flex items-center gap-1">
            View all <ChevronRight className="w-3 h-3" />
          </Link>
        </div>
        <div className="space-y-4">
          {(topJobs?.items ?? []).slice(0, 5).map((job: any, i: number) => (
            <motion.div
              key={job.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 + (i * 0.05) }}
              className="flex items-center gap-4 p-4 bg-[#1d1d1d] border border-white/[0.08] rounded-2xl hover:border-white/20 hover:bg-[#252525] transition-all group"
            >
              <div className="w-12 h-12 rounded-xl bg-[#1c1c1c] shadow-sm flex items-center justify-center shrink-0 border border-white/[0.08] group-hover:scale-110 transition-transform">
                <Briefcase className="w-6 h-6 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold truncate text-white">{job.title}</p>
                <p className="text-xs text-muted-foreground font-medium">{job.company_name} · {job.location ?? "Remote"}</p>
              </div>
              {job.analysis?.match_score != null && (
                <div className="flex flex-col items-end gap-1">
                  <span className={cn("px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-tighter", getMatchBadgeClass(job.analysis.match_score))}>
                    {Math.round(job.analysis.match_score)}% Match
                  </span>
                </div>
              )}

              {job.source_url && (
                <a
                  href={job.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 rounded-lg border border-white/[0.12] text-zinc-300 hover:text-white hover:border-white/30 hover:bg-white/5 transition-colors"
                  title="Open source job page"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              )}

            </motion.div>
          ))}
          {(!topJobs?.items || topJobs.items.length === 0) && (
            <div className="text-center py-20 bg-[#1d1d1d] border border-white/[0.08] rounded-[20px] shadow-[inset_0_1px_0_rgba(255,255,255,0.035)] transition-all">
              <div className="w-12 h-12 rounded-full bg-[#1c1c1c] border border-white/[0.08] flex items-center justify-center mx-auto mb-6">
                <Target className="w-5 h-5 text-zinc-600" />
              </div>
              <p className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400 mb-2">No Matches Deployed</p>
              <p className="text-[9px] font-bold text-zinc-600 max-w-[200px] mx-auto uppercase tracking-wider leading-relaxed italic">
                Ready to start? Initializing the agent will populate this sector.
              </p>
            </div>
          )}
        </div>
      </motion.div>

    </div>
  );
}
