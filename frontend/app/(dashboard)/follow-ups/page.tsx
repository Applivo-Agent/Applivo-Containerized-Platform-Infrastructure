"use client";
import React from "react";
import { Bell, Mail, Clock, Send, CheckCircle2, AlertCircle, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

const followups = [
  { id: 1, company: "Amazon", role: "SDE II", status: "Scheduled", time: "in 2 hours", type: "Email" },
  { id: 2, company: "Microsoft", role: "Specialist", status: "Sent", time: "Yesterday", type: "LinkedIn" },
  { id: 3, company: "Meta", role: "Product Manager", status: "Delayed", time: "Pending", type: "Email" },
];

export default function FollowUpsPage() {
  return (
    <div className="space-y-8 max-w-6xl">
      <div>
        <h1 className="text-3xl font-bold font-display flex items-center gap-3">
          <Bell className="w-8 h-8 text-amber-500" />
          Automated Follow-ups
        </h1>
        <p className="text-muted-foreground mt-1 text-lg">
          Smart reminders and automated check-ins for pending applications.
        </p>
      </div>

       <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
             <div className="glass-card overflow-hidden">
                <div className="p-6 border-b border-border bg-white/5 flex items-center justify-between">
                   <h3 className="font-semibold flex items-center gap-2">
                      <Clock className="w-4 h-4 text-brand-purple-light" />
                      Pending Interactions
                   </h3>
                   <div className="text-[10px] text-muted-foreground uppercase tracking-widest">
                      Auto-pilot: <span className="text-emerald-500 font-bold">Enabled</span>
                   </div>
                </div>
                <div className="divide-y divide-border">
                   {followups.map((f) => (
                      <div key={f.id} className="p-6 hover:bg-white/5 transition-all group flex items-center justify-between">
                         <div className="flex items-center gap-4">
                            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${f.status === 'Sent' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-brand-purple/10 text-brand-purple-light'}`}>
                               {f.type === 'Email' ? <Mail className="w-5 h-5" /> : <Send className="w-5 h-5" />}
                            </div>
                            <div>
                               <h4 className="font-bold text-lg">{f.company}</h4>
                               <p className="text-sm text-muted-foreground">{f.role} • {f.time}</p>
                            </div>
                         </div>
                         <div className="flex flex-col items-end gap-2">
                             <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${f.status === 'Sent' ? 'bg-emerald-500/20 text-emerald-500' : f.status === 'Delayed' ? 'bg-red-500/20 text-red-400' : 'bg-brand-purple/20 text-brand-purple-light'}`}>
                                {f.status}
                             </span>
                             <button className="text-xs text-muted-foreground hover:text-foreground hover:underline italic">Pause</button>
                         </div>
                      </div>
                   ))}
                </div>
             </div>
          </div>

          <div className="space-y-6">
             <div className="glass-card p-6 border-brand-purple/30 bg-brand-purple/5">
                <h3 className="text-[11px] font-black uppercase tracking-widest text-brand-purple-light mb-4">Smart Sequence</h3>
                <div className="space-y-4">
                   <div className="flex items-start gap-3">
                      <div className="mt-1 w-5 h-5 rounded-full bg-brand-purple/20 flex items-center justify-center text-[10px] font-bold text-brand-purple-light shrink-0">1</div>
                      <p className="text-xs text-muted-foreground"><span className="text-foreground font-bold">Day 3:</span> Soft check-in on application status.</p>
                   </div>
                   <div className="flex items-start gap-3">
                      <div className="mt-1 w-5 h-5 rounded-full bg-brand-purple/20 flex items-center justify-center text-[10px] font-bold text-brand-purple-light shrink-0">2</div>
                      <p className="text-xs text-muted-foreground"><span className="text-foreground font-bold">Day 7:</span> Ask about interview timelines.</p>
                   </div>
                   <div className="flex items-start gap-3 opacity-40">
                      <div className="mt-1 w-5 h-5 rounded-full bg-brand-purple/20 flex items-center justify-center text-[10px] font-bold text-brand-purple-light shrink-0">3</div>
                      <p className="text-xs text-muted-foreground"><span className="text-foreground font-bold">Day 14:</span> Final follow-up and value add.</p>
                   </div>
                </div>
             </div>

             <div className="glass-card p-8 bg-gradient-to-br from-amber-500/10 to-transparent">
                <div className="flex items-center gap-3 mb-4">
                   <Sparkles className="w-5 h-5 text-amber-500" />
                   <h3 className="font-bold">Ghosting Rate</h3>
                </div>
                <div className="text-4xl font-black mb-1">12%</div>
                <p className="text-xs text-muted-foreground mb-4">Your current ghosting rate is below the industry average (45%).</p>
                <div className="w-full h-1 bg-muted rounded-full overflow-hidden">
                   <div className="h-full bg-emerald-500" style={{ width: '88%' }} />
                </div>
             </div>
          </div>
       </div>
    </div>
  );
}
