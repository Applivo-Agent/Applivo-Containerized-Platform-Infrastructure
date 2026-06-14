"use client";
import React, { useEffect, useState } from "react";
import {
  Users, Activity, Shield, BarChart3, Globe, Zap,
  AlertCircle, CheckCircle2, Settings, Database, DollarSign,
  Briefcase, TrendingUp, Server, Pause, Play, RotateCcw,
  Trash2, Search, Filter, MoreHorizontal, X, Check,
  ToggleLeft, FileText, History, Cpu, Loader2,
  Clock, Save, Settings2, Share2
} from "lucide-react";
import { motion } from "framer-motion";
import { AreaChart, Area, BarChart, Bar, ComposedChart, Cell, CartesianGrid, Legend, LineChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis, ReferenceLine } from "recharts";
import { siGooglegemini } from "simple-icons";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

type Tab = "dashboard" | "ai-metrics" | "users" | "subscriptions" | "payments" | "applications" | "jobs" | "bot" | "queue" | "errors" | "analytics" | "features" | "audit" | "settings";

interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  plan: string;
  created_at: string;
  last_login_at: string | null;
  applications_count: number;
  ai_credits_used: number;
  ai_credits_limit: number;
  total_tokens: number;
}

interface Subscription {
  id: string;
  user_email: string;
  plan: string;
  status: string;
  start_date: string;
  end_date: string | null;
  daily_limit: number;
}

interface Payment {
  id: string;
  user_email: string;
  amount: number;
  currency: string;
  status: string;
  plan?: string | null;
  razorpay_order_id?: string | null;
  razorpay_payment_id?: string | null;
  created_at: string;
}

interface BotStats {
  applications_today: number;
  success_rate: number;
  failed: number;
  queue_size: number;
  status: string;
}

interface QueueStats {
  pending: number;
  processing: number;
  applying: number;
  failed: number;
  total_jobs: number;
  total_scraped: number;
  scheduled_tasks: { id: string; name: string; next_run: string | null }[];
  scheduler_running: boolean;
  celery_workers: { name: string; status: string; active_tasks: number }[];
  celery_queues: Record<string, number>;
  celery_error?: string;
}

interface SystemHealth {
  status: string;
  timestamp: string;
  checks: Record<string, string>;
  celery_workers?: { name: string; status: string; active_tasks: number }[];
}

interface Stats {
  total_users: number;
  active_users: number;
  total_subscriptions: number;
  active_subscriptions: number;
  total_revenue: number;
  revenue_this_month: number;
  total_applications: number;
  applications_this_month: number;
  jobs_scraped: number;
}

interface Application {
  id: string;
  user_email: string;
  job_title: string;
  company: string;
  status: string;
  error: string | null;
  created_at: string;
}

interface Job {
  id: string;
  title: string;
  company: string;
  source: string;
  status: string;
  scraped_at: string;
}

interface FeatureFlag {
  key: string;
  label: string;
  description: string;
  enabled: boolean;
}

interface AuditLog {
  id: string;
  admin_email: string;
  action: string;
  target: string;
  ip_address: string;
  result: string;
  created_at: string;
}

interface AnalyticsData {
  applications_by_day: { date: string; count: number }[];
  revenue_by_day: { date: string; amount: number }[];
  users_by_day: { date: string; count: number }[];
}

interface LLMProviderUsage {
  provider: string;
  model: string;
  requests: number;
  tokens_used: number;
  prompt_tokens: number;
  completion_tokens: number;
  cached_tokens: number;
  average_tokens: number;
  success_rate: number;
}

interface LLMTimelinePoint {
  date: string;
  total_requests: number;
  total_tokens: number;
  groq_requests: number;
  groq_tokens: number;
  gemini_requests: number;
  gemini_tokens: number;
  status_200: number;
  status_429: number;
  status_500: number;
  prompt_tokens: number;
  completion_tokens: number;
  cached_tokens: number;
  success_rate: number;
  total_errors: number;
}

interface LLMModelTimelinePoint {
  date: string;
  requests: number;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  errors: number;
}

interface LLMModelMetrics {
  model: string;
  provider: string;
  total_requests: number;
  total_tokens: number;
  success_rate: number;
  rate_limit: number;
  timeline: LLMModelTimelinePoint[];
}

interface LLMSystemOverview {
  avg_latency_ms: number;
  cache_hit_rate: number;
  tps: number;
  availability: number;
}

interface LLMFeatureMetric {
  feature: string;
  tokens: number;
  requests: number;
}

interface LLMUserUsage {
  user_email: string;
  total_tokens: number;
  requests: number;
}

interface LLMUsageData {
  total_requests: number;
  total_tokens: number;
  total_estimated_cost: number;
  providers: LLMProviderUsage[];
  timeline: LLMTimelinePoint[];
  models: LLMModelMetrics[];
  overview: LLMSystemOverview;
  features: LLMFeatureMetric[];
  top_users: LLMUserUsage[];
  error_distribution: Record<string, number>;
}

function KPIItem({ title, value, sub, icon }: { title: string; value: string; sub: string; icon: React.ReactNode }) {
  return (
    <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[24px] p-5 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)] group hover:border-white/20 transition-all">
      <div className="flex items-center justify-between mb-4">
        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-600">{title}</span>
        <div className="p-1.5 rounded-lg bg-white/[0.02] border border-white/5 text-zinc-500 group-hover:text-white transition-colors">
          {icon}
        </div>
      </div>
      <div className="space-y-1">
        <div className="text-2xl font-bold text-white tracking-tight">{value}</div>
        <div className="text-[9px] font-black uppercase tracking-widest text-zinc-600 italic">{sub}</div>
      </div>
    </div>
  )
}

function ChartContainer({ title, icon, children, rateLimit, subtitle }: { title: string; icon?: React.ReactNode; children: React.ReactNode; rateLimit?: number; subtitle?: string }) {
  return (
    <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[24px] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)] min-h-full">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-[10px] font-black text-gray-500 uppercase tracking-widest">{title}</h4>
        {icon || <div className="w-4 h-4 rounded-full border border-gray-600 flex items-center justify-center text-[10px] text-gray-500 font-bold">?</div>}
      </div>
      {subtitle && <p className="text-[9px] text-zinc-600 mb-6">{subtitle}</p>}
      <div className="h-[280px] w-full relative">
        {children}
      </div>
    </div>
  );
}

function DropdownItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/[0.03] border border-white/10 hover:bg-white/5 transition-all cursor-pointer min-w-[140px]">
      <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">{label}</span>
      <span className="text-xs font-semibold text-white">{value}</span>
      <MoreHorizontal className="w-3 h-3 text-zinc-600 ml-auto" />
    </div>
  );
}

function ProviderBadgeIcon({ provider }: { provider: string }) {
  if (provider === "groq") {
    return (
      <svg
        viewBox="0 0 24 24"
        className="h-[18px] w-[18px]"
        fill="none"
        aria-hidden="true"
        role="img"
        focusable="false"
      >
        <circle cx="12" cy="12" r="8.1" stroke="currentColor" strokeWidth="2.6" />
        <path d="M5.1 19.2L18.9 4.8" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" />
      </svg>
    );
  }

  const icon = siGooglegemini;
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-[18px] w-[18px]"
      fill="currentColor"
      aria-hidden="true"
      role="img"
      focusable="false"
    >
      <path d={icon.path} />
    </svg>
  );
}

const TABS = [
  { id: "dashboard" as Tab, label: "Dashboard", icon: BarChart3 },
  { id: "ai-metrics" as Tab, label: "AI Metrics", icon: Cpu },
  { id: "users" as Tab, label: "Users", icon: Users },
  { id: "subscriptions" as Tab, label: "Subscriptions", icon: Zap },
  { id: "payments" as Tab, label: "Payments", icon: DollarSign },
  { id: "applications" as Tab, label: "Applications", icon: FileText },
  { id: "jobs" as Tab, label: "Jobs", icon: Briefcase },
  { id: "bot" as Tab, label: "Bot Monitor", icon: Globe },
  { id: "queue" as Tab, label: "Queue", icon: Server },
  { id: "errors" as Tab, label: "Errors", icon: AlertCircle },
  { id: "analytics" as Tab, label: "Analytics", icon: TrendingUp },
  { id: "features" as Tab, label: "Feature Flags", icon: ToggleLeft },
  { id: "audit" as Tab, label: "Audit Logs", icon: History },
  { id: "settings" as Tab, label: "Settings", icon: Settings },
];

