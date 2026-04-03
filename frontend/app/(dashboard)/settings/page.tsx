"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { settingsApi } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { toast } from "sonner";
import { Settings2, Bell, Shield, Key } from "lucide-react";
import { cn } from "@/lib/utils";

export default function SettingsPage() {
  const { user } = useAuth();
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("general");

  const { data: settings, isLoading } = useQuery({
    queryKey: ["settings"],
    queryFn: () => settingsApi.get().then(r => r.data),
  });

  const updateMut = useMutation({
    mutationFn: (data: any) => settingsApi.update(data),
    onSuccess: () => { toast.success("Settings updated"); qc.invalidateQueries({ queryKey: ["settings"] }); },
    onError: () => toast.error("Failed to update settings")
  });

  if (isLoading) return <div className="skeleton h-96 w-full rounded-xl" />;

  const s = settings || {};

  return (
    <div className="max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold font-display">Settings</h1>
        <p className="text-muted-foreground text-sm mt-1">Manage your platform preferences</p>
      </div>

      <div className="flex gap-6">
        {/* Sidebar */}
        <div className="w-48 shrink-0 flex flex-col gap-1">
          {[
            { id: "general", label: "General", icon: Settings2 },
            { id: "notifications", label: "Notifications", icon: Bell },
            { id: "automation", label: "Automation", icon: Settings2 },
          ].map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)}
              className={cn("flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors text-left", activeTab === t.id ? "bg-brand-purple/15 text-brand-purple-light font-medium" : "text-muted-foreground hover:bg-white/5")}>
              <t.icon className="w-4 h-4" /> {t.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 space-y-6">
          {activeTab === "general" && (
            <div className="glass-card p-6 space-y-4">
              <h2 className="font-semibold mb-4">Appearance & General</h2>
              <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
                <div>
                  <p className="font-medium text-sm">Theme</p>
                  <p className="text-xs text-muted-foreground">Applivo is currently Dark Mode only to strictly maintain its premium aesthetic.</p>
                </div>
                <div className="px-3 py-1 bg-brand-purple/20 text-brand-purple-light text-xs rounded-full cursor-not-allowed">Dark</div>
              </div>
            </div>
          )}

          {activeTab === "notifications" && (
            <div className="glass-card p-6 space-y-6">
              <h2 className="font-semibold mb-4">Notification Preferences</h2>

              <div className="space-y-4">
                <label className="flex items-center justify-between p-4 bg-muted/30 rounded-lg cursor-pointer">
                  <div>
                    <p className="font-medium text-sm">Email Notifications</p>
                    <p className="text-xs text-muted-foreground mt-0.5">Receive daily summaries and critical alerts</p>
                  </div>
                  <div className={cn("w-10 h-5 rounded-full transition-colors relative", s.notify_via_email ? "bg-brand-purple" : "bg-muted")}
                    onClick={() => updateMut.mutate({ notify_via_email: !s.notify_via_email })}>
                    <div className={cn("absolute top-0.5 w-4 h-4 bg-white rounded-full transition-all", s.notify_via_email ? "left-[22px]" : "left-0.5")} />
                  </div>
                </label>

                <label className="flex items-center justify-between p-4 bg-muted/30 rounded-lg cursor-pointer">
                  <div>
                    <p className="font-medium text-sm">Telegram Notifications</p>
                    <p className="text-xs text-muted-foreground mt-0.5">Real-time alerts for incoming jobs</p>
                  </div>
                  <div className={cn("w-10 h-5 rounded-full transition-colors relative", s.notify_via_telegram ? "bg-brand-purple" : "bg-muted")}
                    onClick={() => updateMut.mutate({ notify_via_telegram: !s.notify_via_telegram })}>
                    <div className={cn("absolute top-0.5 w-4 h-4 bg-white rounded-full transition-all", s.notify_via_telegram ? "left-[22px]" : "left-0.5")} />
                  </div>
                </label>
              </div>
            </div>
          )}

          {activeTab === "automation" && (
            <div className="glass-card p-6 space-y-6">
              <h2 className="font-semibold mb-4">Bot Settings</h2>

              <div>
                <label className="flex items-center justify-between p-4 bg-muted/30 rounded-lg cursor-pointer mb-4">
                  <div>
                    <p className="font-medium text-sm">Require Application Approval</p>
                    <p className="text-xs text-muted-foreground mt-0.5">Bot requires your review before submission</p>
                  </div>
                  <div className={cn("w-10 h-5 rounded-full transition-colors relative", s.require_apply_approval ? "bg-brand-purple" : "bg-muted")}
                    onClick={() => updateMut.mutate({ require_apply_approval: !s.require_apply_approval })}>
                    <div className={cn("absolute top-0.5 w-4 h-4 bg-white rounded-full transition-all", s.require_apply_approval ? "left-[22px]" : "left-0.5")} />
                  </div>
                </label>
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <label className="text-sm font-medium">Auto Apply Score Threshold</label>
                  <span className="text-sm font-semibold text-brand-purple-light">{s.auto_apply_threshold || 0}%</span>
                </div>
                <input type="range" min={0} max={100} value={s.auto_apply_threshold || 75}
                  onChange={(e) => updateMut.mutate({ auto_apply_threshold: +e.target.value })}
                  className="w-full h-2 bg-muted rounded-full outline-none accent-brand-purple" />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
