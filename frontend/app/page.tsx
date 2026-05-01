"use client";
import Link from "next/link";
import Image from "next/image";
import { NavBar } from "@/components/NavBar";
import { motion, useScroll, useTransform, AnimatePresence } from "framer-motion";
import { useEffect, useState, useRef, useMemo } from "react";
import {
  Zap, Brain, ChevronRight, Check,
  Bot, Search, FileText, Send, Bell, BarChart2,
  ArrowRight, Globe, Sparkles, Shield, Target,
  MessageSquare, Star, TrendingUp, Loader2,
  ChevronDown, Activity, ShieldCheck, Book
} from "lucide-react";
import { PLAN_FEATURES, PLAN_PRICES } from "@/lib/subscription";
import dynamic from "next/dynamic";

const KiloagentBackground = dynamic(() => import("@/components/KiloagentBackground").then(m => ({ default: m.KiloagentBackground })), { ssr: false });
import { MiddleHero } from "@/components/ainest/MiddleHero";
import { WorkflowBento } from "@/components/ainest/WorkflowBento";
import { SecondaryBento } from "@/components/ainest/SecondaryBento";
import { BentoGrid } from "@/components/ainest/BentoGrid";
import { IntegrationsHub } from "@/components/ainest/IntegrationsHub";
import { HowItWorksSteps } from "@/components/ainest/HowItWorksSteps";
import { AppFeaturesGrid } from "@/components/ainest/AppFeaturesGrid";
import { TweetMarquee } from "@/components/ainest/TweetMarquee";
import { SimplePricing as Pricing } from "@/components/ainest/Pricing";


/* ─── HERO MOCKUP ─────────────────────────────────────────── */

function HeroMockup() {
  const [text, setText] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);
  const [loopNum, setLoopNum] = useState(0);
  const [typingSpeed, setTypingSpeed] = useState(100);

  const messages = [
    "Answer customer questions from our help docs...",
    "Analyze my resume for Google's SWE role...",
    "Find AI developer jobs in San Francisco...",
    "Apply for 10 high-match jobs automatically..."
  ];

  useEffect(() => {
    const handleType = () => {
      const i = loopNum % messages.length;
      const fullText = messages[i];

      setText(isDeleting
        ? fullText.substring(0, text.length - 1)
        : fullText.substring(0, text.length + 1)
      );

      setTypingSpeed(isDeleting ? 40 : 80);

      if (!isDeleting && text === fullText) {
        setTimeout(() => setIsDeleting(true), 2000);
      } else if (isDeleting && text === "") {
        setIsDeleting(false);
        setLoopNum(loopNum + 1);
      }
    };

    const timer = setTimeout(handleType, typingSpeed);
    return () => clearTimeout(timer);
  }, [text, isDeleting, loopNum, typingSpeed]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 40, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 1, delay: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className="relative mt-24 max-w-[1100px] mx-auto w-full px-6 lg:px-0"
    >
      {/* Floating Chat Input (Kilo Style rigidly centered) */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 1.2, duration: 0.5, type: "spring" }}
        className="absolute z-30 left-0 right-0 mx-auto -top-12 w-full max-w-md px-6 md:px-0"
      >
        <div className="bg-[#1c1c1e]/95 backdrop-blur-xl border border-[#262626] rounded-2xl p-4 shadow-[0_40px_80px_-20px_rgba(0,0,0,1)] flex flex-col">
          {/* Top text area */}
          <div className="w-full text-left pl-1 min-h-[20px]">
            <p className="text-[#f4f4f5] text-sm font-sans tracking-tight">
              {text}<span className="inline-block w-[2px] h-[16px] bg-[#3b82f6] ml-1 align-middle animate-[pulse_0.8s_infinite]" />
            </p>
          </div>

          {/* Bottom actions row */}
          <div className="flex items-center justify-between mt-4">
            <div className="flex items-center gap-1.5 bg-[#141414] rounded-xl p-1 border border-[#222]">
              <button className="p-1.5 rounded-lg hover:bg-zinc-800 transition-colors text-zinc-500">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48" /></svg>
              </button>
              <button className="p-1.5 rounded-lg hover:bg-zinc-800 transition-colors text-zinc-500">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3" /><path d="M3 5V19A9 3 0 0 0 21 19V5" /><path d="M3 12A9 3 0 0 0 21 12" /></svg>
              </button>
            </div>

            <button className="w-9 h-9 rounded-xl bg-[#f4f4f5] hover:bg-white flex items-center justify-center transition-all shadow-lg active:scale-95 group">
              <Send className="w-4 h-4 text-black shrink-0 transition-transform group-hover:translate-x-0.5" strokeWidth={3} />
            </button>
          </div>
        </div>
      </motion.div>


      {/* Browser chrome */}
      <div className="relative w-full rounded-t-[20px] overflow-hidden border border-[#222222] bg-[#050505] shadow-[0_40px_120px_-20px_rgba(0,0,0,0.8)] z-20 [mask-image:linear-gradient(to_bottom,black_50%,transparent_100%)]">
        {/* Title bar tightly matched to Kiloagent */}
        <div className="flex items-center justify-between px-4 py-3 bg-[#050505] border-b border-[#1a1a1a]">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 bg-[#121212] border border-[#222] rounded-full pl-3 pr-4 py-1.5 min-w-[200px]">
              <Globe className="w-3.5 h-3.5 text-[#52525b]" />
              <div className="text-[#71717a] text-[13px] font-sans tracking-wide">
                https://app.applivo.in/
              </div>
              <div className="ml-auto text-[#3f3f46]">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M12 5v14M5 12h14" /></svg>
              </div>
            </div>
          </div>

          <div className="flex gap-2 mr-2">
            <div className="w-[10px] h-[10px] rounded-full bg-[#262626]" />
            <div className="w-[10px] h-[10px] rounded-full bg-[#262626]" />
            <div className="w-[10px] h-[10px] rounded-full bg-[#262626]" />

          </div>
        </div>

        {/* Dashboard preview correctly seated */}
        <div className="bg-[#050505] relative overflow-hidden">
          <Image
            src="/dashboard-screenshot.png?v=latest"
            alt="Applivo Dashboard"
            width={1600}
            height={900}
            className="w-full h-auto mt-0 border-x border-[#222] rounded-b-xl shadow-2xl"
            priority
            unoptimized
          />


          <div className="absolute inset-x-0 bottom-0 h-[400px] bg-gradient-to-t from-[#000] via-[#000]/90 to-transparent pointer-events-none z-20" />
        </div>
      </div>
    </motion.div>
  );
}

