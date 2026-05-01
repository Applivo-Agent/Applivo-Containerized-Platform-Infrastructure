"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { 
  ShieldCheck, 
  Lock, 
  Eye, 
  Database, 
  UserCheck,
  Globe
} from "lucide-react";
import { NavBar } from "@/components/NavBar";

const sections = [
  {
    title: "Data Collection",
    id: "collection",
    content: "We collect information you provide directly to us when you create an account, upload a resume, or use our automation services. This includes your name, email address, physical address (for job forms), professional experience, and education history.",
    subpoints: [
      "Contact details (Email, Phone, LinkedIn profile)",
      "Resume and professional portfolio data",
      "Application history and status",
      "Usage statistics and platform interactions"
    ]
  },
  {
    title: "AI & Data Processing",
    id: "ai-processing",
    content: "Applivo uses advanced LLM (Large Language Models) to analyze job descriptions and optimize your profile for ATS (Applicant Tracking Systems).",
    subpoints: [
      "Models process your data to calculate match scores",
      "AI generates cover letters based on your professional experience",
      "Your data is never used to train global public models",
      "All AI processing is isolated to your individual session"
    ]
  },
  {
    title: "Data Security",
    id: "security",
    content: "We implement industry-standard security measures to protect your professional data. All sensitive information is encrypted at rest and in transit.",
    subpoints: [
      "AES-256 encryption for resume storage",
      "TLS 1.3 for all data in transit",
      "Regular automated security audits",
      "Strict least-privilege access controls"
    ]
  },
  {
    title: "GDPR & Privacy Rights",
    id: "rights",
    content: "Under the General Data Protection Regulation (GDPR), users in the European Economic Area (EEA) have specific rights regarding their personal data.",
    subpoints: [
      "Right to access and export your data",
      "Right to rectification (correcting errors)",
      "Right to erasure ('Right to be Forgotten')",
      "Right to object to automated processing"
    ]
  },
  {
    title: "Data Retention",
    id: "retention",
    content: "We retain your information as long as your account is active or needed to provide you with services. You can delete your account and all associated data at any time through the security settings.",
    subpoints: []
  }
];

export default function PrivacyPolicyPage() {
  return (
    <div className="min-h-screen bg-black text-white pb-32">
      <NavBar />

      <div className="max-w-[900px] mx-auto px-6 pt-32">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-16"
        >
          <h1 className="text-4xl font-bold tracking-tight mb-4 text-white">Privacy Policy</h1>
          <p className="text-zinc-500 text-lg leading-relaxed">
            Last updated: April 16, 2026. How we protect your data at Applivo.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-[1fr_250px] gap-12">
          {/* Detailed Content */}
          <div className="space-y-16">
            {sections.map((section) => (
              <section key={section.id} id={section.id} className="scroll-mt-32">
                <h2 className="text-xl font-bold mb-4 text-white uppercase tracking-tight">{section.title}</h2>
                <p className="text-zinc-400 leading-relaxed mb-6">
                  {section.content}
                </p>
                {section.subpoints.length > 0 && (
                  <ul className="space-y-3">
                    {section.subpoints.map((point, pi) => (
                      <li key={pi} className="flex items-start gap-3 text-sm text-zinc-500">
                        <div className="w-1.5 h-1.5 rounded-full bg-white/30 mt-1.5 shrink-0" />
                        {point}
                      </li>
                    ))}
                  </ul>
                )}
              </section>
            ))}

          </div>

          {/* Table of Contents - Sticky Desktop */}
          <aside className="hidden md:block">
            <div className="sticky top-32 space-y-6">
              <h4 className="text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-500 mb-4">On this page</h4>
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
                  <Lock className="w-3 h-3" />
                  <span className="text-[10px] font-medium uppercase tracking-widest">Encrypted</span>
                </div>
                <div className="flex items-center gap-2 text-zinc-600">
                  <Eye className="w-3 h-3" />
                  <span className="text-[10px] font-medium uppercase tracking-widest">No Tracking</span>
                </div>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
