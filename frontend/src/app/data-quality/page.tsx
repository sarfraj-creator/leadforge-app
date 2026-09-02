"use client";

import React, { useState, useEffect } from "react";
import {
  ShieldCheck,
  AlertCircle,
  RefreshCw,
  Layers,
  CheckCircle2,
  UserCheck,
  Globe,
  Mail,
  Phone,
  Sparkles,
  Clock,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  BarChart3,
  Filter
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import Link from "next/link";

export default function DataQualityPage() {
  const [data, setData] = useState<any>(null);
  const [rejections, setRejections] = useState<any[]>([]);
  const [sourcePerformance, setSourcePerformance] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchQualityMetrics = async () => {
    setLoading(true);
    try {
      const [qData, rData, spData] = await Promise.all([
        apiFetch("/analytics/data-quality"),
        apiFetch("/analytics/rejection-reasons"),
        apiFetch("/analytics/source-performance")
      ]);
      setData(qData);
      setRejections(rData || []);
      setSourcePerformance(spData || []);
    } catch (err) {
      console.error("Failed to fetch data quality metrics:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQualityMetrics();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">Database Data Quality & Provenance Truth</h1>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              Zero Fabrication Guarantee
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Deterministic stage metrics, multi-source field provenance, rejection telemetry, and source yield rankings.
          </p>
        </div>

        <button
          onClick={fetchQualityMetrics}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-medium transition self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-blue-600" : ""}`} />
          <span>Refresh Truth Metrics</span>
        </button>
      </div>

      {/* 10-Stage Pipeline Progression Card */}
      <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="space-y-0.5">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <Layers className="w-4 h-4 text-blue-600" />
              <span>Strict 8-Stage Qualification Funnel & Database Inventory</span>
            </h3>
            <p className="text-[11px] text-slate-500">
              Leads must provide demonstrable evidence at every step before advancing.
            </p>
          </div>
          <Link
            href="/review"
            className="flex items-center gap-1 text-xs font-semibold text-blue-600 hover:underline"
          >
            <span>Review Queue</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-center">
          <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
            <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">1. Discovered</div>
            <div className="text-xl font-bold font-mono text-slate-900 mt-1">{data?.total_discovered || 0}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Public Sources</div>
          </div>

          <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
            <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">2. Identity Match</div>
            <div className="text-xl font-bold font-mono text-blue-600 mt-1">{data?.identity_verified || 0}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">9-Signal Confirmed</div>
          </div>

          <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
            <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">3. Web Verified</div>
            <div className="text-xl font-bold font-mono text-purple-600 mt-1">{data?.website_verified || 0}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Official Reachable</div>
          </div>

          <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
            <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">4. Audited</div>
            <div className="text-xl font-bold font-mono text-indigo-600 mt-1">{data?.audit_complete || 0}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">7-Dimension Scan</div>
          </div>

          <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
            <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">5. Opp Detected</div>
            <div className="text-xl font-bold font-mono text-amber-600 mt-1">{data?.opportunity_detected || 0}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">9 Core Services</div>
          </div>

          <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
            <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">6. Buying Intent</div>
            <div className="text-xl font-bold font-mono text-slate-800 mt-1">{data?.intent_known || 0}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Explicit Public RFP</div>
          </div>

          <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
            <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">7. Contactable</div>
            <div className="text-xl font-bold font-mono text-teal-600 mt-1">{data?.contactable || 0}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">MX / Phone Valid</div>
          </div>

          <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
            <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">8. Qualified</div>
            <div className="text-xl font-bold font-mono text-blue-700 mt-1">{data?.qualified || 0}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Quality &ge; 70</div>
          </div>

          <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
            <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">9. Review Gate</div>
            <div className="text-xl font-bold font-mono text-amber-700 mt-1">{data?.sales_ready || 0}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Pending Approval</div>
          </div>

          <div className="p-3 rounded-lg bg-emerald-50/60 border border-emerald-200">
            <div className="text-[10px] text-emerald-800 font-bold uppercase tracking-wider">10. Sales Ready</div>
            <div className="text-xl font-bold font-mono text-emerald-700 mt-1">{data?.sales_ready || 0}</div>
            <div className="text-[10px] text-emerald-600 mt-0.5">Approved for Outreach</div>
          </div>
        </div>
      </div>

      {/* KPI Ratios Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="font-semibold">Source Provenance</span>
            <ShieldCheck className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-2xl font-bold font-mono text-blue-700">
            {data?.percentages?.source_provenance_rate || 0}%
          </div>
          <p className="text-[11px] text-slate-500">
            Records backed by verifiable public registry or OSM data.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="font-semibold">Official Website Match</span>
            <Globe className="w-4 h-4 text-purple-600" />
          </div>
          <div className="text-2xl font-bold font-mono text-purple-700">
            {data?.percentages?.website_verification_rate || 0}%
          </div>
          <p className="text-[11px] text-slate-500">
            Reachable URLs verified against corporate identity.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="font-semibold">Contact Provenance</span>
            <Mail className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold font-mono text-emerald-700">
            {data?.percentages?.contact_provenance_rate || 0}%
          </div>
          <p className="text-[11px] text-slate-500">
            Direct MX mail-enabled or telephone reachable channels.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="font-semibold">Fresh Records (0-7d)</span>
            <Clock className="w-4 h-4 text-teal-600" />
          </div>
          <div className="text-2xl font-bold font-mono text-teal-700">
            {data?.percentages?.fresh_rate || 100}%
          </div>
          <p className="text-[11px] text-slate-500">
            Live observations within the active 7-day window.
          </p>
        </div>
      </div>

      {/* Rejection Reasons & Source Performance Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 text-xs">
        {/* Rejection Reasons Breakdown */}
        <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-xs space-y-3">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
            <div className="font-bold text-sm text-slate-900 flex items-center gap-2">
              <Filter className="w-4 h-4 text-rose-600" />
              <span>Rejection Telemetry & Qualification Filters</span>
            </div>
            <span className="text-[11px] text-slate-500 font-normal">Exact Filter Counts</span>
          </div>

          <p className="text-[11px] text-slate-500">
            Why discovered entities did not advance to Qualified or Sales Ready status:
          </p>

          {rejections.length > 0 ? (
            <div className="space-y-2">
              {rejections.map((rej, idx) => (
                <div key={idx} className="flex items-center justify-between p-2 rounded bg-slate-50 border border-slate-100 text-xs">
                  <span className="font-mono text-slate-700 font-medium">{rej.reason.replace("_", " ")}</span>
                  <span className="font-mono font-bold text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-200">
                    {rej.count} filtered
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-6 text-slate-400 text-xs">
              No rejection telemetry recorded for current jobs.
            </div>
          )}
        </div>

        {/* Source Performance Yield */}
        <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-xs space-y-3">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
            <div className="font-bold text-sm text-slate-900 flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-blue-600" />
              <span>Source Performance & Yield Ranking</span>
            </div>
            <span className="text-[11px] text-slate-500 font-normal">Adapter Statistics</span>
          </div>

          <p className="text-[11px] text-slate-500">
            Yield efficiency and contact conversion rates across active discovery adapters:
          </p>

          {sourcePerformance.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-[11px] border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 text-slate-500 uppercase bg-slate-50">
                    <th className="p-2 font-semibold">Adapter</th>
                    <th className="p-2 font-semibold">Discovered</th>
                    <th className="p-2 font-semibold">Web Verified</th>
                    <th className="p-2 font-semibold">Contacts</th>
                    <th className="p-2 font-semibold">Qual Yield</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {sourcePerformance.map((sp, idx) => (
                    <tr key={idx} className="hover:bg-slate-50">
                      <td className="p-2 font-bold text-slate-900">{sp.source}</td>
                      <td className="p-2 font-mono text-slate-700">{sp.discovered_count}</td>
                      <td className="p-2 font-mono text-purple-700">{sp.website_verification_rate}%</td>
                      <td className="p-2 font-mono text-emerald-700">{sp.contact_rate}%</td>
                      <td className="p-2 font-mono font-bold text-blue-700">{sp.qualification_rate}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-6 text-slate-400 text-xs">
              No source performance statistics available.
            </div>
          )}
        </div>
      </div>

      {/* Contradiction & Human Review Card */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between text-slate-700 font-semibold">
            <span>Contradiction Detection Rate</span>
            <AlertTriangle className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-bold font-mono text-amber-700">
            {data?.percentages?.conflicting_rate || 0}%
          </div>
          <p className="text-[11px] text-slate-500">
            Cross-source discrepancies are preserved and flagged without silent overwrites.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between text-slate-700 font-semibold">
            <span>Human Review Queue</span>
            <UserCheck className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-2xl font-bold font-mono text-blue-700">
            {data?.sales_ready || 0}
          </div>
          <Link
            href="/review"
            className="text-[11px] font-semibold text-blue-600 hover:underline flex items-center gap-1"
          >
            <span>Open Human Review Queue &rarr;</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
