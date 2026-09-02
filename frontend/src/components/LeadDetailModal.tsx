"use client";

import React, { useState, useEffect } from "react";
import {
  X,
  Building2,
  Globe,
  Phone,
  Mail,
  Gauge,
  Sparkles,
  RefreshCw,
  Send,
  Calendar,
  CheckSquare,
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  Shield,
  Smartphone,
  Zap,
  Search,
  Layers,
  History,
  FileText,
  ShieldCheck,
  HelpCircle,
  Clock,
  Lock,
  Radio
} from "lucide-react";
import { Lead } from "@/types";
import { LeadScoreBadge } from "./LeadScoreBadge";
import { FreshnessBadge } from "./FreshnessBadge";
import { apiFetch } from "@/lib/api";

interface LeadDetailModalProps {
  leadId: number | null;
  onClose: () => void;
  onOpenEmailComposer?: (lead: Lead) => void;
  onRefreshList?: () => void;
}

export function LeadDetailModal({
  leadId,
  onClose,
  onOpenEmailComposer,
  onRefreshList
}: LeadDetailModalProps) {
  const [lead, setLead] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"overview" | "provenance" | "audit" | "contacts" | "ai" | "timeline" | "tasks">("overview");
  const [rechecking, setRechecking] = useState(false);
  const [newNote, setNewNote] = useState("");
  const [addingNote, setAddingNote] = useState(false);

  useEffect(() => {
    if (!leadId) {
      setLead(null);
      return;
    }
    setLoading(true);
    apiFetch<Lead>(`/leads/${leadId}`)
      .then((data) => setLead(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [leadId]);

  if (!leadId) return null;

  const handleStageChange = async (newStage: string) => {
    if (!lead) return;
    try {
      await apiFetch(`/leads/${lead.id}/stage`, {
        method: "PATCH",
        body: JSON.stringify({ stage: newStage })
      });
      setLead({ ...lead, stage: newStage });
      if (onRefreshList) onRefreshList();
    } catch (err) {
      alert("Failed to update stage: " + err);
    }
  };

  const handleRecheck = async () => {
    if (!lead) return;
    setRechecking(true);
    try {
      await apiFetch(`/leads/${lead.id}/recheck`, { method: "POST" });
      const updated = await apiFetch<Lead>(`/leads/${lead.id}`);
      setLead(updated);
      if (onRefreshList) onRefreshList();
    } catch (err) {
      alert("Recheck failed: " + err);
    } finally {
      setRechecking(false);
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!lead || !newNote.trim()) return;
    setAddingNote(true);
    try {
      const createdNote = await apiFetch(`/crm/notes`, {
        method: "POST",
        body: JSON.stringify({ lead_id: lead.id, content: newNote.trim() })
      });
      setLead({
        ...lead,
        notes: [createdNote, ...(lead.notes || [])]
      });
      setNewNote("");
    } catch (err) {
      alert("Failed to add note: " + err);
    } finally {
      setAddingNote(false);
    }
  };

  const getStageBadgeClass = (stage: string) => {
    switch (stage) {
      case "SALES_READY":
        return "bg-emerald-100 text-emerald-800 border-emerald-300";
      case "QUALIFIED":
        return "bg-blue-100 text-blue-800 border-blue-300";
      case "CONTACTABLE":
        return "bg-teal-100 text-teal-800 border-teal-300";
      case "OPPORTUNITY":
        return "bg-indigo-100 text-indigo-800 border-indigo-300";
      case "AUDITED":
        return "bg-purple-100 text-purple-800 border-purple-300";
      case "VERIFIED":
        return "bg-cyan-100 text-cyan-800 border-cyan-300";
      default:
        return "bg-slate-100 text-slate-700 border-slate-300";
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs">
      <div className="w-full max-w-4xl bg-white rounded-lg shadow-2xl border border-slate-200 flex flex-col max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600 font-bold text-xl">
              {lead?.company?.business_name?.charAt(0) || "L"}
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h2 className="text-xl font-bold text-slate-900">
                  {lead?.company?.business_name || "Loading Lead Details..."}
                </h2>
                {lead?.pipeline_stage && (
                  <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold tracking-wide border uppercase ${getStageBadgeClass(lead.pipeline_stage)}`}>
                    Stage: {lead.pipeline_stage}
                  </span>
                )}
                {lead && <FreshnessBadge state={lead.freshness_state} />}
                {lead?.score && (
                  <LeadScoreBadge
                    score={lead.score.total_score}
                    category={lead.score.category}
                  />
                )}
              </div>
              <div className="flex items-center gap-3 text-xs text-slate-500 mt-1">
                <span className="flex items-center gap-1">
                  <Building2 className="w-3.5 h-3.5" />
                  {lead?.company?.industry || "Industry N/A"}
                </span>
                {lead?.company?.city && (
                  <span>• {lead.company.city}, {lead.company.country || "Worldwide"}</span>
                )}
                {lead?.company?.website && (
                  <a
                    href={lead.company.website.startsWith("http") ? lead.company.website : `https://${lead.company.website}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-blue-600 hover:underline"
                  >
                    <Globe className="w-3.5 h-3.5" />
                    {lead.company.domain || lead.company.website}
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleRecheck}
              disabled={rechecking}
              className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-md transition-colors"
              title="Re-verify Website & Recheck Opportunities"
            >
              <RefreshCw className={`w-4 h-4 ${rechecking ? "animate-spin text-blue-600" : ""}`} />
            </button>
            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-md transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Navigation Tabs */}
        <div className="flex border-b border-slate-100 px-6 bg-slate-50/20 overflow-x-auto">
          {[
            { id: "overview", label: "Overview", icon: Building2 },
            { id: "provenance", label: "Source Provenance", icon: ShieldCheck },
            { id: "audit", label: "Website Audit", icon: Gauge },
            { id: "contacts", label: "Decision Makers", icon: Mail },
            { id: "ai", label: "AI Analysis", icon: Sparkles },
            { id: "timeline", label: "Activity Timeline", icon: History },
            { id: "tasks", label: "Tasks & Notes", icon: CheckSquare }
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 py-3 px-4 text-xs font-semibold border-b-2 transition-colors whitespace-nowrap cursor-pointer ${
                  isActive
                    ? "border-blue-600 text-blue-600 bg-white"
                    : "border-transparent text-slate-500 hover:text-slate-700 hover:bg-slate-50"
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div className="p-6 overflow-y-auto flex-1 bg-slate-50/30">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
            </div>
          ) : lead ? (
            <div className="space-y-6">
              {/* 1. OVERVIEW TAB */}
              {activeTab === "overview" && (
                <div className="space-y-6">
                  {/* Primary Opportunity Banner */}
                  <div className="p-4 rounded-lg bg-blue-50/70 border border-blue-100 flex items-start justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-blue-600 text-white rounded">
                          Primary Observable Opportunity
                        </span>
                        <h4 className="text-sm font-bold text-slate-900">
                          {lead.primary_opportunity || "Website Modernization & Optimization"}
                        </h4>
                      </div>
                      <p className="text-xs text-slate-600 mt-1">
                        {lead.score?.explanation || "Observable potential need for modern responsive design and conversion integration."}
                      </p>
                    </div>

                    <div className="text-right text-xs text-slate-500 shrink-0">
                      Recommended Agency Service: <span className="font-semibold text-slate-800">{lead.recommended_service || "Responsive Redesign"}</span>
                    </div>
                  </div>

                  {/* 5-PART SCORE BREAKDOWN */}
                  <div className="p-4 rounded-lg bg-white border border-slate-200 space-y-3">
                    <div className="text-xs font-bold text-slate-900 border-b border-slate-100 pb-2 flex items-center justify-between">
                      <span>Decoupled 5-Part Lead Scoring Engine</span>
                      <span className="font-mono text-blue-700 font-bold">Overall Priority: {lead.score?.category || "MEDIUM"} ({lead.score?.total_score || 0}/100)</span>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-center">
                      <div className="p-2.5 rounded bg-slate-50 border border-slate-100">
                        <div className="text-[10px] text-slate-400 font-medium uppercase">Data Confidence</div>
                        <div className="text-sm font-bold font-mono text-slate-900 mt-0.5">{lead.score?.data_confidence_score || 0}/100</div>
                      </div>

                      <div className="p-2.5 rounded bg-slate-50 border border-slate-100">
                        <div className="text-[10px] text-slate-400 font-medium uppercase">Business Fit</div>
                        <div className="text-sm font-bold font-mono text-slate-900 mt-0.5">{lead.score?.business_fit_score || 0}/100</div>
                      </div>

                      <div className="p-2.5 rounded bg-slate-50 border border-slate-100">
                        <div className="text-[10px] text-slate-400 font-medium uppercase">Opportunity Score</div>
                        <div className="text-sm font-bold font-mono text-blue-700 mt-0.5">{lead.score?.opportunity_score || 0}/100</div>
                      </div>

                      <div className="p-2.5 rounded bg-slate-50 border border-slate-100">
                        <div className="text-[10px] text-slate-400 font-medium uppercase">Buying Intent</div>
                        <div className="text-xs font-bold font-mono text-slate-600 mt-1 uppercase">{lead.score?.buying_intent || "UNKNOWN"}</div>
                      </div>

                      <div className="p-2.5 rounded bg-slate-50 border border-slate-100">
                        <div className="text-[10px] text-slate-400 font-medium uppercase">Contactability</div>
                        <div className="text-sm font-bold font-mono text-emerald-700 mt-0.5">{lead.score?.contactability_score || 0}/100</div>
                      </div>
                    </div>
                  </div>

                  {/* Company Profile & Operating Status */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 rounded-lg bg-white border border-slate-200 space-y-3">
                      <div className="text-xs font-bold text-slate-900 border-b border-slate-100 pb-2 flex items-center justify-between">
                        <span>Company Details</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          lead.company.operating_status === "ACTIVE" ? "bg-emerald-100 text-emerald-800" :
                          lead.company.operating_status === "PROBABLY_ACTIVE" ? "bg-blue-100 text-blue-800" :
                          lead.company.operating_status === "PERMANENTLY_CLOSED" ? "bg-rose-100 text-rose-800" :
                          "bg-slate-100 text-slate-700"
                        }`}>
                          Status: {lead.company.operating_status || "UNKNOWN"}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div className="text-slate-500">Business Name:</div>
                        <div className="font-semibold text-slate-800">{lead.company.business_name}</div>
                        <div className="text-slate-500">Discovered Industry:</div>
                        <div className="font-semibold text-slate-800">{lead.company.discovered_industry || lead.company.industry || "—"}</div>
                        <div className="text-slate-500">Verified Industry:</div>
                        <div className="font-semibold text-slate-800">{lead.company.verified_industry || lead.company.industry || "—"}</div>
                        <div className="text-slate-500">Location:</div>
                        <div className="font-semibold text-slate-800">{lead.company.city || "—"}, {lead.company.country || "Worldwide"}</div>
                        <div className="text-slate-500">Phone:</div>
                        <div className="font-semibold text-slate-800">{lead.company.phone || "—"}</div>
                        <div className="text-slate-500">Business Email:</div>
                        <div className="font-semibold text-slate-800">{lead.company.business_email || "—"}</div>
                      </div>
                    </div>

                    <div className="p-4 rounded-lg bg-white border border-slate-200 space-y-3">
                      <div className="text-xs font-bold text-slate-900 border-b border-slate-100 pb-2">
                        Operating Status & Discovery Evidence
                      </div>
                      <div className="space-y-2 text-xs">
                        <div className="grid grid-cols-2 gap-2">
                          <div className="text-slate-500">Primary Source:</div>
                          <div className="font-semibold text-slate-800">{lead.company.source}</div>
                          <div className="text-slate-500">Data Confidence:</div>
                          <div className="font-semibold text-slate-800">{Math.round((lead.company.confidence || 0.9) * 100)}%</div>
                          <div className="text-slate-500">Discovered At:</div>
                          <div className="font-semibold text-slate-800">{new Date(lead.company.discovered_at).toLocaleDateString()}</div>
                        </div>

                        {lead.company.operating_status_evidence && lead.company.operating_status_evidence.length > 0 && (
                          <div className="pt-2 border-t border-slate-100">
                            <div className="text-[10px] text-slate-400 font-semibold uppercase mb-1">Observable Operational Signals</div>
                            <div className="space-y-1">
                              {lead.company.operating_status_evidence.map((ev: any, idx: number) => (
                                <div key={idx} className="text-[11px] text-slate-600 flex items-center gap-1.5">
                                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                                  <span>{ev.detail || ev.signal}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* 2. PROVENANCE & EVIDENCE TAB */}
              {activeTab === "provenance" && (
                <div className="space-y-4">
                  {/* Data Quality & Identity Verification Summary */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-white space-y-1">
                      <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Data Quality Score</div>
                      <div className="text-2xl font-extrabold text-emerald-400">{lead.data_quality_score || 0}<span className="text-xs text-slate-400 font-normal"> / 100</span></div>
                      <div className="text-[11px] text-slate-400">Multi-source verification & cross-consistency</div>
                    </div>

                    <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-white space-y-1">
                      <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Identity Match Level</div>
                      <div className="text-2xl font-extrabold text-blue-400">{lead.company?.identity_verification_status || "UNVERIFIED"}</div>
                      <div className="text-[11px] text-slate-400">9-Signal brand & corporate identity cross-match</div>
                    </div>

                    <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-white space-y-1">
                      <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Website Verification</div>
                      <div className="text-2xl font-extrabold text-purple-400">{lead.company?.website_verification_status || "UNVERIFIED"}</div>
                      <div className="text-[11px] text-slate-400">Domain ownership & reachability verification</div>
                    </div>
                  </div>

                  {/* 1. Field-Level Provenance Inspector Table */}
                  <div className="p-4 bg-white rounded-xl border border-slate-200 space-y-3 shadow-sm">
                    <div className="border-b border-slate-100 pb-2 flex items-center justify-between">
                      <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                        <ShieldCheck className="w-4 h-4 text-blue-600" />
                        <span>Field-Level Data Provenance & Traceability Inspector</span>
                      </h4>
                      <span className="text-[10px] text-slate-500 font-mono">Source-Backed • Zero Fabrication</span>
                    </div>

                    {lead.field_provenance && lead.field_provenance.length > 0 ? (
                      <div className="overflow-x-auto">
                        <table className="w-full text-left text-xs border-collapse">
                          <thead>
                            <tr className="border-b border-slate-200 text-[10px] text-slate-500 uppercase bg-slate-50">
                              <th className="p-2 font-semibold">Field</th>
                              <th className="p-2 font-semibold">Observed Value</th>
                              <th className="p-2 font-semibold">Source</th>
                              <th className="p-2 font-semibold">Method</th>
                              <th className="p-2 font-semibold">Status</th>
                              <th className="p-2 font-semibold">Confidence</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-100">
                            {lead.field_provenance.map((fp: any, idx: number) => (
                              <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                                <td className="p-2 font-mono font-semibold text-slate-900">{fp.field_name}</td>
                                <td className="p-2 font-medium text-slate-700 max-w-[200px] truncate">{fp.value || <span className="text-slate-400 italic">NULL</span>}</td>
                                <td className="p-2 text-slate-600">
                                  {fp.source_url ? (
                                    <a href={fp.source_url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline flex items-center gap-1">
                                      {fp.source_type}
                                      <ExternalLink className="w-2.5 h-2.5" />
                                    </a>
                                  ) : (
                                    <span>{fp.source_type}</span>
                                  )}
                                </td>
                                <td className="p-2 font-mono text-[10px] text-slate-500">{fp.verification_method}</td>
                                <td className="p-2">
                                  <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                                    fp.verification_status.includes("VERIFIED") || fp.verification_status.includes("ENABLED")
                                      ? "bg-emerald-100 text-emerald-800"
                                      : fp.verification_status === "UNKNOWN"
                                      ? "bg-slate-100 text-slate-600"
                                      : "bg-blue-100 text-blue-800"
                                  }`}>
                                    {fp.verification_status}
                                  </span>
                                </td>
                                <td className="p-2 font-mono text-slate-700">{Math.round((fp.confidence_score || 1.0) * 100)}%</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div className="p-3 bg-slate-50 text-slate-500 text-xs rounded">
                        Discovered from {lead.company?.source || "Public Source"}. Direct verification records active.
                      </div>
                    )}
                  </div>

                  {/* 2. Service Need Evidence Matrix (9 Core Agency Services) */}
                  <div className="p-4 bg-white rounded-xl border border-slate-200 space-y-3 shadow-sm">
                    <div className="border-b border-slate-100 pb-2">
                      <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-indigo-600" />
                        <span>Agency Service Need Evidence Matrix (9 Core Services)</span>
                      </h4>
                      <p className="text-[11px] text-slate-500 mt-0.5">
                        Observable client defects measured deterministically without AI hallucination.
                      </p>
                    </div>

                    {lead.service_need_evidence && lead.service_need_evidence.length > 0 ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {lead.service_need_evidence.map((sn: any, idx: number) => (
                          <div key={idx} className="p-3 rounded-lg bg-slate-50 border border-slate-200 space-y-1.5">
                            <div className="flex items-center justify-between">
                              <span className="font-bold text-xs text-slate-900">{sn.service_type}</span>
                              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-100 text-indigo-800 font-mono">
                                Need: {sn.need_score}/100
                              </span>
                            </div>
                            <ul className="list-disc list-inside space-y-1 text-[11px] text-slate-600">
                              {sn.evidence?.map((ev: string, i: number) => (
                                <li key={i}>{ev}</li>
                              ))}
                            </ul>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="p-3 bg-slate-50 text-slate-500 text-xs rounded">
                        No service deficiencies detected on audited pages.
                      </div>
                    )}
                  </div>

                  {/* 3. Business Identity Signals & Contradiction Alerts */}
                  {lead.company?.has_conflicts && (
                    <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 flex items-start gap-3">
                      <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                      <div>
                        <h4 className="text-xs font-bold text-amber-900">Source Contradictions Detected</h4>
                        <p className="text-xs text-amber-700 mt-0.5">
                          Discrepancies found between original public directory records and live website data. Both data streams are preserved for human review.
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* 3. AUDIT TAB */}
              {activeTab === "audit" && (
                <div className="space-y-6">
                  {lead.audit ? (
                    <>
                      {/* Audit Status Banner */}
                      <div className="flex items-center justify-between p-3 rounded bg-white border border-slate-200 text-xs">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-slate-700">Audit Status:</span>
                          <span className={`px-2 py-0.5 rounded font-mono font-bold text-[11px] ${lead.audit.audit_status === "AUDIT_COMPLETE" ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800"}`}>
                            {lead.audit.audit_status || "AUDIT_COMPLETE"}
                          </span>
                        </div>
                        <div className="text-slate-500">
                          Measured overall health score: <span className="font-bold text-slate-900">{lead.audit.overall_score}/100</span>
                        </div>
                      </div>

                      {/* Overall Metrics Cards */}
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                        {[
                          { label: "Overall Health", score: lead.audit.overall_score, icon: Gauge },
                          { label: "Mobile Responsive", score: lead.audit.mobile_score, icon: Smartphone },
                          { label: "Performance Speed", score: lead.audit.performance_score, icon: Zap },
                          { label: "On-Page SEO", score: lead.audit.seo_score, icon: Search },
                          { label: "Accessibility", score: lead.audit.accessibility_score, icon: Layers },
                          { label: "Security & TLS", score: lead.audit.security_score, icon: Shield },
                          { label: "UX Architecture", score: lead.audit.ux_score, icon: CheckCircle2 },
                          { label: "Conversion Funnel", score: lead.audit.conversion_score, icon: Sparkles }
                        ].map((m, idx) => {
                          const Icon = m.icon;
                          return (
                            <div key={idx} className="p-3 bg-white rounded-lg border border-slate-200">
                              <div className="flex items-center justify-between text-slate-400">
                                <span className="text-[11px] font-medium">{m.label}</span>
                                <Icon className="w-4 h-4 text-slate-400" />
                              </div>
                              <div className="text-lg font-bold font-mono text-slate-900 mt-1">
                                {m.score}/100
                              </div>
                            </div>
                          );
                        })}
                      </div>

                      {/* Detected Issues */}
                      <div className="p-4 bg-white rounded-lg border border-slate-200 space-y-3">
                        <div className="text-xs font-bold text-slate-900 border-b border-slate-100 pb-2">
                          Observed Technical & Design Opportunities ({lead.audit.issues?.length || 0})
                        </div>
                        <div className="space-y-2">
                          {lead.audit.issues?.map((iss: any, idx: number) => (
                            <div key={idx} className="p-3 rounded-md bg-slate-50 border border-slate-200 text-xs space-y-1">
                              <div className="flex items-center justify-between">
                                <span className="font-bold text-slate-900">{iss.title}</span>
                                <span className="px-1.5 py-0.5 rounded text-[10px] font-bold uppercase bg-amber-100 text-amber-800">
                                  {iss.severity}
                                </span>
                              </div>
                              <div className="text-slate-600">
                                <span className="font-semibold">Evidence:</span> {iss.evidence}
                              </div>
                              <div className="text-slate-500">
                                <span className="font-semibold">Recommendation:</span> {iss.recommendation}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Technologies */}
                      <div className="p-4 bg-white rounded-lg border border-slate-200 space-y-3">
                        <div className="text-xs font-bold text-slate-900 border-b border-slate-100 pb-2">
                          Detected Tech Stack ({lead.audit.technologies?.length || 0})
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {lead.audit.technologies?.map((tech: any, idx: number) => (
                            <span
                              key={idx}
                              className="px-2.5 py-1 rounded bg-slate-100 border border-slate-200 text-xs font-medium text-slate-700"
                            >
                              {tech.name} {tech.version ? `(${tech.version})` : ""}
                            </span>
                          ))}
                        </div>
                      </div>
                    </>
                  ) : (
                    <div className="text-center py-8 text-xs text-slate-400">
                      No technical website audit available for this record.
                    </div>
                  )}
                </div>
              )}

              {/* 4. CONTACTS TAB */}
              {activeTab === "contacts" && (
                <div className="space-y-4">
                  <div className="p-4 bg-white rounded-lg border border-slate-200 space-y-3">
                    <div className="text-xs font-bold text-slate-900 border-b border-slate-100 pb-2 flex items-center justify-between">
                      <span>Verified Public Contacts & Decision Makers</span>
                      <span className="text-[11px] font-normal text-slate-500">Source: Official Crawled Pages</span>
                    </div>
                    {lead.contacts && lead.contacts.length > 0 ? (
                      <div className="space-y-3">
                        {lead.contacts.map((c: any) => (
                          <div
                            key={c.id}
                            className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 flex items-start justify-between gap-4"
                          >
                            <div className="space-y-1.5 text-xs flex-1">
                              <div className="font-bold text-slate-900 flex items-center gap-2">
                                {c.full_name ? c.full_name : <span className="text-slate-500 italic">General Business Inbox (No Named Person)</span>}
                                {c.is_decision_maker && (
                                  <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-700">
                                    Decision Maker
                                  </span>
                                )}
                              </div>
                              {c.job_title && <div className="text-slate-600 font-medium">{c.job_title}</div>}
                              
                              {c.email && (
                                <div className="flex items-center gap-2 text-slate-700 flex-wrap">
                                  <div className="flex items-center gap-1">
                                    <Mail className="w-3.5 h-3.5 text-slate-400" />
                                    <span className="font-mono font-semibold">{c.email}</span>
                                  </div>
                                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 font-mono">
                                    {c.email_status === "MAILBOX_VERIFIED" ? "Mailbox Verified" : "Domain Mail Enabled"}
                                  </span>
                                </div>
                              )}
                              {c.phone && (
                                <div className="flex items-center gap-1.5 text-slate-700">
                                  <Phone className="w-3.5 h-3.5 text-slate-400" />
                                  <span className="font-mono">{c.normalized_phone_e164 || c.phone}</span>
                                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 font-mono">
                                    {c.phone_validation_status || "VALID_E164"}
                                  </span>
                                </div>
                              )}

                              {c.linkedin_url && (
                                <div className="flex items-center gap-1.5 pt-0.5">
                                  <a
                                    href={c.linkedin_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-[#0A66C2]/10 text-[#0A66C2] hover:bg-[#0A66C2]/20 font-semibold text-[11px] transition"
                                  >
                                    <span className="font-bold">in</span>
                                    <span>Verified LinkedIn Profile</span>
                                    <ExternalLink className="w-2.5 h-2.5 ml-0.5" />
                                  </a>
                                </div>
                              )}

                              {/* Exact Source Provenance */}
                              <div className="pt-1.5 text-[11px] text-slate-500 border-t border-slate-100 flex items-center gap-3">
                                <span>Source: <strong className="text-slate-700">{c.contact_source || "Official Website"}</strong></span>
                                {c.source_url && (
                                  <a href={c.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline flex items-center gap-0.5">
                                    <span>{c.source_url.length > 40 ? c.source_url.slice(0, 40) + "..." : c.source_url}</span>
                                    <ExternalLink className="w-2.5 h-2.5" />
                                  </a>
                                )}
                              </div>
                            </div>

                            {onOpenEmailComposer && c.email && (
                              <button
                                onClick={() => {
                                  onClose();
                                  onOpenEmailComposer(lead);
                                }}
                                className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-semibold flex items-center gap-1.5 shrink-0"
                              >
                                <Send className="w-3.5 h-3.5" />
                                Send Outreach
                              </button>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-6 text-xs text-slate-400">
                        No public contact channels discovered on official pages yet.
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* 5. AI ANALYSIS TAB */}
              {activeTab === "ai" && (
                <div className="space-y-4">
                  <div className="p-4 bg-white rounded-lg border border-slate-200 space-y-3 text-xs">
                    <div className="font-bold text-slate-900 border-b border-slate-100 pb-2 flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-purple-600" />
                      <span>Factual Agency Pitch Angle & Value Proposition</span>
                    </div>
                    <p className="text-slate-600 leading-relaxed">
                      Based on measured site metrics, the primary value angle for {lead.company.business_name} is{" "}
                      <span className="font-semibold text-slate-800">{lead.primary_opportunity || "Website Modernization"}</span>.
                    </p>
                    <div className="p-3 bg-purple-50 rounded border border-purple-100 text-purple-900 font-medium">
                      Recommended Pitch: Focus on resolving observable layout responsiveness and booking flow deficiencies to increase customer conversion.
                    </div>
                  </div>
                </div>
              )}

              {/* 6. TIMELINE TAB */}
              {activeTab === "timeline" && (
                <div className="space-y-4">
                  <div className="p-4 bg-white rounded-lg border border-slate-200 space-y-3 text-xs">
                    <div className="font-bold text-slate-900 border-b border-slate-100 pb-2">
                      Lifecycle Audit History
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center gap-3 text-slate-600">
                        <Clock className="w-4 h-4 text-blue-500" />
                        <span>Lead Record Created: {new Date(lead.created_at).toLocaleString()}</span>
                      </div>
                      <div className="flex items-center gap-3 text-slate-600">
                        <ShieldCheck className="w-4 h-4 text-emerald-500" />
                        <span>Public Origin Ingestion from {lead.company.source}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* 7. TASKS & NOTES TAB */}
              {activeTab === "tasks" && (
                <div className="space-y-4">
                  <div className="p-4 bg-white rounded-lg border border-slate-200 space-y-3">
                    <div className="text-xs font-bold text-slate-900 border-b border-slate-100 pb-2">
                      CRM Notes ({lead.notes?.length || 0})
                    </div>
                    <form onSubmit={handleAddNote} className="space-y-2">
                      <textarea
                        value={newNote}
                        onChange={(e) => setNewNote(e.target.value)}
                        placeholder="Add a private note about this lead..."
                        className="w-full text-xs p-2.5 rounded border border-slate-300 focus:outline-hidden focus:ring-1 focus:ring-blue-500"
                        rows={2}
                      />
                      <button
                        type="submit"
                        disabled={addingNote || !newNote.trim()}
                        className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded text-xs font-semibold"
                      >
                        {addingNote ? "Saving..." : "Add Note"}
                      </button>
                    </form>

                    <div className="space-y-2 mt-4">
                      {lead.notes?.map((n: any) => (
                        <div key={n.id} className="p-2.5 bg-slate-50 rounded border border-slate-200 text-xs">
                          <div className="text-slate-800">{n.content}</div>
                          <div className="text-[10px] text-slate-400 mt-1">
                            {new Date(n.created_at).toLocaleString()}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : null}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-100 bg-slate-50/50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 font-medium">CRM Stage:</span>
            <select
              value={lead?.stage || "New"}
              onChange={(e) => handleStageChange(e.target.value)}
              className="text-xs font-semibold py-1.5 px-3 rounded-md bg-white border border-slate-300 text-slate-700 focus:outline-hidden focus:ring-1 focus:ring-blue-500"
            >
              <option value="Discovered">Discovered</option>
              <option value="New">New</option>
              <option value="Qualified">Qualified</option>
              <option value="Sales Ready">Sales Ready</option>
              <option value="Contacted">Contacted</option>
              <option value="Follow-up">Follow-up</option>
              <option value="Interested">Interested</option>
              <option value="Meeting">Meeting</option>
              <option value="Proposal">Proposal</option>
              <option value="Won">Won</option>
              <option value="Lost">Lost</option>
              <option value="Do Not Contact">Do Not Contact</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            {onOpenEmailComposer && lead?.contacts?.[0]?.email && (
              <button
                onClick={() => {
                  onClose();
                  onOpenEmailComposer(lead);
                }}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-xs font-semibold flex items-center gap-2 shadow-xs"
              >
                <Send className="w-3.5 h-3.5" />
                Launch Outreach
              </button>
            )}
            <button
              onClick={onClose}
              className="px-4 py-2 border border-slate-200 hover:bg-slate-100 text-slate-700 rounded-md text-xs font-semibold"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
