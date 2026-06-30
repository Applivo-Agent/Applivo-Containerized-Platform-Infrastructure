"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import {
  Building2, Plus, Search, Loader2, Sparkles,
  CheckCircle2, AlertCircle, Mail, RefreshCw, X,
} from "lucide-react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

const STATUS_COLORS: Record<string, string> = {
  WATCHING: "#6b7280",
  RESEARCHING: "#f59e0b",
  RESEARCHED: "#3b82f6",
  CONTACTED: "#8b5cf6",
  REPLIED: "#10b981",
  INTERVIEWING: "#06b6d4",
  OFFER: "#f59e0b",
  ARCHIVED: "#374151",
};

const PRIORITY_COLORS: Record<string, string> = {
  HOT: "#ef4444",
  WARM: "#f59e0b",
  COLD: "#6b7280",
};

function useCompanies(search: string) {
  return useQuery({
    queryKey: ["outreach-companies", search],
    queryFn: async () => {
      const params = new URLSearchParams({ limit: "100" });
      if (search) params.set("search", search);
      const res = await api.get(`/outreach/companies?${params}`);
      return res.data as any[];
    },
    staleTime: 15_000,
  });
}

function Modal({ onClose, children }: { onClose: () => void; children: React.ReactNode }) {
  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.96 }}
        className="w-full max-w-md bg-[#1c1c1e] border border-zinc-800 rounded-2xl p-6 shadow-2xl"
      >
        {children}
      </motion.div>
    </div>
  );
}

function AddCompanyModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const [domain, setDomain] = useState("");
  const [priority, setPriority] = useState("WARM");
  const [autoResearch, setAutoResearch] = useState(true);

  const createMut = useMutation({
    mutationFn: async (data: any) => {
      const res = await api.post("/outreach/companies", data);
      return res.data;
    },
    onSuccess: async (company) => {
      qc.invalidateQueries({ queryKey: ["outreach-companies"] });
      qc.invalidateQueries({ queryKey: ["outreach-hub"] });
      if (autoResearch) {
        try { await api.post(`/outreach/companies/${company.id}/research`); } catch {}
      }
      onClose();
    },
  });

  return (
    <Modal onClose={onClose}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-bold tracking-tight text-white">Add Company</h2>
        <button onClick={onClose} className="p-1.5 text-zinc-500 hover:text-white transition-colors rounded-lg hover:bg-white/[0.05]">
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="space-y-4">
        <div>
          <label className="text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-1.5 block">Company name *</label>
          <input
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder="e.g. Stripe, Figma, Linear"
            className="w-full px-3 py-2.5 bg-[#1d1d1d] border border-white/[0.08] rounded-xl text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-white/25 transition-colors"
            autoFocus
          />
        </div>
        <div>
          <label className="text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-1.5 block">Domain (optional)</label>
          <input
            value={domain}
            onChange={e => setDomain(e.target.value)}
            placeholder="e.g. stripe.com"
            className="w-full px-3 py-2.5 bg-[#1d1d1d] border border-white/[0.08] rounded-xl text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-white/25 transition-colors"
          />
        </div>
        <div>
          <label className="text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-1.5 block">Priority</label>
          <div className="flex gap-2">
            {[["HOT", "Hot"], ["WARM", "Warm"], ["COLD", "Cold"]].map(([val, label]) => (
              <button
                key={val}
                onClick={() => setPriority(val)}
                className={cn(
                  "flex-1 py-2 rounded-xl text-xs font-bold uppercase tracking-wider border transition-all",
                  priority === val ? "border-white/25 bg-white/10 text-white" : "border-zinc-800 text-zinc-500 hover:text-zinc-300 hover:border-zinc-700"
                )}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
        <div className="flex items-start gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/[0.08]">
          <input
            type="checkbox"
            id="auto-research"
            checked={autoResearch}
            onChange={e => setAutoResearch(e.target.checked)}
            className="w-4 h-4 mt-0.5 accent-white"
          />
          <label htmlFor="auto-research" className="text-xs text-zinc-400 cursor-pointer leading-relaxed">
            <span className="text-white font-semibold">Auto-research company</span> — AI will gather intelligence, tech stack, news, and contacts in the background
          </label>
        </div>
      </div>

      <div className="flex gap-3 mt-6">
        <button onClick={onClose} className="flex-1 py-2.5 rounded-xl border border-zinc-800 text-sm text-zinc-400 hover:text-white hover:border-zinc-700 transition-colors">
          Cancel
        </button>
        <button
          onClick={() => createMut.mutate({ name, domain: domain || null, priority })}
          disabled={!name.trim() || createMut.isPending}
          className="flex-1 py-2.5 rounded-xl bg-white hover:bg-zinc-200 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-bold uppercase tracking-widest text-black transition-colors flex items-center justify-center gap-2"
        >
          {createMut.isPending ? <Loader2 className="w-4 h-4 animate-spin text-black" /> : <Plus className="w-4 h-4" />}
          Add Company
        </button>
      </div>
    </Modal>
  );
}

function EmailComposeModal({ company, onClose }: { company: any; onClose: () => void }) {
  const qc = useQueryClient();
  const [goal, setGoal] = useState("JOB_SEARCH");
  const [generating, setGenerating] = useState(false);
  const [email, setEmail] = useState<any>(null);
  const [editSubject, setEditSubject] = useState("");
  const [editBody, setEditBody] = useState("");
  const [approving, setApproving] = useState(false);
  const [approved, setApproved] = useState(false);
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);
  const [emailId, setEmailId] = useState<string | null>(null);

  const contacts = company?.contacts || [];
  const [selectedContact, setSelectedContact] = useState<string | null>(contacts[0]?.id || null);

  const generate = async () => {
    setGenerating(true);
    try {
      const res = await api.post("/outreach/emails/generate", {
        company_id: company.id,
        contact_id: selectedContact,
        campaign_goal: goal,
        sequence_position: 1,
        voice_style: "professional",
      });
      setEmail(res.data);
      setEditSubject(res.data.subject || "");
      setEditBody(res.data.body || "");
    } catch {}
    setGenerating(false);
  };

  const approve = async () => {
    if (!email) return;
    setApproving(true);
    try {
      await api.post(`/outreach/emails/${email.id}/approve`, { subject: editSubject, body: editBody });
      setEmailId(email.id);
      setApproved(true);
      qc.invalidateQueries({ queryKey: ["outreach-hub"] });
    } catch {}
    setApproving(false);
  };

  const qualityColor = email?.quality_score >= 85 ? "#10b981" : email?.quality_score >= 70 ? "#f59e0b" : "#ef4444";

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.96 }}
        className="w-full max-w-2xl bg-[#1c1c1e] border border-zinc-800 rounded-2xl flex flex-col max-h-[90vh] shadow-2xl"
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
          <div>
            <h2 className="text-sm font-bold tracking-tight text-white">Compose Outreach — {company.name}</h2>
            {email && (
              <p className="text-[11px] text-zinc-400 mt-0.5">
                Quality: <span style={{ color: qualityColor }} className="font-bold">{email.quality_score?.toFixed(0)}/100</span>
                {" · "}Reply probability: <span className="text-blue-400 font-bold">{((email.reply_probability || 0) * 100).toFixed(0)}%</span>
              </p>
            )}
          </div>
          <button onClick={onClose} className="p-1.5 text-zinc-500 hover:text-white transition-colors rounded-lg hover:bg-white/[0.05]">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="overflow-y-auto flex-1 p-6 space-y-4">
          {!email ? (
            <>
              {contacts.length > 0 && (
                <div>
                  <label className="text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2 block">Send to</label>
                  <div className="space-y-2">
                    {contacts.slice(0, 4).map((c: any) => (
                      <div
                        key={c.id}
                        onClick={() => setSelectedContact(c.id)}
                        className={cn(
                          "flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all",
                          selectedContact === c.id ? "border-white/25 bg-white/[0.05]" : "border-zinc-800 hover:border-zinc-700"
                        )}
                      >
                        <div className="w-7 h-7 rounded-full bg-[#222222] border border-zinc-800 flex items-center justify-center text-xs font-bold text-zinc-300">
                          {(c.name || "?")[0]?.toUpperCase()}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-white">{c.name || c.email}</p>
                          <p className="text-xs text-zinc-500">{c.title} · {c.email || "Email TBD"} · {Math.round((c.email_confidence || 0) * 100)}% confidence</p>
                        </div>
                        {selectedContact === c.id && <CheckCircle2 className="w-4 h-4 text-white flex-shrink-0" />}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <label className="text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2 block">Outreach goal</label>
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

              <button
                onClick={generate}
                className="w-full py-3 rounded-xl bg-white hover:bg-zinc-200 text-sm font-bold uppercase tracking-widest text-black transition-colors flex items-center justify-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                Generate Personalized Email
              </button>
            </>
          ) : approved ? (
            <div className="text-center py-10">
              <div className="w-16 h-16 rounded-full bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center mx-auto mb-4">
                {sent ? <Mail className="w-8 h-8 text-emerald-400" /> : <CheckCircle2 className="w-8 h-8 text-emerald-400" />}
              </div>
              <p className="text-lg font-bold tracking-tight text-white mb-1">{sent ? "Email Sent!" : "Email Approved!"}</p>
              <p className="text-sm text-zinc-400 mb-6">{sent ? "Your outreach email has been delivered." : "Your email is saved. Send it now or let the scheduler handle it."}</p>
              {!sent && emailId && (
                <button
                  onClick={async () => {
                    setSending(true);
                    try {
                      await api.post(`/outreach/emails/${emailId}/send`);
                      setSent(true);
                      qc.invalidateQueries({ queryKey: ["outreach-hub"] });
                    } catch (e: any) {
                      alert(e?.response?.data?.detail || "Failed to send email");
                    }
                    setSending(false);
                  }}
                  disabled={sending}
                  className="flex items-center gap-2 mx-auto px-6 py-2.5 rounded-xl bg-white hover:bg-zinc-200 disabled:opacity-50 text-sm font-bold uppercase tracking-widest text-black transition-colors"
                >
                  {sending ? <Loader2 className="w-4 h-4 animate-spin text-black" /> : <Mail className="w-4 h-4" />}
                  {sending ? "Sending…" : "Send Now via Gmail"}
                </button>
              )}
              {!sent && (
                <button onClick={onClose} className="block mx-auto mt-3 text-xs text-zinc-500 hover:text-zinc-300 transition-colors">
                  Schedule for later →
                </button>
              )}
              {sent && (
                <button onClick={onClose} className="mx-auto block px-4 py-1.5 rounded-xl border border-zinc-800 text-sm text-zinc-400 hover:text-white transition-colors">
                  Close
                </button>
              )}
            </div>
          ) : (
            <>
              <div className="flex items-center gap-3 p-3 rounded-xl bg-[#1d1d1d] border border-white/[0.08]">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-zinc-400">Quality Score</span>
                    <span className="text-[11px] font-bold" style={{ color: qualityColor }}>{email.quality_score?.toFixed(0)}/100</span>
                  </div>
                  <div className="h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                    <div className="h-full rounded-full transition-all" style={{ width: `${email.quality_score}%`, background: qualityColor }} />
                  </div>
                </div>
              </div>

              <div>
                <label className="text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-1.5 block">Subject</label>
                <input
                  value={editSubject}
                  onChange={e => setEditSubject(e.target.value)}
                  className="w-full px-3 py-2.5 bg-[#1d1d1d] border border-white/[0.08] rounded-xl text-sm text-white focus:outline-none focus:border-white/25 transition-colors"
                />
                {email.subject_options?.length > 1 && (
                  <div className="mt-2 space-y-1">
                    {email.subject_options.slice(1, 4).map((s: string, i: number) => (
                      <button
                        key={i}
                        onClick={() => setEditSubject(s)}
                        className="w-full text-left px-3 py-1.5 rounded-lg text-xs text-zinc-500 hover:text-zinc-200 hover:bg-white/[0.04] transition-colors truncate"
                      >
                        ↪ {s}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <label className="text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-1.5 block">Email body</label>
                <textarea
                  value={editBody}
                  onChange={e => setEditBody(e.target.value)}
                  rows={10}
                  className="w-full px-3 py-2.5 bg-[#1d1d1d] border border-white/[0.08] rounded-xl text-sm text-white leading-relaxed focus:outline-none focus:border-white/25 transition-colors resize-none"
                />
                <p className="text-[10px] text-zinc-600 mt-1">{editBody.split(/\s+/).filter(Boolean).length} words</p>
              </div>

              {email.personalization_hooks?.length > 0 && (
                <div className="p-3 rounded-xl bg-[#1d1d1d] border border-emerald-500/20">
                  <p className="text-[11px] font-bold uppercase tracking-wider text-emerald-400 mb-2">Personalization hooks used</p>
                  <div className="space-y-1">
                    {email.personalization_hooks.map((h: string, i: number) => (
                      <p key={i} className="text-xs text-zinc-400 flex items-start gap-1.5">
                        <CheckCircle2 className="w-3 h-3 text-emerald-500 flex-shrink-0 mt-0.5" />
                        {h}
                      </p>
                    ))}
                  </div>
                </div>
              )}

              {email.quality_suggestions?.length > 0 && (
                <div className="p-3 rounded-xl bg-[#1d1d1d] border border-amber-500/20">
                  <p className="text-[11px] font-bold uppercase tracking-wider text-amber-400 mb-2">Suggestions to improve</p>
                  {email.quality_suggestions.map((s: string, i: number) => (
                    <p key={i} className="text-xs text-zinc-400 flex items-start gap-1.5 mb-1">
                      <AlertCircle className="w-3 h-3 text-amber-500 flex-shrink-0 mt-0.5" />
                      {s}
                    </p>
                  ))}
                </div>
              )}
            </>
          )}
        </div>

        {email && !approved && (
          <div className="px-6 py-4 border-t border-zinc-800 flex gap-3">
            <button
              onClick={generate}
              disabled={generating}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-zinc-800 bg-[#1d1d1d] hover:bg-[#222222] text-sm text-zinc-400 hover:text-white transition-all"
            >
              {generating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5" />}
              Regenerate
            </button>
            <button
              onClick={approve}
              disabled={approving || !editSubject || !editBody}
              className="flex-1 py-2.5 rounded-xl bg-white hover:bg-zinc-200 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-bold uppercase tracking-widest text-black transition-colors flex items-center justify-center gap-2"
            >
              {approving ? <Loader2 className="w-4 h-4 animate-spin text-black" /> : <CheckCircle2 className="w-4 h-4" />}
              Approve Email
            </button>
          </div>
        )}

        {generating && (
          <div className="px-6 py-4 border-t border-zinc-800 flex items-center justify-center gap-3 text-sm text-zinc-400">
            <Loader2 className="w-4 h-4 animate-spin" />
            AI is researching {company.name} and writing your email...
          </div>
        )}
      </motion.div>
    </div>
  );
}

function CompanyCard({ company, onResearch, onCompose }: {
  company: any;
  onResearch: (id: string) => void;
  onCompose: (company: any) => void;
}) {
  const statusColor = STATUS_COLORS[company.status] || "#6b7280";
  const priorityColor = PRIORITY_COLORS[company.priority] || "#6b7280";

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
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#222222] border border-white/[0.08] flex items-center justify-center group-hover:scale-110 transition-transform">
              <Building2 className="w-5 h-5 text-zinc-400 group-hover:text-white transition-colors" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-white">{company.name}</h3>
                <div className="w-1.5 h-1.5 rounded-full" style={{ background: priorityColor }} title={company.priority} />
              </div>
              {company.domain && <p className="text-[11px] text-zinc-500 mt-0.5">{company.domain}</p>}
            </div>
          </div>
          <span
            className="text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border capitalize"
            style={{ color: statusColor, borderColor: `${statusColor}40`, background: `${statusColor}12` }}
          >
            {company.status?.replace(/_/g, " ")}
          </span>
        </div>

        {company.research_status === "COMPLETE" && company.intelligence ? (
          <div className="mb-4 space-y-2.5">
            <p className="text-[11px] text-zinc-400 leading-relaxed line-clamp-2">{company.intelligence.executive_summary}</p>
            {company.intelligence.tech_stack?.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {company.intelligence.tech_stack.slice(0, 5).map((t: string) => (
                  <span key={t} className="px-2 py-0.5 rounded-md text-[10px] bg-[#1d1d1d] text-zinc-400 border border-white/[0.08] font-medium">{t}</span>
                ))}
              </div>
            )}
          </div>
        ) : company.research_status === "IN_PROGRESS" ? (
          <div className="mb-4 flex items-center gap-2 text-[11px] text-amber-400 p-3 bg-amber-500/5 border border-amber-500/20 rounded-xl">
            <Loader2 className="w-3 h-3 animate-spin" />
            AI researching company...
          </div>
        ) : company.research_status === "FAILED" ? (
          <p className="text-[11px] text-red-400 mb-4 p-2 bg-red-500/5 border border-red-500/20 rounded-xl">Research failed — try again</p>
        ) : (
          <p className="text-[11px] text-zinc-600 mb-4">Not yet researched</p>
        )}

        {company.match_score && (
          <div className="mb-4">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[10px] font-bold uppercase tracking-wider text-zinc-500">Match score</span>
              <span className="text-[10px] font-bold text-emerald-400">{Math.round(company.match_score)}%</span>
            </div>
            <div className="h-1.5 bg-white/[0.05] rounded-full overflow-hidden">
              <div className="h-full bg-emerald-500 rounded-full opacity-60" style={{ width: `${company.match_score}%` }} />
            </div>
          </div>
        )}

        <div className="flex gap-2">
          {company.research_status !== "COMPLETE" && company.research_status !== "IN_PROGRESS" && (
            <button
              onClick={() => onResearch(company.id)}
              className="flex-1 py-2 rounded-xl bg-[#1d1d1d] hover:bg-[#222222] border border-white/[0.08] hover:border-white/20 text-xs font-bold uppercase tracking-wider text-zinc-400 hover:text-white transition-all flex items-center justify-center gap-1.5"
            >
              <Sparkles className="w-3 h-3" />
              Research
            </button>
          )}
          <button
            onClick={() => onCompose(company)}
            disabled={company.research_status === "IN_PROGRESS"}
            className="flex-1 py-2 rounded-xl bg-[#1d1d1d] hover:bg-[#222222] border border-white/[0.08] hover:border-white/20 text-xs font-bold uppercase tracking-wider text-zinc-400 hover:text-white transition-all flex items-center justify-center gap-1.5 disabled:opacity-40"
          >
            <Mail className="w-3 h-3" />
            Compose
          </button>
        </div>
      </div>
    </motion.div>
  );
}

export default function CompaniesPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [showAdd, setShowAdd] = useState(false);
  const [composeTarget, setComposeTarget] = useState<any>(null);

  const { data: companies = [], isLoading } = useCompanies(search);

  const researchMut = useMutation({
    mutationFn: async (companyId: string) => {
      await api.post(`/outreach/companies/${companyId}/research`);
    },
    onSuccess: () => {
      setTimeout(() => qc.invalidateQueries({ queryKey: ["outreach-companies"] }), 2000);
    },
  });

  const handleCompose = async (company: any) => {
    if (!company.contacts) {
      try {
        const res = await api.get(`/outreach/companies/${company.id}`);
        setComposeTarget(res.data);
      } catch {
        setComposeTarget(company);
      }
    } else {
      setComposeTarget(company);
    }
  };

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 p-1 md:p-4 min-h-[90vh]">

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white/90">Companies</h2>
          <p className="text-[11px] text-zinc-400 mt-1">{companies.length} companies · AI-researched targets</p>
        </div>
        <button
          onClick={() => setShowAdd(true)}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white text-black text-sm font-bold uppercase tracking-widest hover:bg-zinc-200 transition-colors self-start md:self-auto"
        >
          <Plus className="w-4 h-4" />
          Add Company
        </button>
      </div>

      <div className="relative">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-600" />
        <input
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search companies..."
          className="w-full pl-10 pr-4 py-2.5 bg-[#1c1c1e] border border-zinc-800 rounded-xl text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-white/25 transition-colors"
        />
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-52 bg-[#1c1c1e] border border-zinc-800 rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : companies.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 text-center bg-[#1c1c1e] border border-zinc-800 rounded-2xl">
          <div className="w-16 h-16 rounded-full bg-[#1d1d1d] border border-white/[0.08] flex items-center justify-center mx-auto mb-6">
            <Building2 className="w-7 h-7 text-zinc-600" />
          </div>
          <p className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400 mb-2">No Companies Yet</p>
          <p className="text-[9px] font-bold text-zinc-600 max-w-[200px] mx-auto uppercase tracking-wider leading-relaxed italic mb-6">
            Add companies you want to reach out to. AI will research them automatically.
          </p>
          <button
            onClick={() => setShowAdd(true)}
            className="px-5 py-2 bg-white text-black text-[9px] font-black uppercase tracking-tighter rounded-lg hover:bg-zinc-200 transition-colors"
          >
            Add Your First Company
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {companies.map((company: any) => (
            <CompanyCard
              key={company.id}
              company={company}
              onResearch={(id) => researchMut.mutate(id)}
              onCompose={handleCompose}
            />
          ))}
        </div>
      )}

      <AnimatePresence>
        {showAdd && <AddCompanyModal onClose={() => setShowAdd(false)} />}
        {composeTarget && <EmailComposeModal company={composeTarget} onClose={() => setComposeTarget(null)} />}
      </AnimatePresence>
    </div>
  );
}
