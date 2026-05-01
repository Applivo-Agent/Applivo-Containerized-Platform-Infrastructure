"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { settingsApi, schedulerApi } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { toast } from "sonner";
import { Settings2, Bell, Shield, Key, Zap, Clock, Play, Pause, RefreshCw , Loader2} from "lucide-react";
import { cn } from "@/lib/utils";

export default function SettingsPage() {
  const { user } = useAuth();
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("general");

  const { data: settings, isLoading } = useQuery({
    queryKey: ["settings"],
    queryFn: () => settingsApi.get().then(r => r.data),
  });

  const { data: schedulerJobs, isLoading: jobsLoading } = useQuery({
    queryKey: ["scheduler-jobs"],
    queryFn: async () => {
      const result = await schedulerApi.listJobs();
      return result.data;
    },
    refetchInterval: 30000,
  });

  const updateMut = useMutation({
    mutationFn: (data: any) => settingsApi.update(data),
    onSuccess: () => { toast.success("Settings updated"); qc.invalidateQueries({ queryKey: ["settings"] }); },
    onError: () => toast.error("Failed to update settings")
  });

  const toggleScrapeMut = useMutation({
    mutationFn: async (enabled: boolean) => {
      return schedulerApi.toggleJob("auto_scrape", enabled);
    },
    onSuccess: () => { 
      toast.success("Scrape job updated"); 
      qc.invalidateQueries({ queryKey: ["scheduler-jobs"] }); 
    },
    onError: (err: any) => { 
      toast.error("Failed to update scrape job: " + (err?.response?.data?.detail || err?.message || "Unknown error"))
    }
  });

  const toggleApplyMut = useMutation({
    mutationFn: async (enabled: boolean) => {
      return schedulerApi.toggleJob("auto_apply_check", enabled);
    },
    onSuccess: () => { 
      toast.success("Auto-apply updated"); 
      qc.invalidateQueries({ queryKey: ["scheduler-jobs"] }); 
    },
    onError: (err: any) => { 
      toast.error("Failed to update apply job: " + (err?.response?.data?.detail || err?.message || "Unknown error"))
    }
  });

  const triggerScrapeMut = useMutation({
    mutationFn: async () => {
      return schedulerApi.runJobNow("auto_scrape");
    },
    onSuccess: () => toast.success("Scrape job triggered!"),
    onError: (err: any) => { 
      toast.error("Failed to trigger scrape: " + (err?.response?.data?.detail || err?.message || "Unknown error"))
    }
  });

  if (isLoading) return <div className="h-96 w-full bg-[#111118] border border-[#1C1C24] animate-pulse rounded-2xl" />;

  const s = settings || {};
  const jobs = schedulerJobs?.jobs || [];
  const scrapeJob = jobs.find((j: any) => j.id === "auto_scrape");
  const applyJob = jobs.find((j: any) => j.id === "auto_apply_check");
  const isScrapePaused = !scrapeJob?.next_run;
  const isApplyPaused = !applyJob?.next_run;

  return (
    <div className="max-w-4xl space-y-6">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-[#242424] border border-white/[0.08] rounded-lg">
          <Settings2 className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Settings</h1>
          <p className="text-sm text-zinc-400 mt-1">Manage your platform preferences</p>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-8">
        {/* Sidebar */}
        <div className="w-full md:w-56 shrink-0 flex flex-col gap-1.5">
          {[
            { id: "general", label: "General", icon: Settings2 },
            { id: "notifications", label: "Notifications", icon: Bell },
            { id: "automation", label: "Automation", icon: Settings2 },
          ].map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)}
              className={cn("flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm transition-all border text-left", 
                activeTab === t.id 
                  ? "bg-white text-black border-transparent font-medium shadow-lg" 
                  : "text-[#A1A1AA] border-transparent hover:bg-[#111118] hover:text-white"
              )}>
              <t.icon className="w-4 h-4" /> {t.label}
            </button>
          ))}
        </div>

        {/* Content Area */}
        <div className="flex-1 space-y-6">
          {activeTab === "general" && (
            <div className="bg-[#1c1c1e] border border-[#262626] rounded-2xl shadow-lg p-6 space-y-6">
              <h2 className="font-semibold text-white">Appearance & General</h2>
              <div className="flex items-center justify-between p-4 bg-[#161616] border border-zinc-800 rounded-xl">
                <div>
                  <p className="font-medium text-sm text-white">Theme</p>
                  <p className="text-xs text-[#A1A1AA] mt-0.5">Applivo is currently Dark Mode only to strictly maintain its premium aesthetic.</p>
                </div>
                <div className="px-4 py-1.5 bg-white text-black text-xs font-bold rounded-full cursor-not-allowed uppercase shadow-lg">Dark</div>
              </div>
            </div>
          )}

          {activeTab === "notifications" && (
            <div className="bg-[#1c1c1e] border border-[#262626] rounded-2xl shadow-lg p-6 space-y-6">
              <h2 className="font-semibold text-white">Notification Preferences</h2>

              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-[#161616] border border-zinc-800 rounded-xl group transition-all">
                  <div>
                    <p className="font-medium text-sm text-white">Email Notifications</p>
                    <p className="text-xs text-[#A1A1AA] mt-0.5">Receive daily summaries and critical alerts</p>
                  </div>
                  <div className={cn("w-12 h-6 rounded-full transition-all relative cursor-pointer border-2 shadow-inner", 
                    s.notify_via_email ? "bg-white border-white" : "bg-[#161616] border-zinc-800")}
                    onClick={() => updateMut.mutate({ notify_via_email: !s.notify_via_email })}>
                    <div className={cn("absolute top-0.5 w-4 h-4 rounded-full transition-all shadow-md", 
                      s.notify_via_email ? "left-6 bg-[#0B0B0F]" : "left-0.5 bg-[#A1A1AA]")} />
                  </div>
                </div>

                <div className="flex items-center justify-between p-4 bg-[#161616] border border-zinc-800 rounded-xl group transition-all">
                  <div>
                    <p className="font-medium text-sm text-white">Telegram Notifications</p>
                    <p className="text-xs text-[#A1A1AA] mt-0.5">Real-time alerts for incoming jobs</p>
                  </div>
                  <div className={cn("w-12 h-6 rounded-full transition-all relative cursor-pointer border-2 shadow-inner", 
                    s.notify_via_telegram ? "bg-white border-white" : "bg-[#161616] border-zinc-800")}
                    onClick={() => updateMut.mutate({ notify_via_telegram: !s.notify_via_telegram })}>
                    <div className={cn("absolute top-0.5 w-4 h-4 rounded-full transition-all shadow-md", 
                      s.notify_via_telegram ? "left-6 bg-[#0B0B0F]" : "left-0.5 bg-[#A1A1AA]")} />
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "automation" && (
            <div className="bg-[#1c1c1e] border border-[#262626] rounded-2xl shadow-lg p-6 space-y-6">
              <h2 className="font-semibold text-white">Automation Settings</h2>

              {/* Auto-Scrape */}
              <div className="p-4 bg-[#161616] border border-zinc-800 rounded-xl space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-[#1c1c1e] border border-zinc-800 flex items-center justify-center">
                      <RefreshCw className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="font-medium text-sm text-white">Auto-Scrape Jobs</p>
                      <p className="text-xs text-[#A1A1AA]">Automatically scrape new jobs every 6 hours</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {isScrapePaused ? (
                      <button onClick={() => toggleScrapeMut.mutate(true)} disabled={toggleScrapeMut.isPending}
                        className="p-2 rounded-lg bg-[#1c1c1e] border border-zinc-800 hover:bg-emerald-500/10 text-[#A1A1AA] hover:text-emerald-500 transition-all"
                        title="Resume schedule"
                      >
                        <Play className="w-4 h-4" />
                      </button>
                    ) : (
                      <button onClick={() => toggleScrapeMut.mutate(false)} disabled={toggleScrapeMut.isPending}
                        className="p-2 rounded-lg bg-[#1c1c1e] border border-zinc-800 hover:bg-red-500/10 text-[#A1A1AA] hover:text-red-500 transition-all"
                        title="Pause schedule"
                      >
                        <Pause className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <button onClick={() => triggerScrapeMut.mutate()} disabled={triggerScrapeMut.isPending}
                    className="text-xs px-4 py-2 bg-white text-black font-bold rounded-lg hover:bg-gray-200 transition-all shadow-lg">
                    Run Now
                  </button>
                  <span className="text-xs text-[#A1A1AA] font-mono">Next: {scrapeJob?.next_run || "N/A"}</span>
                </div>
              </div>

              {/* Auto-Apply */}
              <div className="p-4 bg-[#161616] border border-zinc-800 rounded-xl space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-[#1c1c1e] border border-zinc-800 flex items-center justify-center">
                      <Zap className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="font-medium text-sm text-white">Auto-Apply</p>
                      <p className="text-xs text-[#A1A1AA]">Automatically apply to queued jobs hourly</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {isApplyPaused ? (
                      <button onClick={() => toggleApplyMut.mutate(true)} disabled={toggleApplyMut.isPending}
                        className="p-2 rounded-lg bg-[#1c1c1e] border border-zinc-800 hover:bg-emerald-500/10 text-[#A1A1AA] hover:text-emerald-500 transition-all"
                        title="Resume schedule"
                      >
                        <Play className="w-4 h-4" />
                      </button>
                    ) : (
                      <button onClick={() => toggleApplyMut.mutate(false)} disabled={toggleApplyMut.isPending}
                        className="p-2 rounded-lg bg-[#1c1c1e] border border-zinc-800 hover:bg-red-500/10 text-[#A1A1AA] hover:text-red-500 transition-all"
                        title="Pause schedule"
                      >
                        <Pause className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-[#A1A1AA] font-mono">Next: {applyJob?.next_run || "N/A"}</span>
                </div>
              </div>

              {/* Approval Settings */}
              <div className="flex items-center justify-between p-4 bg-[#161616] border border-zinc-800 rounded-xl">
                <div>
                  <p className="font-medium text-sm text-white">Require Application Approval</p>
                  <p className="text-xs text-[#A1A1AA] mt-0.5">Bot requires your review before submission</p>
                </div>
                <div className={cn("w-12 h-6 rounded-full transition-all relative cursor-pointer border-2 shadow-inner", 
                  s.require_apply_approval ? "bg-white border-white" : "bg-[#161616] border-zinc-800")}
                  onClick={() => updateMut.mutate({ require_apply_approval: !s.require_apply_approval })}>
                  <div className={cn("absolute top-0.5 w-4 h-4 rounded-full transition-all shadow-md", 
                    s.require_apply_approval ? "left-6 bg-[#0B0B0F]" : "left-0.5 bg-[#A1A1AA]")} />
                </div>
              </div>

              <div className="p-4 bg-[#161616] border border-zinc-800 rounded-xl">
                <div className="flex justify-between mb-3">
                  <label className="text-sm font-medium text-white">Auto Apply Score Threshold</label>
                  <span className="text-sm font-bold text-white bg-[#1c1c1e] border border-zinc-800 px-2 py-0.5 rounded-lg">{s.auto_apply_threshold || 0}%</span>
                </div>
                <input type="range" min={0} max={100} value={s.auto_apply_threshold ?? 75}
                  onChange={(e) => updateMut.mutate({ auto_apply_threshold: +e.target.value })}
                  className="w-full h-2 bg-[#1c1c1e] rounded-full outline-none accent-white cursor-pointer" />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
