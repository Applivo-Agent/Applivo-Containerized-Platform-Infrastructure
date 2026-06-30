"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  Building2, Mail, MessageSquare, Plus, ArrowRight,
  CheckCircle2, Clock, Zap, Target, BarChart3,
  AlertCircle, ChevronRight,
} from "lucide-react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

function useOutreachHub() {
  return useQuery({
    queryKey: ["outreach-hub"],
    queryFn: async () => (await api.get("/outreach/hub")).data,
    staleTime: 30_000,
    refetchInterval: 60_000,
  });
}

function StatCard({
  icon: Icon, label, badge, value, sub, delay = 0, urgent = false, onClick,
}: {
  icon: any; label: string; badge: string; value: number; sub?: string;
  delay?: number; urgent?: boolean; onClick?: () => void;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      whileHover={{ y: -4, scale: 1.01 }}
      onClick={onClick}
      className={cn(
        "bg-[#1c1c1e] border rounded-2xl p-5 group cursor-pointer relative overflow-hidden transition-all",
        urgent ? "border-amber-500/40" : "border-zinc-800",
        "hover:border-white/25 hover:shadow-[0_0_0_1px_rgba(255,255,255,0.14),0_20px_40px_rgba(0,0,0,0.45)]"
      )}
    >
      <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-white/10 via-white/5 to-transparent rounded-full -mr-12 -mt-12 group-hover:scale-150 transition-transform duration-500" />
      <div className="relative z-10 flex flex-col h-full justify-between">
        <div className="flex items-center justify-between mb-3">
          <div className="w-10 h-10 rounded-xl bg-[#222222] flex items-center justify-center transition-all group-hover:scale-110">
            <Icon className="w-5 h-5 text-zinc-400 group-hover:text-white transition-colors" />
          </div>
          <span className="text-[9px] font-bold uppercase tracking-wider text-zinc-400 bg-[#1c1c1e] border border-zinc-800 px-2 py-0.5 rounded-md">
            {badge}
          </span>
        </div>
        <div>
          <p className="text-[11px] font-medium text-zinc-400 mb-1">{label}</p>
          <h4 className="text-3xl font-bold tracking-tighter text-white">{value}</h4>
          {sub && <p className="text-[10px] text-zinc-400 mt-2 font-medium">{sub}</p>}
        </div>
      </div>
    </motion.div>
  );
}

