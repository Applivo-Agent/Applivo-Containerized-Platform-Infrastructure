"use client";

import { motion } from "framer-motion";
import { Activity, Zap, Clock, BarChart3 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useState, useEffect } from "react";

interface TaskProgressIndicatorProps {
  isRunning: boolean;
  currentTask?: string | null;
}

export function TaskProgressIndicator({ isRunning, currentTask }: TaskProgressIndicatorProps) {
  const [activeStageIndex, setActiveStageIndex] = useState(0);

  // Define the stages for different task types
  const getStages = (taskType?: string | null) => {
    if (taskType === "apply_queued") {
      return [
        { id: "load", label: "Loading", icon: Clock },
        { id: "deploying", label: "Applying", icon: Zap },
        { id: "queuing", label: "Processing", icon: Activity },
        { id: "analyzing", label: "Analyzing", icon: BarChart3 },
      ];
    }
    if (taskType === "scrape_jobs") {
      return [
        { id: "scraping", label: "Scraping", icon: Activity },
        { id: "queuing", label: "Queuing", icon: Clock },
        { id: "analyzing", label: "Analyzing", icon: BarChart3 },
      ];
    }
    if (taskType === "analyze_jobs") {
      return [
        { id: "analyzing", label: "Analyzing", icon: Zap },
        { id: "processing", label: "Processing", icon: Activity },
      ];
    }
    // Default stages for queue_jobs
    return [
      { id: "scraping", label: "Scraping", icon: Activity },
      { id: "queuing", label: "Queuing", icon: Clock },
      { id: "deploying", label: "Deploying", icon: Zap },
      { id: "analyzing", label: "Analyzing", icon: BarChart3 },
    ];
  };

  const stages = getStages(currentTask);

  // Cycle through stages while running
  useEffect(() => {
    if (!isRunning) {
      setActiveStageIndex(0);
      return;
    }

    // Cycle through stages every 2 seconds
    const interval = setInterval(() => {
      setActiveStageIndex((prev) => (prev + 1) % stages.length);
    }, 2000);

    return () => clearInterval(interval);
  }, [isRunning, stages.length]);
  
  if (!isRunning) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.3 }}
      className="bg-gradient-to-r from-[#1c1c1e] via-[#262626] to-[#1c1c1e] border border-white/10 rounded-xl p-6 mb-6"
    >
      {/* Title */}
      <p className="text-xs font-semibold uppercase tracking-widest text-zinc-400 mb-4">Task Progress</p>

      <div className="flex items-center justify-between gap-3">
        {stages.map((stage, idx) => {
          const Icon = stage.icon;
          const isActive = idx === activeStageIndex;
          const isCompleted = idx < activeStageIndex;
          
          return (
            <div key={stage.id} className="flex items-center flex-1">
              {/* Stage indicator */}
              <motion.div
                animate={{
                  scale: isActive ? 1.15 : isCompleted ? 1 : 0.95,
                }}
                transition={{ duration: 0.3, ease: "easeOut" }}
                className={cn(
                  "relative flex items-center justify-center w-14 h-14 rounded-full border-2 transition-all flex-shrink-0",
                  isActive
                    ? "bg-white/25 border-white shadow-lg shadow-white/30"
                    : isCompleted
                    ? "bg-white/15 border-white/50"
                    : "bg-white/5 border-white/20"
                )}
              >
                <Icon className={cn(
                  "w-6 h-6 transition-colors",
                  isActive ? "text-white" : isCompleted ? "text-white/80" : "text-zinc-500"
                )} />
                
                {/* Animated pulse for active stage */}
                {isActive && (
                  <>
                    <motion.div
                      className="absolute inset-0 rounded-full border-2 border-white"
                      animate={{
                        scale: [1, 1.35, 1],
                        opacity: [0.6, 0, 0.6],
                      }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                      }}
                    />
                    <motion.div
                      className="absolute top-0 left-1/2 w-2 h-2 bg-white rounded-full -translate-x-1/2"
                      animate={{
                        y: [0, -8],
                        opacity: [1, 0],
                      }}
                      transition={{
                        duration: 1.5,
                        repeat: Infinity,
                      }}
                    />
                  </>
                )}
              </motion.div>

              {/* Label */}
              <motion.div
                animate={{ x: isActive ? 6 : 0, opacity: isActive ? 1 : 0.7 }}
                transition={{ duration: 0.3 }}
                className="ml-3 flex-1"
              >
                <p className={cn(
                  "text-xs font-semibold uppercase tracking-wider transition-colors",
                  isActive ? "text-white" : isCompleted ? "text-zinc-400" : "text-zinc-600"
                )}>
                  {stage.label}
                </p>
              </motion.div>

              {/* Divider line to next stage */}
              {idx < stages.length - 1 && (
                <motion.div
                  className="h-1 flex-1 mx-2 bg-gradient-to-r from-white/20 to-transparent rounded-full"
                  animate={{
                    opacity: idx <= activeStageIndex ? 1 : 0.2,
                  }}
                  transition={{ duration: 0.5 }}
                />
              )}
            </div>
          );
        })}
      </div>

      {/* Progress bar at bottom */}
      <motion.div
        className="h-1.5 bg-white/10 rounded-full mt-4 overflow-hidden"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <motion.div
          className="h-full bg-gradient-to-r from-white/40 via-white to-white/40 rounded-full"
          animate={{
            x: ["0%", "100%"],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: "linear",
          }}
          style={{ width: "30%" }}
        />
      </motion.div>
    </motion.div>
  );
}
