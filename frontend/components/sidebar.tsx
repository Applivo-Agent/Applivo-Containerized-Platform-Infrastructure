"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { useSubscription } from "@/lib/subscription";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard, Briefcase, FileText, BarChart2,
  MessageSquare, BotMessageSquare, Settings, LogOut, Crown, Zap,
  Users, Shield, ChevronRight, BookOpen,
  TrendingUp, Mail, Bell, Link2, CreditCard,
  Layers, Target, Star, RefreshCw, Search, Send, Radio
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useAgentStatus } from "@/lib/agent-status";

const TASK_MAP: Record<string, { label: string; icon: any; color: string }> = {
  scrape_jobs: { label: "Scraping Jobs", icon: Search, color: "text-blue-400" },
  analyze_jobs: { label: "Analyzing Jobs", icon: Zap, color: "text-amber-400" },
  queue_jobs: { label: "Staging Applications", icon: Layers, color: "text-emerald-400" },
  apply_jobs: { label: "Deploying Applications", icon: Send, color: "text-purple-400" },
};

const navGroups = [
  {
    label: "Core",
    items: [
      { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
      { href: "/jobs", icon: Briefcase, label: "Jobs" },
      { href: "/applications", icon: Layers, label: "Applications" },
      { href: "/resumes", icon: FileText, label: "Resumes" },
      { href: "/analytics", icon: BarChart2, label: "Analytics" },
      { href: "/chat", icon: MessageSquare, BotMessageSquare, label: "AI Chat" },
      { href: "/messages", icon: Mail, label: "Messages" },
      { href: "/outreach", icon: Radio, label: "Outreach" },
    ],
  },
  {
    label: "Pro Features",
    pro: true,
    items: [
      { href: "/cover-letters", icon: BookOpen, label: "Cover Letters", plan: "pro" },
      { href: "/interviews", icon: Star, label: "Interviews", plan: "pro" },
      { href: "/skill-gaps", icon: Target, label: "Skill Gaps", plan: "pro" },
      { href: "/follow-ups", icon: Bell, label: "Follow-ups", plan: "pro" },
    ],
  },
  {
    label: "Premium",
    premium: true,
    items: [
      { href: "/market", icon: TrendingUp, label: "Market Insights", plan: "premium" },
    ],
  },
  {
    label: "Account",
    items: [
      { href: "/profile", icon: Users, label: "Profile" },
      { href: "/connect", icon: Link2, label: "Connections" },
      { href: "/subscription", icon: CreditCard, label: "Subscription" },
      { href: "/settings", icon: Settings, label: "Settings" },
      { href: "/outreach/settings", icon: Link2, label: "Connectors" },
      { href: "/security", icon: Shield, label: "Security" },
    ],
  },
];

const sidebarVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.04, delayChildren: 0.1 }
  }
};

