export interface SettingsState {
  // General
  timezone: string;
  language: string;
  dateFormat: string;
  theme: "dark" | "light" | "system";
  dashboardLayout: "compact" | "comfortable" | "spacious";

  // Notifications
  channels: {
    email: boolean;
    telegram: boolean;
    discord: boolean;
    slack: boolean;
  };
  types: {
    jobsFound: boolean;
    applicationSubmitted: boolean;
    interviewInvitation: boolean;
    resumeAnalysisCompleted: boolean;
    weeklySummary: boolean;
    aiAgentAlerts: boolean;
    workflowFailures: boolean;
  };
  frequency: "instant" | "hourly" | "daily";

  // Job Automation
  autonomousMode: boolean;
  autoScrapeJobs: boolean;
  autoAnalyzeJobs: boolean;
  autoQueueJobs: boolean;
  autoApply: boolean;
  dailyApplicationLimit: number;
  weeklyApplicationLimit: number;
  requireManualApproval: boolean;
  autoApprovalThreshold: number;
  scheduleInterval: "30min" | "1hour" | "6hours" | "daily";

  // Agent Strategy
  strategyMode: "aggressive" | "balanced" | "quality";

  // AI Settings
  aiProvider: "groq" | "gemini" | "openrouter" | "openai" | "anthropic";
  aiModel: string;
  reasoningDepth: "fast" | "balanced" | "deep";
  applicationStyle: "professional" | "technical" | "startup" | "enterprise";
  fallbackEnabled: boolean;
  fallbackStrategy: "fastest" | "balanced" | "best_quality";

  // Platform Connections
  platforms: {
    linkedin: { connected: boolean; lastSync: string | null; health: "healthy" | "warning" | "error" };
    internshala: { connected: boolean; lastSync: string | null; health: "healthy" | "warning" | "error" };
    indeed: { connected: boolean; lastSync: string | null; health: "healthy" | "warning" | "error" };
    naukri: { connected: boolean; lastSync: string | null; health: "healthy" | "warning" | "error" };
  };

  // Security
  twoFactorEnabled: boolean;

  // Advanced
  debugMode: boolean;
  experimentalFeatures: boolean;
}

