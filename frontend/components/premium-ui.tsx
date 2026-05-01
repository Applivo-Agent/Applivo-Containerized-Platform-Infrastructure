"use client";

import { motion, AnimatePresence } from "framer-motion";
import { ReactNode, useMemo } from "react";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

// ============================================================================
// PREMIUM BUTTON COMPONENT
// ============================================================================
interface PremiumButtonProps {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  icon?: ReactNode;
  children: ReactNode;
  className?: string;
  disabled?: boolean;
  type?: "button" | "submit" | "reset";
  onClick?: () => void;
}

export function PremiumButton({
  variant = "primary",
  size = "md",
  loading = false,
  icon,
  children,
  className,
  disabled,
  type = "button",
  onClick,
}: PremiumButtonProps) {
  const variants = {
    primary: "bg-gradient-to-r from-violet-600 to-indigo-600 text-white hover:from-violet-700 hover:to-indigo-700 shadow-lg shadow-violet-500/25 border-0",
    secondary: "bg-zinc-100 text-zinc-900 hover:bg-zinc-200 border-zinc-200",
    outline: "border-2 border-zinc-200 text-zinc-700 hover:border-zinc-300 hover:bg-zinc-50",
    ghost: "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900",
    danger: "bg-red-500 text-white hover:bg-red-600 shadow-lg shadow-red-500/25",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-5 py-2.5 text-sm",
    lg: "px-8 py-3.5 text-base",
  };

  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={cn(
        "relative inline-flex items-center justify-center gap-2 font-medium rounded-xl transition-all duration-200",
        variants[variant],
        sizes[size],
        disabled || loading ? "opacity-60 cursor-not-allowed" : "",
        className
      )}
      disabled={disabled || loading}
      type={type}
      onClick={onClick}
    >
      {loading ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : icon ? (
        <span className="flex-shrink-0">{icon}</span>
      ) : null}
      {children}
    </motion.button>
  );
}

// ============================================================================
// ANIMATED CARD COMPONENT
// ============================================================================
interface AnimatedCardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  glow?: "purple" | "blue" | "green" | "none";
  onClick?: () => void;
}

export function AnimatedCard({
  children,
  className,
  hover = true,
  glow = "none",
  onClick
}: AnimatedCardProps) {
  const glowColors = {
    purple: "hover:shadow-violet-500/20",
    blue: "hover:shadow-white/20",
    green: "hover:shadow-emerald-500/20",
    none: "",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={hover ? { scale: 1.01, y: -4 } : {}}
      transition={{ duration: 0.3, ease: "easeOut" }}
      onClick={onClick}
      className={cn(
        "bg-white/80 backdrop-blur-xl rounded-2xl border border-zinc-200/50 p-6",
        "shadow-sm hover:shadow-xl transition-all duration-300",
        glowColors[glow],
        onClick && "cursor-pointer",
        className
      )}
    >
      {children}
    </motion.div>
  );
}

// ============================================================================
// GRADIENT BACKGROUND COMPONENT
// ============================================================================
interface GradientBackgroundProps {
  children: ReactNode;
  variant?: "hero" | "subtle" | "spotlight";
  className?: string;
}

export function GradientBackground({ children, variant = "subtle", className }: GradientBackgroundProps) {
  const variants = {
    hero: "bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-violet-100 via-white to-cyan-50/30",
    subtle: "bg-gradient-to-br from-white via-zinc-50 to-zinc-100",
    spotlight: "bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-violet-100/50 via-transparent to-transparent",
  };

  return (
    <div className={cn("relative overflow-hidden", variants[variant], className)}>
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiMyMzIzMjciIGZpbGwtb3BhY2l0eT0iMC4wMyI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMiIvPjwvZz48L2c+PC9zdmc+')] opacity-30" />
      {children}
    </div>
  );
}

// ============================================================================
// STATUS BADGE COMPONENT
// ============================================================================
interface StatusBadgeProps {
  status: "success" | "warning" | "error" | "info" | "neutral";
  children: ReactNode;
  pulse?: boolean;
  className?: string;
}

