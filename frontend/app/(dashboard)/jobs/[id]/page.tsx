"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { jobsApi, applicationsApi, resumesApi, coverLettersApi } from "@/lib/api";
import { useParams, useRouter } from "next/navigation";
import { useSubscription } from "@/lib/subscription";
import { cn, getMatchBadgeClass, formatDate } from "@/lib/utils";
import Link from "next/link";
import { toast } from "sonner";
import { ArrowLeft, Send, FileText, BookOpen, Target, Zap, Award, Users, TrendingUp, Brain, CheckCircle, XCircle } from "lucide-react";

export default function JobDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const qc = useQueryClient();
  const { canAccess } = useSubscription();

  const { data: job, isLoading } = useQuery({
    queryKey: ["job", id],
    queryFn: () => jobsApi.get(id).then((r) => r.data),
  });

  const applyMutation = useMutation({
    mutationFn: () => applicationsApi.create({ job_id: id, method: "auto_bot" }),
    onSuccess: () => { toast.success("Application queued!"); router.push("/applications"); },
    onError: (err: any) => toast.error(err?.response?.data?.detail ?? "Failed to apply"),
  });

  const generateResume = useMutation({
    mutationFn: () => resumesApi.generate({ job_id: id }),
    onSuccess: () => toast.success("Tailored resume generation queued!"),
    onError: () => toast.error("Failed to generate resume"),
  });

  const generateCL = useMutation({
    mutationFn: () => coverLettersApi.generate({ job_id: id, tone: "professional" }),
    onSuccess: () => toast.success("Cover letter generation queued!"),
    onError: () => toast.error("Cover letter requires Pro plan"),
  });

  if (isLoading) {
    return (
      <div className="space-y-5">
        <div className="skeleton h-8 w-48 rounded" />
        <div className="grid grid-cols-3 gap-5">
          <div className="skeleton col-span-2 h-96 rounded-xl" />
          <div className="skeleton h-96 rounded-xl" />
        </div>
      </div>
    );
  }

  const analysis = job?.analysis;

  return (
    <div className="space-y-6">
      {/* Back */}
      <button onClick={() => router.back()} className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors text-sm">
        <ArrowLeft className="w-4 h-4" /> Back to Jobs
      </button>

      {/* Header */}
      <div className="glass-card p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-brand-purple/20 to-brand-blue/20 flex items-center justify-center shrink-0">
              <FileText className="w-7 h-7 text-brand-purple-light" />
            </div>
            <div>
              <h1 className="text-xl font-bold">{job?.title}</h1>
              <p className="text-muted-foreground mt-0.5">{job?.company_name} · {job?.location ?? "Remote"}</p>
              <div className="flex flex-wrap gap-2 mt-3">
                <span className="px-2.5 py-1 bg-muted rounded-full text-xs capitalize">{job?.work_mode}</span>
                <span className="px-2.5 py-1 bg-muted rounded-full text-xs capitalize">{job?.job_type?.replace("_", " ")}</span>
                <span className="px-2.5 py-1 bg-muted rounded-full text-xs capitalize">{job?.source}</span>
                {job?.easy_apply && <span className="px-2.5 py-1 bg-brand-blue/20 text-brand-blue rounded-full text-xs flex items-center gap-1"><Zap className="w-3 h-3" />Easy Apply</span>}
                {analysis?.is_internship && <span className="px-2.5 py-1 bg-violet-500/20 text-violet-400 rounded-full text-xs">Internship</span>}
              </div>
            </div>
          </div>
          {analysis?.match_score != null && (
            <div className="text-center shrink-0">
              <div className={cn("w-16 h-16 rounded-full flex items-center justify-center text-xl font-extrabold border-2", getMatchBadgeClass(analysis.match_score))}>
                {Math.round(analysis.match_score)}
              </div>
              <p className="text-xs text-muted-foreground mt-1">Match %</p>
            </div>
          )}
        </div>

        {/* Action buttons */}
        <div className="flex flex-wrap gap-3 mt-6 pt-5 border-t border-border">
          <button onClick={() => applyMutation.mutate()} disabled={applyMutation.isPending}
            className="flex items-center gap-2 px-5 py-2.5 bg-brand-purple text-white rounded-lg text-sm font-medium hover:bg-brand-purple/90 transition-all disabled:opacity-50">
            <Send className="w-4 h-4" /> Apply Now
          </button>
          <button onClick={() => generateResume.mutate()} disabled={generateResume.isPending}
            className="flex items-center gap-2 px-5 py-2.5 glass rounded-lg text-sm hover:bg-white/5 transition-colors">
            <FileText className="w-4 h-4" /> Generate Resume
          </button>
          {canAccess("cover_letters") ? (
            <button onClick={() => generateCL.mutate()} disabled={generateCL.isPending}
              className="flex items-center gap-2 px-5 py-2.5 glass rounded-lg text-sm hover:bg-white/5 transition-colors">
              <BookOpen className="w-4 h-4" /> Cover Letter
            </button>
          ) : (
            <Link href="/pricing" className="flex items-center gap-2 px-5 py-2.5 glass rounded-lg text-sm text-muted-foreground">
              <BookOpen className="w-4 h-4" /> Cover Letter (Pro)
            </Link>
          )}
          <a href={job?.source_url} target="_blank" rel="noopener noreferrer"
            className="flex items-center gap-2 px-5 py-2.5 glass rounded-lg text-sm hover:bg-white/5 transition-colors text-muted-foreground">
            View on {job?.source}
          </a>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Job description */}
        <div className="lg:col-span-2 space-y-5">
          <div className="glass-card p-6">
            <h2 className="font-semibold mb-4">Job Description</h2>
            <div className="prose prose-sm prose-invert max-w-none text-muted-foreground leading-relaxed whitespace-pre-wrap text-sm">
              {job?.description_clean ?? "No description available."}
            </div>
          </div>

          {/* AI Summary */}
          {analysis?.ai_summary && (
            <div className="glass-card p-6 border border-brand-purple/20">
              <div className="flex items-center gap-2 mb-3">
                <Brain className="w-4 h-4 text-brand-purple-light" />
                <h3 className="font-semibold text-sm">AI Summary</h3>
              </div>
              <p className="text-sm text-muted-foreground">{analysis.ai_summary}</p>
              {analysis.ai_recommendation && (
                <div className="mt-3 p-3 bg-brand-purple/10 rounded-lg text-sm text-brand-purple-light">
                  💡 {analysis.ai_recommendation}
                </div>
              )}
            </div>
          )}
        </div>

        {/* AI Analysis panel */}
        <div className="space-y-4">
          {analysis ? (
            <>
              {/* Scores */}
              <div className="glass-card p-5">
                <h3 className="font-semibold text-sm mb-4">AI Analysis</h3>
                <div className="space-y-3">
                  {[
                    { label: "Skill Match", val: analysis.skill_match_score },
                    { label: "Experience Match", val: analysis.experience_match_score },
                    { label: "Interview Probability", val: analysis.interview_probability },
                  ].filter((s) => s.val != null).map((s) => (
                    <div key={s.label}>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-muted-foreground">{s.label}</span>
                        <span className="font-medium">{Math.round(s.val!)}%</span>
                      </div>
                      <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                        <div className="h-full rounded-full bg-brand-purple" style={{ width: `${s.val}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
                {analysis.competition_level && (
                  <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">
                    <Users className="w-3.5 h-3.5" />
                    Competition: <span className="font-medium capitalize">{analysis.competition_level}</span>
                  </div>
                )}
              </div>

              {/* Matching skills */}
              {analysis.matching_skills?.length > 0 && (
                <div className="glass-card p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <CheckCircle className="w-4 h-4 text-brand-green" />
                    <h3 className="font-semibold text-sm">Matching Skills</h3>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {analysis.matching_skills.map((sk: string) => (
                      <span key={sk} className="px-2.5 py-1 bg-brand-green/15 text-brand-green border border-brand-green/30 rounded-full text-xs">{sk}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Missing skills */}
              {analysis.missing_skills?.length > 0 && (
                <div className="glass-card p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <XCircle className="w-4 h-4 text-brand-red" />
                    <h3 className="font-semibold text-sm">Skill Gaps ({analysis.skill_gap_count})</h3>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {analysis.missing_skills.map((sk: string) => (
                      <span key={sk} className="px-2.5 py-1 bg-red-500/15 text-red-400 border border-red-500/30 rounded-full text-xs">{sk}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* ATS keywords */}
              {analysis.ats_keywords?.length > 0 && (
                <div className="glass-card p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <Target className="w-4 h-4 text-brand-amber" />
                    <h3 className="font-semibold text-sm">ATS Keywords</h3>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {analysis.ats_keywords.slice(0, 20).map((kw: string) => (
                      <span key={kw} className="px-2 py-0.5 bg-muted text-muted-foreground rounded text-xs">{kw}</span>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="glass-card p-6 text-center">
              <Brain className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
              <p className="text-sm text-muted-foreground mb-4">No AI analysis yet</p>
              <button onClick={() => jobsApi.analyze(id).then(() => { toast.success("Analysis triggered!"); qc.invalidateQueries({ queryKey: ["job", id] }); })}
                className="px-4 py-2 bg-brand-purple text-white rounded-lg text-sm hover:bg-brand-purple/90 transition-colors">
                Analyze Now
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
