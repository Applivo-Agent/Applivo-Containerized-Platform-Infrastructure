"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { platformApi } from "@/lib/api";
import { toast } from "sonner";
import { Link2, Trash2, Plus, Shield, Globe, CheckCircle, XCircle, Clock, Eye, EyeOff, Loader2 } from "lucide-react";
import axios from "axios";

type PlatformConnectionStatus = {
  platform: string;
  is_valid: boolean;
  last_validated?: string | null;
  last_used?: string | null;
  expires_at?: string | null;
};

type PlatformStatusResponse = {
  platforms: PlatformConnectionStatus[];
};

type BrowserGuide = {
  name: string;
  steps: string[];
  caption: string;
};

function getSessionExpiryInfo(expiresAt?: string | null) {
  if (!expiresAt) {
    return { text: "No expiry info", daysRemaining: null, isExpiringSoon: false };
  }

  try {
    const expiryDate = new Date(expiresAt);
    const now = new Date();
    const daysRemaining = Math.ceil((expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    
    if (daysRemaining < 0) {
      return { text: "Expired", daysRemaining: 0, isExpiringSoon: true };
    }
    
    if (daysRemaining === 0) {
      return { text: "Expires today", daysRemaining: 0, isExpiringSoon: true };
    }
    
    if (daysRemaining === 1) {
      return { text: "Expires tomorrow", daysRemaining: 1, isExpiringSoon: true };
    }
    
    if (daysRemaining <= 7) {
      return { text: `${daysRemaining} days left`, daysRemaining, isExpiringSoon: true };
    }
    
    return { text: `${daysRemaining} days left`, daysRemaining, isExpiringSoon: false };
  } catch {
    return { text: "Invalid date", daysRemaining: null, isExpiringSoon: false };
  }
}

const BROWSER_GUIDES: BrowserGuide[] = [
  {
    name: "Chrome",
    caption: "Open Internshala and sign in before copying cookies.",
    steps: [
      "Go to internshala.com and log in normally with your email and password.",
      "Press F12 on your keyboard to open DevTools.",
      "Click the Application tab at the top of DevTools. If you do not see it, click the >> arrow.",
      "In the left sidebar, click Cookies, then click https://internshala.com.",
      "Click the Console tab.",
      "Paste the helper script below and press Enter.",
      "If DevTools shows allow pasting, type allow pasting once, then paste again.",
      "Go back to Applivo, paste the copied cookies, and click Connect.",
    ],
  },
  {
    name: "Firefox",
    caption: "Use Storage and Console to capture the session cookies.",
    steps: [
      "Log in to internshala.com normally.",
      "Press F12 to open DevTools.",
      "Click the Storage tab.",
      "Click Cookies, then click https://internshala.com.",
      "Click Console, paste the helper script, and press Enter.",
      "Paste the copied output into Applivo and click Connect.",
    ],
  },
  {
    name: "Safari",
    caption: "Enable Web Developer tools, then copy the cookies into Applivo.",
    steps: [
      "First enable DevTools in Safari Settings → Advanced by ticking Show features for web developers.",
      "Log in to internshala.com normally.",
      "Press Cmd+Option+I to open DevTools.",
      "Click Storage, then click Cookies.",
      "Click Console, paste the helper script, and press Enter.",
      "Paste the copied output into Applivo and click Connect.",
    ],
  },
];

const COOKIE_HELPER_SCRIPT = `copy(JSON.stringify(document.cookie.split(';').map(c=>{const[n,...v]=c.trim().split('=');return{name:n.trim(),value:v.join('=').trim(),domain:'.internshala.com',path:'/'}})))`;

const getErrorMessage = (err: unknown, fallback: string) => {
  if (axios.isAxiosError(err)) {
    return (err.response?.data as { detail?: string } | undefined)?.detail || fallback;
  }
  return fallback;
};

export default function ConnectPage() {
  const qc = useQueryClient();
  const platform = "internshala";
  const [cookieString, setCookieString] = useState("");
  const [scriptCopied, setScriptCopied] = useState(false);
  const [loginTab, setLoginTab] = useState<"credentials" | "cookies">("credentials");
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const { data: status, isLoading } = useQuery({
    queryKey: ["platform-status"],
    queryFn: () => platformApi.status().then((r) => r.data as PlatformStatusResponse),
  });

  const hasInternshalaConnection = (status?.platforms || []).some(
    (p) => p.platform === "internshala"
  );

  const connectMut = useMutation({
    mutationFn: () => platformApi.uploadCookies({ 
      platform, 
      cookies: cookieString 
    }),
    onSuccess: () => { 
      toast.success("Platform connected & cookies encrypted"); 
      setCookieString(""); 
      qc.invalidateQueries({ queryKey: ["platform-status"] }); 
    },
    onError: (err) => toast.error(getErrorMessage(err, "Failed to connect platform")),
  });

  const loginMut = useMutation({
    mutationFn: () => platformApi.login(platform, { 
      email: loginEmail, 
      password: loginPassword 
    }),
    onSuccess: () => { 
      toast.success("Logged in and cookies captured successfully!"); 
      setLoginEmail("");
      setLoginPassword("");
      setLoginTab("cookies");
      qc.invalidateQueries({ queryKey: ["platform-status"] }); 
    },
    onError: (err) => toast.error(getErrorMessage(err, "Login failed - check credentials or captcha")),
  });

  const invalidateMut = useMutation({
    mutationFn: (p: string) => platformApi.disconnect(p),
    onSuccess: () => { 
      toast.success("Platform disconnected"); 
      qc.invalidateQueries({ queryKey: ["platform-status"] }); 
    },
    onError: () => toast.error("Failed to disconnect"),
  });

  const handleCookiesSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!cookieString) return;
    connectMut.mutate();
  };

  const handleLoginSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!loginEmail || !loginPassword) {
      toast.error("Email and password are required");
      return;
    }
    loginMut.mutate();
  };

  const copyHelperScript = async () => {
    try {
      await navigator.clipboard.writeText(COOKIE_HELPER_SCRIPT);
      setScriptCopied(true);
      window.setTimeout(() => setScriptCopied(false), 2000);
    } catch {
      toast.error("Failed to copy helper script");
    }
  };

  const platformConnections = status?.platforms || [];

  return (
    <div className="max-w-4xl space-y-8">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-[#242424] border border-white/[0.08] rounded-lg">
          <Link2 className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Connect Platforms</h1>
          <p className="text-sm text-zinc-400 mt-1">Connect your job board accounts to enable automated applications.</p>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Connection Form */}
        <div className="bg-[#242424] border border-white/[0.08] rounded-2xl shadow-[inset_0_1px_0_rgba(255,255,255,0.035)] p-6">
          <h2 className="text-[12px] font-medium uppercase tracking-[0.2em] text-gray-400 mb-4 flex items-center gap-2">
            <Link2 className="w-5 h-5 text-white" /> 
            Connect {platform.charAt(0).toUpperCase() + platform.slice(1)}
          </h2>

          {hasInternshalaConnection && (
            <div className="mb-4 p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg text-[12px] text-amber-300">
              Internshala is already connected. Delete the existing connection from Active Sessions before connecting another account.
            </div>
          )}

          {/* Tabs */}
          <div className="flex gap-2 mb-5 border-b border-[#34343a]">
            <button
              onClick={() => setLoginTab("credentials")}
              className={`px-4 py-2.5 text-[12px] font-semibold uppercase tracking-[0.1em] transition-colors border-b-2 ${
                loginTab === "credentials"
                  ? "text-white border-white"
                  : "text-[#A1A1AA] border-transparent hover:text-white"
              }`}
            >
              Quick Login
            </button>
            <button
              onClick={() => setLoginTab("cookies")}
              className={`px-4 py-2.5 text-[12px] font-semibold uppercase tracking-[0.1em] transition-colors border-b-2 ${
                loginTab === "cookies"
                  ? "text-white border-white"
                  : "text-[#A1A1AA] border-transparent hover:text-white"
              }`}
            >
              Paste Cookies
            </button>
          </div>

          {/* Quick Login Tab */}
          {loginTab === "credentials" && (
            <form onSubmit={handleLoginSubmit} className="space-y-4">
              <div>
                <label className="block text-[10px] font-bold uppercase tracking-[0.2em] text-gray-500 mb-2">Email</label>
                <input
                  type="email"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  placeholder="your_email@internshala.com"
                  disabled={loginMut.isPending || hasInternshalaConnection}
                  className="w-full bg-[#1d1d1d] border border-[#34343a] rounded-lg px-3 py-2.5 text-[13px] text-white placeholder-[#A1A1AA] focus:border-white/30 transition-all outline-none disabled:opacity-50"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold uppercase tracking-[0.2em] text-gray-500 mb-2">Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    placeholder="your_password"
                    disabled={loginMut.isPending || hasInternshalaConnection}
                    className="w-full bg-[#1d1d1d] border border-[#34343a] rounded-lg px-3 py-2.5 pr-10 text-[13px] text-white placeholder-[#A1A1AA] focus:border-white/30 transition-all outline-none disabled:opacity-50"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    disabled={loginMut.isPending || hasInternshalaConnection}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-[#A1A1AA] hover:text-white transition-colors disabled:opacity-50"
                  >
                    {showPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              <div className="p-3 bg-[#232327] border border-[#34343a] rounded-lg flex gap-3 text-xs text-[#A1A1AA]">
                <Shield className="w-4 h-4 shrink-0 mt-0.5 text-white" />
                <p>We log in from the VPS server, capture session cookies, and delete credentials immediately. Passwords are never stored.</p>
              </div>

              <button 
                type="submit" 
                disabled={!loginEmail || !loginPassword || loginMut.isPending || hasInternshalaConnection} 
                className="w-full py-2.5 bg-white text-black rounded-lg text-[13px] font-semibold hover:bg-gray-200 transition-all disabled:opacity-80 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loginMut.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" /> 
                    Logging in...
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4" /> 
                    Connect via Login
                  </>
                )}
              </button>

              {loginMut.isPending && (
                <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg text-[12px] text-blue-300">
                  ⏳ Logging into Internshala and capturing cookies from VPS... This may take 30-60 seconds.
                </div>
              )}
            </form>
          )}

          {/* Paste Cookies Tab */}
          {loginTab === "cookies" && (
            <form onSubmit={handleCookiesSubmit} className="space-y-4">
              <div>
                <label className="block text-[10px] font-bold uppercase tracking-[0.2em] text-gray-500 mb-1">Raw Cookie String</label>
                <textarea
                  value={cookieString}
                  onChange={(e) => setCookieString(e.target.value)}
                  placeholder="Paste your document.cookie string or JSON cookie array here..."
                  rows={5}
                  className="w-full bg-[#1d1d1d] border border-[#34343a] rounded-lg px-3 py-2.5 text-[13px] font-mono text-white placeholder-[#A1A1AA] resize-none focus:border-white/30 transition-all outline-none"
                />
                <p className="text-[11px] text-[#A1A1AA] mt-1">
                  Open Internshala in your browser, then paste the cookie string or JSON array here. Applivo encrypts it and reuses the session for automation.
                </p>
              </div>
              
              <div className="p-3 bg-[#232327] border border-[#34343a] rounded-lg flex gap-3 text-xs text-[#A1A1AA]">
                <Shield className="w-4 h-4 shrink-0 mt-0.5 text-white" />
                <p>Your cookies are encrypted in the database and only decrypted in memory when the automation runs.</p>
              </div>

              <button 
                type="submit" 
                disabled={!cookieString || connectMut.isPending || hasInternshalaConnection} 
                className="w-full py-2.5 bg-white text-black rounded-lg text-[13px] font-semibold hover:bg-gray-200 transition-all disabled:opacity-80 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <Plus className="w-4 h-4" /> 
                {connectMut.isPending ? "Connecting..." : "Connect Platform"}
              </button>
            </form>
          )}
        </div>

        {/* Existing Connections */}
        <div className="bg-[#242424] border border-white/[0.08] rounded-2xl shadow-[inset_0_1px_0_rgba(255,255,255,0.035)] p-6">
          <h2 className="text-[12px] font-medium uppercase tracking-[0.2em] text-gray-400 mb-4">Active Sessions</h2>
          
          {isLoading ? (
            <div className="space-y-3">{[1,2].map(i => <div key={i} className="h-20 bg-[#1d1d1d] border border-white/[0.06] animate-pulse rounded-xl" />)}</div>
          ) : platformConnections.length > 0 ? (
            <div className="space-y-3">
              {platformConnections.map((p) => {
                const expiryInfo = getSessionExpiryInfo(p.expires_at);
                const expiryColor = expiryInfo.isExpiringSoon ? "text-amber-400" : "text-emerald-400";
                const expiryBgColor = expiryInfo.isExpiringSoon ? "bg-amber-500/10" : "bg-emerald-500/10";
                
                return (
                  <div key={p.platform} className="p-4 bg-[#1d1d1d] border border-[#34343a] rounded-xl flex items-center justify-between group">
                    <div className="flex items-center gap-3 flex-1">
                      <div className="w-10 h-10 rounded-lg bg-[#1d1d1d] flex flex-col items-center justify-center border border-[#34343a]">
                        <Globe className="w-4 h-4 text-white" />
                      </div>
                      <div className="flex-1">
                        <p className="font-semibold text-white text-[13px] capitalize flex items-center gap-2">
                          {p.platform} 
                          {p.is_valid ? (
                            <CheckCircle className="w-3 h-3 text-emerald-400" />
                          ) : (
                            <XCircle className="w-3 h-3 text-red-400" />
                          )}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <p className="text-[11px] text-[#A1A1AA]">
                            {p.is_valid ? "Connected - Bot enabled" : "Session expired - Reconnect"}
                          </p>
                          {p.expires_at && (
                            <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-md text-[10px] font-semibold uppercase tracking-wider ${expiryBgColor} ${expiryColor}`}>
                              <Clock className="w-3 h-3" />
                              {expiryInfo.text}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <button onClick={() => invalidateMut.mutate(p.platform)} className="p-2 text-[#A1A1AA] hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors opacity-0 group-hover:opacity-100">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="py-12 bg-[#1d1d1d] border border-[#34343a] rounded-2xl text-center">
              <Link2 className="w-8 h-8 opacity-30 mx-auto mb-2 text-white" />
              <p className="text-[11px] font-black uppercase tracking-[0.2em] text-zinc-500 mb-1">Sector Inactive</p>
              <p className="text-[10px] font-bold text-zinc-700 uppercase tracking-wider italic">
                Connect a platform to initialize automated deployments.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Browser instructions: placed after the cookie paste form */}
      <div className="rounded-2xl border border-white/[0.08] bg-[#1d1d1d] p-5 space-y-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-white">Browser instructions</h3>
            <p className="text-[12px] text-[#A1A1AA] mt-1">Use the method that matches your browser. The helper script works across all supported browsers.</p>
          </div>
          <div className="flex items-center gap-2">
            <a 
              href="/applivo_cookie_guide_v2.pdf" 
              target="_blank" 
              rel="noopener noreferrer"
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.2em] text-white hover:bg-white/10 transition"
            >
              📄 PDF Guide
            </a>
            <div className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-white">
              Copy once
            </div>
          </div>
        </div>

          <div className="space-y-4">
            {BROWSER_GUIDES.map((guide) => (
              <details key={guide.name} className="group rounded-xl border border-white/[0.08] bg-[#17171a] p-4 open:bg-[#19191d]" open={guide.name === "Chrome"}>
                <summary className="cursor-pointer list-none flex items-center justify-between gap-3">
                  <span className="text-sm font-semibold text-white">{guide.name}</span>
                  <span className="text-[10px] uppercase tracking-[0.2em] text-[#A1A1AA] group-open:text-white">Exact steps</span>
                </summary>
                <div className="mt-4 rounded-xl border border-white/[0.08] bg-[#101014] p-4">
                  <p className="text-[12px] leading-5 text-[#A1A1AA]">{guide.caption}</p>
                </div>
                <div className="mt-4 rounded-lg border border-white/[0.08] bg-[#111114] px-3 py-2 text-[11px] uppercase tracking-[0.2em] text-[#A1A1AA]">
                  {guide.name} cookie steps
                </div>
                <ol className="mt-4 space-y-2 text-[12px] leading-5 text-[#A1A1AA] list-decimal list-inside">
                  {guide.steps.map((step) => (
                    <li key={step}>{step}</li>
                  ))}
                </ol>
              </details>
            ))}
          </div>

          <div className="rounded-xl border border-dashed border-indigo-400/50 bg-indigo-500/10 p-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-indigo-200 mb-2">Helper script</p>
            <p className="text-[12px] text-[#C7D2FE] mb-3">
              Paste this into the browser console after logging in. If DevTools blocks pasting, type allow pasting once and press Enter, then paste the script again.
            </p>
            <div className="rounded-lg border border-white/10 bg-black/40 p-3 overflow-x-auto">
              <div className="flex items-start gap-3">
                <code className="flex-1 text-[11px] leading-5 text-indigo-100 break-all">{COOKIE_HELPER_SCRIPT}</code>
                <button
                  type="button"
                  onClick={copyHelperScript}
                  className="shrink-0 rounded-lg border border-white/10 bg-white px-3 py-1.5 text-[11px] font-semibold text-black transition hover:bg-gray-200"
                >
                  {scriptCopied ? "Copied" : "Copy"}
                </button>
              </div>
            </div>
          </div>
        </div>

    </div>
  );
}