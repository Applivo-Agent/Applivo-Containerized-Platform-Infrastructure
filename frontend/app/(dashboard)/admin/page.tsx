"use client";
import React, { useEffect, useState } from "react";
import { 
  Users, Activity, Shield, BarChart3, Globe, Zap,
  AlertCircle, CheckCircle2, Settings, Database, DollarSign, 
  Briefcase, TrendingUp, Server, Pause, Play, RotateCcw,
  Trash2, Search, Filter, MoreHorizontal, X, Check,
  ToggleLeft, FileText, History, Cpu
} from "lucide-react";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { toast } from "sonner";

type Tab = "dashboard" | "users" | "subscriptions" | "payments" | "applications" | "jobs" | "bot" | "queue" | "errors" | "analytics" | "features" | "audit" | "settings";

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
  applying: number;
  failed: number;
  total_jobs: number;
  scheduled_tasks: { id: string; name: string; next_run: string | null }[];
  scheduler_running: boolean;
  celery_workers: { name: string; status: string; active_tasks: number }[];
  celery_queues: Record<string, number>;
}

interface SystemHealth {
  backend: boolean;
  database: boolean;
  redis: boolean;
  worker: boolean;
  scheduler: boolean;
  uptime: number;
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

const TABS = [
  { id: "dashboard" as Tab, label: "Dashboard", icon: BarChart3 },
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
  
  // Search/filter states
  const [userSearch, setUserSearch] = useState("");
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    if (user?.is_superuser) {
      loadTabData(activeTab);
    }
  }, [user, activeTab]);

  const loadTabData = async (tab: Tab) => {
    setLoading(true);
    try {
      switch (tab) {
        case "dashboard":
          const statsRes = await api.get("/admin/stats");
          setStats(statsRes.data);
          break;
        case "users":
          const usersRes = await api.get("/admin/users?page_size=50");
          setUsers(usersRes.data.items || []);
          break;
        case "subscriptions":
          const subsRes = await api.get("/admin/subscriptions");
          setSubscriptions(subsRes.data || []);
          break;
        case "payments":
          const payRes = await api.get("/admin/payments?page_size=50");
          setPayments(payRes.data.items || []);
          break;
        case "applications":
          const appRes = await api.get("/admin/applications?page_size=50");
          setApplications(appRes.data.items || []);
          break;
        case "jobs":
          const jobsRes = await api.get("/admin/jobs?page_size=50");
          setJobs(jobsRes.data.items || []);
          break;
        case "bot":
          const botRes = await api.get("/agent/status");
          setBotStats(botRes.data);
          break;
        case "queue":
          const queueRes = await api.get("/admin/queue/status");
          setQueueStats(queueRes.data);
          break;
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
    } catch (err) {
      console.error("Failed to load:", err);
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
          <Shield className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold">Access Denied</h2>
          <p className="text-muted-foreground">You must be an admin to view this page.</p>
        </div>
      </div>
    );
  }

  const filteredUsers = users.filter(u => 
    u.email.toLowerCase().includes(userSearch.toLowerCase()) ||
    u.full_name.toLowerCase().includes(userSearch.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold font-display flex items-center gap-3">
          <Shield className="w-8 h-8 text-red-500" />
          Platform Administration
        </h1>
        <p className="text-muted-foreground mt-1">
          Manage users, subscriptions, and system operations.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
              activeTab === tab.id 
                ? "bg-brand-purple text-white" 
                : "glass hover:bg-white/10"
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {loading ? (
        <div className="glass-card p-12 text-center">
          <div className="w-8 h-8 border-2 border-brand-purple border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-muted-foreground mt-4">Loading...</p>
        </div>
      ) : (
        <>
          {activeTab === "dashboard" && <DashboardTab stats={stats} loading={loading} />}
          {activeTab === "users" && <UsersTab users={filteredUsers} search={userSearch} setSearch={setUserSearch} actionLoading={actionLoading} onAction={handleUserAction} />}
          {activeTab === "subscriptions" && <SubscriptionsTab subscriptions={subscriptions} />}
          {activeTab === "payments" && <PaymentsTab payments={payments} />}
          {activeTab === "applications" && <ApplicationsTab applications={applications} />}
          {activeTab === "jobs" && <JobsTab jobs={jobs} />}
          {activeTab === "bot" && <BotTab stats={botStats} />}
          {activeTab === "queue" && <QueueTab stats={queueStats} />}
          {activeTab === "errors" && <ErrorsTab />}
          {activeTab === "analytics" && <AnalyticsTab data={analyticsData} />}
          {activeTab === "features" && <FeaturesTab flags={featureFlags} />}
          {activeTab === "audit" && <AuditTab logs={auditLogs} />}
          {activeTab === "settings" && <SettingsTab health={systemHealth} onAction={runSystemAction} loading={loading} />}
        </>
      )}
    </div>
  );
}

function DashboardTab({ stats, loading }: { stats: Stats | null; loading: boolean }) {
  const formatCurrency = (amount: number) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(amount / 100);
  
  const statsData = stats ? [
    { label: "Total Users", value: stats.total_users.toLocaleString(), icon: Users, color: "text-blue-400" },
    { label: "Active Subs", value: stats.active_subscriptions.toLocaleString(), icon: Zap, color: "text-amber-400" },
    { label: "Revenue (Month)", value: formatCurrency(stats.revenue_this_month), icon: DollarSign, color: "text-emerald-400" },
    { label: "Jobs Scraped", value: stats.jobs_scraped.toLocaleString(), icon: Briefcase, color: "text-brand-purple-light" },
    { label: "Applications", value: stats.total_applications.toLocaleString(), icon: TrendingUp, color: "text-cyan-400" },
  ] : [];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {statsData.map((stat, i) => (
          <motion.div key={stat.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} className="glass-card p-5">
            <div className="flex justify-between items-start mb-3">
              <div className={`p-2 rounded-lg bg-white/5`}>
                <stat.icon className={`w-5 h-5 ${stat.color}`} />
              </div>
            </div>
            <div className="text-2xl font-bold font-display mb-1">{stat.value}</div>
            <div className="text-xs text-muted-foreground uppercase tracking-wider">{stat.label}</div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function UsersTab({ users, search, setSearch, actionLoading, onAction }: {
  users: User[]; search: string; setSearch: (s: string) => void;
  actionLoading: string | null; onAction: (id: string, a: "suspend" | "reactivate" | "delete") => void;
}) {
  return (
    <div className="space-y-4">
      <div className="flex gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text" placeholder="Search users..." value={search} onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-muted border border-border rounded-lg"
          />
        </div>
      </div>
      <div className="glass-card overflow-hidden">
        <table className="w-full">
          <thead className="border-b border-border">
            <tr className="text-left text-xs text-muted-foreground uppercase">
              <th className="p-4">User</th>
              <th className="p-4">Plan</th>
              <th className="p-4">Status</th>
              <th className="p-4">Apps</th>
              <th className="p-4">Joined</th>
              <th className="p-4">Last Login</th>
              <th className="p-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id} className="border-b border-border hover:bg-white/5">
                <td className="p-4">
                  <div>
                    <div className="font-medium">{user.full_name}</div>
                    <div className="text-xs text-muted-foreground">{user.email}</div>
                  </div>
                </td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    user.plan === 'premium' ? 'bg-amber-500/20 text-amber-400' :
                    user.plan === 'pro' ? 'bg-brand-purple/20 text-brand-purple-light' :
                    'bg-zinc-500/20 text-zinc-400'
                  }`}>
                    {user.plan || 'starter'}
                  </span>
                </td>
                <td className="p-4">
                  <span className={`flex items-center gap-1 text-xs ${user.is_active ? 'text-emerald-400' : 'text-red-400'}`}>
                    {user.is_active ? <CheckCircle2 className="w-3 h-3" /> : <X className="w-3 h-3" />}
                    {user.is_active ? 'Active' : 'Suspended'}
                  </span>
                </td>
                <td className="p-4 text-sm">{user.applications_count}</td>
                <td className="p-4 text-sm text-muted-foreground">{new Date(user.created_at).toLocaleDateString()}</td>
                <td className="p-4 text-sm text-muted-foreground">{user.last_login_at ? new Date(user.last_login_at).toLocaleDateString() : 'Never'}</td>
                <td className="p-4">
                  <div className="flex gap-1">
                    {user.is_active ? (
                      <button onClick={() => onAction(user.id, 'suspend')} disabled={actionLoading === user.id} className="p-1.5 hover:bg-amber-500/20 rounded text-amber-400" title="Suspend">
                        <Pause className="w-4 h-4" />
                      </button>
                    ) : (
                      <button onClick={() => onAction(user.id, 'reactivate')} disabled={actionLoading === user.id} className="p-1.5 hover:bg-emerald-500/20 rounded text-emerald-400" title="Reactivate">
                        <Play className="w-4 h-4" />
                      </button>
                    )}
                    <button onClick={() => onAction(user.id, 'delete')} disabled={actionLoading === user.id} className="p-1.5 hover:bg-red-500/20 rounded text-red-400" title="Delete">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function SubscriptionsTab({ subscriptions }: { subscriptions: Subscription[] }) {
  return (
    <div className="glass-card overflow-hidden">
      <table className="w-full">
        <thead className="border-b border-border">
          <tr className="text-left text-xs text-muted-foreground uppercase">
            <th className="p-4">User</th>
            <th className="p-4">Plan</th>
            <th className="p-4">Status</th>
            <th className="p-4">Daily Limit</th>
            <th className="p-4">Start Date</th>
            <th className="p-4">End Date</th>
          </tr>
        </thead>
        <tbody>
          {subscriptions.map(sub => (
            <tr key={sub.id} className="border-b border-border">
              <td className="p-4 text-sm">{sub.user_email}</td>
              <td className="p-4">
                <span className="px-2 py-1 rounded text-xs font-medium bg-brand-purple/20 text-brand-purple-light">{sub.plan}</span>
              </td>
              <td className="p-4">
                <span className={`px-2 py-1 rounded text-xs ${sub.status === 'active' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                  {sub.status}
                </span>
              </td>
              <td className="p-4 text-sm">{sub.daily_limit}</td>
              <td className="p-4 text-sm text-muted-foreground">{new Date(sub.start_date).toLocaleDateString()}</td>
              <td className="p-4 text-sm text-muted-foreground">{sub.end_date ? new Date(sub.end_date).toLocaleDateString() : 'Never'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function PaymentsTab({ payments }: { payments: Payment[] }) {
  const formatCurrency = (amount: number) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(amount / 100);
  
  return (
    <div className="glass-card overflow-hidden">
      <table className="w-full">
        <thead className="border-b border-border">
          <tr className="text-left text-xs text-muted-foreground uppercase">
            <th className="p-4">User</th>
            <th className="p-4">Amount</th>
            <th className="p-4">Status</th>
            <th className="p-4">Date</th>
          </tr>
        </thead>
        <tbody>
          {payments.map(payment => (
            <tr key={payment.id} className="border-b border-border">
              <td className="p-4 text-sm">{payment.user_email}</td>
              <td className="p-4 font-medium">{formatCurrency(payment.amount)}</td>
              <td className="p-4">
                <span className={`px-2 py-1 rounded text-xs ${payment.status === 'completed' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'}`}>
                  {payment.status}
                </span>
              </td>
              <td className="p-4 text-sm text-muted-foreground">{new Date(payment.created_at).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function BotTab({ stats }: { stats: BotStats | null }) {
  const statusStr = String(stats?.status || "").toLowerCase();
  const isRunning = ["running", "true", "active"].includes(statusStr) || Boolean(stats?.status);
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div className="glass-card p-6">
        <div className="text-sm text-muted-foreground mb-2">Applications Today</div>
        <div className="text-3xl font-bold">{stats?.applications_today || 0}</div>
      </div>
      <div className="glass-card p-6">
        <div className="text-sm text-muted-foreground mb-2">Success Rate</div>
        <div className="text-3xl font-bold text-emerald-400">{stats?.success_rate ? `${stats.success_rate}%` : 'N/A'}</div>
      </div>
      <div className="glass-card p-6">
        <div className="text-sm text-muted-foreground mb-2">Failed</div>
        <div className="text-3xl font-bold text-red-400">{stats?.failed || 0}</div>
      </div>
      <div className="glass-card p-6">
        <div className="text-sm text-muted-foreground mb-2">Queue Size</div>
        <div className="text-3xl font-bold">{stats?.queue_size || 0}</div>
      </div>
      <div className="glass-card p-6 md:col-span-2 lg:col-span-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-lg font-semibold">Bot Status</div>
            <div className={`text-sm ${isRunning ? 'text-emerald-400' : 'text-muted-foreground'}`}>
              {isRunning ? 'Running' : 'Idle'}
            </div>
          </div>
          <div className={`w-3 h-3 rounded-full ${isRunning ? 'bg-emerald-400 animate-pulse' : 'bg-zinc-500'}`}></div>
        </div>
      </div>
    </div>
  );
}

function QueueTab({ stats }: { stats: QueueStats | null }) {
  const queueItems = stats ? [
    { name: "Pending Applications", count: stats.pending, color: "bg-amber-500", icon: AlertCircle },
    { name: "Applying", count: stats.applying, color: "bg-blue-500", icon: Activity },
    { name: "Failed", count: stats.failed, color: "bg-red-500", icon: X },
    { name: "Total Jobs Scraped", count: stats.total_jobs, color: "bg-emerald-500", icon: Briefcase },
  ] : [];

  const workerItems = stats?.celery_workers || [];
  const queueNames = stats?.celery_queues ? Object.entries(stats.celery_queues) : [];
  
  return (
    <div className="space-y-6">
      {/* Application Queue Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {queueItems.map(q => (
          <div key={q.name} className="glass-card p-6">
            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
              <q.icon className="w-4 h-4" />
              {q.name}
            </div>
            <div className="text-3xl font-bold">{q.count}</div>
            <div className={`h-1 mt-3 rounded-full ${q.color}`} style={{ width: `${Math.min((q.count / 100) * 100, 100)}%` }}></div>
          </div>
        ))}
      </div>

      {/* Celery Workers */}
      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Server className="w-5 h-5" />
          Celery Workers
        </h3>
        {workerItems.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {workerItems.map((w, i) => (
              <div key={i} className="flex items-center gap-3 p-3 bg-muted rounded-lg">
                <div className={`w-3 h-3 rounded-full ${w.status === 'active' ? 'bg-emerald-400 animate-pulse' : 'bg-zinc-500'}`}></div>
                <div>
                  <div className="text-sm font-medium">{w.name}</div>
                  <div className="text-xs text-muted-foreground">Active tasks: {w.active_tasks}</div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground text-center py-4">No workers connected</p>
        )}
      </div>

      {/* Queue Distribution */}
      {queueNames.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Cpu className="w-5 h-5" />
            Active Tasks by Queue
          </h3>
          <div className="space-y-3">
            {queueNames.map(([name, count]) => (
              <div key={name} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                <span className="font-medium">{name}</span>
                <span className="text-brand-purple-light">{count} tasks</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Scheduled Tasks */}
      {stats?.scheduled_tasks && stats.scheduled_tasks.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <RotateCcw className="w-5 h-5" />
            Scheduled Tasks
          </h3>
          <div className="space-y-2">
            {stats.scheduled_tasks.map((task, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                <span className="font-medium">{task.name}</span>
                <span className="text-xs text-muted-foreground">
                  {task.next_run ? `Next: ${new Date(task.next_run).toLocaleString()}` : 'Not scheduled'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Scheduler Status */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-lg font-semibold">APScheduler</div>
            <div className={`text-sm ${stats?.scheduler_running ? 'text-emerald-400' : 'text-red-400'}`}>
              {stats?.scheduler_running ? 'Running' : 'Stopped'}
            </div>
          </div>
          <div className={`w-3 h-3 rounded-full ${stats?.scheduler_running ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`}></div>
        </div>
      </div>
    </div>
  );
}

function ErrorsTab() {
  return (
    <div className="glass-card p-8 text-center">
      <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
      <p className="text-muted-foreground">No recent errors</p>
      <p className="text-sm text-muted-foreground mt-2">Error logs will appear here when issues occur.</p>
    </div>
  );
}

function SettingsTab({ health, onAction, loading }: { health: SystemHealth | null; onAction: (a: string) => void; loading: boolean }) {
  const services = health ? [
    { name: "Backend API", status: health.backend, icon: Server },
    { name: "Database", status: health.database, icon: Database },
    { name: "Redis", status: health.redis, icon: Zap },
    { name: "Worker", status: health.worker, icon: Activity },
    { name: "Scheduler", status: health.scheduler, icon: RotateCcw },
  ] : [];

  return (
    <div className="space-y-6">
      {/* System Status */}
      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold mb-4">System Services</h3>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {services.map(s => (
            <div key={s.name} className="flex items-center gap-3 p-3 bg-muted rounded-lg">
              <s.icon className={`w-5 h-5 ${s.status ? 'text-emerald-400' : 'text-red-400'}`} />
              <div>
                <div className="text-sm font-medium">{s.name}</div>
                <div className={`text-xs ${s.status ? 'text-emerald-400' : 'text-red-400'}`}>
                  {s.status ? 'Online' : 'Offline'}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Manual Actions */}
      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold mb-4">Manual Controls</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button onClick={() => onAction('run-scraper')} disabled={loading} className="p-4 glass hover:bg-white/10 rounded-lg text-left">
            <Briefcase className="w-5 h-5 mb-2 text-brand-purple-light" />
            <div className="font-medium">Run Scraper</div>
            <div className="text-xs text-muted-foreground">Start job scraping</div>
          </button>
          <button onClick={() => onAction('clear-queue')} disabled={loading} className="p-4 glass hover:bg-white/10 rounded-lg text-left">
            <RotateCcw className="w-5 h-5 mb-2 text-amber-400" />
            <div className="font-medium">Clear Queue</div>
            <div className="text-xs text-muted-foreground">Clear pending tasks</div>
          </button>
          <button onClick={() => onAction('restart-worker')} disabled={loading} className="p-4 glass hover:bg-white/10 rounded-lg text-left">
            <Activity className="w-5 h-5 mb-2 text-emerald-400" />
            <div className="font-medium">Restart Worker</div>
            <div className="text-xs text-muted-foreground">Restart Celery worker</div>
          </button>
        </div>
      </div>
    </div>
  );
}

function ApplicationsTab({ applications }: { applications: Application[] }) {
  const statusColors: Record<string, string> = {
    success: "bg-emerald-500/20 text-emerald-400",
    failed: "bg-red-500/20 text-red-400",
    pending: "bg-amber-500/20 text-amber-400",
    retry: "bg-blue-500/20 text-blue-400",
  };
  
  return (
    <div className="glass-card overflow-hidden">
      <table className="w-full">
        <thead className="border-b border-border">
          <tr className="text-left text-xs text-muted-foreground uppercase">
            <th className="p-4">User</th>
            <th className="p-4">Job</th>
            <th className="p-4">Company</th>
            <th className="p-4">Status</th>
            <th className="p-4">Error</th>
            <th className="p-4">Date</th>
          </tr>
        </thead>
        <tbody>
          {applications.map(app => (
            <tr key={app.id} className="border-b border-border">
              <td className="p-4 text-sm">{app.user_email}</td>
              <td className="p-4 text-sm">{app.job_title}</td>
              <td className="p-4 text-sm">{app.company}</td>
              <td className="p-4">
                <span className={`px-2 py-1 rounded text-xs ${statusColors[app.status] || 'bg-zinc-500/20 text-zinc-400'}`}>
                  {app.status}
                </span>
              </td>
              <td className="p-4 text-sm text-red-400 max-w-[200px] truncate">{app.error || '-'}</td>
              <td className="p-4 text-sm text-muted-foreground">{new Date(app.created_at).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function JobsTab({ jobs }: { jobs: Job[] }) {
  return (
    <div className="glass-card overflow-hidden">
      <table className="w-full">
        <thead className="border-b border-border">
          <tr className="text-left text-xs text-muted-foreground uppercase">
            <th className="p-4">Title</th>
            <th className="p-4">Company</th>
            <th className="p-4">Source</th>
            <th className="p-4">Status</th>
            <th className="p-4">Scraped</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map(job => (
            <tr key={job.id} className="border-b border-border">
              <td className="p-4 text-sm">{job.title}</td>
              <td className="p-4 text-sm">{job.company}</td>
              <td className="p-4 text-sm">{job.source}</td>
              <td className="p-4">
                <span className={`px-2 py-1 rounded text-xs ${job.status === 'active' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-zinc-500/20 text-zinc-400'}`}>
                  {job.status}
                </span>
              </td>
              <td className="p-4 text-sm text-muted-foreground">{new Date(job.scraped_at).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function AnalyticsTab({ data }: { data: AnalyticsData | null }) {
  if (!data) return <div className="glass-card p-8 text-center text-muted-foreground">No analytics data available</div>;
  
  const maxApp = Math.max(...data.applications_by_day.map(d => d.count), 1);
  const maxRev = Math.max(...data.revenue_by_day.map(d => d.amount), 1);
  
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Applications (Last 7 Days)</h3>
          <div className="space-y-2">
            {data.applications_by_day.slice(-7).map(d => (
              <div key={d.date} className="flex items-center gap-3">
                <span className="text-xs text-muted-foreground w-20">{d.date}</span>
                <div className="flex-1 h-6 bg-muted rounded overflow-hidden">
                  <div className="h-full bg-brand-purple" style={{ width: `${(d.count / maxApp) * 100}%` }}></div>
                </div>
                <span className="text-xs w-8">{d.count}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Revenue (Last 7 Days)</h3>
          <div className="space-y-2">
            {data.revenue_by_day.slice(-7).map(d => (
              <div key={d.date} className="flex items-center gap-3">
                <span className="text-xs text-muted-foreground w-20">{d.date}</span>
                <div className="flex-1 h-6 bg-muted rounded overflow-hidden">
                  <div className="h-full bg-emerald-500" style={{ width: `${(d.amount / maxRev) * 100}%` }}></div>
                </div>
                <span className="text-xs w-16">₹{d.amount}</span>
              </div>
            ))}
          </div>
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
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {displayFlags.map(flag => (
        <div key={flag.key} className="glass-card p-5">
          <div className="flex items-start justify-between">
            <div>
              <div className="font-semibold">{flag.label}</div>
              <div className="text-sm text-muted-foreground mt-1">{flag.description}</div>
            </div>
            <div className={`w-3 h-3 rounded-full ${flag.enabled ? 'bg-emerald-400' : 'bg-zinc-500'}`}></div>
          </div>
          <div className="mt-4 flex items-center gap-2">
            <span className={`text-xs px-2 py-1 rounded ${flag.enabled ? 'bg-emerald-500/20 text-emerald-400' : 'bg-zinc-500/20 text-zinc-400'}`}>
              {flag.enabled ? 'Enabled' : 'Disabled'}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}

function AuditTab({ logs }: { logs: AuditLog[] }) {
  return (
    <div className="glass-card overflow-hidden">
      <table className="w-full">
        <thead className="border-b border-border">
          <tr className="text-left text-xs text-muted-foreground uppercase">
            <th className="p-4">Admin</th>
            <th className="p-4">Action</th>
            <th className="p-4">Target</th>
            <th className="p-4">IP Address</th>
            <th className="p-4">Result</th>
            <th className="p-4">Time</th>
          </tr>
        </thead>
        <tbody>
          {logs.length === 0 ? (
            <tr>
              <td colSpan={6} className="p-8 text-center text-muted-foreground">No audit logs</td>
            </tr>
          ) : logs.map(log => (
            <tr key={log.id} className="border-b border-border">
              <td className="p-4 text-sm">{log.admin_email}</td>
              <td className="p-4 text-sm">{log.action}</td>
              <td className="p-4 text-sm">{log.target}</td>
              <td className="p-4 text-sm text-muted-foreground">{log.ip_address}</td>
              <td className="p-4">
                <span className={`px-2 py-1 rounded text-xs ${log.result === 'success' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                  {log.result}
                </span>
              </td>
              <td className="p-4 text-sm text-muted-foreground">{new Date(log.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}