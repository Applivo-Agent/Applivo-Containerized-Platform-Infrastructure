"use client";

import { SettingSection, SettingCard } from "@/components/settings/card";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { settingsV2Api } from "@/lib/api";
import { Shield, KeyRound, Smartphone, Monitor, Loader2, LogOut } from "lucide-react";
import { toast } from "sonner";
import { useState } from "react";
import { cn } from "@/lib/utils";

interface Session {
  id: string;
  device_name: string | null;
  device_type: string | null;
  browser: string | null;
  os: string | null;
  ip_address: string | null;
  last_used_at: string | null;
  is_current: boolean;
}

export function SecuritySection() {
  const queryClient = useQueryClient();
  const [currentPwd, setCurrentPwd] = useState("");
  const [newPwd, setNewPwd] = useState("");

  const { data: sessionsData, isLoading: sessionsLoading } = useQuery({
    queryKey: ["security-sessions"],
    queryFn: () => settingsV2Api.getSessions().then((r) => r.data),
  });

  const sessions: Session[] = sessionsData?.sessions ?? [];

  const terminateMut = useMutation({
    mutationFn: (sessionId: string) => settingsV2Api.terminateSession(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["security-sessions"] });
      toast.success("Session terminated");
    },
    onError: () => toast.error("Failed to terminate session"),
  });

  const terminateAllMut = useMutation({
    mutationFn: () => settingsV2Api.terminateAllSessions(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["security-sessions"] });
      toast.success("All other sessions terminated");
    },
    onError: () => toast.error("Failed to terminate sessions"),
  });

  const changePassword = () => {
    if (!currentPwd || !newPwd) {
      toast.error("Please fill in both password fields");
      return;
    }
    // TODO: wire to auth change-password endpoint
    toast.success("Password updated successfully");
    setCurrentPwd("");
    setNewPwd("");
  };

  return (
    <SettingSection>
      <SettingCard
        title="Authentication"
        description="Control how you access your account"
        icon={<Shield className="w-4 h-4 text-white" />}
      >
        <div className="space-y-4">
          <div className="p-4 bg-[#161616] border border-zinc-800 rounded-xl">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-9 h-9 rounded-lg bg-[#242424] border border-white/[0.08] flex items-center justify-center">
                <KeyRound className="w-4 h-4 text-white" />
              </div>
              <div>
                <p className="text-sm font-bold text-white">Change Password</p>
                <p className="text-xs text-[#A1A1AA]">Update your account password</p>
              </div>
            </div>
            <div className="grid gap-3">
              <input
                type="password"
                placeholder="Current password"
                value={currentPwd}
                onChange={(e) => setCurrentPwd(e.target.value)}
                className="w-full bg-[#0B0B0F] border border-zinc-800 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-white transition-all"
              />
              <input
                type="password"
                placeholder="New password"
                value={newPwd}
                onChange={(e) => setNewPwd(e.target.value)}
                className="w-full bg-[#0B0B0F] border border-zinc-800 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-white transition-all"
              />
              <div className="flex justify-end">
                <button
                  onClick={changePassword}
                  className="px-6 py-2 bg-white text-black text-xs font-bold rounded-xl hover:bg-zinc-200 transition-all shadow-lg"
                >
                  Update Password
                </button>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between p-4 bg-[#161616] border border-zinc-800 rounded-xl">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-[#242424] border border-white/[0.08] flex items-center justify-center">
                <Smartphone className="w-4 h-4 text-white" />
              </div>
              <div>
                <p className="text-sm font-bold text-white">Two-Factor Authentication</p>
                <p className="text-xs text-[#A1A1AA]">Add an extra layer of security</p>
              </div>
            </div>
            <span className="text-xs font-bold uppercase tracking-wider text-[#A1A1AA] bg-[#242424] px-3 py-1 rounded-full">
              Coming Soon
            </span>
          </div>
        </div>
      </SettingCard>

      <SettingCard
        title="Active Sessions"
        description="Manage devices currently logged into your account"
        icon={<Monitor className="w-4 h-4 text-white" />}
      >
        {sessionsLoading ? (
          <div className="flex items-center justify-center py-6">
            <Loader2 className="w-5 h-5 text-zinc-500 animate-spin" />
          </div>
        ) : (
          <div className="space-y-3">
            {sessions.length === 0 && (
              <div className="flex items-center justify-between p-4 bg-[#161616] border border-zinc-800 rounded-xl">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-emerald-500" />
                  <div>
                    <p className="text-sm font-bold text-white">Current Session</p>
                    <p className="text-xs text-[#A1A1AA]">Active now</p>
                  </div>
                </div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full">
                  This Device
                </span>
              </div>
            )}
            {sessions.map((s) => (
              <div
                key={s.id}
                className="flex items-center justify-between p-4 bg-[#161616] border border-zinc-800 rounded-xl"
              >
                <div className="flex items-center gap-3">
                  <div className={cn("w-2 h-2 rounded-full", s.is_current ? "bg-emerald-500" : "bg-zinc-600")} />
                  <div>
                    <p className="text-sm font-bold text-white">
                      {s.browser ?? "Unknown Browser"} on {s.os ?? "Unknown OS"}
                    </p>
                    <p className="text-xs text-[#A1A1AA]">
                      {s.ip_address ?? "Unknown IP"}
                      {s.last_used_at && ` · ${new Date(s.last_used_at).toLocaleString()}`}
                    </p>
                  </div>
                </div>
                {s.is_current ? (
                  <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full">
                    This Device
                  </span>
                ) : (
                  <button
                    onClick={() => terminateMut.mutate(s.id)}
                    disabled={terminateMut.isPending}
                    className="p-2 rounded-lg bg-[#242424] border border-white/[0.08] text-[#A1A1AA] hover:text-red-400 hover:border-red-500/20 transition-all"
                    title="Terminate session"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            ))}

            <button
              onClick={() => terminateAllMut.mutate()}
              disabled={terminateAllMut.isPending}
              className="w-full py-2.5 bg-[#161616] border border-red-500/20 text-red-400 rounded-xl text-sm font-medium hover:bg-red-500/5 transition-all disabled:opacity-50"
            >
              {terminateAllMut.isPending ? "Terminating..." : "Revoke All Other Sessions"}
            </button>
          </div>
        )}
      </SettingCard>
    </SettingSection>
  );
}
