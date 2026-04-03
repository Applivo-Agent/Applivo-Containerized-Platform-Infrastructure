"use client";
import React from "react";
import { Shield, Lock, Key, Eye, EyeOff, ShieldCheck, Fingerprint, AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";

export default function SecurityPage() {
  return (
    <div className="space-y-8 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold font-display flex items-center gap-3">
          <Shield className="w-8 h-8 text-brand-purple-light" />
          Security & Privacy
        </h1>
        <p className="text-muted-foreground mt-1 text-lg">
          Manage your account security, sessions, and data privacy.
        </p>
      </div>

      <div className="grid gap-6">
        {/* Password Section */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-zinc-900 border border-border">
                <Key className="w-5 h-5 text-amber-400" />
              </div>
              <div>
                <h3 className="font-bold">Password</h3>
                <p className="text-xs text-muted-foreground">Last changed 3 months ago</p>
              </div>
            </div>
            <button className="px-4 py-2 bg-white/5 border border-border rounded-lg text-sm font-medium hover:bg-white/10 transition-colors">
              Update Password
            </button>
          </div>
          
          <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20 flex gap-4">
             <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0" />
             <p className="text-xs text-amber-200/70 leading-relaxed">
                Your password is currently rated as <span className="text-amber-400 font-bold">Medium Strength</span>. We recommend using a mix of symbols and numbers for better security.
             </p>
          </div>
        </div>

        {/* 2FA Section */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-zinc-900 border border-border">
                <Fingerprint className="w-5 h-5 text-emerald-400" />
              </div>
              <div>
                <h3 className="font-bold">Two-Factor Authentication</h3>
                <p className="text-xs text-muted-foreground">Add an extra layer of security to your account.</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
               <span className="text-xs text-muted-foreground mr-2 font-medium">Disabled</span>
               <button className="w-10 h-5 rounded-full bg-zinc-800 border border-border relative transition-colors">
                  <div className="absolute left-0.5 top-0.5 w-3.5 h-3.5 rounded-full bg-zinc-600" />
               </button>
            </div>
          </div>
        </div>

        {/* Sessions Section */}
        <div className="glass-card p-6">
          <h3 className="font-bold mb-6 flex items-center gap-2">
             <ShieldCheck className="w-5 h-5 text-brand-purple-light" />
             Active Sessions
          </h3>
          <div className="space-y-4">
             <div className="flex items-center justify-between py-3 border-b border-border last:border-0">
                <div className="flex items-center gap-4">
                   <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_#10b981]" />
                   <div>
                      <p className="text-sm font-medium">MacBook Air — Chrome</p>
                      <p className="text-xs text-muted-foreground">Main (This session) • Mumbai, India</p>
                   </div>
                </div>
                <span className="text-xs font-bold text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded">Current</span>
             </div>
          </div>
          <button className="mt-6 text-sm text-red-400 hover:underline font-medium">
             Sign out of all other sessions
          </button>
        </div>
      </div>
    </div>
  );
}
