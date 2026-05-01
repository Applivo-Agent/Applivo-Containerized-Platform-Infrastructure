"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { 
  Handshake, 
  CreditCard, 
  AlertCircle, 
  Scale, 
  Zap,
  CheckCircle,
  FileText
} from "lucide-react";
import { NavBar } from "@/components/NavBar";

const sections = [
  {
    title: "Acceptance of Terms",
    id: "acceptance",
    content: "By accessing or using the Applivo platform, you agree to be bound by these Terms of Use and all applicable laws and regulations. If you do not agree with any of these terms, you are prohibited from using or accessing this site.",
  },
  {
    title: "Subscription & Payments",
    id: "payments",
    content: "Applivo offers tiered subscription plans (Starter, Pro, Premium). By subscribing, you agree to the specific daily application limits and feature sets associated with your chosen tier.",
    subpoints: [
      "Fees are billed monthly or annually in advance",
      "Subscriptions automatically renew unless cancelled 24 hours before the end of the term",
      "Refunds are processed within 7-10 business days for eligible claims",
      "Unused daily applications do not roll over to the next day"
    ]
  },
  {
    title: "Automation Rules",
    id: "automation",
    content: "Applivo acts as your authorized agent to automate job applications. You are responsible for ensuring your automation settings comply with the target platform's policies.",
    subpoints: [
      "You grant Applivo permission to submit forms on your behalf",
      "Automations must run at reasonable speeds to avoid platform bans",
      "You must provide accurate information in your candidate profile",
      "Applivo is not responsible for applications rejected by external job boards"
    ]
  },
  {
    title: "Acceptable Use",
    id: "usage",
    content: "You may not use Applivo for any illegal purpose or to violate any laws in your jurisdiction (including but not limited to copyright laws).",
    subpoints: [
      "No scraping of Applivo's proprietary matching logic",
      "No creation of multiple accounts to bypass daily limits",
      "No submission of fraudulent professional information",
      "No use of the service to harass job recruiters"
    ]
  },
  {
    title: "Limitation of Liability",
    id: "liability",
    content: "Applivo and its suppliers shall not be liable for any damages (including, without limitation, damages for loss of data or profit, or due to business interruption) arising out of the use or inability to use the platform.",
    subpoints: [
      "Applivo does not guarantee job placement",
      "We are not liable for any third-party data breaches on external job sites",
      "Services are provided on an 'as is' and 'as available' basis"
    ]
  }
];

export default function TermsOfUsePage() {
  return (
    <div className="min-h-screen bg-black text-white pb-32">
      <NavBar />

      <div className="max-w-[900px] mx-auto px-6 pt-32">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-16"
        >
          <h1 className="text-4xl font-bold tracking-tight mb-4 text-white">Terms of Use</h1>
          <p className="text-zinc-500 text-lg leading-relaxed">
            Last updated: April 16, 2026. The rules for using the Applivo platform.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-[1fr_250px] gap-12">
          {/* Detailed Content */}
          <div className="space-y-16">
            {sections.map((section) => (
              <section key={section.id} id={section.id} className="scroll-mt-32">
                <h2 className="text-xl font-bold mb-4 text-white flex items-center gap-3 uppercase tracking-tight">
                  {section.title}
                </h2>
                <p className="text-zinc-400 leading-relaxed mb-6">
                  {section.content}
                </p>
                {section.subpoints && section.subpoints.length > 0 && (
                  <div className="grid grid-cols-1 gap-3">
                    {section.subpoints.map((point, pi) => (
                      <div key={pi} className="flex items-start gap-4 p-4 rounded-xl bg-white/[0.02] border border-white/[0.04]">
                        <CheckCircle className="w-4 h-4 text-white/20 mt-0.5 shrink-0" />
                        <span className="text-sm text-zinc-500">{point}</span>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            ))}

            {/* Quick Summary Box */}
            <div className="bg-[#0f0f12] border-l-2 border-white/20 p-8 rounded-r-2xl shadow-xl">
              <h3 className="font-bold mb-4 flex items-center gap-2 text-white">
                <AlertCircle className="w-4 h-4 text-white/60" />
                Wait, TL;DR?
              </h3>
              <p className="text-sm text-zinc-500 leading-relaxed">
                Basically: We automate applications for you, but you need to provide real info and follow the rules of the platforms we apply to. No spamming, no cheating the limits, and we don&apos;t guarantee you&apos;ll get the job (but we&apos;ll sure try).
              </p>
            </div>
          </div>

          {/* Table of Contents - Sticky Desktop */}
          <aside className="hidden md:block">
            <div className="sticky top-32 space-y-6">
              <h4 className="text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-500 mb-4">Agreement Sections</h4>
              <nav className="flex flex-col gap-3">
                {sections.map((section) => (
                  <a 
                    key={section.id} 
                    href={`#${section.id}`}
                    className="text-xs text-zinc-500 hover:text-white transition-colors"
                  >
                    {section.title}
                  </a>
                ))}
              </nav>

              <div className="pt-8 border-t border-white/5 space-y-4">
                <div className="flex items-center gap-2 text-zinc-600">
                  <Scale className="w-3 h-3" />
                  <span className="text-[10px] font-medium uppercase tracking-widest">Fair Play</span>
                </div>
                <div className="flex items-center gap-2 text-zinc-600">
                  <CreditCard className="w-3 h-3" />
                  <span className="text-[10px] font-medium uppercase tracking-widest">Secure Payments</span>
                </div>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
