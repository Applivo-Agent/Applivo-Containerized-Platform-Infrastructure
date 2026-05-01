"use client";
import React from "react";
import { Bell, Mail, Clock, Send, CheckCircle2, AlertCircle, Sparkles , Loader2} from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

const followups = [
  { id: 1, company: "Amazon", role: "SDE II", status: "Scheduled", time: "in 2 hours", type: "Email" },
  { id: 2, company: "Microsoft", role: "Specialist", status: "Sent", time: "Yesterday", type: "LinkedIn" },
  { id: 3, company: "Meta", role: "Product Manager", status: "Delayed", time: "Pending", type: "Email" },
];

export default function FollowUpsPage() {
  return (
      <div className="dash-page max-w-6xl space-y-6">
         <div className="flex items-center gap-3">
            <div className="p-2 bg-[#242424] border border-white/[0.08] rounded-lg">
              <Bell className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Automated Follow-ups</h1>
              <p className="text-sm text-zinc-400 mt-1">Smart reminders and automated check-ins for pending applications.</p>
            </div>
          </div>

       <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
             <div className="dash-card overflow-hidden p-0">
                <div className="p-4 border-b border-zinc-800 bg-[#161616] flex items-center justify-between">
                   <h3 className="text-sm font-bold flex items-center gap-2 text-white/90">
                      <Clock className="w-4 h-4 text-white" />
                      Pending Interactions
                   </h3>
                   <div className="text-[10px] text-zinc-500 font-bold uppercase tracking-widest">
                      Auto-pilot: <span className="text-white font-black">Enabled</span>
                   </div>
                </div>
                <div className="divide-y divide-white/5">
                   {followups.map((f) => (
                      <div key={f.id} className="p-4 hover:bg-[#161616] transition-all group flex items-center justify-between">
                         <div className="flex items-center gap-4">
                            <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-[#161616] text-white border border-zinc-800">
                               {f.type === 'Email' ? <Mail className="w-5 h-5" /> : <Send className="w-5 h-5" />}
                            </div>
                            <div>
                               <h4 className="font-bold text-sm text-white">{f.company}</h4>
                               <p className="text-[12px] text-zinc-500 font-medium">{f.role} • {f.time}</p>
                            </div>
                         </div>
                         <div className="flex flex-col items-end gap-1.5">
                              <span className="px-2.5 py-1 rounded-md text-[10px] font-black uppercase tracking-widest bg-white/5 border border-white/10 text-white">
                                 {f.status}
                              </span>
                              <button className="text-[10px] font-bold text-zinc-600 hover:text-white uppercase tracking-wider transition-colors">Pause</button>
                         </div>
                      </div>
                   ))}
                </div>
             </div>
          </div>

          <div className="space-y-6">
             <div className="dash-card p-4">
                <h3 className="text-[11px] font-black uppercase tracking-widest text-zinc-500 mb-4">Smart Sequence</h3>
                <div className="space-y-4">
                   <div className="flex items-start gap-3">
                      <div className="mt-1 w-5 h-5 rounded-full bg-[#161616] border border-zinc-800 flex items-center justify-center text-[10px] font-bold text-white shrink-0">1</div>
                      <p className="text-[12px] text-zinc-400"><span className="text-white font-bold">Day 3:</span> Soft check-in on application status.</p>
                   </div>
                   <div className="flex items-start gap-3">
                      <div className="mt-1 w-5 h-5 rounded-full bg-[#161616] border border-zinc-800 flex items-center justify-center text-[10px] font-bold text-white shrink-0">2</div>
                      <p className="text-[12px] text-zinc-400"><span className="text-white font-bold">Day 7:</span> Ask about interview timelines.</p>
                   </div>
                   <div className="flex items-start gap-3 opacity-30">
                      <div className="mt-1 w-5 h-5 rounded-full bg-[#161616] border border-zinc-800 flex items-center justify-center text-[10px] font-bold text-white shrink-0">3</div>
                      <p className="text-[12px] text-zinc-500"><span className="text-white font-bold">Day 14:</span> Final follow-up and value add.</p>
                   </div>
                </div>
             </div>

             <div className="dash-card p-4">
                <div className="flex items-center gap-3 mb-4">
                   <Sparkles className="w-5 h-5 text-white" />
                   <h3 className="text-sm font-bold text-white/90">Ghosting Rate</h3>
                </div>
                <div className="text-[28px] font-black mb-1 text-white tracking-tighter">12%</div>
                <p className="text-[11px] text-zinc-400 leading-relaxed mb-4">Your current ghosting rate is below the industry average (45%).</p>
                <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                   <div className="h-full bg-white shadow-[0_0_8px_rgba(255,255,255,0.5)]" style={{ width: '88%' }} />
                </div>
             </div>
          </div>
       </div>
    </div>
  );
}
