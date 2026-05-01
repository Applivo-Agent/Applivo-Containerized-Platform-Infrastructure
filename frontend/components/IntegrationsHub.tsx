"use client";
import { motion } from "framer-motion";

const integrations = [
  { name: "LinkedIn", color: "#0A66C2", x: 50, y: 5, initial: "in" },
  { name: "Indeed", color: "#003A9B", x: 82, y: 35, initial: "In" },
  { name: "Wellfound", color: "#2A2A2A", x: 72, y: 72, initial: "WF" },
  { name: "Telegram", color: "#26A5E4", x: 28, y: 72, initial: "TG" },
  { name: "Internshala", color: "#00A550", x: 18, y: 35, initial: "IS" },
  { name: "Naukri", color: "#FF7555", x: 50, y: 80, initial: "Na" },
];

export function IntegrationsHub() {
  return (
    <section className="py-32 px-6 relative overflow-hidden">
      {/* Background purple glow */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-[600px] h-[600px] rounded-full bg-white text-black/10 blur-[100px]" />
      </div>

      <div className="max-w-6xl mx-auto">
        {/* Stats Row */}
        <div className="grid md:grid-cols-2 gap-4 mb-8 max-w-2xl">
          <div className="bg-[#1c1c1e] border border-zinc-800 rounded-2xl p-6 shadow-md">
            <p className="text-sm text-zinc-500 font-medium mb-2">Connected job boards</p>
            <p className="text-4xl font-black text-white tracking-tight">50+</p>
          </div>
          <div className="bg-[#1c1c1e] border border-zinc-800 rounded-2xl p-6 shadow-md">
            <p className="text-sm text-zinc-500 font-medium mb-2">Applications automated</p>
            <p className="text-4xl font-black text-white tracking-tight">+100K</p>
          </div>
        </div>

        {/* Main Card */}
        <div className="bg-[#1c1c1e] border border-zinc-800 rounded-3xl p-8 md:p-12 relative overflow-hidden shadow-2xl">
          {/* Header */}
          <div className="mb-10">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-white text-black/20 border border-white/30 flex items-center justify-center">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-zinc-200">
                  <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" />
                  <rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" />
                </svg>
              </div>
              <h2 className="text-2xl font-black text-white tracking-tight">Integrations and connection hub</h2>
            </div>
            <p className="text-zinc-400 text-lg font-medium max-w-xl">
              One platform. 50+ job boards. Automatically synced, deduplicated, and ranked every 6 hours.
            </p>
          </div>

          {/* Arc Visualization */}
          <div className="relative h-[400px] w-full overflow-hidden">
            {/* Integration glow */}
            <div className="integration-glow absolute inset-0 pointer-events-none" />
            {/* Dot pattern */}
            <div className="dot-pattern absolute inset-0 pointer-events-none opacity-40" />

            {/* SVG Arc */}
            <svg
              className="absolute inset-0 w-full h-full"
              viewBox="0 0 800 400"
              preserveAspectRatio="xMidYMid meet"
            >
                {/* Main arc */}
                <path
                  d="M 80 380 Q 400 -50 720 380"
                  fill="none"
                  stroke="url(#arcGrad)"
                  strokeWidth="1.5"
                  opacity="0.6"
                />
                {/* Inner arc */}
                <path
                  d="M 160 380 Q 400 60 640 380"
                  fill="none"
                  stroke="url(#arcGrad)"
                  strokeWidth="1"
                  opacity="0.3"
                  strokeDasharray="6 4"
                />
                <defs>
                  <linearGradient id="arcGrad" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="rgba(124,58,237,0)" />
                    <stop offset="30%" stopColor="rgba(124,58,237,0.6)" />
                    <stop offset="50%" stopColor="rgba(168,85,247,0.8)" />
                    <stop offset="70%" stopColor="rgba(59,130,246,0.6)" />
                    <stop offset="100%" stopColor="rgba(59,130,246,0)" />
                  </linearGradient>
                </defs>

                {/* Connection lines to center */}
                {integrations.map((int, i) => {
                  const cx = (int.x / 100) * 800;
                  const cy = (int.y / 100) * 380;
                  return (
                    <motion.line
                      key={i}
                      x1={cx} y1={cy}
                      x2={400} y2={380}
                      stroke={int.color}
                      strokeWidth="1"
                      strokeOpacity="0.3"
                      initial={{ pathLength: 0, opacity: 0 }}
                      animate={{ pathLength: 1, opacity: 0.3 }}
                      transition={{ duration: 1.5, delay: i * 0.2, ease: "easeOut" }}
                    />
                  );
                })}
            </svg>

            {/* Center Node — Applivo */}
            <motion.div
              className="absolute z-20"
              style={{ left: "calc(50% - 32px)", bottom: "0px" }}
              animate={{ scale: [1, 1.05, 1] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            >
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-white/10 to-transparent flex items-center justify-center shadow-[0_0_40px_rgba(124,58,237,0.6)] border border-blue-400/30">
                <span className="text-white font-black text-xl">A</span>
              </div>
              <div className="absolute inset-0 rounded-2xl animate-ping bg-white text-black/20" style={{ animationDuration: "3s" }} />
            </motion.div>

            {/* Integration nodes */}
            {integrations.map((int, i) => (
              <motion.div
                key={int.name}
                className="absolute z-10"
                style={{
                  left: `calc(${int.x}% - 28px)`,
                  top: `calc(${int.y}% - 28px)`,
                }}
                initial={{ opacity: 0, scale: 0.5 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.3 + i * 0.15, type: "spring" }}
                whileHover={{ scale: 1.15, zIndex: 30 }}
              >
                <div
                  className="w-14 h-14 rounded-2xl flex items-center justify-center text-white font-black text-sm shadow-lg border border-white/10 relative overflow-hidden"
                  style={{ background: int.color }}
                >
                  <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent" />
                  <span className="relative z-10">{int.initial}</span>
                </div>
                <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 whitespace-nowrap text-[10px] font-bold text-zinc-500">
                  {int.name}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
