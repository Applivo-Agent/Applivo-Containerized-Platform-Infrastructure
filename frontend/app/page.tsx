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
  ChevronDown, Activity, ShieldCheck, Book,
  Mail, ExternalLink
} from "lucide-react";
import { siInstagram, siX } from "simple-icons";
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

function BrandIcon({ icon, className, color }: { icon: { path: string; hex: string }, className?: string, color?: string }) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className={className} fill={color ?? `#${icon.hex}`}>
      <path d={icon.path} />
    </svg>
  );
}

type ContactLink =
  | { kind: "email"; label: string; href: string; value: string }
  | { kind: "brand"; label: string; href: string; value: string; icon: { path: string; hex: string }; color?: string }
  | { kind: "linkedin"; label: string; href: string; value: string };

type DeveloperProfile = {
  title: string;
  name: string;
  role: string;
  photo: string;
  github: string;
  githubLabel: string;
  highlights: string[];
};

const DEVELOPER_PROFILES: DeveloperProfile[] = [
  {
    title: "Backend & Deployment",
    name: "Sudharsan",
    role: "APIs, workers, infra, and releases",
    photo: "/assets/IMG_0156.JPG",
    github: "",
    githubLabel: "",
    highlights: [
      "Python, FastAPI, SQLAlchemy (async), Alembic",
      "Postgres, Redis, Celery, Docker, VPS & Nginx",
      "Playwright automation and deployment ops",
    ],
  },
  {
    title: "Frontend Developer",
    name: "Visva",
    role: "UI systems, motion, and product polish",
    photo: "/assets/visva%20frontend.png",
    github: "",
    githubLabel: "",
    highlights: [
      "Next.js + TypeScript, Tailwind, Framer Motion",
      "Design -> implementation, responsive UI",
      "API integration and auth flows (JWT)",
    ],
  },
  {
    title: "QA Tester",
    name: "Ravi Shankar",
    role: "Regression checks, bug reports, and test coverage",
    photo: "/assets/ravifrontend.jpeg",
    github: "",
    githubLabel: "",
    highlights: [
      "Manual + API testing, container checks",
      "Log analysis (Celery, bots) and bug verification",
      "Test plans for apply-bot and login flows",
    ],
  },
];

