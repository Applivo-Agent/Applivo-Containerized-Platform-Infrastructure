"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { platformApi } from "@/lib/api";
import { toast } from "sonner";
import { Link2, Trash2, Plus, Shield, Globe, Lock } from "lucide-react";
import { formatDate } from "@/lib/utils";

export default function ConnectPage() {
  const qc = useQueryClient();
  const [platform, setPlatform] = useState("internshala");
  const [cookieString, setCookieString] = useState("");

  const { data: cookies, isLoading } = useQuery({
    queryKey: ["cookies"],
    queryFn: () => platformApi.cookies().then((r) => r.data),
  });

  const addMut = useMutation({
    mutationFn: () => platformApi.addCookie({ platform, cookie_string: cookieString }),
    onSuccess: () => { toast.success("Cookies saved & encrypted"); setCookieString(""); qc.invalidateQueries({ queryKey: ["cookies"] }); },
    onError: () => toast.error("Failed to save cookies"),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => platformApi.deleteCookie(id),
    onSuccess: () => { toast.success("Cookies deleted"); qc.invalidateQueries({ queryKey: ["cookies"] }); },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!cookieString) return;
    addMut.mutate();
  };

  return (
    <div className="max-w-4xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold font-display">Connected Platforms</h1>
        <p className="text-muted-foreground text-sm mt-1">Connect job boards by providing your session cookies. These are encrypted at rest.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Connection Form */}
        <div className="glass-card p-6">
          <h2 className="font-semibold mb-4 flex items-center gap-2"><Link2 className="w-5 h-5 text-brand-purple-light" /> Add Connection</h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs text-muted-foreground mb-1">Platform</label>
              <select value={platform} onChange={(e) => setPlatform(e.target.value)} className="w-full bg-muted border border-border rounded-lg px-3 py-2 text-sm">
                <option value="internshala">Internshala</option>
                <option value="linkedin">LinkedIn (Coming Soon)</option>
                <option value="indeed">Indeed (Coming Soon)</option>
              </select>
            </div>
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
                Log into {platform}, open DevTools → Console, type <code className="bg-muted px-1 py-0.5 rounded text-foreground">document.cookie</code> and paste the output.
              </p>
            </div>
            
            <div className="p-3 bg-brand-purple/10 border border-brand-purple/20 rounded-lg flex gap-3 text-xs text-brand-purple-light">
              <Shield className="w-4 h-4 shrink-0 mt-0.5" />
              <p>Your cookies are encrypted in our database using AES-256 and are only decrypted in memory just-in-time when the Playwright agent runs.</p>
            </div>

            <button type="submit" disabled={!cookieString || addMut.isPending} className="w-full py-2 bg-brand-purple text-white rounded-lg text-sm font-medium hover:bg-brand-purple/90 transition-all disabled:opacity-50 flex items-center justify-center gap-2">
              <Plus className="w-4 h-4" /> Connect Platform
            </button>
          </form>
        </div>

        {/* Existing Connections */}
        <div className="glass-card p-6">
          <h2 className="font-semibold mb-4">Active Sessions</h2>
          
          {isLoading ? (
            <div className="space-y-3">{[1,2].map(i => <div key={i} className="skeleton h-20 rounded-xl" />)}</div>
          ) : (
            <div className="space-y-3">
              {cookies?.map((c: any) => (
                <div key={c.id} className="p-4 bg-muted/30 border border-border/50 rounded-xl flex items-center justify-between group">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-background flex flex-col items-center justify-center border border-border">
                      <Globe className="w-4 h-4 text-muted-foreground" />
                    </div>
                    <div>
                      <p className="font-semibold text-sm capitalize flex items-center gap-2">
                        {c.platform} <Lock className="w-3 h-3 text-emerald-400" />
                      </p>
                      <p className="text-xs text-muted-foreground">Connected {formatDate(c.created_at)}</p>
                    </div>
                  </div>
                  <button onClick={() => deleteMut.mutate(c.id)} className="p-2 text-muted-foreground hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors opacity-0 group-hover:opacity-100">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
              {cookies?.length === 0 && (
                <div className="py-8 text-center text-muted-foreground">
                  <Link2 className="w-8 h-8 opacity-50 mx-auto mb-2" />
                  <p className="text-sm">No platforms connected.</p>
                  <p className="text-xs mt-1">Bot execution is disabled until you connect a platform.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