const itemVariants = {
  hidden: { opacity: 0, x: -8 },
  show: { opacity: 1, x: 0, transition: { type: "spring" as const, stiffness: 300, damping: 24 } }
};

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();
  const { plan, quota, subscription } = useSubscription();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  const time = new Date().getHours();
  const greeting = time < 12 ? "Good morning" : time < 17 ? "Good afternoon" : "Good evening";

  const planLabel = user?.is_superuser
    ? "Admin"
    : plan === "starter"
      ? "Starter"
      : plan === "pro"
        ? "Pro"
        : plan === "premium"
          ? "Premium"
          : "Free";
  const planColor = user?.is_superuser
    ? "text-zinc-400"
    : plan === "premium"
      ? "text-white"
      : plan === "pro"
        ? "text-zinc-200"
        : plan === "starter"
          ? "text-zinc-600"
          : "text-zinc-500";

  return (
    <aside className="fixed left-0 top-16 h-[calc(100vh-64px)] w-[17rem] flex flex-col bg-[#0d0d0d] border-r border-white/6 z-30 overflow-hidden">

      {/* Greeting & Quick Stats */}
      <motion.div
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: 1, height: "auto" }}
        className="px-5 py-5 border-b border-white/6 bg-white/2"
      >
        <div className="flex flex-col gap-1">
          <span className="text-[11px] font-black text-white/40 uppercase tracking-[0.2em]">{greeting}</span>
          <div className="flex items-center justify-between">
            <span className="text-[15px] font-bold text-white tracking-tight leading-none">
              {user?.full_name ?? "Agent"}
            </span>
            {quota && (
              <span className="text-[10px] font-black text-white/30 uppercase tracking-widest leading-none">
                {quota.used}/{quota.limit}
              </span>
            )}
          </div>
        </div>
        {quota && (
           <div className="w-full h-1 bg-white/[0.03] rounded-full overflow-hidden mt-4">
             <motion.div
               initial={{ width: 0 }}
               animate={{ width: `${Math.min((quota.used / quota.limit) * 100, 100)}%` }}
               transition={{ duration: 1, ease: "anticipate" }}
               className="h-full bg-white/20 rounded-full"
             />
           </div>
        )}
      </motion.div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-5 px-3">
        <motion.div variants={sidebarVariants} initial="hidden" animate="show" className="space-y-5">
          {navGroups.map((group) => (
            <div key={group.label}>
              <p className="px-3 mb-2 text-[10px] font-bold text-zinc-700 uppercase tracking-widest flex items-center gap-2">
                {group.label}
                {group.pro && <span className="text-[8px] bg-white/15 text-zinc-200 px-1.5 py-0.5 rounded-full font-black">PRO</span>}
                {group.premium && <span className="text-[8px] bg-white/[0.05] text-white px-1.5 py-0.5 rounded-full font-black">PREM</span>}
              </p>
              <ul className="space-y-0.5">
                {group.items.map((item) => {
                  const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
                  const isSuper = user?.is_superuser ?? false;
                  const needsPro = (item as any).plan === "pro" && plan !== "pro" && plan !== "premium";
                  const needsPremium = (item as any).plan === "premium" && plan !== "premium";
                  const isLocked = !isSuper && (needsPro || needsPremium);

                  return (
                    <motion.li
                      variants={itemVariants}
                      key={item.href}
                      whileHover={{ x: 2 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <Link
                        href={isLocked ? "/subscription" : item.href}
                        className={cn(
                          "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group relative overflow-hidden",
                          (item as any).indent && "ml-4 py-1.5 text-xs",
                          isActive
                            ? "text-white bg-[#1a1a1a] border border-[#2a2a2a]"
                            : "text-zinc-400 hover:text-zinc-200 hover:bg-[#1a1a1a]",
                          isLocked && "opacity-50"
                        )}
                      >
                        <item.icon className={cn("shrink-0 transition-colors", (item as any).indent ? "w-3 h-3" : "w-4 h-4", isActive ? "text-white" : "text-zinc-500 group-hover:text-zinc-300")} />
                        <span className="flex-1">{item.label}</span>
                        {isLocked && <Crown className="w-3.5 h-3.5 text-amber-500/70" />}
                      </Link>
                    </motion.li>
                  );
                })}
              </ul>
            </div>
          ))}

      {/* Admin link */}
          {user?.is_superuser && (
            <motion.div variants={itemVariants}>
              <p className="px-3 mb-2 text-[10px] font-bold text-zinc-700 uppercase tracking-widest mt-2">Admin Area</p>
              <Link
                href="/admin"
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 relative overflow-hidden",
                  pathname.startsWith("/admin")
                    ? "text-white bg-white/5 border border-white/10"
                    : "text-zinc-600 hover:text-zinc-300 hover:bg-white/5"
                )}
              >
                {pathname.startsWith("/admin") && (
                  <motion.div layoutId="sidebar-admin-active" className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-white rounded-r-full" />
                )}
                <Shield className="w-4 h-4 shrink-0" />
                <span>Admin Panel</span>
              </Link>
            </motion.div>
          )}

          {/* Mission Control Indicator */}
          <AgentMissionControl />
        </motion.div>
      </nav>

      {/* User footer */}
      <div className="p-4 border-t border-white/6 bg-white/2">
        <motion.div
          whileHover={{ scale: 1.01 }}
          className="flex items-center gap-3 px-3 py-3 rounded-xl bg-white/4 border border-white/6 hover:border-white/10 transition-all cursor-pointer group"
        >
          <motion.div
            whileHover={{ scale: 1.1, rotate: 4 }}
            className="w-9 h-9 rounded-full bg-[#050505] border border-[#2a2a2a] flex items-center justify-center text-sm font-black text-white shadow-sm"
          >
            {user?.full_name?.charAt(0)?.toUpperCase() ?? "A"}
          </motion.div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-bold text-white truncate tracking-tight">{user?.full_name ?? "User"}</p>
            <p className={cn("text-[10px] uppercase font-black tracking-widest mt-0.5", planColor)}>{planLabel}</p>
          </div>
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={handleLogout}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-zinc-600 hover:bg-red-500/15 hover:text-red-400 transition-colors"
            title="Logout"
          >
            <LogOut className="w-4 h-4" />
          </motion.button>
        </motion.div>
      </div>
    </aside>
  );
}

function AgentMissionControl() {
  const { isWorking, currentTask } = useAgentStatus();
  const taskInfo = currentTask ? TASK_MAP[currentTask] : null;

  return (
    <AnimatePresence>
      {isWorking && (
        <motion.div
          initial={{ opacity: 0, y: 10, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 10, scale: 0.95 }}
          className="mt-6 px-3"
        >
          <div className="bg-white/[0.03] border border-white/10 rounded-2xl p-4 relative overflow-hidden group hover:border-white/20 transition-colors">
            {/* Background Activity Pulse */}
            <div className="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent pointer-events-none" />
            <motion.div
              animate={{ 
                opacity: [0.3, 0.6, 0.3],
                scale: [1, 1.05, 1] 
              }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
              className="absolute -right-4 -top-4 w-24 h-24 bg-white/[0.02] rounded-full blur-2xl pointer-events-none"
            />

            <div className="flex items-center gap-3 relative z-10">
              <div className="relative">
                <div className="w-8 h-8 rounded-lg bg-black border border-white/10 flex items-center justify-center">
                  {taskInfo ? (
                    <taskInfo.icon className="w-4 h-4 text-white" />
                  ) : (
                    <RefreshCw className="w-4 h-4 text-white animate-spin" />
                  )}
                </div>
              </div>
              
              <div className="flex-1 min-w-0">
                <p className="text-[10px] font-black text-zinc-500 uppercase tracking-widest mb-0.5">Mission Active</p>
                <p className="text-xs font-bold text-white truncate tracking-tight">
                  {taskInfo?.label || "Processing..."}
                </p>
              </div>
            </div>

            {/* Micro-progress bar */}
            <div className="mt-3 h-1 bg-white/[0.05] rounded-full overflow-hidden">
              <motion.div
                animate={{ x: ["-100%", "100%"] }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                className="w-1/2 h-full bg-gradient-to-r from-transparent via-white/20 to-transparent"
              />
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
