"use client";

import { useSettings } from "@/lib/settings-context";
import { motion, AnimatePresence } from "framer-motion";
import { Check, Loader2, AlertCircle } from "lucide-react";

export function SaveStatus() {
  const { saveStatus, hasChanges } = useSettings();

  return (
    <div className="h-8 flex items-center">
      <AnimatePresence mode="wait">
        {saveStatus === "saving" && (
          <motion.div
            key="saving"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="flex items-center gap-2 text-sm text-zinc-400"
          >
            <Loader2 className="w-4 h-4 animate-spin" />
            Saving...
          </motion.div>
        )}
        {saveStatus === "saved" && (
          <motion.div
            key="saved"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="flex items-center gap-2 text-sm text-emerald-400"
          >
            <Check className="w-4 h-4" />
            Saved
          </motion.div>
        )}
        {saveStatus === "error" && (
          <motion.div
            key="error"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="flex items-center gap-2 text-sm text-red-400"
          >
            <AlertCircle className="w-4 h-4" />
            Error saving
          </motion.div>
        )}
        {saveStatus === "idle" && hasChanges && (
          <motion.div
            key="unsaved"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="text-sm text-amber-400"
          >
            Unsaved changes
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
