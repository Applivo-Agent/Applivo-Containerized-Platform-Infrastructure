"use client";
import React, { useEffect, useState } from "react";
import { 
  Users, Activity, Shield, 
  BarChart3, Globe, Zap,
  AlertCircle, CheckCircle2,
  Settings, Database, DollarSign, Briefcase, TrendingUp
} from "lucide-react";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

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

interface AuditLog {
  id: string;
  user_email: string;
  action: string;
  timestamp: string;
  success: boolean;
}

export default function AdminDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState<Stats | null>(null);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.is_superuser) {
      loadData();
    }
  }, [user]);

  const loadData = async () => {
    try {
      const [statsRes, logsRes] = await Promise.all([
        api.get("/admin/stats"),
        api.get("/admin/audit-logs?page_size=10")
      ]);
      setStats(statsRes.data);
      setLogs(logsRes.data);
    } catch (err) {
      console.error("Failed to load admin data:", err);
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

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(amount / 100);
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 60) return `${mins} mins ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours} hours ago`;
    return date.toLocaleDateString();
  };

  const statsData = stats ? [
    { label: "Total Users", value: stats.total_users.toLocaleString(), change: "+12.5%", icon: Users, color: "text-blue-400" },
    { label: "Active Subs", value: stats.active_subscriptions.toLocaleString(), change: "+8.2%", icon: Zap, color: "text-amber-400" },
    { label: "Revenue (Month)", value: formatCurrency(stats.revenue_this_month), change: "+24.1%", icon: DollarSign, color: "text-emerald-400" },
    { label: "Jobs Scraped", value: stats.jobs_scraped.toLocaleString(), change: "Live", icon: Briefcase, color: "text-brand-purple-light" },
    { label: "Applications", value: stats.total_applications.toLocaleString(), change: "+15.3%", icon: TrendingUp, color: "text-cyan-400" },
    { label: "System Health", value: "99.9%", change: "Stable", icon: Shield, color: "text-green-400" },
  ] : [];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold font-display flex items-center gap-3">
          <Shield className="w-8 h-8 text-red-500" />
          Platform Administration
        </h1>
        <p className="text-muted-foreground mt-1 text-lg">
          Global system overview and user management.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {loading ? (
          Array(6).fill(0).map((_, i) => (
            <div key={i} className="glass-card p-6 animate-pulse">
              <div className="h-4 bg-white/10 rounded w-1/2 mb-4"></div>
              <div className="h-8 bg-white/10 rounded w-3/4"></div>
            </div>
          ))
        ) : (
          statsData.map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="glass-card p-5"
            >
              <div className="flex justify-between items-start mb-3">
                <div className={`p-2 rounded-lg bg-white/5`}>
                  <stat.icon className={`w-5 h-5 ${stat.color}`} />
                </div>
                <span className={`text-xs font-medium ${stat.change.includes('+') || stat.change === 'Stable' || stat.change === 'Live' ? 'text-emerald-400' : 'text-muted-foreground'}`}>
                  {stat.change}
                </span>
              </div>
              <div className="text-2xl font-bold font-display mb-1">{stat.value}</div>
              <div className="text-xs text-muted-foreground uppercase tracking-wider">{stat.label}</div>
            </motion.div>
          ))
        )}
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* System Health */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
              <Activity className="w-5 h-5 text-brand-purple-light" />
              Recent Audit Logs
            </h3>
            <div className="space-y-4">
              {loading ? (
                Array(5).fill(0).map((_, i) => (
                  <div key={i} className="flex items-center justify-between py-3 border-b border-border animate-pulse">
                    <div className="flex items-center gap-4">
                      <div className="w-2 h-2 rounded-full bg-white/20"></div>
                      <div>
                        <div className="h-4 bg-white/10 rounded w-32 mb-2"></div>
                        <div className="h-3 bg-white/10 rounded w-24"></div>
                      </div>
                    </div>
                  </div>
                ))
              ) : logs.length > 0 ? (
                logs.map((log) => (
                  <div key={log.id} className="flex items-center justify-between py-3 border-b border-border last:border-0">
                    <div className="flex items-center gap-4">
                      <div className={`w-2 h-2 rounded-full ${log.success ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-amber-500 shadow-[0_0_8px_#f59e0b]'}`} />
                      <div>
                        <p className="text-sm font-medium">{log.action}</p>
                        <p className="text-xs text-muted-foreground">{log.user_email || 'System'} • {formatTime(log.timestamp)}</p>
                      </div>
                    </div>
                    <button className="text-xs text-brand-purple-light hover:underline">View details</button>
                  </div>
                ))
              ) : (
                <p className="text-muted-foreground text-center py-4">No audit logs yet.</p>
              )}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="space-y-6">
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
              <Settings className="w-5 h-5 text-zinc-400" />
              Quick Actions
            </h3>
            <div className="space-y-3">
              <button onClick={() => window.location.reload()} className="w-full text-left px-4 py-3 rounded-lg hover:bg-white/5 border border-border transition-all flex items-center justify-between group">
                <div className="flex items-center gap-3">
                  <Database className="w-4 h-4 text-blue-400" />
                  <span className="text-sm">Refresh Data</span>
                </div>
                <ChevronRightIcon className="w-4 h-4 text-muted-foreground group-hover:translate-x-1 transition-transform" />
              </button>
              <button className="w-full text-left px-4 py-3 rounded-lg hover:bg-white/5 border border-border transition-all flex items-center justify-between group text-red-400">
                <div className="flex items-center gap-3">
                  <AlertCircle className="w-4 h-4" />
                  <span className="text-sm font-medium">Emergency Shutdown</span>
                </div>
                <ChevronRightIcon className="w-4 h-4 opacity-50 group-hover:translate-x-1 transition-transform" />
              </button>
            </div>
          </div>

          <div className="glass-card p-6 bg-gradient-to-br from-brand-purple/10 to-transparent">
            <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-400" />
              Maintenance Mode
            </h3>
            <p className="text-xs text-muted-foreground mb-4">
              Toggling Maintenance Mode will block all non-admin traffic to the platform.
            </p>
            <button className="px-4 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-xs font-semibold border border-border transition-colors">
              Enable Maintenance
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function ChevronRightIcon(props: any) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="m9 18 6-6-6-6"/>
    </svg>
  );
}