"use client";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Zap, Brain, Shield, ChevronRight, Check,
  Bot, Search, FileText, Send, Bell, BarChart2,
  Star, ArrowRight, Sparkles, Globe,
} from "lucide-react";
import { PLAN_FEATURES, PLAN_PRICES } from "@/lib/subscription";

const features = [
  {
    icon: Search,
    title: "Intelligent Job Scraping",
    desc: "Scrapes Internshala, LinkedIn, Indeed, and Wellfound every 6 hours. Deduplicates, cleans, and stores every listing in PostgreSQL.",
    color: "from-blue-500 to-cyan-500",
  },
  {
    icon: Brain,
    title: "Dual-Model AI Scoring",
    desc: "LLaMA-70B deep-analyses every job against your profile. Get a 0–100 match score, skill gap breakdown, and AI recommendation.",
    color: "from-purple-500 to-violet-500",
  },
  {
    icon: FileText,
    title: "ATS-Optimised Resumes",
    desc: "Generates tailored resumes with injected keywords across 6 LaTeX templates. WeasyPrint PDF output, Overleaf compatible.",
    color: "from-emerald-500 to-teal-500",
  },
  {
    icon: Bot,
    title: "Playwright Auto-Apply",
    desc: "Browser agent handles form fill, multi-step flows, OTP detection, and screening questions — across 6 ATS platforms.",
    color: "from-orange-500 to-amber-500",
  },
  {
    icon: Bell,
    title: "Telegram Approval Gate",
    desc: "Every application dispatches a Telegram message with inline approve/skip buttons. No bot applies without your explicit permission.",
    color: "from-sky-500 to-blue-500",
  },
  {
    icon: BarChart2,
    title: "Full Analytics Suite",
    desc: "Application funnel, response rates, resume performance rankings, skill gap analysis, and market salary trends.",
    color: "from-rose-500 to-pink-500",
  },
];

const stats = [
  { value: "500", label: "Applications / Day", suffix: "+" },
  { value: "6", label: "Job Platforms", suffix: "" },
  { value: "6", label: "LaTeX Templates", suffix: "" },
  { value: "100", label: "Match Score", suffix: "/100" },
];

const plans = [
  {
    tier: "starter" as const,
    label: "Starter",
    popular: false,
    color: "border-zinc-700",
    btnClass: "bg-zinc-700 hover:bg-zinc-600 text-white",
    badge: "",
  },
  {
    tier: "pro" as const,
    label: "Pro",
    popular: true,
    color: "border-brand-purple glow-border-purple",
    btnClass: "bg-brand-purple hover:bg-brand-purple/90 text-white",
    badge: "Most Popular",
  },
  {
    tier: "premium" as const,
    label: "Premium",
    popular: false,
    color: "border-amber-500/60",
    btnClass: "bg-gradient-to-r from-amber-500 to-orange-500 hover:opacity-90 text-white",
    badge: "Best Value",
  },
];

