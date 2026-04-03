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
  if (score >= 75) return "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
  if (score >= 50) return "bg-amber-500/20 text-amber-400 border border-amber-500/30";
  return "bg-red-500/20 text-red-400 border border-red-500/30";
}

export function getStatusClass(status: string): string {
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
    offer_declined: "bg-orange-500/20 text-orange-400 border border-orange-500/30",
    rejected: "status-rejected",
    withdrawn: "bg-gray-500/20 text-gray-400 border border-gray-500/30",
    failed: "status-rejected",
    skipped: "bg-zinc-500/20 text-zinc-400 border border-zinc-500/30",
  };
  return map[status] ?? "bg-zinc-500/20 text-zinc-400 border border-zinc-500/30";
}

export function getStatusLabel(status: string): string {
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
  return map[status] ?? status.replace(/_/g, " ");
}

export function truncate(str: string, n: number): string {
  return str.length > n ? str.slice(0, n) + "…" : str;
}