/* ─── FOOTER ──────────────────────────────────────────────── */
function Footer() {
  return (
    <footer className="border-t border-white/6 py-12 px-6">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
          <Image src="/logo.png" alt="Applivo" width={28} height={28} className="rounded-lg" />
          <span className="text-white font-extrabold tracking-tight text-[15px]">Applivo</span>
        </Link>
        <span className="text-zinc-700 mx-2 hidden md:block">·</span>
        <span className="text-zinc-600 text-sm">Built with precision © 2026</span>
      </div>
    </footer>
  );
}

/* ─── MAIN PAGE ───────────────────────────────────────────── */
export default function LandingPage() {
  const isLoggedIn = useMemo(() => {
    if (typeof window === "undefined") return false;
    return Boolean(localStorage.getItem("applivo_token"));
  }, []);

  return (
    <div className="min-h-screen bg-[#000000] text-white selection:bg-white/20">
      <NavBar />

      {/* ── HERO ─────────────────────────────────────────── */}
      <section className="relative min-h-screen flex flex-col items-center justify-center pt-16 pb-8 px-6 overflow-hidden bg-[#0a0a0a]">
        {/* Matrix ASCII Rain Background */}
        <KiloagentBackground />

        <div className="relative z-20 w-full max-w-5xl mx-auto text-center mt-8">
          <motion.h1
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.1 }}
            className="text-5xl lg:text-6xl font-semibold tracking-tight leading-[1.05] mt-4 text-center flex flex-col items-center max-w-2xl mx-auto"
          >
            <span className="text-[#888888] block">Land Your Dream Job</span>
            <span className="text-white font-semibold">With AI Agents</span>
          </motion.h1>

          {/* Subtitle - Kiloagent Style */}
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="text-sm lg:text-base font-sans max-w-xl mx-auto mt-4 leading-relaxed text-[#919191] text-center"
          >
            Applivo automates the job application process by matching opportunities, generating applications, and submitting them automatically.
          </motion.p>

          {/* CTA buttons - Kiloagent Style */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="flex flex-wrap justify-center items-center gap-3 mt-5"
          >
            <Link
              href={isLoggedIn ? "/dashboard" : "/register"}
              className="h-11 px-6 bg-white hover:bg-zinc-100 text-black font-extrabold text-sm rounded-2xl inline-flex items-center justify-center transition-all duration-200 shadow-[0_0_20px_rgba(255,255,255,0.3)] active:scale-95"
            >
              Deploy Agent
            </Link>
            <Link
              href="/#features"
              className="h-11 px-6 bg-[#1c1c1e] border border-white/5 hover:bg-[#252528] text-zinc-300 font-semibold text-sm rounded-2xl inline-flex items-center justify-center transition-all duration-200 active:scale-95 shadow-md"
            >
              Learn more
            </Link>
          </motion.div>

          {/* Dashboard mockup (Kiloagent overlay style) */}
          <HeroMockup />

        </div>
      </section>

      <MiddleHero />

      <div id="workflow" className="pt-20 md:pt-32 pb-12 md:pb-24">
        <div className="max-w-4xl mx-auto text-center px-6 mb-10 md:mb-12 relative z-10">
          <h2 className="text-[2.25rem] md:text-[3.25rem] font-bold text-white tracking-tighter mb-4 leading-[1.1]">Automate Your Job Search — End to End.</h2>
          <p className="text-[17px] text-[#888888] max-w-2xl mx-auto font-medium leading-[1.6]">Connect your accounts, discover matching roles, and let AI apply to opportunities automatically — saving hours of manual effort every day.</p>
        </div>
        <WorkflowBento />

        {/* Kiloagent UI Flow restored */}
        <div className="mt-16 md:mt-24">
          <HowItWorksSteps />
        </div>
      </div>

      <div id="features" className="py-8 md:py-16 relative mt-[-20px]">
        <div className="max-w-4xl mx-auto text-center px-6 mb-10 relative z-10">
          <h2 className="text-[2.25rem] md:text-[3.25rem] font-bold text-white tracking-tighter mb-4 leading-[1.1]">Everything you need to scale.</h2>
          <p className="text-[17px] text-[#888888] max-w-2xl mx-auto font-medium leading-[1.6]">A massively scalable ecosystem that natively handles deployment, tracking, synchronization, and security.</p>
        </div>
        <SecondaryBento />

        <div className="mt-24 md:mt-32 max-w-4xl mx-auto text-center px-6 mb-12 relative z-10">
          <h2 className="text-[2.25rem] md:text-[3.25rem] font-bold text-white tracking-tighter mb-4 leading-[1.1]">Unleash your potential.</h2>
          <p className="text-[17px] text-[#888888] max-w-2xl mx-auto font-medium leading-[1.6]">Advanced career intelligence and analytics built directly into your workflow.</p>
        </div>
        <BentoGrid />
      </div>

      <div id="integrations" className="py-8 md:py-16 relative mt-[-20px]">
        <IntegrationsHub />
      </div>

      <div className="py-4 md:py-12">
        <TweetMarquee />
      </div>

      <div id="pricing">
        <Pricing />
      </div>

      {/* ── GIANT BACKGROUND LOGO ───────────────────────────── */}
      <section className="relative w-full bg-[#080808] pt-12 pb-4 md:pt-20 md:pb-6 flex justify-center items-center overflow-hidden z-0 border-t border-white/[0.02]">

        {/* Massive Text & Logo Container */}
        <div className="relative flex items-center justify-center gap-6 md:gap-8 pointer-events-none select-none opacity-90">

          {/* Logo Box */}
          <div className="w-[120px] h-[120px] md:w-[220px] md:h-[220px] bg-gradient-to-br from-[#2a2a2a] to-[#111111] rounded-[24px] md:rounded-[48px] flex items-center justify-center shadow-[inset_0_2px_10px_rgba(255,255,255,0.03)] overflow-hidden">
            <img src="/logo.png" alt="Applivo Logo" className="w-[80px] h-[80px] md:w-[150px] md:h-[150px] object-contain opacity-50 grayscale brightness-200" />
          </div>

          {/* Typography */}
          <h1 className="text-[120px] md:text-[260px] font-bold tracking-tighter leading-none bg-clip-text text-transparent bg-gradient-to-b from-[#2d2d2d] via-[#1a1a1a] to-[#080808]">Applivo</h1>

        </div>

        {/* Fading gradients to blend it into the background seamlessly */}
        <div className="absolute inset-0 bg-gradient-to-t from-[#080808] via-transparent to-[#080808] pointer-events-none" />
        <div className="absolute inset-0 bg-gradient-to-r from-[#080808] via-transparent to-[#080808] pointer-events-none opacity-80" />
      </section>

      {/* ── FOOTER ───────────────────────────────────────── */}
      <Footer />
    </div>
  );
}