// ─── Backend ↔ Frontend conversion ──────────────────────────────────────────

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function backendToFrontend(b: Record<string, any>): SettingsState {
  const platforms = b.platforms ?? {};
  const normPlatform = (p: Record<string, unknown> | undefined) => ({
    connected: (p?.connected as boolean) ?? false,
    lastSync: (p?.last_sync as string | null) ?? null,
    health: ((p?.health as string) ?? "error") as "healthy" | "warning" | "error",
  });
  const ch = b.channels ?? {};
  const ty = b.types ?? {};
  return {
    timezone: b.timezone ?? "Asia/Kolkata",
    language: b.language ?? "en",
    dateFormat: b.date_format ?? "DD/MM/YYYY",
    theme: (b.theme ?? "dark") as SettingsState["theme"],
    dashboardLayout: (b.dashboard_layout ?? "comfortable") as SettingsState["dashboardLayout"],
    channels: {
      email: ch.email ?? true,
      telegram: ch.telegram ?? false,
      discord: ch.discord ?? false,
      slack: ch.slack ?? false,
    },
    types: {
      jobsFound: ty.jobs_found ?? true,
      applicationSubmitted: ty.application_submitted ?? true,
      interviewInvitation: ty.interview_invitation ?? true,
      resumeAnalysisCompleted: ty.resume_analysis_completed ?? false,
      weeklySummary: ty.weekly_summary ?? true,
      aiAgentAlerts: ty.ai_agent_alerts ?? true,
      workflowFailures: ty.workflow_failures ?? true,
    },
    frequency: (b.frequency ?? "instant") as SettingsState["frequency"],
    autonomousMode: b.agent_mode === "full_auto",
    autoScrapeJobs: b.auto_scrape_jobs ?? true,
    autoAnalyzeJobs: b.auto_analyze_jobs ?? true,
    autoQueueJobs: b.auto_queue_jobs ?? false,
    autoApply: b.auto_apply ?? false,
    dailyApplicationLimit: b.daily_application_limit ?? 10,
    weeklyApplicationLimit: b.weekly_application_limit ?? 50,
    requireManualApproval: b.require_manual_approval ?? true,
    autoApprovalThreshold: b.auto_approval_threshold ?? 75,
    scheduleInterval: (b.schedule_interval ?? "6hours") as SettingsState["scheduleInterval"],
    strategyMode: (b.agent_strategy ?? "balanced") as SettingsState["strategyMode"],
    aiProvider: (b.ai_provider ?? "openai") as SettingsState["aiProvider"],
    aiModel: b.ai_model ?? "gpt-4o",
    reasoningDepth: (b.reasoning_depth ?? "balanced") as SettingsState["reasoningDepth"],
    applicationStyle: (b.app_gen_style ?? "professional") as SettingsState["applicationStyle"],
    fallbackEnabled: b.fallback_enabled ?? true,
    fallbackStrategy: (b.fallback_strategy ?? "balanced") as SettingsState["fallbackStrategy"],
    platforms: {
      linkedin: normPlatform(platforms.linkedin),
      internshala: normPlatform(platforms.internshala),
      indeed: normPlatform(platforms.indeed),
      naukri: normPlatform(platforms.naukri),
    },
    twoFactorEnabled: b.two_factor_enabled ?? false,
    debugMode: b.debug_mode ?? false,
    experimentalFeatures: b.experimental_features ?? false,
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function frontendToBackend(s: SettingsState): Record<string, any> {
  return {
    timezone: s.timezone,
    language: s.language,
    date_format: s.dateFormat,
    theme: s.theme,
    dashboard_layout: s.dashboardLayout,
    channels: s.channels,
    types: {
      jobs_found: s.types.jobsFound,
      application_submitted: s.types.applicationSubmitted,
      interview_invitation: s.types.interviewInvitation,
      resume_analysis_completed: s.types.resumeAnalysisCompleted,
      weekly_summary: s.types.weeklySummary,
      ai_agent_alerts: s.types.aiAgentAlerts,
      workflow_failures: s.types.workflowFailures,
    },
    frequency: s.frequency,
    agent_mode: s.autonomousMode ? "full_auto" : "manual",
    auto_scrape_jobs: s.autoScrapeJobs,
    auto_analyze_jobs: s.autoAnalyzeJobs,
    auto_queue_jobs: s.autoQueueJobs,
    auto_apply: s.autoApply,
    daily_application_limit: s.dailyApplicationLimit,
    weekly_application_limit: s.weeklyApplicationLimit,
    require_manual_approval: s.requireManualApproval,
    auto_approval_threshold: s.autoApprovalThreshold,
    schedule_interval: s.scheduleInterval,
    agent_strategy: s.strategyMode,
    ai_provider: s.aiProvider,
    ai_model: s.aiModel,
    reasoning_depth: s.reasoningDepth,
    app_gen_style: s.applicationStyle,
    two_factor_enabled: s.twoFactorEnabled,
    debug_mode: s.debugMode,
    experimental_features: s.experimentalFeatures,
  };
}

export const DEFAULT_SETTINGS: SettingsState = {
  timezone: "Asia/Kolkata",
  language: "en",
  dateFormat: "DD/MM/YYYY",
  theme: "dark",
  dashboardLayout: "comfortable",

  channels: { email: true, telegram: false, discord: false, slack: false },
  types: {
    jobsFound: true,
    applicationSubmitted: true,
    interviewInvitation: true,
    resumeAnalysisCompleted: false,
    weeklySummary: true,
    aiAgentAlerts: true,
    workflowFailures: true,
  },
  frequency: "instant",

  autonomousMode: false,
  autoScrapeJobs: true,
  autoAnalyzeJobs: true,
  autoQueueJobs: false,
  autoApply: false,
  dailyApplicationLimit: 10,
  weeklyApplicationLimit: 50,
  requireManualApproval: true,
  autoApprovalThreshold: 75,
  scheduleInterval: "6hours",

  strategyMode: "balanced",

  aiProvider: "groq",
  aiModel: "auto",
  reasoningDepth: "balanced",
  applicationStyle: "professional",
  fallbackEnabled: true,
  fallbackStrategy: "balanced",

  platforms: {
    linkedin: { connected: false, lastSync: null, health: "error" },
    internshala: { connected: false, lastSync: null, health: "error" },
    indeed: { connected: false, lastSync: null, health: "error" },
    naukri: { connected: false, lastSync: null, health: "error" },
  },

  twoFactorEnabled: false,

  debugMode: false,
  experimentalFeatures: false,
};
