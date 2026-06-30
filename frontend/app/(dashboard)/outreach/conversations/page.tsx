"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  MessageSquare, Clock, CheckCircle2, AlertCircle,
  Calendar, ChevronRight, Star,
} from "lucide-react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: any }> = {
  AWAITING_REPLY:   { label: "Awaiting Reply",    color: "#6b7280", icon: Clock },
  REPLIED:          { label: "Replied",            color: "#10b981", icon: CheckCircle2 },
  INTERVIEW_SCHEDULED: { label: "Interview Scheduled",  color: "#f59e0b", icon: AlertCircle },
  OFFER_RECEIVED:   { label: "Offer Received",     color: "#f59e0b", icon: Star },
  DECLINED:         { label: "Declined",           color: "#374151", icon: CheckCircle2 },
  ARCHIVED:         { label: "Archived",           color: "#4b5563", icon: Clock },
};

const STATUSES = Object.keys(STATUS_CONFIG);

function useConversations(statusFilter: string | null) {
  return useQuery({
    queryKey: ["outreach-conversations", statusFilter],
    queryFn: async () => {
      const params = new URLSearchParams({ limit: "100" });
      if (statusFilter) params.set("status", statusFilter);
      const res = await api.get(`/outreach/conversations?${params}`);
      return res.data as any[];
    },
    staleTime: 15_000,
    refetchInterval: 30_000,
  });
}

