"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import {
  FileText, Bookmark, Briefcase, Search,
  Send, BarChart2, TrendingUp, ChevronRight,
  Zap, Star
} from "lucide-react";

/* ─── SECTION 1: AI Resume Builder Demo ─────────────────────────── */
const resumeTabs = [
  { id: "tailor", icon: <FileText className="w-4 h-4" />, label: "Tailor resume" },
  { id: "cover", icon: <Zap className="w-4 h-4" />, label: "Write cover letter" },
  { id: "match", icon: <Search className="w-4 h-4" />, label: "Match job skills" },
  { id: "optimize", icon: <Star className="w-4 h-4" />, label: "Optimize keywords" },
];

const resumePrompts: Record<string, string> = {
  tailor: "Tailor my resume for a Senior Product Manager role at a Series B startup...",
  cover: "Write a compelling cover letter for Google's AI Research team position...",
  match: "Analyze this job description and highlight my matching skills from my resume...",
  optimize: "Optimize my resume keywords for ATS systems targeting fintech roles...",
};

function ResumeBuilderCard() {
  const [activeTab, setActiveTab] = useState("tailor");
  const [displayedText, setDisplayedText] = useState("");
  const [isTyping, setIsTyping] = useState(true);

  useEffect(() => {
    const prompt = resumePrompts[activeTab];
    let i = 0;
    setDisplayedText("");
    setIsTyping(true);
    const timer = setInterval(() => {
      if (i < prompt.length) {
        setDisplayedText(prompt.slice(0, i + 1));
        i++;
      } else {
        setIsTyping(false);
        clearInterval(timer);
      }
    }, 28);
    return () => clearInterval(timer);
  }, [activeTab]);

  return (
    <div className="rounded-2xl bg-[#111111] border border-[#222222] overflow-hidden p-0 shadow-2xl">
      {/* Icon Tabs */}
      <div className="flex items-center gap-0 border-b border-[#1e1e1e] px-4 pt-4 pb-0">
        {resumeTabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex flex-col items-center gap-2 px-4 pb-4 pt-2 transition-all border-b-2 -mb-px ${
              activeTab === tab.id
                ? "border-[#ffffff] text-white"
                : "border-transparent text-[#555] hover:text-[#888]"
            }`}
          >
            <div className={`w-9 h-9 rounded-full flex items-center justify-center transition-colors ${
              activeTab === tab.id ? "bg-[#ffffff]/20" : "bg-[#1a1a1a]"
            }`}>
              {tab.icon}
            </div>
            <span className="text-[11px] font-medium whitespace-nowrap">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Input Area */}
      <div className="p-5">
        <div className="rounded-xl border border-[#2a2a2a] bg-[#0d0d0d] p-4 flex items-center gap-3 min-h-[72px]">
          <p className="text-[#888] text-[14px] flex-1 leading-relaxed">
            {displayedText}
            {isTyping && <span className="text-[#ffffff] ml-0.5 animate-pulse">|</span>}
          </p>
          <button className="ml-auto w-9 h-9 rounded-xl bg-[#ffffff] hover:bg-[#38bdf8] flex items-center justify-center transition-colors shrink-0 opacity-100 cursor-pointer">
            <Send className="w-4 h-4 text-[#0d0d0d]" />
          </button>
        </div>
      </div>
    </div>
  );
}

/* ─── SECTION 2: Job Match Score Demo ───────────────────────────── */
const jobs = [
  { title: "Senior Product Manager", company: "Stripe", match: 94, salary: "$180k", tag: "Remote" },
  { title: "AI Product Lead", company: "OpenAI", match: 87, salary: "$210k", tag: "Hybrid" },
  { title: "Growth PM", company: "Figma", match: 81, salary: "$160k", tag: "Onsite" },
];

function JobMatchCard() {
  const [hovered, setHovered] = useState<number | null>(null);

  return (
    <div className="rounded-2xl bg-[#111111] border border-[#222222] overflow-hidden shadow-2xl">
      <div className="px-5 pt-5 pb-2 border-b border-[#1e1e1e]">
        <p className="text-[11px] uppercase tracking-[0.1em] text-[#555] font-medium">AI Job Match Score</p>
      </div>
      <div className="divide-y divide-[#1a1a1a]">
        {jobs.map((job, i) => (
          <motion.div
            key={i}
            onHoverStart={() => setHovered(i)}
            onHoverEnd={() => setHovered(null)}
            className="flex items-center gap-4 px-5 py-4 transition-colors cursor-pointer"
            animate={{ backgroundColor: hovered === i ? "rgba(255,255,255,0.03)" : "rgba(255,255,255,0)" }}
          >
            <div className="w-9 h-9 rounded-lg bg-[#1a1a1a] border border-[#2a2a2a] flex items-center justify-center shrink-0">
              <Briefcase className="w-4 h-4 text-[#666]" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-[13px] font-semibold text-white truncate">{job.title}</p>
              <p className="text-[11px] text-[#555]">{job.company} · {job.salary}</p>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#1a1a1a] border border-[#2a2a2a] text-[#555]">
                {job.tag}
              </span>
              <div className="flex items-center gap-1.5">
                <div className="w-20 h-1.5 rounded-full bg-[#1a1a1a] overflow-hidden">
                  <motion.div
                    className="h-full rounded-full bg-gradient-to-r from-[#ffffff] to-[#38bdf8]"
                    initial={{ width: 0 }}
                    whileInView={{ width: `${job.match}%` }}
                    viewport={{ once: true }}
                    transition={{ duration: 1, delay: i * 0.1 }}
                  />
                </div>
                <span className="text-[12px] font-bold text-[#ffffff]">{job.match}%</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
      <div className="px-5 py-4">
        <button className="w-full flex items-center justify-center gap-2 text-[13px] text-[#ffffff] hover:text-[#38bdf8] transition-colors py-2 rounded-xl border border-[#2a2a2a] hover:border-[#ffffff]/40">
          View all matches <ChevronRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}

/* ─── SECTION 3: Application Analytics Demo ─────────────────────── */
const analyticsData = [
  { metric: "Applications Sent", value: "127", change: "+12", trend: "up" },
  { metric: "Interview Rate", value: "34%", change: "+8.2%", trend: "up" },
  { metric: "Avg. Response Time", value: "3.2d", change: "-1.1d", trend: "up" },
  { metric: "Offer Rate", value: "18%", change: "+4%", trend: "up" },
];

function AnalyticsCard() {
  return (
    <div className="rounded-2xl bg-[#111111] border border-[#222222] overflow-hidden shadow-2xl">
      <div className="px-5 pt-5 pb-2 border-b border-[#1e1e1e] flex items-center justify-between">
        <p className="text-[11px] uppercase tracking-[0.1em] text-[#555] font-medium">Campaign Analytics</p>
        <span className="text-[11px] text-[#ffffff] font-medium">Live ●</span>
      </div>
      <div className="grid grid-cols-2 divide-x divide-y divide-[#1a1a1a]">
        {analyticsData.map((item, i) => (
          <div key={i} className="p-5">
            <p className="text-[11px] text-[#555] mb-1">{item.metric}</p>
            <p className="text-[24px] font-bold text-white tracking-tight">{item.value}</p>
            <div className="flex items-center gap-1 mt-1">
              <TrendingUp className="w-3 h-3 text-[#22c55e]" />
              <span className="text-[11px] text-[#22c55e] font-medium">{item.change}</span>
            </div>
          </div>
        ))}
      </div>
      <div className="px-5 py-4">
        <div className="h-[3px] bg-[#1a1a1a] rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-[#ffffff] to-[#38bdf8] rounded-full"
            initial={{ width: "0%" }}
            whileInView={{ width: "68%" }}
            viewport={{ once: true }}
            transition={{ duration: 1.2 }}
          />
        </div>
        <div className="flex items-center justify-between mt-2">
          <span className="text-[11px] text-[#555]">Monthly goal</span>
          <span className="text-[11px] text-[#ffffff] font-medium">68% complete</span>
        </div>
      </div>
    </div>
  );
}

/* ─── FEATURE SECTION ROW ─────────────────────────────────────── */
interface FeatureRowProps {
  label: string;
  title: string;
  body: string;
  card: React.ReactNode;
  reverse?: boolean;
  delay?: number;
}

function FeatureRow({ label, title, body, card, reverse = false, delay = 0 }: FeatureRowProps) {
  return (
    <div className={`flex flex-col ${reverse ? "lg:flex-row-reverse" : "lg:flex-row"} items-center gap-12 lg:gap-20`}>
      {/* Card */}
      <motion.div
        initial={{ opacity: 0, x: reverse ? 40 : -40 }}
        whileInView={{ opacity: 1, x: 0 }}
        viewport={{ once: true, margin: "-80px" }}
        transition={{ duration: 0.7, delay, ease: [0.16, 1, 0.3, 1] }}
        className="w-full lg:w-[480px] shrink-0"
      >
        {card}
      </motion.div>

      {/* Text */}
      <motion.div
        initial={{ opacity: 0, x: reverse ? -40 : 40 }}
        whileInView={{ opacity: 1, x: 0 }}
        viewport={{ once: true, margin: "-80px" }}
        transition={{ duration: 0.7, delay: delay + 0.1, ease: [0.16, 1, 0.3, 1] }}
        className="flex-1 min-w-0"
      >
        <p className="text-[#ffffff] text-[13px] font-semibold mb-4 tracking-wide uppercase">{label}</p>
        <h3 className="text-[36px] md:text-[42px] font-bold text-white leading-[1.15] tracking-[-0.02em] mb-5">
          {title}
        </h3>
        <p className="text-[16px] text-[#888] leading-[1.7] max-w-[440px]">{body}</p>
        <motion.a
          href="/register"
          className="inline-flex items-center gap-2 mt-8 text-[14px] font-medium text-white hover:text-[#ffffff] transition-colors group"
          whileHover={{ x: 4 }}
          transition={{ type: "spring", stiffness: 400, damping: 25 }}
        >
          Get started free
          <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </motion.a>
      </motion.div>
    </div>
  );
}

/* ─── MAIN EXPORT ─────────────────────────────────────────────── */
export function BentoGrid() {
  return (
    <section className="bg-[#080808] px-6 relative z-10">
      <div className="max-w-6xl mx-auto flex flex-col gap-28">

        <FeatureRow
          label="AI Resume Intelligence"
          title="Build Resumes That Actually Get You Hired"
          body="Embark on a new era of job applications with Applivo's AI — tailor every resume to the exact role, auto-generate cover letters, and match your skills to job requirements in seconds."
          card={<ResumeBuilderCard />}
          delay={0}
        />

        <FeatureRow
          label="Smart Job Discovery"
          title="Find Roles That Match Your Ambitions"
          body="Applivo's AI scores every job against your profile, ranking opportunities by real match percentage. Stop applying blindly — apply strategically and land the interviews that actually count."
          card={<JobMatchCard />}
          reverse={true}
          delay={0.1}
        />

        <FeatureRow
          label="Performance Analytics"
          title="Track Every Application, Optimize Every Move"
          body="Elevate your job search with real-time analytics. Monitor response rates, interview conversion, and offer trends — then use the data to continuously sharpen your strategy."
          card={<AnalyticsCard />}
          delay={0.1}
        />

      </div>
    </section>
  );
}
