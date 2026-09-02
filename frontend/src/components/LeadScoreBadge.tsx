import React from "react";

interface LeadScoreBadgeProps {
  score?: number;
  category?: string;
  size?: "sm" | "md" | "lg";
}

export function LeadScoreBadge({ score = 0, category, size = "md" }: LeadScoreBadgeProps) {
  let cat = category;
  if (!cat) {
    if (score >= 90) cat = "HOT";
    else if (score >= 75) cat = "HIGH";
    else if (score >= 60) cat = "MEDIUM";
    else cat = "LOW";
  }

  let colorClasses = "bg-slate-100 text-slate-700 border-slate-200";
  if (cat === "HOT") {
    colorClasses = "bg-emerald-50 text-emerald-700 border-emerald-200";
  } else if (cat === "HIGH") {
    colorClasses = "bg-blue-50 text-blue-700 border-blue-200";
  } else if (cat === "MEDIUM") {
    colorClasses = "bg-amber-50 text-amber-700 border-amber-200";
  } else {
    colorClasses = "bg-slate-50 text-slate-600 border-slate-200";
  }

  const sizeClasses = size === "sm" ? "px-2 py-0.5 text-xs font-semibold" : size === "lg" ? "px-3 py-1 text-base font-bold" : "px-2.5 py-1 text-xs font-semibold";

  return (
    <span className={`inline-flex items-center gap-1.5 rounded border ${sizeClasses} ${colorClasses}`}>
      <span className="font-mono">{score}</span>
      <span className="text-[10px] uppercase tracking-wider opacity-75">/ 100</span>
      <span className="ml-1 text-[10px] font-bold uppercase">{cat}</span>
    </span>
  );
}

interface FreshnessBadgeProps {
  state?: "FRESH" | "RECENT" | "STALE" | "NEEDS_RECHECK" | string;
  checkedAt?: string;
}

export function FreshnessBadge({ state = "FRESH", checkedAt }: FreshnessBadgeProps) {
  let color = "bg-emerald-50 text-emerald-700 border-emerald-200";
  let label = "Fresh";

  if (state === "RECENT") {
    color = "bg-blue-50 text-blue-700 border-blue-200";
    label = "Recent";
  } else if (state === "STALE") {
    color = "bg-amber-50 text-amber-700 border-amber-200";
    label = "Stale";
  } else if (state === "NEEDS_RECHECK") {
    color = "bg-rose-50 text-rose-700 border-rose-200";
    label = "Needs Recheck";
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded border text-xs font-medium ${color}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
      <span>{label}</span>
    </span>
  );
}
