"use client";
import React from "react";
import { Star, Video, Play, Calendar, User, Zap, Sparkles, CheckCircle2 } from "lucide-react";
import { motion } from "framer-motion";

export default function InterviewsPage() {
  return (
    <div className="space-y-8 max-w-6xl">
       <div>
        <h1 className="text-3xl font-bold font-display flex items-center gap-3">
          <Star className="w-8 h-8 text-amber-500" />
          Interview Preparation
        </h1>
        <p className="text-muted-foreground mt-1 text-lg">
          Simulated AI interviews and real-time prep for your upcoming rounds.
        </p>
      </div>

       <div className="grid lg:grid-cols-2 gap-8">
          <div className="glass-card p-10 bg-gradient-to-br from-brand-purple/15 to-transparent relative overflow-hidden group">
             <div className="relative z-10">
                <Sparkles className="w-10 h-10 text-brand-purple-light mb-6" />
                <h2 className="text-2xl font-bold mb-4">AI Mock Interview</h2>
                <p className="text-muted-foreground mb-8 text-sm leading-relaxed max-w-sm">
                  Our AI agent roleplays as a hiring manager. Practice technical or behavioral questions in a low-pressure environment.
                </p>
                <div className="flex items-center gap-4">
                   <button className="px-6 py-3 bg-brand-purple text-white rounded-xl font-bold hover:shadow-xl hover:shadow-brand-purple/40 transition-all flex items-center gap-2">
                     <Play className="w-4 h-4 fill-white" />
                     Start Mock Session
                   </button>
                   <button className="px-6 py-3 bg-white/5 border border-border rounded-xl font-bold hover:bg-white/10 transition-all">
                     Configure Agent
                   </button>
                </div>
             </div>
             <div className="absolute -bottom-6 -right-6 w-48 h-48 bg-brand-purple/20 blur-3xl rounded-full" />
          </div>

          <div className="glass-card p-10 bg-gradient-to-br from-amber-500/10 to-transparent relative overflow-hidden group border-amber-500/20">
             <div className="relative z-10">
                <Calendar className="w-10 h-10 text-amber-400 mb-6" />
                <h2 className="text-2xl font-bold mb-4">Upcoming Rounds</h2>
                <p className="text-muted-foreground mb-8 text-sm leading-relaxed max-w-sm">
                  Track your scheduled interviews and get automated prep sheets for each company.
                </p>
                <div className="space-y-3">
                   <div className="flex items-center justify-between p-3 rounded-lg bg-zinc-900 border border-border text-xs">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400 font-bold">R1</div>
                        <div>
                          <p className="font-semibold">Google — ML System Design</p>
                          <p className="text-muted-foreground">Tomorrow, 10:00 AM</p>
                        </div>
                      </div>
                      <button className="text-amber-400 hover:underline">Prep Pack</button>
                   </div>
                </div>
             </div>
          </div>
       </div>

       <div className="glass-card p-6">
          <h3 className="font-bold mb-6 flex items-center gap-2">
             <Zap className="w-4 h-4 text-violet-400" />
             AI Performance Insights
          </h3>
          <div className="grid md:grid-cols-3 gap-6">
             <div className="p-4 rounded-xl bg-white/5 border border-border">
                <p className="text-[10px] uppercase tracking-widest text-muted-foreground mb-1">Clarity Score</p>
                <div className="text-2xl font-black text-brand-purple-light">84/100</div>
                <div className="w-full h-1 bg-muted rounded-full mt-3 overflow-hidden">
                   <div className="h-full bg-brand-purple-light" style={{ width: '84%' }} />
                </div>
             </div>
             <div className="p-4 rounded-xl bg-white/5 border border-border">
                <p className="text-[10px] uppercase tracking-widest text-muted-foreground mb-1">Technical Accuracy</p>
                <div className="text-2xl font-black text-emerald-400">92/100</div>
                <div className="w-full h-1 bg-muted rounded-full mt-3 overflow-hidden">
                   <div className="h-full bg-emerald-400" style={{ width: '92%' }} />
                </div>
             </div>
             <div className="p-4 rounded-xl bg-white/5 border border-border">
                <p className="text-[10px] uppercase tracking-widest text-muted-foreground mb-1">Confidence Rating</p>
                <div className="text-2xl font-black text-amber-400">76/100</div>
                <div className="w-full h-1 bg-muted rounded-full mt-3 overflow-hidden">
                   <div className="h-full bg-amber-400" style={{ width: '76%' }} />
                </div>
             </div>
          </div>
       </div>
    </div>
  );
}
