"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import {
  Bold, Italic, Underline, Link2, Code2,
  AlignLeft, Sparkles, Command, Sparkle,
  Network, CheckCircle2
} from "lucide-react";

/* ─── LEFT CARD: Prompt / Typewriter ──────────────────────────── */
const prompts = [
  {
    text: "Find matching internships from Internshala. Score them based on my profile potential. Automatically route ",
    highlight: "high match roles",
    endText: " to my @dashboard while auto-applying for remote roles."
  }
];

const toolbarButtons = [
  { icon: <Bold className="w-4 h-4" />, label: "Bold" },
  { icon: <Italic className="w-4 h-4" />, label: "Italic" },
  { icon: <Underline className="w-4 h-4" />, label: "Underline" },
  { icon: <Link2 className="w-4 h-4" />, label: "Link" },
  { icon: <Code2 className="w-4 h-4" />, label: "Code" },
  { icon: <AlignLeft className="w-4 h-4" />, label: "Align" },
];

function PromptBuilderCard() {
  return (
    <div className="flex flex-col h-full bg-[#0d0d0d] relative w-full overflow-hidden">

      {/* Background radial gradient to give that faint glow in the center */}
      <div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[200px] pointer-events-none"
        style={{
          background: "radial-gradient(ellipse at center, rgba(255,255,255,0.06) 0%, transparent 70%)",
          filter: "blur(20px)"
        }}
      />

      {/* Editor Content Area (Centered vertically) */}
      <div className="flex-1 flex items-center justify-center relative px-10 py-16">

        {/* Floating Toolbar styling exact to Kilo */}
        <motion.div
          initial={{ opacity: 0, y: 10, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="absolute top-[80px] left-[70px] flex items-center gap-2 bg-[#121212] border border-[#222] rounded-full px-3 py-2 shadow-[0_8px_30px_rgba(0,0,0,0.8)] z-20"
        >
          {toolbarButtons.map((btn, i) => (
            <button
              key={i}
              className="w-8 h-8 rounded shrink-0 flex items-center justify-center text-[#999] hover:text-white transition-colors"
              title={btn.label}
            >
              {btn.icon}
            </button>
          ))}
          <div className="w-px h-5 bg-[#333] mx-1 shrink-0" />
          <button className="flex items-center gap-1.5 px-3 py-1.5 shrink-0 text-[#ffffff] hover:text-[#38bdf8] transition-colors font-medium text-[14px]">
            <Sparkles className="w-4 h-4 shrink-0" />
            Ask
          </button>
        </motion.div>

        {/* Typed Text exactly matching the kilo styling */}
        <div className="text-[22px] leading-[1.65] font-normal text-[#888] relative z-10 max-w-[420px] ml-auto mr-auto pl-10 pt-16">
          <p>
            Find matching internships from <span className="text-[#00a5ec] font-bold">Internshala</span>. Score them based on my profile potential. Automatically route{" "}

            <span className="relative inline-block text-[#38bdf8] bg-[#ffffff]/10 border border-[#ffffff]/30 rounded px-1.5 mx-0.5">
              high match roles
              <motion.span
                animate={{ opacity: [1, 0, 1] }}
                transition={{ duration: 1, repeat: Infinity }}
                className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-[2px] w-[2px] h-[70%] bg-white"
              />
            </span>

            {" "}to my <span className="text-[#ffffff]">@dashboard</span> while auto-applying for remote roles.
          </p>
        </div>

      </div>

      {/* Footer Title / Subtext */}
      <div className="px-8 pb-8 pt-4 z-10 border-t border-transparent relative">
        <h3 className="text-[17px] font-semibold text-white mb-2 tracking-tight">Apply to jobs up to 10x faster</h3>
        <p className="text-[15px] text-[#888] leading-[1.6] max-w-[380px]">
          Set your preferences. Applivo matches opportunities to your profile and submits applications automatically.
        </p>
      </div>

    </div>
  );
}

/* ─── RIGHT CARD: Pipeline Connectors ────────────────────────── */
const workflowCodeBg = `{ "id": "kb_7f3", "name": "Internshala Sync",
  "status": "active", "created_at": "2025-12-22T09:14:32Z", 
  "config": { "type": "url", "address": "https://internshala.com/", 
  "last_synced": "2025-12-21T18:02:10Z" }, "settings": { 
  "auto_update": true, "chunk_size": 800, "chunk_overlap": 150 }, 
  "metrics": { "documents_indexed": 42, "tokens_processed": 183450 } }
{ "id": "kb_8a1", "name": "AI Matcher", "status": "active", 
  "created_at": "2025-12-22T09:14:32Z", "config": { "type": "pdf", 
  "filename": "Applivo_Resume.pdf" } }\n`;

const nodes = [
  { id: "internshala", x: 40, y: 140, title: "Internshala", sub: "New internship posted", icon: "🇮🇳", color: "#00a5ec", badge: "check" },
  { id: "matcher", x: 200, y: 40, title: "AI Matcher", sub: "Score match > 85%", icon: "🌟", color: "#eab308", badge: "check" },
  { id: "apply", x: 180, y: 270, title: "Agent Action", sub: "Auto Apply", icon: "🤖", color: "#38bdf8", badge: "wrench" },
  { id: "dashboard", x: 340, y: 160, title: "Airtable", sub: "Add to database", icon: "🧊", color: "#10b981", badge: "wrench", dragging: true },
];

function PipelineBuilderCard() {
  return (
    <div className="flex flex-col h-full bg-[#0d0d0d] relative w-full overflow-hidden">

      {/* Background Code Faint Text */}
      <div className="absolute inset-x-8 inset-y-16 overflow-hidden pointer-events-none opacity-[0.15]">
        <pre className="text-[12px] text-[#666] font-mono leading-[1.8] whitespace-pre-wrap">
          {workflowCodeBg}
          {workflowCodeBg}
          {workflowCodeBg}
        </pre>
      </div>

      <div className="flex-1 relative w-full min-h-[360px] pointer-events-none">

        {/* Connection Curves */}
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 500 400" fill="none">
          {/* Internshala to Matcher */}
          <path d="M110,165 C140,165 170,60 200,60" stroke="rgba(255,255,255,0.08)" strokeWidth="2" strokeDasharray="4 4" />
          <circle cx="155" cy="115" r="9" fill="#121212" stroke="#222" strokeWidth="1" />
          <path d="M151,115 h8 M155,111 v8" stroke="#555" strokeWidth="1.5" strokeLinecap="round" />
          
          {/* Matcher to Airtable */}
          <path d="M280,60 C320,60 320,175 340,185" stroke="rgba(255,255,255,0.08)" strokeWidth="2" strokeDasharray="4 4" />
          <circle cx="310" cy="122" r="9" fill="#121212" stroke="#222" strokeWidth="1" />
          <path d="M306,122 h8 M310,118 v8" stroke="#555" strokeWidth="1.5" strokeLinecap="round" />

          {/* Internshala to Agent Action */}
          <path d="M115,175 C140,185 150,285 180,295" stroke="rgba(255,255,255,0.08)" strokeWidth="2" strokeDasharray="4 4" />
          <circle cx="145" cy="235" r="9" fill="#121212" stroke="#222" strokeWidth="1" />
          <path d="M141,235 h8 M145,231 v8" stroke="#555" strokeWidth="1.5" strokeLinecap="round" />

        </svg>

        {/* Nodes */}
        {nodes.map((n, i) => (
          <motion.div
            key={i}
            className={`absolute flex items-center gap-3 bg-[#111] border border-[#222] rounded-2xl px-4 py-3 shadow-[0_10px_40px_rgba(0,0,0,0.6)] ${n.dragging ? 'z-30 rotate-2 scale-105' : 'z-20'}`}
            style={{ left: n.x, top: n.y, width: 200 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 + (i * 0.1) }}
          >
            {/* Status Badges - Premium solid style */}
            {n.badge === "check" ? (
              <div className="absolute -top-1.5 -right-1.5 w-6 h-6 bg-[#059669] border border-white/10 rounded-full flex items-center justify-center shadow-[0_2px_10px_rgba(0,0,0,0.5)]">
                <CheckCircle2 className="w-3.5 h-3.5 text-white" />
              </div>
            ) : (
              <div className="absolute -top-1.5 -right-1.5 w-6 h-6 bg-[#d97706] border border-white/10 rounded-full flex items-center justify-center shadow-[0_2px_10px_rgba(0,0,0,0.5)]">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="text-white">
                  <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
                </svg>
              </div>
            )}

            {/* Icon Box - Custom SVGs for Internshala & Airtable */}
            <div className="w-10 h-10 rounded-xl flex items-center justify-center text-[18px] bg-[#161616] border border-white/10 shrink-0 font-bold overflow-hidden"
                 style={{ 
                   boxShadow: `0 0 20px ${n.id === 'internshala' ? 'rgba(0,165,236,0.15)' : 'rgba(255,255,255,0.05)'}`
                 }}>
              {n.id === 'internshala' ? (
                <div className="bg-[#00a5ec] w-full h-full flex items-center justify-center">
                   <span className="text-white text-[16px] font-black tracking-tighter">IS</span>
                </div>
              ) : n.id === 'dashboard' ? (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M12 2L3 7v10l9 5 9-5V7l-9-5z" fill="#f87171" fillOpacity="0.8" />
                  <path d="M12 2L3 7l9 5 9-5-9-5z" fill="#facc15" fillOpacity="0.8" />
                  <path d="M12 12v10l9-5V7l-9 5z" fill="#3b82f6" fillOpacity="0.8" />
                </svg>
              ) : n.id === 'apply' ? (
                 <div className="w-full h-full bg-[#38bdf8]/10 flex items-center justify-center">
                    <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix&backgroundColor=b6e3f4" alt="avatar" className="w-full h-full object-cover" />
                 </div>
              ) : n.icon}
            </div>

            {/* Text */}
            <div className="flex-1 min-w-0 flex flex-col justify-center">
              <p className="text-white text-[13px] font-semibold truncate leading-tight mb-0.5">{n.title}</p>
              <p className="text-[#666] text-[11px] truncate leading-tight">{n.sub}</p>
            </div>

            {/* Simulated Hand Cursor */}
            {n.dragging && (
              <motion.div
                className="absolute right-2 -bottom-6 w-6 h-6 text-white"
                initial={{ rotate: -15, scale: 1.2 }}
                animate={{ rotate: 0, scale: 1 }}
              >
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M21 11H20V6c0-1.1-.9-2-2-2s-2 .9-2 2v2h-1V4c0-1.1-.9-2-2-2s-2 .9-2 2v4h-1V2c0-1.1-.9-2-2-2s-2 .9-2 2v9.31l-3.32-1.39c-.58-.24-1.25-.13-1.74.31-.83.74-.91 2.03-.17 2.86l5.77 6.4c1.19 1.33 2.89 2.1 4.69 2.1H18c2.76 0 5-2.24 5-5v-6c0-1.1-.9-2-2-2z" /></svg>
              </motion.div>
            )}
          </motion.div>
        ))}

      </div>

      {/* Footer Title / Subtext */}
      <div className="px-8 pb-8 pt-4 z-10 border-t border-transparent relative">
        <h3 className="text-[17px] font-semibold text-white mb-2 tracking-tight">Automation working for you 24/7</h3>
        <p className="text-[15px] text-[#888] leading-[1.6] max-w-[380px]">
          Applivo detects new jobs, matches them to your profile, and applies automatically — all in the background.
        </p>
      </div>

    </div>
  );
}


/* ─── MAIN EXPORTED COMPONENT ────────────────────────────────── */
export function WorkflowBento() {
  return (
    <section className="bg-[#080808] py-24 px-6 relative z-10">
      <div className="max-w-[1240px] mx-auto">

        {/* Two-column bento grid exact to the Kilo image layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 h-auto lg:h-[600px]">

          {/* LEFT CARD */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
            className="rounded-[24px] bg-[#0d0d0d] border border-[#1e1e1e] overflow-hidden flex flex-col transition-all h-full shadow-[0_0_80px_rgba(0,0,0,0.5)]"
          >
            {/* Minimalist Top Header Bar */}
            <div className="flex items-center gap-3 px-6 py-5 border-b border-[#181818]/60">
              <Command className="w-[18px] h-[18px] text-[#888]" strokeWidth={2} />
              <span className="text-[#e5e5e5] font-semibold text-[15px] tracking-tight">Automation Handle Applications</span>
            </div>

            {/* Content Body */}
            <div className="flex-1 overflow-hidden relative">
              <PromptBuilderCard />
            </div>
          </motion.div>

          {/* RIGHT CARD */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.7, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="rounded-[24px] bg-[#0d0d0d] border border-[#1e1e1e] overflow-hidden flex flex-col transition-all h-full shadow-[0_0_80px_rgba(0,0,0,0.5)]"
          >
            {/* Minimalist Top Header Bar */}
            <div className="flex items-center gap-3 px-6 py-5 border-b border-[#181818]/60">
              <Network className="w-[18px] h-[18px] text-[#888]" strokeWidth={2} />
              <span className="text-[#e5e5e5] font-semibold text-[15px] tracking-tight">Intelligent Job Automation</span>
            </div>

            {/* Content Body */}
            <div className="flex-1 overflow-hidden relative">
              <PipelineBuilderCard />
            </div>
          </motion.div>

        </div>
      </div>
    </section>
  );
}
