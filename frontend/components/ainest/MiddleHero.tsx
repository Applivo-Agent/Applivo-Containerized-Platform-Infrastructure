"use client";

import { motion } from "framer-motion";
import { Zap, LayoutTemplate, Bookmark, Smartphone } from "lucide-react";

// ── Job platform & integration logos — AiNest style: small SVG icon + name ──
const Platforms = [
  {
    name: "LinkedIn",
    icon: (
      <svg viewBox="0 0 24 24" fill="currentColor" className="w-[18px] h-[18px] shrink-0">
        <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z" />
        <rect x="2" y="9" width="4" height="12" />
        <circle cx="4" cy="4" r="2" />
      </svg>
    )
  },
  {
    name: "Indeed",
    icon: (
      <svg viewBox="0 0 24 24" fill="currentColor" className="w-[18px] h-[18px] shrink-0">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z" />
      </svg>
    )
  },
  {
    name: "Glassdoor",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="w-[18px] h-[18px] shrink-0">
        <circle cx="12" cy="12" r="10" />
        <path d="M8 12h8M12 8v8" strokeLinecap="round" />
      </svg>
    )
  },
  {
    name: "Greenhouse",
    icon: (
      <svg viewBox="0 0 24 24" fill="currentColor" className="w-[18px] h-[18px] shrink-0">
        <path d="M12 2l2 7h7l-5.5 4 2 7L12 16l-5.5 4 2-7L3 9h7z" />
      </svg>
    )
  },
  {
    name: "Lever",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-[18px] h-[18px] shrink-0">
        <path d="M4 6h16M4 12h10M4 18h6" strokeLinecap="round" />
      </svg>
    )
  },
  {
    name: "Workday",
    icon: (
      <svg viewBox="0 0 24 24" fill="currentColor" className="w-[18px] h-[18px] shrink-0">
        <path d="M12 2a10 10 0 100 20A10 10 0 0012 2zm0 4a2 2 0 110 4 2 2 0 010-4zm0 10c-2.67 0-5.33-1.33-6-2 .67-1.33 3.33-2 6-2s5.33.67 6 2c-.67.67-3.33 2-6 2z" />
      </svg>
    )
  },
  {
    name: "AngelList",
    icon: (
      <svg viewBox="0 0 24 24" fill="currentColor" className="w-[18px] h-[18px] shrink-0">
        <path d="M12 2L8 9H2l5 4-2 7 7-4 7 4-2-7 5-4h-6z" />
      </svg>
    )
  },
  {
    name: "Wellfound",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-[18px] h-[18px] shrink-0">
        <polyline points="20 6 12 14 8 10 4 14" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    )
  },
];

export function MiddleHero() {
  const marqueeItems = [...Platforms, ...Platforms, ...Platforms];

  return (
    <section className="bg-[#080808] pt-16 pb-20 md:pt-24 md:pb-32 relative overflow-hidden flex flex-col items-center z-10">

      {/* ── AiNest-style centered header text ── */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="text-center mb-10 z-20 px-6"
      >
        <p className="text-white text-[15px] font-medium mb-1">
          Powering ambitious job seekers worldwide.
        </p>
        <p className="text-[#555] text-[14px]">
          From fresh graduates to senior executives — all in one intelligent platform.
        </p>
      </motion.div>

      {/* ── Logo Marquee ── single smooth-scrolling row ── */}
      <div
        className="w-full relative flex items-center mb-0 z-20 overflow-hidden"
        style={{
          maskImage: 'linear-gradient(to right, transparent 0%, black 12%, black 88%, transparent 100%)',
          WebkitMaskImage: 'linear-gradient(to right, transparent 0%, black 12%, black 88%, transparent 100%)'
        }}
      >
        <motion.div
          className="flex gap-16 px-8 items-center"
          animate={{ x: [0, -1400] }}
          transition={{
            repeat: Infinity,
            ease: "linear",
            duration: 30,
            repeatType: "loop"
          }}
          style={{ willChange: 'transform' }}
        >
          {marqueeItems.map((platform, i) => (
            <div
              key={i}
              className="flex items-center gap-3 text-[#5a5a5a] hover:text-[#bbb] font-semibold text-[20px] tracking-tight shrink-0 select-none transition-colors duration-300 cursor-default"
            >
              <span className="text-[#4a4a4a] flex-shrink-0 [&>svg]:w-6 [&>svg]:h-6">{platform.icon}</span>
              {platform.name}
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
