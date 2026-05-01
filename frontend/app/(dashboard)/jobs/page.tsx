"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { jobsApi, applicationsApi } from "@/lib/api";
import { cn, getMatchBadgeClass, getStatusClass, timeAgo, truncate } from "@/lib/utils";
import { motion } from "framer-motion";
import { Search, Filter, SlidersHorizontal, Briefcase, MapPin, Clock, Zap, Send, SkipForward, ChevronRight, RefreshCw, ExternalLink, Loader2 } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";

function MatchScoreRing({ score, size = 48 }: { score: number; size?: number }) {
  const r = (size - 8) / 2;
  const circ = 2 * Math.PI * r;
  const pct = Math.min(Math.max(score, 0), 100);
  const color = score >= 80 ? "#ffffff" : score >= 60 ? "#e4e4e7" : score >= 40 ? "#a1a1aa" : "#52525b";
  
  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg className="w-full h-full -rotate-90">
        <circle cx={size/2} cy={size/2} r={r} fill="none" strokeWidth="4" className="text-zinc-100" />
        <motion.circle
          cx={size/2} cy={size/2} r={r} fill="none" strokeWidth="4"
          stroke={color} strokeLinecap="round"
          initial={{ strokeDasharray: circ, strokeDashoffset: circ }}
          animate={{ strokeDashoffset: circ - (circ * pct) / 100 }}
          transition={{ duration: 1, ease: "easeOut" }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-xs font-black text-white">{Math.round(pct)}</span>
      </div>
    </div>
  );
}

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
  const [isManualRefreshing, setIsManualRefreshing] = useState(false);

  const { data, isLoading, isRefetching, refetch } = useQuery({
    queryKey: ["jobs", filters, page],
    queryFn: () => jobsApi.list({ ...filters, page, page_size: 20, min_match_score: filters.min_match_score || undefined }).then((r) => r.data),
  });

  const isRefreshing = isManualRefreshing || isRefetching;

  const handleRefresh = async () => {
    if (isRefreshing) return;
    setIsManualRefreshing(true);
    try {
      const result = await refetch();
      if (result.error) {
        toast.error("Failed to refresh job feed.");
      } else {
        toast.success("Job feed refreshed.");
      }
    } catch {
      toast.error("Failed to refresh job feed.");
    } finally {
      setIsManualRefreshing(false);
    }
  };

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
    <div className="dash-page">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-[#242424] border border-white/[0.08] rounded-lg">
          <Briefcase className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-white">Job Feed.</h1>
          <p className="text-sm text-zinc-400 mt-1">{data?.total ?? 0} high-priority opportunities matched to your profile across various sources.</p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="flex items-center gap-2 px-4 py-2 bg-[#1c1c1e] hover:bg-[#2a2a2a] text-white rounded-lg text-sm font-medium transition-colors border border-[#2a2a2a] disabled:opacity-60 disabled:cursor-not-allowed"
          title={isRefreshing ? "Refreshing..." : "Refresh"}
        >
          {isRefreshing ? <Loader2 className="w-5 h-5 animate-spin text-zinc-300" /> : <RefreshCw className="w-5 h-5 text-zinc-400" />}
          <span>{isRefreshing ? "Refreshing..." : "Refresh"}</span>
        </button>
      </div>

      {/* Search + filter bar */}
      <div className="dash-card flex flex-col gap-4 relative z-20">
        <div className="flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
            <input
              type="text" placeholder="Search roles, companies, or skills…"
              value={filters.keyword} onChange={(e) => F("keyword", e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-[#1c1c1e] border border-zinc-800 rounded-xl text-sm font-medium text-white placeholder-zinc-600 focus:ring-1 focus:ring-white/50 focus:border-white/30 transition-all outline-none"
            />
          </div>
          <div className="flex gap-2">
            <select value={filters.sort_by} onChange={(e) => F("sort_by", e.target.value)}
              className="px-3 py-2 bg-[#1c1c1e] border border-zinc-800 rounded-lg text-sm font-bold text-zinc-300 focus:ring-1 focus:ring-white/50 transition-all appearance-none cursor-pointer min-w-[150px] outline-none">
              {SORTS.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
            </select>
            <button onClick={() => setShowFilters(!showFilters)}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-bold transition-all", 
                showFilters ? "bg-white text-black" : "bg-[#1c1c1e] border border-zinc-800 text-zinc-400 hover:bg-[#2a2a2a]"
              )}
            >
              <SlidersHorizontal className="w-4 h-4" /> 
              <span>Filters</span>
            </button>
          </div>
        </div>

        {showFilters && (
          <motion.div 
            initial={{ opacity: 0, y: -10 }} 
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 md:grid-cols-4 gap-3 p-4 bg-[#1c1c1e]/3 rounded-xl border border-white/10"
          >
            <div className="space-y-1.5">
              <label className="text-[10px] font-black uppercase tracking-widest text-zinc-400 ml-2">Source</label>
              <select value={filters.source} onChange={(e) => F("source", e.target.value)}
                className="w-full px-3 py-2 bg-[#1c1c1e] border border-zinc-800 rounded-lg text-sm font-medium text-zinc-300 outline-none">
                <option value="">All sources</option>
                {SOURCES.filter(Boolean).map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-[10px] font-black uppercase tracking-widest text-zinc-400 ml-2">Job Type</label>
              <select value={filters.job_type} onChange={(e) => F("job_type", e.target.value)}
                className="w-full px-3 py-2 bg-[#1c1c1e] border border-zinc-800 rounded-lg text-sm font-medium text-zinc-300 outline-none">
                <option value="">All types</option>
                {TYPES.filter(Boolean).map((t) => <option key={t} value={t}>{t.replace("_", " ")}</option>)}
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-[10px] font-black uppercase tracking-widest text-zinc-400 ml-2">Work Mode</label>
              <select value={filters.work_mode} onChange={(e) => F("work_mode", e.target.value)}
                className="w-full px-3 py-2 bg-[#1c1c1e] border border-zinc-800 rounded-lg text-sm font-medium text-zinc-300 outline-none">
                <option value="">All modes</option>
                {MODES.filter(Boolean).map((m) => <option key={m} value={m}>{m}</option>)}
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-[10px] font-black uppercase tracking-widest text-zinc-400 ml-2">Min Score</label>
              <input type="number" min={0} max={100} value={filters.min_match_score}
                onChange={(e) => F("min_match_score", +e.target.value)}
                className="w-full px-3 py-2 bg-[#1c1c1e] border border-zinc-800 rounded-lg text-sm font-medium text-zinc-300 outline-none" />
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
        <div className="space-y-4 pb-12">
          {(data?.items ?? []).map((job: any, i: number) => (
            <motion.div 
              key={job.id} 
              initial={{ opacity: 0, y: 12 }} 
              animate={{ opacity: 1, y: 0 }} 
              transition={{ delay: i * 0.04 }}
              whileHover={{ y: -3 }}
              className="bg-[#1c1c1e] p-4 rounded-xl border border-zinc-800 hover:border-white/20 flex flex-col md:flex-row items-center gap-6 group transition-all"
            >
              {/* Company icon */}
              <div className="w-10 h-10 rounded-xl bg-[#222222] flex items-center justify-center shrink-0 border border-zinc-800">
                {job.company_logo_url ? (
                  <img src={job.company_logo_url} className="w-6 h-6 object-contain rounded-lg" alt="" />
                ) : (
                  <Briefcase className="w-6 h-6 text-zinc-400" />
                )}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0 text-center md:text-left">
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-3">
                  <div>
                    <h3 className="font-bold text-sm tracking-tight text-white leading-tight mb-1 group-hover:text-zinc-200 transition-colors">{job.title}</h3>
                    <div className="flex flex-wrap items-center justify-center md:justify-start gap-2 mt-1 text-[11px] font-bold text-zinc-400 uppercase tracking-wider">
                       <span className="text-zinc-300">{job.company_name}</span>
                       <span className="w-1 h-1 bg-zinc-700 rounded-full" />
                       <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{job.location || "Remote"}</span>
                    </div>
                  </div>
                  {job.analysis?.match_score != null && (
                    <div className="flex items-center gap-2 px-3 py-2 bg-[#1c1c1e] rounded-xl border border-zinc-800">
                      <MatchScoreRing score={job.analysis.match_score} size={36} />
                      <div className="flex flex-col">
                        <span className="text-[9px] font-bold uppercase tracking-widest text-zinc-400">Match</span>
                        <span className={cn("text-xs font-black", 
                          job.analysis.match_score >= 80 ? "text-white" : 
                          job.analysis.match_score >= 60 ? "text-zinc-200" : 
                          job.analysis.match_score >= 40 ? "text-zinc-400" : "text-zinc-500"
                        )}>
                          {job.analysis.match_score >= 80 ? "Excellent" : 
                           job.analysis.match_score >= 60 ? "Good" : 
                           job.analysis.match_score >= 40 ? "Fair" : "Low"}
                        </span>
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex flex-wrap items-center justify-center md:justify-start gap-2 mt-4 text-[11px] font-medium text-zinc-400 uppercase tracking-wider">
                  <span className="bg-[#1c1c1e] px-2.5 py-1 rounded-full border border-zinc-800">{job.work_mode}</span>
                  {job.job_type && <span className="bg-[#1c1c1e] px-2.5 py-1 rounded-full border border-zinc-800">{job.job_type.replace("_", " ")}</span>}
                  {job.posted_at && <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{timeAgo(job.posted_at)}</span>}
                  {(job.salary_min || job.salary_max) && (
                    <span className="text-green-400 bg-green-500/10 border border-green-500/20 px-2.5 py-1 rounded-full font-black">₹{job.salary_min ?? "?"} – {job.salary_max ?? "?"}K</span>
                  )}
                </div>

                {job.analysis?.ai_summary && (
                  <p className="text-xs text-zinc-400 mt-3 line-clamp-2 italic font-serif leading-relaxed">"{job.analysis.ai_summary}"</p>
                )}
              </div>

              {/* Actions */}
              <div className="flex flex-row md:flex-col gap-2 shrink-0 w-full md:w-auto">
                <button onClick={() => applyMutation.mutate(job.id)} disabled={applyMutation.isPending}
                  className="flex-1 md:w-32 flex items-center justify-center gap-2 px-4 py-1.5 bg-white text-black rounded-lg text-xs font-black uppercase tracking-widest hover:scale-105 transition-transform disabled:opacity-50 shadow-sm">
                  <Send className="w-4 h-4" /> Apply
                </button>
                <div className="flex gap-2 flex-1 md:flex-none">
                  {job.source_url && (
                    <a
                      href={job.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 md:w-auto flex items-center justify-center p-2 bg-[#1c1c1e] border border-zinc-800 rounded-lg hover:bg-[#2a2a2a] hover:border-white/30 transition-colors"
                      title="Open job source"
                    >
                      <ExternalLink className="w-4 h-4 text-zinc-400 hover:text-zinc-200" />
                    </a>
                  )}
                  <button onClick={() => analyzeMutation.mutate(job.id)} disabled={analyzeMutation.isPending}
                    className="flex-1 md:w-auto flex items-center justify-center p-2 bg-[#1c1c1e] border border-zinc-800 rounded-lg hover:bg-[#2a2a2a] hover:border-white/30 transition-colors">
                    <Zap className="w-4 h-4 text-zinc-400 hover:text-zinc-200" />
                  </button>
                  <button onClick={() => skipMutation.mutate(job.id)}
                    className="flex-1 md:w-auto flex items-center justify-center p-2 bg-[#1c1c1e] border border-zinc-800 rounded-lg hover:bg-red-500/10 hover:border-red-500/20 transition-colors">
                    <SkipForward className="w-4 h-4 text-zinc-400 hover:text-red-400" />
                  </button>
                  
                </div>
              </div>
            </motion.div>
          ))}

          {data?.items?.length === 0 && (
            <div className="dark-card p-12 text-center">
              <Briefcase className="w-12 h-12 text-zinc-300 mx-auto mb-3" />
              <p className="text-zinc-400">No jobs found. Try adjusting filters or run the agent to scrape new listings.</p>
            </div>
          )}
        </div>
      )}

      {/* Pagination */}
      {data && data.pages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-2">
          <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}
            className="px-4 py-2  rounded-lg text-sm disabled:opacity-80 disabled:cursor-not-allowed">←</button>
          <span className="text-sm text-muted-foreground">Page {page} of {data.pages}</span>
          <button onClick={() => setPage((p) => Math.min(data.pages, p + 1))} disabled={page === data.pages}
            className="px-4 py-2  rounded-lg text-sm disabled:opacity-80 disabled:cursor-not-allowed">→</button>
        </div>
      )}
    </div>
  );
}