export default function OutreachPage() {
  const router = useRouter();
  const { data, isLoading } = useOutreachHub();

  const pipeline = data?.pipeline || {};
  const emailStats = data?.email_stats || {};
  const hotCompanies = data?.hot_companies || [];

  const funnelSteps = [
    { label: "Researched", value: pipeline.companies_added ?? 0, color: "#6b7280" },
    { label: "Contacted",  value: pipeline.contacted ?? 0,       color: "#8b5cf6" },
    { label: "Replied",    value: pipeline.replied ?? 0,          color: "#3b82f6" },
    { label: "Interview",  value: pipeline.interviewing ?? 0,     color: "#10b981" },
    { label: "Offer",      value: pipeline.offer ?? 0,            color: "#f59e0b" },
  ];
  const maxFunnel = Math.max(...funnelSteps.map(s => s.value), 1);

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 p-1 md:p-4 min-h-[90vh]">

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <h2 className="text-xl font-bold tracking-tight text-white/90 hidden md:block">Outreach</h2>
        <div className="flex items-center gap-3">
          <motion.button
            onClick={() => router.push("/outreach/campaigns")}
            whileTap={{ scale: 0.97 }}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium border bg-[#171717] hover:bg-[#222222] text-white border-[#262626] transition-all"
          >
            <Zap className="w-4 h-4 text-zinc-400" />
            Campaigns
          </motion.button>
          <motion.button
            onClick={() => router.push("/outreach/companies")}
            whileTap={{ scale: 0.97 }}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white text-black text-sm font-bold uppercase tracking-widest hover:bg-zinc-200 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add Company
          </motion.button>
        </div>
      </div>

      {/* Attention banner */}
      {(data?.needs_attention ?? 0) > 0 && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 p-4 bg-indigo-500/10 border border-indigo-500/30 rounded-xl">
          <AlertCircle className="w-5 h-5 text-indigo-400 shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-medium text-indigo-400">
              {data.needs_attention} conversation{data.needs_attention > 1 ? "s" : ""} received a reply and need your attention.
            </p>
            <p className="text-xs text-indigo-400/70">Review and respond to keep momentum</p>
          </div>
          <button
            onClick={() => router.push("/outreach/conversations")}
            className="px-4 py-1.5 bg-white text-black text-xs font-bold uppercase tracking-widest rounded-lg hover:bg-zinc-200 transition-colors whitespace-nowrap"
          >
            Review →
          </button>
        </motion.div>
      )}

      {/* Stat cards */}
      {isLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-[#1c1c1e] border border-zinc-800 rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard icon={Building2}     label="Companies Added"  badge="Total"    value={pipeline.companies_added ?? 0}       sub={`${pipeline.contacted ?? 0} contacted`}      delay={0}    onClick={() => router.push("/outreach/companies")} />
          <StatCard icon={Mail}          label="Emails Sent"      badge="Outreach" value={emailStats.sent ?? 0}                sub={`${emailStats.reply_rate ?? 0}% reply rate`}  delay={0.08} onClick={() => router.push("/outreach/conversations")} />
          <StatCard icon={MessageSquare} label="Replies Received" badge="Inbox"    value={emailStats.replied ?? 0}            sub={`${pipeline.interviewing ?? 0} interviewing`}  delay={0.16} onClick={() => router.push("/outreach/conversations")} />
          <StatCard icon={Clock}         label="Pending Approval" badge="Review"   value={emailStats.pending_approvals ?? 0}  sub="drafts awaiting review"                       delay={0.24} urgent={(emailStats.pending_approvals ?? 0) > 0} onClick={() => router.push("/outreach/companies")} />
        </div>
      )}

      {/* Career Funnel + Hot Companies */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">

        <div className="lg:col-span-2 bg-[#242424] border border-white/[0.08] rounded-2xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-bold text-lg tracking-tight">Career Funnel</h3>
              <p className="text-[11px] text-zinc-400 mt-0.5">From research to offer</p>
            </div>
            <BarChart3 className="w-4 h-4 text-zinc-600" />
          </div>
          <div className="space-y-4">
            {funnelSteps.map((step) => (
              <div key={step.label}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[11px] font-medium text-zinc-400">{step.label}</span>
                  <span className="text-[11px] font-bold text-white tabular-nums">{step.value}</span>
                </div>
                <div className="h-2 bg-white/[0.04] rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(step.value / maxFunnel) * 100}%` }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="h-full rounded-full"
                    style={{ background: step.color }}
                  />
                </div>
              </div>
            ))}
          </div>
          {(pipeline.replied ?? 0) > 0 && (pipeline.contacted ?? 0) > 0 && (
            <div className="mt-5 pt-5 border-t border-white/[0.06] flex items-center gap-2 text-[11px] text-zinc-400">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              Reply rate: <span className="text-emerald-400 font-bold">{((pipeline.replied / pipeline.contacted) * 100).toFixed(1)}%</span>
            </div>
          )}
        </div>

        <div className="bg-[#242424] border border-white/[0.08] rounded-2xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-bold text-lg tracking-tight">Hot Companies</h3>
            <button onClick={() => router.push("/outreach/companies")} className="text-xs font-bold text-white hover:underline flex items-center gap-1">
              View all <ChevronRight className="w-3 h-3" />
            </button>
          </div>
          {hotCompanies.length > 0 ? (
            <div className="space-y-3">
              {hotCompanies.map((company: any, i: number) => (
                <motion.div
                  key={company.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + i * 0.05 }}
                  onClick={() => router.push("/outreach/companies")}
                  className="flex items-center gap-3 p-4 bg-[#1d1d1d] border border-white/[0.08] rounded-2xl hover:border-white/20 hover:bg-[#252525] transition-all cursor-pointer group"
                >
                  <div className="w-9 h-9 rounded-xl bg-[#222222] flex items-center justify-center shrink-0 border border-white/[0.08] group-hover:scale-110 transition-transform">
                    <Building2 className="w-4 h-4 text-zinc-400 group-hover:text-white transition-colors" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-bold truncate text-white">{company.name}</p>
                    <p className="text-xs text-zinc-400 capitalize mt-0.5">{company.status?.replace(/_/g, " ")}</p>
                  </div>
                  {company.match_score && (
                    <span className="px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-tighter bg-emerald-500/15 text-emerald-400">
                      {Math.round(company.match_score)}%
                    </span>
                  )}
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-10 text-center">
              <div className="w-12 h-12 rounded-full bg-[#1d1d1d] border border-white/[0.08] flex items-center justify-center mx-auto mb-4">
                <Building2 className="w-5 h-5 text-zinc-600" />
              </div>
              <p className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400 mb-2">No Companies Yet</p>
              <p className="text-[9px] font-bold text-zinc-600 max-w-[180px] mx-auto uppercase tracking-wider leading-relaxed italic mb-4">
                Add companies to start your outreach campaign
              </p>
              <button
                onClick={() => router.push("/outreach/companies")}
                className="px-4 py-1.5 bg-white text-black text-[9px] font-black uppercase tracking-tighter rounded-lg hover:bg-zinc-200 transition-colors"
              >
                Add Company
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-[#242424] border border-white/[0.08] rounded-2xl p-6"
      >
        <h3 className="font-bold text-lg tracking-tight mb-6">Quick Actions</h3>
        <div className="space-y-3">
          {[
            { title: "Research a Company",  desc: "AI analyzes culture, tech stack, and generates personalization hooks", icon: Target,        href: "/outreach/companies" },
            { title: "Build a Campaign",    desc: "Set up a multi-company outreach campaign with AI-written emails",     icon: Zap,           href: "/outreach/campaigns" },
            { title: "View Conversations",  desc: "Track replies, manage follow-ups, and handle interview invitations",  icon: MessageSquare, href: "/outreach/conversations" },
          ].map((item, i) => (
            <motion.div
              key={item.title}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 + i * 0.05 }}
              onClick={() => router.push(item.href)}
              className="flex items-center gap-4 p-4 bg-[#1d1d1d] border border-white/[0.08] rounded-2xl hover:border-white/20 hover:bg-[#252525] transition-all cursor-pointer group"
            >
              <div className="w-12 h-12 rounded-xl bg-[#1c1c1c] shadow-sm flex items-center justify-center shrink-0 border border-white/[0.08] group-hover:scale-110 transition-transform">
                <item.icon className="w-6 h-6 text-zinc-400 group-hover:text-white transition-colors" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold text-white">{item.title}</p>
                <p className="text-xs text-zinc-400 mt-0.5">{item.desc}</p>
              </div>
              <ArrowRight className="w-4 h-4 text-zinc-600 group-hover:text-zinc-300 transition-colors flex-shrink-0" />
            </motion.div>
          ))}
        </div>
      </motion.div>

    </div>
  );
}
