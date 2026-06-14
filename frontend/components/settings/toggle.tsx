"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  size?: "sm" | "md" | "lg";
}

export function Toggle({ checked, onChange, disabled, size = "md" }: ToggleProps) {
  const sizes = {
    sm: { w: "w-9", h: "h-5", knob: "w-3.5 h-3.5", active: "left-[18px]", inactive: "left-[2px]" },
    md: { w: "w-12", h: "h-6", knob: "w-4 h-4", active: "left-6", inactive: "left-0.5" },
    lg: { w: "w-14", h: "h-7", knob: "w-5 h-5", active: "left-[26px]", inactive: "left-[2px]" },
  };
  const s = sizes[size];

  return (
    <button
      type="button"
      disabled={disabled}
      onClick={() => onChange(!checked)}
      className={cn(
        "relative rounded-full transition-all duration-300 border-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-white/30",
        s.w,
        s.h,
        checked ? "bg-white border-white" : "bg-[#161616] border-zinc-800",
        disabled && "opacity-40 cursor-not-allowed"
      )}
    >
      <motion.div
        className={cn("absolute top-0.5 rounded-full shadow-md", s.knob, checked ? "bg-[#0B0B0F]" : "bg-[#A1A1AA]")}
        animate={{ left: checked ? s.active : s.inactive }}
        transition={{ type: "spring", stiffness: 500, damping: 30 }}
      />
    </button>
  );
}
