"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
  title?: string;
  description?: string;
  icon?: ReactNode;
  action?: ReactNode;
}

export function SettingCard({ children, className, title, description, icon, action }: CardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      className={cn(
        "bg-[#1c1c1e] border border-[#262626] rounded-2xl shadow-lg overflow-hidden",
        className
      )}
    >
      {(title || icon) && (
        <div className="flex items-center justify-between px-6 py-5 border-b border-[#262626]">
          <div className="flex items-center gap-3">
            {icon && (
              <div className="w-9 h-9 rounded-xl bg-[#242424] border border-white/[0.08] flex items-center justify-center">
                {icon}
              </div>
            )}
            <div>
              {title && <h3 className="font-semibold text-white text-sm">{title}</h3>}
              {description && <p className="text-xs text-[#A1A1AA] mt-0.5">{description}</p>}
            </div>
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div className="p-6">{children}</div>
    </motion.div>
  );
}

interface RowProps {
  label: string;
  description?: string;
  children: ReactNode;
  className?: string;
}

export function SettingRow({ label, description, children, className }: RowProps) {
  return (
    <div className={cn("flex items-center justify-between py-4 border-b border-[#262626] last:border-0", className)}>
      <div className="flex-1 min-w-0 pr-4">
        <p className="text-sm font-medium text-white">{label}</p>
        {description && <p className="text-xs text-[#A1A1AA] mt-0.5">{description}</p>}
      </div>
      <div className="shrink-0">{children}</div>
    </div>
  );
}

interface SectionProps {
  children: ReactNode;
  className?: string;
}

export function SettingSection({ children, className }: SectionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className={cn("space-y-6", className)}
    >
      {children}
    </motion.div>
  );
}
