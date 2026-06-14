"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Settings2 } from "lucide-react";
import { SettingsProvider } from "@/lib/settings-context";
import { SettingsSidebar } from "@/components/settings/sidebar";
import { SaveStatus } from "@/components/settings/save-status";
import { GeneralSection } from "./_sections/general";
import { NotificationsSection } from "./_sections/notifications";
import { JobAutomationSection } from "./_sections/job-automation";
import { AgentStrategySection } from "./_sections/agent-strategy";
import { AISettingsSection } from "./_sections/ai-settings";
import { PlatformConnectionsSection } from "./_sections/platform-connections";
import { SecuritySection } from "./_sections/security";
import { AdvancedSection } from "./_sections/advanced";

const sections = [
  { id: "general", label: "General", component: GeneralSection },
  { id: "notifications", label: "Notifications", component: NotificationsSection },
  { id: "job-automation", label: "Job Automation", component: JobAutomationSection },
  { id: "agent-strategy", label: "Agent Strategy", component: AgentStrategySection },
  { id: "ai-settings", label: "AI Settings", component: AISettingsSection },
  { id: "platform-connections", label: "Platforms", component: PlatformConnectionsSection },
  { id: "security", label: "Security", component: SecuritySection },
  { id: "advanced", label: "Advanced", component: AdvancedSection },
];

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("general");

  return (
    <SettingsProvider>
      <div className="max-w-6xl space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-[#242424] border border-white/[0.08] rounded-lg">
              <Settings2 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Settings</h1>
              <p className="text-sm text-zinc-400 mt-1">AI Agent Control Center</p>
            </div>
          </div>
          <SaveStatus />
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          <SettingsSidebar activeTab={activeTab} onTabChange={setActiveTab} sections={sections} />
          <div className="flex-1 min-w-0">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.2 }}
              >
                {sections.map((s) => s.id === activeTab && <s.component key={s.id} />)}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>
    </SettingsProvider>
  );
}
