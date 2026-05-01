"use client";
import React from "react";
import { Star, Video, Play, Calendar, User, Zap, Sparkles, CheckCircle2 , Loader2} from "lucide-react";
import { motion } from "framer-motion";

export default function InterviewsPage() {
  return (
      <div className="dash-page max-w-6xl space-y-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-[#242424] border border-white/[0.08] rounded-lg">
              <Star className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Interview Preparation</h1>
              <p className="text-sm text-zinc-400 mt-1">Simulated AI interviews and real-time prep for your upcoming rounds.</p>
            </div>
          </div>

       <div className="grid lg:grid-cols-2 gap-6">
               <div className="dash-card p-5 relative overflow-hidden group">
             <div className="relative z-10">
                <Sparkles className="w-7 h-7 text-white mb-4" />
                <h2 className="text-lg font-bold mb-3">AI Mock Interview</h2>
                <p className="text-zinc-400 mb-6 text-[13px] leading-relaxed max-w-sm">
                  Our AI agent roleplays as a hiring manager. Practice technical or behavioral questions in a low-pressure environment.
                </p>
                <div className="flex items-center gap-3">
                   <button className="px-4 py-2 bg-white text-black rounded-lg text-sm font-bold hover:bg-gray-200 transition-all flex items-center gap-2">
                     <Play className="w-4 h-4 fill-black" />
                     Start Mock Session
                   </button>
                   <button className="px-4 py-2 bg-[#161616] border border-zinc-800 text-white rounded-lg text-sm font-bold hover:bg-white/5 transition-all">
                     Configure Agent
                   </button>
                </div>
             </div>
          </div>

          <div className="dash-card p-5 relative overflow-hidden group">
             <div className="relative z-10">
                <Calendar className="w-7 h-7 text-white mb-4" />
                <h2 className="text-lg font-bold mb-3">Upcoming Rounds</h2>
                <p className="text-zinc-400 mb-6 text-[13px] leading-relaxed max-w-sm">
                  Track your scheduled interviews and get automated prep sheets for each company.
                </p>
                <div className="space-y-2">
                   <div className="flex items-center justify-between p-3 rounded-xl bg-[#161616] border border-zinc-800 text-[11px]">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-[#1c1c1e] border border-white/10 flex items-center justify-center text-white font-bold">R1</div>
                        <div>
                          <p className="font-bold text-white">Google — ML System Design</p>
                          <p className="text-zinc-500">Tomorrow, 10:00 AM</p>
                        </div>
                      </div>
                      <button className="text-white hover:underline font-bold uppercase tracking-wider text-[10px]">Prep Pack</button>
                   </div>
                </div>
             </div>
          </div>
       </div>

      <div className="dash-card p-4">
          <h3 className="text-sm font-bold mb-5 flex items-center gap-2">
             <Zap className="w-4 h-4 text-white" />
             AI Performance Insights
          </h3>
          <div className="grid md:grid-cols-3 gap-4">
              <div className="p-4 rounded-xl bg-[#161616] border border-zinc-800">
                <p className="text-[11px] font-bold uppercase tracking-widest text-zinc-500 mb-1">Clarity Score</p>
                <div className="text-[22px] font-black text-white">84/100</div>
                <div className="w-full h-1 bg-white/5 rounded-full mt-3 overflow-hidden">
                   <div className="h-full bg-white shadow-[0_0_8px_rgba(255,255,255,0.5)]" style={{ width: '84%' }} />
                </div>
             </div>
             <div className="p-4 rounded-xl bg-[#161616] border border-zinc-800">
                <p className="text-[11px] font-bold uppercase tracking-widest text-zinc-500 mb-1">Technical Accuracy</p>
                <div className="text-[22px] font-black text-white">92/100</div>
                <div className="w-full h-1 bg-white/5 rounded-full mt-3 overflow-hidden">
                   <div className="h-full bg-white shadow-[0_0_8px_rgba(255,255,255,0.5)]" style={{ width: '92%' }} />
                </div>
             </div>
             <div className="p-4 rounded-xl bg-[#161616] border border-zinc-800">
                <p className="text-[11px] font-bold uppercase tracking-widest text-zinc-500 mb-1">Confidence Rating</p>
                <div className="text-[22px] font-black text-white">76/100</div>
                <div className="w-full h-1 bg-white/5 rounded-full mt-3 overflow-hidden">
                   <div className="h-full bg-white shadow-[0_0_8px_rgba(255,255,255,0.5)]" style={{ width: '76%' }} />
                </div>
             </div>
          </div>
       </div>
    </div>
  );
}
