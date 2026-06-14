"use client";

import { SettingSection, SettingCard, SettingRow } from "@/components/settings/card";
import { Toggle } from "@/components/settings/toggle";
import { useSettings } from "@/lib/settings-context";
import { Zap, RefreshCw, BarChart3, ShieldCheck, Clock } from "lucide-react";
import { useCallback, useState } from "react";

function cn(...classes: (string | boolean | undefined)[]) {
  return classes.filter(Boolean).join(" ");
}

export function JobAutomationSection() {
  const { settings, saveSection } = useSettings();

  const [localDaily, setLocalDaily] = useState(settings.dailyApplicationLimit);
  const [localWeekly, setLocalWeekly] = useState(settings.weeklyApplicationLimit);
  const [localThreshold, setLocalThreshold] = useState(settings.autoApprovalThreshold);

  const save = useCallback((data: Record<string, unknown>) => {
    saveSection("automation", data);
  }, [saveSection]);

  const autonomousActive = settings.autonomousMode;

  return (
    <SettingSection>
      <SettingCard
        title="Autonomous Mode"
        description="When enabled, your AI agent operates fully autonomously based on your configured rules"
        icon={<Zap className="w-4 h-4 text-white" />}
        action={
          <Toggle
            checked={settings.autonomousMode}
            onChange={(v) => save({ agent_mode: v ? "full_auto" : "manual" })}
            size="lg"
          />
        }
      >
        <div className="flex items-center gap-3 p-4 bg-[#161616] border border-zinc-800 rounded-xl">
          <div className={cn("w-2 h-2 rounded-full", autonomousActive ? "bg-emerald-500 animate-pulse" : "bg-zinc-600")} />
          <p className="text-sm text-[#A1A1AA]">
            {autonomousActive
              ? "Agent is running autonomously. All configured automations are active."
              : "Agent is in manual mode. You must trigger each action manually."}
          </p>
        </div>
      </SettingCard>

      <SettingCard
        title="Automation Pipeline"
        description="Control each stage of the job application pipeline"
        icon={<RefreshCw className="w-4 h-4 text-white" />}
      >
        <div className="space-y-1">
          <SettingRow label="Auto Scrape Jobs" description="Continuously discover new opportunities from connected platforms">
            <Toggle checked={settings.autoScrapeJobs} onChange={(v) => save({ auto_scrape_jobs: v })} />
          </SettingRow>
          <SettingRow label="Auto Analyze Jobs" description="AI automatically scores and ranks each discovered job">
            <Toggle checked={settings.autoAnalyzeJobs} onChange={(v) => save({ auto_analyze_jobs: v })} />
          </SettingRow>
          <SettingRow label="Auto Queue Jobs" description="High-scoring jobs are automatically added to your application queue">
            <Toggle checked={settings.autoQueueJobs} onChange={(v) => save({ auto_queue_jobs: v })} />
          </SettingRow>
          <SettingRow label="Auto Apply" description="Submit applications to queued jobs without manual intervention">
            <Toggle checked={settings.autoApply} onChange={(v) => save({ auto_apply: v })} />
          </SettingRow>
        </div>
      </SettingCard>

      <SettingCard
        title="Application Limits"
        description="Set boundaries to prevent overwhelming recruiters or burning quotas"
        icon={<BarChart3 className="w-4 h-4 text-white" />}
      >
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-[#161616] border border-zinc-800 rounded-xl space-y-3">
            <label className="text-xs font-bold uppercase tracking-widest text-[#A1A1AA]">Daily Limit</label>
            <div className="flex items-center gap-3">
              <input
                type="number"
                min={1}
                max={50}
                value={localDaily}
                onChange={(e) => setLocalDaily(Number(e.target.value))}
                onBlur={() => save({ daily_application_limit: localDaily })}
                className="w-20 bg-[#0B0B0F] border border-zinc-800 rounded-xl px-3 py-2 text-sm text-white text-center focus:outline-none focus:border-white transition-all"
              />
              <span className="text-xs text-[#A1A1AA]">apps / day</span>
            </div>
            <input
              type="range"
              min={1}
              max={50}
              value={localDaily}
              onChange={(e) => setLocalDaily(Number(e.target.value))}
              onMouseUp={() => save({ daily_application_limit: localDaily })}
              onTouchEnd={() => save({ daily_application_limit: localDaily })}
              className="w-full h-1.5 bg-[#0B0B0F] rounded-full accent-white cursor-pointer"
            />
          </div>

          <div className="p-4 bg-[#161616] border border-zinc-800 rounded-xl space-y-3">
            <label className="text-xs font-bold uppercase tracking-widest text-[#A1A1AA]">Weekly Limit</label>
            <div className="flex items-center gap-3">
              <input
                type="number"
                min={1}
                max={200}
                value={localWeekly}
                onChange={(e) => setLocalWeekly(Number(e.target.value))}
                onBlur={() => save({ weekly_application_limit: localWeekly })}
                className="w-20 bg-[#0B0B0F] border border-zinc-800 rounded-xl px-3 py-2 text-sm text-white text-center focus:outline-none focus:border-white transition-all"
              />
              <span className="text-xs text-[#A1A1AA]">apps / week</span>
            </div>
            <input
              type="range"
              min={1}
              max={200}
              value={localWeekly}
              onChange={(e) => setLocalWeekly(Number(e.target.value))}
              onMouseUp={() => save({ weekly_application_limit: localWeekly })}
              onTouchEnd={() => save({ weekly_application_limit: localWeekly })}
              className="w-full h-1.5 bg-[#0B0B0F] rounded-full accent-white cursor-pointer"
            />
          </div>
        </div>
      </SettingCard>

      <SettingCard
        title="Approval Settings"
        description="Control how much autonomy your agent has"
        icon={<ShieldCheck className="w-4 h-4 text-white" />}
      >
        <div className="space-y-1">
          <SettingRow label="Require Manual Approval" description="Every application is held for your review before submission">
            <Toggle checked={settings.requireManualApproval} onChange={(v) => save({ require_manual_approval: v })} />
          </SettingRow>

          <div className="py-4 border-b border-[#262626] last:border-0">
            <div className="flex justify-between items-center mb-3">
              <label className="text-sm font-medium text-white">Auto Approval Threshold</label>
              <span className="text-sm font-bold text-white bg-[#1c1c1e] border border-zinc-800 px-2 py-0.5 rounded-lg">
                {localThreshold}%
              </span>
            </div>
            <p className="text-xs text-[#A1A1AA] mb-3">Jobs scoring above this threshold are auto-approved if manual approval is off</p>
            <input
              type="range"
              min={0}
              max={100}
              value={localThreshold}
              onChange={(e) => setLocalThreshold(Number(e.target.value))}
              onMouseUp={() => save({ auto_approval_threshold: localThreshold })}
              onTouchEnd={() => save({ auto_approval_threshold: localThreshold })}
              className="w-full h-2 bg-[#0B0B0F] rounded-full accent-white cursor-pointer"
            />
            <div className="flex justify-between mt-2 text-[10px] text-[#A1A1AA] uppercase tracking-wider">
              <span>Any match</span>
              <span>Perfect match</span>
            </div>
          </div>
        </div>
      </SettingCard>

      <SettingCard
        title="Schedule"
        description="How often the agent checks for new jobs and processes the queue"
        icon={<Clock className="w-4 h-4 text-white" />}
      >
        <div className="grid grid-cols-4 gap-2">
          {([
            { value: "30min" as const, label: "30 min", desc: "Aggressive" },
            { value: "1hour" as const, label: "1 hour", desc: "Standard" },
            { value: "6hours" as const, label: "6 hours", desc: "Relaxed" },
            { value: "daily" as const, label: "Daily", desc: "Passive" },
          ]).map((opt) => (
            <button
              key={opt.value}
              onClick={() => save({ schedule_interval: opt.value })}
              className={`p-3 rounded-xl border text-center transition-all ${
                settings.scheduleInterval === opt.value
                  ? "bg-white text-black border-white shadow-lg"
                  : "bg-[#161616] text-[#A1A1AA] border-zinc-800 hover:border-white/30"
              }`}
            >
              <p className="text-sm font-bold">{opt.label}</p>
              <p className="text-[10px] mt-0.5 opacity-60">{opt.desc}</p>
            </button>
          ))}
        </div>
      </SettingCard>
    </SettingSection>
  );
}
