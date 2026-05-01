"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Image from "next/image";
import { Terminal, Link2, Rocket, CheckCircle2, Brain, Bot, Zap } from "lucide-react";

const steps = [
  {
    number: 1,
    label: "Describe",
    icon: Terminal,
    title: "Describe Your Workflow",
    subtitle: "Tell Applivo what you want to automate using plain English. No technical knowledge needed.",
    bullets: [
      { icon: Brain, text: "AI-powered profile analysis" },
      { icon: CheckCircle2, text: "Smart job matching criteria" },
      { icon: Terminal, text: "Natural language setup" },
    ],
    image: "/workflow-profile.png",
    color: "rgba(124, 58, 237, 0.12)",
    borderColor: "rgba(124, 58, 237, 0.3)",
  },
  {
    number: 2,
    label: "Connect",
    icon: Link2,
    title: "Connect Your Accounts",
    subtitle: "Securely link your job portals once. Encrypted session management with zero credential storage.",
    bullets: [
      { icon: Link2, text: "One-time secure connection" },
      { icon: CheckCircle2, text: "AES-256 session encryption" },
      { icon: Zap, text: "Multi-portal support" },
    ],
    image: "/workflow-connect.png",
    color: "rgba(59, 130, 246, 0.12)",
    borderColor: "rgba(59, 130, 246, 0.3)",
  },
  {
    number: 3,
    label: "Deploy",
    icon: Rocket,
    title: "Approve & Deploy",
    subtitle: "Get Telegram notifications for every match. One tap to approve. Playwright handles the rest automatically.",
    bullets: [
      { icon: Bot, text: "Playwright auto-fill agent" },
      { icon: CheckCircle2, text: "Telegram approval gates" },
      { icon: Zap, text: "Real-time status tracking" },
    ],
    image: "/workflow-approve.png",
    color: "rgba(16, 185, 129, 0.12)",
    borderColor: "rgba(16, 185, 129, 0.3)",
  },
];

export function WorkflowTabs() {
  const [active, setActive] = useState(0);
  const step = steps[active];

  return (
    <section id="workflow" className="py-32 px-6 relative bg-[#000000]">
      {/* Background gradient */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/2 right-0 w-[800px] h-[800px] rounded-full bg-white text-black/5 blur-[120px]" />
      </div>

      <div className="max-w-7xl mx-auto relative">
        <div className="grid lg:grid-cols-12 gap-16 items-start">
          {/* Left: Tab list */}
          <div className="lg:col-span-5 relative z-10 pt-10">
            {/* Step pills - Vertical Stack for Kiloagent style */}
            <div className="flex flex-row lg:flex-col gap-4 mb-16 overflow-x-auto pb-4 lg:pb-0 scrollbar-hide">
              {steps.map((s, i) => (
                <button
                  key={i}
                  onClick={() => setActive(i)}
                  className={`flex items-center gap-4 px-6 py-4 rounded-2xl text-left font-bold transition-all duration-300 w-full min-w-[200px] border ${
                    active === i
                      ? "bg-[#1c1c1e] border-zinc-800 text-white shadow-[0_8px_30px_rgb(0,0,0,0.4)]"
                      : "bg-transparent border-transparent text-zinc-600 hover:text-zinc-300 hover:bg-[#0a0a09]"
                  }`}
                >
                  <span className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-black shrink-0 ${active === i ? "bg-[#2563eb] text-white" : "bg-zinc-900 border border-zinc-800 text-zinc-500"}`}>
                    {s.number}
                  </span>
                  <span className="text-lg whitespace-nowrap">{s.label}</span>
                </button>
              ))}
            </div>

            <AnimatePresence mode="wait">
              <motion.div
                key={active}
                initial={{ opacity: 0, x: -16 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -16 }}
                transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
                className="pl-4 border-l border-zinc-800 ml-4 max-w-sm"
              >
                <h2 className="text-4xl md:text-5xl font-sans tracking-tight text-white leading-[1.05] mb-4">
                  {step.title}
                </h2>
                <p className="text-xl text-zinc-400 font-medium leading-relaxed mb-10 max-w-md">
                  {step.subtitle}
                </p>

                <div className="space-y-4">
                  {step.bullets.map((b, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -12 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.1 }}
                      className="flex items-center gap-3 group"
                    >
                      <div className="w-6 h-6 rounded-md flex items-center justify-center shrink-0">
                        <CheckCircle2 className="w-5 h-5 text-zinc-500 group-hover:text-zinc-300 transition-colors" />
                      </div>
                      <span className="text-zinc-400 font-sans text-base">{b.text}</span>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Right: Dashboard mockup */}
          <div className="lg:col-span-7 relative flex justify-end">
            <AnimatePresence mode="wait">
              <motion.div
                key={active}
                initial={{ opacity: 0, scale: 0.96, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.96, y: -10 }}
                transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                className="relative"
              >
                <div
                  className="rounded-[24px] overflow-hidden border border-zinc-800 bg-[#1c1c1e] shadow-2xl p-2 pb-0 w-full"
                >
                  {/* Browser chrome Kiloagent style */}
                  <div className="flex items-center gap-3 px-4 py-3 bg-[#1c1c1e]">
                    <div className="flex gap-2">
                       <div className="w-3 h-3 rounded-full bg-zinc-800" />
                       <div className="w-3 h-3 rounded-full bg-zinc-800" />
                       <div className="w-3 h-3 rounded-full bg-zinc-800" />
                    </div>
                  </div>
                  {/* Screenshot */}
                  <div className="bg-[#1c1c1e] relative overflow-hidden rounded-t-[16px] border border-zinc-800 border-b-0" style={{ minHeight: 400 }}>
                    <Image
                      src={step.image}
                      alt={step.title}
                      width={700}
                      height={500}
                      className="w-full h-auto object-cover mockup-fade-bottom"
                      priority
                    />
                  </div>
                </div>

                {/* Floating glow orb */}
                <div
                  className="absolute -inset-8 rounded-3xl pointer-events-none"
                  style={{ background: `radial-gradient(ellipse at center, ${step.color} 0%, transparent 70%)` }}
                />
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>
    </section>
  );
}
