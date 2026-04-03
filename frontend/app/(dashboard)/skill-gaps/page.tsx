"use client";
import React from "react";
import { Target, BookOpen, ExternalLink, Zap, Lock, Sparkles, TrendingUp } from "lucide-react";
import { motion } from "framer-motion";

const skills = [
  { name: "Kubernetes (EKS/GKE)", gap: "High", priority: "Urgent", resource: "Udemy: K8s Mastery" },
  { name: "Terraform (IaC)", gap: "Medium", priority: "Recommended", resource: "Coursera: Cloud Infra" },
  { name: "Prometheus Monitoring", gap: "Low", priority: "Optional", resource: "Pluralsight: Obs" },
];

export default function SkillGapsPage() {
  return (
    <div className="space-y-8 max-w-6xl">
      <div>
        <h1 className="text-3xl font-bold font-display flex items-center gap-3">
          <Target className="w-8 h-8 text-emerald-500" />
          Skill Gap Analysis
        </h1>
        <p className="text-muted-foreground mt-1 text-lg text-brand-purple-light">
          AI comparison between your profile and target job roles.
        </p>
      </div>

       <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
             <div className="glass-card p-8 bg-brand-purple/5">
                <div className="flex items-center justify-between mb-8">
                   <h3 className="text-xl font-bold font-display">Target Role: Senior Platform Engineer</h3>
                   <div className="px-3 py-1 bg-brand-purple/20 text-brand-purple-light rounded-full text-xs font-bold ring-1 ring-brand-purple/30">
                      Overall Match: 76.5%
                   </div>
                </div>
                
                <div className="space-y-4">
                   {skills.map((s) => (
                      <div key={s.name} className="p-4 rounded-xl bg-white/5 border border-border group hover:border-brand-purple-light/50 transition-all">
                         <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                               <div className={`p-2 rounded-lg bg-zinc-900 border ${s.gap === 'High' ? 'border-red-500/50 text-red-400' : 'border-amber-500/50 text-amber-400'}`}>
                                  <TrendingUp className="w-4 h-4" />
                               </div>
                               <div>
                                  <h4 className="font-bold text-sm tracking-wide">{s.name}</h4>
                                  <p className="text-[10px] text-muted-foreground uppercase tracking-widest">{s.gap} Gap — {s.priority}</p>
                               </div>
                            </div>
                            <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-brand-purple-light/10 text-brand-purple-light text-[10px] font-bold hover:bg-brand-purple-light/20 transition-all uppercase tracking-widest">
                               Learn <ExternalLink className="w-3 h-3" />
                            </button>
                         </div>
                      </div>
                   ))}
                </div>
             </div>
          </div>

          <div className="space-y-6">
             <div className="glass-card p-6 border-amber-500/30 bg-amber-500/5">
                <h3 className="text-sm font-bold mb-4 flex items-center gap-2">
                   <Sparkles className="w-4 h-4 text-amber-500" />
                   AI Career Roadmap
                </h3>
                <div className="space-y-4">
                   <div className="relative pl-6 pb-6 border-l border-zinc-800">
                      <div className="absolute top-0 left-[-5px] w-2.5 h-2.5 rounded-full bg-emerald-500" />
                      <p className="text-[11px] font-bold">Certification: CKA</p>
                      <p className="text-[10px] text-muted-foreground">Est: 3 Weeks</p>
                   </div>
                   <div className="relative pl-6 pb-6 border-l border-zinc-800">
                      <div className="absolute top-0 left-[-5px] w-2.5 h-2.5 rounded-full bg-zinc-700" />
                      <p className="text-[11px] font-bold">Portfolio: IaC AWS</p>
                      <p className="text-[10px] text-muted-foreground">Est: 2 Weeks</p>
                   </div>
                </div>
             </div>

             <div className="glass-card p-8 text-center bg-gradient-to-br from-emerald-500/10 to-transparent">
                <div className="w-20 h-20 rounded-full border-4 border-emerald-500/20 border-t-emerald-500 mx-auto mb-4 flex items-center justify-center">
                   <span className="text-xl font-black font-display">76%</span>
                </div>
                <p className="text-sm font-medium mb-1">Career Velocity</p>
                <p className="text-[10px] text-muted-foreground uppercase tracking-widest">Top 5% of Applicants</p>
             </div>
          </div>
       </div>
    </div>
  );
}
