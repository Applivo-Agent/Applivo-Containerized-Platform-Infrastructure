"use client";

import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import { subscriptionsApi, quotasApi } from "./api";
import { useAuth } from "./auth";

export type PlanTier = "starter" | "pro" | "premium" | "none";

export interface Subscription {
  id: string;
  plan: PlanTier;
  status: string;
  start_date: string;
  end_date: string | null;
  daily_limit: number;
}

export interface QuotaStatus {
  allowed: boolean;
  plan: PlanTier;
  limit: number;
  used: number;
  remaining: number;
}

interface SubscriptionContextType {
  subscription: Subscription | null;
  quota: QuotaStatus | null;
  plan: PlanTier;
  isActive: boolean;
  isPro: boolean;
  isPremium: boolean;
  canAccess: (feature: Feature) => boolean;
  isLoading: boolean;
  refresh: () => Promise<void>;
}

// Feature gating matrix
export type Feature =
  | "jobs" | "applications" | "resumes" | "profile"
  | "settings" | "analytics" | "chat" | "dashboard" | "connect"
  | "cover_letters" | "interviews" | "skill_gaps" | "email_monitor"
  | "follow_ups" | "market_insights" | "advanced_analytics"
  | "priority_queue" | "telegram_notifications";

const FEATURE_REQUIREMENTS: Record<Feature, PlanTier[]> = {
  // All plans
  jobs: ["starter", "pro", "premium"],
  applications: ["starter", "pro", "premium"],
  resumes: ["starter", "pro", "premium"],
  profile: ["starter", "pro", "premium"],
  settings: ["starter", "pro", "premium"],
  analytics: ["starter", "pro", "premium"],
  chat: ["starter", "pro", "premium"],
  dashboard: ["starter", "pro", "premium"],
  connect: ["starter", "pro", "premium"],
  // Pro+
  cover_letters: ["pro", "premium"],
  interviews: ["pro", "premium"],
  skill_gaps: ["pro", "premium"],
  email_monitor: ["pro", "premium"],
  follow_ups: ["pro", "premium"],
  priority_queue: ["pro", "premium"],
  telegram_notifications: ["pro", "premium"],
  // Premium only
  market_insights: ["premium"],
  advanced_analytics: ["premium"],
};

export const PLAN_FEATURES: Record<PlanTier, string[]> = {
  none: [],
  starter: [
    "50 daily applications",
    "Analyze budget: 25k tokens/run",
    "Analyze budget: 120k tokens/month",
    "Internshala scraping",
    "Auto-apply bot",
    "Resume upload & management",
    "AI match scoring",
    "Basic analytics",
    "Email notifications",
    "Application tracking (Kanban)",
    "AI Chat assistant (50 messages/month)",
  ],
  pro: [
    "100 daily applications",
    "Analyze budget: 60k tokens/run",
    "Analyze budget: 600k tokens/month",
    "Everything in Starter",
    "Advanced AI analysis",
    "Cover letter generator",
    "Telegram notifications",
    "Interview tracking & prep",
    "Email inbox monitoring (IMAP)",
    "7-day follow-up automation",
    "Priority queue processing",
    "Skill gap analysis",
    "AI Chat assistant (100 messages/month)",
  ],
  premium: [
    "150 daily applications",
    "Analyze budget: 120k tokens/run",
    "Analyze budget: 1.2M tokens/month",
    "AI Chat assistant (150 messages/month)",
    "Everything in Pro",
    "Highest priority queue",
    "Advanced analytics",
    "Market insights & salary data",
    "Resume performance ranking",
    "Interview conversion funnel",
    "Dedicated support",
  ],
};

export const PLAN_PRICES: Record<PlanTier, number> = {
  none: 0,
  starter: 19900,    // ₹199
  pro: 39900,        // ₹399
  premium: 59900,    // ₹599
};

export const PLAN_ANALYZE_BUDGETS: Record<Exclude<PlanTier, "none">, {
  run_limit_tokens: number;
  monthly_limit_tokens: number;
  daily_plan_tokens: number;
}> = {
  starter: {
    run_limit_tokens: 25000,
    monthly_limit_tokens: 120000,
    daily_plan_tokens: 4000,
  },
  pro: {
    run_limit_tokens: 60000,
    monthly_limit_tokens: 600000,
    daily_plan_tokens: 20000,
  },
  premium: {
    run_limit_tokens: 120000,
    monthly_limit_tokens: 1200000,
    daily_plan_tokens: 40000,
  },
};

