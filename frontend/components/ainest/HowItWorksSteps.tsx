"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";
import {
  FileText, Link2, Zap,
  BarChart2, Briefcase,
  User, Target,
  Clock, TrendingUp,
  Cpu, CheckCircle2, FileSearch, Share2, Brain, ShieldCheck, Globe, Bell
} from "lucide-react";

/* ─── STEP DEFINITIONS ─────────────────────────────────────── */
const steps = [
  {
    id: 1,
    label: "Describe",
    heading: "Set Up Your Profile",
    body: "Tell Applivo about your career goals using plain English. Upload your resume and set your target roles — no technical knowledge needed.",
    bullets: [
      { icon: <FileSearch className="w-5 h-5" />, text: "Smart Resume Parsing" },
      { icon: <Target className="w-5 h-5" />, text: "Target Role Configuration" },
      { icon: <Cpu className="w-5 h-5" />, text: "AI Preference Learning" },
    ],
    mockup: <UploadMockup />,
  },
  {
    id: 2,
    label: "Connect",
    heading: "Connect Your Tools",
    body: "Link the apps you already use with one click. Applivo handles all the technical setup and syncs your profiles across every board automatically.",
    bullets: [
      { icon: <ShieldCheck className="w-5 h-5" />, text: "One-Click Authentication" },
      { icon: <Share2 className="w-5 h-5" />, text: "5000+ Pre-Built Integrations" },
      { icon: <Brain className="w-5 h-5" />, text: "Auto-Mapping" },
    ],
    mockup: <ConnectMockup />,
  },
  {
    id: 3,
    label: "Deploy",
    heading: "Watch AI Apply For You",
    body: "Your AI agent starts applying immediately — 24/7. Monitor every application in real-time, track responses, and let Applivo handle follow-ups automatically.",
    bullets: [
      { icon: <Zap className="w-5 h-5" />, text: "Instant Autonomous Applying" },
      { icon: <BarChart2 className="w-5 h-5" />, text: "Real-Time Application Tracking" },
      { icon: <Bell className="w-5 h-5" />, text: "Smart Follow-Up Automation" },
    ],
    mockup: <ApplyMockup />,
  },
];

/* ─── SIDEBAR LAYOUT ────────────────────────────────────────── */
function SidebarLayout({ children, activeTab }: { children: React.ReactNode; activeTab: string }) {
  const menuItems = [
    { icon: <Briefcase className="w-3.5 h-3.5" />, label: "Agents" },
    { icon: <Zap className="w-3.5 h-3.5" />, label: "Workflows" },
    { icon: <Link2 className="w-3.5 h-3.5" />, label: "Integrations" },
    { icon: <BarChart2 className="w-3.5 h-3.5" />, label: "Analytics" },
  ];

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <div className="w-[155px] shrink-0 border-r border-white/5 p-4 flex flex-col gap-5">
        <div className="flex items-center gap-2 px-1 pt-1">
          <div className="w-5 h-5 rounded bg-indigo-500/80 flex items-center justify-center text-[10px] font-bold text-white shrink-0">
            A
          </div>
          <span className="text-white font-bold text-[12px] tracking-tight">Applivo.inc</span>
        </div>
        <div className="flex flex-col gap-0.5">
          <div className="px-2 mb-1.5 text-[10px] font-bold text-[#333] uppercase tracking-widest">Menu</div>
          {menuItems.map((item) => (
            <div
              key={item.label}
              className={`flex items-center gap-2 px-2.5 py-1.5 rounded-md text-[12px] font-medium transition-colors ${item.label === activeTab ? "bg-white/5 text-white" : "text-[#444]"
                }`}
            >
              {item.icon}
              {item.label}
            </div>
          ))}
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-hidden min-w-0">{children}</div>
    </div>
  );
}

