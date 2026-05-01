"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { useSubscription } from "@/lib/subscription";
import type { Feature } from "@/lib/subscription";

interface GuardProps {
  children: React.ReactNode;
  feature?: Feature;
  requireAdmin?: boolean;
}

export function AuthGuard({ children, feature, requireAdmin }: GuardProps) {
  const { isAuthenticated, isLoading, user } = useAuth();
  const { canAccess, isLoading: subLoading } = useSubscription();
  const router = useRouter();

  useEffect(() => {
    if (isLoading || subLoading) return;
    if (!isAuthenticated) {
      router.replace("/login");
      return;
    }
    if (requireAdmin && !user?.is_superuser) {
      router.replace("/dashboard");
      return;
    }
  }, [isAuthenticated, isLoading, subLoading, router, requireAdmin, user]);

  if (isLoading || subLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-2 border-brand-primary border-t-transparent animate-spin" />
          <p className="text-muted-foreground text-sm">Loading Applivo…</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) return null;
  if (requireAdmin && !user?.is_superuser) return null;

  // Feature locked — show upgrade prompt
  if (feature && !canAccess(feature)) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="-card p-10 text-center max-w-md">
          <div className="w-16 h-16 rounded-full bg-white text-black/20 flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">🔒</span>
          </div>
          <h2 className="text-xl font-semibold mb-2">Upgrade Required</h2>
          <p className="text-muted-foreground mb-6 text-sm">
            This feature requires a higher subscription plan.
          </p>
          <a
            href="/pricing"
            className="inline-flex items-center gap-2 px-6 py-2.5 bg-white text-black text-white rounded-lg hover:bg-white text-black/90 transition-colors text-sm font-medium"
          >
            View Plans
          </a>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
