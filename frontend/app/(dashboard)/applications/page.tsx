"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { applicationsApi, agentApi } from "@/lib/api";
import { cn, getStatusClass, getStatusLabel, timeAgo, formatDate } from "@/lib/utils";
import Link from "next/link";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { Search, Filter, LayoutGrid, List, SlidersHorizontal, Check, Star, RefreshCw, ChevronRight, AlertCircle, Play } from "lucide-react";

const KANBAN_COLUMNS = [
  { id: "pending_approval", label: "Pending" },
  { id: "queued", label: "Queued" },
  { id: "applying", label: "Applying" },
  { id: "applied", label: "Applied" },
  { id: "viewed", label: "Viewed" },
  { id: "shortlisted", label: "Shortlisted" },
  { id: "interview_scheduled", label: "Interview" },
  { id: "offer_received", label: "Offer" },
  { id: "rejected", label: "Rejected" },
];

export default function ApplicationsPage() {
  const qc = useQueryClient();
  const [view, setView] = useState<"kanban" | "table">("kanban");
  const [filters, setFilters] = useState({ status: "", is_starred: undefined as boolean | undefined });
  const [page, setPage] = useState(1);

  const { data, isLoading, refetch } = useQuery({
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

  // Group applications for Kanban
  const groupedApps = KANBAN_COLUMNS.reduce((acc, col) => {
    acc[col.id] = data?.items?.filter((app: any) => app.status === col.id) ?? [];
    return acc;
  }, {} as Record<string, any[]>);

  const pendingApps = data?.items?.filter((a: any) => a.status === "pending_approval") ?? [];

  return (
    <div className="space-y-6 flex flex-col h-[calc(100vh-6rem)]">
      {/* Header & Stats */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold font-display">Applications</h1>
            <p className="text-muted-foreground text-sm mt-1">{data?.total ?? 0} total applications tracked</p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => refetch()} className="flex items-center gap-2 px-3 py-2 glass rounded-lg text-sm hover:bg-white/5 transition-colors text-muted-foreground">
              <RefreshCw className="w-4 h-4" />
            </button>
            <div className="flex p-1 bg-muted/50 rounded-lg">
              <button onClick={() => setView("kanban")} className={cn("px-3 py-1.5 flex items-center gap-2 rounded-md text-sm transition-colors", view === "kanban" ? "bg-background shadow-sm text-brand-purple-light" : "text-muted-foreground hover:text-foreground")}><LayoutGrid className="w-4 h-4" /> Kanban</button>
              <button onClick={() => setView("table")} className={cn("px-3 py-1.5 flex items-center gap-2 rounded-md text-sm transition-colors", view === "table" ? "bg-background shadow-sm text-brand-purple-light" : "text-muted-foreground hover:text-foreground")}><List className="w-4 h-4" /> Table</button>
            </div>
          </div>
        </div>

        {stats && (
          <div className="grid grid-cols-4 gap-4">
            {[{ l: "Total Sent", v: stats.total_sent }, { l: "Response Rate", v: `${(stats.response_rate * 100).toFixed(1)}%` }, { l: "Interviews", v: stats.interviews }, { l: "Offers", v: stats.offers }].map(s => (
              <div key={s.l} className="glass-card px-4 py-3"><p className="text-xs text-muted-foreground font-medium">{s.l}</p><p className="text-xl font-bold font-display">{s.v}</p></div>
            ))}
          </div>
        )}
      </div>

      {pendingApps.length > 0 && filters.status === "" && (
        <div className="flex items-center gap-3 p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl mb-2">
          <AlertCircle className="w-5 h-5 text-amber-400 shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-medium text-amber-400">{pendingApps.length} applications pending approval</p>
          </div>
          <button onClick={() => pendingApps.forEach((a: any) => approveMut.mutate(a.id))}
            className="px-4 py-1.5 bg-brand-purple text-white rounded-lg text-xs font-medium hover:bg-brand-purple/90 transition-colors">
            Approve All
          </button>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 min-h-0 overflow-hidden">
        {isLoading ? (
          <div className="flex h-full items-center justify-center"><div className="w-8 h-8 rounded-full border-2 border-brand-purple border-t-transparent animate-spin" /></div>
        ) : view === "kanban" ? (
          <div className="h-full overflow-x-auto overflow-y-hidden pb-4">
            <div className="flex gap-4 h-full min-w-max">
              {KANBAN_COLUMNS.map((col) => {
                const columnApps = groupedApps[col.id] || [];
                return (
                  <div key={col.id} className="w-80 flex flex-col bg-muted/20 border border-border/50 rounded-xl max-h-full">
                    <div className="p-3 border-b border-border/50 flex items-center justify-between shrink-0">
                      <span className="font-semibold text-sm">{col.label}</span>
                      <span className="text-xs px-2 py-0.5 bg-muted rounded-full text-muted-foreground">{columnApps.length}</span>
                    </div>
                    <div className="flex-1 overflow-y-auto p-3 space-y-3">
                      {columnApps.map((app) => (
                        <div key={app.id} className="glass-card p-4 card-hover cursor-pointer relative group" onClick={() => (window as any).location.href = `/applications/${app.id}`}>
                          <button onClick={(e) => { e.stopPropagation(); starMut.mutate(app.id); }} className="absolute top-3 right-3 text-muted-foreground hover:text-amber-400 transition-colors z-10 w-6 h-6 flex items-center justify-center">
                            <Star className={cn("w-4 h-4", app.is_starred ? "fill-amber-400 text-amber-400" : "")} />
                          </button>
                          <div className={cn("inline-block px-2 text-[10px] font-bold rounded mb-2 border", getStatusClass(col.id))}>{getStatusLabel(col.id)}</div>
                          <p className="font-semibold text-sm leading-tight pr-6">{app.job_title_snapshot}</p>
                          <p className="text-muted-foreground text-xs mt-1">{app.company_snapshot}</p>
                          <div className="flex items-center justify-between mt-3 text-[10px] text-muted-foreground">
                            <span>{timeAgo(app.created_at)}</span>
                            {app.match_score_at_apply && <span className="font-bold text-brand-purple-light">{Math.round(app.match_score_at_apply)}% match</span>}
                          </div>
                          {col.id === "pending_approval" && (
                            <div className="mt-3 pt-3 border-t border-border flex gap-2">
                              <button onClick={(e) => { e.stopPropagation(); approveMut.mutate(app.id); }} className="flex-1 px-2 py-1.5 bg-brand-purple text-white text-xs font-medium rounded hover:bg-brand-purple/90">Approve</button>
                            </div>
                          )}
                          {col.id === "queued" && (
                            <div className="mt-3 pt-3 border-t border-border">
                              <button onClick={(e) => { e.stopPropagation(); triggerBot.mutate(app.id); }} className="w-full px-2 py-1.5 flex items-center justify-center gap-1.5 glass text-xs hover:bg-white/5 rounded">
                                <Play className="w-3 h-3" /> Force Run Bot
                              </button>
                            </div>
                          )}
                        </div>
                      ))}
                      {columnApps.length === 0 && <p className="text-xs text-muted-foreground text-center py-4 opacity-50">Empty</p>}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="bg-card border border-border rounded-xl overflow-hidden h-full flex flex-col">
            <div className="overflow-x-auto flex-1">
              <table className="w-full text-sm text-left whitespace-nowrap">
                <thead className="bg-muted/50 text-muted-foreground border-b border-border sticky top-0 z-10">
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
                <tbody className="divide-y divide-border">
                  {data?.items?.map((app: any) => (
                    <tr key={app.id} className="hover:bg-muted/30 transition-colors group">
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
                        {app.status === "pending_approval" ? (
                          <button onClick={() => approveMut.mutate(app.id)} className="px-3 py-1 bg-brand-purple text-white text-xs font-medium rounded hover:bg-brand-purple/90">Approve</button>
                        ) : (
                          <Link href={`/applications/${app.id}`} className="text-brand-purple-light hover:underline text-xs inline-flex items-center gap-1">View <ChevronRight className="w-3 h-3" /></Link>
                        )}
                      </td>
                    </tr>
                  ))}
                  {data?.items?.length === 0 && <tr><td colSpan={7} className="px-4 py-8 text-center text-muted-foreground">No applications found.</td></tr>}
                </tbody>
              </table>
            </div>
            {data && data.pages > 1 && (
              <div className="p-3 border-t border-border flex items-center justify-center gap-2 shrink-0 bg-muted/20">
                <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1} className="px-3 py-1 glass rounded text-xs disabled:opacity-30">Prev</button>
                <span className="text-xs text-muted-foreground">Page {page} of {data.pages}</span>
                <button onClick={() => setPage((p) => Math.min(data.pages, p + 1))} disabled={page === data.pages} className="px-3 py-1 glass rounded text-xs disabled:opacity-30">Next</button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
