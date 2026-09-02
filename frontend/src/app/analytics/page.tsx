"use client";

import React, { useState, useEffect } from "react";
import { BarChart3, TrendingUp, Compass, Award, Send, Users, ShieldCheck } from "lucide-react";
import { DashboardStats } from "@/types";
import { apiFetch } from "@/lib/api";

export default function AnalyticsPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [sources, setSources] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiFetch<DashboardStats>("/analytics/dashboard"),
      apiFetch<any[]>("/sources")
    ])
      .then(([statsData, sourcesData]) => {
        setStats(statsData);
        setSources(sourcesData);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Discovery & Pipeline Analytics</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Real database measurements of source yield, lead qualification velocity, and outreach conversion rates.
        </p>
      </div>

      {/* Source Performance Table */}
      <div className="p-6 bg-white rounded-lg border border-slate-200 shadow-xs space-y-4">
        <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
          Multi-Source Discovery Yield & Health Metrics
        </h2>

        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50 text-slate-500 font-bold uppercase tracking-wider text-[10px]">
              <th className="p-3">Source Name</th>
              <th className="p-3">Adapter Type</th>
              <th className="p-3">Connection Status</th>
              <th className="p-3">Total Discovered</th>
              <th className="p-3">New Records</th>
              <th className="p-3">Duplicates Filtered</th>
              <th className="p-3">Rate Limit</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-700">
            {sources.map((s) => (
              <tr key={s.id} className="hover:bg-slate-50">
                <td className="p-3 font-bold text-slate-900">{s.name}</td>
                <td className="p-3 font-mono text-[11px] text-slate-600">{s.source_type}</td>
                <td className="p-3">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    {s.status}
                  </span>
                </td>
                <td className="p-3 font-mono font-bold text-slate-900">{s.total_discovered}</td>
                <td className="p-3 font-mono font-bold text-emerald-600">+{s.total_new_records}</td>
                <td className="p-3 font-mono text-slate-400">{s.total_duplicates}</td>
                <td className="p-3 text-slate-500">{s.rate_limit_per_min} req/min</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Outreach Funnel Analytics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-5 rounded-lg bg-white border border-slate-200 shadow-xs space-y-2">
          <div className="text-xs font-bold text-slate-500">Outreach Reply Rate</div>
          <div className="text-2xl font-bold font-mono text-slate-900">
            {stats && stats.emails_sent_count > 0
              ? `${Math.round((stats.replies_count / stats.emails_sent_count) * 100)}%`
              : "0%"}
          </div>
          <div className="text-[11px] text-slate-400">
            {stats?.replies_count || 0} total replies from {stats?.emails_sent_count || 0} sent
          </div>
        </div>

        <div className="p-5 rounded-lg bg-white border border-slate-200 shadow-xs space-y-2">
          <div className="text-xs font-bold text-slate-500">Positive Sentiment Conversion</div>
          <div className="text-2xl font-bold font-mono text-emerald-600">
            {stats && stats.replies_count > 0
              ? `${Math.round((stats.positive_replies_count / stats.replies_count) * 100)}%`
              : "0%"}
          </div>
          <div className="text-[11px] text-slate-400">
            {stats?.positive_replies_count || 0} positive responses classified by AI
          </div>
        </div>

        <div className="p-5 rounded-lg bg-white border border-slate-200 shadow-xs space-y-2">
          <div className="text-xs font-bold text-slate-500">Meeting Booking Rate</div>
          <div className="text-2xl font-bold font-mono text-blue-600">
            {stats && stats.positive_replies_count > 0
              ? `${Math.round((stats.meetings_count / stats.positive_replies_count) * 100)}%`
              : "0%"}
          </div>
          <div className="text-[11px] text-slate-400">
            {stats?.meetings_count || 0} scheduled discovery calls
          </div>
        </div>
      </div>
    </div>
  );
}