export default function AdminDashboard() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<Tab>("dashboard");
  const [loading, setLoading] = useState(true);

  // Data states
  const [stats, setStats] = useState<Stats | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [botStats, setBotStats] = useState<BotStats | null>(null);
  const [queueStats, setQueueStats] = useState<QueueStats | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [featureFlags, setFeatureFlags] = useState<FeatureFlag[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [llmUsage, setLlmUsage] = useState<LLMUsageData | null>(null);
  const [failedJobs, setFailedJobs] = useState<any[]>([]);
  const [platformMessages, setPlatformMessages] = useState<any[]>([]);

  // Search/filter states
  const [userSearch, setUserSearch] = useState("");
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  // 1. General Tab Loading (runs on tab switch)
  useEffect(() => {
    if (!user || !user.is_superuser) return;
    if (activeTab !== "users") {
      loadTabData(activeTab);
    }
  }, [user, activeTab]);

  // 2. Specialized User Search (runs on search input with debounce)
  useEffect(() => {
    if (!user || !user.is_superuser || activeTab !== "users") return;

    const timeout = setTimeout(() => {
      loadTabData("users", userSearch);
    }, 500);

    return () => clearTimeout(timeout);
  }, [user, activeTab, userSearch]);

  // Safety timeout - reset loading after 10 seconds no matter what
  useEffect(() => {
    const timeout = setTimeout(() => {
      console.log("Admin: safety timeout - setting loading=false");
      setLoading(false);
    }, 10000);
    return () => clearTimeout(timeout);
  }, [activeTab]);

  const loadTabData = async (tab: Tab, searchQuery: string = "") => {
    console.log("loadTabData called with tab:", tab, "current loading:", loading);
    setLoading(true);
    try {
      console.log("Fetching data for tab:", tab);
      switch (tab) {
        case "dashboard": {
          // Parallel fetch for operational dashboard
          const [statsRes, healthRes, botRes, queueRes, failedRes] = await Promise.all([
            api.get("/admin/stats"),
            api.get("/admin/system/health"),
            api.get("/admin/automation/status"),
            api.get("/admin/queue/status").catch(() => ({ data: null })),
            api.get("/admin/queue/failed").catch(() => ({ data: { failed_jobs: [] } }))
          ]);
          setStats(statsRes.data);
          setSystemHealth(healthRes.data);
          setBotStats(botRes.data);
          if (queueRes.data) setQueueStats(queueRes.data);
          setFailedJobs(failedRes.data.failed_jobs || []);
          break;
        }
        case "ai-metrics": {
          const llmRes = await api.get("/admin/llm-usage");
          setLlmUsage(llmRes.data);
          break;
        }
        case "users":
          const usersRes = await api.get(`/admin/users?page_size=50&search=${encodeURIComponent(searchQuery)}`);
          setUsers(usersRes.data || []);
          break;
        case "subscriptions":
          const subsRes = await api.get("/admin/subscriptions");
          setSubscriptions(subsRes.data || []);
          break;
        case "payments":
          const payRes = await api.get("/admin/payments?page_size=50");
          setPayments(Array.isArray(payRes.data) ? payRes.data : (payRes.data.items || []));
          break;
        case "applications":
          const appRes = await api.get("/admin/applications?page_size=50");
          setApplications(appRes.data.items || []);
          break;
        case "jobs":
          const jobsRes = await api.get("/admin/jobs?page_size=50");
          setJobs(jobsRes.data.items || []);
          break;
        case "bot": {
          const botRes = await api.get("/admin/automation/status");
          setBotStats(botRes.data);
          break;
        }
        case "queue": {
          try {
            const queueRes = await api.get("/admin/queue/status");
            setQueueStats(queueRes.data);
          } catch (e: any) {
            console.warn("Queue status unavailable:", e);
            setQueueStats({
              pending: 0,
              processing: 0,
              applying: 0,
              failed: 0,
              total_jobs: 0,
              total_scraped: 0,
              scheduled_tasks: [],
              scheduler_running: false,
              celery_workers: [],
              celery_queues: {},
              celery_error: e?.response?.data?.detail || "Queue service unavailable",
            });
          }
          break;
        }
        case "analytics":
          const analyticsRes = await api.get("/admin/analytics");
          setAnalyticsData(analyticsRes.data);
          break;
        case "features":
          const featuresRes = await api.get("/admin/features");
          setFeatureFlags(featuresRes.data || []);
          break;
        case "audit":
          const auditRes = await api.get("/admin/audit-logs?page_size=50");
          setAuditLogs(auditRes.data.items || []);
          break;
        case "settings":
          const healthRes = await api.get("/admin/system/health");
          setSystemHealth(healthRes.data);
          break;
      }
    } catch (err: any) {
      console.error("Failed to load:", err, err?.response?.data);
      toast.error(err?.response?.data?.detail || `Failed to load ${tab}`);
    } finally {
      setLoading(false);
    }
  };

  const handleUserAction = async (userId: string, action: "suspend" | "reactivate" | "delete") => {
    setActionLoading(userId);
    try {
      if (action === "delete") {
        if (!confirm("Are you sure? This cannot be undone.")) return;
        await api.delete(`/admin/users/${userId}`);
        toast.success("User deleted");
      } else if (action === "suspend") {
        await api.patch(`/admin/users/${userId}`, { is_active: false });
        toast.success("User suspended");
      } else if (action === "reactivate") {
        await api.patch(`/admin/users/${userId}`, { is_active: true });
        toast.success("User reactivated");
      }
      loadTabData("users");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Action failed");
    } finally {
      setActionLoading(null);
    }
  };

  const runSystemAction = async (action: string) => {
    setLoading(true);
    try {
      await api.post(`/admin/system/${action}`);
      toast.success(`${action} completed`);
      loadTabData("settings");
    } catch (err) {
      toast.error("Action failed");
    } finally {
      setLoading(false);
    }
  };

  if (!user?.is_superuser) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Shield className="w-16 h-16 text-white mx-auto mb-4" />
          <h2 className="text-xl font-bold">Access Denied</h2>
          <p className="text-muted-foreground">You must be an admin to view this page.</p>
        </div>
      </div>
    );
  }

  const filteredUsers = users.filter(u =>
    u.email.toLowerCase().includes(userSearch.toLowerCase()) ||
    u.full_name.toLowerCase().includes(userSearch.toLowerCase()) ||
    u.id.toLowerCase().includes(userSearch.toLowerCase())
  );

  return (
    <div className="admin-panel min-h-screen bg-[#000000] text-white p-6">
      {/* Page Header */}
      <div className="flex items-center gap-3 mb-6 max-w-7xl mx-auto">
        <div className="p-2 bg-[#242424] border border-white/[0.08] rounded-lg">
          <Shield className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Admin Panel</h1>
          <p className="text-sm text-zinc-400 mt-1">System operations and infrastructure management</p>
        </div>
      </div>

      <style jsx global>{`
        .admin-panel [class*="bg-[#0b0b0f]"] {
          background-color: #1c1c1e !important;
          box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02) !important;
        }
        .admin-panel [class*="bg-black"] {
          background-color: #111118 !important;
        }
        .admin-panel [class*="bg-black/40"] {
          background-color: #111118 !important;
        }
        .admin-panel [class*="bg-[#050505]/50"] {
          background-color: rgba(17, 17, 24, 0.5) !important;
        }
      `}</style>
      <div className="max-w-[1400px] mx-auto space-y-8">

        {/* Tabs */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          {TABS.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-3 py-2 text-[11px] font-black uppercase tracking-widest whitespace-nowrap transition-all border-b-2 ${activeTab === tab.id
                  ? "border-white text-white"
                  : "border-transparent text-zinc-500 hover:text-zinc-300"
                }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {loading ? (
          <div className="-card p-12 text-center">
            <div className="w-8 h-8 border-2 border-brand-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="text-muted-foreground mt-4">Loading...</p>
          </div>
        ) : (
          <>
            {activeTab === "dashboard" && <DashboardTab stats={stats} botStats={botStats} queueStats={queueStats} health={systemHealth} failedJobs={failedJobs} onAction={runSystemAction} loading={loading} />}
            {activeTab === "ai-metrics" && <AIMetricsTab llmUsage={llmUsage} />}
            {activeTab === "users" && <UsersTab users={filteredUsers} search={userSearch} setSearch={setUserSearch} actionLoading={actionLoading} onAction={handleUserAction} />}
            {activeTab === "subscriptions" && <SubscriptionsTab subscriptions={subscriptions} />}
            {activeTab === "payments" && <PaymentsTab payments={payments} />}
            {activeTab === "applications" && <ApplicationsTab applications={applications} />}
            {activeTab === "jobs" && <JobsTab jobs={jobs} />}
            {activeTab === "bot" && <BotTab stats={botStats} />}
            {activeTab === "queue" && <QueueTab stats={queueStats} />}
            {activeTab === "errors" && <ErrorsTab failedJobs={failedJobs} setFailedJobs={setFailedJobs} loading={loading} />}
            {activeTab === "analytics" && <AnalyticsTab data={analyticsData} />}
            {activeTab === "features" && <FeaturesTab flags={featureFlags} />}
            {activeTab === "audit" && <AuditTab logs={auditLogs} />}
            {activeTab === "settings" && <SettingsTab health={systemHealth} onAction={runSystemAction} loading={loading} />}
          </>
        )}
      </div>
    </div>
  );
}

function DashboardTab({ stats, botStats, queueStats, health, failedJobs, onAction, loading }: {
  stats: Stats | null;
  botStats: BotStats | null;
  queueStats: QueueStats | null;
  health: SystemHealth | null;
  failedJobs: any[];
  onAction: (a: string) => void;
  loading: boolean;
}) {
  const isBotRunning = botStats?.status === "running" || botStats?.status === "active";
  const isSchedulerRunning = queueStats?.scheduler_running;

  const healthItems = health?.checks ? Object.entries(health.checks).map(([name, status]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    status: status === "healthy" || status === "available" || status === "running",
    icon: name === "database" ? Database : name === "redis" ? Zap : name === "celery" ? Cpu : RotateCcw,
  })) : [
    { name: "Database", status: true, icon: Database },
    { name: "Redis", status: true, icon: Zap },
    { name: "Celery", status: false, icon: Cpu },
    { name: "APScheduler", status: isSchedulerRunning, icon: RotateCcw },
  ];

  const opsMetrics = [
    { label: "Applications Today", value: botStats?.applications_today || 0, sub: "Processing normally", icon: FileText, color: "text-white" },
    { label: "Success Rate", value: botStats?.success_rate ? `${botStats.success_rate}%` : "0%", sub: "Agent accuracy", icon: CheckCircle2, color: "text-white" },
    { label: "Failed Jobs", value: botStats?.failed || 0, sub: "Requires attention", icon: AlertCircle, color: "text-white" },
    { label: "Queue Size", value: botStats?.queue_size || 0, sub: "Pending tasks", icon: Server, color: "text-white" },
    { label: "Bot Status", value: isBotRunning ? "Running" : "Idle", sub: isBotRunning ? "Active session" : "Standby", icon: Globe, color: "text-white" },
  ];

  return (
    <div className="space-y-6 pb-12">
      {/* CARD 1: SYSTEM HEALTH */}
      <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[16px] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
        <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400 mb-6">System Health</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {healthItems.map((s) => (
            <div key={s.name} className="flex items-center gap-4 group">
              <div className="p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.05]">
                <s.icon className="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" />
              </div>
              <div className="flex-1">
                <div className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-0.5">{s.name}</div>
                <div className="flex items-center gap-2">
                  <span className={cn(
                    "text-sm font-semibold tracking-tight",
                    s.status ? "text-emerald-400" : "text-red-400"
                  )}>
                    {s.status ? "Online" : "Offline"}
                  </span>
                  <div className={cn(
                    "w-1.5 h-1.5 rounded-full animate-pulse",
                    s.status ? "bg-emerald-400" : "bg-red-400"
                  )} />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* CARD 2: LIVE OPERATIONS */}
      <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[16px] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
        <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400 mb-6">Live Operations</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-8">
          {opsMetrics.map((met) => (
            <div key={met.label} className="space-y-1">
              <div className="text-[28px] font-semibold text-white tracking-tight leading-none group-hover:scale-105 transition-transform">{met.value}</div>
              <div className="text-[11px] font-bold text-gray-500 uppercase tracking-widest">{met.label}</div>
              <div className={cn(
                "text-[10px] font-bold italic",
                met.label === "Bot Status" && met.value === "Running" ? "text-blue-400" :
                  met.label === "Success Rate" ? "text-emerald-400" :
                    met.label === "Failed Jobs" && typeof met.value === "number" && met.value > 0 ? "text-red-400" :
                      "text-gray-600"
              )}>
                {met.sub}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* CARD 3: MANUAL CONTROLS */}
      <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[16px] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
        <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400 mb-6">Manual Controls</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <button
            onClick={() => onAction('run-scraper')}
            className="flex items-center gap-4 px-6 py-4 bg-[#202024] border border-white/10 rounded-xl hover:bg-white/[0.05] hover:border-white/20 transition-all group text-left"
          >
            <div className="p-2.5 rounded-lg bg-white/[0.03] border border-white/[0.05] group-hover:scale-110 transition-transform">
              <Briefcase className="w-5 h-5 text-gray-400 group-hover:text-white" />
            </div>
            <div>
              <div className="text-sm font-semibold text-white">Run Scraper</div>
              <div className="text-[10px] text-gray-500 font-medium">Initiate job discovery loop</div>
            </div>
          </button>

          <button
            onClick={() => onAction('clear-queue')}
            className="flex items-center gap-4 px-6 py-4 bg-[#202024] border border-white/10 rounded-xl hover:bg-white/[0.05] hover:border-white/20 transition-all group text-left"
          >
            <div className="p-2.5 rounded-lg bg-white/[0.03] border border-white/[0.05] group-hover:scale-110 transition-transform">
              <RotateCcw className="w-5 h-5 text-gray-400 group-hover:text-white" />
            </div>
            <div>
              <div className="text-sm font-semibold text-white">Clear Queue</div>
              <div className="text-[10px] text-gray-500 font-medium">Flush all pending tasks</div>
            </div>
          </button>

          <button
            onClick={() => onAction('restart-worker')}
            className="flex items-center gap-4 px-6 py-4 bg-[#202024] border border-white/10 rounded-xl hover:bg-white/[0.05] hover:border-white/20 transition-all group text-left"
          >
            <div className="p-2.5 rounded-lg bg-white/[0.03] border border-white/[0.05] group-hover:scale-110 transition-transform">
              <Activity className="w-5 h-5 text-gray-400 group-hover:text-white" />
            </div>
            <div>
              <div className="text-sm font-semibold text-white">Restart Worker</div>
              <div className="text-[10px] text-gray-500 font-medium">Reload background process</div>
            </div>
          </button>
        </div>
      </div>

      {/* CARD 4: RECENT ERRORS */}
      <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[16px] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
        <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400 mb-6">Recent Errors</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-white/[0.05] text-[10px] font-bold uppercase tracking-widest text-gray-500">
                <th className="py-3 px-4 first:pl-0">Process</th>
                <th className="py-3 px-4">Entity</th>
                <th className="py-3 px-4">Issue</th>
                <th className="py-3 px-4">Retries</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4 last:pr-0 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.03]">
              {failedJobs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-16 text-center bg-[#141418]/50">
                    <div className="w-12 h-12 rounded-full bg-white/[0.02] border border-white/5 flex items-center justify-center mx-auto mb-4">
                      <CheckCircle2 className="w-5 h-5 text-emerald-500/30" />
                    </div>
                    <p className="text-[11px] font-black uppercase tracking-[0.2em] text-emerald-400 mb-1">Zero Failure Events / Operational</p>
                    <p className="text-[10px] font-bold text-zinc-800 uppercase tracking-widest italic leading-relaxed">System cluster fully synchronized. No intervention required.</p>
                  </td>
                </tr>
              ) : failedJobs.slice(0, 5).map((job) => (
                <tr key={job.id} className="hover:bg-white/[0.02] transition-colors group">
                  <td className="py-4 px-4 first:pl-0">
                    <div className="text-[13px] font-semibold text-white leading-snug">{job.job_title}</div>
                    <div className="text-[10px] font-bold text-gray-600 uppercase tracking-tighter">Application Loop</div>
                  </td>
                  <td className="py-4 px-4">
                    <div className="text-[12px] text-gray-400 font-medium">{job.company}</div>
                  </td>
                  <td className="py-4 px-4">
                    <span className="text-[11px] font-medium text-red-400/80 bg-red-400/[0.03] border border-red-400/10 px-2.5 py-1 rounded inline-block max-w-[300px] truncate leading-none">
                      {job.error || "Execution timeout"}
                    </span>
                  </td>
                  <td className="py-4 px-4">
                    <div className="text-[12px] font-bold text-gray-500">{job.retry_count}</div>
                  </td>
                  <td className="py-4 px-4">
                    <div className="text-[11px] font-medium text-gray-600">{new Date().toLocaleTimeString()}</div>
                  </td>
                  <td className="py-4 px-4 last:pr-0 text-right">
                    <button className="p-2 rounded-lg bg-white/[0.03] border border-white/[0.05] hover:bg-white hover:text-black transition-all group/btn shadow-sm">
                      <RotateCcw className="w-3.5 h-3.5 group-hover/btn:rotate-180 transition-transform duration-500" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="mt-6 pt-4 border-t border-white/[0.05] text-center">
            <button className="text-xs font-semibold uppercase tracking-widest text-gray-500 hover:text-white transition-colors flex items-center gap-2 mx-auto">
              View All Failure Records
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function UsersTab({ users, search, setSearch, actionLoading, onAction }: {
  users: User[]; search: string; setSearch: (s: string) => void;
  actionLoading: string | null; onAction: (id: string, a: "suspend" | "reactivate" | "delete") => void;
}) {
  return (
    <div className="space-y-6">
      <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[16px] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div className="flex items-center gap-3">
            <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400">User Management</h3>
            <span className="px-2 py-0.5 rounded-full bg-white/[0.03] border border-white/10 text-[10px] font-black text-emerald-400 uppercase tracking-widest">
              {users.length} Users
            </span>
          </div>
          <div className="relative max-w-sm w-full group">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 group-hover:text-white transition-colors" />
            <input
              type="text" placeholder="Search by name, email, or App ID..." value={search} onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-11 pr-4 py-2.5 bg-[#202024] border border-white/10 rounded-xl text-sm focus:outline-none focus:border-white/20 transition-all placeholder:text-gray-700 font-medium"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-white/[0.05] text-[10px] font-bold uppercase tracking-widest text-gray-500">
                <th className="py-3 px-4 first:pl-0">User Identity</th>
                <th className="py-3 px-4">Access Level</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Usage</th>
                <th className="py-3 px-4">Consumption</th>
                <th className="py-3 px-4">Registered</th>
                <th className="py-3 px-4 last:pr-0 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.03]">
              {users.map(user => (
                <tr key={user.id} className="hover:bg-white/[0.02] transition-colors group">
                  <td className="py-4 px-4 first:pl-0">
                    <div className="font-semibold text-white text-[13px]">{user.full_name || "System User"}</div>
                    <div className="text-[11px] font-medium text-gray-600 tracking-tight">{user.email}</div>
                  </td>
                  <td className="py-4 px-4">
                    <span className={`px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-[0.1em] border ${user.is_superuser
                        ? 'bg-white text-black border-white'
                        : 'bg-zinc-900 text-white border-white/20'
                      }`}>
                      {user.is_superuser ? 'admin' : 'user'}
                    </span>
                    <div className="text-[9px] font-bold text-gray-600 uppercase mt-1 tracking-widest">
                      {user.plan || 'no active plan'}
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <span className={`flex items-center gap-1.5 text-[10px] font-black uppercase tracking-widest ${user.is_active ? 'text-white' : 'text-gray-600'}`}>
                      <div className={`w-1.5 h-1.5 rounded-full ${user.is_active ? 'bg-emerald-400 shadow-[0_0_5px_#34d399]' : 'bg-red-400 shadow-[0_0_5px_#f87171]'}`} />
                      {user.is_active ? 'Active' : 'Suspended'}
                    </span>
                  </td>
                  <td className="py-4 px-4">
                    <div className="text-[12px] font-bold text-white leading-none">{user.applications_count}</div>
                    <div className="text-[9px] font-bold text-gray-600 uppercase mt-1">Apps</div>
                  </td>
                  <td className="py-4 px-4">
                    <div className="space-y-1.5">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-1 bg-white/[0.03] rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-400"
                            style={{ width: `${user.ai_credits_limit > 0 ? Math.min(100, (user.ai_credits_used / user.ai_credits_limit) * 100) : 0}%` }}
                          />
                        </div>
                        <div className="text-[10px] font-black text-white/90 tabular-nums">
                          {user.ai_credits_used ?? 0}
                          <span className="text-gray-600 mx-0.5">/</span>
                          {(user.ai_credits_limit ?? 0) > 0 ? user.ai_credits_limit : "-"}
                        </div>
                      </div>
                      <div className="flex items-center gap-1.5 grayscale opacity-50 group-hover:grayscale-0 group-hover:opacity-100 transition-all">
                        <div className="text-[9px] font-black uppercase tracking-widest text-gray-500">Tokens:</div>
                        <div className="text-[10px] font-bold text-white">{((user.total_tokens || 0) / 1000).toFixed(1)}k</div>
                      </div>
                    </div>
                  </td>
                  <td className="py-4 px-4 text-[11px] font-medium text-gray-500">{new Date(user.created_at).toLocaleDateString()}</td>
                  <td className="py-4 px-4 last:pr-0 text-right">
                    <div className="flex justify-end gap-1.5">
                      {user.is_active ? (
                        <button onClick={() => onAction(user.id, 'suspend')} disabled={actionLoading === user.id} className="p-2 bg-white/[0.03] border border-white/[0.05] rounded-lg hover:bg-white hover:text-black transition-all group/btn" title="Suspend">
                          <Pause className="w-3.5 h-3.5" />
                        </button>
                      ) : (
                        <button onClick={() => onAction(user.id, 'reactivate')} disabled={actionLoading === user.id} className="p-2 bg-emerald-400/10 border border-emerald-400/20 text-emerald-400 rounded-lg hover:bg-emerald-400 hover:text-black transition-all group/btn" title="Reactivate">
                          <Play className="w-3.5 h-3.5" />
                        </button>
                      )}
                      <button onClick={() => onAction(user.id, 'delete')} disabled={actionLoading === user.id} className="p-2 bg-red-400/10 border border-red-400/20 text-red-400 rounded-lg hover:bg-red-400 hover:text-black transition-all group/btn" title="Delete">
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function SubscriptionsTab({ subscriptions }: { subscriptions: Subscription[] }) {
  return (
    <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[16px] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
      <div className="flex items-center gap-3 mb-6 px-1">
        <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400">Active Subscriptions</h3>
        <span className="px-2 py-0.5 rounded-full bg-white/[0.03] border border-white/10 text-[10px] font-black text-emerald-400 uppercase tracking-widest">
          {subscriptions.length} Plans
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-white/[0.05] text-[10px] font-bold uppercase tracking-widest text-gray-500">
              <th className="py-3 px-4 first:pl-0">User Reference</th>
              <th className="py-3 px-4">Service Plan</th>
              <th className="py-3 px-4">Operational Status</th>
              <th className="py-3 px-4">Throughput Limit</th>
              <th className="py-3 px-4">Start Date</th>
              <th className="py-3 px-4 last:pr-0">Expiry Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.03]">
            {subscriptions.map(sub => (
              <tr key={sub.id} className="hover:bg-white/[0.02] transition-colors group">
                <td className="py-4 px-4 first:pl-0 text-[13px] font-semibold text-white/90">{sub.user_email}</td>
                <td className="py-4 px-4">
                  <span className={`px-2.5 py-1 rounded-[4px] text-[10px] font-black uppercase tracking-widest shadow-sm ${sub.plan === 'premium' ? 'bg-white text-black border border-white' :
                      sub.plan === 'pro' ? 'bg-zinc-900 text-white border border-white/20' :
                        'bg-[#202024] text-gray-500 border border-white/[0.05]'
                    }`}>
                    {sub.plan}
                  </span>
                </td>
                <td className="py-4 px-4">
                  <span className={`flex items-center gap-1.5 text-[10px] font-black uppercase tracking-widest ${sub.status === 'active' ? 'text-emerald-400' : 'text-gray-600'}`}>
                    <div className={`w-1 h-1 rounded-full ${sub.status === 'active' ? 'bg-emerald-400 animate-pulse' : 'bg-gray-800'}`} />
                    {sub.status}
                  </span>
                </td>
                <td className="py-4 px-4">
                  <div className="text-[12px] font-bold text-white">{sub.daily_limit}</div>
                  <div className="text-[9px] font-bold text-gray-600 uppercase">Requests/Day</div>
                </td>
                <td className="py-4 px-4 text-[11px] font-medium text-gray-600">{new Date(sub.start_date).toLocaleDateString()}</td>
                <td className="py-4 px-4 last:pr-0 text-[11px] font-medium text-gray-600 italic">{sub.end_date ? new Date(sub.end_date).toLocaleDateString() : 'Continuous'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function PaymentsTab({ payments }: { payments: Payment[] }) {
  const [search, setSearch] = useState("");
  const formatCurrency = (amount: number) => new Intl.NumberFormat('en-IN', {
    style: 'currency', currency: 'INR', minimumFractionDigits: 0
  }).format(amount / 100);

  const filteredPayments = payments.filter((payment) => {
    const query = search.trim().toLowerCase();
    if (!query) return true;
    return [
      payment.user_email,
      payment.id,
      payment.plan || "",
      payment.status,
      payment.razorpay_payment_id || "",
      payment.razorpay_order_id || "",
    ].some((value) => String(value).toLowerCase().includes(query));
  });

  return (
    <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[16px] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
      <div className="flex items-center justify-between gap-4 mb-6 px-1">
        <div className="flex items-center gap-3">
          <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400">Payment History</h3>
          <span className="px-2 py-0.5 rounded-full bg-white/[0.03] border border-white/10 text-[10px] font-black text-emerald-400 uppercase tracking-widest">
            {payments.length} Payments
          </span>
        </div>
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by email, transaction, status..."
          className="w-full max-w-sm rounded-xl border border-white/[0.08] bg-[#202024] px-4 py-2 text-sm text-white placeholder:text-gray-600 outline-none focus:border-white/20"
        />
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-white/[0.05] text-[10px] font-bold uppercase tracking-widest text-gray-500">
              <th className="py-3 px-4 first:pl-0">Transactional Identity</th>
              <th className="py-3 px-4">Amount</th>
              <th className="py-3 px-4">Processing Result</th>
              <th className="py-3 px-4 last:pr-0 text-right">Settled Timestamp</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.03]">
            {filteredPayments.map(payment => (
              <tr key={payment.id} className="hover:bg-white/[0.02] transition-colors group">
                <td className="py-4 px-4 first:pl-0">
                  <div className="text-[13px] font-semibold text-white/90">{payment.user_email}</div>
                  <div className="text-[10px] font-bold text-gray-700 uppercase leading-none mt-1">Transaction ID: {payment.razorpay_payment_id || payment.razorpay_order_id || payment.id}</div>
                </td>
                <td className="py-4 px-4">
                  <div className="text-[13px] font-black text-white">{formatCurrency(payment.amount)}</div>
                </td>
                <td className="py-4 px-4">
                  <span className={`px-2.5 py-1 rounded text-[10px] font-black uppercase tracking-widest border transition-all ${['captured', 'success'].includes(payment.status.toLowerCase()) ? 'bg-emerald-400 text-black border-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.3)]' :
                      payment.status.toLowerCase() === 'failed' ? 'bg-red-400/10 text-red-400 border-red-400/20' :
                        'bg-[#202024] text-gray-400 border-white/[0.05]'
                    }`}>
                    {payment.status}
                  </span>
                </td>
                <td className="py-4 px-4 last:pr-0 text-right text-[11px] font-medium text-gray-600 italic">
                  {new Date(payment.created_at).toLocaleString()}
                </td>
              </tr>
            ))}
            {filteredPayments.length === 0 && (
              <tr>
                <td className="py-10 px-4 text-center text-sm text-gray-500" colSpan={4}>
                  No payment records match your search.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function BotTab({ stats }: { stats: BotStats | null }) {
  if (!stats) return <div className="p-12 text-center text-gray-600 font-medium italic">Establishing bot telemetry...</div>;

  const metrics = [
    { label: "Today's Volume", value: stats.applications_today, sub: "Total processed", color: "text-white" },
    { label: "Execution Success", value: `${stats.success_rate}%`, sub: "Accuracy rating", color: "text-emerald-400" },
    { label: "Failure Events", value: stats.failed, sub: "Requires review", color: "text-red-400" },
    { label: "Backlog Size", value: stats.queue_size, sub: "In processing", color: "text-amber-400" },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map(m => (
          <div key={m.label} className="bg-[#111118] border border-[#262626] rounded-[16px] p-6 space-y-1">
            <div className={`text-[28px] font-black tracking-tighter leading-none ${m.color}`}>{m.value}</div>
            <div className="text-[11px] font-bold text-gray-500 uppercase tracking-widest">{m.label}</div>
            <div className="text-[10px] font-bold text-gray-600 italic mt-1">{m.sub}</div>
          </div>
        ))}
      </div>

      <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[16px] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
        <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400 mb-6">Bot System Status</h3>
        <div className="flex items-center justify-between p-4 bg-[#111118] border border-[#262626] rounded-xl">
          <div className="flex items-center gap-3">
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 shadow-[0_0_10px_#34d399] animate-pulse" />
            <div className="text-sm font-black uppercase tracking-widest text-white">Agent Online</div>
          </div>
          <div className="text-[11px] font-bold text-gray-600 italic">Connected to core cluster</div>
        </div>
      </div>
    </div>
  );
}

function QueueTab({ stats }: { stats: QueueStats | null }) {
  if (!stats) return <div className="p-12 text-center text-gray-600 font-medium italic">Querying queue controller...</div>;

  const qMetrics = [
    { label: "Pending Tasks", val: stats.pending, icon: Clock, col: "text-white" },
    { label: "In Progress", val: stats.processing || 0, icon: Play, col: "text-blue-400" },
    { label: "Failure Log", val: stats.failed, icon: AlertCircle, col: "text-red-400" },
    { label: "Operational Registry", val: stats.total_scraped || 0, icon: Save, col: "text-emerald-400" },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
        {qMetrics.map(m => (
          <div key={m.label} className="bg-[#111118] border border-[#262626] rounded-[16px] p-6 group hover:border-white/20 transition-all">
            <div className="flex items-start justify-between mb-4">
              <m.icon className="w-5 h-5 text-gray-600 group-hover:text-white transition-colors" />
            </div>
            <div className={`text-[28px] font-semibold tracking-tighter leading-none mb-1 ${m.col}`}>{m.val}</div>
            <div className="text-[11px] font-bold text-gray-500 uppercase tracking-widest">{m.label}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[16px] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
          <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400 mb-6 flex items-center gap-2">
            <Cpu className="w-4 h-4" /> Celery Cluster
          </h3>
          <div className="p-16 bg-[#111118]/70 border border-white/[0.03] rounded-2xl text-center">
            <div className="w-12 h-12 rounded-full bg-white/[0.02] border border-white/5 flex items-center justify-center mx-auto mb-4">
              <Cpu className="w-5 h-5 text-zinc-700" />
            </div>
            <p className="text-[11px] font-black uppercase tracking-[0.2em] text-zinc-600 mb-1">No Active Nodes Located</p>
            <p className="text-[10px] font-bold text-zinc-800 uppercase tracking-widest italic leading-relaxed">Establishing connection to decentralized worker cluster.</p>
          </div>
        </div>

        <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[16px] p-6 text-center flex flex-col items-center justify-center min-h-[200px] shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
          <div className="text-[11px] font-bold text-gray-500 uppercase tracking-[0.2em] mb-4">APScheduler Controller</div>
          <div className="text-[24px] font-black text-white/40 uppercase tracking-tighter mb-4">Stopped</div>
          <div className="w-3 h-3 rounded-full bg-zinc-900 border border-white/10" />
        </div>
      </div>
    </div>
  );
}

function ErrorsTab({ failedJobs, setFailedJobs, loading }: {
  failedJobs: any[];
  setFailedJobs: React.Dispatch<React.SetStateAction<any[]>>;
  loading: boolean;
}) {
  const [retryingId, setRetryingId] = useState<string | null>(null);

  const handleRetry = async (appId: string) => {
    setRetryingId(appId);
    try {
      await api.post(`/admin/queue/retry/${appId}`);
      toast.success("Application queued for retry");
      setFailedJobs(prev => prev.filter(j => j.id !== appId));
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Retry failed");
    } finally {
      setRetryingId(null);
    }
  };

  if (loading && failedJobs.length === 0) {
    return <div className="p-12 text-center text-gray-600 italic">Synchronizing failure registry...</div>;
  }

  return (
    <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[16px] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
      <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400 mb-6 px-1">Critical Failure Registry</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.05] text-[10px] font-bold uppercase tracking-widest text-gray-500">
              <th className="py-3 px-4 first:pl-0">Bot Process</th>
              <th className="py-3 px-4">Entity</th>
              <th className="py-3 px-4">Failure Signature</th>
              <th className="py-3 px-4">Retries</th>
              <th className="py-3 px-4">Timestamp</th>
              <th className="py-3 px-4 last:pr-0 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.03]">
            {failedJobs.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-16 text-center bg-[#111118]/70">
                  <div className="w-12 h-12 rounded-full bg-white/[0.02] border border-white/5 flex items-center justify-center mx-auto mb-4">
                    <CheckCircle2 className="w-5 h-5 text-emerald-500/30" />
                  </div>
                  <p className="text-[11px] font-black uppercase tracking-[0.2em] text-zinc-600 mb-1">Critical Registry Clear</p>
                  <p className="text-[10px] font-bold text-zinc-800 uppercase tracking-widest italic leading-relaxed">No high-intensity failure events detected in current operational cycle.</p>
                </td>
              </tr>
            ) : failedJobs.map(job => (
              <tr key={job.id} className="hover:bg-white/[0.02] transition-colors group">
                <td className="py-4 px-4 first:pl-0">
                  <div className="text-[13px] font-semibold text-white">{job.job_title}</div>
                </td>
                <td className="py-4 px-4 text-[12px] font-medium text-gray-400 italic font-medium">{job.company}</td>
                <td className="py-4 px-4">
                  <span className="text-[11px] font-medium text-red-400/80 bg-red-400/[0.03] border border-red-400/10 px-2.5 py-1 rounded inline-block max-w-[250px] truncate leading-none">
                    {job.error || 'Unknown Exception'}
                  </span>
                </td>
                <td className="py-4 px-4 text-[12px] font-bold text-gray-500">{job.retry_count}</td>
                <td className="py-4 px-4 text-[11px] font-medium text-gray-600">{job.updated_at ? new Date(job.updated_at).toLocaleDateString() : '-'}</td>
                <td className="py-4 px-4 last:pr-0 text-right">
                  <button
                    onClick={() => handleRetry(job.id)}
                    disabled={retryingId === job.id}
                    className="p-2.5 bg-white/[0.03] border border-white/[0.05] rounded-xl hover:bg-white hover:text-black transition-all group/btn"
                    title="Retry"
                  >
                    <RotateCcw className={`w-3.5 h-4 ${retryingId === job.id ? 'animate-spin' : ''}`} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function SettingsTab({ health, onAction, loading }: { health: SystemHealth | null; onAction: (a: string) => void; loading: boolean }) {
  return (
    <div className="space-y-6">
      <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[16px] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
        <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400 mb-8 flex items-center gap-2">
          <Settings2 className="w-4 h-4" /> Platform Configuration
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="flex items-center justify-between p-4 bg-[#111118] border border-[#262626] rounded-xl group hover:border-white/10 transition-all">
            <div>
              <div className="text-[13px] font-black text-white uppercase tracking-widest leading-none mb-1">Maintenance Mode</div>
              <div className="text-[10px] font-bold text-gray-600 italic">Temporarily disable public access</div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[9px] font-black text-gray-700 uppercase tracking-widest">Disabled</span>
              <div className="w-9 h-4.5 rounded-full bg-zinc-900 border border-white/5 relative flex items-center px-1">
                <div className="w-2.5 h-2.5 rounded-full bg-zinc-700" />
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between p-4 bg-[#111118] border border-[#262626] rounded-xl group hover:border-white/10 transition-all">
            <div>
              <div className="text-[13px] font-black text-white uppercase tracking-widest leading-none mb-1">Advanced Logging</div>
              <div className="text-[10px] font-bold text-gray-600 italic">Enable verbose telemetry stream</div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[9px] font-black text-white uppercase tracking-widest">Enabled</span>
              <div className="w-9 h-4.5 rounded-full bg-white/10 border border-white/10 relative flex items-center justify-end px-1">
                <div className="w-2.5 h-2.5 rounded-full bg-white shadow-[0_0_8px_white]" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[16px] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
        <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400 mb-8 flex items-center gap-2">
          <Share2 className="w-4 h-4" /> External Integrations
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="p-5 bg-[#111118] border border-[#262626] rounded-2xl space-y-3 group hover:border-white/20 transition-all">
            <div className="text-[13px] font-black text-white uppercase tracking-widest leading-none">Razorpay Gateway</div>
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399]" />
              <span className="text-[10px] font-black uppercase tracking-widest text-emerald-400">Connected</span>
            </div>
            <div className="text-[10px] font-bold text-gray-700 italic">Live production environment</div>
          </div>

          <div className="p-5 bg-[#111118] border border-[#262626] rounded-2xl space-y-3 group hover:border-white/20 transition-all">
            <div className="text-[13px] font-black text-white uppercase tracking-widest leading-none">OpenAI API</div>
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399]" />
              <span className="text-[10px] font-black uppercase tracking-widest text-emerald-400">Connected</span>
            </div>
            <div className="text-[10px] font-bold text-gray-700 italic">Gpt-4-turbo orchestration</div>
          </div>

          <div className="p-5 bg-[#111118] border border-[#262626] rounded-2xl space-y-3 group hover:border-white/20 transition-all opacity-40">
            <div className="text-[13px] font-black text-white/50 uppercase tracking-widest leading-none">Stripe Sync</div>
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-gray-800" />
              <span className="text-[10px] font-black uppercase tracking-widest text-gray-600">Standby</span>
            </div>
            <div className="text-[10px] font-bold text-gray-800 italic">Awaiting credentials</div>
          </div>

          <div className="p-5 bg-[#111118] border border-[#262626] rounded-2xl space-y-3 group hover:border-white/20 transition-all opacity-40">
            <div className="text-[13px] font-black text-white/50 uppercase tracking-widest leading-none">Redis Cluster</div>
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-gray-800" />
              <span className="text-[10px] font-black uppercase tracking-widest text-gray-600">Standby</span>
            </div>
            <div className="text-[10px] font-bold text-gray-800 italic">Caching layer pending</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ApplicationsTab({ applications }: { applications: Application[] }) {
  return (
    <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[16px] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
      <div className="flex items-center gap-3 mb-6 px-1">
        <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400">Application Registry</h3>
        <span className="px-2 py-0.5 rounded-full bg-white/[0.03] border border-white/10 text-[10px] font-black text-emerald-400 uppercase tracking-widest">
          {applications.length} Records
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.05] text-[10px] font-bold uppercase tracking-widest text-gray-500">
              <th className="py-3 px-4 first:pl-0">Applicant Identity</th>
              <th className="py-3 px-4">Target Role</th>
              <th className="py-3 px-4">Organization</th>
              <th className="py-3 px-4 text-center">Outcome</th>
              <th className="py-3 px-4">Log</th>
              <th className="py-3 px-4 last:pr-0 text-right">Settled</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.03]">
            {applications.map(app => (
              <tr key={app.id} className="hover:bg-white/[0.02] transition-colors group">
                <td className="py-4 px-4 first:pl-0">
                  <div className="text-[13px] font-semibold text-white leading-none">{app.user_email}</div>
                </td>
                <td className="py-4 px-4">
                  <div className="text-[12px] font-bold text-gray-300">{app.job_title}</div>
                </td>
                <td className="py-4 px-4">
                  <div className="text-[12px] text-gray-500 font-medium italic">{app.company}</div>
                </td>
                <td className="py-4 px-4 text-center">
                  <span className={`px-2.5 py-1 rounded-[4px] text-[10px] font-black uppercase tracking-widest ${[
                      'success', 'applied', 'viewed', 'shortlisted',
                      'interview_scheduled', 'interview_completed',
                      'offer_received', 'offer_accepted'
                    ].includes(app.status.toLowerCase()) ? 'bg-emerald-400 text-black shadow-[0_0_10px_rgba(52,211,153,0.3)]' :
                      ['failed', 'rejected'].includes(app.status.toLowerCase()) ? 'bg-red-400/20 text-red-400 border border-red-400/30' :
                        'bg-zinc-800 text-gray-500'
                    }`}>
                    {app.status}
                  </span>
                </td>
                <td className="py-4 px-4">
                  <div className="text-[11px] font-medium text-red-400/80 max-w-[200px] truncate italic bg-red-400/[0.02] px-2 py-0.5 rounded">
                    {app.error || '-'}
                  </div>
                </td>
                <td className="py-4 px-4 last:pr-0 text-right text-[11px] font-medium text-gray-600">
                  {new Date(app.created_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function JobsTab({ jobs }: { jobs: Job[] }) {
  return (
    <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[16px] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
      <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400 mb-6 px-1">Job Discovery Index</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-white/[0.05] text-[10px] font-bold uppercase tracking-widest text-gray-500">
              <th className="py-3 px-4 first:pl-0">Position Identity</th>
              <th className="py-3 px-4">Organization</th>
              <th className="py-3 px-4">Source Origin</th>
              <th className="py-3 px-4">Discovery Status</th>
              <th className="py-3 px-4 last:pr-0 text-right">Discovered</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.03]">
            {jobs.map(job => (
              <tr key={job.id} className="hover:bg-white/[0.02] transition-colors group">
                <td className="py-4 px-4 first:pl-0 text-[13px] font-semibold text-white/90">{job.title}</td>
                <td className="py-4 px-4 text-[12px] font-medium text-gray-400 italic">{job.company}</td>
                <td className="py-4 px-4">
                  <span className="text-[10px] font-black uppercase tracking-tighter text-gray-600 bg-white/[0.03] px-2 py-0.5 rounded border border-white/[0.05]">{job.source}</span>
                </td>
                <td className="py-4 px-4">
                  <span className={`px-2 py-1 rounded-[4px] text-[9px] font-black uppercase tracking-widest ${job.status === 'active' ? 'bg-white text-black' : 'bg-zinc-900 text-gray-600'}`}>
                    {job.status}
                  </span>
                </td>
                <td className="py-4 px-4 last:pr-0 text-right text-[11px] font-medium text-gray-600">
                  {new Date(job.scraped_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function AnalyticsTab({ data }: { data: AnalyticsData | null }) {
  if (!data) return <div className="p-12 text-center text-gray-600 font-medium italic">Establishing analytics telemetry...</div>;

  const maxApp = Math.max(...data.applications_by_day.map(d => d.count), 1);
  const maxRev = Math.max(...data.revenue_by_day.map(d => d.amount), 1);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[16px] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
        <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400 mb-8 px-1">Applications (Last 7 Days)</h3>
        <div className="space-y-6">
          {data.applications_by_day.slice(-7).map(d => (
            <div key={d.date} className="flex items-center gap-4 group">
              <span className="text-[10px] font-black text-gray-500 w-24 uppercase tracking-tighter group-hover:text-white transition-colors">{d.date}</span>
              <div className="flex-1 h-2 bg-[#111118] rounded-full overflow-hidden border border-white/[0.03]">
                <div className="h-full bg-white shadow-[0_0_10px_white] transition-all duration-1000" style={{ width: `${(d.count / maxApp) * 100}%` }}></div>
              </div>
              <span className="text-[11px] font-black text-white w-8">{d.count}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[16px] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
        <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400 mb-8 px-1">Revenue Stream (Last 7 Days)</h3>
        <div className="space-y-6">
          {data.revenue_by_day.slice(-7).map(d => (
            <div key={d.date} className="flex items-center gap-4 group">
              <span className="text-[10px] font-black text-gray-500 w-24 uppercase tracking-tighter group-hover:text-white transition-colors">{d.date}</span>
              <div className="flex-1 h-2 bg-[#111118] rounded-full overflow-hidden border border-white/[0.03]">
                <div className="h-full bg-emerald-400 shadow-[0_0_10px_#34d399] transition-all duration-1000" style={{ width: `${(d.amount / maxRev) * 100}%` }}></div>
              </div>
              <span className="text-[11px] font-black text-white w-16">₹{d.amount}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function FeaturesTab({ flags }: { flags: FeatureFlag[] }) {
  const defaultFlags: FeatureFlag[] = [
    { key: "auto_apply", label: "Auto Apply", description: "Automatically apply to matching jobs", enabled: true },
    { key: "ai_chat", label: "AI Chat", description: "AI-powered chat support", enabled: true },
    { key: "payments", label: "Payments", description: "Enable payment system", enabled: true },
    { key: "scraper", label: "Scraper", description: "Enable job scraping", enabled: true },
    { key: "maintenance", label: "Maintenance Mode", description: "Show maintenance page to users", enabled: false },
  ];

  const displayFlags = flags.length > 0 ? flags : defaultFlags;

  return (
    <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[16px] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
      <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400 mb-8 px-1">Infrastructure Control Flags</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {displayFlags.map(flag => (
          <div key={flag.key} className="bg-[#111118] border border-[#262626] rounded-2xl p-6 group hover:border-white/20 transition-all">
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="text-[13px] font-black text-white uppercase tracking-widest mb-1">{flag.label}</div>
                <div className="text-[10px] font-medium text-gray-600 italic leading-tight">{flag.description}</div>
              </div>
              <div className={`w-2.5 h-2.5 rounded-full ${flag.enabled ? 'bg-emerald-400 shadow-[0_0_8px_#34d399]' : 'bg-gray-800'}`}></div>
            </div>
            <div className="flex items-center gap-3">
              <span className={`text-[10px] font-black uppercase tracking-widest px-3 py-1 border rounded-lg transition-all ${flag.enabled ? 'bg-white text-black border-white' : 'bg-transparent text-gray-700 border-white/[0.05]'
                }`}>
                {flag.enabled ? 'Operational' : 'Disabled'}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function AuditTab({ logs }: { logs: AuditLog[] }) {
  return (
    <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[16px] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
      <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400 mb-6 px-1">Infrastructure Audit Trail</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.05] text-[10px] font-bold uppercase tracking-widest text-gray-500">
              <th className="py-3 px-4 first:pl-0">Operator</th>
              <th className="py-3 px-4">Action Event</th>
              <th className="py-3 px-4">Target Resource</th>
              <th className="py-3 px-4">Network Node</th>
              <th className="py-3 px-4 text-center">Result</th>
              <th className="py-3 px-4 last:pr-0 text-right">Timestamp</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.03]">
            {logs.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-16 text-center bg-[#111118]/70">
                  <div className="w-12 h-12 rounded-full bg-white/[0.02] border border-white/5 flex items-center justify-center mx-auto mb-4">
                    <History className="w-5 h-5 text-zinc-700" />
                  </div>
                  <p className="text-[11px] font-black uppercase tracking-[0.2em] text-zinc-600 mb-1">Audit Registry Empty</p>
                  <p className="text-[10px] font-bold text-zinc-800 uppercase tracking-widest italic leading-relaxed">No administrative activity logged within the current settlement window.</p>
                </td>
              </tr>
            ) : logs.map(log => (
              <tr key={log.id} className="hover:bg-white/[0.02] transition-colors group">
                <td className="py-4 px-4 first:pl-0">
                  <div className="text-[12px] font-semibold text-white leading-none">{log.admin_email}</div>
                </td>
                <td className="py-4 px-4">
                  <div className="text-[11px] font-black uppercase tracking-tighter text-gray-300">{log.action}</div>
                </td>
                <td className="py-4 px-4 text-[12px] text-gray-500 font-medium">{log.target}</td>
                <td className="py-4 px-4 text-[10px] font-bold text-gray-700 font-mono tracking-tight">{log.ip_address}</td>
                <td className="py-4 px-4 text-center">
                  <span className={`px-2 py-0.5 rounded-[4px] text-[9px] font-black uppercase tracking-widest border transition-all ${log.result === 'success' ? 'bg-emerald-400/10 text-emerald-400 border-emerald-400/20' :
                      'bg-red-400/10 text-red-400 border-red-400/20'
                    }`}>
                    {log.result}
                  </span>
                </td>
                <td className="py-4 px-4 last:pr-0 text-right text-[11px] font-medium text-gray-600 whitespace-nowrap">
                  {new Date(log.created_at).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function MessagesTab({ messages }: { messages: any[] }) {
  const importantMessages = messages.filter(m => m.is_important);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-[#111118] border border-[#262626] rounded-[16px] p-6 space-y-1 group hover:border-white/20 transition-all">
          <div className="text-[28px] font-black text-white tracking-tighter leading-none group-hover:scale-105 transition-transform">{messages.length}</div>
          <div className="text-[11px] font-bold text-gray-500 uppercase tracking-widest">Message Volume</div>
          <div className="text-[10px] font-bold text-gray-600 italic mt-1">Total aggregated records</div>
        </div>
        <div className="bg-[#111118] border border-[#262626] rounded-[16px] p-6 space-y-1 group hover:border-white/20 transition-all">
          <div className="text-[28px] font-black text-amber-400 tracking-tighter leading-none group-hover:scale-105 transition-transform">{importantMessages.length}</div>
          <div className="text-[11px] font-bold text-gray-500 uppercase tracking-widest">Critical Intensity</div>
          <div className="text-[10px] font-bold text-gray-600 italic mt-1">High priority events</div>
        </div>
        <div className="bg-[#111118] border border-[#262626] rounded-[16px] p-6 space-y-1 group hover:border-white/20 transition-all">
          <div className="text-[28px] font-black text-blue-400 tracking-tighter leading-none group-hover:scale-105 transition-transform">
            {new Set(messages.map(m => m.platform)).size}
          </div>
          <div className="text-[11px] font-bold text-gray-500 uppercase tracking-widest">Source Channels</div>
          <div className="text-[10px] font-bold text-gray-600 italic mt-1">Active platform nodes</div>
        </div>
      </div>

      <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[16px] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
        <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400 mb-6 px-1">Communication Telemetry</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-white/[0.05] text-[10px] font-bold uppercase tracking-widest text-gray-500">
                <th className="py-3 px-4 first:pl-0">Network Hub</th>
                <th className="py-3 px-4">Origin Sender</th>
                <th className="py-3 px-4">Subject Vector</th>
                <th className="py-3 px-4">Priority Status</th>
                <th className="py-3 px-4 last:pr-0 text-right">Settled Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.03]">
              {messages.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-16 text-center bg-[#111118]/70">
                    <div className="w-12 h-12 rounded-full bg-white/[0.02] border border-white/5 flex items-center justify-center mx-auto mb-4">
                      <Globe className="w-5 h-5 text-zinc-700" />
                    </div>
                    <p className="text-[11px] font-black uppercase tracking-[0.2em] text-zinc-600 mb-1">Communication Log / Zero Records</p>
                    <p className="text-[10px] font-bold text-zinc-800 uppercase tracking-widest italic leading-relaxed">Awaiting telemetry from external communication channels.</p>
                  </td>
                </tr>
              ) : messages.map(msg => (
                <tr key={msg.id} className="hover:bg-white/[0.02] transition-colors group">
                  <td className="py-4 px-4 first:pl-0">
                    <span className="px-2.5 py-0.5 rounded-[4px] text-[10px] font-black uppercase tracking-widest border border-white/5 bg-white/[0.03] text-gray-400">
                      {msg.platform}
                    </span>
                  </td>
                  <td className="py-4 px-4 text-[13px] font-semibold text-white/90">{msg.sender || '-'}</td>
                  <td className="py-4 px-4 text-[12px] font-medium text-gray-500 max-w-[200px] truncate italic">{msg.subject || '-'}</td>
                  <td className="py-4 px-4">
                    {msg.is_important ? (
                      <span className="px-2.5 py-1 rounded-[4px] text-[10px] font-black uppercase tracking-widest bg-amber-400/10 text-amber-400 border border-amber-400/20 shadow-[0_0_10px_rgba(251,191,36,0.1)]">Priority</span>
                    ) : (
                      <span className="text-[10px] font-black uppercase tracking-widest text-gray-800">Routine</span>
                    )}
                  </td>
                  <td className="py-4 px-4 last:pr-0 text-right text-[11px] font-medium text-gray-600 whitespace-nowrap">
                    {msg.created_at ? new Date(msg.created_at).toLocaleString() : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
function useQueryAI(range: string) {
  return useQuery({
    queryKey: ["admin-llm-usage-full", range],
    queryFn: async () => {
      const rangeMap: Record<string, string> = { "7d": "7d", "24h": "24h", "30d": "30d" };
      const res = await api.get(`/admin/llm-usage?range=${rangeMap[range] || "7d"}`);
      return res.data;
    },
    staleTime: 60_000,
  });
}

// AIMetricsTab embeds the full AI Observability page inline.
// It self-fetches with its own richer type so it doesn't depend on the
// parent's LLMUsageData shape.

interface AIFullUsage {
  total_requests: number; total_tokens: number;
  total_estimated_cost: number; today_cost: number; week_cost: number; month_cost: number;
  providers: { provider: string; model: string; requests: number; tokens_used: number; prompt_tokens: number; completion_tokens: number; cached_tokens: number; success_rate: number; cost: number; latency_p50: number; latency_p95: number; }[];
  timeline: { date: string; total_requests: number; total_tokens: number; prompt_tokens: number; completion_tokens: number; cached_tokens: number; success_rate: number; total_errors: number; cost: number; latency_avg: number; groq_requests: number; gemini_requests: number; openrouter_requests: number; status_429: number; status_500: number; }[];
  models: { model: string; provider: string; total_requests: number; total_tokens: number; success_rate: number; rate_limit: number; cost: number; latency_p50: number; latency_p95: number; cached_tokens: number; timeline: { date: string; requests: number; prompt_tokens: number; completion_tokens: number; total_tokens: number; errors: number; cost: number; latency: number; }[]; }[];
  overview: { avg_latency_ms: number; cache_hit_rate: number; tps: number; availability: number; p50_latency: number; p95_latency: number; p99_latency: number; rpm: number; peak_rpm: number; error_rate: number; };
  features: { feature: string; tokens: number; requests: number; cost: number; latency_avg: number; }[];
  top_users: { user_email: string; total_tokens: number; requests: number; cost: number; provider: string; last_active: string; }[];
  error_distribution: Record<string, number>;
  provider_credits: { provider: string; current_credit: number; spend_today: number; projected_burn: number; remaining_days: number; }[];
  routing: { preferred_provider: string; fallback_activations: number; provider_switches: number; failed_routes: number; success_rate: number; } | null;
}

const AI_PROVIDER_COLORS: Record<string, string> = { groq: "#f59e0b", gemini: "#3b82f6", openrouter: "#8b5cf6", openai: "#10b981", anthropic: "#ec4899" };
const AI_MODEL_COLORS = ["#ec4899","#8b5cf6","#3b82f6","#10b981","#f59e0b","#ef4444","#06b6d4","#84cc16"];

function AIStatusBadge({ status }: { status: string }) {
  const c: Record<string, string> = { healthy: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20", degraded: "text-amber-400 bg-amber-400/10 border-amber-400/20", down: "text-red-400 bg-red-400/10 border-red-400/20" };
  return <span className={cn("px-2 py-0.5 rounded-full text-[10px] font-bold uppercase border", c[status] || c.down)}>{status}</span>;
}

function AISparkline({ data, color = "#fff" }: { data: number[]; color?: string }) {
  if (data.length < 2) return <div className="w-20 h-6" />;
  const max = Math.max(...data, 1), min = Math.min(...data, 0), range = max - min || 1;
  const points = data.map((v, i) => `${(i / (data.length - 1)) * 80},${24 - ((v - min) / range) * 24}`).join(" ");
  return (
    <svg width={80} height={24} className="overflow-visible">
      <polyline points={points} fill="none" stroke={color} strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round" opacity={0.7} />
      <circle cx={80} cy={24 - ((data[data.length - 1] - min) / range) * 24} r={2.5} fill={color} />
    </svg>
  );
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
function AIMetricsTab({ llmUsage: _ignored }: { llmUsage: LLMUsageData | null }) {
  const [timeRange, setTimeRange] = useState("7d");
  const [activeSubTab, setActiveSubTab] = useState<"overview"|"trends"|"explore"|"models">("overview");
  const [expandedModel, setExpandedModel] = useState<string | null>(null);

  // Self-fetch with richer type
  const { data, isLoading, refetch } = useQueryAI(timeRange);
  const d = data as AIFullUsage | undefined;

  const fmtDate = (v: string) => new Date(v).toLocaleDateString(undefined, { month: "short", day: "numeric" });
  const fmt$ = (n: number | null | undefined, digits = 2) => (n == null || isNaN(n)) ? "--" : `$${n.toFixed(digits)}`;
  const fmtN = (n: number | null | undefined) => (n == null || isNaN(n)) ? "--" : n.toLocaleString();
  const fmtK = (n: number | null | undefined, digits = 1) => (n == null || isNaN(n)) ? "--" : `${(n / 1000).toFixed(digits)}K`;
  const fmtPct = (n: number | null | undefined, digits = 1) => (n == null || isNaN(n)) ? "--" : `${n.toFixed(digits)}%`;
  const fmtMs = (n: number | null | undefined) => (n == null || isNaN(n)) ? "--" : `${Math.round(n)}ms`;
  const fmtSec = (n: number | null | undefined) => (n == null || isNaN(n)) ? "--" : `${(n / 1000).toFixed(1)}s`;

  const timeline = (d?.timeline || []);
  const providers = d?.providers || [];
  const models = d?.models || [];
  const features = d?.features || [];
  const topUsers = d?.top_users || [];
  const routing = d?.routing || null;
  const overview = d?.overview;

  const totalTokens = d?.total_tokens || 0;
  const totalRequests = d?.total_requests || 0;
  const inputTokens = providers.reduce((s, p) => s + p.prompt_tokens, 0);
  const outputTokens = providers.reduce((s, p) => s + p.completion_tokens, 0);
  const cachedTokens = providers.reduce((s, p) => s + p.cached_tokens, 0);

  const sparkReq = timeline.map(t => t.total_requests);
  const sparkTok = timeline.map(t => t.total_tokens);
  const sparkCost = timeline.map(t => t.cost);
  const sparkLatency = timeline.map(t => t.latency_avg);

  const modelRows = [...models].sort((a, b) => b.total_tokens - a.total_tokens);
  const maxTok = Math.max(...modelRows.map(m => m.total_tokens), 1);

  const errorChartData = Object.entries(d?.error_distribution || {}).map(([code, count]) => ({
    code: code === "429" ? "Rate Limit" : code === "500" ? "Server Error" : code === "timeout" ? "Timeout" : `HTTP ${code}`,
    count,
    color: code === "429" ? "#f59e0b" : code === "500" ? "#ef4444" : "#8b5cf6",
  }));

  const tStyle = { backgroundColor: "#111", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "10px", color: "#fff", fontSize: 11 } as const;

  if (isLoading) {
    return (
      <div className="space-y-4 py-4">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <div key={i} className="h-32 bg-white/[0.03] border border-white/[0.05] rounded-2xl animate-pulse" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-0 pb-10">

      {/* ── Sub-header: time range + sub-tabs ── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-6">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Activity</h2>
          <p className="text-xs text-zinc-500 mt-0.5">Real-time AI infrastructure telemetry</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 bg-white/[0.03] border border-white/[0.06] rounded-lg p-0.5">
            {(["24h","7d","30d"] as const).map(r => (
              <button key={r} onClick={() => setTimeRange(r)}
                className={cn("px-3 py-1.5 rounded-md text-[11px] font-semibold transition-all",
                  timeRange === r ? "bg-white text-black" : "text-zinc-500 hover:text-zinc-300")}>
                {r === "24h" ? "Last 24h" : r === "7d" ? "7 Days" : "30 Days"}
              </button>
            ))}
          </div>
          <button onClick={() => refetch()} className="p-2 bg-white/[0.03] border border-white/[0.06] rounded-lg text-zinc-500 hover:text-white transition-colors">
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Sub-tab bar */}
      <div className="flex items-center gap-1 border-b border-white/[0.06] mb-6">
        {([
          { id: "overview", label: "Overview", icon: BarChart3 },
          { id: "trends",   label: "Trends",   icon: TrendingUp },
          { id: "explore",  label: "Explore",  icon: Globe },
          { id: "models",   label: "Models",   icon: Cpu },
        ] as const).map(tab => (
          <button key={tab.id} onClick={() => setActiveSubTab(tab.id as typeof activeSubTab)}
            className={cn("flex items-center gap-1.5 px-4 py-2.5 text-xs font-semibold transition-all border-b-2 -mb-px",
              activeSubTab === tab.id ? "border-white text-white" : "border-transparent text-zinc-500 hover:text-zinc-300")}>
            <tab.icon className="w-3.5 h-3.5" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* ── OVERVIEW ── */}
      {activeSubTab === "overview" && (
        <div className="space-y-5">

          {/* 4 stat cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: "Total spend",    value: fmt$(d?.today_cost),                sub: `7d: ${fmt$(d?.week_cost)} · 30d: ${fmt$(d?.month_cost)}`,  data: sparkCost,    color: "#10b981" },
              { label: "Requests",       value: fmtN(totalRequests),                sub: `RPM: ${fmtN(overview?.rpm)} · Peak: ${fmtN(overview?.peak_rpm)}`, data: sparkReq,     color: "#8b5cf6" },
              { label: "Token volume",   value: fmtK(totalTokens),                  sub: `In: ${fmtK(inputTokens, 0)} · Out: ${fmtK(outputTokens, 0)}`, data: sparkTok,     color: "#3b82f6" },
              { label: "Cache hit rate", value: fmtPct(overview?.cache_hit_rate),   sub: `${fmtK(cachedTokens, 0)} cached`,                              data: timeline.map(t => t.cached_tokens), color: "#f59e0b" },
            ].map((card, i) => (
              <div key={card.label} className="bg-[#111]/70 border border-white/[0.06] rounded-2xl p-5 hover:border-white/[0.12] transition-all">
                <p className="text-sm text-zinc-400 font-medium mb-3">{card.label}</p>
                <p className="text-3xl font-bold text-white tabular-nums tracking-tight">{card.value}</p>
                <div className="h-10 my-3">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={card.data.map((v, j) => ({ v, j }))} margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
                      <defs><linearGradient id={`ai-ov-${i}`} x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={card.color} stopOpacity={0.3}/><stop offset="100%" stopColor={card.color} stopOpacity={0}/></linearGradient></defs>
                      <Area type="monotone" dataKey="v" stroke={card.color} strokeWidth={1.5} fill={`url(#ai-ov-${i})`} dot={false} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
                <p className="text-xs text-zinc-600">{card.sub}</p>
              </div>
            ))}
          </div>

          {/* Provider cards + system stats */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-3 gap-4">
              {(providers.length > 0 ? providers : [
                { provider: "openrouter", model: "", requests: 0, tokens_used: 0, prompt_tokens: 0, completion_tokens: 0, cached_tokens: 0, success_rate: 0, cost: 0, latency_p50: 0, latency_p95: 0 },
                { provider: "gemini",     model: "", requests: 0, tokens_used: 0, prompt_tokens: 0, completion_tokens: 0, cached_tokens: 0, success_rate: 0, cost: 0, latency_p50: 0, latency_p95: 0 },
                { provider: "groq",       model: "", requests: 0, tokens_used: 0, prompt_tokens: 0, completion_tokens: 0, cached_tokens: 0, success_rate: 0, cost: 0, latency_p50: 0, latency_p95: 0 },
              ]).slice(0, 3).map((p, i) => {
                const color = AI_PROVIDER_COLORS[p.provider] || "#6b7280";
                const status = p.requests === 0 ? "down" : p.success_rate > 95 ? "healthy" : p.success_rate > 80 ? "degraded" : "down";
                const spark = timeline.map(t => (t[`${p.provider}_requests` as keyof typeof t] as number) || 0);
                return (
                  <div key={p.provider} className="bg-[#111]/70 border border-white/[0.06] rounded-2xl p-5">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full" style={{ background: color }} />
                        <span className="text-sm font-semibold text-white capitalize">{p.provider}</span>
                      </div>
                      <AIStatusBadge status={status} />
                    </div>
                    <div className="grid grid-cols-2 gap-x-4 gap-y-3 mb-4">
                      {[["Requests", fmtN(p.requests)], ["Success", fmtPct(p.success_rate)], ["Latency", fmtSec(p.latency_p50)], ["Cost", fmt$(p.cost)]].map(([l, v]) => (
                        <div key={l}><p className="text-xs text-zinc-500 mb-0.5">{l}</p><p className="text-sm font-bold text-white">{v}</p></div>
                      ))}
                    </div>
                    <div className="flex items-center justify-between">
                      <div><p className="text-xs text-zinc-500 mb-0.5">Tokens</p><p className="text-sm font-semibold text-white">{fmtK(p.tokens_used)}</p></div>
                      <AISparkline data={spark} color={color} />
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="bg-[#111]/70 border border-white/[0.06] rounded-2xl p-5 space-y-4">
              <p className="text-sm font-semibold text-white">System stats</p>
              {[
                { l: "Avg latency",      v: fmtMs(overview?.avg_latency_ms),  sub: `P50: ${fmtMs(overview?.p50_latency)} · P95: ${fmtMs(overview?.p95_latency)}` },
                { l: "Availability",     v: fmtPct(overview?.availability, 2), sub: "Provider uptime" },
                { l: "Est. monthly burn",v: fmt$(d ? d.month_cost * 4 : 0),   sub: "Projected cost" },
                { l: "Active users",     v: fmtN(topUsers.length),             sub: "Consuming AI" },
                ...(routing ? [{ l: "Fallback activations", v: fmtN(routing.fallback_activations), sub: `${routing.provider_switches} switches` }] : []),
              ].map(({ l, v, sub }) => (
                <div key={l} className="flex items-start justify-between gap-2 pb-4 border-b border-white/[0.04] last:border-0 last:pb-0">
                  <div><p className="text-xs text-zinc-400 font-medium">{l}</p>{sub && <p className="text-[10px] text-zinc-600 mt-0.5">{sub}</p>}</div>
                  <p className="text-sm font-bold text-white tabular-nums">{v}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="bg-[#111]/70 border border-white/[0.06] rounded-2xl p-5">
              <p className="text-sm font-semibold text-white mb-4">Spend over time</p>
              <div className="h-52">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={timeline} margin={{ top: 4, right: 0, left: -28, bottom: 0 }}>
                    <defs>{Object.entries(AI_PROVIDER_COLORS).map(([k, c]) => <linearGradient key={k} id={`ai-sp-${k}`} x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor={c} stopOpacity={0.25}/><stop offset="95%" stopColor={c} stopOpacity={0}/></linearGradient>)}</defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
                    <XAxis dataKey="date" stroke="#3f3f46" fontSize={10} tickLine={false} axisLine={false} tickFormatter={fmtDate} />
                    <YAxis stroke="#3f3f46" fontSize={10} tickLine={false} axisLine={false} tickFormatter={v => `$${v}`} />
                    <Tooltip contentStyle={tStyle} formatter={(v: any) => [fmt$(Number(v)), ""]} />
                    <Legend iconType="circle" wrapperStyle={{ fontSize: 10, paddingTop: 8 }} />
                    {Object.keys(AI_PROVIDER_COLORS).map(p => (
                      <Area key={p} type="monotone" dataKey={`${p}_cost`} name={p} stroke={AI_PROVIDER_COLORS[p]} strokeWidth={1.5} fill={`url(#ai-sp-${p})`} stackId="cost" dot={false} />
                    ))}
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-[#111]/70 border border-white/[0.06] rounded-2xl p-5">
              <div className="flex items-center justify-between mb-4">
                <p className="text-sm font-semibold text-white">Token breakdown</p>
                <div className="flex items-center gap-3 text-xs text-zinc-500">
                  {[["Input","#3b82f6"],["Output","#8b5cf6"],["Cached","#10b981"]].map(([l,c]) => (
                    <span key={l} className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{ background: c }} />{l}</span>
                  ))}
                </div>
              </div>
              <div className="h-52">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={timeline} margin={{ top: 4, right: 0, left: -28, bottom: 0 }} barCategoryGap="25%">
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
                    <XAxis dataKey="date" stroke="#3f3f46" fontSize={10} tickLine={false} axisLine={false} tickFormatter={fmtDate} />
                    <YAxis stroke="#3f3f46" fontSize={10} tickLine={false} axisLine={false} tickFormatter={v => v >= 1000 ? fmtK(v, 0) : v} />
                    <Tooltip contentStyle={tStyle} />
                    <Bar dataKey="prompt_tokens" name="Input" fill="#3b82f6" fillOpacity={0.7} stackId="a" />
                    <Bar dataKey="completion_tokens" name="Output" fill="#8b5cf6" fillOpacity={0.7} stackId="a" />
                    <Bar dataKey="cached_tokens" name="Cached" fill="#10b981" fillOpacity={0.7} radius={[3,3,0,0]} stackId="a" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Top users + features */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div className="lg:col-span-2 bg-[#111]/70 border border-white/[0.06] rounded-2xl overflow-hidden">
              <div className="px-5 py-4 border-b border-white/[0.04]"><p className="text-sm font-semibold text-white">Top users</p><p className="text-xs text-zinc-500 mt-0.5">By token consumption</p></div>
              <table className="w-full">
                <thead><tr className="border-b border-white/[0.04]">
                  {["#","User","Requests","Tokens","Cost","Provider"].map(h => <th key={h} className="px-5 py-3 text-left text-xs font-medium text-zinc-500">{h}</th>)}
                </tr></thead>
                <tbody>
                  {topUsers.length > 0 ? topUsers.slice(0, 8).map((u, i) => (
                    <tr key={u.user_email} className="border-b border-white/[0.03] hover:bg-white/[0.02] transition-colors">
                      <td className="px-5 py-3 text-xs font-bold text-zinc-600">{i+1}</td>
                      <td className="px-5 py-3 text-sm font-medium text-white">{u.user_email}</td>
                      <td className="px-5 py-3 text-sm text-zinc-300 tabular-nums">{fmtN(u.requests)}</td>
                      <td className="px-5 py-3 text-sm text-zinc-300 tabular-nums">{fmtK(u.total_tokens)}</td>
                      <td className="px-5 py-3 text-sm text-zinc-300 tabular-nums">{fmt$(u.cost)}</td>
                      <td className="px-5 py-3"><span className="text-xs px-2 py-0.5 rounded-full border border-white/[0.08] text-zinc-400 capitalize">{u.provider || "--"}</span></td>
                    </tr>
                  )) : <tr><td colSpan={6} className="py-10 text-center text-sm text-zinc-500">No user data yet</td></tr>}
                </tbody>
              </table>
            </div>

            <div className="bg-[#111]/70 border border-white/[0.06] rounded-2xl p-5">
              <p className="text-sm font-semibold text-white mb-1">Feature usage</p>
              <p className="text-xs text-zinc-500 mb-5">Token consumption by feature</p>
              {features.length > 0 ? (
                <div className="space-y-4">
                  {features.map((f, i) => {
                    const maxF = Math.max(...features.map(x => x.tokens), 1);
                    return (
                      <div key={f.feature}>
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="text-xs text-zinc-300 font-medium capitalize">{f.feature}</span>
                          <span className="text-xs text-zinc-500 tabular-nums">{fmtK(f.tokens)}</span>
                        </div>
                        <div className="h-1.5 bg-white/[0.04] rounded-full overflow-hidden">
                          <div className="h-full rounded-full" style={{ width: `${(f.tokens/maxF)*100}%`, background: AI_MODEL_COLORS[i % AI_MODEL_COLORS.length] }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-10 text-zinc-600"><Zap className="w-7 h-7 mb-2" /><p className="text-sm text-zinc-500">No feature data yet</p></div>
              )}
            </div>
          </div>

          {/* Error charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="bg-[#111]/70 border border-white/[0.06] rounded-2xl p-5">
              <p className="text-sm font-semibold text-white mb-1">Error distribution</p>
              <p className="text-xs text-zinc-500 mb-4">By HTTP status code</p>
              <div className="h-44">
                {errorChartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={errorChartData} margin={{ top: 4, right: 0, left: -28, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
                      <XAxis dataKey="code" stroke="#3f3f46" fontSize={10} tickLine={false} axisLine={false} />
                      <YAxis stroke="#3f3f46" fontSize={10} tickLine={false} axisLine={false} />
                      <Tooltip contentStyle={tStyle} />
                      <Bar dataKey="count" radius={[4,4,0,0]} barSize={36}>
                        {errorChartData.map((e, idx) => <Cell key={idx} fill={e.color} fillOpacity={0.75} />)}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center gap-3">
                    <CheckCircle2 className="w-7 h-7 text-emerald-500/40" />
                    <p className="text-sm text-zinc-500">Zero errors detected</p>
                  </div>
                )}
              </div>
            </div>

            <div className="bg-[#111]/70 border border-white/[0.06] rounded-2xl p-5">
              <p className="text-sm font-semibold text-white mb-1">Error timeline</p>
              <p className="text-xs text-zinc-500 mb-4">Error frequency over time</p>
              <div className="h-44">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={timeline} margin={{ top: 4, right: 0, left: -28, bottom: 0 }}>
                    <defs><linearGradient id="ai-err" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#ef4444" stopOpacity={0.25}/><stop offset="95%" stopColor="#ef4444" stopOpacity={0}/></linearGradient></defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
                    <XAxis dataKey="date" stroke="#3f3f46" fontSize={10} tickLine={false} axisLine={false} tickFormatter={fmtDate} />
                    <YAxis stroke="#3f3f46" fontSize={10} tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={tStyle} />
                    <Legend iconType="circle" wrapperStyle={{ fontSize: 10, paddingTop: 8 }} />
                    <Area type="monotone" dataKey="total_errors" name="Errors" stroke="#ef4444" strokeWidth={1.5} fill="url(#ai-err)" dot={false} />
                    <Area type="monotone" dataKey="status_429" name="Rate Limits" stroke="#f59e0b" strokeWidth={1.5} fill="none" dot={false} />
                    <Area type="monotone" dataKey="status_500" name="Server Errors" stroke="#8b5cf6" strokeWidth={1.5} fill="none" dot={false} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── TRENDS ── */}
      {activeSubTab === "trends" && (
        <div className="space-y-5">
          <div className="bg-[#111]/70 border border-white/[0.06] rounded-2xl p-5">
            <p className="text-sm font-semibold text-white mb-4">Request volume by model</p>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={timeline} margin={{ top: 4, right: 0, left: -28, bottom: 0 }} barCategoryGap="25%">
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
                  <XAxis dataKey="date" stroke="#3f3f46" fontSize={10} tickLine={false} axisLine={false} tickFormatter={fmtDate} />
                  <YAxis stroke="#3f3f46" fontSize={10} tickLine={false} axisLine={false} />
                  <Tooltip contentStyle={tStyle} />
                  <Legend iconType="circle" wrapperStyle={{ fontSize: 10, paddingTop: 8 }} />
                  {models.map((m, i) => <Bar key={m.model} dataKey={`model_${m.model}_requests`} name={m.model} fill={AI_MODEL_COLORS[i%AI_MODEL_COLORS.length]} fillOpacity={0.75} radius={[2,2,0,0]} stackId="req" />)}
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {models.slice(0, 4).map((m, i) => (
              <div key={m.model} className="bg-[#111]/70 border border-white/[0.06] rounded-2xl p-4 flex items-center gap-4 hover:border-white/[0.12] transition-all">
                <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: `${AI_MODEL_COLORS[i%AI_MODEL_COLORS.length]}18` }}>
                  <Cpu className="w-4 h-4" style={{ color: AI_MODEL_COLORS[i%AI_MODEL_COLORS.length] }} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-bold text-white truncate">{m.model}</p>
                  <p className="text-xs text-zinc-500">by {m.provider}</p>
                </div>
                <div className="text-right flex-shrink-0">
                  <p className="text-sm font-bold text-emerald-400 flex items-center gap-1"><TrendingUp className="w-3 h-3" />New</p>
                  <p className="text-xs text-zinc-500">{fmtN(m.total_requests)} req</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── EXPLORE ── */}
      {activeSubTab === "explore" && (
        <div className="space-y-5">
          {/* Model table */}
          <div className="bg-[#111]/70 border border-white/[0.06] rounded-2xl overflow-hidden">
            <div className="flex items-center justify-between px-5 py-4 border-b border-white/[0.04]">
              <p className="text-sm font-semibold text-white">Usage by model</p>
              <span className="text-xs text-zinc-500">{modelRows.length} models</span>
            </div>
            {/* mini bar */}
            <div className="px-5 py-4 border-b border-white/[0.04]">
              <div className="flex items-end gap-1 h-14">
                {modelRows.slice(0,8).map((m,i) => {
                  const pct = (m.total_tokens / maxTok) * 100;
                  return <div key={m.model} className="flex-1 flex flex-col justify-end"><div className="rounded-t-sm" style={{ height:`${Math.max(pct,4)}%`, background: AI_MODEL_COLORS[i%AI_MODEL_COLORS.length] }} /></div>;
                })}
              </div>
              <div className="flex items-center gap-4 mt-2 flex-wrap">
                {modelRows.slice(0,5).map((m,i) => (
                  <span key={m.model} className="flex items-center gap-1.5 text-xs text-zinc-400">
                    <span className="w-2 h-2 rounded-full" style={{ background: AI_MODEL_COLORS[i%AI_MODEL_COLORS.length] }} />{m.model}
                  </span>
                ))}
              </div>
            </div>
            <table className="w-full">
              <thead><tr className="border-b border-white/[0.04]">
                {["Model","Requests","Tokens","Success","% of Total"].map((h,i) => <th key={h} className={cn("px-5 py-3 text-xs font-medium text-zinc-500", i>0?"text-right":"text-left")}>{h}</th>)}
              </tr></thead>
              <tbody>
                {modelRows.length > 0 ? modelRows.map((m,i) => {
                  const pct = maxTok > 0 ? (m.total_tokens/maxTok)*100 : 0;
                  const color = AI_MODEL_COLORS[i%AI_MODEL_COLORS.length];
                  return (
                    <tr key={m.model} className="border-b border-white/[0.03] hover:bg-white/[0.02] transition-colors">
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full" style={{ background: color }} /><span className="text-sm font-medium text-white">{m.model}</span><span className="text-xs text-zinc-600 capitalize">{m.provider}</span></div>
                      </td>
                      <td className="px-5 py-3.5 text-right text-sm text-zinc-300 tabular-nums">{fmtN(m.total_requests)}</td>
                      <td className="px-5 py-3.5 text-right text-sm text-zinc-300 tabular-nums">{fmtK(m.total_tokens)}</td>
                      <td className="px-5 py-3.5 text-right text-sm tabular-nums" style={{ color: m.success_rate>=95?"#34d399":m.success_rate>=80?"#fb923c":"#f87171" }}>{fmtPct(m.success_rate)}</td>
                      <td className="px-5 py-3.5">
                        <div className="flex items-center justify-end gap-2">
                          <div className="w-20 h-1.5 bg-white/[0.05] rounded-full overflow-hidden"><div className="h-full rounded-full" style={{ width:`${pct}%`, background: color }} /></div>
                          <span className="text-xs text-zinc-400 tabular-nums w-8 text-right">{pct.toFixed(0)}%</span>
                        </div>
                      </td>
                    </tr>
                  );
                }) : <tr><td colSpan={5} className="py-10 text-center text-sm text-zinc-500">No model data yet</td></tr>}
              </tbody>
            </table>
          </div>

          {/* Cache + prompt caching charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="bg-[#111]/70 border border-white/[0.06] rounded-2xl p-5">
              <p className="text-sm font-semibold text-white mb-4">Prompt token caching</p>
              <div className="h-52">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={timeline} margin={{ top: 4, right: 0, left: -28, bottom: 0 }} barCategoryGap="25%">
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
                    <XAxis dataKey="date" stroke="#3f3f46" fontSize={10} tickLine={false} axisLine={false} tickFormatter={fmtDate} />
                    <YAxis stroke="#3f3f46" fontSize={10} tickLine={false} axisLine={false} tickFormatter={v => v>=1000?fmtK(v,0):v} />
                    <Tooltip contentStyle={tStyle} />
                    <Bar dataKey="prompt_tokens" name="Prompt" fill="#3b82f6" fillOpacity={0.6} radius={[2,2,0,0]} />
                    <Bar dataKey="cached_tokens" name="Cached" fill="#10b981" fillOpacity={0.6} radius={[2,2,0,0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="bg-[#111]/70 border border-white/[0.06] rounded-2xl p-5">
              <p className="text-sm font-semibold text-white mb-4">Usage type over time</p>
              <div className="h-52">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={timeline} margin={{ top: 4, right: 0, left: -28, bottom: 0 }}>
                    <defs><linearGradient id="ai-ut" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/><stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/></linearGradient></defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
                    <XAxis dataKey="date" stroke="#3f3f46" fontSize={10} tickLine={false} axisLine={false} tickFormatter={fmtDate} />
                    <YAxis stroke="#3f3f46" fontSize={10} tickLine={false} axisLine={false} tickFormatter={v => `$${v}`} />
                    <Tooltip contentStyle={tStyle} formatter={(v: any) => [fmt$(Number(v)), ""]} />
                    <Area type="monotone" dataKey="cost" name="Spend" stroke="#8b5cf6" strokeWidth={2} fill="url(#ai-ut)" dot={false} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── MODELS ── */}
      {activeSubTab === "models" && (
        <div className="space-y-3">
          {models.length > 0 ? models.map((model, i) => {
            const isExp = expandedModel === model.model;
            const color = AI_MODEL_COLORS[i % AI_MODEL_COLORS.length];
            const tl = model.timeline.map(t => ({ ...t, label: fmtDate(t.date) }));
            return (
              <div key={model.model} className="bg-[#111]/70 border border-white/[0.06] rounded-2xl overflow-hidden hover:border-white/[0.10] transition-all">
                <button onClick={() => setExpandedModel(isExp ? null : model.model)} className="w-full flex items-center justify-between px-5 py-4 text-left">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full" style={{ background: color }} />
                    <div>
                      <p className="text-base font-bold text-white">{model.model}</p>
                      <p className="text-xs text-zinc-500">by {model.provider}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    {[["requests", fmtN(model.total_requests)], ["tokens", fmtK(model.total_tokens)], ["cost", fmt$(model.cost)], ["success", fmtPct(model.success_rate)], ["latency", fmtSec(model.latency_p50)]].map(([l, v]) => (
                      <div key={l} className="text-right hidden md:block">
                        <p className="text-sm font-bold text-white">{v}</p>
                        <p className="text-[10px] text-zinc-500">{l}</p>
                      </div>
                    ))}
                    {isExp ? <AlertCircle className="w-4 h-4 text-zinc-500 rotate-180" /> : <AlertCircle className="w-4 h-4 text-zinc-500" style={{ transform: "rotate(0deg)" }} />}
                  </div>
                </button>
                {isExp && (
                  <div className="px-5 pb-5 border-t border-white/[0.04]">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
                      {[
                        { title: "Requests over time", key: "requests" as const, color },
                        { title: "Token usage", key: "total_tokens" as const, color: "#3b82f6" },
                      ].map(({ title, key, color: c }) => (
                        <div key={title} className="bg-white/[0.02] border border-white/[0.04] rounded-xl p-4">
                          <p className="text-xs font-semibold text-zinc-400 mb-3">{title}</p>
                          <div className="h-40">
                            <ResponsiveContainer width="100%" height="100%">
                              <AreaChart data={tl} margin={{ top: 4, right: 0, left: -28, bottom: 0 }}>
                                <defs><linearGradient id={`ai-m-${key}-${i}`} x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor={c} stopOpacity={0.2}/><stop offset="95%" stopColor={c} stopOpacity={0}/></linearGradient></defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
                                <XAxis dataKey="label" stroke="#3f3f46" fontSize={9} tickLine={false} axisLine={false} />
                                <YAxis stroke="#3f3f46" fontSize={9} tickLine={false} axisLine={false} tickFormatter={v => v>=1000?fmtK(v,0):v} />
                                <Tooltip contentStyle={tStyle} />
                                <Area type="monotone" dataKey={key} stroke={c} strokeWidth={2} fill={`url(#ai-m-${key}-${i})`} dot={false} />
                              </AreaChart>
                            </ResponsiveContainer>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          }) : (
            <div className="text-center py-16">
              <Cpu className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
              <p className="text-zinc-500">No model data yet</p>
            </div>
          )}
        </div>
      )}

    </div>
  );
}


// ── UTILITY COMPONENTS (EXPANDED) ──────────────────────────────────────────

