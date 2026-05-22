"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { subscriptionsApi, paymentsApi } from "@/lib/api";
import { useSubscription, PLAN_FEATURES, PLAN_PRICES, PlanTier } from "@/lib/subscription";
import { useAuth } from "@/lib/auth";
import { cn, formatDate } from "@/lib/utils";
import { CreditCard, Check, ShieldAlert, Sparkles, Crown, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";

function paymentStatusMeta(status: unknown): { label: string; className: string } {
  const normalized = String(status || "").toLowerCase();
  if (normalized === "captured") {
    return { label: "Paid", className: "text-emerald-400" };
  }
  if (normalized === "failed") {
    return { label: "Failed", className: "text-red-400" };
  }
  if (normalized === "refunded") {
    return { label: "Refunded", className: "text-amber-300" };
  }
  if (normalized === "created" || normalized === "authorized" || normalized === "pending") {
    return { label: "Not Paid", className: "text-amber-300" };
  }
  return { label: normalized ? normalized : "Unknown", className: "text-zinc-400" };
}

function formatINRFromPaise(amount: unknown): string {
  const value = Number(amount || 0);
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(Math.round(value / 100));
}

function PaymentHistory({ payments }: { payments: any[] }) {
  if (!payments.length) {
    return (
      <div className="bg-[#0b0b0f] border border-white/5 rounded-2xl p-6 text-sm text-zinc-500">
        No payment history yet.
      </div>
    );
  }

  return (
    <div className="bg-[#0b0b0f] border border-white/5 rounded-2xl p-6">
      <h3 className="text-sm font-medium uppercase tracking-wide text-gray-400 mb-5 px-1">Payment History</h3>
      <div className="space-y-3">
        {payments.map((payment) => (
          (() => {
            const statusMeta = paymentStatusMeta(payment.status);
            return (
          <div key={payment.id} className="flex flex-col gap-2 rounded-xl border border-white/5 bg-white/[0.02] p-4 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="text-sm font-semibold text-white">{String(payment.plan || "plan").toUpperCase()}</div>
              <div className="mt-1 text-[11px] text-zinc-500 break-all">
                Transaction ID: {payment.transaction_id || payment.razorpay_payment_id || payment.razorpay_order_id || payment.id}
              </div>
            </div>
            <div className="flex items-center gap-4 text-[11px] text-zinc-400">
              <span className="font-semibold text-white">{formatINRFromPaise(payment.amount)}</span>
              <span className={statusMeta.className}>{statusMeta.label}</span>
              <span>{new Date(payment.created_at).toLocaleString()}</span>
            </div>
          </div>
            );
          })()
        ))}
      </div>
    </div>
  );
}

export default function SubscriptionPage() {
  const { subscription: sub, plan: currentPlan, isActive, quota, refresh } = useSubscription();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const { data: historyData } = useQuery({
    queryKey: ["payment-history"],
    queryFn: () => paymentsApi.history().then(r => r.data),
  });

  const [razorpayLoaded, setRazorpayLoaded] = useState(false);

  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.async = true;
    script.onload = () => setRazorpayLoaded(true);
    document.body.appendChild(script);
    return () => {
      if (document.body.contains(script)) {
        document.body.removeChild(script);
      }
    };
  }, []);

  const createOrderMut = useMutation({
    mutationFn: (plan: PlanTier) => paymentsApi.createOrder({ plan }),
    onSuccess: async (res) => {
      if (!razorpayLoaded) {
        alert("Payment system loading, please try again");
        return;
      }
      const { order_id, key_id, amount } = res.data;
      const rzp = new (window as any).Razorpay({
        key: key_id,
        amount,
        currency: "INR",
        name: "Applivo",
        order_id: order_id,
        handler: async (response: any) => {
          try {
            await paymentsApi.verify({
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_order_id: response.razorpay_order_id,
              razorpay_signature: response.razorpay_signature,
            });
            refresh();
            queryClient.invalidateQueries({ queryKey: ["subscription"] });
            queryClient.invalidateQueries({ queryKey: ["payment-history"] });
          } catch (err) {
            alert("Payment verification failed. Please contact support.");
          }
        },
        prefill: { email: user?.email },
        theme: { color: "#ffffff" },
      });
      rzp.open();
    },
    onError: (err: any) => {
      alert(err.response?.data?.detail || "Failed to create order. Please try again.");
    },
  });

  const cancelMut = useMutation({
    mutationFn: () => subscriptionsApi.cancel(),
    onSuccess: () => {
      refresh();
      queryClient.invalidateQueries({ queryKey: ["subscription"] });
    },
    onError: () => alert("Failed to cancel. Contact support."),
  });

  const handleCheckout = (planTier: PlanTier) => {
    if (currentPlan === planTier) return;
    createOrderMut.mutate(planTier);
  };

  const handleCancel = () => {
    if (confirm("Are you sure you want to cancel your subscription?")) {
      cancelMut.mutate();
    }
  };

  const plans: { tier: PlanTier; label: string; popular?: boolean }[] = [
    { tier: "starter", label: "Starter" },
    { tier: "pro", label: "Pro", popular: true },
    { tier: "premium", label: "Premium" },
  ];

  const allPayments = historyData?.payments ?? [];
  const latestPayment = allPayments[0] ?? null;
  const olderPayments = allPayments.slice(1);
  const latestPaymentMeta = paymentStatusMeta(latestPayment?.status);

  const trialDaysRemaining = sub?.trial_days_remaining ?? 0;
  const isTrialExpired = sub?.status === "TRIAL_EXPIRED";
  const isOnTrial = sub?.status === "TRIAL" && trialDaysRemaining > 0;
  const noAutopay = sub?.status === "TRIAL" && !sub?.autopay_enabled;

  return (
    <div className="max-w-5xl space-y-6">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-[#242424] border border-white/[0.08] rounded-lg">
          <CreditCard className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Subscription</h1>
          <p className="text-sm text-zinc-400 mt-1">Manage your Applivo billing loop and quotas</p>
        </div>
      </div>

      {/* Trial Banners */}
      {isOnTrial && (
        <div className="bg-amber-950/40 border border-amber-700/50 rounded-2xl p-4 md:p-5 shadow-lg">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-sm font-bold text-amber-100 flex items-center gap-2">
                <span>⏳</span> You are on a 7-day free trial
              </p>
              <p className="text-sm text-amber-200/80 mt-2">
                {trialDaysRemaining} {trialDaysRemaining === 1 ? "day" : "days"} remaining. Your card will be charged ₹199 when the trial ends.
              </p>
            </div>
            <button
              onClick={() => alert("Razorpay subscription management coming soon")}
              className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white text-sm font-semibold rounded-lg transition whitespace-nowrap"
            >
              Manage Autopay
            </button>
          </div>
        </div>
      )}

      {noAutopay && (
        <div className="bg-orange-950/40 border border-orange-700/50 rounded-2xl p-4 md:p-5 shadow-lg">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-sm font-bold text-orange-100 flex items-center gap-2">
                <span>⚠️</span> No payment method saved
              </p>
              <p className="text-sm text-orange-200/80 mt-2">
                Add your card to avoid losing access after your trial ends in {trialDaysRemaining} days.
              </p>
            </div>
            <button
              onClick={() => alert("Start autopay flow coming soon")}
              className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white text-sm font-semibold rounded-lg transition whitespace-nowrap"
            >
              Add Card
            </button>
          </div>
        </div>
      )}

      {isTrialExpired && (
        <div className="bg-red-950/40 border border-red-700/50 rounded-2xl p-4 md:p-5 shadow-lg">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-sm font-bold text-red-100 flex items-center gap-2">
                <span>❌</span> Your free trial has ended
              </p>
              <p className="text-sm text-red-200/80 mt-2">
                Subscribe to continue using Applivo. Choose a plan and start your paid subscription.
              </p>
            </div>
            <button
              onClick={() => window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" })}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-semibold rounded-lg transition whitespace-nowrap"
            >
              Subscribe Now
            </button>
          </div>
        </div>
      )}

      {latestPayment && (
        <div className="bg-[#232327] border border-white/10 rounded-2xl p-4 md:p-5 shadow-lg">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400">Latest Payment</p>
              <p className="text-sm font-semibold text-white mt-1">
                {String(latestPayment.plan || "starter").toUpperCase()} • {formatINRFromPaise(latestPayment.amount)}
              </p>
              <p className="text-[11px] text-zinc-400 mt-1 break-all">
                Transaction ID: {latestPayment.transaction_id || latestPayment.razorpay_payment_id || latestPayment.razorpay_order_id || latestPayment.id}
              </p>
            </div>
            <div className="text-left md:text-right">
              <p className={cn(
                "text-sm font-bold uppercase tracking-wider",
                latestPaymentMeta.className
              )}>
                {latestPaymentMeta.label}
              </p>
              <p className="text-[11px] text-zinc-400 mt-1">{new Date(latestPayment.created_at).toLocaleString()}</p>
            </div>
          </div>
          {!isActive && String(latestPayment?.status || "").toLowerCase() === "captured" && (
            <p className="mt-3 text-[11px] text-zinc-300 border-t border-white/10 pt-3">
              Payment is captured. Plan activation is syncing. Please refresh once or wait a moment.
            </p>
          )}
        </div>
      )}

      {isActive && sub ? (
        <div className="bg-[#161616] p-4 flex items-start justify-between border border-zinc-800 border-l-4 border-l-white rounded-2xl shadow-lg">
          <div>
            <div className="flex items-center gap-2.5 mb-1.5">
              <h2 className="text-lg font-bold capitalize text-white">{sub.plan} Plan</h2>
              <span className="px-2 py-0.5 bg-white text-black text-[9px] font-black rounded-full uppercase tracking-wider">Active</span>
            </div>
            <p className="text-[12px] text-zinc-400 max-w-lg">
              Active until {sub.end_date ? formatDate(sub.end_date) : "the end of time"}. Quota: {quota?.limit || "unlimited"}/day.
            </p>
          </div>
          <button
            onClick={handleCancel}
            disabled={cancelMut.isPending}
            className="px-3 py-1.5 border border-red-500/20 text-red-500 hover:bg-red-500/5 rounded-lg text-xs transition-colors disabled:opacity-80 disabled:cursor-not-allowed font-bold uppercase tracking-wider"
          >
            {cancelMut.isPending ? "..." : "Cancel"}
          </button>
        </div>
      ) : (
        <div className="flex items-center gap-3 p-4 bg-[#161616] border border-zinc-800 rounded-xl shadow-lg">
          <ShieldAlert className="w-4 h-4 text-white shrink-0" />
          <p className="text-[12px] font-medium text-zinc-400">Upgrade to unlock the autonomous agent.</p>
        </div>
      )}

      {/* Upgrade Grid */}
      <div className="grid md:grid-cols-3 gap-4 pt-2">
        {plans.map(p => (
          <div key={p.tier} className={cn("relative bg-[#1c1c1e] p-5 flex flex-col border transition-all hover:-translate-y-0.5 duration-300 rounded-2xl shadow-lg",
            p.popular ? "border-white/20 ring-1 ring-white/10" : "border-white/5 hover:border-white/20",
            currentPlan === p.tier ? "opacity-70 grayscale-[0.5]" : "")}>

            {currentPlan === p.tier && (
              <div className="absolute -top-2.5 right-4 text-[9px] font-black px-2 py-0.5 bg-white text-black rounded-full z-10 uppercase tracking-widest shadow-xl">
                Current
              </div>
            )}

            <div className="flex items-center justify-between mb-6">
              <div className="flex-1">
                <div className="flex items-center gap-1.5 mb-1">
                  <h3 className="font-bold text-base text-white">{p.label}</h3>
                  {p.tier === 'premium' && <Crown className="w-3.5 h-3.5 text-white" />}
                </div>
                <div className="flex items-baseline gap-1">
                  <span className="text-[28px] font-black text-white tracking-tighter">{formatINRFromPaise(PLAN_PRICES[p.tier])}</span>
                  <span className="text-zinc-500 text-[9px] font-bold uppercase tracking-wider">/mo</span>
                </div>
              </div>
              {p.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-white text-black text-[9px] font-black uppercase tracking-widest shadow-xl flex items-center gap-1">
                  <Sparkles className="w-2.5 h-2.5" /> Popular
                </div>
              )}
            </div>

            <ul className="space-y-2 mb-8 flex-1">
              {PLAN_FEATURES[p.tier].map(f => (
                <li key={f} className="flex gap-2.5 items-start">
                  <div className="mt-0.5 w-4 h-4 rounded-full bg-white/5 flex items-center justify-center shrink-0">
                    <Check className="w-2.5 h-2.5 text-white/50" />
                  </div>
                  <span className="text-zinc-500 font-medium text-[11px] leading-snug">{f}</span>
                </li>
              ))}
            </ul>

            <button
              onClick={() => handleCheckout(p.tier)}
              disabled={currentPlan === p.tier || createOrderMut.isPending}
              className={cn("w-full py-2.5 rounded-lg text-[11px] font-black transition-all disabled:opacity-50 disabled:cursor-not-allowed uppercase tracking-widest",
                currentPlan === p.tier ? "bg-white/5 border border-white/10 text-zinc-600" : "bg-white text-black hover:bg-zinc-200 shadow-xl hover:scale-[1.02] active:scale-[0.98]"
              )}>
              {createOrderMut.isPending ? "..." : currentPlan === p.tier ? "Current" : `Upgrade`}
            </button>
          </div>
        ))}
      </div>

      {olderPayments.length > 0 && <PaymentHistory payments={olderPayments} />}
    </div>
  );
}
