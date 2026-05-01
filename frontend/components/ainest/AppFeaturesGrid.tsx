"use client";

import { motion } from "framer-motion";
import { Mic, Image as ImageIcon, MessageSquare, Video, LineChart, FileText, Globe, Link, Briefcase } from "lucide-react";

const miniFeatures = [
  { text: "Smart Resumes", icon: <FileText className="w-5 h-5 text-zinc-500" /> },
  { text: "AI Cover Letters", icon: <MessageSquare className="w-5 h-5 text-zinc-500" /> },
  { text: "Career Tracking", icon: <LineChart className="w-5 h-5 text-zinc-500" /> },
  { text: "Job Scraping", icon: <Globe className="w-5 h-5 text-zinc-500" /> },
  { text: "LinkedIn Links", icon: <Link className="w-5 h-5 text-zinc-500" /> },
  { text: "Portfolio Gen", icon: <Briefcase className="w-5 h-5 text-zinc-500" /> },
  { text: "Voice Prep", icon: <Mic className="w-5 h-5 text-zinc-500" /> },
  { text: "Video Analytics", icon: <Video className="w-5 h-5 text-zinc-500" /> },
  { text: "Profile Image", icon: <ImageIcon className="w-5 h-5 text-zinc-500" /> },
];

export function AppFeaturesGrid() {
  return (
    <section className="bg-[#050505] py-24 px-6 relative z-10 border-b border-zinc-900/50">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl font-medium tracking-tight text-white mb-4">
            Everything you need
          </h2>
          <p className="text-[#a1a1aa]">Powerful AI models driving your job applications</p>
        </motion.div>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {miniFeatures.map((feat, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.05 }}
              className="flex items-center gap-4 bg-[#1c1c1e] border border-[#1a1a1a] rounded-2xl p-5 hover:bg-[#111] transition-colors cursor-default"
            >
              {feat.icon}
              <span className="text-zinc-300 font-medium text-sm">{feat.text}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
