"use client";

import { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import {
  Mail, CheckCircle2, AlertCircle, Loader2,
  Unlink, RefreshCw, Clock, Shield, Zap,
  ExternalLink
} from "lucide-react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

function useEmailConnectors() {
  return useQuery({
    queryKey: ["outreach-connectors"],
    queryFn: async () => {
      const res = await api.get("/outreach/connectors");
      return res.data as any[];
    },
    staleTime: 30_000,
  });
}

function useGitHubConnector() {
  return useQuery({
    queryKey: ["outreach-github-connector"],
    queryFn: async () => {
      const res = await api.get("/outreach/connectors/github");
      return res.data as any | null;
    },
    staleTime: 30_000,
  });
}

function GitHubIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
    </svg>
  );
}

function GmailConnectorCard({ connector, onDisconnect }: { connector: any; onDisconnect: () => void }) {
  const disconnectMut = useMutation({
    mutationFn: async () => api.delete(`/outreach/connectors/${connector.id}`),
    onSuccess: onDisconnect,
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center gap-4 p-4 bg-[#1d1d1d] border border-emerald-500/20 rounded-2xl"
    >
      <div className="w-12 h-12 rounded-xl bg-[#222222] border border-white/[0.08] flex items-center justify-center shrink-0">
        <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none">
          <path d="M22 6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6z" fill="#EA4335" fillOpacity=".2" stroke="#EA4335" strokeWidth=".5"/>
          <path d="M22 6l-10 7L2 6" stroke="#EA4335" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="text-sm font-bold text-white">Gmail</p>
          <span className="text-[9px] font-black uppercase tracking-wider px-2 py-0.5 rounded-md bg-emerald-500/15 text-emerald-400 border border-emerald-500/20">
            Connected
          </span>
        </div>
        <p className="text-[11px] text-zinc-400 mt-0.5 truncate">{connector.email_address || "Unknown address"}</p>
        {connector.last_sync_at && (
          <p className="text-[10px] text-zinc-600 mt-0.5">
            Last synced: {new Date(connector.last_sync_at).toLocaleString()}
          </p>
        )}
      </div>
      <button
        onClick={() => disconnectMut.mutate()}
        disabled={disconnectMut.isPending}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-zinc-800 bg-[#1d1d1d] hover:bg-[#222222] hover:border-red-500/30 text-[11px] font-bold uppercase tracking-wider text-zinc-500 hover:text-red-400 transition-all"
      >
        {disconnectMut.isPending ? <Loader2 className="w-3 h-3 animate-spin" /> : <Unlink className="w-3 h-3" />}
        Disconnect
      </button>
    </motion.div>
  );
}

function ConnectGmailCard({ onConnecting }: { onConnecting: () => void }) {
  const connectMut = useMutation({
    mutationFn: async () => {
      const res = await api.post("/outreach/connectors/gmail/auth");
      return res.data as { auth_url: string };
    },
    onSuccess: (data) => {
      onConnecting();
      window.location.href = data.auth_url;
    },
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center gap-4 p-4 bg-[#1d1d1d] border border-zinc-800 rounded-2xl hover:border-zinc-700 transition-all group"
    >
      <div className="w-12 h-12 rounded-xl bg-[#222222] border border-white/[0.08] flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform">
        <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none">
          <path d="M22 6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6z" fill="#EA4335" fillOpacity=".15" stroke="#EA4335" strokeWidth=".5"/>
          <path d="M22 6l-10 7L2 6" stroke="#EA4335" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-bold text-white">Connect Gmail</p>
        <p className="text-[11px] text-zinc-400 mt-0.5">Send outreach emails directly from your Gmail account</p>
      </div>
      <button
        onClick={() => connectMut.mutate()}
        disabled={connectMut.isPending}
        className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white hover:bg-zinc-200 disabled:opacity-50 text-sm font-bold uppercase tracking-widest text-black transition-colors whitespace-nowrap"
      >
        {connectMut.isPending ? <Loader2 className="w-4 h-4 animate-spin text-black" /> : null}
        {connectMut.isPending ? "Redirecting…" : "Connect"}
      </button>
    </motion.div>
  );
}

function GitHubConnectorCard({ connector, onDisconnect }: { connector: any; onDisconnect: () => void }) {
  const disconnectMut = useMutation({
    mutationFn: async () => api.delete(`/outreach/connectors/github/${connector.id}`),
    onSuccess: onDisconnect,
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center gap-4 p-4 bg-[#1d1d1d] border border-emerald-500/20 rounded-2xl"
    >
      <div className="w-12 h-12 rounded-xl bg-[#222222] border border-white/[0.08] flex items-center justify-center shrink-0">
        <GitHubIcon className="w-6 h-6 text-white" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="text-sm font-bold text-white">@{connector.github_username || "GitHub"}</p>
          <span className="text-[9px] font-black uppercase tracking-wider px-2 py-0.5 rounded-md bg-emerald-500/15 text-emerald-400 border border-emerald-500/20">
            Connected
          </span>
        </div>
        <div className="flex items-center gap-3 mt-1">
          {connector.repo_count !== null && (
            <span className="text-[10px] text-zinc-400">{connector.repo_count} repos</span>
          )}
          {connector.star_count !== null && (
            <span className="text-[10px] text-zinc-400">{connector.star_count} stars</span>
          )}
        </div>
        {connector.last_sync_at && (
          <p className="text-[10px] text-zinc-600 mt-0.5">
            Last synced: {new Date(connector.last_sync_at).toLocaleString()}
          </p>
        )}
      </div>
      <button
        onClick={() => disconnectMut.mutate()}
        disabled={disconnectMut.isPending}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-zinc-800 bg-[#1d1d1d] hover:bg-[#222222] hover:border-red-500/30 text-[11px] font-bold uppercase tracking-wider text-zinc-500 hover:text-red-400 transition-all"
      >
        {disconnectMut.isPending ? <Loader2 className="w-3 h-3 animate-spin" /> : <Unlink className="w-3 h-3" />}
        Disconnect
      </button>
    </motion.div>
  );
}

function ConnectGitHubCard({ onConnecting }: { onConnecting: () => void }) {
  const connectMut = useMutation({
    mutationFn: async () => {
      const res = await api.post("/outreach/connectors/github/auth");
      return res.data as { auth_url: string };
    },
    onSuccess: (data) => {
      onConnecting();
      window.location.href = data.auth_url;
    },
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center gap-4 p-4 bg-[#1d1d1d] border border-zinc-800 rounded-2xl hover:border-zinc-700 transition-all group"
    >
      <div className="w-12 h-12 rounded-xl bg-[#222222] border border-white/[0.08] flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform">
        <GitHubIcon className="w-6 h-6 text-zinc-400 group-hover:text-white transition-colors" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-bold text-white">Connect GitHub</p>
        <p className="text-[11px] text-zinc-400 mt-0.5">Link your GitHub profile to showcase repos in outreach</p>
      </div>
      <button
        onClick={() => connectMut.mutate()}
        disabled={connectMut.isPending}
        className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white hover:bg-zinc-200 disabled:opacity-50 text-sm font-bold uppercase tracking-widest text-black transition-colors whitespace-nowrap"
      >
        {connectMut.isPending ? <Loader2 className="w-4 h-4 animate-spin text-black" /> : null}
        {connectMut.isPending ? "Redirecting…" : "Connect"}
      </button>
    </motion.div>
  );
}

export default function OutreachSettingsPage() {
  const searchParams = useSearchParams();
  const qc = useQueryClient();
  const [banner, setBanner] = useState<"success" | "error" | null>(null);
  const [connectingGmail, setConnectingGmail] = useState(false);
  const [connectingGitHub, setConnectingGitHub] = useState(false);

  const { data: emailConnectors = [], isLoading: emailLoading, refetch: refetchEmail } = useEmailConnectors();
  const { data: githubConnector, isLoading: githubLoading, refetch: refetchGitHub } = useGitHubConnector();
  
  const gmailConnector = emailConnectors.find((c: any) => c.provider === "gmail");

  // Handle OAuth callback query params
  useEffect(() => {
    const connected = searchParams.get("connected");
    const githubConnected = searchParams.get("github_connected");
    const error = searchParams.get("error");
    if (connected === "true" || githubConnected === "true") {
      setBanner("success");
      refetchEmail();
      refetchGitHub();
      window.history.replaceState({}, "", "/outreach/settings");
    } else if (error) {
      setBanner("error");
      window.history.replaceState({}, "", "/outreach/settings");
    }
  }, [searchParams, refetchEmail, refetchGitHub]);

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 p-1 md:p-4 min-h-[90vh]">

      <div>
        <h2 className="text-xl font-bold tracking-tight text-white/90">Outreach Settings</h2>
        <p className="text-[11px] text-zinc-400 mt-1">Connect your accounts to power outreach automation</p>
      </div>

      {/* Status banners */}
      {banner === "success" && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
          <p className="text-sm font-medium text-emerald-400">Account connected successfully!</p>
          <button onClick={() => setBanner(null)} className="ml-auto text-emerald-400/60 hover:text-emerald-400">×</button>
        </motion.div>
      )}
      {banner === "error" && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
          <p className="text-sm font-medium text-red-400">Connection failed. Please try again.</p>
          <button onClick={() => setBanner(null)} className="ml-auto text-red-400/60 hover:text-red-400">×</button>
        </motion.div>
      )}

      {/* Email connector section */}
      <div className="bg-[#242424] border border-white/[0.08] rounded-2xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="font-bold text-lg tracking-tight">Email Account</h3>
            <p className="text-[11px] text-zinc-400 mt-0.5">Connect your inbox so Applivo can send outreach on your behalf</p>
          </div>
          <Mail className="w-4 h-4 text-zinc-600" />
        </div>

        {emailLoading ? (
          <div className="h-20 bg-[#1d1d1d] border border-zinc-800 rounded-2xl animate-pulse" />
        ) : gmailConnector ? (
          <GmailConnectorCard
            connector={gmailConnector}
            onDisconnect={() => {
              qc.invalidateQueries({ queryKey: ["outreach-connectors"] });
            }}
          />
        ) : (
          <ConnectGmailCard onConnecting={() => setConnectingGmail(true)} />
        )}

        {connectingGmail && !gmailConnector && (
          <div className="flex items-center gap-2 mt-3 text-[11px] text-zinc-500">
            <Loader2 className="w-3 h-3 animate-spin" />
            Redirecting to Google…
          </div>
        )}
      </div>

      {/* GitHub connector section */}
      <div className="bg-[#242424] border border-white/[0.08] rounded-2xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="font-bold text-lg tracking-tight">GitHub Profile</h3>
            <p className="text-[11px] text-zinc-400 mt-0.5">Link your GitHub to showcase repositories and coding activity in outreach</p>
          </div>
          <GitHubIcon className="w-4 h-4 text-zinc-600" />
        </div>

        {githubLoading ? (
          <div className="h-20 bg-[#1d1d1d] border border-zinc-800 rounded-2xl animate-pulse" />
        ) : githubConnector ? (
          <GitHubConnectorCard
            connector={githubConnector}
            onDisconnect={() => {
              qc.invalidateQueries({ queryKey: ["outreach-github-connector"] });
            }}
          />
        ) : (
          <ConnectGitHubCard onConnecting={() => setConnectingGitHub(true)} />
        )}

        {connectingGitHub && !githubConnector && (
          <div className="flex items-center gap-2 mt-3 text-[11px] text-zinc-500">
            <Loader2 className="w-3 h-3 animate-spin" />
            Redirecting to GitHub…
          </div>
        )}
      </div>

      {/* How it works */}
      <div className="bg-[#242424] border border-white/[0.08] rounded-2xl p-6">
        <h3 className="font-bold text-lg tracking-tight mb-6">How it works</h3>
        <div className="space-y-3">
          {[
            { icon: Shield,  title: "Secure OAuth2",        desc: "We use official OAuth2 flows — your password is never stored. Tokens are AES-256 encrypted at rest." },
            { icon: Mail,    title: "Send from your inbox", desc: "Emails go out from your real Gmail address. Recipients see your name and address, not a marketing domain." },
            { icon: RefreshCw, title: "Reply detection",    desc: "Applivo polls your Gmail inbox hourly and automatically marks conversations as 'Replied' when you get a response." },
            { icon: Zap,     title: "Scheduled delivery",   desc: "Approved emails are sent automatically at the scheduled time via Celery background tasks." },
            { icon: Clock,   title: "Follow-up reminders",  desc: "After 5 days without a reply, a follow-up draft is automatically queued for your review." },
          ].map((item, i) => (
            <motion.div
              key={item.title}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 + i * 0.05 }}
              className="flex items-start gap-4 p-4 bg-[#1d1d1d] border border-white/[0.08] rounded-2xl"
            >
              <div className="w-10 h-10 rounded-xl bg-[#222222] border border-white/[0.08] flex items-center justify-center shrink-0 mt-0.5">
                <item.icon className="w-4 h-4 text-zinc-400" />
              </div>
              <div>
                <p className="text-sm font-bold text-white">{item.title}</p>
                <p className="text-[11px] text-zinc-400 mt-1 leading-relaxed">{item.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

    </div>
  );
}
