"use client";

import { SettingSection, SettingCard } from "@/components/settings/card";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { settingsV2Api } from "@/lib/api";
import { Link2, RefreshCw, Unlink, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { useState } from "react";

const PLATFORMS = [
  { id: "linkedin", label: "LinkedIn", color: "text-blue-400" },
  { id: "internshala", label: "Internshala", color: "text-amber-400" },
  { id: "indeed", label: "Indeed", color: "text-emerald-400" },
  { id: "naukri", label: "Naukri", color: "text-rose-400" },
] as const;

type PlatformId = typeof PLATFORMS[number]["id"];

interface PlatformStatus {
  connected: boolean;
  last_sync: string | null;
  health: string;
}

export function PlatformConnectionsSection() {
  const queryClient = useQueryClient();
  const [syncing, setSyncing] = useState<PlatformId | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["platform-status"],
    queryFn: () => settingsV2Api.getPlatformStatus().then((r) => r.data),
    refetchInterval: 30_000,
  });

  const platforms: Record<string, PlatformStatus> = data?.platforms ?? {};

  const handleConnect = (platformId: PlatformId) => {
    // LinkedIn uses OAuth — redirect to platform login via cookie service
    if (platformId === "linkedin") {
      window.open("/dashboard/platforms/linkedin/connect", "_blank");
    } else if (platformId === "internshala") {
      window.open("/dashboard/platforms/internshala/connect", "_blank");
    } else {
      toast.info(`${platformId} integration coming soon`);
    }
  };

  const handleSync = async (platformId: PlatformId) => {
    setSyncing(platformId);
    try {
      await settingsV2Api.updatePlatforms({
        platforms: {
          [platformId]: { last_sync: new Date().toISOString(), health: "syncing" },
        },
      });
      queryClient.invalidateQueries({ queryKey: ["platform-status"] });
      toast.success(`${platformId} synced`);
    } catch {
      toast.error(`Failed to sync ${platformId}`);
    } finally {
      setSyncing(null);
    }
  };

  const handleDisconnect = async (platformId: PlatformId) => {
    try {
      await settingsV2Api.updatePlatforms({
        platforms: { [platformId]: { connected: false, health: "disconnected" } },
      });
      queryClient.invalidateQueries({ queryKey: ["platform-status"] });
      toast.success(`${platformId} disconnected`);
    } catch {
      toast.error(`Failed to disconnect ${platformId}`);
    }
  };

  return (
    <SettingSection>
      <SettingCard
        title="Connected Platforms"
        description="Manage where your AI agent searches and applies for jobs"
        icon={<Link2 className="w-4 h-4 text-white" />}
      >
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-5 h-5 text-zinc-500 animate-spin" />
          </div>
        ) : (
          <div className="space-y-3">
            {PLATFORMS.map((p) => {
              const status = platforms[p.id] ?? { connected: false, last_sync: null, health: "disconnected" };
              const isConnected = status.connected;
              const health = status.health;
              const isSyncing = syncing === p.id || health === "syncing";

              return (
                <div
                  key={p.id}
                  className={cn(
                    "flex items-center justify-between p-4 rounded-xl border transition-all",
                    isConnected ? "bg-[#1a1a1a] border-zinc-800" : "bg-[#161616] border-zinc-800/50"
                  )}
                >
                  <div className="flex items-center gap-4">
                    <div className={cn("w-10 h-10 rounded-xl flex items-center justify-center bg-[#242424] border border-white/[0.08]", p.color)}>
                      <span className="text-xs font-bold">{p.label.slice(0, 2)}</span>
                    </div>
                    <div>
                      <p className="text-sm font-bold text-white">{p.label}</p>
                      {isConnected && status.last_sync ? (
                        <p className="text-[10px] text-[#A1A1AA] mt-0.5">
                          Last sync: {new Date(status.last_sync).toLocaleString()}
                        </p>
                      ) : (
                        <p className="text-[10px] text-[#A1A1AA] mt-0.5">Not connected</p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {isConnected && (
                      <div
                        className={cn(
                          "w-2 h-2 rounded-full",
                          health === "healthy" && "bg-emerald-500",
                          health === "warning" && "bg-amber-500 animate-pulse",
                          (health === "error" || health === "disconnected") && "bg-red-500",
                          health === "syncing" && "bg-blue-400 animate-pulse"
                        )}
                        title={`Health: ${health}`}
                      />
                    )}

                    {isConnected ? (
                      <>
                        <button
                          onClick={() => handleSync(p.id)}
                          disabled={isSyncing}
                          className="p-2 rounded-lg bg-[#242424] border border-white/[0.08] text-[#A1A1AA] hover:text-white hover:border-white/20 transition-all disabled:opacity-50"
                          title="Sync"
                        >
                          <RefreshCw className={cn("w-3.5 h-3.5", isSyncing && "animate-spin")} />
                        </button>
                        <button
                          onClick={() => handleDisconnect(p.id)}
                          className="p-2 rounded-lg bg-[#242424] border border-white/[0.08] text-[#A1A1AA] hover:text-red-400 hover:border-red-500/20 transition-all"
                          title="Disconnect"
                        >
                          <Unlink className="w-3.5 h-3.5" />
                        </button>
                      </>
                    ) : (
                      <button
                        onClick={() => handleConnect(p.id)}
                        className="px-4 py-2 bg-white text-black text-xs font-bold rounded-xl hover:bg-zinc-200 transition-all shadow-lg"
                      >
                        Connect
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </SettingCard>
    </SettingSection>
  );
}
