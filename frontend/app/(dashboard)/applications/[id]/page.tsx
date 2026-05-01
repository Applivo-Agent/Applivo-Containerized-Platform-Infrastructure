"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { applicationsApi, jobsApi } from "@/lib/api";
import { useParams, useRouter } from "next/navigation";
import { cn, getMatchBadgeClass, getStatusClass, getStatusLabel, formatDateTime, formatDate } from "@/lib/utils";
import Link from "next/link";
import { toast } from "sonner";
import { ArrowLeft, ExternalLink, Calendar, Star, Edit3, Building, Mail, AlignLeft, ShieldAlert, Users, ChevronRight, Briefcase, FileText, Clock , Loader2} from "lucide-react";

export default function ApplicationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const qc = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);
  const [form, setForm] = useState({ status: "", recruiter_name: "", recruiter_email: "", interview_date: "", offer_salary: "", notes: "" });

  const { data: app, isLoading } = useQuery({
    queryKey: ["application", id],
    queryFn: () => applicationsApi.get(id).then((r) => r.data),
  });

  const { data: job } = useQuery({
    queryKey: ["job", app?.job_id],
    queryFn: () => jobsApi.get(app.job_id).then((r) => r.data),
    enabled: !!app?.job_id,
  });

  const updateMut = useMutation({
    mutationFn: (data: any) => applicationsApi.updateStatus(id, data),
    onSuccess: () => { toast.success("Updated!"); setIsEditing(false); qc.invalidateQueries({ queryKey: ["application", id] }); },
  });

  const starMut = useMutation({
    mutationFn: () => applicationsApi.star(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["application", id] }),
  });

  if (isLoading) return <div className="skeleton h-96 w-full rounded-xl" />;

  const handleEdit = () => {
    setForm({
      status: app.status,
      recruiter_name: app.recruiter_name ?? "",
      recruiter_email: app.recruiter_email ?? "",
      interview_date: app.interview_date ? new Date(app.interview_date).toISOString().slice(0, 16) : "",
      offer_salary: app.offer_salary?.toString() ?? "",
      notes: app.notes ?? "",
    });
    setIsEditing(true);
  };

  const submitEdit = (e: React.FormEvent) => {
    e.preventDefault();
    updateMut.mutate({
      ...form,
      offer_salary: form.offer_salary ? parseInt(form.offer_salary) : null,
      interview_date: form.interview_date ? new Date(form.interview_date).toISOString() : null,
    });
  };

  return (
    <div className="space-y-6">
      <button onClick={() => router.back()} className="flex items-center gap-2 text-muted-foreground hover:text-foreground text-sm">
        <ArrowLeft className="w-4 h-4" /> Back
      </button>

      <div className="-card p-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className={cn("px-2.5 py-1 text-[10px] uppercase tracking-wider font-bold rounded border", getStatusClass(app?.status))}>
                {getStatusLabel(app?.status)}
              </span>
              {app?.match_score_at_apply && (
                <span className={cn("px-2 py-0.5 text-xs font-bold rounded", getMatchBadgeClass(app.match_score_at_apply))}>
                  {Math.round(app.match_score_at_apply)}% Match
                </span>
              )}
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white mb-1">{app?.job_title_snapshot ?? job?.title}</h1>
            <p className="text-muted-foreground mt-1 flex items-center gap-2">
              <Building className="w-4 h-4" /> {app?.company_snapshot ?? job?.company_name}
            </p>
          </div>
          <div className="flex gap-2">
            <button onClick={() => starMut.mutate()} className="p-2  rounded-lg hover:bg-[#1c1c1e] disabled:opacity-50 text-amber-400">
              <Star className={cn("w-5 h-5", app?.is_starred ? "fill-amber-400" : "")} />
            </button>
            <button onClick={handleEdit} className="flex items-center gap-2 px-4 py-2  rounded-lg text-sm hover:bg-[#1c1c1e] transition-colors">
              <Edit3 className="w-4 h-4" /> Update
            </button>
            {job?.source_url && (
              <a href={job.source_url} target="_blank" rel="noopener noreferrer" className="p-2  rounded-lg hover:bg-[#1c1c1e] text-muted-foreground">
                <ExternalLink className="w-5 h-5" />
              </a>
            )}
          </div>
        </div>

        {/* Bot Info if failed */}
        {app?.status === "failed" && app?.bot_error && (
          <div className="mt-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-start gap-3">
            <ShieldAlert className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-red-400">Bot execution failed (Retry {app.retry_count}/3)</p>
              <p className="text-xs text-red-400/80 mt-1 font-mono bg-red-500/10 p-2 rounded">{app.bot_error}</p>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Col - Details & Editing */}
        <div className="lg:col-span-2 space-y-6">
          {isEditing ? (
            <form onSubmit={submitEdit} className="-card p-6 space-y-4">
              <h3 className="font-semibold mb-4">Edit Details</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2 sm:col-span-1">
                  <label className="block text-xs text-muted-foreground mb-1">Status</label>
                  <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })} className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm">
                    {["pending_approval", "queued", "applying", "applied", "viewed", "shortlisted", "interview_scheduled", "interview_completed", "offer_received", "offer_accepted", "offer_declined", "rejected", "withdrawn", "failed"].map(s => <option key={s} value={s}>{getStatusLabel(s)}</option>)}
                  </select>
                </div>
                {/* Specific fields based on status */}
                {form.status.includes("interview") && (
                  <div className="col-span-2 sm:col-span-1">
                    <label className="block text-xs text-muted-foreground mb-1">Interview Date</label>
                    <input type="datetime-local" value={form.interview_date} onChange={(e) => setForm({ ...form, interview_date: e.target.value })} className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm" />
                  </div>
                )}
                {form.status.includes("offer") && (
                  <div className="col-span-2 sm:col-span-1">
                    <label className="block text-xs text-muted-foreground mb-1">Offer Salary (₹)</label>
                    <input type="number" value={form.offer_salary} onChange={(e) => setForm({ ...form, offer_salary: e.target.value })} className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm" />
                  </div>
                )}
                <div className="col-span-2 sm:col-span-1">
                  <label className="block text-xs text-muted-foreground mb-1">Recruiter Name</label>
                  <input type="text" value={form.recruiter_name} onChange={(e) => setForm({ ...form, recruiter_name: e.target.value })} className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm" />
                </div>
                <div className="col-span-2 sm:col-span-1">
                  <label className="block text-xs text-muted-foreground mb-1">Recruiter Email</label>
                  <input type="email" value={form.recruiter_email} onChange={(e) => setForm({ ...form, recruiter_email: e.target.value })} className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm" />
                </div>
                <div className="col-span-2 border-t border-border/50 pt-4 mt-2">
                  <label className="block text-xs text-muted-foreground mb-1">Notes</label>
                  <textarea rows={4} value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm resize-none" placeholder="Feedback, thoughts…" />
                </div>
              </div>
              <div className="flex justify-end gap-2 mt-4 pt-4 border-t border-border">
                <button type="button" onClick={() => setIsEditing(false)} className="px-4 py-2  rounded-md text-sm hover:bg-[#1c1c1e]">Cancel</button>
                <button type="submit" disabled={updateMut.isPending} className="px-4 py-2 bg-white text-black text-white rounded-md text-sm hover:bg-white text-black/90">Save Changes</button>
              </div>
            </form>
          ) : (
            <div className="-card p-6 space-y-6">
              {(app?.notes || app?.recruiter_name || app?.interview_date || app?.offer_salary) ? (
                <>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {app.recruiter_name && <div><p className="text-xs text-muted-foreground mb-1">Recruiter</p><p className="text-sm font-medium flex items-center gap-1.5"><Users className="w-3.5 h-3.5 text-muted-foreground" /> {app.recruiter_name}</p></div>}
                    {app.recruiter_email && <div><p className="text-xs text-muted-foreground mb-1">Email</p><p className="text-sm font-medium flex items-center gap-1.5"><Mail className="w-3.5 h-3.5 text-muted-foreground" /> {app.recruiter_email}</p></div>}
                    {app.interview_date && <div><p className="text-xs text-muted-foreground mb-1">Interview At</p><p className="text-sm font-medium flex items-center gap-1.5"><Calendar className="w-3.5 h-3.5 text-white-light" /> {formatDateTime(app.interview_date)}</p></div>}
                    {app.offer_salary && <div><p className="text-xs text-muted-foreground mb-1">Offer Salary</p><p className="text-sm font-medium text-brand-green">₹{app.offer_salary}</p></div>}
                  </div>
                  {app.notes && (
                    <div className="pt-4 border-t border-border">
                      <p className="text-xs text-muted-foreground flex items-center gap-1 mb-2"><AlignLeft className="w-3.5 h-3.5" /> Notes</p>
                      <p className="text-sm text-foreground/90 whitespace-pre-wrap">{app.notes}</p>
                    </div>
                  )}
                </>
              ) : (
                <div className="text-center py-6 text-muted-foreground"><p className="text-sm">No additional details added yet.</p><button onClick={handleEdit} className="text-white-light hover:underline text-sm mt-2">Add details</button></div>
              )}
            </div>
          )}

          {/* Connected Job/Resume */}
          <div className="-card p-6">
            <h3 className="font-semibold mb-4 text-sm">Linked Assets</h3>
            <div className="space-y-3 pt-2">
              <Link href={`/jobs/${app.job_id}`} className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg hover:bg-muted/50 transition-colors">
                <Briefcase className="w-5 h-5 text-zinc-200 shrink-0" />
                <div className="flex-1"><p className="text-sm font-medium">Job Details</p><p className="text-xs text-muted-foreground">Original scraping and analysis</p></div>
                <ChevronRight className="w-4 h-4 text-muted-foreground" />
              </Link>
              {app.resume_id && (
                <Link href={`/resumes`} className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg hover:bg-muted/50 transition-colors">
                  <FileText className="w-5 h-5 text-emerald-400 shrink-0" />
                  <div className="flex-1"><p className="text-sm font-medium">Applied Resume</p><p className="text-xs text-muted-foreground">View document used</p></div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                </Link>
              )}
            </div>
          </div>
        </div>

        {/* Right Col - Timeline */}
        <div className="-card p-6">
          <h3 className="font-semibold mb-6 text-sm flex items-center gap-2"><Clock className="w-4 h-4" /> Lifecycle Timeline</h3>
          <div className="relative border-l border-border/80 ml-3 space-y-6">
            <div className="relative pl-6">
               <div className="absolute w-3 h-3 bg-card border-2 border-brand-primary rounded-full left-[-6.5px] top-1" />
               <p className="text-sm font-medium">{getStatusLabel(app.status)}</p>
               <p className="text-xs text-muted-foreground mt-0.5">Current Status</p>
            </div>
            {/* Real events would be mapped here (ApplicationEvent), stubbing common states for now */}
            {["applied_at", "viewed_at", "shortlisted_at", "offer_received_at", "rejected_at"].map(k => (
              app[k as keyof typeof app] && (
                <div key={k} className="relative pl-6 opacity-60">
                   <div className="absolute w-2 h-2 bg-muted-foreground rounded-full left-[-4px] top-1.5" />
                   <p className="text-sm">{k.replace("_at", "").replace("_", " ")}</p>
                   <p className="text-xs text-muted-foreground mt-0.5">{formatDate(app[k as keyof typeof app] as string)}</p>
                </div>
              )
            )).filter(Boolean).reverse()}
             <div className="relative pl-6 opacity-60">
               <div className="absolute w-2 h-2 bg-muted-foreground rounded-full left-[-4px] top-1.5" />
               <p className="text-sm">Created</p>
               <p className="text-xs text-muted-foreground mt-0.5">{formatDateTime(app.created_at)}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
