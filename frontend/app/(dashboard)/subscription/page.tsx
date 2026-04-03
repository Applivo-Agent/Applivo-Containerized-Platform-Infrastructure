"use client";
import { useQuery } from "@tanstack/react-query";
import { subscriptionsApi } from "@/lib/api";
import { useSubscription, PLAN_FEATURES, PLAN_PRICES, PlanTier } from "@/lib/subscription";
import { cn, formatDate } from "@/lib/utils";
import { CreditCard, Check, ShieldAlert, Sparkles } from "lucide-react";

export default function SubscriptionPage() {
  const { subscription: sub, plan: currentPlan, isActive } = useSubscription();

  const { data: history } = useQuery({
    queryKey: ["payment-history"],
    queryFn: () => subscriptionsApi.current().then(r => r.data), // Mocked for now to avoid 404 if not implemented
  });

  const handleCheckout = (planTier: PlanTier) => {
    alert(`Razorpay checkout mock for ${planTier}. Proceeding to checkout...`);
    // In prod: call paymentsApi.createOrder({ plan: planTier }) then load razorpay sdk with orderId
  };

  const plans: { tier: PlanTier; label: string; popular?: boolean }[] = [
    { tier: "starter", label: "Starter" },
    { tier: "pro", label: "Pro", popular: true },
    { tier: "premium", label: "Premium" },
  ];

  return (
    <div className="max-w-5xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold font-display">Subscription</h1>
        <p className="text-muted-foreground text-sm mt-1">Manage your Applivo billing loop and quotas</p>
      </div>

      {isActive && sub ? (
        <div className="glass-card p-6 flex items-start justify-between border-l-4 border-l-brand-purple">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-xl font-bold capitalize">{sub.plan} Plan</h2>
              <span className="px-2 py-0.5 bg-brand-green/20 text-brand-green text-[10px] font-bold rounded-full uppercase">Active</span>
            </div>
            <p className="text-sm text-muted-foreground max-w-lg mb-4">
              Your subscription is active until {sub.end_date ? formatDate(sub.end_date) : "the end of time"}. You get {sub.daily_limit} applications per day.
            </p>
          </div>
          <button className="px-4 py-2 border border-red-500/30 text-red-400 hover:bg-red-500/10 rounded-lg text-sm transition-colors">
            Cancel Subscription
          </button>
        </div>
      ) : (
        <div className="flex items-center gap-3 p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl">
          <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0" />
          <p className="text-sm font-medium text-amber-400">You are currently on the Free/Trial plan. Upgrade to unlock the autonomous agent.</p>
        </div>
      )}

      {/* Upgrade Grid */}
      <div className="grid md:grid-cols-3 gap-6">
        {plans.map(p => (
           <div key={p.tier} className={cn("relative glass-card p-6 flex flex-col border-2 transition-all",
             p.popular ? "border-brand-purple glow-border-purple scale-[1.02]" : "border-border hover:border-brand-purple/50",
             currentPlan === p.tier ? "opacity-60 grayscale" : "")}>
             {p.popular && <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 bg-brand-purple text-white text-[10px] font-bold uppercase rounded-full tracking-wider flex items-center gap-1"><Sparkles className="w-3 h-3" /> Most Popular</div>}
             {currentPlan === p.tier && <div className="absolute top-3 right-3 text-[10px] font-bold px-2 py-0.5 bg-muted rounded">CURRENT</div>}
             
             <h3 className="font-bold text-lg font-display mb-1">{p.label}</h3>
             <div className="flex items-baseline gap-1 mb-6">
                <span className="text-3xl font-extrabold">₹{PLAN_PRICES[p.tier]}</span>
                <span className="text-muted-foreground text-xs">/month</span>
             </div>

             <ul className="space-y-3 mb-8 flex-1">
               {PLAN_FEATURES[p.tier].map(f => (
                 <li key={f} className="flex gap-2 text-xs leading-tight">
                   <Check className="w-3.5 h-3.5 text-brand-green shrink-0 mt-0.5" />
                   <span className="text-muted-foreground">{f}</span>
                 </li>
               ))}
             </ul>

             <button
               onClick={() => handleCheckout(p.tier)}
               disabled={currentPlan === p.tier}
               className={cn("w-full py-2.5 rounded-lg text-sm font-medium transition-colors disabled:cursor-not-allowed",
                 p.popular ? "bg-brand-purple text-white hover:bg-brand-purple/90" : "bg-muted hover:bg-white/5",
                 currentPlan === p.tier ? "opacity-50" : ""
               )}>
               {currentPlan === p.tier ? "Current Plan" : `Upgrade to ${p.label}`}
             </button>
           </div>
        ))}
      </div>
    </div>
  );
}
