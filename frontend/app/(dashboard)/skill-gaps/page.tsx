"use client";
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/lib/api";
import { Target, BookOpen, ExternalLink, Zap, Lock, Sparkles, TrendingUp , Loader2} from "lucide-react";
import { motion } from "framer-motion";

export default function SkillGapsPage() {
  const { data: skillGaps, isLoading } = useQuery({
    queryKey: ["skill-gaps"],
    queryFn: () => analyticsApi.skillGaps().then(r => r.data),
  });
  
  const skills: Array<{ name: string; gap: string; priority: string }> = (skillGaps || []) as any;
  return (
      <div className="dash-page max-w-6xl space-y-6">
         <div className="flex items-center gap-3">
            <div className="p-2 bg-[#242424] border border-white/[0.08] rounded-lg">
              <Target className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Skill Gap Analysis</h1>
              <p className="text-sm text-zinc-400 mt-1">AI comparison between your profile and target job roles.</p>
            </div>
          </div>

       <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
             <div className="dash-card p-4">
                <div className="flex items-center justify-between mb-6">
                   <h3 className="text-lg font-bold text-white">Target Role: Senior Platform Engineer</h3>
                   <div className="px-3 py-1 bg-white/5 border border-white/10 text-white rounded-full text-[11px] font-bold">
                      Overall Match: 76.5%
                   </div>
                </div>
                
                <div className="space-y-3">
                   {skills.map((s) => (
                      <div key={s.name} className="p-4 rounded-xl bg-[#161616] border border-zinc-800 group hover:border-white/20 transition-all">
                         <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                               <div className="p-2 rounded-lg bg-[#161616] border border-zinc-800 text-white">
                                  <TrendingUp className="w-4 h-4" />
                               </div>
                               <div>
                                  <h4 className="font-bold text-sm tracking-wide text-white">{s.name}</h4>
                                  <p className="text-[10px] text-zinc-500 uppercase tracking-widest">{s.gap} Gap — {s.priority}</p>
                               </div>
                            </div>
                            <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white text-black text-[10px] font-bold hover:bg-gray-200 transition-all uppercase tracking-widest">
                               Learn <ExternalLink className="w-3 h-3" />
                            </button>
                         </div>
                      </div>
                   ))}
                </div>
             </div>
          </div>

          <div className="space-y-6">
             <div className="dash-card p-4">
                <h3 className="text-sm font-bold mb-4 flex items-center gap-2">
                   <Sparkles className="w-4 h-4 text-white" />
                   AI Career Roadmap
                </h3>
                <div className="space-y-4">
                   <div className="relative pl-6 pb-6 border-l border-zinc-800">
                      <div className="absolute top-0 left-[-5px] w-2.5 h-2.5 rounded-full bg-white shadow-[0_0_8px_#fff]" />
                      <p className="text-[11px] font-bold">Certification: CKA</p>
                      <p className="text-[10px] text-zinc-500">Est: 3 Weeks</p>
                   </div>
                   <div className="relative pl-6 pb-6 border-l border-zinc-800">
                      <div className="absolute top-0 left-[-5px] w-2.5 h-2.5 rounded-full bg-white/40" />
                      <p className="text-[11px] font-bold">Portfolio: IaC AWS</p>
                      <p className="text-[10px] text-zinc-500">Est: 2 Weeks</p>
                   </div>
                </div>
             </div>

             <div className="dash-card p-5 text-center">
                <div className="w-20 h-20 rounded-full border-4 border-white/5 border-t-white mx-auto mb-4 flex items-center justify-center">
                   <span className="text-[22px] font-black">76%</span>
                </div>
                <p className="text-sm font-bold mb-1">Career Velocity</p>
                <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-medium">Top 5% of Applicants</p>
             </div>
          </div>
       </div>
    </div>
  );
}
