"use client";

import React, { useState, useEffect } from "react";
import {
  Gauge,
  Smartphone,
  Zap,
  Search,
  Shield,
  Layers,
  CheckCircle2,
  AlertTriangle,
  ExternalLink,
  RefreshCw,
  FileText
} from "lucide-react";
import { Lead } from "@/types";
import { apiFetch } from "@/lib/api";
import { LeadDetailModal } from "@/components/LeadDetailModal";
import { TechnicalAuditReportModal } from "@/components/TechnicalAuditReportModal";

export default function AuditsPage() {
  const [leadsWithAudits, setLeadsWithAudits] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLeadId, setSelectedLeadId] = useState<number | null>(null);
  const [reportModalLeadId, setReportModalLeadId] = useState<number | null>(null);

  const fetchAudits = async () => {
    setLoading(true);
    try {
      const data = await apiFetch<{ leads: Lead[] }>("/leads?limit=50");
      setLeadsWithAudits(data.leads.filter((l) => l.audit !== null));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAudits();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Website Intelligence & Technical Audits</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Deterministic measurements across Mobile, Performance, SEO, Security, Accessibility, and Conversion Funnels.
          </p>
        </div>

        <button
          onClick={fetchAudits}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded-lg text-xs font-semibold shadow-2xs self-start"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Audits</span>
        </button>
      </div>

      {/* Audited Sites Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {loading ? (
          <div className="col-span-full py-16 text-center text-xs text-slate-400">Loading audit records...</div>
        ) : leadsWithAudits.length === 0 ? (
          <div className="col-span-full py-16 text-center text-xs text-slate-400">No audited websites found.</div>
        ) : (
          leadsWithAudits.map((l) => {
            const audit = l.audit!;
            return (
              <div
                key={l.id}
                onClick={() => setSelectedLeadId(l.id)}
                className="p-5 bg-white rounded-lg border border-slate-200 shadow-xs hover:shadow-sm hover:border-blue-300 transition cursor-pointer space-y-4 text-xs"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="font-bold text-sm text-slate-900 leading-tight">
                      {l.company.business_name}
                    </h2>
                    <div className="text-[11px] text-slate-500 flex items-center gap-1 mt-0.5">
                      <span>{l.company.domain || l.company.website}</span>
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="text-[10px] uppercase font-bold text-slate-400">Overall Health</span>
                    <div className="text-lg font-mono font-bold text-slate-900">{audit.overall_score}/100</div>
                  </div>
                </div>

                {/* Score Pills Grid */}
                <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
                  <div className="p-2 rounded bg-slate-50 border border-slate-100">
                    <div className="text-slate-400 text-[10px]">Mobile</div>
                    <div className={`font-mono font-bold ${audit.mobile_score < 60 ? "text-rose-600" : "text-slate-800"}`}>
                      {audit.mobile_score}
                    </div>
                  </div>
                  <div className="p-2 rounded bg-slate-50 border border-slate-100">
                    <div className="text-slate-400 text-[10px]">Speed</div>
                    <div className={`font-mono font-bold ${audit.performance_score < 60 ? "text-amber-600" : "text-slate-800"}`}>
                      {audit.performance_score}
                    </div>
                  </div>
                  <div className="p-2 rounded bg-slate-50 border border-slate-100">
                    <div className="text-slate-400 text-[10px]">SEO</div>
                    <div className="font-mono font-bold text-slate-800">{audit.seo_score}</div>
                  </div>
                </div>

                {/* Primary Opportunity Tag */}
                <div className="p-2.5 rounded bg-blue-50/70 border border-blue-200/80 text-blue-900">
                  <div className="text-[10px] uppercase font-bold text-blue-700">Identified Agency Opportunity</div>
                  <div className="font-semibold text-xs mt-0.5">{l.primary_opportunity || "Website Redesign"}</div>
                </div>

                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px]">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setReportModalLeadId(l.id);
                    }}
                    className="flex items-center gap-1 font-semibold text-slate-700 hover:text-blue-600 px-2 py-0.5 rounded bg-slate-100 hover:bg-blue-50 border border-slate-200"
                  >
                    <FileText className="w-3 h-3 text-blue-600" />
                    <span>View R&D Doc</span>
                  </button>
                  <span className="text-blue-600 font-semibold hover:underline">Deep Audit &rarr;</span>
                </div>
              </div>
            );
          })
        )}
      </div>

      <TechnicalAuditReportModal
        leadId={reportModalLeadId}
        onClose={() => setReportModalLeadId(null)}
      />

      <LeadDetailModal
        leadId={selectedLeadId}
        onClose={() => setSelectedLeadId(null)}
        onRefreshList={fetchAudits}
      />
    </div>
  );
}
