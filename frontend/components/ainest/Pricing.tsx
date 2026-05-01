"use client";

import { motion } from "framer-motion";
import { Check, Zap, Star, Crown } from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";

const plans = [
  {
    tier: "starter",
    name: "Starter",
    icon: <Zap className="w-4 h-4" />,
    description: "Perfect for students & fresh job seekers",
    monthlyPrice: 199,
    yearlyPrice: 159,
    highlight: false,
    badge: null,
    color: "slate",
    features: [
      "50 daily applications",
      "Analyze budget: 25k tokens/run",
      "Analyze budget: 120k tokens/month",
      "Internshala scraping",
      "Auto-apply bot",
      "Resume upload & management",
      "AI match scoring",
      "Basic analytics",
      "Email notifications",
      "Application tracking (Kanban)",
      "AI Chat assistant (50 messages/month)",
    ],
  },
  {
    tier: "pro",
    name: "Pro",
    icon: <Star className="w-4 h-4" />,
    description: "For serious job hunters who want every edge",
    monthlyPrice: 399,
    yearlyPrice: 319,
    highlight: true,
    badge: "Most Popular",
    color: "white",
    features: [
      "100 daily applications",
      "Analyze budget: 60k tokens/run",
      "Analyze budget: 600k tokens/month",
      "Everything in Starter",
      "Advanced AI analysis",
      "Cover letter generator",
      "Telegram notifications",
      "Interview tracking & prep",
      "Email inbox monitoring (IMAP)",
      "7-day follow-up automation",
      "Priority queue processing",
      "Skill gap analysis",
      "AI Chat assistant (100 messages/month)",
    ],
  },
  {
    tier: "premium",
    name: "Premium",
    icon: <Crown className="w-4 h-4" />,
    description: "Maximum power for executives & professionals",
    monthlyPrice: 599,
    yearlyPrice: 479,
    highlight: false,
    badge: null,
    color: "zinc",
    features: [
      "150 daily applications",
      "Analyze budget: Unlimited",
      "AI Chat assistant (150 messages/month)",
      "Everything in Pro",
      "Highest priority queue",
      "Advanced analytics",
      "Market insights & salary data",
      "Resume performance ranking",
      "Interview conversion funnel",
      "Dedicated support",
    ],
  },
];

const colorMap: Record<string, { glow: string; ring: string; badge: string; icon: string; check: string; btn: string }> = {
  slate: {
    glow: "rgba(255,255,255,0.03)",
    ring: "hover:border-white/10",
    badge: "bg-white/10 text-zinc-400 border-white/10",
    icon: "bg-white/10 border-white/10 text-zinc-400",
    check: "bg-white/10 border-white/10 text-zinc-400",
    btn: "bg-white text-black hover:bg-zinc-200 shadow-xl",
  },
  white: {
    glow: "rgba(255,255,255,0.05)",
    ring: "border-[#ffffff]/30",
    badge: "bg-white/15 text-white border-[#ffffff]/25",
    icon: "bg-white/15 border-[#ffffff]/30 text-white",
    check: "bg-white/10 border-[#ffffff]/25 text-white",
    btn: "bg-white hover:bg-zinc-100 text-black",
  },
  zinc: {
    glow: "rgba(255,255,255,0.03)",
    ring: "hover:border-white/10",
    badge: "bg-white/10 text-zinc-400 border-white/10",
    icon: "bg-white/10 border-white/10 text-zinc-400",
    check: "bg-white/10 border-white/10 text-zinc-400",
    btn: "bg-white text-black hover:bg-zinc-200 shadow-xl",
  },
};

