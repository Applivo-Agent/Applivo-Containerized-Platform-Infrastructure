"use client";

import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import {
  Settings,
  Bell,
  Zap,
  Brain,
  Cpu,
  Link2,
  Shield,
  SlidersHorizontal,
} from "lucide-react";

const icons: Record<string, React.ReactNode> = {
  general: <Settings className="w-4 h-4" />,
  notifications: <Bell className="w-4 h-4" />,
  "job-automation": <Zap className="w-4 h-4" />,
  "agent-strategy": <Brain className="w-4 h-4" />,
  "ai-settings": <Cpu className="w-4 h-4" />,
  "platform-connections": <Link2 className="w-4 h-4" />,
  security: <Shield className="w-4 h-4" />,
  advanced: <SlidersHorizontal className="w-4 h-4" />,
};

interface Section {
  id: string;
  label: string;
  component: React.ComponentType;
}

interface SettingsSidebarProps {
  activeTab: string;
  onTabChange: (id: string) => void;
  sections: Section[];
}

export function SettingsSidebar({ activeTab, onTabChange, sections }: SettingsSidebarProps) {
  return (
    <div className="lg:w-56 lg:sticky lg:top-24 shrink-0">
      <div className="bg-[#1c1c1e] border border-[#262626] rounded-2xl p-2 space-y-1">
        {sections.map((section) => (
          <button
            key={section.id}
            onClick={() => onTabChange(section.id)}
            className={cn(
              "relative w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors",
              activeTab === section.id
                ? "text-white"
                : "text-zinc-400 hover:text-zinc-200 hover:bg-white/5"
            )}
          >
            {activeTab === section.id && (
              <motion.div
                layoutId="activeTab"
                className="absolute inset-0 bg-white/10 rounded-xl border border-white/10"
                transition={{ type: "spring", stiffness: 400, damping: 30 }}
              />
            )}
            <span className="relative z-10">{icons[section.id]}</span>
            <span className="relative z-10">{section.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
