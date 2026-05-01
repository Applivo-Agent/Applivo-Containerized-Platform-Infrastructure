"use client";
import React, { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Shield, Key, Fingerprint, AlertTriangle, Laptop, Monitor, Smartphone, Trash2, X } from "lucide-react";
import { motion } from "framer-motion";
import { api, authApi } from "@/lib/api";
import { toast } from "sonner";

interface Session {
  id: string;
  device_name: string | null;
  device_type: string | null;
  browser: string | null;
  os: string | null;
  ip_address: string | null;
  location: string | null;
  is_current: boolean;
  is_active: boolean;
  created_at: string;
  last_used_at: string | null;
}

export default function SecurityPage() {
  const qc = useQueryClient();
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const { data: sessions = [], isLoading: sessionsLoading } = useQuery<Session[]>({
    queryKey: ["security-sessions"],
    queryFn: () => api.get("/auth/sessions").then((r) => r.data),
  });

  const revokeMutation = useMutation({
    mutationFn: (sessionId: string) => api.delete(`/auth/sessions/${sessionId}`),
    onSuccess: () => {
      toast.success("Session terminated");
      qc.invalidateQueries({ queryKey: ["security-sessions"] });
    },
    onError: () => toast.error("Failed to terminate session"),
  });

  const revokeAllMutation = useMutation({
    mutationFn: () => api.delete("/auth/sessions"),
    onSuccess: () => {
      toast.success("Signed out of other sessions");
      qc.invalidateQueries({ queryKey: ["security-sessions"] });
    },
    onError: () => toast.error("Failed to sign out other sessions"),
  });

  const changePasswordMutation = useMutation({
    mutationFn: (payload: { current_password: string; new_password: string }) =>
      authApi.changePassword(payload),
    onSuccess: () => {
      toast.success("Password updated successfully");
      setShowPasswordModal(false);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || "Failed to update password";
      toast.error(message);
    },
  });

  const getDeviceIcon = (deviceType: string | null) => {
    if (deviceType === "mobile") return <Smartphone className="w-4 h-4 text-white" />;
    if (deviceType === "desktop") return <Monitor className="w-4 h-4 text-white" />;
    return <Laptop className="w-4 h-4 text-white" />;
  };

  const getSessionTitle = (session: Session) => {
    if (session.device_name?.trim()) return session.device_name;
    const browser = session.browser?.trim();
    const os = session.os?.trim();
    if (browser && os) return `${os} - ${browser}`;
    if (browser) return browser;
    if (os) return os;
    return "Unknown Device";
  };

  const getSessionSubtitle = (session: Session) => {
    const left = session.is_current ? "Main (This session)" : "Other session";
    const right = session.location || session.ip_address || "Unknown location";
    return `${left} - ${right}`;
  };

  const hasOtherSessions = sessions.some((session) => !session.is_current);

  const handleUpdatePassword = () => {
    const trimmedCurrent = currentPassword.trim();
    const trimmedNew = newPassword.trim();
    const trimmedConfirm = confirmPassword.trim();

    if (!trimmedCurrent || !trimmedNew || !trimmedConfirm) {
      toast.error("Please fill all password fields");
      return;
    }

    if (trimmedNew.length < 8) {
      toast.error("New password must be at least 8 characters");
      return;
    }

    if (trimmedNew !== trimmedConfirm) {
      toast.error("New password and confirm password do not match");
      return;
    }

    changePasswordMutation.mutate({
      current_password: trimmedCurrent,
      new_password: trimmedNew,
    });
  };

  const handleSignOutOthers = () => {
    if (!hasOtherSessions) {
      toast.info("No other active sessions to sign out");
      return;
    }
    revokeAllMutation.mutate();
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-[#242424] border border-white/[0.08] rounded-lg">
          <Shield className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Security & Privacy</h1>
          <p className="text-sm text-zinc-400 mt-1">Manage your account security, sessions, and data privacy.</p>
        </div>
      </div>

      <div className="grid gap-4">
        {/* Password Section */}
        <div className="bg-[#1c1c1e] border border-[#262626] p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-black/20 border border-white/5">
                <Key className="w-4 h-4 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-sm text-white">Password</h3>
                <p className="text-[11px] font-bold text-zinc-500 uppercase tracking-widest">Last changed 3 months ago</p>
              </div>
            </div>
            <button
              onClick={() => setShowPasswordModal(true)}
              className="px-4 py-2 bg-white text-black rounded-lg text-[11px] font-black uppercase tracking-widest hover:bg-zinc-200 transition-all shadow-lg active:scale-95"
            >
              Update Password
            </button>
          </div>
          
          <div className="p-4 rounded-xl bg-[#17171a] border border-[#2a2a2e] flex gap-3.5 items-center">
             <AlertTriangle className="w-4 h-4 text-white/50 shrink-0" />
             <p className="text-[12px] text-zinc-400 font-medium leading-relaxed">
                Your password is currently rated as <span className="text-white font-black">Medium Strength</span>.
             </p>
          </div>
        </div>

        {/* Sessions Section */}
        <div className="bg-[#1c1c1e] border border-[#262626] p-5 rounded-2xl shadow-lg">
          <h3 className="text-sm font-bold text-white mb-5 flex items-center gap-2">
             <Fingerprint className="w-4 h-4 text-white" />
             Active Sessions
          </h3>
          {sessionsLoading ? (
            <div className="space-y-3">
              {[1, 2].map((i) => (
                <div key={i} className="h-16 rounded-xl bg-[#17171a] border border-[#2a2a2e] animate-pulse" />
              ))}
            </div>
          ) : (
            <>
              <div className="space-y-2">
                {sessions.map((session) => (
                  <div key={session.id} className="flex items-center justify-between p-3 rounded-xl bg-[#17171a] border border-[#2a2a2e]">
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="w-8 h-8 rounded-lg bg-[#202025] border border-[#303036] flex items-center justify-center shrink-0">
                        {getDeviceIcon(session.device_type)}
                      </div>
                      <div className="min-w-0">
                        <p className="text-xs font-bold text-white truncate">{getSessionTitle(session)}</p>
                        <p className="text-[11px] font-medium text-zinc-500 truncate">{getSessionSubtitle(session)}</p>
                      </div>
                    </div>

                    {session.is_current ? (
                      <span className="text-[9px] font-black text-white bg-white/10 px-2 py-0.5 rounded-md uppercase tracking-widest border border-white/10">
                        Current
                      </span>
                    ) : (
                      <button
                        onClick={() => revokeMutation.mutate(session.id)}
                        disabled={revokeMutation.isPending}
                        className="p-2 rounded-lg text-zinc-400 hover:text-white hover:bg-white/5 transition-colors"
                        title="Sign out this session"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                ))}

                {!sessions.length && (
                  <div className="p-4 rounded-xl bg-[#17171a] border border-[#2a2a2e]">
                    <p className="text-xs text-zinc-400">No active sessions found.</p>
                  </div>
                )}
              </div>

              <button
                onClick={handleSignOutOthers}
                disabled={revokeAllMutation.isPending}
                className="mt-5 text-[11px] text-zinc-400 hover:text-white hover:underline font-black uppercase tracking-widest transition-colors disabled:opacity-50 disabled:no-underline disabled:cursor-not-allowed"
              >
                {revokeAllMutation.isPending ? "Signing out..." : "Sign out of all other sessions"}
              </button>
            </>
          )}
        </div>
      </div>

      {showPasswordModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
          <div className="w-full max-w-md rounded-2xl border border-[#262626] bg-[#1c1c1e] p-5 shadow-2xl">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-sm font-bold uppercase tracking-widest text-white">Update Password</h3>
              <button
                onClick={() => setShowPasswordModal(false)}
                className="rounded-lg p-2 text-zinc-400 transition-colors hover:bg-white/5 hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <label className="mb-1 block text-[11px] font-bold uppercase tracking-widest text-zinc-500">
                  Current Password
                </label>
                <input
                  type="password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  className="w-full rounded-xl border border-[#303036] bg-[#17171a] px-3 py-2 text-sm text-white outline-none focus:border-white/30"
                />
              </div>

              <div>
                <label className="mb-1 block text-[11px] font-bold uppercase tracking-widest text-zinc-500">
                  New Password
                </label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full rounded-xl border border-[#303036] bg-[#17171a] px-3 py-2 text-sm text-white outline-none focus:border-white/30"
                />
              </div>

              <div>
                <label className="mb-1 block text-[11px] font-bold uppercase tracking-widest text-zinc-500">
                  Confirm New Password
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full rounded-xl border border-[#303036] bg-[#17171a] px-3 py-2 text-sm text-white outline-none focus:border-white/30"
                />
              </div>
            </div>

            <div className="mt-5 flex justify-end gap-2">
              <button
                onClick={() => setShowPasswordModal(false)}
                className="rounded-lg px-4 py-2 text-xs font-bold uppercase tracking-widest text-zinc-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={handleUpdatePassword}
                disabled={changePasswordMutation.isPending}
                className="rounded-lg bg-white px-4 py-2 text-xs font-black uppercase tracking-widest text-black hover:bg-zinc-200 disabled:opacity-60"
              >
                {changePasswordMutation.isPending ? "Updating..." : "Update"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