function DeveloperCarouselSection() {
  const [activeDeveloper, setActiveDeveloper] = useState(0);
  const [direction, setDirection] = useState(1);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setDirection(1);
      setActiveDeveloper((current) => (current + 1) % DEVELOPER_PROFILES.length);
    }, 7000);

    return () => window.clearInterval(timer);
  }, []);

  const paginate = (nextDirection: number) => {
    setDirection(nextDirection);
    setActiveDeveloper((current) => {
      const nextIndex = (current + nextDirection + DEVELOPER_PROFILES.length) % DEVELOPER_PROFILES.length;
      return nextIndex;
    });
  };

  const activeProfile = DEVELOPER_PROFILES[activeDeveloper];

  const variants = {
    enter: (slideDirection: number) => ({
      x: slideDirection > 0 ? 120 : -120,
      opacity: 0,
      scale: 0.98,
      filter: "blur(6px)",
    }),
    center: {
      x: 0,
      opacity: 1,
      scale: 1,
      filter: "blur(0px)",
    },
    exit: (slideDirection: number) => ({
      x: slideDirection > 0 ? -120 : 120,
      opacity: 0,
      scale: 0.98,
      filter: "blur(6px)",
    }),
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-120px" }}
      transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
      className="rounded-[28px] border border-white/[0.06] bg-[#111111] p-4 md:p-6 shadow-[0_20px_60px_-30px_rgba(0,0,0,0.95)]"
    >
      <div className="flex items-center justify-between gap-4 mb-5 md:mb-6">
        <div>
          <p className="text-[11px] uppercase tracking-[0.28em] text-zinc-500 font-black">Team</p>
          <h3 className="mt-2 text-xl md:text-2xl font-bold text-white tracking-tight">Swipe through the team</h3>
        </div>
        <div className="hidden md:flex items-center gap-2 rounded-full border border-white/[0.06] bg-black/30 px-3 py-2 text-[11px] uppercase tracking-[0.22em] text-zinc-400 font-black">
          <span>{String(activeDeveloper + 1).padStart(2, "0")}</span>
          <span className="text-zinc-600">/</span>
          <span>{String(DEVELOPER_PROFILES.length).padStart(2, "0")}</span>
        </div>
      </div>

      <div className="relative overflow-hidden rounded-[30px] border border-white/[0.06] bg-black/30">
        <AnimatePresence initial={false} custom={direction} mode="wait">
          <motion.div
            key={activeProfile.title}
            custom={direction}
            variants={variants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
            drag="x"
            dragConstraints={{ left: 0, right: 0 }}
            dragElastic={0.16}
            onDragEnd={(_, info) => {
              if (info.offset.x < -90 || info.velocity.x < -450) {
                paginate(1);
              } else if (info.offset.x > 90 || info.velocity.x > 450) {
                paginate(-1);
              }
            }}
            className="touch-pan-y cursor-grab active:cursor-grabbing"
          >
            <div className="relative p-4 md:p-5">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(255,255,255,0.06),transparent_40%)] pointer-events-none" />
              <div className="relative grid gap-4 md:grid-cols-[180px_1fr] md:gap-5 items-start">
                <div className="relative mx-auto md:mx-0 w-[160px] h-[160px] md:w-[180px] md:h-[180px] rounded-[24px] overflow-hidden border border-white/[0.08] bg-[#0d0d0d] shadow-[0_12px_40px_-20px_rgba(0,0,0,0.6)]">
                  <Image
                    src={activeProfile.photo}
                    alt={activeProfile.name}
                    fill
                    className="object-cover"
                    sizes="(max-width: 768px) 180px, 220px"
                  />
                </div>

                <div className="space-y-4 text-center md:text-left">
                  <div>
                    <p className="text-[10px] uppercase tracking-[0.3em] text-zinc-500 font-black">{activeProfile.title}</p>
                    <h4 className="mt-2 text-xl md:text-3xl font-bold text-white tracking-tight">{activeProfile.name}</h4>
                    <p className="mt-2 text-sm md:text-sm text-[#A1A1AA] leading-6 max-w-2xl">{activeProfile.role}</p>
                  </div>

                  <div className="grid gap-2">
                    {activeProfile.highlights.map((highlight) => (
                      <div key={highlight} className="rounded-2xl border border-white/[0.06] bg-white/[0.03] px-3 py-2 text-sm text-[#D4D4D8] leading-6">
                        {highlight}
                      </div>
                    ))}
                  </div>

                  <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                    {activeProfile.github ? (
                      <a
                        href={activeProfile.github}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center justify-center gap-2 rounded-2xl border border-white/[0.08] bg-white/[0.04] px-4 py-3 text-sm font-semibold text-white transition-all hover:border-white/15 hover:bg-white/[0.07]"
                      >
                        <span className="text-[11px] uppercase tracking-[0.24em] text-zinc-400 font-black">GitHub</span>
                        <span className="text-zinc-500">·</span>
                        <span className="truncate">{activeProfile.githubLabel}</span>
                        <ExternalLink className="h-4 w-4 text-[#A1A1AA]" />
                      </a>
                    ) : (
                      <div className="inline-flex items-center gap-2 rounded-2xl border border-white/[0.04] bg-white/[0.02] px-4 py-3 text-sm text-zinc-500">Shared on request</div>
                    )}

                    <div className="flex items-center justify-center md:justify-end gap-2">
                      <button
                        type="button"
                        onClick={() => paginate(-1)}
                        aria-label="Previous developer"
                        className="flex h-10 w-10 items-center justify-center rounded-full border border-white/[0.08] bg-white/[0.04] text-white transition-all hover:bg-white/[0.08]"
                      >
                        <ChevronRight className="h-4 w-4 rotate-180" />
                      </button>
                      <button
                        type="button"
                        onClick={() => paginate(1)}
                        aria-label="Next developer"
                        className="flex h-10 w-10 items-center justify-center rounded-full border border-white/[0.08] bg-white/[0.04] text-white transition-all hover:bg-white/[0.08]"
                      >
                        <ChevronRight className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="mt-4 flex items-center justify-between gap-3">
        <p className="text-[10px] uppercase tracking-[0.22em] text-zinc-500 font-black">Swipe or use the arrows</p>
        <div className="flex items-center gap-2">
          {DEVELOPER_PROFILES.map((profile, index) => (
            <button
              key={profile.title}
              type="button"
              aria-label={`Show ${profile.title}`}
              onClick={() => {
                setDirection(index > activeDeveloper ? 1 : -1);
                setActiveDeveloper(index);
              }}
              className={`h-2.5 rounded-full transition-all ${index === activeDeveloper ? "w-8 bg-white" : "w-2.5 bg-white/20 hover:bg-white/35"}`}
            />
          ))}
        </div>
      </div>
    </motion.div>
  );
}

