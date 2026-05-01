"use client";

import { motion } from "framer-motion";
import { LayoutDashboard } from "lucide-react";

/* ─── Integration Icons (job platforms & tools Applivo connects to) ─────── */
const integrations = [
  // Outer Arc
  {
    name: "LinkedIn",
    bg: "#0077B5",
    icon: (
      <svg viewBox="0 0 24 24" fill="white" className="w-6 h-6">
        <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
      </svg>
    ),
    angle: 110,
    radius: "outer",
    delay: 0,
  },
  {
    name: "Telegram",
    bg: "#0088CC",
    icon: (
      <svg viewBox="0 0 24 24" fill="white" className="w-5 h-5 ml-0.5">
        <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.891 8.22l-1.912 9.03c-.135.6-.5.75-.991.45l-2.91-2.14-1.403 1.35c-.15.15-.3.3-.6.3l.18-2.535 4.61-4.162c.2-.18-.045-.285-.3-.12l-5.7 3.585-2.46-.773c-.54-.18-.555-.54.12-.81l9.585-3.69c.45-.165.84.105.675.87z" />
      </svg>
    ),
    angle: 55,
    radius: "outer",
    delay: 0.4,
  },
  {
    name: "Internshala",
    bg: "#00A5EC",
    icon: (
      <div className="flex flex-col items-center justify-center leading-none">
        <span className="text-white font-black text-[18px] tracking-tighter">IS</span>
        <span className="text-white/60 text-[5px] font-bold tracking-widest uppercase mt-0.5">Official</span>
      </div>
    ),
    angle: 140,
    radius: "outer",
    delay: 0.2,
  },
  {
    name: "Gmail",
    bg: "#EA4335",
    icon: (
       <svg viewBox="0 0 24 24" fill="white" className="w-5 h-5">
         <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z" />
       </svg>
    ),
    angle: 25,
    radius: "outer",
    delay: 0.6,
  },
  // Inner Arc
  {
    name: "Llama 3",
    bg: "#0081fb",
    icon: (
      <img src="/assets/meta_logo_glossy.png" alt="Meta AI" className="w-[100%] h-[100%] object-contain" />
    ),
    angle: 95,
    radius: "inner",
    delay: 0.1,
  },
  {
    name: "Resume",
    bg: "#3b82f6",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" className="w-4 h-4">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
        <line x1="10" y1="9" x2="8" y2="9" />
      </svg>
    ),
    angle: 145,
    radius: "inner",
    delay: 0.5,
  },
  {
    name: "Ollama",
    bg: "#8b5cf6",
    icon: (
      <img src="/assets/ollama_face.png" alt="Ollama" className="w-6 h-6 object-contain invert brightness-[100]" />
    ),
    angle: 42,
    radius: "inner",
    delay: 0.3,
  },
  {
    name: "Submission",
    bg: "#8b5cf6",
    icon: (
      <svg viewBox="0 0 24 24" fill="white" className="w-5 h-5">
        <path d="M22 2L11 13M22 2L15 22L11 13M11 13L2 9L22 2" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
    angle: 80,
    radius: "outer",
    delay: 0.8,
  },
];

/* ─── Helper: convert polar to cartesian, centered at bottom-center ──────── */
function polarToCartesian(
  angleDeg: number,
  radiusPx: number,
  cx: number,
  cy: number
) {
  // 0° = right, 180° = left, 90° = top (we flip because SVG y is inverted)
  const rad = ((180 - angleDeg) * Math.PI) / 180;
  return {
    x: cx + radiusPx * Math.cos(rad),
    y: cy - radiusPx * Math.sin(rad),
  };
}

const W = 900;
const H = 440;
const CX = W / 2;
const CY = H + 30; // arc center below visible area — so only top half shows
const R_OUTER = 340;
const R_INNER = 220;

