"use client";

import { motion } from "framer-motion";
import Image from "next/image";

const testimonials = [
  {
    name: "Ananya Rao",
    handle: "@ananya_ui",
    text: "Applivo has transformed how I apply to roles — it saves hours and gets me more interviews."
  },
  {
    name: "Arjun Mehta",
    handle: "@arjun_codes",
    text: "Every feature feels thoughtfully built for busy professionals in India and helps me apply at scale."
  },
  {
    name: "Priya Sharma",
    handle: "@priyadev",
    text: "The automated cover letters and tailored matches are spot on — best tool I've used for job hunting."
  },
  {
    name: "Rohit Verma",
    handle: "@rohit_tests",
    text: "It removed the stress of tracking dozens of applications so I can focus on interview prep."
  },
  {
    name: "Nisha Kapoor",
    handle: "@nisha_ops",
    text: "Applivo simplifies scraping and automation, making my career search far more efficient."
  }
];

export function TweetMarquee() {
  return (
    <section className="bg-[#050505] py-24 relative z-10 border-b border-zinc-900/50 overflow-hidden flex flex-col items-center">
      <div className="text-center mb-16 px-6">
        <h2 className="text-3xl font-medium tracking-tight text-white mb-4">
          Our Customers
        </h2>
        <p className="text-[#a1a1aa]">Powering the world&apos;s best professional careers.</p>
      </div>

      <div className="w-full relative flex items-center">
        {/* Gradients to mask edges */}
        <div className="absolute inset-y-0 left-0 w-32 bg-gradient-to-r from-[#050505] to-transparent z-10 pointer-events-none" />
        <div className="absolute inset-y-0 right-0 w-32 bg-gradient-to-l from-[#050505] to-transparent z-10 pointer-events-none" />
        
        <motion.div
          className="flex gap-6 px-6"
          animate={{ x: [0, -2000] }}
          transition={{
            repeat: Infinity,
            ease: "linear",
            duration: 40,
          }}
        >
          {/* Double array to ensure smooth seamless loop */}
          {[...testimonials, ...testimonials, ...testimonials].map((t, i) => (
            <div 
              key={i} 
              className="w-[340px] flex-shrink-0 bg-[#0a0a09] border border-[#1a1a1a] rounded-2xl p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-zinc-800 flex items-center justify-center text-white font-medium">
                  {t.name[0]}
                </div>
                <div>
                  <div className="text-white font-medium text-sm">{t.name}</div>
                  <div className="text-[#a1a1aa] text-xs">{t.handle}</div>
                </div>
              </div>
              <p className="text-zinc-300 text-sm leading-relaxed">
                &quot;{t.text}&quot;
              </p>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
