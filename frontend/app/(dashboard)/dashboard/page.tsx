"use client";
import { useQuery, useMutation } from "@tanstack/react-query";
import { analyticsApi, agentApi, applicationsApi, jobsApi } from "@/lib/api";
import { useSubscription } from "@/lib/subscription";
import { useAuth } from "@/lib/auth";
import { motion } from "framer-motion";
import { cn, formatDate, getStatusClass, getStatusLabel, getMatchBadgeClass, timeAgo } from "@/lib/utils";
import {
  Briefcase, FileText, Send, TrendingUp, Clock, Zap,
  AlertCircle, Star, ChevronRight, Play, Pause, RefreshCw, CheckCircle,
} from "lucide-react";
import { toast } from "sonner";
import Link from "next/link";

function StatCard({ icon: Icon, label, value, sub, color }: { icon: any; label: string; value: any; sub?: string; color?: string }) {
  return (
    <div className="glass-card p-5 card-hover">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-muted-foreground font-medium mb-1">{label}</p>
          <p className="text-3xl font-bold font-display">{value ?? "—"}</p>
          {sub && <p className="text-xs text-muted-foreground mt-1">{sub}</p>}
        </div>
        <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center", color ?? "bg-brand-purple/20")}>
          <Icon className="w-5 h-5 text-brand-purple-light" />
        </div>
      </div>
    </div>
  );
}

