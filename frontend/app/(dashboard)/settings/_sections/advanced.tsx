"use client";

import { SettingSection, SettingCard, SettingRow } from "@/components/settings/card";
import { Toggle } from "@/components/settings/toggle";
import { useSettings } from "@/lib/settings-context";
import { settingsV2Api } from "@/lib/api";
import { FlaskConical, Bug, Download, Key, AlertTriangle, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { useState } from "react";

export function AdvancedSection() {
  const { settings, saveSection } = useSettings();
  const [exporting, setExporting] = useState(false);
  const [resetConfirm, setResetConfirm] = useState("");
  const [resetting, setResetting] = useState(false);

  const handleExport = async (types: string[], format: string) => {
    setExporting(true);
    try {
      const res = await settingsV2Api.exportData(types, format);
      const blob = new Blob([JSON.stringify(res.data.data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `applivo-export-${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success("Export downloaded");
    } catch {
      toast.error("Export failed");
    } finally {
      setExporting(false);
    }
  };

  const handleReset = async () => {
    if (resetConfirm !== "RESET") {
      toast.error("Type RESET to confirm");
      return;
    }
    setResetting(true);
    try {
      await settingsV2Api.resetSystem("RESET");
      toast.success("All settings reset to defaults");
      setResetConfirm("");
      window.location.reload();
    } catch {
      toast.error("Reset failed");
    } finally {
      setResetting(false);
    }
  };

  return (
    <SettingSection>
      <SettingCard
        title="Developer & Power User"
        description="Advanced controls for debugging and integrations"
        icon={<FlaskConical className="w-4 h-4 text-white" />}
      >
        <div className="space-y-1">
          <SettingRow label="Debug Mode" description="Show detailed logs and agent reasoning in the UI">
            <Toggle
              checked={settings.debugMode}
              onChange={(v) => saveSection("advanced", { debug_mode: v })}
            />
          </SettingRow>
          <SettingRow label="Experimental Features" description="Enable beta features that are still in development">
            <Toggle
              checked={settings.experimentalFeatures}
              onChange={(v) => saveSection("advanced", { experimental_features: v })}
            />
          </SettingRow>
        </div>
      </SettingCard>

      <SettingCard
        title="Data & Exports"
        description="Download your data or export configurations"
        icon={<Download className="w-4 h-4 text-white" />}
      >
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => handleExport(["settings", "applications", "jobs"], "json")}
            disabled={exporting}
            className="p-4 bg-[#161616] border border-zinc-800 rounded-xl text-left hover:border-white/20 transition-all disabled:opacity-50"
          >
            <Download className="w-4 h-4 text-white mb-2" />
            <p className="text-sm font-bold text-white">Export All Data</p>
            <p className="text-xs text-[#A1A1AA] mt-0.5">JSON format</p>
          </button>

          <button
            onClick={() => handleExport(["settings"], "json")}
            disabled={exporting}
            className="p-4 bg-[#161616] border border-zinc-800 rounded-xl text-left hover:border-white/20 transition-all disabled:opacity-50"
          >
            <Bug className="w-4 h-4 text-white mb-2" />
            <p className="text-sm font-bold text-white">Export Settings</p>
            <p className="text-xs text-[#A1A1AA] mt-0.5">Configuration only</p>
          </button>
        </div>
      </SettingCard>

      <SettingCard
        title="API & Webhooks"
        description="Integrate Applivo with external systems"
        icon={<Key className="w-4 h-4 text-white" />}
      >
        <div className="p-4 bg-[#161616] border border-zinc-800 rounded-xl">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <p className="text-xs text-amber-400 font-medium">Enterprise feature — contact support to enable</p>
          </div>
          <div className="space-y-3 opacity-40">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Key className="w-4 h-4 text-[#A1A1AA]" />
                <span className="text-sm text-[#A1A1AA]">API Key</span>
              </div>
              <span className="text-xs font-mono text-[#A1A1AA] bg-[#0B0B0F] px-2 py-1 rounded-lg">••••••••••••</span>
            </div>
          </div>
        </div>
      </SettingCard>

      <SettingCard
        title="Reset System"
        description="Reset all settings to factory defaults"
        icon={<Trash2 className="w-4 h-4 text-red-400" />}
      >
        <div className="p-4 bg-red-500/5 border border-red-500/20 rounded-xl space-y-3">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
            <p className="text-xs text-red-400">This will permanently reset ALL settings to defaults. This cannot be undone.</p>
          </div>
          <input
            type="text"
            placeholder='Type "RESET" to confirm'
            value={resetConfirm}
            onChange={(e) => setResetConfirm(e.target.value)}
            className="w-full bg-[#0B0B0F] border border-red-500/30 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-red-500 transition-all"
          />
          <button
            onClick={handleReset}
            disabled={resetConfirm !== "RESET" || resetting}
            className="w-full py-2.5 bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl text-sm font-bold hover:bg-red-500/20 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
          >
            {resetting ? "Resetting..." : "Reset All Settings"}
          </button>
        </div>
      </SettingCard>
    </SettingSection>
  );
}
