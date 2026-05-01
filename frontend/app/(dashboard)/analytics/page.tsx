"use client";
import { useQuery } from "@tanstack/react-query";
import { analyticsApi, applicationsApi } from "@/lib/api";
import { useSubscription } from "@/lib/subscription";
import { motion } from "framer-motion";
import { XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, AreaChart, Area } from "recharts";
import { TrendingUp, Target, ShieldAlert, Award } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

export default function AnalyticsPage() {
  const { isPro, isPremium } = useSubscription();

  const { data: dashboard } = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => analyticsApi.dashboard().then((r) => r.data),
  });

  const { data: applications } = useQuery({
    queryKey: ["applications-stats"],
    queryFn: () => applicationsApi.stats().then((r) => r.data).catch(() => null),
    enabled: true,
  });

  const { data: gaps } = useQuery({
    queryKey: ["skill-gaps"],
    queryFn: () => analyticsApi.skillGaps().then((r) => r.data),
    enabled: isPro,
  });

  const { data: market } = useQuery({
    queryKey: ["market-insights"],
    queryFn: () => analyticsApi.market().then((r) => r.data).catch(() => null),
    enabled: isPremium,
  });

  const { data: velocityData } = useQuery({
    queryKey: ["velocity", 7],
    queryFn: () => analyticsApi.velocity(7).then((r) => r.data),
    staleTime: 5 * 60 * 1000,
  });

  const totalApplications =
    applications?.total_sent ??
    dashboard?.total_applications ??
    0;

  const appsToday = Number(dashboard?.applications_today || 0);
  const pendingApproval = Number(applications?.pending_approval ?? dashboard?.pending_approval ?? 0);
  const recruiterResponses = Number(applications?.recruiter_responses ?? 0);

  const timelineData = (Array.isArray(velocityData) && velocityData.length > 0)
    ? velocityData
    : [
        { name: "Mon", applied: 0, interviews: 0 },
        { name: "Tue", applied: 0, interviews: 0 },
        { name: "Wed", applied: 0, interviews: 0 },
        { name: "Thu", applied: 0, interviews: 0 },
        { name: "Fri", applied: 0, interviews: 0 },
        { name: "Sat", applied: 0, interviews: 0 },
        { name: "Sun", applied: 0, interviews: 0 },
      ];

  const velocityTotals = timelineData.reduce(
    (acc, d) => ({
      applied: acc.applied + (Number(d.applied) || 0),
      interviews: acc.interviews + (Number(d.interviews) || 0),
    }),
    { applied: 0, interviews: 0 }
  );
  const peakDay = timelineData.reduce(
    (best, d) => ((Number(d.applied) || 0) > (Number(best.applied) || 0) ? d : best),
    timelineData[0] || { name: "-", applied: 0, interviews: 0 }
  );
  const activeDays = timelineData.filter((d) => (Number(d.applied) || 0) > 0).length;
  const avgPerDay = (velocityTotals.applied / Math.max(timelineData.length, 1)).toFixed(1);

  return (
    <div className="dash-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 p-2">
        <div className="flex-1 dash-header">
          
          <motion.h1 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="dash-title"
          >
            Analytics.
          </motion.h1>
          <p className="dash-subtitle">
            Real-time application and market metrics from your account data.
          </p>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { l: "Total Applications", v: `${totalApplications}`, sub: "Pipeline", color: "text-white" },
          { l: "Pending Approval", v: `${pendingApproval}`, sub: "Needs Review", color: "text-white" },
          { l: "Responses", v: `${recruiterResponses}`, sub: "From Inbox Scan", color: "text-white" },
          { l: "Applied Today", v: `${appsToday}`, sub: "Today's Volume" }
        ].map((s, i) => (
          <motion.div 
            key={i} 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="dash-stat-card transition-all hover:border-white/20"
          >
             <p className="dash-label mb-1">{s.l}</p>
             <p className={cn("dash-value", s.color || "text-white")}>{s.v}</p>
             <div className="flex items-center gap-1.5 mt-2 pt-2 border-t border-white/5">
               <p className="dash-label">{s.sub}</p>
             </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6">
        {/* Activity Timeline */}
        <div className="bg-[#1c1c1e] p-3 rounded-xl border border-zinc-800 overflow-hidden flex flex-col">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-bold tracking-tight text-white flex items-center gap-2.5">
              <TrendingUp className="w-4 h-4 text-white" /> 
              Application Velocity
            </h2>
            <div className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-[9px] font-black text-white/70 uppercase tracking-widest">
              Last 7 Days
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-2 mb-3">
            <div className="bg-[#161616] border border-zinc-800 rounded-lg p-2">
              <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold">Total Applied</p>
              <p className="text-xl font-black text-white mt-1">{velocityTotals.applied}</p>
            </div>
            <div className="bg-[#161616] border border-zinc-800 rounded-lg p-2">
              <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold">Avg / Day</p>
              <p className="text-xl font-black text-white mt-1">{avgPerDay}</p>
              <p className="text-[10px] text-zinc-500 mt-1">Across {timelineData.length} days</p>
            </div>
            <div className="bg-[#161616] border border-zinc-800 rounded-lg p-2">
              <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold">Active Days</p>
              <p className="text-xl font-black text-white mt-1">{activeDays}/{timelineData.length}</p>
              <p className="text-[10px] text-zinc-500 mt-1">Peak: {peakDay?.name || "-"} ({Number(peakDay?.applied) || 0})</p>
            </div>
          </div>
          <div className="h-[220px] md:h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timelineData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorApplied" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ffffff" stopOpacity={0.1}/>
                    <stop offset="95%" stopColor="#ffffff" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorInterviews" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#a1a1aa" stopOpacity={0.12}/>
                    <stop offset="95%" stopColor="#a1a1aa" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.05)" vertical={false} />
                <XAxis dataKey="name" stroke="#a1a1aa" fontSize={10} fontWeight="bold" tickLine={false} axisLine={false} />
                <YAxis stroke="#a1a1aa" fontSize={10} fontWeight="bold" tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1c1c1e', border: '1px solid #27272a', borderRadius: '0.75rem', fontSize: '11px', fontWeight: 'bold', color: '#ffffff' }}
                  formatter={(value, name) => {
                    const v = Number(value ?? 0);
                    const n = String(name ?? "");
                    if (n === "applied") return [v, "Applied"];
                    if (n === "interviews") return [v, "Interviews"];
                    return [v, n];
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="applied"
                  stroke="#ffffff"
                  strokeWidth={3}
                  fillOpacity={1}
                  fill="url(#colorApplied)"
                  dot={{ r: 2 }}
                  activeDot={{ r: 5 }}
                />
                <Area
                  type="monotone"
                  dataKey="interviews"
                  stroke="#a1a1aa"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorInterviews)"
                  dot={{ r: 2 }}
                  activeDot={{ r: 4 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Pro/Premium Section */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Skill Gaps */}
        <div className={cn("bg-[#1c1c1e] p-4 rounded-xl border border-zinc-800 relative overflow-hidden", !isPro && "grayscale opacity-70")}>
           {!isPro && (
              <div className="absolute inset-0 z-10 flex items-center justify-center bg-black/55 backdrop-blur-sm p-6">
                <div className="w-full max-w-xs bg-[#1c1c1e] border border-zinc-800 rounded-2xl p-6 text-center shadow-2xl">
                  <ShieldAlert className="w-8 h-8 text-zinc-100 mx-auto mb-4" />
                  <p className="text-lg font-bold text-white tracking-tight mb-2">Pro Matrix Required</p>
                  <p className="text-zinc-400 text-sm font-bold uppercase tracking-widest mb-6">Upgrade to Unlock Insights</p>
                    <Link href="/subscription" className="block w-full py-3 bg-white text-black rounded-xl text-xs font-black uppercase tracking-widest hover:bg-zinc-200 transition-colors">Upgrade Now</Link>
                 </div>
              </div>
           )}
           <h2 className="text-lg font-bold tracking-tight text-white flex items-center gap-2.5 mb-2">
             <Target className="w-5 h-5 text-white/80" /> 
             Skill Gap Matrix
           </h2>
            <p className="text-zinc-400 text-xs font-medium mb-6">Critical missing skills detected in your target job market.</p>
             <div className="space-y-4">
                {(gaps && gaps.length > 0) ? gaps.map((sg: any, i: number) => (
                   <div key={i} className="flex items-center justify-between p-3 bg-[#1c1c1e] rounded-xl border border-zinc-800 group hover:bg-[#2a2a2a] transition-all">
                      <span className="font-black text-white tracking-tight uppercase">{sg.skill_name || sg.skill}</span>
                      <span className="text-[10px] font-black text-zinc-400 uppercase tracking-widest">{sg.demand_count || 0}% Market Demand</span>
                   </div>
                )) : (
                   <div className="p-3 bg-[#1c1c1e] rounded-xl border border-zinc-800 text-center">
                      <span className="font-black text-zinc-400 tracking-tight tracking-widest uppercase">Waiting for Data...</span>
                   </div>
                )}
             </div>
        </div>

        {/* Market Insights */}
        <div className={cn("bg-[#1c1c1e] p-4 rounded-xl border border-zinc-800 relative overflow-hidden", !isPremium && "grayscale opacity-70")}>
           {!isPremium && (
              <div className="absolute inset-0 z-10 flex items-center justify-center bg-black/55 backdrop-blur-sm p-6">
                <div className="w-full max-w-xs bg-[#1c1c1e] border border-zinc-800 rounded-2xl p-6 text-center shadow-2xl">
                  <Award className="w-8 h-8 text-zinc-100 mx-auto mb-4" />
                  <p className="text-lg font-bold text-white tracking-tight mb-2">Premium Intel Only</p>
                  <p className="text-zinc-400 text-sm font-bold uppercase tracking-widest mb-6">Exclusive Market Data</p>
                    <Link href="/subscription" className="block w-full py-3 bg-white text-black rounded-xl text-xs font-black uppercase tracking-widest hover:bg-zinc-200 transition-colors">Get Premium</Link>
                 </div>
              </div>
           )}
           <h2 className="text-lg font-bold tracking-tight text-white flex items-center gap-2.5 mb-2">
             <TrendingUp className="w-5 h-5 text-white/80" /> 
             Market Value
           </h2>
           <div className="space-y-6">
              {market?.salary_data ? (
                 <div className="p-3 bg-[#1c1c1e] text-white rounded-xl border border-white/5 shadow-xl">
                    <p className="text-[10px] font-black text-zinc-400 uppercase tracking-widest mb-2">Estimated Salary Band</p>
                    {(market.salary_data.min_salary && market.salary_data.max_salary) ? (
                     <>
                      <p className="text-[22px] font-bold text-white tracking-tighter">
                        {`₹${Math.round(market.salary_data.min_salary / 100000)}L - ₹${Math.round(market.salary_data.max_salary / 100000)}L`}
                      </p>
                      <p className="text-[10px] font-bold text-zinc-500 uppercase mt-4 tracking-widest">Calculated from {market.total_jobs_analyzed} data points</p>
                     </>
                    ) : (
                     <p className="text-[12px] font-bold text-zinc-500 uppercase tracking-widest">No salary data available yet</p>
                    )}
                 </div>
              ) : (
                 <div className="p-3 bg-[#1c1c1e] text-white rounded-xl border border-white/5 shadow-xl">
                    <p className="text-[10px] font-black text-zinc-400 uppercase tracking-widest mb-2">Estimated Salary Band</p>
                    <p className="text-[12px] font-bold text-zinc-500 uppercase tracking-widest">No market data available yet</p>
                 </div>
              )}
              {market?.by_work_mode ? (
                <div className="p-4 bg-muted/30 rounded-lg border border-border/50">
                   <p className="text-xs text-muted-foreground mb-2">Jobs by Work Mode</p>
                    <div className="space-y-2">
                       {Object.entries(market.by_work_mode as Record<string, number>).map(([mode, count]) => (
                          <div key={mode}>
                             <div className="flex justify-between text-[10px] mb-1">
                                <span className="capitalize">{mode}</span>
                                <span>{count} jobs</span>
                             </div>
                             <div className="h-1.5 bg-muted rounded-full">
                                <div className="h-full bg-white text-black rounded-full" style={{ width: `${(count / (market.total_jobs_analyzed || 1)) * 100}%` }} />
                             </div>
                          </div>
                       ))}
                    </div>
                </div>
              ) : (
                <div className="p-4 bg-muted/30 rounded-lg border border-border/50">
                   <p className="text-xs text-muted-foreground">No work mode distribution data yet.</p>
                </div>
              )}
           </div>
        </div>
      </div>
    </div>
  );
}