function QuotaRing({ used, limit }: { used: number; limit: number }) {
  const pct = limit > 0 ? Math.min((used / limit) * 100, 100) : 0;
  const r = 36; const circ = 2 * Math.PI * r;
  const color = pct >= 90 ? "#ef4444" : pct >= 70 ? "#f59e0b" : "#10b981";
  return (
    <div className="glass-card p-5 flex flex-col items-center justify-center">
      <p className="text-xs text-muted-foreground font-medium mb-3">Daily Quota</p>
      <svg width="90" height="90" viewBox="0 0 90 90">
        <circle cx="45" cy="45" r={r} fill="none" strokeWidth="6" stroke="rgba(255,255,255,0.07)" />
        <circle cx="45" cy="45" r={r} fill="none" strokeWidth="6" stroke={color}
          strokeDasharray={circ} strokeDashoffset={circ - (circ * pct) / 100}
          strokeLinecap="round" transform="rotate(-90 45 45)" style={{ transition: "stroke-dashoffset 0.5s ease" }} />
        <text x="45" y="48" textAnchor="middle" fill={color} fontSize="13" fontWeight="700">{Math.round(pct)}%</text>
      </svg>
      <p className="text-xs text-muted-foreground mt-2">{used} / {limit} used</p>
    </div>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const { quota, subscription } = useSubscription();

  const { data: dashboard, isLoading } = useQuery({ queryKey: ["dashboard"], queryFn: () => analyticsApi.dashboard().then((r) => r.data) });
  const { data: agentStatus } = useQuery({ queryKey: ["agent-status"], queryFn: () => agentApi.status().then((r) => r.data), refetchInterval: 30000 });
  const { data: queueStatus } = useQuery({ queryKey: ["queue-status"], queryFn: () => applicationsApi.queueStatus().then((r) => r.data) });
  const { data: topJobs } = useQuery({ queryKey: ["top-jobs"], queryFn: () => jobsApi.list({ sort_by: "match_score", page: 1, page_size: 5 }).then((r) => r.data) });

  const runAgent = useMutation({
    mutationFn: () => agentApi.run({ task_type: "scrape_jobs" }),
    onSuccess: () => toast.success("Scrape started! Check back in a few minutes."),
    onError: () => toast.error("Failed to start agent"),
  });

  const stats = dashboard ? [
    { icon: Briefcase, label: "Total Jobs", value: dashboard.total_jobs, sub: `${dashboard.jobs_today} today`, color: "bg-blue-500/20" },
    { icon: TrendingUp, label: "High Match Jobs", value: dashboard.high_match_jobs, sub: "≥75% match score", color: "bg-emerald-500/20" },
    { icon: Send, label: "Applications", value: dashboard.total_applications, sub: `${dashboard.applications_today} today`, color: "bg-violet-500/20" },
    { icon: FileText, label: "Pending Approval", value: dashboard.pending_approval, sub: "awaiting your review", color: "bg-amber-500/20" },
    { icon: Star, label: "Interviews", value: dashboard.interviews_scheduled, sub: "scheduled", color: "bg-cyan-500/20" },
    { icon: CheckCircle, label: "Offers", value: dashboard.offers_received, sub: "received", color: "bg-green-500/20" },
  ] : [];

  return (
    <div className="space-y-7">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold font-display">
            Good {new Date().getHours() < 12 ? "morning" : new Date().getHours() < 17 ? "afternoon" : "evening"},{" "}
            <span className="gradient-text">{user?.full_name?.split(" ")[0] ?? "there"}</span> 👋
          </h1>
          <p className="text-muted-foreground text-sm mt-1">Here's your job automation dashboard</p>
        </div>
        <button
          onClick={() => runAgent.mutate()}
          disabled={runAgent.isPending}
          className="flex items-center gap-2 px-4 py-2 bg-brand-purple text-white rounded-lg text-sm font-medium hover:bg-brand-purple/90 transition-all disabled:opacity-50"
        >
          {runAgent.isPending ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          Run Now
        </button>
      </div>

      {/* Pending approval banner */}
      {(queueStatus?.pendingApproval ?? 0) > 0 && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl">
          <AlertCircle className="w-5 h-5 text-amber-400 shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-medium text-amber-400">
              {queueStatus.pendingApproval} application{queueStatus.pendingApproval > 1 ? "s" : ""} awaiting your approval
            </p>
            <p className="text-xs text-muted-foreground">Review and approve before the bot applies</p>
          </div>
          <Link href="/applications?status=pending_approval"
            className="px-3 py-1.5 bg-amber-500/20 text-amber-400 rounded-lg text-xs font-medium hover:bg-amber-500/30 transition-colors whitespace-nowrap">
            Review →
          </Link>
        </motion.div>
      )}

      {/* Stats grid */}
      {isLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {[...Array(6)].map((_, i) => <div key={i} className="skeleton h-28 rounded-xl" />)}
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {stats.map((s, i) => (
            <motion.div key={s.label} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}>
              <StatCard {...s} />
            </motion.div>
          ))}
        </div>
      )}

      {/* Quota + Agent status row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Quota ring */}
        {quota && <QuotaRing used={quota.used} limit={quota.limit} />}

        {/* Agent status */}
        <div className="glass-card p-5 md:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-sm">Agent Status</h3>
            <div className={cn("flex items-center gap-1.5 text-xs px-2 py-1 rounded-full",
              agentStatus?.is_running ? "bg-emerald-500/20 text-emerald-400" : "bg-zinc-500/20 text-zinc-400")}>
              <div className={cn("w-1.5 h-1.5 rounded-full", agentStatus?.is_running ? "bg-emerald-400 animate-pulse" : "bg-zinc-400")} />
              {agentStatus?.is_running ? "Running" : "Idle"}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="p-3 bg-muted/50 rounded-lg">
              <p className="text-xs text-muted-foreground mb-1">Last run</p>
              <p className="font-medium">{agentStatus?.last_run ? timeAgo(agentStatus.last_run) : "Never"}</p>
            </div>
            <div className="p-3 bg-muted/50 rounded-lg">
              <p className="text-xs text-muted-foreground mb-1">Jobs today</p>
              <p className="font-medium">{agentStatus?.jobs_found_today ?? 0}</p>
            </div>
            <div className="p-3 bg-muted/50 rounded-lg">
              <p className="text-xs text-muted-foreground mb-1">Applied today</p>
              <p className="font-medium">{agentStatus?.applications_today ?? 0}</p>
            </div>
            <div className="p-3 bg-muted/50 rounded-lg">
              <p className="text-xs text-muted-foreground mb-1">Response rate</p>
              <p className="font-medium">{((dashboard?.response_rate ?? 0) * 100).toFixed(1)}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Top job matches */}
      <div className="glass-card p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold">Top Job Matches</h3>
          <Link href="/jobs" className="text-xs text-brand-purple-light hover:text-brand-purple transition-colors flex items-center gap-1">
            View all <ChevronRight className="w-3 h-3" />
          </Link>
        </div>
        <div className="space-y-3">
          {(topJobs?.items ?? []).slice(0, 5).map((job: any) => (
            <div key={job.id} className="flex items-center gap-4 p-3 bg-muted/30 rounded-xl hover:bg-muted/50 transition-colors group">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-brand-purple/30 to-brand-blue/30 flex items-center justify-center shrink-0">
                <Briefcase className="w-5 h-5 text-brand-purple-light" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{job.title}</p>
                <p className="text-xs text-muted-foreground">{job.company_name} · {job.location ?? "Remote"}</p>
              </div>
              {job.analysis?.match_score != null && (
                <span className={cn("px-2.5 py-1 rounded-full text-xs font-bold", getMatchBadgeClass(job.analysis.match_score))}>
                  {Math.round(job.analysis.match_score)}%
                </span>
              )}
              <Link href={`/jobs/${job.id}`}
                className="opacity-0 group-hover:opacity-100 text-xs text-brand-purple-light flex items-center gap-0.5 transition-opacity shrink-0">
                View <ChevronRight className="w-3 h-3" />
              </Link>
            </div>
          ))}
          {(!topJobs?.items || topJobs.items.length === 0) && (
            <div className="text-center py-8 text-muted-foreground text-sm">
              No jobs yet — run the agent to scrape new listings.
            </div>
          )}
        </div>
      </div>

      {/* Recent activity */}
      {dashboard?.recent_activity && dashboard.recent_activity.length > 0 && (
        <div className="glass-card p-5">
          <h3 className="font-semibold mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {dashboard.recent_activity.slice(0, 6).map((activity: any, i: number) => (
              <div key={i} className="flex items-center gap-3 text-sm">
                <div className="w-2 h-2 rounded-full bg-brand-purple-light shrink-0" />
                <span className="text-muted-foreground flex-1">{activity.description ?? JSON.stringify(activity)}</span>
                <span className="text-xs text-muted-foreground">{timeAgo(activity.created_at)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
