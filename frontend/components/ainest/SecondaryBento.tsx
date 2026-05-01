"use client";

import { motion } from "framer-motion";
import {
  Link2, Send, UploadCloud, Plus,
  Brain, Briefcase, Mail, Globe, Bot,
  Layers, FileText, Monitor, Target, Settings, MousePointer2, Activity
} from "lucide-react";

/* ─── CARD 1: Sync Graphic (Nodes) ─────────────────────────── */
function AgentNode({ avatar, delay, size = 70, isMain = false }: { avatar?: string, delay: number, size?: number, isMain?: boolean }) {
  return (
    <motion.div
      initial={{ scale: 0, opacity: 0 }}
      animate={{
        scale: 1,
        opacity: 1,
        y: isMain ? 0 : [0, -6, 0]
      }}
      transition={{
        scale: { type: "spring", stiffness: 220, damping: 18, delay },
        opacity: { duration: 0.4, delay },
        y: isMain ? {} : { duration: 4 + (delay % 1.5), repeat: Infinity, ease: "easeInOut", delay }
      }}
      className="absolute rounded-full flex items-center justify-center z-20 overflow-hidden"
      style={{
        width: size,
        height: size,
        background: "radial-gradient(circle at top, #334155 0%, #0f172a 100%)",
        border: "2px solid rgba(255,255,255,0.12)",
        boxShadow: isMain
          ? "0 0 30px rgba(148,163,184,0.3), 0 8px 32px rgba(0,0,0,0.5)"
          : "0 8px 24px rgba(0,0,0,0.4), inset 0 1px 2px rgba(255,255,255,0.1)",
      }}
    >
      {/* Cloud Decor at bottom - muted white */}
      <div className="absolute bottom-0 left-0 right-0 h-1/3 opacity-20 pointer-events-none">
        <svg viewBox="0 0 100 40" className="w-full h-full fill-white">
          <path d="M10 40 Q 25 20 40 40 Q 55 15 70 40 Q 85 25 100 40 L 100 40 L 0 40 Z" />
        </svg>
      </div>

      {/* Avatar Image / Icon */}
      {avatar && (
        <div
          className="w-[85%] h-[85%] rounded-full bg-cover bg-center"
          style={{ backgroundImage: `url(${avatar})`, backgroundSize: isMain ? 'cover' : '300% 200%' }}
        />
      )}

      {/* Glossy Overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent pointer-events-none" />
    </motion.div>
  );
}

function SyncGraphGraphic() {
  const cx = 200;
  const cy = 160; // Perfect mathematical vertical center of 320px height
  const r = 100; // Symmetrical radius for all nodes

  // Perfect hexagonal angles (even 60-degree increments)
  // Top, Top-Right, Bottom-Right, Bottom, Bottom-Left, Top-Left
  const angles = [270, 330, 30, 90, 150, 210];

  const platforms = [
    {
      label: "LinkedIn",
      icon: (
        <svg viewBox="0 0 24 24" className="w-8 h-8 fill-white/90">
          <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
        </svg>
      )
    },
    {
      label: "Internshala",
      icon: (
        <div className="flex flex-col items-center justify-center leading-none">
          <span className="text-white/90 font-black text-[18px] tracking-tighter leading-none">IS</span>
          <span className="text-white/50 text-[6px] font-bold tracking-widest mt-0.5 uppercase">Internshala</span>
        </div>
      )
    },
    {
      label: "Indeed",
      icon: (
        <svg viewBox="0 0 60 60" className="w-8 h-8 fill-white/90">
          <circle cx="30" cy="14" r="8" />
          <rect x="21" y="26" width="18" height="30" rx="3" />
        </svg>
      )
    },
    {
      label: "Naukri",
      icon: (
        <div className="flex flex-col items-center justify-center leading-none">
          <span className="text-white/90 font-black text-[13px] tracking-tight uppercase leading-none">naukri</span>
          <div className="w-6 h-[2.5px] bg-white/40 rounded-full mt-1.5" />
        </div>
      )
    },
    {
      label: "Glassdoor",
      icon: (
        <svg viewBox="0 0 32 32" className="w-8 h-8 fill-white/90">
          <path d="M16 3C8.8 3 3 8.8 3 16s5.8 13 13 13 13-5.8 13-13S23.2 3 16 3zm0 3c2.8 0 5.3 1 7.2 2.7H8.8C10.7 7 13.2 6 16 6zm0 20c-2.8 0-5.3-1-7.2-2.7h14.4C21.3 25 18.8 26 16 26zm8.5-5H7.5v-2h17v2zm0-5H7.5v-2h17v2z" />
        </svg>
      )
    },
    {
      label: "Resume",
      icon: (
        <svg viewBox="0 0 24 24" className="w-8 h-8 fill-none stroke-white/90" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
          <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="16" y1="13" x2="8" y2="13" />
          <line x1="16" y1="17" x2="8" y2="17" />
          <line x1="10" y1="9" x2="8" y2="9" />
        </svg>
      )
    },
  ];

  const mainAvatarPath = "/main_ai_agent_avatar_1776344206856.png";

  const toRad = (deg: number) => (deg * Math.PI) / 180;

  return (
    <div className="absolute inset-0 flex items-center justify-center">
      {/* Faint Blurred Code Background */}
      <div className="absolute inset-0 opacity-[0.02] pointer-events-none p-4 z-0 overflow-hidden blur-[0.5px]">
        <pre className="text-[9px] text-white font-mono leading-[2.2] tracking-wider w-full h-full whitespace-pre-wrap text-center">
          {`{  "agent_id": "agt_92xkL",  "role": "Orchestrator",  "status": "synchronized",
  "knowledge_base": "career_vault_v2", "state": "active_learning",
  "workflows": [
    { "id": "w1", "type": "auto_apply", "nodes": 6 },
    { "id": "w2", "type": "skill_mapping", "accuracy": "99.8%" }
  ]
}`}
        </pre>
      </div>

      <div className="flex-1 flex items-center justify-center relative z-10">
        
        {/* Center Lumi Orb — The "Spirit Core" (White Ethereal Version) */}
        <motion.div
          className="rounded-full flex items-center justify-center z-30"
          style={{
            width: 130,
            height: 130,
            background: "radial-gradient(circle at center, #ffffff 0%, #f0f0f0 20%, #000 100%)",
          }}
          initial={{ scale: 0, opacity: 0 }}
          whileInView={{ scale: 1, opacity: 1 }}
          viewport={{ once: true }}
          whileHover={{ scale: 1.05 }}
          animate={{
            y: [0, -10, 0],
            boxShadow: [
              "0 0 50px rgba(255, 255, 255, 0.4), inset 0 0 20px rgba(255, 255, 255, 0.2)",
              "0 0 100px rgba(255, 255, 255, 0.7), inset 0 0 40px rgba(255, 255, 255, 0.5)",
              "0 0 50px rgba(255, 255, 255, 0.4), inset 0 0 20px rgba(255, 255, 255, 0.2)",
            ]
          }}
          transition={{
            y: { duration: 5, repeat: Infinity, ease: "easeInOut" },
            boxShadow: { duration: 3, repeat: Infinity, ease: "easeInOut" },
            scale: { type: "spring", stiffness: 300, damping: 20 }
          }}
        >
          {/* Ethereal Smoke Layer 1 */}
          <motion.div 
            className="absolute inset-[-25px] rounded-full opacity-30"
            style={{
              background: "conic-gradient(from 0deg, transparent 0%, rgba(255,255,255,0.6) 20%, transparent 40%, rgba(255,255,255,0.3) 70%, transparent 100%)",
              filter: "blur(18px)"
            }}
            animate={{ rotate: 360, scale: [1, 1.15, 1] }}
            transition={{ 
              rotate: { duration: 10, repeat: Infinity, ease: "linear" },
              scale: { duration: 6, repeat: Infinity, ease: "easeInOut" }
            }}
          />

          {/* Ethereal Smoke Layer 2 */}
          <motion.div 
            className="absolute inset-[-35px] rounded-full opacity-20"
            style={{
              background: "conic-gradient(from 180deg, transparent 0%, rgba(255,255,255,0.4) 30%, transparent 50%, rgba(255,255,255,0.5) 80%, transparent 100%)",
              filter: "blur(22px)"
            }}
            animate={{ rotate: -360, scale: [1.15, 1, 1.15] }}
            transition={{ 
              rotate: { duration: 15, repeat: Infinity, ease: "linear" },
              scale: { duration: 7, repeat: Infinity, ease: "easeInOut" }
            }}
          />

          {/* Flare Emissions (The "tails" in the reference) */}
          {[0, 60, 120, 180, 240, 300].map((angle, i) => (
            <motion.div
              key={i}
              className="absolute w-[2px] h-[65px] bg-gradient-to-t from-transparent via-white/50 to-white shadow-[0_0_20px_rgba(255,255,255,1)]"
              style={{ 
                left: '50%',
                top: '50%',
                transformOrigin: '0% 0%',
                transform: `rotate(${angle}deg) translateY(-85px) translateX(-50%)`
              }}
              animate={{
                opacity: [0.3, 0.8, 0.3],
                height: [45, 80, 45],
              }}
              transition={{
                duration: 2 + i * 0.4,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            />
          ))}

          {/* Intense Core Shine */}
          <div className="absolute inset-[15%] rounded-full bg-white blur-xl opacity-40" />
          <div className="absolute w-2.5 h-2.5 rounded-full bg-white shadow-[0_0_15px_3px_white] opacity-90" />
        </motion.div>
      </div>
    </div>
  );
}


/* ─── CARD 2: Vault Upload ─────────────────────────────────── */
function VaultGraphic() {
  return (
    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">

      {/* Radial glow behind center */}
      <div
        className="absolute w-[500px] h-[500px] rounded-full z-0 opacity-40"
        style={{
          background: "radial-gradient(circle, rgba(37,99,235,0.2) 0%, transparent 70%)",
          left: '50%',
          top: '50%',
          transform: 'translate(-50%, -50%)'
        }}
      />

      {/* Localized glow behind card area */}
      <div
        className="absolute w-[300px] h-[300px] rounded-full z-0 opacity-30"
        style={{
          background: "radial-gradient(circle, rgba(59,130,246,0.25) 0%, transparent 70%)",
          left: '20%',
          top: '40%',
          transform: 'translate(-50%, -50%)'
        }}
      />

      {/* 1. Background Layer: The Upload Panel */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        whileInView={{ y: 0, opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="relative z-10"
      >
        <div
          className="w-[360px] bg-[#111111]/90 backdrop-blur-2xl border border-white/[0.05] rounded-[24px] shadow-[0_20px_60px_-10px_rgba(0,0,0,0.9)] p-6 flex flex-col"
          style={{ opacity: 1, transform: "scale(1)" }}
        >
          <p className="text-white text-[13px] font-semibold mb-5 opacity-80">Upload to knowledge base</p>
          <div className="bg-[#0a0a0a]/50 rounded-[20px] border border-white/[0.02] p-4 flex flex-col items-center justify-center text-center gap-4 h-[180px] w-[110%] -ml-6 pr-10 shadow-[inset_0_4px_20px_rgba(0,0,0,0.5)]">
            <div className="w-12 h-12 bg-[#1c1c1c] border border-[#2a2a2a] rounded-[14px] flex items-center justify-center opacity-80 shadow-[0_4px_12px_rgba(0,0,0,0.5)]">
              <UploadCloud className="w-[18px] h-[18px] text-[#bbb]" />
            </div>
            <div>
              <p className="text-white text-[13px] font-semibold mb-1 opacity-90">Upload files</p>
              <p className="text-[#888] text-[11px] leading-[1.6] w-[200px] opacity-70">
                Add docs, PDFs, or URLs to train your agent.
              </p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* 2. Middle Layer: Floating URL Card */}
      <motion.div
        initial={{ x: -20, opacity: 0 }}
        whileInView={{ x: 0, opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.7, delay: 0.2, ease: "easeOut" }}
        className="absolute z-20 p-4 rounded-[20px] bg-[#0d0d0d] border border-white/[0.05] shadow-[0_30px_60px_-12px_rgba(0,0,0,0.9)] w-[260px]"
        style={{
          left: '10%',
          top: '45%',
          transform: 'translate(0, -50%)'
        }}
      >
        <p className="text-[#888] text-[11px] mb-2.5 font-medium tracking-wide">Attach URL</p>
        <div className="flex bg-[#121212] border border-[#2a2a2a] rounded-[12px] items-center px-3 py-1.5 shadow-[inset_0_2px_4px_rgba(0,0,0,0.5)] h-[42px]">
          <span className="text-[#666] text-[13px] flex-1">Enter URL</span>
          <Send className="w-4 h-4 text-[#888] ml-2" />
        </div>
      </motion.div>

      {/* 3. Foreground Accent: Primary Action Button */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        whileInView={{ y: 0, opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="absolute z-30"
        style={{ right: '18%', bottom: '18%' }}
      >
        <button
          className="flex items-center justify-center gap-2 text-black px-5 py-2 rounded-[12px] text-[13px] font-bold shadow-[0_8px_24px_rgba(255,255,255,0.25)]"
          style={{
            background: "white",
          }}
        >
          <Plus className="w-4 h-4" />
          Select files
        </button>
      </motion.div>
    </div>
  );
}

/* ─── CARD 3: Multi-Channel Cursors ────────────────────────── */
function CursorsGraphic() {
  return (
    <div className="w-full flex justify-center items-center h-[180px] relative overflow-hidden">
      {/* Background Soft Aura */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[240px] h-[240px] bg-white/[0.03] rounded-full blur-[60px] z-0" />

      <div className="relative z-10 flex flex-col items-center">
        {/* Central Document Focus - Modern Glassy Resume */}
        <motion.div
          animate={{ scale: [1, 1.02, 1] }}
          transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
          className="w-[62px] h-[78px] rounded-[16px] bg-white/[0.05] backdrop-blur-[12px] border border-white/[0.1] shadow-[0_15px_35px_rgba(0,0,0,0.6),inset_0_1px_1px_rgba(255,255,255,0.1)] flex items-center justify-center z-20 relative"
        >
          <FileText className="w-8 h-8 text-white/90" strokeWidth={1.5} />

          {/* Internal Pulse Line */}
          <motion.div
            animate={{ opacity: [0, 1, 0], x: [-10, 10] }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="absolute bottom-4 left-1/2 -translate-x-1/2 w-8 h-[1px] bg-white/20"
          />
        </motion.div>

        {/* Clustered "Clicking" Cursors (Replicating exact reference interaction) */}
        {[
          { x: 38, y: 18, rotate: 15, delay: 0.1 },
          { x: 32, y: 48, rotate: 45, delay: 0.4 },
          { x: 8, y: 62, rotate: 0, delay: 0.7 },
          { x: -32, y: 42, rotate: -30, delay: 1.0 },
        ].map((cursor, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{
              opacity: 1,
              scale: [0.8, 1, 0.9, 1],
              x: [cursor.x + 10, cursor.x, cursor.x + 2, cursor.x],
              y: [cursor.y + 10, cursor.y, cursor.y + 2, cursor.y]
            }}
            transition={{
              duration: 2.5,
              repeat: Infinity,
              delay: cursor.delay,
              ease: "easeInOut"
            }}
            className="absolute z-30 drop-shadow-[0_4px_8px_rgba(0,0,0,0.6)]"
            style={{
              top: '50%',
              left: '50%',
              transform: `rotate(${cursor.rotate}deg)`,
              marginTop: cursor.y - 39,
              marginLeft: cursor.x
            }}
          >
            <MousePointer2 className="w-7 h-7 text-white fill-white stroke-[2px] stroke-black" />
          </motion.div>
        ))}
      </div>
    </div>
  );
}

/* ─── CARD 4: Radar Status ─────────────────────────────────── */
function RadarGraphic() {
  return (
    <div className="w-full flex justify-center items-center h-[180px] relative overflow-hidden">
      {/* Soft radial glow behind EVERYTHING */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] bg-green-500/10 rounded-full blur-[80px] z-0" />

      {/* Central Axis Point */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-0">
        {/* Soft concentric radar rings */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[240px] h-[240px] border border-white/[0.03] rounded-full z-0" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[150px] h-[150px] border border-white/[0.04] rounded-full z-0" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[70px] h-[70px] border border-white/[0.06] rounded-full z-0" />

        {/* Pulsing Detection Dot */}
        <motion.div
          animate={{
            opacity: [0.4, 1, 0.4],
            scale: [1, 1.25, 1]
          }}
          transition={{
            duration: 1.2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute w-[8px] h-[8px] bg-[#4ade80] rounded-full shadow-[0_0_12px_#4ade80,0_0_24px_rgba(74,222,128,0.6)] z-20"
          style={{ top: '-46px', left: '46px', transform: 'translate(-50%, -50%)' }}
        />

        {/* Animated Radar Sweep (2s Linear per request) */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="absolute top-1/2 left-1/2 w-[240px] h-[240px] rounded-full mix-blend-screen pointer-events-none z-10"
          style={{
            background: "conic-gradient(from 0deg, rgba(34,197,94,0) 0%, rgba(34,197,94,0) 65%, rgba(34,197,94,0.06) 85%, rgba(34,197,94,0.4) 100%)",
            x: "-50%",
            y: "-50%"
          }}
        >
          {/* Scanning Line Edge - Corrected 1px centering offset */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[2px] h-[120px] bg-gradient-to-t from-transparent via-[#4ade80] to-[#4ade80] shadow-[0_0_15px_#4ade80]" />
        </motion.div>

        {/* Center Target Icon Container (Modern Monitoring Style) */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[52px] h-[52px] bg-[#0d0d0d] border border-white/[0.08] rounded-[14px] z-30 flex items-center justify-center shadow-[0_8px_24px_rgba(0,0,0,0.6)] transition-colors">
          <Activity className="w-6 h-6 text-white" strokeWidth={2} />
        </div>
      </div>
    </div>
  );
}

/* ─── CARD 5: Lock & Security ──────────────────────────────── */
function LockGraphic() {
  return (
    <div className="w-full flex justify-center items-center h-[180px] relative overflow-hidden">
      {/* Micro-text Faint Background Code */}
      <div className="absolute inset-0 opacity-[0.05] pointer-events-none overflow-hidden flex items-center justify-center p-4">
        <pre className="text-[11px] text-white font-mono leading-[2.2] tracking-wider text-center w-full">
          {`{ "agent_id": "agt_92kxL", "label":
"Onboarding": "triggers": "environment":
"production": "***********************" "type":
"event", "source": "signup_form",
"action": [ "validate", "encrypt" ],
"workflow": { "steps": [ {
"step": "verify", "message": "auth",
"content": "profile fully set up." } ] },
"integration": "s2", "type": "oauth2"
"security": "L4", "rotation": "daily" }`}
        </pre>
      </div>

      {/* Centered White Aura (Enhanced Atmospheric Glow) */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[320px] h-[320px] bg-white/[0.03] rounded-full blur-[100px] z-0" />

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        whileInView={{ y: 0, opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.7 }}
        className="relative z-10 flex flex-col items-center"
      >
        {/* Shackle: Significantly brighter to match silver/metal look in reference */}
        <div className="w-[36px] h-[30px] border-[4.5px] border-[#d1d5db]/60 border-b-0 rounded-t-[18px] mb-[-3.5px] relative z-0" />

        {/* 1:1 Match Glassmorphism Housing with Enhanced Lighting */}
        <div
          className="w-[82px] h-[68px] flex items-center justify-center relative z-10"
          style={{
            background: "linear-gradient(180deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.01) 100%)",
            backdropFilter: "blur(24px)",
            borderRadius: "12px",
            border: "1px solid rgba(255,255,255,0.12)",
            borderTop: "1px solid rgba(255,255,255,0.4)", // Ultra-sharp top-edge highlight
            boxShadow: "0 20px 60px rgba(0,0,0,0.85), inset 0 1px 2px rgba(255,255,255,0.1)"
          }}
        >
          {/* Luminous Core localized behind the star */}
          <div className="absolute w-10 h-10 bg-white/[0.3] blur-3xl rounded-full" />

          {/* Sharp Pinpoint Star */}
          <svg width="17" height="17" viewBox="0 0 24 24" fill="white">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
        </div>
      </motion.div>
    </div>
  );
}

/* ─── MAIN EXPORT ──────────────────────────────────────────── */
export function SecondaryBento() {
  return (
    <section className="bg-[#080808] pb-16 px-6 relative z-10">
      <div className="max-w-[1240px] mx-auto">


        {/* ROW 1: 2 Columns */}
        <div className="grid grid-cols-1 lg:grid-cols-[1.1fr_1.8fr] gap-5 mb-5">

          {/* Card 1: Agent Context */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.7 }}
            className="rounded-[24px] border border-[#1e1e1e] overflow-hidden flex flex-col h-[500px] shadow-[0_0_80px_rgba(0,0,0,0.3)] relative group"
            style={{
              background: "radial-gradient(circle at top left, rgba(255,255,255,0.03) 0%, #0d0d0d 100%)"
            }}
          >
            <div className="flex items-center gap-3 px-7 py-5 border-b border-white/[0.03] relative z-20">
              <Bot className="w-[18px] h-[18px] text-[#888]" strokeWidth={2} />
              <span className="text-[#e5e5e5] font-semibold text-[15px] tracking-tight">Introducing Lumi</span>
            </div>

            <div className="flex-1 relative">
              <SyncGraphGraphic />
            </div>

            <div className="px-8 pb-10 pt-4 border-t border-transparent relative z-20">
              <h3 className="text-[18px] font-semibold text-white mb-2 tracking-tight">Your AI job agent, working around the clock</h3>
              <p className="text-[15px] text-[#888] leading-[1.6]">
                Lumi continuously searches for opportunities, optimizes your profile, and applies to matching roles — so you never miss a beat.
              </p>
            </div>
          </motion.div>

          {/* Card 2: Custom Knowledge Base */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.7, delay: 0.1 }}
            className="rounded-[24px] border border-[#1e1e1e] overflow-hidden flex flex-col h-[500px] shadow-[0_0_80px_rgba(0,0,0,0.3)] relative group"
            style={{
              background: "radial-gradient(circle at top left, rgba(255,255,255,0.03) 0%, #0d0d0d 100%)"
            }}
          >
            <div className="flex items-center gap-3 px-7 py-5 border-b border-white/[0.03] relative z-20">
              <Settings className="w-[18px] h-[18px] text-[#888]" strokeWidth={2} />
              <span className="text-[#e5e5e5] font-semibold text-[15px] tracking-tight">Custom Knowledge Base</span>
            </div>

            <div className="flex-1 relative">
              <VaultGraphic />
            </div>

            <div className="px-8 pb-10 pt-4 border-t border-transparent relative z-20 w-full lg:w-[65%]">
              <h3 className="text-[18px] font-semibold text-white mb-2 tracking-tight">Your Career, Stored Once — Applied Everywhere</h3>
              <p className="text-[15px] text-[#888] leading-[1.6]">
                Upload your resume and preferences once. Applivo keeps your profile ready and automatically applies to relevant jobs across different platforms.
              </p>
            </div>
          </motion.div>

        </div>

        {/* ROW 2: 3 Columns */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">

          {/* Card 3: Smart Automation */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.6 }}
            className="rounded-[24px] border border-[#1e1e1e] overflow-hidden flex flex-col h-[400px] p-8 shadow-[0_0_50px_rgba(0,0,0,0.2)] group"
            style={{
              background: "radial-gradient(circle at top left, rgba(255,255,255,0.03) 0%, #0d0d0d 100%)"
            }}
          >
            <div className="flex-1 flex flex-col justify-center">
              <CursorsGraphic />
            </div>
            <div className="mt-auto pt-6">
              <h3 className="text-[18px] font-semibold text-white mb-2 tracking-tight">Smart Application Automation</h3>
              <p className="text-[15px] text-[#888] leading-[1.6]">
                Applivo automatically finds relevant opportunities, fills application forms, and submits them on your behalf — saving hours of manual effort.
              </p>
            </div>
          </motion.div>

          {/* Card 4: Tracking */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="rounded-[24px] border border-[#1e1e1e] overflow-hidden flex flex-col h-[400px] p-8 shadow-[0_0_50px_rgba(0,0,0,0.2)] group"
            style={{
              background: "radial-gradient(circle at top left, rgba(255,255,255,0.03) 0%, #0d0d0d 100%)"
            }}
          >
            <div className="flex-1 flex flex-col justify-center">
              <RadarGraphic />
            </div>
            <div className="mt-auto pt-6">
              <h3 className="text-[18px] font-semibold text-white mb-2 tracking-tight">Real-Time Application Tracking</h3>
              <p className="text-[15px] text-[#888] leading-[1.6]">
                Track every application, response, and interview update in one unified dashboard with instant notifications.
              </p>
            </div>
          </motion.div>

          {/* Card 5: Security */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="rounded-[24px] border border-[#1e1e1e] overflow-hidden flex flex-col h-[400px] p-8 shadow-[0_0_50px_rgba(0,0,0,0.2)] relative group"
            style={{
              background: "radial-gradient(circle at top left, rgba(255,255,255,0.04) 0%, #0d0d0d 100%)"
            }}
          >
            <div className="flex-1 flex flex-col justify-center">
              <LockGraphic />
            </div>
            <div className="mt-auto pt-6 relative z-10">
              <h3 className="text-[18px] font-semibold text-white mb-2 tracking-tight">Secure Career Data</h3>
              <p className="text-[15px] text-[#888] leading-[1.6]">
                Your resume, personal details, and application history are securely stored with strong encryption and privacy protection.
              </p>
            </div>
          </motion.div>

        </div>

      </div>
    </section>
  );
}