export function StatusBadge({ status, children, pulse = false, className }: StatusBadgeProps) {
  const colors = {
    success: "bg-emerald-50 text-emerald-700 border-emerald-200",
    warning: "bg-amber-50 text-amber-700 border-amber-200",
    error: "bg-red-50 text-red-700 border-red-200",
    info: "bg-blue-50 text-blue-700 border-blue-200",
    neutral: "bg-zinc-50 text-zinc-700 border-zinc-200",
  };

  return (
    <span className={cn(
      "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border",
      colors[status],
      className
    )}>
      {pulse && (
        <span className="relative flex h-2 w-2">
          <span className={cn("animate-ping absolute inline-flex h-full w-full rounded-full opacity-75", {
            "bg-emerald-400": status === "success",
            "bg-amber-400": status === "warning",
            "bg-red-400": status === "error",
            "bg-blue-400": status === "info",
            "bg-zinc-400": status === "neutral",
          })} />
          <span className={cn("relative inline-flex rounded-full h-2 w-2", {
            "bg-emerald-500": status === "success",
            "bg-amber-500": status === "warning",
            "bg-red-500": status === "error",
            "bg-blue-500": status === "info",
            "bg-zinc-500": status === "neutral",
          })} />
        </span>
      )}
      {children}
    </span>
  );
}

// ============================================================================
// LOADING SKELETON COMPONENT
// ============================================================================
interface SkeletonProps {
  className?: string;
  variant?: "text" | "circular" | "rectangular";
}

export function Skeleton({ className, variant = "rectangular" }: SkeletonProps) {
  const variants = {
    text: "h-4 w-full rounded",
    circular: "rounded-full",
    rectangular: "rounded-xl",
  };

  return (
    <div className={cn(
      "animate-pulse bg-zinc-200/50",
      variants[variant],
      className
    )} />
  );
}

export function CardSkeleton() {
  return (
    <div className="bg-white/80 backdrop-blur-xl rounded-2xl border border-zinc-200/50 p-6 space-y-4">
      <div className="flex items-center gap-4">
        <Skeleton className="h-12 w-12" variant="circular" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-1/2" />
        </div>
      </div>
      <Skeleton className="h-20 w-full" />
      <div className="flex gap-2">
        <Skeleton className="h-6 w-16" />
        <Skeleton className="h-6 w-16" />
        <Skeleton className="h-6 w-16" />
      </div>
    </div>
  );
}

export function DashboardSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {[1, 2, 3, 4].map((i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  );
}

// ============================================================================
// ANIMATED COUNTER COMPONENT
// ============================================================================
interface AnimatedCounterProps {
  value: number;
  prefix?: string;
  suffix?: string;
  duration?: number;
  className?: string;
}

export function AnimatedCounter({ value, prefix = "", suffix = "", duration = 1, className }: AnimatedCounterProps) {
  return (
    <motion.span
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn("font-bold", className)}
    >
      {prefix}
      <motion.span
        key={value}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration }}
      >
        {value.toLocaleString()}
      </motion.span>
      {suffix}
    </motion.span>
  );
}

// ============================================================================
// NOTIFICATION TOAST COMPONENT
// ============================================================================
interface ToastProps {
  message: string;
  type?: "success" | "error" | "info" | "warning";
  onClose?: () => void;
}

export function Toast({ message, type = "info", onClose }: ToastProps) {
  const icons = {
    success: "✓",
    error: "✕",
    info: "ℹ",
    warning: "⚠",
  };

  const colors = {
    success: "bg-emerald-500",
    error: "bg-red-500",
    info: "bg-blue-500",
    warning: "bg-amber-500",
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 50, scale: 0.9 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 20, scale: 0.9 }}
        className={cn(
          "fixed bottom-6 right-6 z-50 flex items-center gap-3 px-5 py-3 rounded-xl shadow-2xl text-white",
          colors[type]
        )}
      >
        <span className="text-lg">{icons[type]}</span>
        <span className="font-medium">{message}</span>
        {onClose && (
          <button onClick={onClose} className="ml-2 hover:opacity-80">
            ✕
          </button>
        )}
      </motion.div>
    </AnimatePresence>
  );
}

// ============================================================================
// PROGRESS BAR COMPONENT
// ============================================================================
interface ProgressBarProps {
  value: number;
  max?: number;
  color?: "purple" | "blue" | "green" | "amber" | "red";
  showLabel?: boolean;
  className?: string;
}

export function ProgressBar({ value, max = 100, color = "purple", showLabel = false, className }: ProgressBarProps) {
  const colors = {
    purple: "bg-gradient-to-r from-violet-500 to-indigo-500",
    blue: "bg-gradient-to-r from-white/10 to-cyan-500",
    green: "bg-gradient-to-r from-emerald-500 to-green-500",
    amber: "bg-gradient-to-r from-amber-500 to-orange-500",
    red: "bg-gradient-to-r from-red-500 to-rose-500",
  };

  const percentage = Math.min((value / max) * 100, 100);

  return (
    <div className={cn("w-full", className)}>
      <div className="h-2 bg-zinc-100 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className={cn("h-full rounded-full", colors[color])}
        />
      </div>
      {showLabel && (
        <p className="mt-1 text-xs text-zinc-500 text-right">{Math.round(percentage)}%</p>
      )}
    </div>
  );
}

