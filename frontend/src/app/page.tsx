"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  Flame,
  CheckCircle2,
  Gauge,
  Send,
  MessageSquare,
  Sparkles,
  Calendar,
  Award,
  DollarSign,
  TrendingUp,
  ArrowRight,
  Plus,
  Building2,
  Compass,
  AlertCircle
} from "lucide-react";
import { DashboardStats } from "@/types";
import { apiFetch } from "@/lib/api";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [opps, setOpps] = useState<Array<{ opportunity: string; count: number }>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiFetch<DashboardStats>("/analytics/dashboard"),
      apiFetch<Array<{ opportunity: string; count: number }>>("/analytics/opportunities-distribution")
    ])
      .then(([statsData, oppsData]) => {
        setStats(statsData);
        setOpps(Array.isArray(oppsData) ? oppsData : []);
      })
      .catch((err) => {
        console.error(err);
        setOpps([]);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Title & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Executive Dashboard</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Observational lead discovery, technical audit intelligence, and outreach metrics.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link
            href="/discovery"
            className="flex items-center gap-1.5 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-xs font-semibold shadow-xs transition"
          >
            <Compass className="w-3.5 h-3.5" />
            <span>Launch Discovery</span>
          </Link>
          <Link
            href="/leads"
            className="flex items-center gap-1.5 px-3.5 py-1.5 bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 rounded-md text-xs font-medium transition"
          >
            <span>View All Leads</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* Zero Leads Onboarding Banner */}
      {!loading && stats?.qualified_leads_count === 0 && (
        <div className="p-6 rounded-lg bg-blue-50/80 border border-blue-200 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="font-bold text-sm text-blue-900 flex items-center gap-2">
              <Compass className="w-4 h-4 text-blue-600" />
              <span>Ready for Real Global Lead Discovery</span>
            </div>
            <p className="text-xs text-blue-700">
              No mock data exists. Configure a global discovery job targeting businesses worldwide (e.g. Restaurants, Dental, Agencies) to discover real prospects with observable technical service needs.
            </p>
          </div>
          <Link
            href="/discovery"
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded font-semibold text-xs shrink-0 shadow-xs flex items-center gap-1.5"
          >
            <Compass className="w-3.5 h-3.5" />
            <span>Launch Real Discovery</span>
          </Link>
        </div>
      )}

      {/* Top 4 Primary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-lg bg-white border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">Fresh Qualified Leads</span>
            <div className="p-1.5 rounded-md bg-emerald-50 text-emerald-600">
              <Flame className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-slate-900">
              {loading ? "..." : stats?.fresh_leads_count || 0}
            </span>
            <span className="text-[11px] font-semibold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
              Verified &lt; 7d
            </span>
          </div>
          <div className="mt-1 text-[11px] text-slate-400">
            Total qualified prospects: {stats?.qualified_leads_count || 0}
          </div>
        </div>

        <div className="p-4 rounded-lg bg-white border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">High Urgency (Hot) Leads</span>
            <div className="p-1.5 rounded-md bg-rose-50 text-rose-600">
              <Sparkles className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-slate-900">
              {loading ? "..." : stats?.hot_leads_count || 0}
            </span>
            <span className="text-[11px] font-semibold text-rose-600 bg-rose-50 px-1.5 py-0.5 rounded">
              Score 90+
            </span>
          </div>
          <div className="mt-1 text-[11px] text-slate-400">Severe mobile/conversion defects</div>
        </div>

        <div className="p-4 rounded-lg bg-white border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">Interested Replies</span>
            <div className="p-1.5 rounded-md bg-blue-50 text-blue-600">
              <MessageSquare className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-slate-900">
              {loading ? "..." : stats?.positive_replies_count || 0}
            </span>
            <span className="text-[11px] font-semibold text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded">
              Positive Sentiment
            </span>
          </div>
          <div className="mt-1 text-[11px] text-slate-400">
            From {stats?.emails_sent_count || 0} emails dispatched
          </div>
        </div>

        <div className="p-4 rounded-lg bg-white border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">Active Pipeline Value</span>
            <div className="p-1.5 rounded-md bg-amber-50 text-amber-600">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-slate-900">
              ${loading ? "..." : (stats?.pipeline_value || 0).toLocaleString()}
            </span>
            <span className="text-[11px] font-semibold text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded">
              {stats?.won_deals_count || 0} Won Deals
            </span>
          </div>
          <div className="mt-1 text-[11px] text-slate-400">
            {stats?.meetings_count || 0} Meetings · {stats?.proposals_count || 0} Proposals
          </div>
        </div>
      </div>

      {/* Secondary Grid: Pipeline Stage Funnel & Opportunities Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Opportunity Breakdown */}
        <div className="p-5 rounded-lg bg-white border border-slate-200 shadow-xs lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Observable Agency Service Opportunities
              </h2>
              <p className="text-[11px] text-slate-500">
                Calculated strictly from deterministic technical audits
              </p>
            </div>
            <Link href="/audits" className="text-xs font-semibold text-blue-600 hover:underline">
              Inspect Audits &rarr;
            </Link>
          </div>

          <div className="space-y-3">
            {loading ? (
              <div className="py-8 text-center text-xs text-slate-400">Loading opportunity distribution...</div>
            ) : !opps || opps.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-400">No opportunities detected yet.</div>
            ) : (
              (opps || []).map((item, idx) => {
                const maxCount = Math.max(...(opps || []).map((o) => o.count), 1);
                const percent = Math.round((item.count / maxCount) * 100);
                return (
                  <div key={idx} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-medium text-slate-800">{item.opportunity}</span>
                      <span className="font-mono font-bold text-slate-600">{item.count} leads</span>
                    </div>
                    <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-600 rounded-full transition-all duration-500"
                        style={{ width: `${percent}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Live CRM Stage Flow */}
        <div className="p-5 rounded-lg bg-white border border-slate-200 shadow-xs space-y-4">
          <div className="border-b border-slate-100 pb-3">
            <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              Sales Pipeline Velocity
            </h2>
            <p className="text-[11px] text-slate-500">Active deal distribution by stage</p>
          </div>

          <div className="space-y-2.5">
            {[
              { label: "Qualified", count: stats?.qualified_leads_count || 0, color: "bg-slate-400" },
              { label: "Outreach Contacted", count: stats?.emails_sent_count || 0, color: "bg-blue-500" },
              { label: "Interested Replies", count: stats?.positive_replies_count || 0, color: "bg-indigo-500" },
              { label: "Meetings Scheduled", count: stats?.meetings_count || 0, color: "bg-amber-500" },
              { label: "Proposals Sent", count: stats?.proposals_count || 0, color: "bg-cyan-500" },
              { label: "Won Contracts", count: stats?.won_deals_count || 0, color: "bg-emerald-500" },
            ].map((st, i) => (
              <div key={i} className="flex items-center justify-between p-2 rounded-md bg-slate-50 border border-slate-100 text-xs">
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${st.color}`}></span>
                  <span className="font-medium text-slate-700">{st.label}</span>
                </div>
                <span className="font-mono font-bold text-slate-900">{loading ? "..." : st.count}</span>
              </div>
            ))}
          </div>

          <Link
            href="/crm"
            className="block text-center w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded text-xs transition"
          >
            Open Kanban Board
          </Link>
        </div>
      </div>

      {/* Recent Activity Timeline */}
      <div className="p-5 rounded-lg bg-white border border-slate-200 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div>
            <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              Recent System & Outreach Activity
            </h2>
            <p className="text-[11px] text-slate-500">Live operational audit and pipeline events</p>
          </div>
        </div>

        <div className="divide-y divide-slate-100">
          {loading ? (
            <div className="py-6 text-center text-xs text-slate-400">Loading recent activities...</div>
          ) : !stats?.recent_activities || stats.recent_activities.length === 0 ? (
            <div className="py-6 text-center text-xs text-slate-400">No activity logged yet.</div>
          ) : (
            stats.recent_activities.map((act) => (
              <div key={act.id} className="py-2.5 flex items-start justify-between gap-4 text-xs">
                <div>
                  <div className="font-bold text-slate-900">{act.title}</div>
                  <div className="text-slate-500 text-[11px] mt-0.5">{act.description}</div>
                </div>
                <div className="text-[10px] text-slate-400 shrink-0">
                  {new Date(act.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
