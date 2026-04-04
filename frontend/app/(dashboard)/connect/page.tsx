"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { platformApi } from "@/lib/api";
import { toast } from "sonner";
import { Link2, Trash2, Plus, Shield, Globe, Lock, CheckCircle, XCircle, Key, Cookie } from "lucide-react";

type ConnectionMode = "login" | "cookies";

export default function ConnectPage() {
  const qc = useQueryClient();
  const [platform, setPlatform] = useState("internshala");
  const [mode, setMode] = useState<ConnectionMode>("login");
  const [cookieString, setCookieString] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const { data: status, isLoading } = useQuery({
    queryKey: ["platform-status"],
    queryFn: () => platformApi.status().then((r) => r.data),
  });

  const connectMut = useMutation({
    mutationFn: () => platformApi.connect({ 
      platform, 
      cookies: cookieString 
    }),
    onSuccess: () => { 
      toast.success("Platform connected & cookies encrypted"); 
      setCookieString(""); 
      qc.invalidateQueries({ queryKey: ["platform-status"] }); 
    },
    onError: (err: any) => toast.error(err?.response?.data?.detail || "Failed to connect platform"),
  });

  const loginMut = useMutation({
    mutationFn: () => platformApi.login(platform, { email, password }),
    onSuccess: (res) => { 
      toast.success("Successfully logged into " + platform);
      setEmail("");
      setPassword("");
      qc.invalidateQueries({ queryKey: ["platform-status"] });
    },
    onError: (err: any) => toast.error(err?.response?.data?.detail || "Login failed - check credentials or try again"),
  });

  const invalidateMut = useMutation({
    mutationFn: (p: string) => platformApi.invalidate(p),
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

  const platforms = status?.platforms || [];

  return (
    <div className="max-w-4xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold font-display">Connect Platforms</h1>
        <p className="text-muted-foreground text-sm mt-1">Connect your job board accounts to enable automated applications.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Connection Form */}
        <div className="glass-card p-6">
          <h2 className="font-semibold mb-4 flex items-center gap-2">
            <Link2 className="w-5 h-5 text-brand-purple-light" /> 
            Connect {platform.charAt(0).toUpperCase() + platform.slice(1)}
          </h2>
          
          <div className="flex gap-2 mb-4">
            <button
              type="button"
              onClick={() => setMode("login")}
              className={`flex-1 py-2 px-3 text-xs font-medium rounded-lg flex items-center justify-center gap-2 transition-all ${
                mode === "login" 
                  ? "bg-brand-purple text-white" 
                  : "bg-muted text-muted-foreground hover:bg-muted/80"
              }`}
            >
              <Key className="w-3 h-3" /> Login with Email
            </button>
            <button
              type="button"
              onClick={() => setMode("cookies")}
              className={`flex-1 py-2 px-3 text-xs font-medium rounded-lg flex items-center justify-center gap-2 transition-all ${
                mode === "cookies" 
                  ? "bg-brand-purple text-white" 
                  : "bg-muted text-muted-foreground hover:bg-muted/80"
              }`}
            >
              <Cookie className="w-3 h-3" /> Paste Cookies
            </button>
          </div>

          {mode === "login" ? (
            <form onSubmit={handleLoginSubmit} className="space-y-4">
              <div>
                <label className="block text-xs text-muted-foreground mb-1">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  className="w-full bg-muted border border-border rounded-lg px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs text-muted-foreground mb-1">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Your Internshala password"
                  className="w-full bg-muted border border-border rounded-lg px-3 py-2 text-sm"
                />
              </div>
              
              <div className="p-3 bg-brand-purple/10 border border-brand-purple/20 rounded-lg flex gap-3 text-xs text-brand-purple-light">
                <Shield className="w-4 h-4 shrink-0 mt-0.5" />
                <p>Your credentials are never stored. We use them only to obtain a session and then save encrypted cookies.</p>
              </div>

              <button 
                type="submit" 
                disabled={loginMut.isPending} 
                className="w-full py-2 bg-brand-purple text-white rounded-lg text-sm font-medium hover:bg-brand-purple/90 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <Globe className="w-4 h-4" /> 
                {loginMut.isPending ? "Logging in..." : "Login to " + platform}
              </button>

              {loginMut.isPending && (
                <p className="text-xs text-center text-muted-foreground">
                  A browser window opened. Log in to Internshala manually, then wait for success.
                </p>
              )}
            </form>
          ) : (
            <form onSubmit={handleCookiesSubmit} className="space-y-4">
              <div>
                <label className="block text-xs text-muted-foreground mb-1">Raw Cookie String</label>
                <textarea
                  value={cookieString}
                  onChange={(e) => setCookieString(e.target.value)}
                  placeholder="Paste your document.cookie string here..."
                  rows={4}
                  className="w-full bg-muted border border-border rounded-lg px-3 py-2 text-sm font-mono text-xs resize-none placeholder:font-sans"
                />
                <p className="text-[10px] text-muted-foreground mt-1">
                  Log into {platform}, open DevTools → Console, type <code className="bg-muted px-1 py-0.5 rounded text-foreground">document.cookie</code> and paste.
                </p>
              </div>
              
              <div className="p-3 bg-brand-purple/10 border border-brand-purple/20 rounded-lg flex gap-3 text-xs text-brand-purple-light">
                <Shield className="w-4 h-4 shrink-0 mt-0.5" />
                <p>Your cookies are encrypted in our database using AES-256 and only decrypted in memory when the automation runs.</p>
              </div>

              <button 
                type="submit" 
                disabled={!cookieString || connectMut.isPending} 
                className="w-full py-2 bg-brand-purple text-white rounded-lg text-sm font-medium hover:bg-brand-purple/90 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <Plus className="w-4 h-4" /> 
                {connectMut.isPending ? "Connecting..." : "Connect Platform"}
              </button>
            </form>
          )}
        </div>

        {/* Existing Connections */}
        <div className="glass-card p-6">
          <h2 className="font-semibold mb-4">Active Sessions</h2>
          
          {isLoading ? (
            <div className="space-y-3">{[1,2].map(i => <div key={i} className="skeleton h-20 rounded-xl" />)}</div>
          ) : platforms.length > 0 ? (
            <div className="space-y-3">
              {platforms.map((p: any) => (
                <div key={p.platform} className="p-4 bg-muted/30 border border-border/50 rounded-xl flex items-center justify-between group">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-background flex flex-col items-center justify-center border border-border">
                      <Globe className="w-4 h-4 text-muted-foreground" />
                    </div>
                    <div>
                      <p className="font-semibold text-sm capitalize flex items-center gap-2">
                        {p.platform} 
                        {p.is_valid ? (
                          <CheckCircle className="w-3 h-3 text-emerald-400" />
                        ) : (
                          <XCircle className="w-3 h-3 text-red-400" />
                        )}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {p.is_valid ? "Connected - Bot enabled" : "Session expired - Reconnect"}
                      </p>
                    </div>
                  </div>
                  <button onClick={() => invalidateMut.mutate(p.platform)} className="p-2 text-muted-foreground hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors opacity-0 group-hover:opacity-100">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-8 text-center text-muted-foreground">
              <Link2 className="w-8 h-8 opacity-50 mx-auto mb-2" />
              <p className="text-sm">No platforms connected.</p>
              <p className="text-xs mt-1">Bot execution is disabled until you connect a platform.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}