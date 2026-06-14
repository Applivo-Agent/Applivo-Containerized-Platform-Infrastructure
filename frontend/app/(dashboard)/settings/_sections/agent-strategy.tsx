"use client";

import { SettingSection, SettingCard } from "@/components/settings/card";
import { useSettings } from "@/lib/settings-context";
import { Rocket, Scale, Gem, ChevronRight } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

const strategies = [
  {
    id: "aggressive" as const,
    label: "Aggressive",
    description: "Apply to more jobs with a lower match threshold. Faster automation, higher volume.",
    details: [
      "Lower match threshold (50%)",
      "Applies to 2x more jobs",
      "Faster queue processing",
      "Higher daily application cap",
    ],
    icon: Rocket,
    color: "text-amber-400",
    border: "border-amber-500/20",
    bg: "bg-amber-500/5",
    ring: "ring-amber-500/20",
  },
  {
    id: "balanced" as const,
    label: "Balanced",
    description: "The recommended mode. A healthy mix of quantity and quality for most users.",
    details: [
      "Standard match threshold (75%)",
      "Moderate application volume",
      "Smart queue prioritization",
      "Best for most users",
    ],
    icon: Scale,
    color: "text-emerald-400",
    border: "border-emerald-500/20",
    bg: "bg-emerald-500/5",
    ring: "ring-emerald-500/20",
  },
  {
    id: "quality" as const,
    label: "Quality",
    description: "Apply only to the strongest matches. Higher standards, better targeting.",
    details: [
      "High match threshold (90%)",
      "Fewer but stronger applications",
      "Detailed cover letters",
      "Best for senior roles",
    ],
    icon: Gem,
    color: "text-sky-400",
    border: "border-sky-500/20",
    bg: "bg-sky-500/5",
    ring: "ring-sky-500/20",
  },
];

export function AgentStrategySection() {
  const { settings, saveSection } = useSettings();

  return (
    <SettingSection>
      <SettingCard
        title="Agent Strategy"
        description="Define how your AI agent approaches the job market"
        icon={<Scale className="w-4 h-4 text-white" />}
      >
        <div className="grid gap-4">
          {strategies.map((s, i) => {
            const Icon = s.icon;
            const isActive = settings.strategyMode === s.id;

            return (
              <motion.button
                key={s.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                onClick={() => saveSection("strategy", { agent_strategy: s.id })}
                className={cn(
                  "relative text-left p-5 rounded-2xl border transition-all duration-300",
                  isActive
                    ? cn("bg-[#1a1a1a]", s.border, "ring-1", s.ring)
                    : "bg-[#161616] border-zinc-800 hover:border-zinc-700"
                )}
              >
                {isActive && (
                  <div className={cn("absolute top-4 right-4 text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-full", s.bg, s.color, s.border, "border")}>
                    Active
                  </div>
                )}
                <div className="flex items-start gap-4">
                  <div className={cn("w-10 h-10 rounded-xl flex items-center justify-center shrink-0", s.bg, s.border, "border")}>
                    <Icon className={cn("w-5 h-5", s.color)} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-bold text-white mb-1">{s.label}</h4>
                    <p className="text-xs text-[#A1A1AA] leading-relaxed mb-3">{s.description}</p>
                    <ul className="space-y-1.5">
                      {s.details.map((d) => (
                        <li key={d} className="flex items-center gap-2 text-xs text-[#A1A1AA]">
                          <ChevronRight className={cn("w-3 h-3 shrink-0", s.color)} />
                          {d}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </motion.button>
            );
          })}
        </div>
      </SettingCard>
    </SettingSection>
  );
}