function DevelopersContactSection() {
  const contactLinks: ContactLink[] = [
    { kind: "email", label: "Email", href: "mailto:applivoagent@gmail.com", value: "applivoagent@gmail.com" },
    { kind: "brand", label: "X", href: "https://x.com/applivo_in", value: "x.com/applivo_in", icon: siX, color: "#f5f5f5" },
    { kind: "linkedin", label: "LinkedIn", href: "https://www.linkedin.com/company/applivo-agent/", value: "linkedin.com/company/applivo-agent" },
    { kind: "brand", label: "Instagram", href: "https://www.instagram.com/applivo.in/", value: "instagram.com/applivo.in", icon: siInstagram },
  ];

  return (
    <section id="contact" className="relative overflow-hidden border-t border-white/[0.04] bg-[#080808] py-20 md:py-28">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(255,255,255,0.06),transparent_40%)] pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto px-6">
        <div className="max-w-3xl mb-12 md:mb-16">
          <p className="text-[11px] uppercase tracking-[0.35em] text-zinc-500 font-black mb-4">Developers & Contact</p>
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight text-white leading-[1.05]">
            Built by a small team that cares about the details.
          </h2>
          <p className="mt-4 text-sm md:text-base text-[#888888] max-w-2xl leading-7">
            Meet the people behind Applivo and reach out directly for product questions, partnerships, or support.
          </p>
        </div>

        <div className="grid lg:grid-cols-[1.2fr_0.8fr] gap-6 md:gap-8">
          <DeveloperCarouselSection />

          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-120px" }}
            transition={{ duration: 0.6, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="rounded-[20px] border border-white/[0.06] bg-[#111111] p-4 md:p-6 shadow-[0_20px_60px_-30px_rgba(0,0,0,0.95)]"
          >
            <p className="text-[10px] uppercase tracking-[0.24em] text-zinc-500 font-black">Contact</p>
            <h3 className="mt-2 text-xl md:text-2xl font-bold text-white tracking-tight">Let&apos;s talk</h3>
            <p className="mt-2 text-sm text-[#A1A1AA] leading-6">
              For product demos, support, feedback, or collaborations, use any of the direct channels below.
            </p>

            <div className="mt-4 space-y-3">
              {contactLinks.map((item) => {
                return (
                  <a
                    key={item.label}
                    href={item.href}
                    target={item.href.startsWith("http") ? "_blank" : undefined}
                    rel={item.href.startsWith("http") ? "noopener noreferrer" : undefined}
                    className="group flex items-center justify-between gap-4 rounded-2xl border border-white/[0.06] bg-black/30 px-4 py-4 transition-all hover:border-white/12 hover:bg-white/[0.04]"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/[0.08] bg-white/[0.04] text-white">
                        {item.kind === "linkedin" ? (
                          <span className="text-[11px] font-black uppercase tracking-[0.08em]">in</span>
                        ) : item.kind === "email" ? (
                          <Mail className="h-4 w-4" />
                        ) : (
                          <BrandIcon icon={item.icon} color={item.color} className="h-4 w-4" />
                        )}
                      </span>
                      <div className="min-w-0">
                        <p className="text-xs uppercase tracking-[0.24em] text-zinc-500 font-black">{item.label}</p>
                        <p className="mt-1 truncate text-sm font-medium text-white">{item.value}</p>
                      </div>
                    </div>
                    <ExternalLink className="h-4 w-4 shrink-0 text-[#A1A1AA] transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
                  </a>
                );
              })}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
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

      <DevelopersContactSection />

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
