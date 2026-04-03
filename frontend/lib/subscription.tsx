"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
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
    "150 daily applications",
    "Internshala scraping",
    "Auto-apply bot",
    "Resume upload & management",
    "AI match scoring",
    "Basic analytics",
    "Email notifications",
    "Application tracking (Kanban)",
    "AI Chat assistant",
  ],
  pro: [
    "250 daily applications",
    "Everything in Starter",
    "Full AI analysis (LLaMA-70B)",
    "Cover letter generator",
    "Telegram notifications",
    "Interview tracking & prep",
    "Email inbox monitoring (IMAP)",
    "7-day follow-up automation",
    "Priority queue processing",
    "Skill gap analysis",
  ],
  premium: [
    "500 daily applications",
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
  starter: 200,
  pro: 400,
  premium: 800,
};

const SubscriptionContext = createContext<SubscriptionContextType | null>(null);

export function SubscriptionProvider({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated } = useAuth();
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [quota, setQuota] = useState<QuotaStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refresh = async () => {
    if (!isAuthenticated) return;
    try {
      const [subRes, quotaRes] = await Promise.allSettled([
        subscriptionsApi.current(),
        quotasApi.status(),
      ]);
      if (subRes.status === "fulfilled") setSubscription(subRes.value.data);
      if (quotaRes.status === "fulfilled") setQuota(quotaRes.value.data);
    } catch {
      // Not subscribed yet
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      refresh();
    } else {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  const isSuper = user?.is_superuser ?? false;
  const plan = isSuper ? "premium" : ((subscription?.status === "active" ? subscription?.plan : "none") ?? "none");
  const isActive = isSuper || subscription?.status === "active";
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