/* ─── BROWSER CHROME WRAPPER ─────────────────────────────────
   Matches Kilo's top URL bar + dots exactly
────────────────────────────────────────────────────────────── */
function BrowserChrome({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col h-full">
      {/* URL bar row */}
      <div
        className="flex items-center gap-3 px-4 shrink-0 border-b border-white/5"
        style={{ height: "44px", background: "#0a0a0a" }}
      >
        {/* Globe icon */}
        <Globe className="w-3.5 h-3.5 text-[#444] shrink-0" />

        {/* URL pill */}
        <div
          className="flex items-center px-3 rounded-md text-[12px] text-[#555]"
          style={{ background: "#111", height: "28px", minWidth: "200px" }}
        >
          app.applivo.in
        </div>

        {/* Dots */}
        <div className="flex items-center gap-1.5 ml-2">
          {[0, 1, 2].map((i) => (
            <div key={i} className="w-1.5 h-1.5 rounded-full bg-[#333]" />
          ))}
        </div>
      </div>

      {/* App content */}
      <div className="flex-1 overflow-hidden min-h-0">{children}</div>
    </div>
  );
}

/* ─── MOCKUP PANELS ─────────────────────────────────────────── */

function UploadMockup() {
  return (
    <BrowserChrome>
      <SidebarLayout activeTab="Agents">
        <div className="flex flex-col gap-3.5 p-5 h-full overflow-hidden">
          {/* Header row */}
          <div className="flex items-center justify-between">
            <h4 className="text-white font-bold text-[15px]">Onboarding Flow</h4>
            <button className="bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-bold px-3 py-1.5 rounded-md transition-all">
              Run agent
            </button>
          </div>

          {/* Profile card */}
          <div className="flex items-center gap-3.5 bg-[#0f0f0f] border border-white/[0.07] rounded-xl p-3.5">
            <div className="w-10 h-10 rounded-full bg-[#1c1c1e] flex items-center justify-center shrink-0">
              <User className="w-5 h-5 text-[#888]" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white text-[14px] font-semibold">Alex Johnson</p>
              <p className="text-[#555] text-[12px]">Senior Product Manager · San Francisco</p>
            </div>
            <span className="text-[11px] bg-white/[0.07] text-[#aaa] border border-white/10 px-2.5 py-1 rounded-full shrink-0">
              Active
            </span>
          </div>

          {/* Resume upload */}
          <div className="border border-dashed border-white/20 rounded-xl p-4 flex items-center gap-3.5 bg-white/[0.03]">
            <div className="w-9 h-9 bg-white/10 rounded-lg flex items-center justify-center shrink-0">
              <FileText className="w-4 h-4 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white text-[13px] font-medium">Alex_Johnson_PM_Resume.pdf</p>
              <div className="flex items-center gap-2 mt-2">
                <div className="flex-1 h-1 bg-[#1a1a1a] rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-white rounded-full"
                    initial={{ width: "0%" }}
                    animate={{ width: "100%" }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                  />
                </div>
                <span className="text-[11px] text-[#444] shrink-0">100%</span>
              </div>
            </div>
            <CheckCircle2 className="w-4.5 h-4.5 text-white shrink-0" />
          </div>

          {/* Target roles */}
          <div className="bg-[#0f0f0f] border border-white/[0.07] rounded-xl p-4">
            <p className="text-[#444] text-[10px] uppercase tracking-widest mb-3">Target Roles</p>
            <div className="flex flex-wrap gap-2">
              {["Product Manager", "Growth PM", "Senior PM", "Head of Product"].map((role) => (
                <span
                  key={role}
                  className="text-[11px] bg-[#161616] border border-white/[0.07] text-[#777] px-3 py-1.5 rounded-full"
                >
                  {role}
                </span>
              ))}
            </div>
          </div>

          {/* AI parsing */}
          <div className="flex items-center gap-3 bg-[#0f0f0f] border border-white/[0.07] rounded-xl px-4 py-3">
            <Cpu className="w-4 h-4 text-white shrink-0" />
            <p className="text-[#555] text-[12px]">
              AI extracting <span className="text-white font-medium">24 skills</span> from your resume…
            </p>
            <div className="ml-auto flex gap-1">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className="w-1.5 h-1.5 bg-white rounded-full"
                  animate={{ opacity: [0.2, 1, 0.2] }}
                  transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                />
              ))}
            </div>
          </div>
        </div>
      </SidebarLayout>
    </BrowserChrome>
  );
}