export function SimplePricing() {
  const [yearly, setYearly] = useState(false);
  const isLoggedIn = useMemo(() => {
    if (typeof window === "undefined") return false;
    return Boolean(localStorage.getItem("applivo_token"));
  }, []);

  return (
    <section className="bg-[#080808] py-32 px-6 relative z-10 flex flex-col items-center">

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="text-center mb-12"
      >
        <p className="text-white text-[13px] font-semibold uppercase tracking-[0.1em] mb-4">Pricing</p>
        <h2 className="text-[40px] md:text-[48px] font-bold tracking-tight text-white mb-5 leading-[1.15]">
          Simple, transparent plans
        </h2>
        <p className="text-[#666] text-[16px] max-w-[440px] mx-auto leading-[1.7]">
          Tailored for every stage of your career journey. No hidden fees, cancel anytime.
        </p>
      </motion.div>

      {/* Monthly / Yearly Toggle */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.4, delay: 0.1 }}
        className="flex items-center gap-2 p-1.5 bg-[#111] rounded-full border border-[#1e1e1e] mb-14"
      >
        <button
          onClick={() => setYearly(false)}
          className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${!yearly ? "bg-white text-black shadow-sm" : "text-[#555] hover:text-white"}`}
        >
          Monthly
        </button>
        <button
          onClick={() => setYearly(true)}
          className={`px-6 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-2 ${yearly ? "bg-white text-black shadow-sm" : "text-[#555] hover:text-white"}`}
        >
          Yearly
          <span className="bg-white/15 text-white text-[10px] px-2 py-0.5 rounded-full border border-[#ffffff]/25 font-semibold">
            Save 20%
          </span>
        </button>
      </motion.div>

      {/* Pricing Cards */}
      <div className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-3 gap-5">
        {plans.map((plan, i) => {
          const c = colorMap[plan.color];
          const price = yearly ? plan.yearlyPrice : plan.monthlyPrice;

          return (
            <motion.div
              key={plan.tier}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.08 }}
              className={`relative rounded-2xl bg-[#1c1c1e] border border-[#262626] overflow-hidden flex flex-col transition-all duration-300 ${plan.highlight
                ? "shadow-[0_0_60px_-10px_rgba(255,255,255,0.1)] scale-[1.02] border-white/20"
                : `hover:border-white/10`
                }`}
            >
              {/* Glow */}
              <div
                className="absolute top-0 right-0 w-48 h-48 rounded-full opacity-60 blur-[80px] pointer-events-none"
                style={{ background: c.glow }}
              />

              {/* Popular badge */}
              {plan.badge && (
                <div className="absolute top-4 right-4">
                  <span className={`text-[11px] font-semibold px-2.5 py-1 rounded-full border ${c.badge}`}>
                    {plan.badge}
                  </span>
                </div>
              )}

              <div className="relative z-10 p-7 flex flex-col flex-1">

                {/* Plan name + icon */}
                <div className="flex items-center gap-2.5 mb-1">
                  <div className={`w-7 h-7 rounded-lg flex items-center justify-center border ${c.icon}`}>
                    {plan.icon}
                  </div>
                  <span className="text-white font-semibold text-[16px]">{plan.name}</span>
                </div>
                <p className="text-[#555] text-[13px] mb-7 leading-relaxed">{plan.description}</p>

                {/* Price */}
                <div className="flex items-end gap-1 mb-1">
                  <span className="text-[13px] text-[#555] font-medium">₹</span>
                  <motion.span
                    key={price}
                    initial={{ opacity: 0, y: -8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.25 }}
                    className="text-[44px] font-bold text-white leading-none tracking-tight"
                  >
                    {price}
                  </motion.span>
                  <span className="text-[#444] text-[13px] mb-1">/ month</span>
                </div>
                {yearly && (
                  <p className="text-[11px] text-[#555] mb-7">Billed ₹{price * 12}/year</p>
                )}
                {!yearly && <div className="mb-7" />}

                {/* Divider */}
                <div className="h-[1px] bg-[#1a1a1a] mb-6" />

                {/* Features */}
                <div className="space-y-3 flex-1">
                  {plan.features.map((feat, fi) => (
                    <div key={fi} className="flex items-start gap-3">
                      <div className={`mt-0.5 w-4 h-4 rounded-full flex items-center justify-center border shrink-0 ${c.check}`}>
                        <Check className="w-2.5 h-2.5" strokeWidth={3} />
                      </div>
                      <span className="text-[#888] text-[13px] leading-relaxed">{feat}</span>
                    </div>
                  ))}
                </div>

                {/* CTA */}
                <Link
                  href={isLoggedIn ? "/subscription" : "/register"}
                  className={`mt-8 block w-full text-center py-3 rounded-xl text-[14px] font-semibold transition-all ${c.btn}`}
                >
                  Get started
                </Link>
              </div>
            </motion.div>
          );
        })}
      </div>

    </section>
  );
}
