"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import {
  Radio, Plus, Play, Pause, Clock, CheckCircle2,
  Loader2, X, Send, MessageSquare, TrendingUp,
} from "lucide-react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  draft:     { label: "Draft",     color: "#6b7280" },
  active:    { label: "Active",    color: "#10b981" },
  paused:    { label: "Paused",    color: "#f59e0b" },
  completed: { label: "Completed", color: "#3b82f6" },
  archived:  { label: "Archived",  color: "#374151" },
};

function useCampaigns() {
  return useQuery({
    queryKey: ["outreach-campaigns"],
    queryFn: async () => {
      const res = await api.get("/outreach/campaigns");
      return res.data as any[];
    },
    staleTime: 15_000,
  });
}

function NewCampaignModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const [goal, setGoal] = useState("JOB_SEARCH");
  const [dailyLimit, setDailyLimit] = useState(5);

  const createMut = useMutation({
    mutationFn: async () => {
      const res = await api.post("/outreach/campaigns", { name, goal, daily_limit: dailyLimit });
      return res.data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["outreach-campaigns"] });
      onClose();
    },
  });

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.96 }}
        className="w-full max-w-md bg-[#1c1c1e] border border-zinc-800 rounded-2xl p-6 shadow-2xl"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-bold tracking-tight text-white">New Campaign</h2>
          <button onClick={onClose} className="p-1.5 text-zinc-500 hover:text-white transition-colors rounded-lg hover:bg-white/[0.05]">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-1.5 block">Campaign name *</label>
            <input
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="e.g. Q3 SWE Outreach — Seed Stage"
              className="w-full px-3 py-2.5 bg-[#1d1d1d] border border-white/[0.08] rounded-xl text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-white/25 transition-colors"
              autoFocus
            />
          </div>

          <div>
            <label className="text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-1.5 block">Goal</label>
            <div className="grid grid-cols-3 gap-2">
              {[["JOB_SEARCH", "Job Search"], ["NETWORKING", "Networking"], ["REFERRAL", "Referral"]].map(([val, label]) => (
                <button
                  key={val}
                  onClick={() => setGoal(val)}
                  className={cn(
                    "py-2 rounded-xl text-xs font-bold uppercase tracking-wider border transition-all",
                    goal === val ? "border-white/25 bg-white/10 text-white" : "border-zinc-800 text-zinc-500 hover:text-zinc-300 hover:border-zinc-700"
                  )}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-1.5 block">
              Daily email limit: <span className="text-white normal-case tracking-normal font-semibold">{dailyLimit}</span>
            </label>
            <div className="relative w-full h-2 bg-white/[0.06] rounded-full mt-2">
              <div
                className="absolute h-full bg-white rounded-full transition-all"
                style={{ width: `${((dailyLimit - 1) / 14) * 100}%` }}
              />
              <input
                type="range" min={1} max={15} value={dailyLimit}
                onChange={e => setDailyLimit(Number(e.target.value))}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
            </div>
            <div className="flex justify-between text-[10px] text-zinc-600 mt-1">
              <span>1 · conservative</span>
              <span>15 · aggressive</span>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-[#1d1d1d] border border-white/[0.08] text-[11px] text-zinc-500 leading-relaxed">
            The campaign defines delivery settings. Add companies to the campaign after creation.
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <button onClick={onClose} className="flex-1 py-2.5 rounded-xl border border-zinc-800 text-sm text-zinc-400 hover:text-white hover:border-zinc-700 transition-colors">
            Cancel
          </button>
          <button
            onClick={() => createMut.mutate()}
            disabled={!name.trim() || createMut.isPending}
            className="flex-1 py-2.5 rounded-xl bg-white hover:bg-zinc-200 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-bold uppercase tracking-widest text-black transition-colors flex items-center justify-center gap-2"
          >
            {createMut.isPending ? <Loader2 className="w-4 h-4 animate-spin text-black" /> : <Plus className="w-4 h-4" />}
            Create
          </button>
        </div>
      </motion.div>
    </div>
  );
}

function CampaignCard({ campaign }: { campaign: any }) {
  const qc = useQueryClient();
  const cfg = STATUS_CONFIG[campaign.status] || STATUS_CONFIG.draft;
  const stats = campaign.stats || {};

  const launchMut = useMutation({
    mutationFn: async () => api.post(`/outreach/campaigns/${campaign.id}/launch`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["outreach-campaigns"] }),
  });

  const pauseMut = useMutation({
    mutationFn: async () => api.post(`/outreach/campaigns/${campaign.id}/pause`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["outreach-campaigns"] }),
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4, scale: 1.01 }}
      className="bg-[#1c1c1e] border border-zinc-800 rounded-2xl p-5 group relative overflow-hidden transition-all hover:border-white/25 hover:shadow-[0_0_0_1px_rgba(255,255,255,0.14),0_20px_40px_rgba(0,0,0,0.45)]"
    >
      <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-white/10 via-white/5 to-transparent rounded-full -mr-12 -mt-12 group-hover:scale-150 transition-transform duration-500" />

      <div className="relative z-10">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-bold text-white truncate">{campaign.name}</h3>
            <p className="text-[11px] text-zinc-500 capitalize mt-0.5">{campaign.goal?.replace(/_/g, " ")}</p>
          </div>
          <span
            className="text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border ml-3 flex-shrink-0"
            style={{ color: cfg.color, borderColor: `${cfg.color}40`, background: `${cfg.color}12` }}
          >
            {cfg.label}
          </span>
        </div>

        <div className="grid grid-cols-4 gap-2 mb-4">
          {[
            { label: "Sent",       value: stats.sent ?? 0,       icon: Send,          color: "#6b7280" },
            { label: "Opened",     value: stats.opened ?? 0,     icon: CheckCircle2,  color: "#3b82f6" },
            { label: "Replied",    value: stats.replied ?? 0,    icon: MessageSquare, color: "#10b981" },
            { label: "Interviews", value: stats.interviews ?? 0, icon: TrendingUp,    color: "#f59e0b" },
          ].map(s => (
            <div key={s.label} className="text-center p-2.5 rounded-xl bg-[#1d1d1d] border border-white/[0.06]">
              <p className="text-lg font-bold tabular-nums tracking-tighter" style={{ color: s.value > 0 ? s.color : "#374151" }}>{s.value}</p>
              <p className="text-[9px] font-bold uppercase tracking-wider text-zinc-600 mt-0.5">{s.label}</p>
            </div>
          ))}
        </div>

        <div className="flex gap-2">
          {campaign.status === "DRAFT" && (
            <button
              onClick={() => launchMut.mutate()}
              disabled={launchMut.isPending}
              className="flex-1 py-2 rounded-xl bg-[#1d1d1d] hover:bg-[#222222] border border-white/[0.08] hover:border-emerald-500/30 text-xs font-bold uppercase tracking-wider text-zinc-400 hover:text-emerald-400 transition-all flex items-center justify-center gap-1.5"
            >
              {launchMut.isPending ? <Loader2 className="w-3 h-3 animate-spin" /> : <Play className="w-3 h-3" />}
              Launch
            </button>
          )}
          {campaign.status === "ACTIVE" && (
            <button
              onClick={() => pauseMut.mutate()}
              disabled={pauseMut.isPending}
              className="flex-1 py-2 rounded-xl bg-[#1d1d1d] hover:bg-[#222222] border border-white/[0.08] hover:border-amber-500/30 text-xs font-bold uppercase tracking-wider text-zinc-400 hover:text-amber-400 transition-all flex items-center justify-center gap-1.5"
            >
              {pauseMut.isPending ? <Loader2 className="w-3 h-3 animate-spin" /> : <Pause className="w-3 h-3" />}
              Pause
            </button>
          )}
          {campaign.status === "PAUSED" && (
            <button
              onClick={() => launchMut.mutate()}
              disabled={launchMut.isPending}
              className="flex-1 py-2 rounded-xl bg-[#1d1d1d] hover:bg-[#222222] border border-white/[0.08] hover:border-emerald-500/30 text-xs font-bold uppercase tracking-wider text-zinc-400 hover:text-emerald-400 transition-all flex items-center justify-center gap-1.5"
            >
              <Play className="w-3 h-3" /> Resume
            </button>
          )}
          <div className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-[#1d1d1d] border border-white/[0.06] text-[11px] text-zinc-500">
            <Clock className="w-3 h-3" />
            {campaign.daily_limit}/day
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export default function CampaignsPage() {
  const [showNew, setShowNew] = useState(false);
  const { data: campaigns = [], isLoading } = useCampaigns();

  const active = campaigns.filter(c => c.status === "ACTIVE").length;
  const drafts  = campaigns.filter(c => c.status === "DRAFT").length;

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 p-1 md:p-4 min-h-[90vh]">

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white/90">Campaigns</h2>
          <p className="text-[11px] text-zinc-400 mt-1">
            {active > 0 ? `${active} active` : "No active campaigns"}
            {drafts > 0 ? ` · ${drafts} draft${drafts > 1 ? "s" : ""}` : ""}
          </p>
        </div>
        <button
          onClick={() => setShowNew(true)}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white text-black text-sm font-bold uppercase tracking-widest hover:bg-zinc-200 transition-colors self-start md:self-auto"
        >
          <Plus className="w-4 h-4" />
          New Campaign
        </button>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-48 bg-[#1c1c1e] border border-zinc-800 rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : campaigns.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 text-center bg-[#1c1c1e] border border-zinc-800 rounded-2xl">
          <div className="w-16 h-16 rounded-full bg-[#1d1d1d] border border-white/[0.08] flex items-center justify-center mx-auto mb-6">
            <Radio className="w-7 h-7 text-zinc-600" />
          </div>
          <p className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400 mb-2">No Campaigns Yet</p>
          <p className="text-[9px] font-bold text-zinc-600 max-w-[200px] mx-auto uppercase tracking-wider leading-relaxed italic mb-6">
            Create a campaign to organize and track your outreach efforts.
          </p>
          <button
            onClick={() => setShowNew(true)}
            className="px-5 py-2.5 bg-white text-black text-[11px] font-bold uppercase tracking-widest rounded-xl hover:bg-zinc-200 transition-colors"
          >
            Create First Campaign
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {campaigns.map((c: any) => (
            <CampaignCard key={c.id} campaign={c} />
          ))}
        </div>
      )}

      <AnimatePresence>
        {showNew && <NewCampaignModal onClose={() => setShowNew(false)} />}
      </AnimatePresence>
    </div>
  );
}
