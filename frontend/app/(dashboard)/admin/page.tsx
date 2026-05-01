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
            className={`flex items-center gap-2 px-3 py-2 text-[11px] font-black uppercase tracking-widest whitespace-nowrap transition-all border-b-2 ${
              activeTab === tab.id 
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
                    <p className="text-[11px] font-black uppercase tracking-[0.2em] text-zinc-500 mb-1">Zero Failure Events / Operational</p>
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
          <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400">User Management</h3>
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
                    <span className={`px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-[0.1em] border ${
                      user.is_superuser
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
      <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400 mb-6 px-1">Active Subscriptions</h3>
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
                  <span className={`px-2.5 py-1 rounded-[4px] text-[10px] font-black uppercase tracking-widest shadow-sm ${
                    sub.plan === 'premium' ? 'bg-white text-black border border-white' :
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
        <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400">Payment History</h3>
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
                  <span className={`px-2.5 py-1 rounded text-[10px] font-black uppercase tracking-widest border transition-all ${
                    payment.status === 'captured' ? 'bg-emerald-400 text-black border-emerald-400' : 
                    payment.status === 'failed' ? 'bg-red-400/10 text-red-400 border-red-400/20' :
                    'bg-[#202024] text-gray-500 border-white/[0.05]'
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
      <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400 mb-6 px-1">Application Registry</h3>
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
                  <span className={`px-2.5 py-1 rounded-[4px] text-[10px] font-black uppercase tracking-widest ${
                    app.status === 'success' ? 'bg-emerald-400 text-black' : 
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
              <span className={`text-[10px] font-black uppercase tracking-widest px-3 py-1 border rounded-lg transition-all ${
                flag.enabled ? 'bg-white text-black border-white' : 'bg-transparent text-gray-700 border-white/[0.05]'
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
                  <span className={`px-2 py-0.5 rounded-[4px] text-[9px] font-black uppercase tracking-widest border transition-all ${
                    log.result === 'success' ? 'bg-emerald-400/10 text-emerald-400 border-emerald-400/20' : 
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
function AIMetricsTab({ llmUsage }: { llmUsage: LLMUsageData | null }) {
  const [showLimits, setShowLimits] = useState(true);
  const [timeRange, setTimeRange] = useState("Last 7 days");
  const [modelFilter, setModelFilter] = useState("Show all Models");
  
  const usageTimeline = (llmUsage?.timeline || []).map((point) => ({
    ...point,
    label: new Date(point.date).toLocaleDateString(undefined, { month: "short", day: "numeric" }),
    success_rate: Number(point.success_rate.toFixed(1)),
  }));

  const errorData = llmUsage?.error_distribution ? Object.entries(llmUsage.error_distribution).map(([code, count]) => ({
    code: `HTTP ${code}`,
    count,
  })) : [];

  const tooltipStyle = {
    backgroundColor: "#0b0b0f",
    border: "1px solid rgba(255,255,255,0.08)",
    borderRadius: "16px",
    color: "#fff",
    boxShadow: "0 20px 50px rgba(0,0,0,0.35)",
  } as const;

  const overview = llmUsage?.overview;

  return (
    <div className="space-y-10 pb-28">
      {/* 1. TOP CONTROLS */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 px-1">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
             <h1 className="text-3xl font-semibold text-white tracking-tight">Metrics</h1>
          </div>
          
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Show Limits</span>
            <button 
              onClick={() => setShowLimits(!showLimits)}
              className={cn(
                "w-10 h-5 rounded-full transition-all relative flex items-center px-1 border border-white/10",
                showLimits ? "bg-white" : "bg-zinc-800"
              )}
            >
              <div className={cn(
                "w-3 h-3 rounded-full transition-all",
                showLimits ? "bg-black ml-auto" : "bg-zinc-500"
              )} />
            </button>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <button className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/[0.03] border border-white/10 hover:bg-white/5 transition-all">
            <RotateCcw className="w-3 h-3 text-gray-500" />
            <span className="text-xs font-semibold text-white">Refresh</span>
          </button>
          
          <DropdownItem label="Time Range" value={timeRange} />
          <DropdownItem label="Model" value={modelFilter} />
          <DropdownItem label="API Keys" value="Show all API Keys" />
        </div>
      </div>

      {/* 2. SYSTEM KPI GRID (NEW) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 px-1">
        <KPIItem title="Avg Latency" value={`${overview?.avg_latency_ms || 0}ms`} sub="Inference Speed" icon={<Zap className="w-4 h-4" />} />
        <KPIItem title="Cache Rate" value={`${overview?.cache_hit_rate || 0}%`} sub="Cost Efficiency" icon={<Database className="w-4 h-4" />} />
        <KPIItem title="Availability" value={`${overview?.availability || 100}%`} sub="System Uptime" icon={<Shield className="w-4 h-4" />} />
        <KPIItem title="TPS" value={`${overview?.tps || 0}`} sub="Tokens / Sec" icon={<Server className="w-4 h-4" />} />
      </div>

      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 px-1 mt-12">
        <div className="space-y-4">
          <div className="flex items-center gap-3">
             <h2 className="text-2xl font-bold text-white tracking-tight">AI Fleet Intelligence</h2>
             <span className="px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-[10px] font-bold text-gray-400">Live Telemetry</span>
          </div>
          <div className="flex items-center gap-4">
             <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/[0.03] border border-white/10 min-w-[160px]">
                <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Environment</span>
                <span className="text-xs font-semibold text-white">Production Cluster</span>
             </div>
          </div>
        </div>

        <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[24px] p-6 min-w-[300px]">
           <div className="flex items-start justify-between mb-2">
              <span className="text-sm text-gray-400 font-medium">Monthly Burn</span>
              <span className="text-xl font-bold text-white tabular-nums">${llmUsage?.total_estimated_cost?.toFixed(2) || "0.00"}</span>
           </div>
           <p className="text-[10px] text-gray-500 leading-relaxed max-w-[240px]">
              Estimated infrastructure spend based on current token volume and provider rates.
           </p>
        </div>
      </div>

      {/* 3. PRODUCT INTELLIGENCE & CONSUMERS (NEW) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <ChartContainer title="PRODUCT INTELLIGENCE" icon={<Cpu className="w-4 h-4 text-gray-600" />} subtitle="Token consumption by feature (resume analysis, job discovery, chat, auto-apply)">
            <div className="space-y-8 pt-4">
              {(llmUsage?.features || []).map((f, i) => {
                const maxTokens = Math.max(...(llmUsage?.features || []).map(x => x.tokens), 1);
                return (
                  <div key={f.feature} className="space-y-2 group">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-black text-white/40 uppercase tracking-widest group-hover:text-white transition-colors">{f.feature}</span>
                      <span className="text-[11px] font-bold text-white tracking-tighter">{(f.tokens / 1000).toFixed(1)}k TOKENS</span>
                    </div>
                    <div className="h-1.5 bg-white/[0.02] border border-white/[0.05] rounded-full overflow-hidden">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${(f.tokens / maxTokens) * 100}%` }}
                        transition={{ duration: 1, delay: i * 0.1 }}
                        className="h-full bg-white shadow-[0_0_10px_white]"
                      />
                    </div>
                  </div>
                )
              })}
              {(llmUsage?.features || []).length === 0 && (
                 <div className="h-full flex flex-col items-center justify-center py-20 space-y-4">
                    <div className="w-12 h-12 rounded-full bg-white/5 border border-white/10 flex items-center justify-center">
                      <Zap className="w-5 h-5 text-zinc-600" />
                    </div>
                    <div className="text-center space-y-2">
                      <p className="text-sm font-bold text-white/60">No Feature Usage Yet</p>
                      <p className="text-[10px] text-zinc-600 max-w-xs">Usage data will appear when users leverage AI features: resume analysis, job matching, auto-apply, or chat assistance.</p>
                    </div>
                 </div>
              )}
            </div>
          </ChartContainer>
        </div>

        <div className="space-y-6">
          <div className="bg-[#1c1c1e] border border-white/[0.08] rounded-[24px] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)] min-h-full">
            <h4 className="text-sm font-medium text-gray-400 uppercase tracking-widest mb-2 flex items-center gap-2">
               <Users className="w-4 h-4" /> Industrial Consumers
            </h4>
            <p className="text-[10px] text-zinc-600 mb-6">Top users by token consumption</p>
            <div className="space-y-6">
              {(llmUsage?.top_users || []).map((u, i) => (
                <div key={u.user_email} className="flex items-center justify-between group">
                  <div className="space-y-0.5">
                    <div className="text-xs font-bold text-white tabular-nums group-hover:translate-x-1 transition-transform truncate max-w-[180px]">{u.user_email}</div>
                    <div className="text-[9px] font-black text-zinc-600 uppercase tracking-[0.15em]">{u.requests} API CALLS</div>
                  </div>
                  <div className="text-[11px] font-black text-white tabular-nums border border-white/5 bg-white/[0.02] px-2 py-1 rounded-lg">
                    {((u.total_tokens || 0) / 1000).toFixed(1)}k
                  </div>
                </div>
              ))}
              {(llmUsage?.top_users || []).length === 0 && (
                <div className="text-center py-20 space-y-3">
                  <div className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center mx-auto">
                    <Users className="w-4 h-4 text-zinc-600" />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-white/60 mb-1">No Active Users</p>
                    <p className="text-[9px] text-zinc-600">Users will appear here once they start using AI services</p>
                  </div>
                </div>
              )}
            </div>

            <div className="mt-12 pt-6 border-t border-white/[0.04]">
               <button className="w-full py-3 text-[9px] font-black uppercase tracking-[0.3em] text-zinc-500 hover:text-white border border-white/[0.05] hover:border-white/10 rounded-xl transition-all">
                  Full User Ledger
               </button>
            </div>
          </div>
        </div>
      </div>

      {/* 4. OVERVIEW CHARTS */}
      <div className="space-y-6">
        <h3 className="text-xl font-semibold text-white px-1 pt-4 flex items-center gap-2 uppercase tracking-widest">
          Global Synchronization
          <div className="w-4 h-4 rounded-full border border-gray-600 flex items-center justify-center text-[10px] text-gray-500 font-bold cursor-help" title="System-wide throughput and error metrics across all AI providers">i</div>
        </h3>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartContainer title="SYSTEM THROUGHPUT" icon={<TrendingUp className="w-4 h-4 text-gray-600" />} subtitle="API requests and success rate over 14 days">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={usageTimeline} margin={{ top: 10, right: -10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#fff" strokeOpacity={0.03} vertical={false} />
                <XAxis dataKey="label" stroke="#3f3f46" fontSize={10} fontWeight="600" tickLine={false} axisLine={false} />
                <YAxis yAxisId="left" stroke="#3f3f46" fontSize={10} fontWeight="600" tickLine={false} axisLine={false} />
                <YAxis yAxisId="right" orientation="right" domain={[0, 100]} stroke="#3f3f46" fontSize={10} fontWeight="600" tickLine={false} axisLine={false} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar yAxisId="left" dataKey="total_requests" name="Requests" fill="#ffffff" fillOpacity={0.08} stroke="#ffffff" strokeOpacity={0.2} strokeWidth={1} radius={[2, 2, 0, 0]} barSize={24} />
                <Line yAxisId="right" type="stepAfter" dataKey="success_rate" name="Success %" stroke="#ffffff" strokeWidth={1.5} dot={false} activeDot={{ r: 4, fill: '#fff' }} />
                <Legend iconType="circle" wrapperStyle={{ fontSize: 10, fontWeight: 'bold', paddingTop: 20 }} />
              </ComposedChart>
            </ResponsiveContainer>
          </ChartContainer>

          <ChartContainer title="EXCEPTION FREQUENCY" icon={<AlertCircle className="w-4 h-4 text-gray-600" />} subtitle="HTTP status codes and rate limit violations">
            {errorData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={errorData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#fff" strokeOpacity={0.03} vertical={false} />
                  <XAxis dataKey="code" stroke="#3f3f46" fontSize={10} fontWeight="600" tickLine={false} axisLine={false} />
                  <YAxis stroke="#3f3f46" fontSize={10} fontWeight="600" tickLine={false} axisLine={false} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Bar dataKey="count" name="Errors" radius={[2, 2, 0, 0]} barSize={40} fill="#ffffff" fillOpacity={0.08} stroke="#ffffff" strokeOpacity={0.2} strokeWidth={1}>
                    {errorData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.code.includes('429') ? '#fff' : '#fff'} fillOpacity={entry.code.includes('429') ? 0.3 : 0.08} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-zinc-700 py-20 space-y-4">
                 <CheckCircle2 className="w-12 h-12 mb-2 opacity-30" />
                 <div className="text-center space-y-2">
                   <p className="text-sm font-bold text-white/60">Zero Errors Detected</p>
                   <p className="text-[10px] text-zinc-600 max-w-xs">All AI API requests completed successfully. Error logs will appear when rate limits or API failures occur.</p>
                 </div>
              </div>
            )}
          </ChartContainer>
        </div>
      </div>

      {/* 5. DETAILED MODEL METRICS */}
      <div className="space-y-12">
        <h3 className="text-xl font-semibold text-white px-1 pt-4 flex items-center gap-2 uppercase tracking-widest">
           Inference Nodes
           <span className="text-xs font-normal text-zinc-600 tracking-normal">— per-model performance and request timeline</span>
        </h3>
        {(llmUsage?.models || []).map((model) => (
          <div key={`${model.provider}-${model.model}`} className="space-y-6 pt-8 border-t border-white/[0.04]">
            <div className="flex items-center gap-3 px-1">
              <h4 className="text-2xl font-bold text-white tracking-tight">{model.model}</h4>
              <div className="w-4 h-4 rounded-full border border-gray-600 flex items-center justify-center text-[10px] text-gray-500 font-bold">?</div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ChartContainer title="Requests" rateLimit={showLimits ? model.rate_limit : undefined}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={model.timeline.map(p => ({ ...p, label: new Date(p.date).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric' }) }))}>
                    <defs>
                      <linearGradient id={`grad-req-${model.model}`} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#ffffff" stopOpacity={0.1}/>
                        <stop offset="95%" stopColor="#ffffff" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
                    <XAxis dataKey="label" stroke="#3f3f46" fontSize={9} fontWeight="bold" tickLine={false} axisLine={false} />
                    <YAxis stroke="#3f3f46" fontSize={9} fontWeight="bold" tickLine={false} axisLine={false} />
                    <Tooltip 
                      contentStyle={tooltipStyle}
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const data = payload[0].payload;
                          return (
                            <div className="bg-[#0b0b0f] border border-white/10 rounded-2xl p-4 shadow-2xl min-w-[140px]">
                              <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-3">{data.label}</p>
                              <div className="space-y-2">
                                <div className="flex items-center justify-between gap-8">
                                  <div className="flex items-center gap-2">
                                    <div className="w-2 h-2 rounded-full bg-white shadow-[0_0_8px_white]" />
                                    <span className="text-xs font-bold text-white">API Calls</span>
                                  </div>
                                  <span className="text-xs font-black text-white">{data.requests}</span>
                                </div>
                                <div className="flex items-center justify-between gap-8">
                                  <div className="flex items-center gap-2">
                                    <div className="w-2 h-2 rounded-full bg-red-500 shadow-[0_0_8px_#ef4444]" />
                                    <span className="text-xs font-bold text-white">Rate Limit</span>
                                  </div>
                                  <span className="text-xs font-black text-white">{model.rate_limit}</span>
                                </div>
                              </div>
                              <div className="mt-3 pt-3 border-t border-white/5">
                                <p className="text-[10px] font-bold text-zinc-600 uppercase tracking-tighter">
                                  {Math.round((data.requests / model.rate_limit) * 100)}% consumed
                                </p>
                              </div>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Area type="monotone" dataKey="requests" stroke="#ffffff" strokeWidth={1.5} fillOpacity={1} fill={`url(#grad-req-${model.model})`} dot={false} />
                    {showLimits && (
                      <ReferenceLine y={model.rate_limit} stroke="#ef4444" strokeDasharray="3 3" label={{ position: 'right', value: 'LIMIT', fill: '#ef4444', fontSize: 8, fontWeight: 'bold' }} />
                    )}
                  </AreaChart>
                </ResponsiveContainer>
              </ChartContainer>

              <ChartContainer title="Total Tokens" rateLimit={showLimits ? model.rate_limit * 1000 : undefined}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={model.timeline.map(p => ({ ...p, label: new Date(p.date).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric' }) }))}>
                    <defs>
                      <linearGradient id={`grad-tok-${model.model}`} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#ffffff" stopOpacity={0.1}/>
                        <stop offset="95%" stopColor="#ffffff" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
                    <XAxis dataKey="label" stroke="#3f3f46" fontSize={9} fontWeight="bold" tickLine={false} axisLine={false} />
                    <YAxis stroke="#3f3f46" fontSize={9} fontWeight="bold" tickLine={false} axisLine={false} tickFormatter={(v) => v >= 1000 ? `${v/1000}K` : v} />
                    <Tooltip contentStyle={tooltipStyle} />
                    <Legend iconType="circle" wrapperStyle={{ fontSize: 10, fontWeight: 'bold', paddingTop: 20 }} />
                    <Area type="monotone" dataKey="prompt_tokens" name="Input" stroke="#ffffff" strokeOpacity={0.1} fill="#ffffff" fillOpacity={0.03} strokeWidth={1} stackId="1" dot={false} />
                    <Area type="monotone" dataKey="completion_tokens" name="Output" stroke="#ffffff" strokeOpacity={0.2} fill="#ffffff" fillOpacity={0.05} strokeWidth={1} stackId="1" dot={false} />
                    <Area type="monotone" dataKey="total_tokens" name="Total" stroke="#ffffff" strokeWidth={1.5} fill={`url(#grad-tok-${model.model})`} stackId="2" dot={false} />
                  </AreaChart>
                </ResponsiveContainer>
              </ChartContainer>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── UTILITY COMPONENTS (EXPANDED) ──────────────────────────────────────────