function ConversationDetail({ conv, onClose }: { conv: any; onClose: () => void }) {
  const qc = useQueryClient();
  const [note, setNote] = useState("");
  const [status, setStatus] = useState(conv.status);

  const updateMut = useMutation({
    mutationFn: async (data: any) => api.patch(`/outreach/conversations/${conv.id}`, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["outreach-conversations"] }),
  });

  const addNoteMut = useMutation({
    mutationFn: async () => api.post(`/outreach/conversations/${conv.id}/notes`, { note }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["outreach-conversations"] });
      setNote("");
    },
  });

  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.awaiting_reply;

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-xl bg-[#1c1c1e] border border-zinc-800 rounded-2xl overflow-hidden max-h-[90vh] flex flex-col shadow-2xl"
      >
        <div className="px-6 py-4 border-b border-zinc-800 flex items-center justify-between">
          <div>
            <p className="text-sm font-bold tracking-tight text-white">{conv.company_id || "Unknown Company"}</p>
            <span
              className="text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border mt-1 inline-block"
              style={{ color: cfg.color, borderColor: `${cfg.color}40`, background: `${cfg.color}12` }}
            >
              {cfg.label}
            </span>
          </div>
          <button onClick={onClose} className="p-1.5 text-zinc-500 hover:text-white transition-colors rounded-lg hover:bg-white/[0.05]">
            ×
          </button>
        </div>

        <div className="overflow-y-auto flex-1 p-6 space-y-5">
          <div>
            <label className="text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2 block">Update status</label>
            <div className="grid grid-cols-2 gap-2">
              {STATUSES.slice(0, 6).map(s => {
                const c = STATUS_CONFIG[s];
                return (
                  <button
                    key={s}
                    onClick={() => {
                      setStatus(s);
                      updateMut.mutate({ status: s });
                    }}
                    className={cn(
                      "py-2 px-3 rounded-xl text-xs font-bold uppercase tracking-wider border text-left transition-all",
                      status === s ? "border-white/25 bg-white/10 text-white" : "border-zinc-800 text-zinc-500 hover:text-zinc-300 hover:border-zinc-700"
                    )}
                    style={status === s ? { borderColor: `${c.color}40`, background: `${c.color}12`, color: c.color } : {}}
                  >
                    {c.label}
                  </button>
                );
              })}
            </div>
          </div>

          {conv.ai_summary && (
            <div className="p-4 rounded-xl bg-[#1d1d1d] border border-white/[0.08]">
              <p className="text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2">AI Summary</p>
              <p className="text-xs text-zinc-300 leading-relaxed">{conv.ai_summary}</p>
            </div>
          )}

          {conv.next_action && (
            <div className="flex items-start gap-3 p-4 rounded-xl bg-[#1d1d1d] border border-amber-500/20">
              <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-[11px] font-bold uppercase tracking-wider text-amber-400 mb-1">Next Action</p>
                <p className="text-xs text-zinc-300">{conv.next_action}</p>
                {conv.next_action_due && (
                  <p className="text-[10px] text-zinc-500 mt-1">Due: {new Date(conv.next_action_due).toLocaleDateString()}</p>
                )}
              </div>
            </div>
          )}

          {conv.interview_date && (
            <div className="flex items-center gap-3 p-4 rounded-xl bg-[#1d1d1d] border border-cyan-500/20">
              <Calendar className="w-4 h-4 text-cyan-400" />
              <div>
                <p className="text-[11px] font-bold uppercase tracking-wider text-cyan-400">Interview Scheduled</p>
                <p className="text-xs text-zinc-300 mt-1">{new Date(conv.interview_date).toLocaleString()}</p>
              </div>
            </div>
          )}

          {conv.notes && (
            <div>
              <p className="text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2">Notes</p>
              <div className="p-3 rounded-xl bg-[#1d1d1d] border border-white/[0.08]">
                <p className="text-xs text-zinc-300 whitespace-pre-line leading-relaxed">{conv.notes}</p>
              </div>
            </div>
          )}

          <div>
            <label className="text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-1.5 block">Add note</label>
            <div className="flex gap-2">
              <input
                value={note}
                onChange={e => setNote(e.target.value)}
                placeholder="What happened? Any key info..."
                className="flex-1 px-3 py-2 bg-[#1d1d1d] border border-white/[0.08] rounded-xl text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-white/25 transition-colors"
                onKeyDown={e => e.key === "Enter" && note.trim() && addNoteMut.mutate()}
              />
              <button
                onClick={() => addNoteMut.mutate()}
                disabled={!note.trim() || addNoteMut.isPending}
                className="px-4 py-2 rounded-xl bg-white hover:bg-zinc-200 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-bold text-black uppercase tracking-widest transition-colors"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

export default function ConversationsPage() {
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [selected, setSelected] = useState<any>(null);

  const { data: conversations = [], isLoading } = useConversations(statusFilter);

  const priorityStatuses = ["REPLIED", "INTERVIEW_SCHEDULED", "OFFER_RECEIVED"];
  const attention = conversations.filter(c => priorityStatuses.includes(c.status));

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 p-1 md:p-4 min-h-[90vh]">

      <div>
        <h2 className="text-xl font-bold tracking-tight text-white/90">Conversations</h2>
        <p className="text-[11px] text-zinc-400 mt-1">Track replies, manage follow-ups, log interviews</p>
      </div>

      {attention.length > 0 && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 p-4 bg-indigo-500/10 border border-indigo-500/30 rounded-xl">
          <AlertCircle className="w-5 h-5 text-indigo-400 shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-medium text-indigo-400">
              {attention.length} conversation{attention.length > 1 ? "s" : ""} need your attention
            </p>
            <p className="text-xs text-indigo-400/70">Replies and follow-ups waiting</p>
          </div>
          <button
            onClick={() => setStatusFilter("REPLIED")}
            className="px-4 py-1.5 bg-white text-black text-xs font-bold uppercase tracking-widest rounded-lg hover:bg-zinc-200 transition-colors whitespace-nowrap"
          >
            Review →
          </button>
        </motion.div>
      )}

      {/* Status filters */}
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => setStatusFilter(null)}
          className={cn(
            "px-3 py-1.5 rounded-lg text-[11px] font-bold uppercase tracking-wider border transition-all",
            statusFilter === null ? "border-white/25 bg-white/10 text-white" : "border-zinc-800 text-zinc-500 hover:text-zinc-300 hover:border-zinc-700"
          )}
        >
          All ({conversations.length})
        </button>
        {Object.entries(STATUS_CONFIG).map(([s, cfg]) => {
          const count = conversations.filter(c => c.status === s).length;
          if (count === 0 && statusFilter !== s) return null;
          return (
            <button
              key={s}
              onClick={() => setStatusFilter(statusFilter === s ? null : s)}
              className={cn(
                "px-3 py-1.5 rounded-lg text-[11px] font-bold uppercase tracking-wider border transition-all",
                statusFilter === s ? "border-white/25 text-white" : "border-zinc-800 text-zinc-500 hover:text-zinc-300 hover:border-zinc-700"
              )}
              style={statusFilter === s ? { color: cfg.color, background: `${cfg.color}18`, borderColor: `${cfg.color}40` } : {}}
            >
              {cfg.label} {count > 0 && `(${count})`}
            </button>
          );
        })}
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-20 bg-[#1c1c1e] border border-zinc-800 rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : conversations.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 text-center bg-[#1c1c1e] border border-zinc-800 rounded-2xl">
          <div className="w-16 h-16 rounded-full bg-[#1d1d1d] border border-white/[0.08] flex items-center justify-center mx-auto mb-6">
            <MessageSquare className="w-7 h-7 text-zinc-600" />
          </div>
          <p className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400 mb-2">No Conversations Yet</p>
          <p className="text-[9px] font-bold text-zinc-600 max-w-[200px] mx-auto uppercase tracking-wider leading-relaxed italic">
            Send your first outreach email to start tracking conversations.
          </p>
        </div>
      ) : (
        <div className="bg-[#242424] border border-white/[0.08] rounded-2xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-bold text-lg tracking-tight">
              {statusFilter ? STATUS_CONFIG[statusFilter]?.label : "All Conversations"}
            </h3>
            <span className="text-[11px] font-bold text-zinc-400">{conversations.length} total</span>
          </div>
          <div className="space-y-3">
            {conversations.map((conv: any) => {
              const cfg = STATUS_CONFIG[conv.status] || STATUS_CONFIG.awaiting_reply;
              const Icon = cfg.icon;
              return (
                <motion.div
                  key={conv.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  onClick={() => setSelected(conv)}
                  className="flex items-center gap-4 p-4 bg-[#1d1d1d] border border-white/[0.08] rounded-2xl hover:border-white/20 hover:bg-[#252525] cursor-pointer transition-all group"
                >
                  <div className="w-10 h-10 rounded-xl bg-[#222222] border border-white/[0.08] flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform" style={{ background: `${cfg.color}15` }}>
                    <Icon className="w-4 h-4" style={{ color: cfg.color }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-bold text-white truncate">{conv.company_id || "Unknown"}</p>
                      {conv.next_action_due && new Date(conv.next_action_due) < new Date() && (
                        <span className="text-[9px] font-black uppercase tracking-wider text-red-400 bg-red-400/10 border border-red-400/20 px-1.5 py-0.5 rounded-md">Overdue</span>
                      )}
                    </div>
                    <p className="text-[11px] text-zinc-500 truncate mt-0.5">{conv.next_action || conv.ai_summary || "No summary yet"}</p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <span
                      className="text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border"
                      style={{ color: cfg.color, borderColor: `${cfg.color}40`, background: `${cfg.color}12` }}
                    >
                      {cfg.label}
                    </span>
                    {conv.last_message_at && (
                      <p className="text-[10px] text-zinc-600 mt-1">{new Date(conv.last_message_at).toLocaleDateString()}</p>
                    )}
                  </div>
                  <ChevronRight className="w-4 h-4 text-zinc-600 group-hover:text-zinc-300 transition-colors flex-shrink-0" />
                </motion.div>
              );
            })}
          </div>
        </div>
      )}

      {selected && <ConversationDetail conv={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
