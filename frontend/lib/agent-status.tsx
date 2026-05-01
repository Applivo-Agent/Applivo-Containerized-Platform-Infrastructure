"use client";

import React, { createContext, useContext } from "react";
import { useState } from "react";
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

interface AgentStatusContextType {
  status: AgentStatus | null;
  isLoading: boolean;
  isWorking: boolean;
  currentTask: string | null;
  runTask: (taskType: string, payload?: Record<string, unknown>) => Promise<void>;
  isMutating: boolean;
}

const AgentStatusContext = createContext<AgentStatusContextType | null>(null);

export function AgentStatusProvider({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient();

  const { user } = useAuth();
  const [optimisticTask, setOptimisticTask] = useState<string | null>(null);

  const { data: status, isLoading } = useQuery({
    queryKey: ["agent-status"],
    queryFn: () => agentApi.status().then((r) => r.data),
    staleTime: 5000,
    enabled: !!user,
    refetchInterval: (query) => {
      if (!user) return false;
      // Poll every 5s while the backend reports an active task.
      const data = query.state.data as AgentStatus | undefined;
      return data?.is_running ? 5000 : 30000;
    },
    onSuccess: (data) => {
      // If backend is still running, sync optimistic state with server current_task
      if (data.is_running && data.current_task) {
        setOptimisticTask(data.current_task);
        return;
      }

      // If backend is not running, always clear optimistic task
      if (!data.is_running) {
        setOptimisticTask(null);
      }
    },
  });

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
    },
  });

  const runTask = async (taskType: string, payload?: Record<string, unknown>) => {
    setOptimisticTask(taskType);
    await runMutation.mutateAsync({ taskType, payload });
  };

  const currentTaskLabel = status?.current_task || optimisticTask || null;
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
