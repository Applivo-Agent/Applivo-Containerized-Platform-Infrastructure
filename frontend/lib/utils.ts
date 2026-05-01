import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date | null | undefined): string {
  if (!date) return "—";
  return new Date(date).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export function formatDateTime(date: string | Date | null | undefined): string {
  if (!date) return "—";
  return new Date(date).toLocaleString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatCurrency(amount: number, currency = "INR"): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function timeAgo(date: string | Date | null | undefined): string {
  if (!date) return "—";
  const now = new Date();
  const d = new Date(date);
  const diff = Math.floor((now.getTime() - d.getTime()) / 1000);

  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
  return formatDate(date);
}

export function getMatchColor(score: number): string {
  if (score >= 75) return "match-high";
  if (score >= 50) return "match-medium";
  return "match-low";
}

export function getMatchBadgeClass(score: number): string {
  if (score >= 75) return "bg-white/10 text-white border border-white/20";
  if (score >= 50) return "bg-white/5 text-zinc-300 border border-white/10";
  return "bg-zinc-800/10 text-zinc-500 border border-white/5";
}

export function getStatusClass(status: string): string {
  if (!status) return "bg-zinc-500/20 text-zinc-400 border border-zinc-500/30";
  const s = status.toLowerCase();
  const map: Record<string, string> = {
    pending_approval: "status-pending",
    queued: "status-queued",
    applying: "bg-violet-500/20 text-violet-400 border border-violet-500/30",
    applied: "status-applied",
    viewed: "status-viewed",
    shortlisted: "status-shortlisted",
    interview_scheduled: "status-interview",
    interview_completed: "status-interview",
    offer_received: "status-offer",
    offer_accepted: "bg-green-500/20 text-green-300 border border-green-500/40",
    offer_declined: "bg-zinc-800/20 text-zinc-400 border border-zinc-800/30",
    rejected: "status-rejected",
    withdrawn: "bg-gray-500/20 text-gray-400 border border-gray-500/30",
    failed: "status-rejected",
    skipped: "bg-zinc-500/20 text-zinc-400 border border-zinc-500/30",
  };
  return map[s] ?? "bg-zinc-500/20 text-zinc-400 border border-zinc-500/30";
}

export function getStatusLabel(status: string): string {
  if (!status) return "Unknown";
  const s = status.toLowerCase();
  const map: Record<string, string> = {
    pending_approval: "Pending Approval",
    queued: "Queued",
    applying: "Applying",
    applied: "Applied",
    viewed: "Viewed",
    shortlisted: "Shortlisted",
    interview_scheduled: "Interview",
    interview_completed: "Interview Done",
    offer_received: "Offer Received",
    offer_accepted: "Offer Accepted",
    offer_declined: "Offer Declined",
    rejected: "Rejected",
    withdrawn: "Withdrawn",
    failed: "Failed",
    skipped: "Skipped",
  };
  return map[s] ?? status.replace(/_/g, " ").replace(/\w\S*/g, (txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase());
}

export function truncate(str: string, n: number): string {
  return str.length > n ? str.slice(0, n) + "…" : str;
}

/**
 * Safely extracts a human-readable error message from an API error.
 * Handles strings, Pydantic validation error lists, and generic objects.
 */
type ApiErrorDetail = { msg?: string; message?: string };
type ApiErrorPayload = { detail?: unknown; message?: string };
type ApiErrorShape = {
  response?: { data?: ApiErrorPayload };
  message?: string;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

export function getErrorMessage(error: unknown, fallback = "An unexpected error occurred"): string {
  if (!error) return fallback;

  // 1. Handle string errors directly
  if (typeof error === "string") return error;

  // 2. Handle Axios/Fetch error responses
  const data = isRecord(error)
    ? (error as ApiErrorShape).response?.data
    : undefined;
  if (data) {
    const detail = data.detail;
    
    // Pydantic list of errors: [{ type, loc, msg, input }, ...]
    if (Array.isArray(detail) && isRecord(detail[0]) && typeof (detail[0] as ApiErrorDetail).msg === "string") {
      return (detail[0] as ApiErrorDetail).msg as string;
    }
    
    // Single detail string or object
    if (detail) {
      if (typeof detail === "string") return detail;
      if (isRecord(detail) && typeof (detail as ApiErrorDetail).message === "string") {
        return (detail as ApiErrorDetail).message as string;
      }
      if (isRecord(detail) && typeof (detail as ApiErrorDetail).msg === "string") {
        return (detail as ApiErrorDetail).msg as string;
      }
    }

    if (data.message) return data.message;
  }

  // 3. Handle generic Error objects
  if (isRecord(error) && typeof (error as ApiErrorShape).message === "string") {
    return (error as ApiErrorShape).message as string;
  }

  return fallback;
}