export function IntegrationsHub() {
  return (
    <section className="bg-[#080808] py-24 px-6 relative z-10">
      <div className="max-w-5xl mx-auto">

        {/* Section label */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <p className="text-white/80 text-[13px] font-semibold uppercase tracking-[0.1em] mb-3">Integrations</p>
          <h2 className="text-[36px] md:text-[44px] font-bold text-white tracking-[-0.02em] leading-[1.15] mb-4">
            Every job platform. One agent.
          </h2>
          <p className="text-[#666] text-[16px] max-w-[480px] mx-auto leading-[1.7]">
            Applivo connects to all major job boards and ATS systems in seconds — no manual setup required.
          </p>
        </motion.div>

        {/* Main card */}
        <motion.div
          initial={{ opacity: 0, y: 32 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          className="rounded-2xl overflow-hidden border border-white/10 relative"
          style={{
            background: "linear-gradient(180deg, #0f0f0f 0%, #050505 100%)",
            boxShadow: "0 20px 60px -20px rgba(255, 255, 255, 0.05)"
          }}
        >
          {/* Card header */}
          <div className="relative z-20 px-7 pt-7 pb-5">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-8 h-8 bg-white/5 border border-white/10 rounded-lg flex items-center justify-center backdrop-blur-md">
                <LayoutDashboard className="w-4 h-4 text-white" />
              </div>
              <h3 className="text-white text-[19px] font-semibold tracking-tight">Integrations and job platform hub</h3>
            </div>
            <p className="text-[#888] text-[14px]">
              Connect to any job board in minutes and trigger automated multi-platform applications automatically.
            </p>
          </div>

          {/* Stat pills */}
          <div className="relative z-20 px-7 pb-6 grid grid-cols-2 gap-4">
            {[
              { label: "Connected platforms", value: "10+" },
              { label: "Daily auto-applications", value: "+150/day" },
            ].map((s) => (
              <div
                key={s.label}
                className="rounded-xl border border-white/5 px-6 py-4 backdrop-blur-md relative overflow-hidden"
                style={{ background: "rgba(255,255,255,0.02)" }}
              >
                <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-500" />
                <p className="text-[#777] text-[12px] mb-1 uppercase tracking-wider">{s.label}</p>
                <p className="text-white text-[28px] font-bold tracking-tight leading-none">{s.value}</p>
              </div>
            ))}
          </div>

          {/* Arc + Icons visualization */}
          <div className="relative w-full overflow-hidden" style={{ height: H }}>

            {/* Dot grid background */}
            <div
              className="absolute inset-0"
              style={{
                backgroundImage: "radial-gradient(circle at 1px 1px, rgba(255,255,255,0.07) 1px, transparent 0)",
                backgroundSize: "24px 24px",
              }}
            />

            {/* Animated Radial glow bloom at center */}
            <motion.div
              className="absolute pointer-events-none"
              animate={{ 
                opacity: [0.6, 1, 0.6],
                scale: [0.95, 1.05, 0.95]
              }}
              transition={{ duration: 6, ease: "easeInOut", repeat: Infinity }}
              style={{
                left: "50%",
                bottom: "-80px",
                transform: "translateX(-50%)",
                width: 600,
                height: 400,
                background: "radial-gradient(ellipse at center bottom, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.05) 45%, transparent 70%)",
                filter: "blur(25px)",
              }}
            />
            <div
              className="absolute pointer-events-none"
              style={{
                left: "50%",
                bottom: "-40px",
                transform: "translateX(-50%)",
                width: 300,
                height: 200,
                background: "radial-gradient(ellipse at center, rgba(255, 255, 255, 0.1) 0%, transparent 60%)",
                filter: "blur(20px)",
              }}
            />

            {/* SVG Arcs */}
            <svg
              className="absolute inset-0 w-full h-full"
              viewBox={`0 0 ${W} ${H}`}
              preserveAspectRatio="xMidYMax slice"
              fill="none"
            >
              <defs>
                <linearGradient id="arcGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="rgba(255, 255, 255, 0)" />
                  <stop offset="50%" stopColor="rgba(255, 255, 255, 0.4)" />
                  <stop offset="100%" stopColor="rgba(255, 255, 255, 0)" />
                </linearGradient>
              </defs>
              
              {/* Outer arc */}
              <motion.path
                d={`M ${CX - R_OUTER} ${CY} A ${R_OUTER} ${R_OUTER} 0 0 1 ${CX + R_OUTER} ${CY}`}
                stroke="url(#arcGrad)"
                strokeWidth="2.5"
                strokeDasharray="4 6"
                animate={{ strokeDashoffset: [0, -100] }}
                transition={{ repeat: Infinity, duration: 4, ease: "linear" }}
              />
              {/* Inner arc */}
              <motion.path
                d={`M ${CX - R_INNER} ${CY} A ${R_INNER} ${R_INNER} 0 0 1 ${CX + R_INNER} ${CY}`}
                stroke="url(#arcGrad)"
                strokeWidth="2"
                strokeDasharray="3 5"
                animate={{ strokeDashoffset: [0, 100] }}
                transition={{ repeat: Infinity, duration: 5, ease: "linear" }}
              />
            </svg>

            {/* Integration Icons positioned along arcs */}
            {integrations.map((intg, i) => {
              const r = intg.radius === "outer" ? R_OUTER : R_INNER;
              const iconSize = intg.radius === "outer" ? 54 : 44;
              const pos = polarToCartesian(intg.angle, r, CX, CY);
              const left = Math.round(pos.x);
              const top = Math.round(pos.y);

              return (
                <motion.div
                  key={intg.name}
                  className="absolute"
                  style={{
                    left,
                    top,
                    transform: "translate(-50%, -50%)",
                  }}
                  initial={{ opacity: 0, scale: 0.6 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{
                    delay: intg.delay + 0.3,
                    duration: 0.5,
                    type: "spring",
                    stiffness: 200,
                    damping: 18,
                  }}
                >
                  <motion.div
                    animate={{ y: [0, intg.delay % 2 === 0 ? -10 : 10, 0] }}
                    transition={{
                      duration: 4 + intg.delay,
                      repeat: Infinity,
                      ease: "easeInOut",
                      type: "tween",
                      delay: intg.delay * 0.5,
                    }}
                    className="relative"
                  >
                    {/* Pulsing ring behind the icon */}
                    <motion.div
                      className="absolute inset-0 rounded-2xl pointer-events-none"
                      style={{ border: `1px solid ${intg.bg}` }}
                      animate={{ scale: [1, 1.3], opacity: [0.5, 0] }}
                      transition={{ duration: 2, repeat: Infinity, ease: "easeOut", delay: intg.delay }}
                    />
                    
                    <div
                      className="relative rounded-2xl flex items-center justify-center shadow-2xl backdrop-blur-md"
                      style={{
                        width: iconSize,
                        height: iconSize,
                        background: `linear-gradient(135deg, ${intg.bg}EE, ${intg.bg}AA)`,
                        boxShadow: `0 10px 40px ${intg.bg}88, inset 0 1px 0 rgba(255,255,255,0.2)`,
                        border: "1px solid rgba(255,255,255,0.1)",
                      }}
                    >
                      {intg.icon}
                    </div>
                  </motion.div>
                </motion.div>
              );
            })}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
