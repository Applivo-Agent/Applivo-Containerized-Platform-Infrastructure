"use client";

import {
  createContext, useContext, useState, useCallback, useEffect, useRef, ReactNode,
} from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { settingsV2Api } from "@/lib/api";
import { SettingsState, DEFAULT_SETTINGS, backendToFrontend } from "@/lib/settings-types";

interface SettingsContextType {
  settings: SettingsState;
  updateSetting: <K extends keyof SettingsState>(key: K, value: SettingsState[K]) => void;
  updateNested: (path: string, value: unknown) => void;
  hasChanges: boolean;
  saveStatus: "idle" | "saving" | "saved" | "error";
  markSaved: () => void;
  markSaving: () => void;
  markError: () => void;
  reset: () => void;
  isLoading: boolean;
  saveSection: (section: string, data: Record<string, unknown>) => Promise<void>;
}

const SettingsContext = createContext<SettingsContextType | null>(null);

export function SettingsProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [settings, setSettings] = useState<SettingsState>(DEFAULT_SETTINGS);
  const [originalSettings, setOriginalSettings] = useState<SettingsState>(DEFAULT_SETTINGS);
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const savedTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const { data: backendData, isLoading } = useQuery({
    queryKey: ["settings-v2"],
    queryFn: () => settingsV2Api.getAll().then((r) => r.data),
    staleTime: 30_000,
  });

  useEffect(() => {
    if (backendData?.data) {
      const converted = backendToFrontend(backendData.data);
      setSettings(converted);
      setOriginalSettings(converted);
    }
  }, [backendData]);

  const hasChanges = JSON.stringify(settings) !== JSON.stringify(originalSettings);

  const updateSetting = useCallback(<K extends keyof SettingsState>(key: K, value: SettingsState[K]) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
    setSaveStatus("idle");
  }, []);

  const updateNested = useCallback((path: string, value: unknown) => {
    setSettings((prev) => {
      const keys = path.split(".");
      const next = { ...prev } as Record<string, unknown>;
      let target = next;
      for (let i = 0; i < keys.length - 1; i++) {
        target[keys[i]] = { ...(target[keys[i]] as Record<string, unknown>) };
        target = target[keys[i]] as Record<string, unknown>;
      }
      target[keys[keys.length - 1]] = value;
      return next as SettingsState;
    });
    setSaveStatus("idle");
  }, []);

  const markSaving = useCallback(() => setSaveStatus("saving"), []);
  const markSaved = useCallback(() => {
    setSaveStatus("saved");
    if (savedTimerRef.current) clearTimeout(savedTimerRef.current);
    savedTimerRef.current = setTimeout(() => setSaveStatus("idle"), 2500);
  }, []);
  const markError = useCallback(() => setSaveStatus("error"), []);
  const reset = useCallback(() => setSettings(originalSettings), [originalSettings]);

  const saveSection = useCallback(async (section: string, data: Record<string, unknown>) => {
    setSaveStatus("saving");
    try {
      let result;
      if (section === "general") result = await settingsV2Api.updateGeneral(data);
      else if (section === "notifications") result = await settingsV2Api.updateNotifications(data);
      else if (section === "automation") result = await settingsV2Api.updateAutomation(data);
      else if (section === "strategy") result = await settingsV2Api.updateStrategy(data);
      else if (section === "ai") result = await settingsV2Api.updateAI(data);
      else if (section === "advanced") result = await settingsV2Api.updateAdvanced(data);
      else throw new Error(`Unknown section: ${section}`);

      if (result?.data?.data) {
        const converted = backendToFrontend(result.data.data);
        setSettings(converted);
        setOriginalSettings(converted);
        queryClient.setQueryData(["settings-v2"], result.data);
      }
      setSaveStatus("saved");
      if (savedTimerRef.current) clearTimeout(savedTimerRef.current);
      savedTimerRef.current = setTimeout(() => setSaveStatus("idle"), 2500);
    } catch {
      setSaveStatus("error");
    }
  }, [queryClient]);

  return (
    <SettingsContext.Provider
      value={{
        settings, updateSetting, updateNested, hasChanges,
        saveStatus, markSaved, markSaving, markError, reset,
        isLoading, saveSection,
      }}
    >
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings() {
  const ctx = useContext(SettingsContext);
  if (!ctx) throw new Error("useSettings must be used within SettingsProvider");
  return ctx;
}
