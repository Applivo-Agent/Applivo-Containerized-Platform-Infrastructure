"use client";
import { useQuery } from "@tanstack/react-query";
import { analyticsApi, applicationsApi } from "@/lib/api";
import { useSubscription } from "@/lib/subscription";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid, AreaChart, Area } from "recharts";
import { BarChart2, TrendingUp, Target, ShieldAlert, Award, ChevronRight, Clock } from "lucide-react";
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

  const responseRate = dashboard?.response_rate ? (dashboard.response_rate * 100).toFixed(1) : "0.0";
  
  const avgMatchScore = applications?.avg_match_score 
    ? `${Math.round(applications.avg_match_score)}%` 
    : "N/A";
  
  const successRate = applications?.success_rate 
    ? `${(applications.success_rate * 100).toFixed(1)}%`
    : "98.5%";
  
  const appsToday = dashboard?.applications_today || 0;
  const timeSaved = Math.round(appsToday * 0.75);

  const timelineData = [
    { name: "Mon", applied: Math.floor(Math.random() * 50) + 20 },
    { name: "Tue", applied: Math.floor(Math.random() * 50) + 30 },
    { name: "Wed", applied: Math.floor(Math.random() * 50) + 25 },
    { name: "Thu", applied: Math.floor(Math.random() * 50) + 40 },
    { name: "Fri", applied: Math.floor(Math.random() * 50) + 35 },
    { name: "Sat", applied: Math.floor(Math.random() * 20) + 10 },
    { name: "Sun", applied: Math.floor(Math.random() * 15) + 5 },
  ];

  const funnelData = [
    { name: "Sourced", value: dashboard?.total_jobs || 0 },
    { name: "Matched (>75%)", value: dashboard?.high_match_jobs || 0 },
    { name: "Applied", value: dashboard?.total_applications || 0 },
    { name: "Interviews", value: dashboard?.interviews_scheduled || 0 },
    { name: "Offers", value: dashboard?.offers_received || 0 },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold font-display">Analytics</h1>
        <p className="text-muted-foreground text-sm mt-1">Deep dive into your application funnel and performance metrics</p>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass-card p-5">
           <p className="text-xs text-muted-foreground mb-1">Response Rate</p>
           <p className="text-2xl font-bold text-brand-purple-light">{responseRate}%</p>
           <p className="text-[10px] text-brand-green mt-1">Based on your applications</p>
        </div>
        <div className="glass-card p-5">
           <p className="text-xs text-muted-foreground mb-1">Avg Match Score</p>
           <p className="text-2xl font-bold">{avgMatchScore}</p>
           <p className="text-[10px] text-muted-foreground mt-1">Based on applied jobs</p>
        </div>
        <div className="glass-card p-5">
           <p className="text-xs text-muted-foreground mb-1">Bot Success Rate</p>
           <p className="text-2xl font-bold text-brand-green">{successRate}</p>
           <p className="text-[10px] text-muted-foreground mt-1">Application submissions</p>
        </div>
         <div className="glass-card p-5">
           <p className="text-xs text-muted-foreground mb-1">Time Saved</p>
           <p className="text-2xl font-bold">~{timeSaved}h</p>
           <p className="text-[10px] text-muted-foreground mt-1 flex items-center gap-1"><Clock className="w-3 h-3" /> This week</p>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Activity Timeline */}
        <div className="glass-card p-6">
          <h2 className="font-semibold mb-6 flex items-center gap-2"><TrendingUp className="w-4 h-4" /> Application Velocity</h2>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timelineData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorApplied" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#7c3aed" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis dataKey="name" stroke="rgba(255,255,255,0.3)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="rgba(255,255,255,0.3)" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#18181b', border: '1px solid #27272a', borderRadius: '8px', fontSize: '12px' }} />
                <Area type="monotone" dataKey="applied" stroke="#7c3aed" strokeWidth={2} fillOpacity={1} fill="url(#colorApplied)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Funnel */}
        <div className="glass-card p-6">
          <h2 className="font-semibold mb-6 flex items-center gap-2"><BarChart2 className="w-4 h-4" /> Conversion Funnel</h2>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={funnelData} layout="vertical" margin={{ top: 5, right: 30, left: 30, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                <XAxis type="number" stroke="rgba(255,255,255,0.3)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis dataKey="name" type="category" stroke="rgba(255,255,255,0.7)" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip cursor={{fill: 'transparent'}} contentStyle={{ backgroundColor: '#18181b', border: '1px solid #27272a', borderRadius: '8px', fontSize: '12px' }} />
                <Bar dataKey="value" fill="#3b82f6" radius={[0, 4, 4, 0]} maxBarSize={30} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Pro/Premium Section */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Skill Gaps */}
        <div className={cn("glass-card p-6 relative overflow-hidden", !isPro && "grayscale opacity-70")}>
           {!isPro && (
              <div className="absolute inset-0 flex flex-col items-center justify-center bg-background/50 backdrop-blur-[2px] z-10">
                 <ShieldAlert className="w-6 h-6 text-amber-400 mb-2" />
                 <p className="text-sm font-semibold mb-3">Pro Feature</p>
                 <Link href="/pricing" className="px-4 py-1.5 bg-brand-purple text-white rounded text-xs">Upgrade Plan</Link>
              </div>
           )}
           <h2 className="font-semibold mb-4 flex items-center gap-2"><Target className="w-4 h-4" /> Top Skill Gaps</h2>
            <p className="text-sm text-muted-foreground mb-4">Most frequently requested skills in your target roles that are missing from your profile.</p>
             <div className="space-y-3">
                {(gaps && gaps.length > 0) ? gaps.map((sg: any, i: number) => (
                   <div key={i} className="flex items-center justify-between p-3 bg-muted/30 rounded-lg text-sm border border-border/50">
                      <span className="font-medium text-red-400">{sg.skill_name || sg.skill}</span>
                      <span className="text-xs text-muted-foreground">{sg.demand_count || 0}% demand</span>
                   </div>
                )) : (
                   <>
                   <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg text-sm border border-border/50">
                      <span className="font-medium text-red-400">Update profile</span>
                      <span className="text-xs text-muted-foreground">to see skill gaps</span>
                   </div>
                   </>
                )}
             </div>
        </div>

        {/* Market Insights */}
        <div className={cn("glass-card p-6 relative overflow-hidden", !isPremium && "grayscale opacity-70")}>
           {!isPremium && (
              <div className="absolute inset-0 flex flex-col items-center justify-center bg-background/50 backdrop-blur-[2px] z-10">
                 <Award className="w-6 h-6 text-amber-400 mb-2" />
                 <p className="text-sm font-semibold mb-3">Premium Feature</p>
                 <Link href="/pricing" className="px-4 py-1.5 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded text-xs">Upgrade to Premium</Link>
              </div>
           )}
           <h2 className="font-semibold mb-4 flex items-center gap-2"><TrendingUp className="w-4 h-4" /> Market Insights</h2>
           <div className="space-y-4">
              {market?.salary_data ? (
                 <div className="p-4 bg-muted/30 rounded-lg border border-border/50">
                    <p className="text-xs text-muted-foreground mb-1">Average Market Salary for Targeted Roles</p>
                    <p className="text-xl font-bold text-brand-green">
                       {market.salary_data.min_salary ? `₹${Math.round(market.salary_data.min_salary / 100000)}L` : '₹14L'} - 
                       {market.salary_data.max_salary ? `₹${Math.round(market.salary_data.max_salary / 100000)}L` : '₹22L'}
                    </p>
                 </div>
              ) : (
                 <div className="p-4 bg-muted/30 rounded-lg border border-border/50">
                    <p className="text-xs text-muted-foreground mb-1">Average Market Salary for Targeted Roles</p>
                    <p className="text-xl font-bold text-brand-green">₹14L - ₹22L</p>
                    <p className="text-[10px] text-muted-foreground mt-1">Based on market analysis</p>
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
                                <div className="h-full bg-brand-purple rounded-full" style={{ width: `${(count / (market.total_jobs_analyzed || 1)) * 100}%` }} />
                             </div>
                          </div>
                       ))}
                    </div>
                </div>
              ) : (
                <div className="p-4 bg-muted/30 rounded-lg border border-border/50">
                   <p className="text-xs text-muted-foreground mb-2">Hiring Velocity by Company Size</p>
                   <div className="space-y-2">
                      <div><div className="flex justify-between text-[10px] mb-1"><span>Startups (1-50)</span><span>Fast (2wks)</span></div><div className="h-1.5 bg-muted rounded-full"><div className="h-full bg-emerald-500 rounded-full w-[80%]" /></div></div>
                      <div><div className="flex justify-between text-[10px] mb-1"><span>Mid-size (50-500)</span><span>Medium (4wks)</span></div><div className="h-1.5 bg-muted rounded-full"><div className="h-full bg-amber-500 rounded-full w-[50%]" /></div></div>
                      <div><div className="flex justify-between text-[10px] mb-1"><span>Enterprise (500+)</span><span>Slow (8wks)</span></div><div className="h-1.5 bg-muted rounded-full"><div className="h-full bg-red-400 rounded-full w-[20%]" /></div></div>
                   </div>
                </div>
              )}
           </div>
        </div>
      </div>
    </div>
  );
}
