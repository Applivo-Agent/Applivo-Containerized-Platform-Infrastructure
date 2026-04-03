"use client";
import React from "react";
import { 
  Users, Activity, Shield, 
  BarChart3, Globe, Zap,
  AlertCircle, CheckCircle2,
  Settings, Database
} from "lucide-react";
import { motion } from "framer-motion";

const stats = [
  { label: "Total Users", value: "1,284", change: "+12.5%", icon: Users, color: "text-blue-400" },
  { label: "Active Subs", value: "856", change: "+8.2%", icon: Zap, color: "text-amber-400" },
  { label: "API Requests", value: "482k", change: "+24.1%", icon: Activity, color: "text-emerald-400" },
  { label: "System Health", value: "99.9%", change: "Stable", icon: Shield, color: "text-brand-purple-light" },
];

const logs = [
  { id: 1, user: "admin@applivo.com", action: "System Config Update", time: "2 mins ago", status: "success" },
  { id: 2, user: "test@example.com", action: "Subscription Upgrade", time: "15 mins ago", status: "success" },
  { id: 3, user: "system", action: "Daily Job Scrape", time: "1 hour ago", status: "success" },
  { id: 4, user: "unknown_ip", action: "Failed Login Attempt", time: "3 hours ago", status: "warning" },
];

export default function AdminDashboard() {
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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-card p-6"
          >
            <div className="flex justify-between items-start mb-4">
              <div className={`p-2 rounded-lg bg-white/5`}>
                <stat.icon className={`w-5 h-5 ${stat.color}`} />
              </div>
              <span className={`text-xs font-medium ${stat.change.includes('+') ? 'text-emerald-400' : 'text-muted-foreground'}`}>
                {stat.change}
              </span>
            </div>
            <div className="text-2xl font-bold font-display mb-1">{stat.value}</div>
            <div className="text-xs text-muted-foreground uppercase tracking-wider">{stat.label}</div>
          </motion.div>
        ))}
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
              {logs.map((log) => (
                <div key={log.id} className="flex items-center justify-between py-3 border-b border-border last:border-0">
                  <div className="flex items-center gap-4">
                    <div className={`w-2 h-2 rounded-full ${log.status === 'success' ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-amber-500 shadow-[0_0_8px_#f59e0b]'}`} />
                    <div>
                      <p className="text-sm font-medium">{log.action}</p>
                      <p className="text-xs text-muted-foreground">{log.user} • {log.time}</p>
                    </div>
                  </div>
                  <button className="text-xs text-brand-purple-light hover:underline">View details</button>
                </div>
              ))}
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
              <button className="w-full text-left px-4 py-3 rounded-lg hover:bg-white/5 border border-border transition-all flex items-center justify-between group">
                <div className="flex items-center gap-3">
                  <Database className="w-4 h-4 text-blue-400" />
                  <span className="text-sm">Database Backup</span>
                </div>
                <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:translate-x-1 transition-transform" />
              </button>
              <button className="w-full text-left px-4 py-3 rounded-lg hover:bg-white/5 border border-border transition-all flex items-center justify-between group text-red-400">
                <div className="flex items-center gap-3">
                  <AlertCircle className="w-4 h-4" />
                  <span className="text-sm font-medium">Emergency Shutdown</span>
                </div>
                <ChevronRight className="w-4 h-4 opacity-50 group-hover:translate-x-1 transition-transform" />
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

function ChevronRight(props: any) {
  return (
    <svg 
      {...props} 
      xmlns="http://www.w3.org/2000/svg" 
      width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
    >
      <path d="m9 18 6-6-6-6"/>
    </svg>
  );
}