export function getPlanAnalyzeBudget(plan: PlanTier | null | undefined) {
  if (!plan || plan === "none") return null;
  return PLAN_ANALYZE_BUDGETS[plan];
}

const SubscriptionContext = createContext<SubscriptionContextType | null>(null);

export function SubscriptionProvider({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated } = useAuth();
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [quota, setQuota] = useState<QuotaStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const normalizePlan = (raw: unknown): PlanTier => {
    if (raw === null || raw === undefined) return "none";
    const text = String(raw).toLowerCase();
    const value = text.includes(".") ? text.split(".").pop() || "" : text;
    if (value === "starter" || value === "pro" || value === "premium") return value;
    return "none";
  };

  const normalizeStatus = (raw: unknown): string => {
    if (raw === null || raw === undefined) return "";
    const text = String(raw).toLowerCase();
    return text.includes(".") ? text.split(".").pop() || "" : text;
  };

  const normalizeSubscriptionResponse = (data: unknown): Subscription | null => {
    if (!data) return null;

    if (typeof data !== "object" || data === null) return null;
    const root = data as Record<string, unknown>;
    const candidateRaw = (root.subscription as Record<string, unknown> | undefined) ?? root;
    const candidate = candidateRaw as Record<string, unknown>;
    if (!candidate.plan) return null;

    const planValue =
      typeof candidate.plan === "object" && candidate.plan !== null
        ? (candidate.plan as Record<string, unknown>).value ?? candidate.plan
        : candidate.plan;
    const statusValue =
      typeof candidate.status === "object" && candidate.status !== null
        ? (candidate.status as Record<string, unknown>).value ?? candidate.status
        : candidate.status;

    const normalizedPlan = normalizePlan(planValue);
    const normalizedStatus = normalizeStatus(statusValue);

    return {
      id: String(candidate.id ?? ""),
      plan: normalizedPlan,
      status: normalizedStatus,
      start_date: typeof candidate.start_date === "string" ? candidate.start_date : null,
      end_date: typeof candidate.end_date === "string" ? candidate.end_date : null,
      daily_limit: Number(candidate.daily_limit ?? 0),
    } as Subscription;
  };

  const refresh = useCallback(async () => {
    if (!isAuthenticated) return;
    try {
      const [subRes, quotaRes] = await Promise.allSettled([
        subscriptionsApi.current(),
        quotasApi.status(),
      ]);
      if (subRes.status === "fulfilled") {
        setSubscription(normalizeSubscriptionResponse(subRes.value.data));
      }
      if (quotaRes.status === "fulfilled") setQuota(quotaRes.value.data);
    } catch {
      // Not subscribed yet
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (isAuthenticated) {
      refresh();
    } else {
      setSubscription(null);
      setQuota(null);
      setIsLoading(false);
    }
  }, [isAuthenticated, refresh]);

  useEffect(() => {
    if (!isAuthenticated) return;

    const handleFocus = () => {
      refresh();
    };

    const handleVisibilityChange = () => {
      if (!document.hidden) {
        refresh();
      }
    };

    window.addEventListener("focus", handleFocus);
    document.addEventListener("visibilitychange", handleVisibilityChange);

    const interval = window.setInterval(() => {
      refresh();
    }, 60000);

    return () => {
      window.removeEventListener("focus", handleFocus);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      window.clearInterval(interval);
    };
  }, [isAuthenticated, refresh]);

  const isSuper = user?.is_superuser ?? false;
  const hasActiveStatus = normalizeStatus(subscription?.status) === "active";
  const plan = (isSuper ? "premium" : (
    hasActiveStatus
      ? normalizePlan(subscription?.plan)
      : "none"
  )) as PlanTier;
  const isActive = isSuper || hasActiveStatus;
  const isPro = isSuper || plan === "pro" || plan === "premium";
  const isPremium = isSuper || plan === "premium";

  const canAccess = (feature: Feature): boolean => {
    if (isSuper) return true;
    if (!isActive) return false;
    return FEATURE_REQUIREMENTS[feature]?.includes(plan) ?? false;
  };

  return (
    <SubscriptionContext.Provider
      value={{
        subscription,
        quota,
        plan,
        isActive,
        isPro,
        isPremium,
        canAccess,
        isLoading,
        refresh,
      }}
    >
      {children}
    </SubscriptionContext.Provider>
  );
}

export function useSubscription() {
  const ctx = useContext(SubscriptionContext);
  if (!ctx) throw new Error("useSubscription must be used inside SubscriptionProvider");
  return ctx;
}
