import React from "react";

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