const steps = [
  { step: "01", title: "Register & Onboard", desc: "Complete your 8-step profile in under 5 minutes." },
  { step: "02", title: "Connect Internshala", desc: "Paste your session cookies once. We encrypt and reuse them." },
  { step: "03", title: "Enable Auto-Apply", desc: "Set your match threshold (default 75). Bot handles the rest." },
  { step: "04", title: "Approve via Telegram", desc: "Each job gets a Telegram message. Tap approve. Bot applies." },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background animated-gradient grid-pattern text-foreground">
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-white/5">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-purple to-brand-blue flex items-center justify-center">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <span className="text-xl font-bold font-display gradient-text">Applivo</span>
          </Link>
          <div className="hidden md:flex items-center gap-8 text-sm text-muted-foreground">
            <a href="#features" className="hover:text-foreground transition-colors">Features</a>
            <a href="#how" className="hover:text-foreground transition-colors">How it works</a>
            <a href="#pricing" className="hover:text-foreground transition-colors">Pricing</a>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login" className="text-sm text-muted-foreground hover:text-foreground transition-colors px-4 py-2">
              Sign in
            </Link>
            <Link
              href="/register"
              className="px-4 py-2 bg-brand-purple text-white rounded-lg text-sm font-medium hover:bg-brand-purple/90 transition-all hover:shadow-lg hover:shadow-brand-purple/30"
            >
              Get started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-20 px-6 relative overflow-hidden">
        {/* Glow orbs */}
        <div className="absolute top-20 left-1/4 w-96 h-96 bg-brand-purple/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-40 right-1/4 w-80 h-80 bg-brand-blue/15 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-4xl mx-auto text-center relative">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-purple/10 border border-brand-purple/30 text-brand-purple-light text-sm mb-6">
              <Sparkles className="w-3.5 h-3.5" />
              AI-Powered Career Automation Platform v2.0
            </div>

            <h1 className="text-5xl md:text-7xl font-extrabold font-display leading-tight mb-6">
              Apply to{" "}
              <span className="gradient-text">500 jobs</span>
              <br />a day. On autopilot.
            </h1>

            <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed">
              Applivo scrapes job boards every 6 hours, scores every listing against your profile using LLaMA-70B,
              generates ATS-optimised resumes, and submits applications — all without you lifting a finger.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/register"
                className="inline-flex items-center gap-2 px-8 py-4 bg-brand-purple text-white rounded-xl font-semibold text-lg hover:bg-brand-purple/90 transition-all hover:shadow-xl hover:shadow-brand-purple/40 hover:-translate-y-0.5"
              >
                Start automating free
                <ArrowRight className="w-5 h-5" />
              </Link>
              <a
                href="#how"
                className="inline-flex items-center gap-2 px-8 py-4 glass rounded-xl font-semibold text-lg hover:bg-white/5 transition-all"
              >
                See how it works
              </a>
            </div>
          </motion.div>

          {/* Stats bar */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-6"
          >
            {stats.map((s) => (
              <div key={s.label} className="glass-card p-6 text-center">
                <div className="text-4xl font-extrabold font-display gradient-text mb-1">
                  {s.value}{s.suffix}
                </div>
                <div className="text-sm text-muted-foreground">{s.label}</div>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold font-display mb-4">
              Everything your job search needs
            </h2>
            <p className="text-muted-foreground text-lg max-w-xl mx-auto">
              From discovery to offer — every step of the pipeline is automated and AI-enhanced.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: i * 0.08 }}
                viewport={{ once: true }}
                className="glass-card p-6 card-hover"
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${f.color} flex items-center justify-center mb-4 shadow-lg`}>
                  <f.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="py-24 px-6 bg-card/30">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold font-display mb-4">Set up in minutes</h2>
            <p className="text-muted-foreground text-lg">Four steps to full automation.</p>
          </div>
          <div className="space-y-6">
            {steps.map((step, i) => (
              <motion.div
                key={step.step}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.4, delay: i * 0.1 }}
                viewport={{ once: true }}
                className="flex items-start gap-6 glass-card p-6"
              >
                <div className="text-4xl font-extrabold font-display gradient-text-purple shrink-0 w-12 text-center">
                  {step.step}
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-1">{step.title}</h3>
                  <p className="text-muted-foreground text-sm">{step.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold font-display mb-4">Simple monthly pricing</h2>
            <p className="text-muted-foreground text-lg">Pay monthly in INR. Cancel anytime.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {plans.map((plan, i) => (
              <motion.div
                key={plan.tier}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: i * 0.1 }}
                viewport={{ once: true }}
                className={`relative glass-card p-7 border ${plan.color} ${plan.popular ? "scale-105" : ""} flex flex-col`}
              >
                {plan.badge && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-brand-purple text-white text-xs font-semibold">
                    {plan.badge}
                  </div>
                )}
                <div className="mb-6">
                  <h3 className="text-xl font-bold font-display mb-1">{plan.label}</h3>
                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl font-extrabold">₹{PLAN_PRICES[plan.tier]}</span>
                    <span className="text-muted-foreground text-sm">/month</span>
                  </div>
                </div>
                <ul className="space-y-3 flex-1 mb-8">
                  {PLAN_FEATURES[plan.tier].map((feat) => (
                    <li key={feat} className="flex items-start gap-2 text-sm">
                      <Check className="w-4 h-4 text-brand-green shrink-0 mt-0.5" />
                      <span className="text-muted-foreground">{feat}</span>
                    </li>
                  ))}
                </ul>
                <Link
                  href={`/register?plan=${plan.tier}`}
                  className={`w-full px-6 py-3 rounded-lg font-semibold text-center text-sm transition-all ${plan.btnClass}`}
                >
                  Get started with {plan.label}
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6">
        <div className="max-w-2xl mx-auto text-center">
          <div className="glass-card p-12 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-brand-purple/10 to-brand-blue/10" />
            <div className="relative">
              <Globe className="w-12 h-12 text-brand-purple-light mx-auto mb-4 animate-float" />
              <h2 className="text-3xl font-bold font-display mb-4">
                Start your automated job search today
              </h2>
              <p className="text-muted-foreground mb-8">
                Join thousands of candidates who apply smarter, not harder.
              </p>
              <Link
                href="/register"
                className="inline-flex items-center gap-2 px-8 py-4 bg-brand-purple text-white rounded-xl font-semibold hover:bg-brand-purple/90 transition-all hover:shadow-xl hover:shadow-brand-purple/40"
              >
                Create free account
                <ChevronRight className="w-5 h-5" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-brand-purple-light" />
            <span>Applivo v2.0 — AI Career Automation SaaS</span>
          </div>
          <div className="flex gap-6">
            <Link href="/pricing" className="hover:text-foreground transition-colors">Pricing</Link>
            <Link href="/login" className="hover:text-foreground transition-colors">Login</Link>
            <Link href="/register" className="hover:text-foreground transition-colors">Register</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
