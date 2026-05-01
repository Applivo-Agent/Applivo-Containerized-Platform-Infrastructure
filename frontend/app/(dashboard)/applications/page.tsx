"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { applicationsApi, agentApi } from "@/lib/api";
import { cn, getStatusClass, getStatusLabel, timeAgo, formatDate } from "@/lib/utils";
import Link from "next/link";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { Search, Filter, LayoutGrid, List, SlidersHorizontal, Check, Star, RefreshCw, ChevronRight, AlertCircle, Play, Loader2, Layers } from "lucide-react";

const KANBAN_COLUMNS = [
  { id: "pending_approval", label: "Pending" },
  { id: "queued", label: "Queued" },
  { id: "applying", label: "Applying" },
  { id: "applied", label: "Applied" },
];

export default function ApplicationsPage() {
  const qc = useQueryClient();
  const [view, setView] = useState<"kanban" | "table">("kanban");
  const [filters, setFilters] = useState({ status: "", is_starred: undefined as boolean | undefined });
  const [page, setPage] = useState(1);
  const [isManualRefreshing, setIsManualRefreshing] = useState(false);

  const { data, isLoading, isRefetching, refetch } = useQuery({
    queryKey: ["applications", filters, page, view === "kanban" ? 100 : 20], // Load more for kanban
    queryFn: () => applicationsApi.list({ ...filters, page, page_size: view === "kanban" ? 100 : 20 }).then((r) => r.data),
  });

  const { data: stats } = useQuery({ queryKey: ["applications-stats"], queryFn: () => applicationsApi.stats().then((r) => r.data) });
  const { data: queue } = useQuery({ queryKey: ["queue-status"], queryFn: () => applicationsApi.queueStatus().then((r) => r.data) });

  const approveMut = useMutation({
    mutationFn: (id: string) => applicationsApi.approve(id),
    onSuccess: () => { toast.success("Approved! Sent to apply queue."); qc.invalidateQueries({ queryKey: ["applications"] }); qc.invalidateQueries({ queryKey: ["queue-status"] }); },
  });

  const starMut = useMutation({
    mutationFn: (id: string) => applicationsApi.star(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["applications"] }),
  });

  const triggerBot = useMutation({
    mutationFn: (id: string) => agentApi.applyOne(id),
    onSuccess: () => toast.success("Bot triggered manually! Check logs shortly."),
  });

  const isRefreshing = isManualRefreshing || isRefetching;

  const handleRefresh = async () => {
    if (isRefreshing) return;
    setIsManualRefreshing(true);
    try {
      await Promise.all([
        refetch(),
        qc.invalidateQueries({ queryKey: ["applications-stats"] }),
        qc.invalidateQueries({ queryKey: ["queue-status"] }),
      ]);
      toast.success("Applications data refreshed.");
    } finally {
      setIsManualRefreshing(false);
    }
  };

  // Group applications for Kanban
  const groupedApps = KANBAN_COLUMNS.reduce((acc, col) => {
    acc[col.id] = data?.items?.filter((app: any) => app.status?.toLowerCase() === col.id.toLowerCase()) ?? [];
    return acc;
  }, {} as Record<string, any[]>);

  const pendingApps = data?.items?.filter((a: any) => a.status?.toLowerCase() === "pending_approval") ?? [];

  return (
    <div className="dash-page space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-[#242424] border border-white/[0.08] rounded-lg">
            <Layers className="w-5 h-5 text-white" />
          </div>
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-white">Applications Flow.</h1>
            <p className="text-sm text-zinc-400 mt-1">{data?.total ?? 0} total applications tracked across your automated career growth journey.</p>
            {isRefreshing && (
              <p className="mt-2 text-xs font-semibold text-zinc-300 flex items-center gap-2">
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                Refreshing latest application activity...
              </p>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-2 px-3 py-2 bg-[#1c1c1e] hover:bg-[#2a2a2a] text-white rounded-lg text-sm font-medium transition-colors border border-[#2a2a2a] disabled:opacity-60 disabled:cursor-not-allowed"
            title={isRefreshing ? "Refreshing..." : "Refresh"}
          >
            {isRefreshing ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4 text-zinc-300" />}
            <span>{isRefreshing ? "Refreshing..." : "Refresh"}</span>
          </button>
          <div className="flex p-1.5 bg-[#1c1c1e] rounded-2xl border border-[#262626]">
            <button 
              onClick={() => setView("kanban")} 
              aria-pressed={view === "kanban"}
              className={cn(
                "px-4 py-2 flex items-center gap-2 rounded-xl text-sm font-bold transition-all", 
                view === "kanban" ? "bg-[#2a2a2a] text-white" : "text-zinc-400 hover:text-zinc-300"
              )}
            >
              <LayoutGrid className="w-4 h-4" /> Kanban
            </button>
            <button 
              onClick={() => setView("table")} 
              aria-pressed={view === "table"}
              className={cn(
                "px-4 py-2 flex items-center gap-2 rounded-xl text-sm font-bold transition-all", 
                view === "table" ? "bg-[#2a2a2a] text-white" : "text-zinc-400 hover:text-zinc-300"
              )}
            >
              <List className="w-4 h-4" /> Table
            </button>
          </div>
        </div>
      </div>

      {pendingApps.length > 0 && filters.status === "" && (
        <div className="flex items-center gap-3 p-4 bg-indigo-500/10 border border-indigo-500/30 rounded-xl mb-2">
          <AlertCircle className="w-5 h-5 text-indigo-400 shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-medium text-indigo-400">{pendingApps.length} applications pending approval</p>
          </div>
          <button onClick={() => pendingApps.forEach((a: any) => approveMut.mutate(a.id))}
            className="px-4 py-1.5 bg-white text-black rounded-lg text-xs font-medium hover:bg-zinc-200 transition-colors">
            Approve All
          </button>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 min-h-0 overflow-hidden">
        {isLoading ? (
          <div className="flex h-full items-center justify-center py-20"><div className="w-12 h-12 rounded-full border-4 border-blue-500 border-t-transparent animate-spin" /></div>
        ) : view === "kanban" ? (
          <div className="h-full overflow-x-auto pb-8 -mx-2 px-2 scrollbar-none">
            <div className="flex gap-5 h-full min-w-max">
              {KANBAN_COLUMNS.map((col) => {
                const columnApps = groupedApps[col.id] || [];
                return (
                  <div key={col.id} className="w-80 flex flex-col bg-[#242424] border border-white/[0.08] rounded-2xl p-4 max-h-[70vh] shadow-[inset_0_1px_0_rgba(255,255,255,0.035)]">
                    <div className="px-4 py-3 mb-4 flex items-center justify-between shrink-0">
                      <span className="font-bold text-[11px] tracking-[0.2em] text-zinc-300 uppercase">{col.label}</span>
                      <span className="text-[10px] font-black px-2.5 py-1 bg-[#1c1c1c] border border-white/[0.08] rounded-full text-zinc-300">{columnApps.length}</span>
                    </div>
                    <div className="flex-1 overflow-y-auto space-y-3 px-1 pb-4 scrollbar-none">
                      {columnApps.map((app) => (
                        <motion.div 
                          key={app.id} 
                          whileHover={{ y: -3 }}
                          className="bg-[#1d1d1d] p-5 rounded-2xl border border-white/[0.08] hover:border-white/20 relative group transition-all shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]"
                        >
                          <button onClick={(e) => { e.stopPropagation(); starMut.mutate(app.id); }} className="absolute top-4 right-4 text-zinc-400 hover:text-amber-400 transition-colors z-10 w-8 h-8 flex items-center justify-center">
                            <Star className={cn("w-4 h-4", app.is_starred ? "fill-amber-400 text-amber-400" : "")} />
                          </button>
                          <div className={cn("inline-block px-3 py-1 text-[9px] font-black uppercase tracking-widest rounded-full mb-3 border", getStatusClass(col.id))}>{getStatusLabel(col.id)}</div>
                          <a 
                            href={app.job?.source_url || `/applications/${app.id}`} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="block hover:opacity-80 transition-opacity"
                          >
                            <p className="font-black text-sm text-white leading-tight pr-6 tracking-tight mb-1">{app.job_title_snapshot}</p>
                            <p className="text-zinc-400 text-xs font-medium">{app.company_snapshot}</p>
                          </a>
                          
                          <div className="flex items-center justify-between mt-4 text-[10px] font-bold text-zinc-400 uppercase tracking-widest">
                            <span>{timeAgo(app.created_at)}</span>
                            {app.match_score_at_apply && <span className="text-zinc-200 bg-white/10 border border-white/20 px-2 py-0.5 rounded-full">{Math.round(app.match_score_at_apply)}%</span>}
                          </div>

                          {col.id === "pending_approval" && (
                            <div className="mt-4 pt-3 border-t border-white/10 flex gap-2">
                              <button onClick={(e) => { e.stopPropagation(); approveMut.mutate(app.id); }} className="flex-1 px-4 py-2 bg-white text-black text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-zinc-200 transition-colors">Approve</button>
                            </div>
                          )}
                          {col.id === "queued" && (
                            <div className="mt-4 pt-3 border-t border-white/[0.08]">
                              <button onClick={(e) => { e.stopPropagation(); triggerBot.mutate(app.id); }} className="w-full px-4 py-2 flex items-center justify-center gap-2 bg-[#252525] text-zinc-300 text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-[#303030] transition-colors border border-white/[0.08]">
                                <Play className="w-3 h-3" /> Force Deploy
                              </button>
                            </div>
                          )}
                        </motion.div>
                      ))}
                      {columnApps.length === 0 && (
                        <div className="h-24 flex items-center justify-center bg-[#1d1d1d] border border-white/[0.08] rounded-2xl shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
                          <p className="text-[10px] font-black text-zinc-400 uppercase tracking-[0.3em] italic">Empty Sector</p>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="bg-[#242424] border border-white/[0.08] rounded-xl overflow-hidden h-full flex flex-col shadow-[inset_0_1px_0_rgba(255,255,255,0.035)]">
            <div className="overflow-x-auto flex-1">
              <table className="w-full text-sm text-left whitespace-nowrap">
                <thead className="bg-[#1d1d1d] text-zinc-400 border-b border-white/[0.08] sticky top-0 z-10">
                  <tr>
                    <th className="px-4 py-3 font-medium cursor-pointer w-10">⭐</th>
                    <th className="px-4 py-3 font-medium">Role & Company</th>
                    <th className="px-4 py-3 font-medium">Status</th>
                    <th className="px-4 py-3 font-medium">Match</th>
                    <th className="px-4 py-3 font-medium">Date</th>
                    <th className="px-4 py-3 font-medium">Recruiter</th>
                    <th className="px-4 py-3 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {data?.items?.map((app: any) => (
                    <tr key={app.id} className="hover:bg-white/[0.02] transition-colors group">
                      <td className="px-4 py-3">
                        <button onClick={() => starMut.mutate(app.id)} className="text-muted-foreground hover:text-amber-400">
                          <Star className={cn("w-4 h-4", app.is_starred ? "fill-amber-400 text-amber-400" : "")} />
                        </button>
                      </td>
                      <td className="px-4 py-3">
                        <p className="font-semibold">{app.job_title_snapshot}</p>
                        <p className="text-xs text-muted-foreground">{app.company_snapshot}</p>
                      </td>
                      <td className="px-4 py-3">
                        <span className={cn("px-2 py-1 text-[10px] font-bold rounded border", getStatusClass(app.status))}>{getStatusLabel(app.status)}</span>
                      </td>
                      <td className="px-4 py-3 font-medium">{app.match_score_at_apply ? `${Math.round(app.match_score_at_apply)}%` : "—"}</td>
                      <td className="px-4 py-3 text-muted-foreground text-xs">{formatDate(app.created_at)}</td>
                      <td className="px-4 py-3 text-xs">{app.recruiter_name ?? "—"}</td>
                      <td className="px-4 py-3 text-right">
                        {app.status?.toLowerCase() === "pending_approval" ? (
                          <button onClick={() => approveMut.mutate(app.id)} className="px-3 py-1 bg-white text-black text-xs font-medium rounded hover:bg-zinc-200 transition-colors">Approve</button>
                        ) : (
                          <a 
                            href={app.job?.source_url || `/applications/${app.id}`} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-white hover:underline text-xs inline-flex items-center gap-1"
                          >
                            View <ChevronRight className="w-3 h-3" />
                          </a>
                        )}
                      </td>
                    </tr>
                  ))}
                  {data?.items?.length === 0 && <tr><td colSpan={7} className="px-4 py-8 text-center text-muted-foreground">No applications found.</td></tr>}
                </tbody>
              </table>
            </div>
            {data && data.pages > 1 && (
              <div className="p-3 border-t border-white/[0.08] flex items-center justify-center gap-2 shrink-0 bg-[#1d1d1d]">
                <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1} className="px-3 py-1 bg-[#252525] border border-white/[0.08] text-white rounded text-xs disabled:opacity-50 disabled:cursor-not-allowed">Prev</button>
                <span className="text-xs text-zinc-500">Page {page} of {data.pages}</span>
                <button onClick={() => setPage((p) => Math.min(data.pages, p + 1))} disabled={page === data.pages} className="px-3 py-1 bg-[#252525] border border-white/[0.08] text-white rounded text-xs disabled:opacity-50 disabled:cursor-not-allowed">Next</button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
