"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { jobsApi, applicationsApi } from "@/lib/api";
import { cn, getMatchBadgeClass, getStatusClass, timeAgo, truncate } from "@/lib/utils";
import { motion } from "framer-motion";
import { Search, Filter, SlidersHorizontal, Briefcase, MapPin, Clock, Zap, Send, SkipForward, ChevronRight, RefreshCw } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";

const SOURCES = ["", "internshala", "linkedin", "indeed", "wellfound"];
const TYPES = ["", "internship", "full_time", "contract", "part_time"];
const MODES = ["", "remote", "hybrid", "onsite"];
const SORTS = [
  { value: "match_score", label: "Match Score" },
  { value: "priority_score", label: "Priority" },
  { value: "posted_at", label: "Posted Date" },
  { value: "created_at", label: "Scraped Date" },
];

export default function JobsPage() {
  const qc = useQueryClient();
  const [filters, setFilters] = useState({ source: "", job_type: "", work_mode: "", min_match_score: 0, keyword: "", status: "", sort_by: "match_score" });
  const [page, setPage] = useState(1);
  const [showFilters, setShowFilters] = useState(false);

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["jobs", filters, page],
    queryFn: () => jobsApi.list({ ...filters, page, page_size: 20, min_match_score: filters.min_match_score || undefined }).then((r) => r.data),
  });

  const applyMutation = useMutation({
    mutationFn: (jobId: string) => applicationsApi.create({ job_id: jobId, method: "auto_bot" }),
    onSuccess: () => { toast.success("Application queued!"); qc.invalidateQueries({ queryKey: ["jobs"] }); },
    onError: (err: any) => toast.error(err?.response?.data?.detail ?? "Failed to apply"),
  });

  const skipMutation = useMutation({
    mutationFn: (jobId: string) => jobsApi.skip(jobId),
    onSuccess: () => { toast.info("Job skipped"); qc.invalidateQueries({ queryKey: ["jobs"] }); },
  });

  const analyzeMutation = useMutation({
    mutationFn: (jobId: string) => jobsApi.analyze(jobId),
    onSuccess: () => { toast.success("Analysis queued!"); qc.invalidateQueries({ queryKey: ["jobs"] }); },
  });

  const F = (key: string, val: any) => { setFilters((f) => ({ ...f, [key]: val })); setPage(1); };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold font-display">Job Feed</h1>
          <p className="text-muted-foreground text-sm mt-1">
            {data?.total ?? 0} jobs found
          </p>
        </div>
        <button onClick={() => refetch()} className="flex items-center gap-2 px-3 py-2 glass rounded-lg text-sm hover:bg-white/5 transition-colors">
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      {/* Search + filter bar */}
      <div className="flex flex-col gap-3">
        <div className="flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text" placeholder="Search jobs, companies, skills…"
              value={filters.keyword} onChange={(e) => F("keyword", e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-purple/50"
            />
          </div>
          <select value={filters.sort_by} onChange={(e) => F("sort_by", e.target.value)}
            className="px-4 py-2.5 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-purple/50">
            {SORTS.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
          </select>
          <button onClick={() => setShowFilters(!showFilters)}
            className={cn("flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm transition-all", showFilters ? "bg-brand-purple text-white" : "glass hover:bg-white/5")}>
            <SlidersHorizontal className="w-4 h-4" /> Filters
          </button>
        </div>

        {showFilters && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }}
            className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <select value={filters.source} onChange={(e) => F("source", e.target.value)}
              className="px-4 py-2.5 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-purple/50">
              <option value="">All sources</option>
              {SOURCES.filter(Boolean).map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
            <select value={filters.job_type} onChange={(e) => F("job_type", e.target.value)}
              className="px-4 py-2.5 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-purple/50">
              <option value="">All types</option>
              {TYPES.filter(Boolean).map((t) => <option key={t} value={t}>{t.replace("_", " ")}</option>)}
            </select>
            <select value={filters.work_mode} onChange={(e) => F("work_mode", e.target.value)}
              className="px-4 py-2.5 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-purple/50">
              <option value="">All modes</option>
              {MODES.filter(Boolean).map((m) => <option key={m} value={m}>{m}</option>)}
            </select>
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground whitespace-nowrap">Min score:</span>
              <input type="number" min={0} max={100} value={filters.min_match_score}
                onChange={(e) => F("min_match_score", +e.target.value)}
                className="flex-1 px-3 py-2.5 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-purple/50" />
            </div>
          </motion.div>
        )}
      </div>

      {/* Job cards */}
      {isLoading ? (
        <div className="space-y-3">
          {[...Array(8)].map((_, i) => <div key={i} className="skeleton h-28 rounded-xl" />)}
        </div>
      ) : (
        <div className="space-y-3">
          {(data?.items ?? []).map((job: any, i: number) => (
            <motion.div key={job.id} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}
              className="glass-card p-5 card-hover flex items-start gap-4">
              {/* Company icon */}
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-brand-purple/20 to-brand-blue/20 flex items-center justify-center shrink-0">
                {job.company_logo_url ? (
                  <img src={job.company_logo_url} className="w-8 h-8 object-contain" alt="" />
                ) : (
                  <Briefcase className="w-6 h-6 text-brand-purple-light" />
                )}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="font-semibold text-sm leading-tight">{job.title}</h3>
                    <p className="text-muted-foreground text-xs mt-0.5">{job.company_name}</p>
                  </div>
                  {job.analysis?.match_score != null && (
                    <span className={cn("px-2.5 py-1 rounded-full text-xs font-bold shrink-0", getMatchBadgeClass(job.analysis.match_score))}>
                      {Math.round(job.analysis.match_score)}% match
                    </span>
                  )}
                </div>

                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-xs text-muted-foreground">
                  {job.location && <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{job.location}</span>}
                  <span className="flex items-center gap-1 capitalize"><Briefcase className="w-3 h-3" />{job.work_mode}</span>
                  {job.posted_at && <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{timeAgo(job.posted_at)}</span>}
                  {(job.salary_min || job.salary_max) && (
                    <span className="text-brand-green">₹{job.salary_min ?? "?"} – {job.salary_max ?? "?"}K</span>
                  )}
                  {job.easy_apply && (
                    <span className="flex items-center gap-0.5 bg-brand-blue/20 text-brand-blue px-2 py-0.5 rounded-full"><Zap className="w-2.5 h-2.5" />Easy Apply</span>
                  )}
                </div>

                {job.analysis?.ai_summary && (
                  <p className="text-xs text-muted-foreground mt-2 line-clamp-1">{job.analysis.ai_summary}</p>
                )}
              </div>

              {/* Actions */}
              <div className="flex flex-col gap-2 shrink-0">
                <button onClick={() => applyMutation.mutate(job.id)} disabled={applyMutation.isPending}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-brand-purple text-white rounded-lg text-xs font-medium hover:bg-brand-purple/90 transition-colors disabled:opacity-50">
                  <Send className="w-3 h-3" /> Apply
                </button>
                <button onClick={() => analyzeMutation.mutate(job.id)} disabled={analyzeMutation.isPending}
                  className="flex items-center gap-1.5 px-3 py-1.5 glass rounded-lg text-xs hover:bg-white/5 transition-colors text-muted-foreground">
                  <Zap className="w-3 h-3" /> Analyze
                </button>
                <button onClick={() => skipMutation.mutate(job.id)}
                  className="flex items-center gap-1.5 px-3 py-1.5 glass rounded-lg text-xs hover:bg-red-500/10 transition-colors text-muted-foreground hover:text-red-400">
                  <SkipForward className="w-3 h-3" /> Skip
                </button>
                <Link href={`/jobs/${job.id}`}
                  className="flex items-center gap-1.5 px-3 py-1.5 glass rounded-lg text-xs hover:bg-white/5 transition-colors text-muted-foreground">
                  Detail <ChevronRight className="w-3 h-3" />
                </Link>
              </div>
            </motion.div>
          ))}

          {data?.items?.length === 0 && (
            <div className="glass-card p-12 text-center">
              <Briefcase className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
              <p className="text-muted-foreground">No jobs found. Try adjusting filters or run the agent to scrape new listings.</p>
            </div>
          )}
        </div>
      )}

      {/* Pagination */}
      {data && data.pages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-2">
          <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}
            className="px-4 py-2 glass rounded-lg text-sm disabled:opacity-30">←</button>
          <span className="text-sm text-muted-foreground">Page {page} of {data.pages}</span>
          <button onClick={() => setPage((p) => Math.min(data.pages, p + 1))} disabled={page === data.pages}
            className="px-4 py-2 glass rounded-lg text-sm disabled:opacity-30">→</button>
        </div>
      )}
    </div>
  );
}
