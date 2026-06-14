"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { agentApi } from "./api";
import { toast } from "sonner";
import { useAuth } from "./auth";

interface AgentStatus {
  is_running: boolean;
  current_task: string | null;
  last_run: string | null;
  next_run_at: string | null;
  tasks_today: number;
  tasks_succeeded: number;
  tasks_failed: number;
  jobs_found_today: number;
  applications_today: number;
}

interface PersistedTask {
  task: string;
  startedAt: number; // timestamp
}

interface AgentStatusContextType {
  status: AgentStatus | null;
  isLoading: boolean;
  isWorking: boolean;
  currentTask: string | null;
  runTask: (taskType: string, payload?: Record<string, unknown>) => Promise<void>;
  isMutating: boolean;
}

const STORAGE_KEY = "applivo_agent_task";
const MAX_TASK_AGE_MS = 30 * 60 * 1000; // 30 minutes safety cap

function readStoredTask(): string | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed: PersistedTask = JSON.parse(raw);
    const age = Date.now() - parsed.startedAt;
    if (age > MAX_TASK_AGE_MS) {
      localStorage.removeItem(STORAGE_KEY);
      return null;
    }
    return parsed.task;
  } catch {
    localStorage.removeItem(STORAGE_KEY);
    return null;
  }
}

function writeStoredTask(task: string | null) {
  if (typeof window === "undefined") return;
  if (!task) {
    localStorage.removeItem(STORAGE_KEY);
    return;
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ task, startedAt: Date.now() }));
}

const AgentStatusContext = createContext<AgentStatusContextType | null>(null);

export function AgentStatusProvider({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient();
  const { user } = useAuth();

  // Restore optimistic task from localStorage on mount so it survives
  // page navigation, hard refreshes, and tab switches.
  const [optimisticTask, setOptimisticTask] = useState<string | null>(readStoredTask);

  const { data: status, isLoading } = useQuery({
    queryKey: ["agent-status"],
    queryFn: () => agentApi.status().then((r) => r.data),
    staleTime: 2000,
    enabled: !!user,
    refetchInterval: (query) => {
      if (!user) return false;
      const data = query.state.data as AgentStatus | undefined;
      return data?.is_running ? 1000 : 10000;
    },
  });

  // Sync optimisticTask with backend status and localStorage
  useEffect(() => {
    if (!status) return;

    if (status.is_running && status.current_task) {
      setOptimisticTask(status.current_task);
      writeStoredTask(status.current_task);
      return;
    }

    if (!status.is_running) {
      setOptimisticTask(null);
      writeStoredTask(null);
    }
  }, [status?.is_running, status?.current_task, status]);

  const runMutation = useMutation({
    mutationFn: (variables: { taskType: string; payload?: Record<string, unknown> }) =>
      agentApi.run({ task_type: variables.taskType, payload: variables.payload }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agent-status"] });
    },
    onError: (err: unknown) => {
      const status = (err as { response?: { status?: number } } | null)?.response?.status;
      if (status === 403) {
        toast.error("Subscription required for agent features.");
      } else {
        toast.error("Failed to start agent task.");
      }
      // Clear stored task on error so UI doesn't stay stuck
      setOptimisticTask(null);
      writeStoredTask(null);
    },
  });

  const runTask = useCallback(
    async (taskType: string, payload?: Record<string, unknown>) => {
      setOptimisticTask(taskType);
      writeStoredTask(taskType);
      await runMutation.mutateAsync({ taskType, payload });
    },
    [runMutation]
  );

  // Backend returns uppercase enum values (SCRAPE_JOBS) but frontend keys are lowercase
  const normalizeTask = (task: string | null): string | null => {
    if (!task) return null;
    const map: Record<string, string> = {
      scrape_jobs: "scrape_jobs",
      analyze_jobs: "analyze_jobs",
      analyze_job: "analyze_jobs",
      queue_jobs: "queue_jobs",
      analyze_and_queue: "queue_jobs",
      apply_queued: "apply_queued",
      apply_que: "apply_queued",
      // Uppercase variants from backend enum
      SCRAPE_JOBS: "scrape_jobs",
      ANALYZE_JOB: "analyze_jobs",
      ANALYZE_AND_QUEUE: "queue_jobs",
      APPLY_QUEUED: "apply_queued",
    };
    return map[task] || task.toLowerCase();
  };

  const currentTaskLabel = normalizeTask(status?.current_task || optimisticTask || null);
  const isWorking = !!status?.is_running || runMutation.isPending || !!currentTaskLabel;

  return (
    <AgentStatusContext.Provider
      value={{
        status: status || null,
        isLoading,
        isWorking,
        currentTask: currentTaskLabel,
        runTask,
        isMutating: runMutation.isPending,
      }}
    >
      {children}
    </AgentStatusContext.Provider>
  );
}

export function useAgentStatus() {
  const context = useContext(AgentStatusContext);
  if (!context) {
    throw new Error("useAgentStatus must be used within an AgentStatusProvider");
  }
  return context;
}
