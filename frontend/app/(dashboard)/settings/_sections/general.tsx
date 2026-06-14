"use client";

import { SettingSection, SettingCard, SettingRow } from "@/components/settings/card";
import { useSettings } from "@/lib/settings-context";
import { Globe, Monitor } from "lucide-react";

export function GeneralSection() {
  const { settings, saveSection } = useSettings();

  return (
    <SettingSection>
      <SettingCard
        title="General Preferences"
        description="Platform-wide settings that control how Applivo behaves"
        icon={<Globe className="w-4 h-4 text-white" />}
      >
        <div className="space-y-1">
          <SettingRow label="Timezone" description="All schedules and notifications use this timezone">
            <select
              value={settings.timezone}
              onChange={(e) => saveSection("general", { timezone: e.target.value })}
              className="bg-[#161616] border border-zinc-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-white transition-all"
            >
              <option value="Asia/Kolkata">Asia/Kolkata (IST)</option>
              <option value="Asia/Dubai">Asia/Dubai (GST)</option>
              <option value="Asia/Singapore">Asia/Singapore (SGT)</option>
              <option value="Europe/London">Europe/London (GMT)</option>
              <option value="America/New_York">America/New_York (EST)</option>
              <option value="America/Los_Angeles">America/Los_Angeles (PST)</option>
              <option value="UTC">UTC</option>
            </select>
          </SettingRow>

          <SettingRow label="Language" description="Interface language for the platform">
            <select
              value={settings.language}
              onChange={(e) => saveSection("general", { language: e.target.value })}
              className="bg-[#161616] border border-zinc-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-white transition-all"
            >
              <option value="en">English</option>
              <option value="hi">Hindi</option>
              <option value="ta">Tamil</option>
              <option value="te">Telugu</option>
            </select>
          </SettingRow>

          <SettingRow label="Date Format" description="How dates are displayed across the platform">
            <select
              value={settings.dateFormat}
              onChange={(e) => saveSection("general", { date_format: e.target.value })}
              className="bg-[#161616] border border-zinc-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-white transition-all"
            >
              <option value="DD/MM/YYYY">DD/MM/YYYY</option>
              <option value="MM/DD/YYYY">MM/DD/YYYY</option>
              <option value="YYYY-MM-DD">YYYY-MM-DD</option>
            </select>
          </SettingRow>

          <SettingRow label="Theme" description="Applivo is currently Dark Mode only">
            <div className="flex items-center gap-2">
              <Monitor className="w-4 h-4 text-[#A1A1AA]" />
              <span className="text-xs font-bold uppercase tracking-wider text-white bg-white/10 px-3 py-1 rounded-full">
                Dark
              </span>
            </div>
          </SettingRow>

          <SettingRow label="Dashboard Layout" description="Control the density of information on your dashboard">
            <div className="flex items-center gap-2 bg-[#161616] border border-zinc-800 rounded-xl p-1">
              {(["compact", "comfortable", "spacious"] as const).map((layout) => (
                <button
                  key={layout}
                  onClick={() => saveSection("general", { dashboard_layout: layout })}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    settings.dashboardLayout === layout
                      ? "bg-white text-black"
                      : "text-[#A1A1AA] hover:text-white"
                  }`}
                >
                  {layout.charAt(0).toUpperCase() + layout.slice(1)}
                </button>
              ))}
            </div>
          </SettingRow>
        </div>
      </SettingCard>
    </SettingSection>
  );
}
