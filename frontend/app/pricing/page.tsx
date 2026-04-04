"use client";
import React from "react";
import Link from "next/link";
import { Check, Zap, Crown, ArrowRight, Sparkles } from "lucide-react";
import { motion } from "framer-motion";
import { PLAN_FEATURES, PLAN_PRICES } from "@/lib/subscription";

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

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-background animated-gradient grid-pattern text-foreground py-24 px-6 mt-16">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-purple/10 border border-brand-purple/30 text-brand-purple-light text-sm mb-6"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Simple Transparent Pricing
          </motion.div>
          <h1 className="text-4xl md:text-6xl font-extrabold font-display mb-6">
            Choose the perfect <span className="gradient-text">automation speed</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Scale your job search effort with AI-powered tools designed to land you offers faster.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {plans.map((plan, i) => (
            <motion.div
              key={plan.tier}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className={`relative glass-card p-8 border ${plan.color} ${plan.popular ? "scale-105 shadow-2xl shadow-brand-purple/10" : ""} flex flex-col h-full`}
            >
              {plan.badge && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-brand-purple text-white text-xs font-bold tracking-wide">
                  {plan.badge}
                </div>
              )}
              
              <div className="mb-8">
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-2xl font-bold font-display">{plan.label}</h3>
                  {plan.tier === 'premium' && <Crown className="w-5 h-5 text-amber-400" />}
                </div>
                <div className="flex items-baseline gap-1">
                  <span className="text-5xl font-extrabold tracking-tight">₹{PLAN_PRICES[plan.tier]}</span>
                  <span className="text-muted-foreground text-sm font-medium">/month</span>
                </div>
              </div>

              <ul className="space-y-4 flex-1 mb-10">
                {PLAN_FEATURES[plan.tier].map((feat) => (
                  <li key={feat} className="flex items-start gap-3">
                    <div className="mt-1 w-5 h-5 rounded-full bg-emerald-500/10 flex items-center justify-center shrink-0">
                      <Check className="w-3.5 h-3.5 text-emerald-500" />
                    </div>
                    <span className="text-muted-foreground text-sm leading-relaxed">{feat}</span>
                  </li>
                ))}
              </ul>

              <Link
                href={`/register?plan=${plan.tier}`}
                className={`w-full px-6 py-4 rounded-xl font-bold text-center text-sm transition-all flex items-center justify-center gap-2 ${plan.btnClass}`}
              >
                Get Started
                <ArrowRight className="w-4 h-4" />
              </Link>
            </motion.div>
          ))}
        </div>

        <div className="mt-20 text-center">
            <p className="text-muted-foreground text-sm">
                Pricing in INR includes all taxes. Cancel anytime from your settings.
            </p>
        </div>
      </div>
    </div>
  );
}
