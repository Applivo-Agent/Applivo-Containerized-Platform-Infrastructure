"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { useSubscription } from "@/lib/subscription";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard, Briefcase, FileText, BarChart2,
  MessageSquare, Settings, LogOut, Crown, Zap,
  Users, Shield, ChevronRight, BookOpen,
  TrendingUp, Mail, Bell, Link2, CreditCard,
  Layers, Target, Star,
} from "lucide-react";

const navGroups = [
  {
    label: "Core",
    items: [
      { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
      { href: "/jobs", icon: Briefcase, label: "Jobs" },
      { href: "/applications", icon: Layers, label: "Applications" },
      { href: "/resumes", icon: FileText, label: "Resumes" },
      { href: "/analytics", icon: BarChart2, label: "Analytics" },
      { href: "/chat", icon: MessageSquare, label: "AI Chat" },
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
      { href: "/security", icon: Shield, label: "Security" },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();
  const { plan, quota, subscription } = useSubscription();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  const quotaPercent = quota ? Math.round((quota.used / quota.limit) * 100) : 0;
  const quotaColor =
    quotaPercent >= 90 ? "#ef4444" :
    quotaPercent >= 70 ? "#f59e0b" : "#10b981";

  const planLabel = plan === "starter" ? "Starter" : plan === "pro" ? "Pro" : plan === "premium" ? "Premium" : "No Plan";
  const planColor =
    plan === "premium" ? "text-amber-400" :
    plan === "pro" ? "text-violet-400" : "text-zinc-400";

  return (
    <aside className="fixed left-0 top-0 h-full w-60 flex flex-col bg-card border-r border-border z-30">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-border">
        <Link href="/dashboard" className="flex items-center gap-2.5 group">
          <img src="/logo.JPG" alt="Applivo" className="w-8 h-8 rounded-lg group-hover:scale-105 transition-transform object-cover" />
          <span className="text-lg font-bold font-display gradient-text">Applivo</span>
        </Link>
      </div>

      {/* Quota ring */}
      {quota && (
        <div className="px-4 py-3 border-b border-border">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs text-muted-foreground">Daily Quota</span>
            <span className="text-xs font-medium" style={{ color: quotaColor }}>
              {quota.used}/{quota.limit}
            </span>
          </div>
          <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{ width: `${Math.min(quotaPercent, 100)}%`, background: quotaColor }}
            />
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-4">
        {navGroups.map((group) => (
          <div key={group.label}>
            <p className="px-3 mb-1 text-[10px] font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1">
              {group.label}
              {group.pro && <span className="text-[9px] bg-violet-500/20 text-violet-400 px-1.5 py-0.5 rounded-full">PRO</span>}
              {group.premium && <span className="text-[9px] bg-amber-500/20 text-amber-400 px-1.5 py-0.5 rounded-full">PREMIUM</span>}
            </p>
            <ul className="space-y-0.5">
              {group.items.map((item) => {
                const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
                const isSuper = user?.is_superuser ?? false;
                const needsPro = (item as any).plan === "pro" && plan !== "pro" && plan !== "premium";
                const needsPremium = (item as any).plan === "premium" && plan !== "premium";
                const isLocked = !isSuper && (needsPro || needsPremium);

                return (
                  <li key={item.href}>
                    <Link
                      href={isLocked ? "/pricing" : item.href}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-150 group",
                        isActive
                          ? "bg-brand-purple/15 text-brand-purple-light border-r-2 border-brand-purple"
                          : "text-muted-foreground hover:text-foreground hover:bg-white/5",
                        isLocked && "opacity-50"
                      )}
                    >
                      <item.icon className={cn("w-4 h-4 shrink-0", isActive ? "text-brand-purple-light" : "")} />
                      <span className="flex-1">{item.label}</span>
                      {isLocked && (
                        <Crown className="w-3 h-3 text-amber-400" />
                      )}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}

        {/* Admin link */}
        {user?.is_superuser && (
          <div>
            <p className="px-3 mb-1 text-[10px] font-semibold text-red-400 uppercase tracking-wider">Admin</p>
            <Link
              href="/admin"
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all",
                pathname.startsWith("/admin")
                  ? "bg-red-500/15 text-red-400"
                  : "text-muted-foreground hover:text-foreground hover:bg-white/5"
              )}
            >
              <Shield className="w-4 h-4" />
              <span>Admin Panel</span>
            </Link>
          </div>
        )}
      </nav>

      {/* User profile footer */}
      <div className="border-t border-border p-3">
        <div className="flex items-center gap-3 px-2 py-2 rounded-lg hover:bg-white/5 transition-colors">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-brand-purple to-brand-blue flex items-center justify-center text-xs font-bold text-white shrink-0">
            {user?.full_name?.charAt(0)?.toUpperCase() ?? "A"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user?.full_name ?? "User"}</p>
            <p className={cn("text-[11px] font-medium", planColor)}>{planLabel}</p>
          </div>
          <button
            onClick={handleLogout}
            className="text-muted-foreground hover:text-red-400 transition-colors"
            title="Logout"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
