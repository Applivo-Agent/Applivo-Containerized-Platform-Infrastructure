"use client";

import { motion } from "framer-motion";

export function TopMarquee() {
  const text = "Our AI agents automate your entire job search at all times.";
  
  return (
    <div className="w-full overflow-hidden border-y border-zinc-800 bg-[#050505] py-5 relative flex items-center">
      {/* Left/Right Fade */}
      <div className="absolute inset-y-0 left-0 w-32 bg-gradient-to-r from-[#050505] to-transparent z-10" />
      <div className="absolute inset-y-0 right-0 w-32 bg-gradient-to-l from-[#050505] to-transparent z-10" />
      
      <motion.div
        className="flex whitespace-nowrap gap-16 text-zinc-300 font-semibold text-xl uppercase tracking-widest px-4"
        animate={{ x: [0, -1035] }}
        transition={{
          repeat: Infinity,
          ease: "linear",
          duration: 30, // Slow marquee
        }}
      >
        {/* We repeat the text multiple times to ensure a smooth scrolling loop */}
        {[...Array(6)].map((_, i) => (
          <span key={i} className="flex items-center gap-12">
            <span>{text}</span>
            <span className="text-zinc-700 mx-4">•</span>
          </span>
        ))}
      </motion.div>
    </div>
  );
}