function ConnectMockup() {
  const platforms = [
    { name: "LinkedIn", status: "Connected", icon: "in", jobs: "312 jobs" },
    { name: "Indeed", status: "Connected", icon: "id", jobs: "247 jobs" },
    { name: "Internshala", status: "Connect", icon: "IS", jobs: null },
    { name: "Glassdoor", status: "Connect", icon: "GD", jobs: null },
  ];

  return (
    <BrowserChrome>
      <SidebarLayout activeTab="Integrations">
        <div className="flex flex-col gap-3.5 p-5 h-full overflow-hidden">
          <h4 className="text-white font-bold text-[15px]">Connected Tools</h4>
          <div className="bg-[#0f0f0f] border border-white/[0.07] rounded-xl overflow-hidden">
            <div className="px-4 py-3 border-b border-white/[0.05] flex items-center justify-between">
              <p className="text-[#444] text-[10px] uppercase tracking-widest">Job Platform Integrations</p>
              <span className="text-[11px] text-white">4 available</span>
            </div>
            <div className="divide-y divide-white/[0.04]">
              {platforms.map((p) => (
                <div key={p.name} className="flex items-center gap-3.5 px-4 py-3.5">
                  <div className="w-9 h-9 rounded-xl bg-[#161616] border border-white/[0.07] flex items-center justify-center text-white text-[10px] font-bold shrink-0">
                    {p.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-white text-[13px] font-semibold">{p.name}</p>
                    {p.jobs && <p className="text-[11px] text-[#444]">Syncing {p.jobs}</p>}
                  </div>
                  <button
                    className={`text-[11px] font-semibold px-3 py-1.5 rounded-lg transition-colors shrink-0 ${p.status === "Connected"
                        ? "bg-white/[0.07] text-white border border-white/10"
                        : "bg-white/10 text-white border border-white/20 hover:bg-white/15"
                      }`}
                  >
                    {p.status === "Connected" ? "✓ Connected" : "Connect"}
                  </button>
                </div>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-3 bg-white/[0.04] border border-white/10 rounded-xl px-4 py-3">
            <Globe className="w-4 h-4 text-white shrink-0" />
            <p className="text-[#666] text-[12px]">
              <span className="text-white font-medium">2 platforms</span> connected ·{" "}
              <span className="text-white font-medium">559 jobs</span> synced and ready
            </p>
          </div>
        </div>
      </SidebarLayout>
    </BrowserChrome>
  );
}

function ApplyMockup() {
  const apps = [
    { title: "Senior Product Manager", company: "Stripe", status: "Applied", time: "2m ago" },
    { title: "Growth PM", company: "Notion", status: "Applied", time: "4m ago" },
    { title: "Product Lead", company: "Linear", status: "Interview 🎉", time: "1h ago" },
    { title: "Head of Product", company: "Vercel", status: "Applied", time: "8m ago" },
  ];

  return (
    <BrowserChrome>
      <SidebarLayout activeTab="Workflows">
        <div className="flex flex-col gap-3.5 p-5 h-full overflow-hidden">
          {/* Live status */}
          <div className="flex items-center justify-between bg-[#0f0f0f] border border-white/[0.07] rounded-xl px-4 py-3.5">
            <div className="flex items-center gap-2">
              <motion.div
                className="w-2 h-2 bg-green-400 rounded-full"
                animate={{ opacity: [1, 0.3, 1] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              />
              <p className="text-white text-[13px] font-semibold">AI Agent Active</p>
            </div>
            <p className="text-[#444] text-[12px]">127 applied today</p>
          </div>

          {/* Application feed */}
          <div className="bg-[#0f0f0f] border border-white/[0.07] rounded-xl overflow-hidden">
            <div className="px-4 py-3 border-b border-white/[0.05] flex items-center justify-between">
              <p className="text-[#444] text-[10px] uppercase tracking-widest">Live Applications</p>
              <p className="text-white text-[11px]">Applying…</p>
            </div>
            <div className="divide-y divide-white/[0.04]">
              {apps.map((app, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="flex items-center gap-3.5 px-4 py-3"
                >
                  <div className="w-8 h-8 rounded-lg bg-[#161616] border border-white/[0.06] flex items-center justify-center shrink-0">
                    <Briefcase className="w-3.5 h-3.5 text-[#444]" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-white text-[12px] font-medium truncate">{app.title}</p>
                    <p className="text-[#444] text-[11px]">{app.company}</p>
                  </div>
                  <div className="flex flex-col items-end gap-0.5 shrink-0">
                    <span className="text-[10px] font-semibold px-2.5 py-1 rounded-full bg-white/[0.07] text-white border border-white/10">
                      {app.status}
                    </span>
                    <span className="text-[#333] text-[10px]">{app.time}</span>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-2.5">
            {[
              { label: "Response", value: "34%", icon: <TrendingUp className="w-3.5 h-3.5 text-white" /> },
              { label: "Interviews", value: "12", icon: <CheckCircle2 className="w-3.5 h-3.5 text-white" /> },
              { label: "Pending", value: "38", icon: <Clock className="w-3.5 h-3.5 text-[#444]" /> },
            ].map((s) => (
              <div
                key={s.label}
                className="bg-[#0f0f0f] border border-white/[0.07] rounded-xl p-3 flex flex-col items-center text-center"
              >
                {s.icon}
                <p className="text-white text-[17px] font-bold mt-1">{s.value}</p>
                <p className="text-[#444] text-[10px] mt-0.5">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </SidebarLayout>
    </BrowserChrome>
  );
}

/* ─── MAIN COMPONENT ─────────────────────────────────────────── */
export function HowItWorksSteps() {
  const [active, setActive] = useState(0);
  const step = steps[active];

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setActive((current) => (current + 1) % steps.length);
    }, 3500);

    return () => window.clearTimeout(timer);
  }, [active]);

  return (
    <section
      className="relative bg-black overflow-hidden"
      style={{ minHeight: "100vh" }}
    >
      {/* ── LEFT COLUMN ──────────────────────────────────────────
          Width: ~42%, left padding: 80px, vertically centered     */}
      <div
        className="absolute top-0 left-0 bottom-0 flex flex-col justify-center z-10"
        style={{ width: "42%", paddingLeft: "80px", paddingRight: "32px" }}
      >
        {/* Step pills */}
        <div className="flex items-center gap-1 mb-8">
          {steps.map((s, i) => (
            <button
              key={s.id}
              onClick={() => setActive(i)}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-full text-[13px] font-semibold transition-all duration-200 ${active === i
                  ? "bg-white text-black"
                  : "text-[#444] bg-transparent hover:text-[#777]"
                }`}
            >
              <span className={`text-[11px] font-bold ${active === i ? "text-black" : "text-[#333]"}`}>
                {s.id}
              </span>
              {s.label}
            </button>
          ))}
        </div>

        {/* Animated text + bullets */}
        <AnimatePresence mode="wait">
          <motion.div
            key={active}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
          >
            {/* Heading */}
            <h2
              className="font-bold text-white leading-none mb-6"
              style={{
                fontSize: "clamp(44px, 4.5vw, 60px)",
                letterSpacing: "-0.03em",
                lineHeight: 1.02,
              }}
            >
              {step.heading}
            </h2>

            {/* Body */}
            <p
              className="mb-12"
              style={{
                fontSize: "16px",
                color: "#666",
                lineHeight: 1.6,
                maxWidth: "320px",
              }}
            >
              {step.body}
            </p>

            {/* Feature list */}
            <div className="flex flex-col" style={{ gap: "20px" }}>
              {step.bullets.map((b, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -6 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.07, duration: 0.25 }}
                  className="flex items-center"
                  style={{ gap: "14px" }}
                >
                  <div style={{ color: "#3a3a3a", flexShrink: 0 }}>{b.icon}</div>
                  <span style={{ fontSize: "15px", color: "#fff", fontWeight: 500 }}>
                    {b.text}
                  </span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* ── RIGHT PANEL ──────────────────────────────────────────
          - Starts at top:120px (just below nav), right:0, width:65%
          - NO left fade — left edge is crisp/sharp
          - ONLY bottom fade gradient dissolves into black
          - Mockup is wider than container so right side clips off viewport
          - No border, no shadow, no card wrapper               */}
      <div
        className="hidden lg:block absolute right-0 bottom-0 overflow-hidden"
        style={{ top: "120px", width: "55%" }}
      >
        {/* BOTTOM fade ONLY — transparent → black */}
        <div
          className="absolute inset-x-0 bottom-0 z-20 pointer-events-none"
          style={{
            height: "45%",
            background: "linear-gradient(to top, #000000 0%, #000000 15%, transparent 100%)",
          }}
        />

        {/* Mockup — wider than container so right edge clips off-screen like Kilo */}
        <AnimatePresence mode="wait">
          <motion.div
            key={active}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
            style={{ width: "115%", minHeight: "650px" }}
          >
            {step.mockup}
          </motion.div>
        </AnimatePresence>
      </div>
    </section>
  );
}