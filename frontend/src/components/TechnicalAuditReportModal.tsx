"use client";

import React, { useState, useEffect } from "react";
import {
  X,
  Printer,
  Send,
  Sparkles,
  ShieldCheck,
  Smartphone,
  Zap,
  Globe,
  CheckCircle2,
  AlertTriangle,
  ExternalLink,
  Layers,
  TrendingUp,
  FileText
} from "lucide-react";
import { TechnicalAuditReport } from "@/types";
import { apiFetch } from "@/lib/api";

interface TechnicalAuditReportModalProps {
  leadId: number | null;
  onClose: () => void;
  onOpenComposer?: (leadId: number) => void;
}

export function TechnicalAuditReportModal({
  leadId,
  onClose,
  onOpenComposer
}: TechnicalAuditReportModalProps) {
  const [report, setReport] = useState<TechnicalAuditReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!leadId) {
      setReport(null);
      return;
    }

    const fetchReport = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await apiFetch<TechnicalAuditReport>(`/audits/lead/${leadId}/report`);
        setReport(data);
      } catch (err: any) {
        setError(err.message || "Failed to load Technical R&D Audit Report");
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [leadId]);

  if (!leadId) return null;

  const handlePrint = () => {
    window.open(`http://localhost:8000/api/audits/lead/${leadId}/report/html`, "_blank");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs overflow-y-auto">
      <div className="w-full max-w-4xl bg-white rounded-xl shadow-2xl border border-slate-200 flex flex-col my-8 max-h-[90vh] overflow-hidden">
        {/* Modal Toolbar Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-900 text-white">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center shadow-inner">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white tracking-tight">
                  {report ? report.company.business_name : "Loading Report..."}
                </h2>
                {report && (
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-400/30">
                    {report.category_label}
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                LeadForge Deterministic R&D Audit Document &bull; {report?.report_id || "Generating..."}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handlePrint}
              disabled={!report}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition disabled:opacity-50"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print / Export PDF</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading ? (
            <div className="py-24 text-center space-y-3">
              <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
              <div className="text-xs text-slate-500 font-medium">
                Compiling deterministic technical audit, Core Web Vitals, and modernization proposal...
              </div>
            </div>
          ) : error ? (
            <div className="p-4 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs">
              {error}
            </div>
          ) : report ? (
            <>
              {/* Executive Overview Header */}
              <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="text-xs text-slate-500">
                    Industry: <span className="font-semibold text-slate-800">{report.company.industry || "General Business"}</span> &bull; Location: <span className="font-semibold text-slate-800">{report.company.city || "Global"}</span>
                  </div>
                  <div className="text-xs text-slate-500">
                    Official Website / Domain:{" "}
                    {report.company.website !== "None" ? (
                      <a
                        href={report.company.website.startsWith("http") ? report.company.website : `https://${report.company.website}`}
                        target="_blank"
                        rel="noreferrer"
                        className="font-mono text-blue-600 font-semibold hover:underline inline-flex items-center gap-1"
                      >
                        {report.company.domain || report.company.website}
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    ) : (
                      <span className="font-semibold text-amber-700">No Web Footprint Found (New Build Opportunity)</span>
                    )}
                  </div>
                  <div className="text-xs text-slate-500">
                    Primary Contact: <span className="font-semibold text-slate-800">{report.contact.name}</span> ({report.contact.title}) &bull; <span className="font-mono">{report.contact.email || "Email unverified"}</span>
                  </div>
                </div>

                <div className="text-right shrink-0">
                  <div className="text-[10px] uppercase font-bold text-slate-400">Deterministic Overall Health</div>
                  <div className={`text-2xl font-mono font-bold ${report.scores.overall_score >= 75 ? "text-emerald-600" : report.scores.overall_score >= 50 ? "text-amber-600" : "text-rose-600"}`}>
                    {report.scores.overall_score}/100
                  </div>
                </div>
              </div>

              {/* 4 Scorecard Metrics */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 rounded-lg border border-slate-200 bg-white shadow-2xs text-center space-y-1">
                  <div className="flex items-center justify-center text-slate-400">
                    <Smartphone className="w-4 h-4 text-blue-600" />
                  </div>
                  <div className="text-[10px] uppercase font-bold text-slate-400">Mobile Experience</div>
                  <div className={`text-lg font-mono font-bold ${report.scores.mobile_score < 60 ? "text-rose-600" : "text-slate-800"}`}>
                    {report.scores.mobile_score}/100
                  </div>
                </div>

                <div className="p-3 rounded-lg border border-slate-200 bg-white shadow-2xs text-center space-y-1">
                  <div className="flex items-center justify-center text-slate-400">
                    <Zap className="w-4 h-4 text-amber-500" />
                  </div>
                  <div className="text-[10px] uppercase font-bold text-slate-400">Speed / CWV</div>
                  <div className={`text-lg font-mono font-bold ${report.scores.performance_score < 60 ? "text-amber-600" : "text-slate-800"}`}>
                    {report.scores.performance_score}/100
                  </div>
                </div>

                <div className="p-3 rounded-lg border border-slate-200 bg-white shadow-2xs text-center space-y-1">
                  <div className="flex items-center justify-center text-slate-400">
                    <Globe className="w-4 h-4 text-indigo-500" />
                  </div>
                  <div className="text-[10px] uppercase font-bold text-slate-400">SEO & Structure</div>
                  <div className="text-lg font-mono font-bold text-slate-800">
                    {report.scores.seo_score}/100
                  </div>
                </div>

                <div className="p-3 rounded-lg border border-slate-200 bg-white shadow-2xs text-center space-y-1">
                  <div className="flex items-center justify-center text-slate-400">
                    <ShieldCheck className="w-4 h-4 text-emerald-500" />
                  </div>
                  <div className="text-[10px] uppercase font-bold text-slate-400">Security & SSL</div>
                  <div className="text-lg font-mono font-bold text-slate-800">
                    {report.scores.security_score}/100
                  </div>
                </div>
              </div>

              {/* Observed Deficiencies & Findings */}
              <div className="space-y-3">
                <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                    Observable Technical Deficiencies ({report.issues.length})
                  </h3>
                  <span className="text-[11px] text-slate-400">Zero Synthetic Hallucinations</span>
                </div>

                {report.issues.length === 0 ? (
                  <div className="p-4 rounded bg-slate-50 text-xs text-slate-500 text-center">
                    No critical technical deficiencies observed. Website complies with baseline standards.
                  </div>
                ) : (
                  <div className="space-y-2.5">
                    {report.issues.map((iss, idx) => {
                      const isCrit = iss.severity.toLowerCase() === "critical";
                      const isHigh = iss.severity.toLowerCase() === "high";
                      return (
                        <div
                          key={idx}
                          className={`p-3.5 rounded-lg border text-xs space-y-1.5 ${
                            isCrit
                              ? "bg-rose-50/50 border-rose-200"
                              : isHigh
                              ? "bg-amber-50/50 border-amber-200"
                              : "bg-blue-50/50 border-blue-200"
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="font-bold text-slate-900 flex items-center gap-2">
                              <AlertTriangle
                                className={`w-3.5 h-3.5 ${
                                  isCrit ? "text-rose-600" : isHigh ? "text-amber-600" : "text-blue-600"
                                }`}
                              />
                              <span>{iss.title}</span>
                            </div>
                            <span
                              className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded ${
                                isCrit
                                  ? "bg-rose-600 text-white"
                                  : isHigh
                                  ? "bg-amber-600 text-white"
                                  : "bg-blue-600 text-white"
                              }`}
                            >
                              {iss.severity}
                            </span>
                          </div>

                          <div className="text-slate-600">
                            <strong>Observed Evidence:</strong> {iss.evidence}
                          </div>

                          <div className="p-2 rounded bg-white/80 border border-slate-200/80 text-blue-900 text-[11px]">
                            <strong>Agency Action:</strong> {iss.recommendation}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Strategic Modernization Blueprint */}
              <div className="space-y-3">
                <div className="border-b border-slate-200 pb-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                    Strategic Modernization Blueprint
                  </h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {report.action_plan.map((act, idx) => (
                    <div key={idx} className="p-3 rounded-lg border border-slate-200 bg-slate-50 space-y-1 text-xs">
                      <div className="font-bold text-blue-700">{act.phase}</div>
                      <div className="text-slate-600">{act.action}</div>
                      <div className="text-[11px] font-semibold text-emerald-700 pt-1 border-t border-slate-200/60 mt-1 flex items-center gap-1">
                        <TrendingUp className="w-3 h-3" />
                        <span>Expected Impact: {act.impact}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Executive Proposal Banner */}
              <div className="p-4 rounded-xl bg-slate-900 text-white space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs uppercase font-bold tracking-wider text-blue-400">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Executive Modernization Proposal</span>
                  </div>
                  <span className="text-xs text-slate-400">LeadForge Agency Package</span>
                </div>

                <div className="text-sm font-bold text-white">
                  {report.agency_recommendation.service}
                </div>

                <div className="grid grid-cols-2 gap-4 pt-2 border-t border-slate-800 text-xs">
                  <div>
                    <span className="text-slate-400">Estimated Turnaround:</span>{" "}
                    <span className="font-semibold text-slate-200">{report.agency_recommendation.estimated_timeline}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">Projected Value:</span>{" "}
                    <span className="font-semibold text-emerald-400">{report.agency_recommendation.projected_roi}</span>
                  </div>
                </div>
              </div>
            </>
          ) : null}
        </div>

        {/* Modal Footer Toolbar */}
        <div className="px-6 py-3.5 border-t border-slate-200 bg-slate-50 flex items-center justify-between">
          <div className="text-xs text-slate-500">
            Document attachable to automated 3/7/14-day sequences.
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-3.5 py-1.5 text-xs text-slate-600 hover:text-slate-900 font-medium"
            >
              Close
            </button>
            {onOpenComposer && (
              <button
                onClick={() => {
                  onClose();
                  onOpenComposer(leadId);
                }}
                className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-xs transition"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Send Email with Attached Report</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
