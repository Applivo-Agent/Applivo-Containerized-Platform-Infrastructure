"use client";
import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/lib/api";
import { useSubscription } from "@/lib/subscription";
import { TrendingUp, Briefcase, DollarSign, MapPin, Users , Loader2} from "lucide-react";

export default function MarketPage() {
  const { isPremium, isLoading: subLoading } = useSubscription();

  const { data: market, isLoading } = useQuery({
    queryKey: ["market-insights"],
    queryFn: () => analyticsApi.market().then((r) => r.data),
    enabled: isPremium,
    staleTime: 10 * 60 * 1000,
  });

  if (subLoading || isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-brand-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isPremium) {
    return (
      <div className="-card p-12 text-center">
        <TrendingUp className="w-12 h-12 text-white mx-auto mb-4" />
        <h2 className="text-xl font-bold mb-2">Premium Feature</h2>
        <p className="text-muted-foreground">Upgrade to Premium to access market insights.</p>
      </div>
    );
  }

  if (!market) {
    return (
      <div className="-card p-12 text-center">
        <p className="text-muted-foreground">No market data available. Run the agent first to collect data.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-[#242424] border border-white/[0.08] rounded-lg">
          <TrendingUp className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Market Insights</h1>
          <p className="text-sm text-zinc-400 mt-1">Latest job market intelligence based on your target roles</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="-card p-5">
          <div className="flex items-center gap-2 mb-2">
            <Briefcase className="w-4 h-4 text-white" />
            <span className="text-xs text-muted-foreground">Jobs Analyzed</span>
          </div>
          <p className="text-2xl font-bold">{market.total_jobs_analyzed?.toLocaleString() || 0}</p>
        </div>
        <div className="-card p-5">
          <div className="flex items-center gap-2 mb-2">
            <DollarSign className="w-4 h-4 text-emerald-400" />
            <span className="text-xs text-muted-foreground">Avg Salary Range</span>
          </div>
          <p className="text-2xl font-bold">
            ₹{Math.round((market.salary_data?.min_salary || 1400000) / 100000)}L - 
            ₹{Math.round((market.salary_data?.max_salary || 2200000) / 100000)}L
          </p>
        </div>
        <div className="-card p-5">
          <div className="flex items-center gap-2 mb-2">
            <MapPin className="w-4 h-4 text-amber-400" />
            <span className="text-xs text-muted-foreground">Top Work Mode</span>
          </div>
          <p className="text-2xl font-bold capitalize">
            {market.by_work_mode ? Object.entries(market.by_work_mode as Record<string, number>).sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A' : 'N/A'}
          </p>
        </div>
        <div className="-card p-5">
          <div className="flex items-center gap-2 mb-2">
            <Users className="w-4 h-4 text-cyan-400" />
            <span className="text-xs text-muted-foreground">Top Companies</span>
          </div>
          <p className="text-2xl font-bold">{market.top_companies_hiring?.length || 0}</p>
        </div>
      </div>

      {market.top_skills?.length > 0 && (
        <div className="-card p-6">
          <h2 className="font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="w-4 h-4" /> Top Skills in Demand
          </h2>
          <div className="flex flex-wrap gap-2">
            {(market.top_skills as string[]).map((skill: string, i: number) => (
              <span key={i} className="px-3 py-1 bg-white text-black/20 text-white-light rounded-full text-sm">
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {market.emerging_roles?.length > 0 && (
        <div className="-card p-6">
          <h2 className="font-semibold mb-4">Emerging Roles</h2>
          <div className="space-y-2">
            {(market.emerging_roles as string[]).map((role: string, i: number) => (
              <div key={i} className="flex items-center gap-2 text-sm">
                <span className="w-2 h-2 bg-emerald-400 rounded-full" />
                <span>{role}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="-card p-6">
        <h2 className="font-semibold mb-4">Work Mode Distribution</h2>
        {market.by_work_mode && (
          <div className="space-y-3">
            {Object.entries(market.by_work_mode as Record<string, number>).map(([mode, count]) => (
              <div key={mode}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="capitalize">{mode}</span>
                  <span className="text-muted-foreground">{count} jobs</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-white text-black rounded-full" 
                    style={{ width: `${(count / (market.total_jobs_analyzed || 1)) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}