// ============================================================================
// TYPING INDICATOR COMPONENT
// ============================================================================
export function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-4 py-3 bg-zinc-100 rounded-2xl rounded-bl-md">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className="w-2 h-2 bg-zinc-400 rounded-full"
          animate={{ y: [0, -4, 0] }}
          transition={{
            duration: 0.6,
            repeat: Infinity,
            delay: i * 0.15,
          }}
        />
      ))}
    </div>
  );
}

// ============================================================================
// AVATAR COMPONENT
// ============================================================================
interface AvatarProps {
  src?: string;
  name?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function Avatar({ src, name, size = "md", className }: AvatarProps) {
  const sizes = {
    sm: "w-8 h-8 text-xs",
    md: "w-10 h-10 text-sm",
    lg: "w-14 h-14 text-lg",
  };

  const initials = name?.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2) || "?";

  if (src) {
    return (
      <img
        src={src}
        alt={name || "avatar"}
        className={cn("rounded-full object-cover border-2 border-white shadow-md", sizes[size], className)}
      />
    );
  }

  return (
    <div className={cn(
      "rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center text-white font-medium",
      sizes[size],
      className
    )}>
      {initials}
    </div>
  );
}

// ============================================================================
// PAGE TRANSITION WRAPPER
// ============================================================================
interface PageTransitionProps {
  children: ReactNode;
  className?: string;
}

export function PageTransition({ children, className }: PageTransitionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

// ============================================================================
// STAGGER CONTAINER COMPONENT
// ============================================================================
interface StaggerContainerProps {
  children: ReactNode;
  className?: string;
  delay?: number;
}

export function StaggerContainer({ children, className, delay = 0.1 }: StaggerContainerProps) {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={{
        hidden: { opacity: 0 },
        visible: {
          opacity: 1,
          transition: {
            staggerChildren: delay,
          },
        },
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

export function StaggerItem({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <motion.div
      variants={{
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0, transition: { duration: 0.4 } },
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

// ============================================================================
// FLOATING PARTICLES BACKGROUND
// ============================================================================
export function FloatingParticles() {
  const particles = useMemo(
    () =>
      Array.from({ length: 20 }, (_, i) => {
        const seed = i + 1;
        const x = (seed * 37) % 100;
        const y = (seed * 53) % 100;
        const duration = 10 + ((seed * 29) % 10);
        const delay = ((seed * 13) % 50) / 10;
        const left = (seed * 41) % 100;
        const animationDelay = ((seed * 17) % 50) / 10;
        return {
          x,
          y,
          duration,
          delay,
          left,
          animationDelay,
        };
      }),
    []
  );

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map((p, i) => (
        <motion.div
          key={i}
          className="absolute w-1 h-1 bg-violet-400/30 rounded-full"
          initial={{
            x: `${p.x}%`,
            y: `${p.y}%`,
          }}
          animate={{
            y: [null, "-100%"],
            opacity: [0, 1, 0],
          }}
          transition={{
            duration: p.duration,
            repeat: Infinity,
            delay: p.delay,
          }}
          style={{
            left: `${p.left}%`,
            animationDelay: `${p.animationDelay}s`,
          }}
        />
      ))}
    </div>
  );
}

// ============================================================================
// MATCH SCORE BADGE
// ============================================================================
interface MatchScoreBadgeProps {
  score: number;
  className?: string;
}

export function MatchScoreBadge({ score, className }: MatchScoreBadgeProps) {
  const getColor = (score: number) => {
    if (score >= 80) return "text-white";
    if (score >= 60) return "text-zinc-200";
    if (score >= 40) return "text-zinc-400";
    return "text-zinc-600";
  };

  const getLabel = (score: number) => {
    if (score >= 80) return "Excellent Match";
    if (score >= 60) return "Good Match";
    if (score >= 40) return "Fair Match";
    return "Low Match";
  };

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <div className="relative w-10 h-10">
        <svg className="w-10 h-10 -rotate-90">
          <circle
            cx="20"
            cy="20"
            r="16"
            stroke="currentColor"
            strokeWidth="3"
            fill="none"
            className="text-zinc-100"
          />
          <motion.circle
            cx="20"
            cy="20"
            r="16"
            stroke="currentColor"
            strokeWidth="3"
            fill="none"
            className={getColor(score)}
            strokeLinecap="round"
            initial={{ strokeDasharray: 100, strokeDashoffset: 100 }}
            animate={{ strokeDashoffset: 100 - score }}
            transition={{ duration: 1, ease: "easeOut" }}
          />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center text-xs font-bold">
          {Math.round(score)}
        </span>
      </div>
      <span className="text-xs font-medium text-zinc-600">{getLabel(score)}</span>
    </div>
  );
}