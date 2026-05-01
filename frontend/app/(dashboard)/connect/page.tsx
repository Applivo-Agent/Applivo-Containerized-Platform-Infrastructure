"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { platformApi } from "@/lib/api";
import { toast } from "sonner";
import { Link2, Trash2, Plus, Shield, Globe, CheckCircle, XCircle, Key, Cookie, Eye, EyeOff } from "lucide-react";
import axios from "axios";

type ConnectionMode = "login" | "cookies";

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

const getErrorMessage = (err: unknown, fallback: string) => {
  if (axios.isAxiosError(err)) {
    return (err.response?.data as { detail?: string } | undefined)?.detail || fallback;
  }
  return fallback;
};

export default function ConnectPage() {
  const qc = useQueryClient();
  const platform = "internshala";
  const [mode, setMode] = useState<ConnectionMode>("login");
  const [cookieString, setCookieString] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loginFallbackMessage, setLoginFallbackMessage] = useState<string | null>(null);

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
      setLoginFallbackMessage(null);
      qc.invalidateQueries({ queryKey: ["platform-status"] }); 
    },
    onError: (err) => toast.error(getErrorMessage(err, "Failed to connect platform")),
  });

  const loginMut = useMutation({
    mutationFn: () => platformApi.login(platform, { email, password }),
    onSuccess: () => { 
      toast.success("Successfully logged into " + platform);
      setEmail("");
      setPassword("");
      setLoginFallbackMessage(null);
      qc.invalidateQueries({ queryKey: ["platform-status"] });
    },
    onError: (err) => {
      const message = getErrorMessage(err, "Login failed - check credentials or try again");
      toast.error(message);

      if (
        message.toLowerCase().includes("captcha") ||
        message.toLowerCase().includes("timeout") ||
        message.toLowerCase().includes("verification") ||
        message.toLowerCase().includes("bad request")
      ) {
        setMode("cookies");
        setLoginFallbackMessage(
          "Internshala blocked the automated login on this server. Paste cookies from your browser to connect the session instead."
        );
      }
    },
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
    if (!email || !password) return;
    loginMut.mutate();
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

          {loginFallbackMessage && (
            <div className="mb-4 p-3 bg-indigo-500/10 border border-indigo-500/30 rounded-lg text-[12px] text-indigo-300">
              {loginFallbackMessage}
            </div>
          )}
          
          <div className="flex gap-2 mb-4">
            <button
              type="button"
              onClick={() => setMode("login")}
              disabled={hasInternshalaConnection}
              className={`flex-1 py-2 px-3 text-[11px] font-medium rounded-lg flex items-center justify-center gap-2 transition-all ${
                mode === "login" 
                  ? "bg-white text-black" 
                  : "bg-[#1d1d1d] border border-[#34343a] text-[#A1A1AA] hover:bg-[#1d1d1d]"
              } ${hasInternshalaConnection ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              <Key className="w-3 h-3" /> Login with Email
            </button>
            <button
              type="button"
              onClick={() => setMode("cookies")}
              disabled={hasInternshalaConnection}
              className={`flex-1 py-2 px-3 text-[11px] font-medium rounded-lg flex items-center justify-center gap-2 transition-all ${
                mode === "cookies" 
                  ? "bg-white text-black" 
                  : "bg-[#1d1d1d] border border-[#34343a] text-[#A1A1AA] hover:bg-[#1d1d1d]"
              } ${hasInternshalaConnection ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              <Cookie className="w-3 h-3" /> Paste Cookies
            </button>
          </div>

          {mode === "login" ? (
            <form onSubmit={handleLoginSubmit} className="space-y-4">
              <div>
                <label className="block text-[10px] font-bold uppercase tracking-[0.2em] text-gray-500 mb-1">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  className="w-full bg-[#1d1d1d] border border-[#34343a] rounded-lg px-3 py-2.5 text-[13px] text-white placeholder-[#A1A1AA] focus:border-white/30 transition-all outline-none"
                />
              </div>
              <div>
                <label className="block text-[10px] font-bold uppercase tracking-[0.2em] text-gray-500 mb-1">Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Your Internshala password"
                    className="w-full bg-[#1d1d1d] border border-[#34343a] rounded-lg px-3 py-2.5 pr-10 text-[13px] text-white placeholder-[#A1A1AA] focus:border-white/30 transition-all outline-none"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-[#A1A1AA] hover:text-white transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              
              <div className="p-3 bg-[#1d1d1d] border border-[#34343a] rounded-lg flex gap-3 text-[11px] text-[#A1A1AA]">
                <Shield className="w-4 h-4 shrink-0 mt-0.5 text-white" />
                <p>Your credentials are never stored. We use them only to obtain a session and then save encrypted cookies.</p>
              </div>

              <button 
                type="submit" 
                disabled={loginMut.isPending || hasInternshalaConnection} 
                className="w-full py-2.5 bg-white text-black rounded-lg text-[13px] font-semibold hover:bg-gray-200 transition-all disabled:opacity-80 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <Globe className="w-4 h-4" /> 
                {loginMut.isPending ? "Logging in..." : "Login to " + platform}
              </button>

              {loginMut.isPending && (
                <p className="text-[11px] text-center text-[#A1A1AA]">
                  A browser window opened. Log in to Internshala manually, then wait for success.
                </p>
              )}
            </form>
          ) : (
            <form onSubmit={handleCookiesSubmit} className="space-y-4">
              <div>
                <label className="block text-[10px] font-bold uppercase tracking-[0.2em] text-gray-500 mb-1">Raw Cookie String</label>
                <textarea
                  value={cookieString}
                  onChange={(e) => setCookieString(e.target.value)}
                  placeholder="Paste your document.cookie string here..."
                  rows={4}
                  className="w-full bg-[#1d1d1d] border border-[#34343a] rounded-lg px-3 py-2.5 text-[13px] font-mono text-white placeholder-[#A1A1AA] resize-none focus:border-white/30 transition-all outline-none"
                />
                <p className="text-[11px] text-[#A1A1AA] mt-1">
                  Log into {platform}, open DevTools → Console, type <code className="bg-[#232327] px-1 py-0.5 rounded text-white border border-white/10">document.cookie</code> and paste.
                </p>
              </div>
              
              <div className="p-3 bg-[#232327] border border-[#34343a] rounded-lg flex gap-3 text-xs text-[#A1A1AA]">
                <Shield className="w-4 h-4 shrink-0 mt-0.5 text-white" />
                <p>Your cookies are encrypted in our database using AES-256 and only decrypted in memory when the automation runs.</p>
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
              {platformConnections.map((p) => (
                <div key={p.platform} className="p-4 bg-[#1d1d1d] border border-[#34343a] rounded-xl flex items-center justify-between group">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-[#1d1d1d] flex flex-col items-center justify-center border border-[#34343a]">
                      <Globe className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <p className="font-semibold text-white text-[13px] capitalize flex items-center gap-2">
                        {p.platform} 
                        {p.is_valid ? (
                          <CheckCircle className="w-3 h-3 text-emerald-400" />
                        ) : (
                          <XCircle className="w-3 h-3 text-red-400" />
                        )}
                      </p>
                      <p className="text-[11px] text-[#A1A1AA]">
                        {p.is_valid ? "Connected - Bot enabled" : "Session expired - Reconnect"}
                      </p>
                    </div>
                  </div>
                  <button onClick={() => invalidateMut.mutate(p.platform)} className="p-2 text-[#A1A1AA] hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors opacity-0 group-hover:opacity-100">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
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
    </div>
  );
}