"use client";
import { useRef, useEffect } from "react";

interface Logo {
  name: string;
  initial: string;
  color: string;
}

const logos: Logo[] = [
  { name: "LinkedIn", initial: "in", color: "#0A66C2" },
  { name: "Indeed", initial: "In", color: "#003A9B" },
  { name: "Internshala", initial: "IS", color: "#00A550" },
  { name: "Wellfound", initial: "WF", color: "#2A2A2A" },
  { name: "Glassdoor", initial: "GD", color: "#0CAA41" },
  { name: "Naukri", initial: "Na", color: "#FF7555" },
  { name: "Monster", initial: "Mo", color: "#6E4299" },
  { name: "Shine", initial: "Sh", color: "#F47920" },
  { name: "Unstop", initial: "Un", color: "#7B2FF7" },
  { name: "HackerEarth", initial: "HE", color: "#3498DB" },
  { name: "AngelList", initial: "AL", color: "#000000" },
  { name: "Upwork", initial: "Up", color: "#14A800" },
];

function LogoPill({ logo }: { logo: Logo }) {
  return (
    <div className="flex items-center gap-3 px-6 py-3.5 rounded-full border border-zinc-800 bg-[#1c1c1e] hover:border-zinc-700 hover:bg-[#1c1c1e] transition-all duration-300 cursor-default whitespace-nowrap group mx-3 shadow-md">
      <div
        className="w-8 h-8 rounded-lg flex items-center justify-center text-white text-[11px] font-black shrink-0 shadow-sm"
        style={{ background: logo.color }}
      >
        {logo.initial}
      </div>
      <span className="text-sm font-semibold text-zinc-400 group-hover:text-zinc-200 transition-colors">
        {logo.name}
      </span>
    </div>
  );
}

export function InfiniteMarquee() {
  const doubled = [...logos, ...logos]; // duplicate for seamless loop

  return (
    <div className="py-16 border-y border-zinc-900 overflow-hidden bg-[#000000]">
      <div className="text-center mb-10 px-6">
        <p className="text-sm font-bold text-zinc-500 uppercase tracking-[0.2em]">
          Scraping 50+ job boards in real-time
        </p>
        <p className="text-xs text-zinc-600 mt-1 font-medium">
          Every 6 hours. Deduplicated. Ranked by your match score.
        </p>
      </div>

      <div className="marquee-container">
        <div className="flex animate-marquee" style={{ width: "max-content" }}>
          {doubled.map((logo, i) => (
            <LogoPill key={`a-${i}`} logo={logo} />
          ))}
          {doubled.map((logo, i) => (
            <LogoPill key={`b-${i}`} logo={logo} />
          ))}
        </div>
      </div>
    </div>
  );
}
