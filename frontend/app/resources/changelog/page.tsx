"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import { 
  ShieldCheck, 
  History
} from "lucide-react";
import { NavBar } from "@/components/NavBar";

export default function ChangelogPage() {
  return (
    <div className="min-h-screen bg-black text-white selection:bg-white/20">
      <NavBar />

      <div className="max-w-6xl mx-auto px-6 pt-32 pb-32">
        {/* Hero */}
        <div className="max-w-[850px] mx-auto mb-20 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center"
          >
            <div className="flex items-center gap-2 mb-4">
              <div className="w-3 h-[2px] rounded-full bg-white/30" />
              <span className="text-[9px] font-black tracking-[0.3em] uppercase text-white/70">Changelog</span>
              <div className="w-3 h-[2px] rounded-full bg-white/30" />
            </div>
            <h1 className="text-4xl md:text-6xl font-black tracking-tighter mb-6 bg-gradient-to-b from-white to-white/60 bg-clip-text text-transparent transform-gpu">
              What&apos;s New at Applivo
            </h1>
            <p className="text-zinc-500 text-lg leading-relaxed max-w-xl">
              New features, improvements, and fixes to help you streamline your career growth.
            </p>
          </motion.div>
        </div>

        {/* Timeline Container */}
        <div className="relative">

          {/* v3.1 — Current Release */}
          <div className="grid grid-cols-1 lg:grid-cols-[240px_1fr] gap-12 lg:gap-24 mb-32 group">
            {/* Left: Date + Dot */}
            <div className="relative flex lg:flex-col items-start lg:items-end pt-2">
              <div className="sticky top-24 flex items-center gap-4 lg:gap-6 z-20">
                <span className="px-4 py-1.5 rounded-full border border-white/20 bg-white/5 text-white text-[10px] md:text-[11px] font-bold tracking-widest uppercase whitespace-nowrap shadow-[0_0_15px_rgba(255,255,255,0.05)]">
                  June 13, 2026
                </span>
                <div className="hidden lg:block w-2.5 h-2.5 rounded-full bg-white shadow-[0_0_12px_rgba(255,255,255,0.8)] border-2 border-black" />
              </div>
              {/* Vertical Line */}
              <div className="absolute hidden lg:block right-[4.5px] top-6 bottom-[-128px] w-px bg-zinc-800" />
            </div>

            {/* Right: Content */}
            <div className="space-y-12">
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest bg-white text-black">Current</span>
                  <span className="text-xs font-bold text-zinc-500 uppercase tracking-widest">v3.1.0</span>
                </div>
                <h2 className="text-4xl md:text-5xl font-black tracking-tighter mb-12">AI Orchestration Engine</h2>

                {/* Feature Image */}
                <div className="relative w-full aspect-[21/9] rounded-2xl overflow-hidden border border-white/10 mb-12 shadow-2xl group/image bg-zinc-950">
                  <Image
                    src="/assets/changelog/v3-orchestration.png"
                    alt="AI Orchestration Engine"
                    fill
                    className="object-cover transition-transform duration-700 group-hover/image:scale-105"
                    onError={() => {}}
                  />
                  <div className="absolute inset-x-0 bottom-0 h-1/3 bg-gradient-to-t from-black/60 to-transparent" />
                </div>

                <div className="space-y-16">

                  {/* Multi-Provider */}
                  <div className="space-y-4">
                    <div className="flex items-center gap-3 flex-wrap">
                      <h3 className="text-xl font-bold text-white tracking-tight">Multi-Provider AI Infrastructure</h3>
                      <span className="px-2 py-0.5 rounded-full border border-white/20 bg-white/5 text-[10px] font-medium text-white/80">Major Update</span>
                      <span className="px-2 py-0.5 rounded-full border border-zinc-800 bg-zinc-900 text-[10px] font-medium text-zinc-500">Infrastructure</span>
                    </div>
                    <p className="text-zinc-400 leading-relaxed text-base max-w-3xl">
                      Applivo now routes AI requests through a unified orchestration layer spanning three providers — Groq, Gemini, and OpenRouter. This enables higher reliability, broader model coverage, and intelligent provider switching without any user-facing disruption.
                    </p>
                    <div className="grid grid-cols-3 gap-4 max-w-xl pt-2">
                      {["Groq", "Gemini", "OpenRouter"].map((p) => (
                        <div key={p} className="p-4 rounded-2xl bg-zinc-900/50 border border-white/5 text-center">
                          <p className="text-sm font-bold text-zinc-200">{p}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Dynamic Model Selection */}
                  <div className="space-y-4">
                    <div className="flex items-center gap-3 flex-wrap">
                      <h3 className="text-xl font-bold text-white tracking-tight">Dynamic Model Selection</h3>
                      <span className="px-2 py-0.5 rounded-full border border-white/20 bg-white/5 text-[10px] font-medium text-white/80">New</span>
                    </div>
                    <p className="text-zinc-400 leading-relaxed text-base max-w-3xl">
                      Users can now select their preferred AI model directly from Settings. Models are grouped by plan tier with real-time availability gating.
                    </p>
                    <div className="overflow-hidden rounded-2xl border border-white/5 bg-zinc-900/30 max-w-2xl">
                      <table className="w-full text-left text-sm">
                        <thead>
                          <tr className="border-b border-white/5 text-zinc-500 uppercase text-[9px] font-black tracking-[0.2em]">
                            <th className="px-5 py-3">Model</th>
                            <th className="px-5 py-3">Provider</th>
                            <th className="px-5 py-3">Plan</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5 text-zinc-300 font-medium">
                          {[
                            ["Auto", "Groq", "Free"],
                            ["Llama 3.1 8B", "Groq", "Free"],
                            ["Llama 3.3 70B", "Groq", "Free"],
                            ["Gemini 1.5 Flash", "Gemini", "Free"],
                            ["DeepSeek V3", "OpenRouter", "Free"],
                            ["Qwen 3", "OpenRouter", "Free"],
                            ["Claude Sonnet 4", "OpenRouter", "Pro"],
                            ["Gemini 2.5 Pro", "Gemini", "Pro"],
                            ["DeepSeek R1", "OpenRouter", "Pro"],
                            ["Claude Opus 4.1", "OpenRouter", "Premium"],
                            ["GPT-5", "OpenRouter", "Premium"],
                          ].map(([model, provider, plan]) => (
                            <tr key={model}>
                              <td className="px-5 py-3">{model}</td>
                              <td className="px-5 py-3 text-zinc-500">{provider}</td>
                              <td className="px-5 py-3">
                                <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                                  plan === "Free" ? "bg-zinc-800 text-zinc-400" :
                                  plan === "Pro" ? "bg-blue-500/10 text-blue-400" :
                                  "bg-amber-500/10 text-amber-400"
                                }`}>{plan}</span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Intelligent Routing */}
                  <div className="space-y-4">
                    <div className="flex items-center gap-3 flex-wrap">
                      <h3 className="text-xl font-bold text-white tracking-tight">Intelligent Model Routing</h3>
                      <span className="px-2 py-0.5 rounded-full border border-white/20 bg-white/5 text-[10px] font-medium text-white/80">New</span>
                      <span className="px-2 py-0.5 rounded-full border border-zinc-800 bg-zinc-900 text-[10px] font-medium text-zinc-500">AI Pipeline</span>
                    </div>
                    <p className="text-zinc-400 leading-relaxed text-base max-w-3xl">
                      A new routing engine determines the optimal model for every request based on user preference, plan permissions, real-time availability, and latency signals — without any manual intervention.
                    </p>
                    <ul className="grid grid-cols-1 md:grid-cols-2 gap-y-3 gap-x-8 list-none text-sm text-zinc-500 max-w-xl">
                      {["User preference", "Plan permissions", "Real-time availability", "Performance signals", "Latency optimization", "Cost awareness"].map((item) => (
                        <li key={item} className="flex items-center gap-2">
                          <div className="w-1 h-1 rounded-full bg-white/20" /> {item}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Smart Fallback */}
                  <div className="space-y-4">
                    <div className="flex items-center gap-3 flex-wrap">
                      <h3 className="text-xl font-bold text-white tracking-tight">Smart Fallback System</h3>
                      <span className="px-2 py-0.5 rounded-full border border-white/20 bg-white/5 text-[10px] font-medium text-white/80">New</span>
                    </div>
                    <p className="text-zinc-400 leading-relaxed text-base max-w-3xl">
                      When a model becomes unavailable due to rate limits, provider outages, or capacity restrictions, Applivo automatically reroutes to the next best alternative. Three strategies available:
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl pt-2">
                      {[
                        { label: "Fastest", desc: "Groq → Gemini Flash → DeepSeek" },
                        { label: "Balanced", desc: "Groq 70B → Gemini → DeepSeek" },
                        { label: "Best Quality", desc: "Claude Sonnet → R1 → Gemini Pro" },
                      ].map((s) => (
                        <div key={s.label} className="p-5 rounded-2xl bg-zinc-900/50 border border-white/5">
                          <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-2">{s.label}</p>
                          <p className="text-sm text-zinc-300">{s.desc}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Reasoning Profiles */}
                  <div className="space-y-4">
                    <div className="flex items-center gap-3 flex-wrap">
                      <h3 className="text-xl font-bold text-white tracking-tight">Reasoning Profiles</h3>
                      <span className="px-2 py-0.5 rounded-full border border-white/20 bg-white/5 text-[10px] font-medium text-white/80">New</span>
                    </div>
                    <p className="text-zinc-400 leading-relaxed text-base max-w-3xl">
                      New reasoning modes control inference depth, injected into every AI request across the platform.
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl pt-2">
                      {[
                        { label: "Fast", temp: "0.2", tokens: "1k", note: "Lowest latency, cost optimized" },
                        { label: "Balanced", temp: "0.4", tokens: "2.5k", note: "Speed / quality tradeoff" },
                        { label: "Deep", temp: "0.7", tokens: "5k", note: "Extended reasoning, max quality" },
                      ].map((r) => (
                        <div key={r.label} className="p-5 rounded-2xl bg-zinc-900/50 border border-white/5 space-y-3">
                          <p className="text-sm font-bold text-white">{r.label}</p>
                          <div className="flex gap-4 text-[10px] text-zinc-500 font-mono">
                            <span>temp={r.temp}</span>
                            <span>{r.tokens} tokens</span>
                          </div>
                          <p className="text-xs text-zinc-500">{r.note}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Generation Styles */}
                  <div className="space-y-4">
                    <div className="flex items-center gap-3 flex-wrap">
                      <h3 className="text-xl font-bold text-white tracking-tight">Application Generation Styles</h3>
                      <span className="px-2 py-0.5 rounded-full border border-white/20 bg-white/5 text-[10px] font-medium text-white/80">New</span>
                    </div>
                    <p className="text-zinc-400 leading-relaxed text-base max-w-3xl">
                      Four specialized generation frameworks injected into every cover letter, resume optimization, follow-up, and AI chat response.
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl pt-2">
                      {[
                        { label: "Professional", desc: "Enterprise and ATS-optimized communication." },
                        { label: "Technical", desc: "Engineering-focused language and terminology." },
                        { label: "Startup", desc: "Builder-oriented, impact-driven communication." },
                        { label: "Enterprise", desc: "Executive-level, process-oriented communication." },
                      ].map((s) => (
                        <div key={s.label} className="p-5 rounded-2xl bg-zinc-900/50 border border-white/5">
                          <p className="text-sm font-bold text-white mb-1">{s.label}</p>
                          <p className="text-xs text-zinc-500">{s.desc}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Persistent Settings + Audit */}
                  <div className="space-y-4">
                    <h3 className="text-xl font-bold text-white tracking-tight">Persistent Settings Engine</h3>
                    <p className="text-zinc-400 leading-relaxed text-base max-w-3xl">
                      All AI preferences now survive page refresh, logout/login, and deployment restarts. Provider, model, reasoning profile, generation style, and fallback strategy are stored per-user in the database.
                    </p>
                    <ul className="grid grid-cols-1 md:grid-cols-2 gap-y-3 gap-x-8 list-none text-sm text-zinc-500 max-w-xl">
                      {[
                        "Settings V2 API",
                        "User Settings Database",
                        "Audit Log System (full change history)",
                        "Session Management",
                        "Active session listing",
                        "Logout from all devices",
                      ].map((item) => (
                        <li key={item} className="flex items-center gap-2">
                          <div className="w-1 h-1 rounded-full bg-white/20" /> {item}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Free Trial */}
                  <div className="space-y-4">
                    <div className="flex items-center gap-3 flex-wrap">
                      <h3 className="text-xl font-bold text-white tracking-tight">7-Day Free Trial</h3>
                      <span className="px-2 py-0.5 rounded-full border border-white/20 bg-white/5 text-[10px] font-medium text-white/80">New</span>
                    </div>
                    <p className="text-zinc-400 leading-relaxed text-base max-w-3xl">
                      New users now receive 7-day Starter access with full AI features — no credit card required upfront.
                    </p>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3 max-w-xl pt-2">
                      {["AI Resume Generation", "AI Cover Letters", "Job Automation", "AI Chat", "Multi-Model Access", "Dynamic Model Routing"].map((f) => (
                        <div key={f} className="px-4 py-3 rounded-xl bg-zinc-900/50 border border-white/5 text-xs text-zinc-400 font-medium">{f}</div>
                      ))}
                    </div>
                  </div>

                </div>
              </div>
            </div>
          </div>

          {/* v3.0 — Previous Release */}
          <div className="grid grid-cols-1 lg:grid-cols-[240px_1fr] gap-12 lg:gap-24 mb-32 group">
            {/* Left: Date + Dot */}
            <div className="relative flex lg:flex-col items-start lg:items-end pt-2">
              <div className="sticky top-24 flex items-center gap-4 lg:gap-6 z-20">
                <span className="px-4 py-1.5 rounded-full border border-zinc-800 bg-zinc-900/50 text-zinc-400 text-[10px] md:text-[11px] font-bold tracking-widest uppercase whitespace-nowrap">
                  April 15, 2026
                </span>
                <div className="hidden lg:block w-2.5 h-2.5 rounded-full bg-zinc-700 border-2 border-black" />
              </div>
              {/* Vertical Line */}
              <div className="absolute hidden lg:block right-[4.5px] top-6 bottom-[-128px] w-px bg-zinc-800" />
            </div>

            {/* Right: Content */}
            <div className="space-y-12">
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-xs font-bold text-zinc-500 uppercase tracking-widest">v3.0.0</span>
                </div>
                <h2 className="text-4xl md:text-5xl font-black tracking-tighter mb-12">The AI Transformation</h2>

                {/* Feature Image Header */}
                <div className="relative w-full aspect-[21/9] rounded-2xl overflow-hidden border border-white/10 mb-12 shadow-2xl group/image">
                  <Image 
                    src="/assets/changelog/v3-natural.png" 
                    alt="The AI Transformation" 
                    fill 
                    className="object-cover transition-transform duration-700 group-hover/image:scale-105" 
                  />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <h3 className="text-4xl md:text-7xl font-black text-white tracking-tighter drop-shadow-2xl opacity-90">
                      Dual-LLM
                    </h3>
                  </div>
                  <div className="absolute inset-x-0 bottom-0 h-1/3 bg-gradient-to-t from-black/60 to-transparent" />
                </div>

                <div className="space-y-16">
                  {/* AI Analysis */}
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <h3 className="text-xl font-bold text-white tracking-tight">Dual-LLM Job Analysis Engine Launched</h3>
                      <div className="flex gap-2">
                        <span className="px-2 py-0.5 rounded-full border border-white/20 bg-white/5 text-[10px] font-medium text-white/80">Major Update</span>
                        <span className="px-2 py-0.5 rounded-full border border-zinc-800 bg-zinc-900 text-[10px] font-medium text-zinc-500">AI Pipeline</span>
                      </div>
                    </div>
                    <p className="text-zinc-400 leading-relaxed text-base max-w-3xl">
                      Applivo now uses a two-pass AI system for job matching. Pass 1 runs a fast rule-based keyword filter using LLaMA-8B — jobs with less than 30% skill overlap are scored and skipped instantly with no LLM cost. Pass 2 sends qualified jobs to LLaMA-70B for deep structured extraction: required skills, tech stack, ATS keywords, responsibilities, match scores, and personalized recommendations.
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl pt-2">
                      <div className="p-5 rounded-2xl bg-zinc-900/50 border border-white/5">
                        <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-2">Models Used</p>
                        <p className="text-sm text-zinc-200">llama-3.3-70b-versatile & llama-3.1-8b-instant</p>
                      </div>
                      <div className="p-5 rounded-2xl bg-zinc-900/50 border border-white/5">
                        <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-2">Inference</p>
                        <p className="text-sm text-zinc-200">Groq primary with Google Gemini fallback</p>
                      </div>
                    </div>
                  </div>

                  {/* 6-Hour Cycle */}
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <h3 className="text-xl font-bold text-white tracking-tight">6-Hour Autonomous Agent Cycle</h3>
                      <div className="flex gap-2">
                        <span className="px-2 py-0.5 rounded-full border border-white/20 bg-white/5 text-[10px] font-medium text-white/80">Major Update</span>
                        <span className="px-2 py-0.5 rounded-full border border-zinc-800 bg-zinc-900 text-[10px] font-medium text-zinc-500">Automation</span>
                      </div>
                    </div>
                    <p className="text-zinc-400 leading-relaxed text-base max-w-3xl">
                      Celery Beat fires the full pipeline every 6 hours: scrape, analyze, gate, queue, apply, notify, follow-up. A Priority Queue ensures Premium subscribers&apos; applications are processed before lower-tier users.
                    </p>
                    <ul className="grid grid-cols-1 md:grid-cols-2 gap-y-3 gap-x-8 list-none text-sm text-zinc-500">
                      <li className="flex items-center gap-2"><div className="w-1 h-1 rounded-full bg-white/20" /> 7 named Celery queues</li>
                      <li className="flex items-center gap-2"><div className="w-1 h-1 rounded-full bg-white/20" /> In-memory min-heap backed by Redis</li>
                      <li className="flex items-center gap-2"><div className="w-1 h-1 rounded-full bg-white/20" /> Concurrency level 4</li>
                      <li className="flex items-center gap-2"><div className="w-1 h-1 rounded-full bg-white/20" /> Daily application limits enforced</li>
                    </ul>
                  </div>

                  {/* Career Assistant */}
                  <div className="space-y-4">
                    <h3 className="text-xl font-bold text-white tracking-tight">AI Career Assistant Chat</h3>
                    <div className="overflow-hidden rounded-2xl border border-white/5 bg-zinc-900/30 max-w-md">
                      <table className="w-full text-left text-sm">
                        <thead>
                          <tr className="border-b border-white/5 text-zinc-500 uppercase text-[9px] font-black tracking-[0.2em]">
                            <th className="px-6 py-4">Plan</th>
                            <th className="px-6 py-4">Monthly Credits</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5 text-zinc-300 font-medium">
                          <tr><td className="px-6 py-4">Starter</td><td className="px-6 py-4">100 messages</td></tr>
                          <tr><td className="px-6 py-4">Pro</td><td className="px-6 py-4">500 messages</td></tr>
                          <tr><td className="px-6 py-4">Premium</td><td className="px-6 py-4">Unlimited</td></tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* v2 — Infrastructure & Payments */}
          <div className="grid grid-cols-1 lg:grid-cols-[240px_1fr] gap-12 lg:gap-24 mb-32 group">
            {/* Left: Date + Dot */}
            <div className="relative flex lg:flex-col items-start lg:items-end pt-2">
              <div className="sticky top-24 flex items-center gap-4 lg:gap-6 z-20">
                <span className="px-4 py-1.5 rounded-full border border-zinc-800 bg-zinc-900/50 text-zinc-400 text-[10px] md:text-[11px] font-bold tracking-widest uppercase whitespace-nowrap">
                  March 20, 2026
                </span>
                <div className="hidden lg:block w-2.5 h-2.5 rounded-full bg-zinc-700 border-2 border-black" />
              </div>
              {/* Vertical Line */}
              <div className="absolute hidden lg:block right-[4.5px] top-6 bottom-[-128px] w-px bg-zinc-800 group-last:bg-gradient-to-b group-last:from-zinc-800 group-last:to-transparent" />
            </div>

            {/* Right: Content */}
            <div className="space-y-12">
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-xs font-bold text-zinc-500 uppercase tracking-widest">v2.0.0</span>
                </div>
                <h2 className="text-4xl md:text-5xl font-black tracking-tighter mb-12">Infrastructure & Payments</h2>

                {/* Feature Image Header */}
                <div className="relative w-full aspect-[21/9] rounded-2xl overflow-hidden border border-white/10 mb-12 shadow-2xl group/image">
                  <Image 
                    src="/assets/changelog/v2-natural.png" 
                    alt="Infrastructure" 
                    fill 
                    className="object-cover transition-transform duration-700 group-hover/image:scale-105" 
                  />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <h3 className="text-4xl md:text-7xl font-black text-white tracking-tighter drop-shadow-2xl opacity-90">
                      Distributed
                    </h3>
                  </div>
                  <div className="absolute inset-x-0 bottom-0 h-1/3 bg-gradient-to-t from-black/60 to-transparent" />
                </div>

                <div className="space-y-12">
                  <div className="space-y-4">
                    <h3 className="text-xl font-bold text-white tracking-tight">Razorpay Subscription Billing</h3>
                    <p className="text-zinc-400 leading-relaxed text-base max-w-3xl">
                      Full Razorpay payment flow integrated with HMAC-SHA256 verification. Automated 30-day subscription provisioning on successful capture.
                    </p>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-xl font-bold text-white tracking-tight">6-Container Docker Compose Stack</h3>
                    <div className="overflow-hidden rounded-2xl border border-white/5 bg-zinc-900/30 max-w-xl">
                      <table className="w-full text-left text-sm">
                        <thead>
                          <tr className="border-b border-white/5 text-zinc-500 uppercase text-[9px] font-black tracking-[0.2em]">
                            <th className="px-6 py-4">Container</th>
                            <th className="px-6 py-4">Role</th>
                            <th className="px-6 py-4">Port</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5 text-zinc-300 font-medium">
                          <tr><td className="px-6 py-4">backend</td><td className="px-6 py-4">FastAPI / Uvicorn</td><td className="px-6 py-4">8000</td></tr>
                          <tr><td className="px-6 py-4">worker</td><td className="px-6 py-4">Celery Worker</td><td className="px-6 py-4">internal</td></tr>
                          <tr><td className="px-6 py-4">database</td><td className="px-6 py-4">PostgreSQL 16</td><td className="px-6 py-4">5433</td></tr>
                          <tr><td className="px-6 py-4">redis</td><td className="px-6 py-4">Redis 7</td><td className="px-6 py-4">6379</td></tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* v1 — Foundation */}
          <div className="grid grid-cols-1 lg:grid-cols-[240px_1fr] gap-12 lg:gap-24 group">
            {/* Left: Date + Dot */}
            <div className="relative flex lg:flex-col items-start lg:items-end pt-2">
              <div className="sticky top-24 flex items-center gap-4 lg:gap-6 z-20">
                <span className="px-4 py-1.5 rounded-full border border-zinc-800 bg-zinc-900 text-zinc-500 text-[10px] md:text-[11px] font-bold tracking-widest uppercase whitespace-nowrap">
                  Feb 12, 2026
                </span>
                <div className="hidden lg:block w-2.5 h-2.5 rounded-full bg-zinc-800 border-2 border-black" />
              </div>
              {/* Vertical Line — fades at end */}
              <div className="absolute hidden lg:block right-[4.5px] top-6 bottom-0 w-px bg-gradient-to-b from-zinc-800 to-transparent" />
            </div>

            {/* Right: Content */}
            <div className="space-y-12">
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-xs font-bold text-zinc-500 uppercase tracking-widest">v1.0.0</span>
                </div>
                <h2 className="text-4xl md:text-5xl font-black tracking-tighter mb-12">Foundation</h2>

                {/* Feature Image Header */}
                <div className="relative w-full aspect-[21/9] rounded-2xl overflow-hidden border border-white/10 mb-12 shadow-2xl group/image">
                  <Image 
                    src="/assets/changelog/v1-natural.png" 
                    alt="Foundation" 
                    fill 
                    className="object-cover transition-transform duration-700 group-hover/image:scale-105" 
                  />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <h3 className="text-4xl md:text-7xl font-black text-white tracking-tighter drop-shadow-2xl opacity-90 uppercase">
                      Security
                    </h3>
                  </div>
                  <div className="absolute inset-x-0 bottom-0 h-1/3 bg-gradient-to-t from-black/60 to-transparent" />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                   <div className="flex flex-col gap-4 p-6 rounded-2xl bg-zinc-900/20 border border-white/5">
                      <ShieldCheck className="w-6 h-6 text-zinc-600" />
                      <div>
                        <h4 className="font-bold text-white mb-2">AES-256-GCM Encryption</h4>
                        <p className="text-zinc-500 text-sm leading-relaxed">Applied session cookies and credentials encrypted at rest with random nonces. Credentials never stored in plaintext.</p>
                      </div>
                   </div>
                   <div className="flex flex-col gap-4 p-6 rounded-2xl bg-zinc-900/20 border border-white/5">
                      <History className="w-6 h-6 text-zinc-600" />
                      <div>
                        <h4 className="font-bold text-white mb-2">Lifecycle Machine</h4>
                        <p className="text-zinc-500 text-sm leading-relaxed">Every application tracked via immutable event logs. Logic handles transitions from Pending to Offer Accepted or Failure.</p>
                      </div>
                   </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
