"use client";
import React, { useEffect, useState } from "react";
import { 
  Users, Activity, Shield, BarChart3, Globe, Zap,
  AlertCircle, CheckCircle2, Settings, Database, DollarSign, 
  Briefcase, TrendingUp, Server, Pause, Play, RotateCcw,
  Trash2, Search, Filter, MoreHorizontal, X, Check
} from "lucide-react";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { toast } from "sonner";

type Tab = "dashboard" | "users" | "subscriptions" | "payments" | "bot" | "queue" | "errors" | "settings";

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
  default: number;
  scraping: number;
  analysis: number;
  apply: number;
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

const TABS = [
  { id: "dashboard" as Tab, label: "Dashboard", icon: BarChart3 },
  { id: "users" as Tab, label: "Users", icon: Users },
  { id: "subscriptions" as Tab, label: "Subscriptions", icon: Zap },
  { id: "payments" as Tab, label: "Payments", icon: DollarSign },
  { id: "bot" as Tab, label: "Bot Monitor", icon: Globe },
  { id: "queue" as Tab, label: "Queue", icon: Server },
  { id: "errors" as Tab, label: "Errors", icon: AlertCircle },
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
  const [botStats, setBotStats] = useState<BotStats | null>(null);
  const [queueStats, setQueueStats] = useState<QueueStats | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  
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
        case "bot":
          const botRes = await api.get("/agent/status");
          setBotStats(botRes.data);
          break;
        case "queue":
          const queueRes = await api.get("/admin/queue/status");
          setQueueStats(queueRes.data);
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
          {activeTab === "bot" && <BotTab stats={botStats} />}
          {activeTab === "queue" && <QueueTab stats={queueStats} />}
          {activeTab === "errors" && <ErrorsTab />}
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
  const isRunning = !!(stats?.status === "running" || stats?.status === true || stats?.status === "true");
  
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
  const queues = stats ? [
    { name: "Default", count: stats.default, color: "bg-blue-500" },
    { name: "Scraping", count: stats.scraping, color: "bg-amber-500" },
    { name: "Analysis", count: stats.analysis, color: "bg-brand-purple" },
    { name: "Apply", count: stats.apply, color: "bg-emerald-500" },
  ] : [];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {queues.map(q => (
        <div key={q.name} className="glass-card p-6">
          <div className="text-sm text-muted-foreground mb-2">{q.name}</div>
          <div className="text-3xl font-bold">{q.count}</div>
          <div className={`h-1 mt-3 rounded-full ${q.color}`} style={{ width: `${Math.min((q.count / 100) * 100, 100)}%` }}></div>
        </div>
      ))}
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