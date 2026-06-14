"use client";

import { SettingSection, SettingCard, SettingRow } from "@/components/settings/card";
import { Toggle } from "@/components/settings/toggle";
import { useSettings } from "@/lib/settings-context";
import { Bell, Radio, Hash, TestTube } from "lucide-react";
import { useState } from "react";
import { settingsV2Api } from "@/lib/api";
import { toast } from "sonner";

export function NotificationsSection() {
  const { settings, saveSection } = useSettings();
  const [testing, setTesting] = useState(false);

  const saveChannels = (key: string, value: boolean) => {
    saveSection("notifications", {
      channels: { ...settings.channels, [key]: value },
    });
  };

  const saveTypes = (key: string, value: boolean) => {
    const backendKey = key
      .replace(/([A-Z])/g, "_$1")
      .toLowerCase();
    saveSection("notifications", {
      types: {
        jobs_found: settings.types.jobsFound,
        application_submitted: settings.types.applicationSubmitted,
        interview_invitation: settings.types.interviewInvitation,
        resume_analysis_completed: settings.types.resumeAnalysisCompleted,
        weekly_summary: settings.types.weeklySummary,
        ai_agent_alerts: settings.types.aiAgentAlerts,
        workflow_failures: settings.types.workflowFailures,
        [backendKey]: value,
      },
    });
  };

  const saveFrequency = (freq: string) => {
    saveSection("notifications", { frequency: freq });
  };

  const sendTest = async (channel: string) => {
    setTesting(true);
    try {
      const res = await settingsV2Api.testNotification(channel);
      toast.success(res.data.message ?? "Test sent!");
    } catch {
      toast.error("Failed to send test notification");
    } finally {
      setTesting(false);
    }
  };

  return (
    <SettingSection>
      <SettingCard
        title="Notification Channels"
        description="Choose how you want to receive alerts from your AI agent"
        icon={<Radio className="w-4 h-4 text-white" />}
      >
        <div className="space-y-1">
          <SettingRow label="Email Notifications" description="Receive daily summaries and critical alerts via email">
            <Toggle checked={settings.channels.email} onChange={(v) => saveChannels("email", v)} />
          </SettingRow>
          <SettingRow label="Telegram Notifications" description="Real-time alerts delivered to your Telegram">
            <Toggle checked={settings.channels.telegram} onChange={(v) => saveChannels("telegram", v)} />
          </SettingRow>
          <SettingRow label="Discord" description="Send notifications to a Discord channel (coming soon)">
            <Toggle checked={settings.channels.discord} onChange={(v) => saveChannels("discord", v)} disabled />
          </SettingRow>
          <SettingRow label="Slack" description="Integrate with your Slack workspace (coming soon)">
            <Toggle checked={settings.channels.slack} onChange={(v) => saveChannels("slack", v)} disabled />
          </SettingRow>
        </div>
      </SettingCard>

      <SettingCard
        title="Notification Types"
        description="Fine-tune which events trigger notifications"
        icon={<Bell className="w-4 h-4 text-white" />}
      >
        <div className="space-y-1">
          <SettingRow label="Jobs Found" description="Alert when new matching jobs are discovered">
            <Toggle checked={settings.types.jobsFound} onChange={(v) => saveTypes("jobsFound", v)} />
          </SettingRow>
          <SettingRow label="Application Submitted" description="Confirmations when your agent submits applications">
            <Toggle checked={settings.types.applicationSubmitted} onChange={(v) => saveTypes("applicationSubmitted", v)} />
          </SettingRow>
          <SettingRow label="Interview Invitation" description="Instant alert when you receive an interview request">
            <Toggle checked={settings.types.interviewInvitation} onChange={(v) => saveTypes("interviewInvitation", v)} />
          </SettingRow>
          <SettingRow label="Resume Analysis Completed" description="Notify when AI finishes analyzing your resume">
            <Toggle checked={settings.types.resumeAnalysisCompleted} onChange={(v) => saveTypes("resumeAnalysisCompleted", v)} />
          </SettingRow>
          <SettingRow label="Weekly Summary" description="Digest of all activity from the past week">
            <Toggle checked={settings.types.weeklySummary} onChange={(v) => saveTypes("weeklySummary", v)} />
          </SettingRow>
          <SettingRow label="AI Agent Alerts" description="Warnings when the agent needs your attention">
            <Toggle checked={settings.types.aiAgentAlerts} onChange={(v) => saveTypes("aiAgentAlerts", v)} />
          </SettingRow>
          <SettingRow label="Workflow Failures" description="Critical errors that require immediate action">
            <Toggle checked={settings.types.workflowFailures} onChange={(v) => saveTypes("workflowFailures", v)} />
          </SettingRow>
        </div>
      </SettingCard>

      <SettingCard
        title="Digest Frequency"
        description="How often non-urgent notifications are batched"
        icon={<Hash className="w-4 h-4 text-white" />}
      >
        <div className="flex gap-2">
          {(["instant", "hourly", "daily"] as const).map((freq) => (
            <button
              key={freq}
              onClick={() => saveFrequency(freq)}
              className={`flex-1 py-2.5 rounded-xl text-xs font-bold uppercase tracking-wider transition-all border ${
                settings.frequency === freq
                  ? "bg-white text-black border-white shadow-lg"
                  : "bg-[#161616] text-[#A1A1AA] border-zinc-800 hover:border-white/30"
              }`}
            >
              {freq === "instant" ? "Instant" : freq === "hourly" ? "Hourly Digest" : "Daily Digest"}
            </button>
          ))}
        </div>
      </SettingCard>

      <SettingCard
        title="Test Notifications"
        description="Send a test notification to verify your channels are working"
        icon={<TestTube className="w-4 h-4 text-white" />}
      >
        <div className="flex gap-2">
          <button
            onClick={() => sendTest("email")}
            disabled={testing}
            className="flex-1 py-2.5 bg-[#161616] border border-zinc-800 rounded-xl text-sm font-medium text-white hover:bg-[#242424] hover:border-white/20 transition-all disabled:opacity-50"
          >
            Test Email
          </button>
          {settings.channels.telegram && (
            <button
              onClick={() => sendTest("telegram")}
              disabled={testing}
              className="flex-1 py-2.5 bg-[#161616] border border-zinc-800 rounded-xl text-sm font-medium text-white hover:bg-[#242424] hover:border-white/20 transition-all disabled:opacity-50"
            >
              Test Telegram
            </button>
          )}
        </div>
      </SettingCard>
    </SettingSection>
  );
}
