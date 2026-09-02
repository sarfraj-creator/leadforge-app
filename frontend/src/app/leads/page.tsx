"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Search,
  Filter,
  Plus,
  Flame,
  Globe,
  ExternalLink,
  Mail,
  RefreshCw,
  Send,
  MoreVertical,
  CheckCircle2,
  AlertCircle,
  Clock,
  Layers,
  ChevronLeft,
  ChevronRight,
  Download,
  ShieldCheck,
  Zap,
  CheckCheck,
  FileText,
  Sparkles,
  Rocket,
  Compass,
  X
} from "lucide-react";
import { Lead } from "@/types";
import { LeadScoreBadge } from "@/components/LeadScoreBadge";
import { FreshnessBadge } from "@/components/FreshnessBadge";
import { LeadDetailModal } from "@/components/LeadDetailModal";
import { EmailComposerModal } from "@/components/EmailComposerModal";
import { TechnicalAuditReportModal } from "@/components/TechnicalAuditReportModal";
import { apiFetch } from "@/lib/api";

export default function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  
  // Category Segment State
  const [leadCategory, setLeadCategory] = useState<string>("");

  // Filter States
  const [search, setSearch] = useState("");
  const [pipelineStage, setPipelineStage] = useState("");
  const [stage, setStage] = useState("");
  const [minScore, setMinScore] = useState<number | "">("");
  const [freshness, setFreshness] = useState("");
  const [needsReviewOnly, setNeedsReviewOnly] = useState(false);
  const [hasEmailOnly, setHasEmailOnly] = useState(false);
  const [salesReadyOnly, setSalesReadyOnly] = useState(false);
  
  // Pagination
  const [page, setPage] = useState(1);
  const limit = 25;

  // Selected for Bulk Action
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [bulkActionLoading, setBulkActionLoading] = useState(false);

  // Autonomous Campaign Launcher state
  const [launchingAuto, setLaunchingAuto] = useState(false);
  const [autoLaunchMessage, setAutoLaunchMessage] = useState<string | null>(null);

  // Modal States
  const [selectedLeadId, setSelectedLeadId] = useState<number | null>(null);
  const [composerLead, setComposerLead] = useState<Lead | null>(null);
  const [reportModalLeadId, setReportModalLeadId] = useState<number | null>(null);

  const fetchLeads = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.append("search", search);
      if (leadCategory) params.append("lead_category", leadCategory);
      if (pipelineStage) params.append("pipeline_stage", pipelineStage);
      if (stage) params.append("stage", stage);
      if (minScore) params.append("min_score", minScore.toString());
      if (freshness) params.append("freshness", freshness);
      if (needsReviewOnly) params.append("needs_review", "true");
      if (hasEmailOnly) params.append("has_email", "true");
      if (salesReadyOnly) params.append("is_sales_ready", "true");
      params.append("limit", limit.toString());
      params.append("offset", ((page - 1) * limit).toString());

      const res = await apiFetch<{ total: number; leads: Lead[] }>(`/leads?${params.toString()}`);
      setLeads(res.leads);
      setTotal(res.total);
    } catch (err) {
      console.error("Failed to load leads", err);
    } finally {
      setLoading(false);
    }
  }, [search, leadCategory, pipelineStage, stage, minScore, freshness, needsReviewOnly, hasEmailOnly, salesReadyOnly, page]);

  useEffect(() => {
    fetchLeads();
    const interval = setInterval(() => {
      fetchLeads();
    }, 5000);
    return () => clearInterval(interval);
  }, [fetchLeads]);

  const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) {
      setSelectedIds(leads.map((l) => l.id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleToggleSelect = (id: number) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const handleBulkAction = async (action: string) => {
    if (selectedIds.length === 0) return;
    setBulkActionLoading(true);
    try {
      await apiFetch("/leads/bulk-action", {
        method: "POST",
        body: JSON.stringify({
          lead_ids: selectedIds,
          action: action
        })
      });
      setSelectedIds([]);
      fetchLeads();
    } catch (err) {
      console.error(err);
    } finally {
      setBulkActionLoading(false);
    }
  };

  const handleLaunchAutonomousCampaign = async () => {
    setLaunchingAuto(true);
    setAutoLaunchMessage(null);
    try {
      const res = await apiFetch<{ status: string; enrolled: number; dispatched: number; message: string }>("/campaigns/auto-launch", {
        method: "POST",
        body: JSON.stringify({
          category: leadCategory || "HAS_WEBSITE_REDESIGN",
          auto_dispatch_initial: true
        })
      });
      setAutoLaunchMessage(res.message);
      fetchLeads();
      setTimeout(() => setAutoLaunchMessage(null), 8000);
    } catch (err: any) {
      setAutoLaunchMessage(`Error: ${err.message || "Failed to launch autonomous campaign"}`);
    } finally {
      setLaunchingAuto(false);
    }
  };

  const totalPages = Math.ceil(total / limit) || 1;

  const getStageBadge = (stg: string) => {
    switch (stg) {
      case "SALES_READY":
        return "bg-emerald-50 text-emerald-800 border-emerald-300 font-bold";
      case "QUALIFIED":
        return "bg-blue-50 text-blue-700 border-blue-200 font-semibold";
      case "CONTACTABLE":
        return "bg-indigo-50 text-indigo-700 border-indigo-200";
      case "OPPORTUNITY":
        return "bg-purple-50 text-purple-700 border-purple-200";
      case "AUDITED":
        return "bg-cyan-50 text-cyan-700 border-cyan-200";
      case "VERIFIED":
        return "bg-teal-50 text-teal-700 border-teal-200";
      case "IDENTITY_VERIFIED":
        return "bg-amber-50 text-amber-700 border-amber-200";
      default:
        return "bg-slate-50 text-slate-600 border-slate-200";
    }
  };

  const getCategoryBadge = (cat?: string) => {
    switch (cat) {
      case "HAS_WEBSITE_REDESIGN":
        return {
          label: "Website Redesign & Audit",
          className: "bg-blue-50 text-blue-700 border-blue-200"
        };
      case "NO_WEBSITE_NEW_BUILD":
        return {
          label: "New Website Build",
          className: "bg-amber-50 text-amber-800 border-amber-200"
        };
      case "BUYER_INTENT_POST":
        return {
          label: "Social / RFQ Buyer Intent",
          className: "bg-rose-50 text-rose-700 border-rose-200"
        };
      default:
        return {
          label: "Web Lead",
          className: "bg-slate-50 text-slate-600 border-slate-200"
        };
    }
  };

  return (
    <div className="space-y-5 max-w-7xl mx-auto">
      {/* Page Header with Action Button */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <span>Verified Lead Intelligence</span>
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
              {total} Total
            </span>
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Deterministic technical audits, multi-source buyer intent, and autonomous 3/7/14-day follow-up sequences.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleLaunchAutonomousCampaign}
            disabled={launchingAuto}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-lg text-xs font-bold shadow-xs disabled:opacity-50 transition"
          >
            <Sparkles className={`w-4 h-4 ${launchingAuto ? "animate-spin" : ""}`} />
            <span>{launchingAuto ? "Launching Autonomous Engine..." : "Launch AI 4-Step Sequence"}</span>
          </button>
        </div>
      </div>

      {/* Auto Launch Notification Banner */}
      {autoLaunchMessage && (
        <div className="p-3 rounded-lg bg-blue-50 border border-blue-200 text-xs text-blue-900 flex items-center justify-between shadow-2xs">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />
            <span className="font-semibold">{autoLaunchMessage}</span>
          </div>
          <button onClick={() => setAutoLaunchMessage(null)} className="text-slate-400 hover:text-slate-600">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Lead Category Segregation Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-3 overflow-x-auto">
        <button
          onClick={() => {
            setLeadCategory("");
            setPage(1);
          }}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
            leadCategory === ""
              ? "bg-slate-900 text-white shadow-xs"
              : "bg-slate-100 text-slate-600 hover:bg-slate-200"
          }`}
        >
          <Globe className="w-3.5 h-3.5" />
          <span>All Leads ({total})</span>
        </button>

        <button
          onClick={() => {
            setLeadCategory("HAS_WEBSITE_REDESIGN");
            setPage(1);
          }}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
            leadCategory === "HAS_WEBSITE_REDESIGN"
              ? "bg-blue-600 text-white shadow-xs"
              : "bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200"
          }`}
        >
          <Zap className="w-3.5 h-3.5" />
          <span>Website Redesign & Audits</span>
        </button>

        <button
          onClick={() => {
            setLeadCategory("NO_WEBSITE_NEW_BUILD");
            setPage(1);
          }}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
            leadCategory === "NO_WEBSITE_NEW_BUILD"
              ? "bg-amber-600 text-white shadow-xs"
              : "bg-amber-50 text-amber-800 hover:bg-amber-100 border border-amber-200"
          }`}
        >
          <Rocket className="w-3.5 h-3.5" />
          <span>New Website Builds (Zero Site)</span>
        </button>

        <button
          onClick={() => {
            setLeadCategory("BUYER_INTENT_POST");
            setPage(1);
          }}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
            leadCategory === "BUYER_INTENT_POST"
              ? "bg-rose-600 text-white shadow-xs"
              : "bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200"
          }`}
        >
          <Flame className="w-3.5 h-3.5" />
          <span>Social / RFQ Buyer Intent</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="p-4 bg-white rounded-lg border border-slate-200 shadow-2xs space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search company, domain, city, industry..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-xs border border-slate-300 rounded-md focus:outline-hidden focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div>
            <select
              value={pipelineStage}
              onChange={(e) => setPipelineStage(e.target.value)}
              className="w-full py-2 px-3 text-xs border border-slate-300 rounded-md focus:outline-hidden focus:ring-1 focus:ring-blue-500 text-slate-700 font-medium"
            >
              <option value="">All Pipeline Stages</option>
              <option value="SALES_READY">★ SALES_READY (Qualified + Contactable)</option>
              <option value="QUALIFIED">✔ QUALIFIED (Verified + Opp &ge; 60)</option>
              <option value="CONTACTABLE">CONTACTABLE (Email/Phone Verified)</option>
              <option value="OPPORTUNITY">OPPORTUNITY (Deficiencies Detected)</option>
              <option value="AUDITED">AUDITED (Audit Complete)</option>
              <option value="VERIFIED">VERIFIED (Website Matched)</option>
              <option value="DISCOVERED">DISCOVERED (Raw Source Record)</option>
            </select>
          </div>

          <div>
            <select
              value={minScore}
              onChange={(e) => setMinScore(e.target.value ? Number(e.target.value) : "")}
              className="w-full py-2 px-3 text-xs border border-slate-300 rounded-md focus:outline-hidden focus:ring-1 focus:ring-blue-500 text-slate-700 font-medium"
            >
              <option value="">Any Lead Score</option>
              <option value="80">HOT (80+)</option>
              <option value="65">HIGH (65+)</option>
              <option value="50">MEDIUM (50+)</option>
            </select>
          </div>

          <div>
            <select
              value={freshness}
              onChange={(e) => setFreshness(e.target.value)}
              className="w-full py-2 px-3 text-xs border border-slate-300 rounded-md focus:outline-hidden focus:ring-1 focus:ring-blue-500 text-slate-700 font-medium"
            >
              <option value="">Any Freshness</option>
              <option value="FRESH">Fresh (&lt; 7 Days)</option>
              <option value="RECENT">Recent (&lt; 30 Days)</option>
              <option value="STALE">Stale (&gt; 30 Days)</option>
            </select>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-4 pt-3 border-t border-slate-100 text-xs text-slate-600">
          <div className="flex items-center gap-4 flex-wrap">
            <label className="flex items-center gap-1.5 cursor-pointer font-medium">
              <input
                type="checkbox"
                checked={salesReadyOnly}
                onChange={(e) => setSalesReadyOnly(e.target.checked)}
                className="rounded text-blue-600 focus:ring-blue-500"
              />
              <span>Sales-Ready Only</span>
            </label>
            <label className="flex items-center gap-1.5 cursor-pointer font-medium">
              <input
                type="checkbox"
                checked={hasEmailOnly}
                onChange={(e) => setHasEmailOnly(e.target.checked)}
                className="rounded text-blue-600 focus:ring-blue-500"
              />
              <span>Has Verified Contact</span>
            </label>
            <label className="flex items-center gap-1.5 cursor-pointer font-medium">
              <input
                type="checkbox"
                checked={needsReviewOnly}
                onChange={(e) => setNeedsReviewOnly(e.target.checked)}
                className="rounded text-blue-600 focus:ring-blue-500"
              />
              <span>Needs Review</span>
            </label>
          </div>

          {selectedIds.length > 0 && (
            <div className="flex items-center gap-2">
              <span className="font-semibold text-blue-700 font-mono">
                {selectedIds.length} Selected
              </span>
              <button
                onClick={() => handleBulkAction("approve")}
                disabled={bulkActionLoading}
                className="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded text-xs font-semibold"
              >
                Approve
              </button>
              <button
                onClick={() => handleBulkAction("mark_dnc")}
                disabled={bulkActionLoading}
                className="px-2.5 py-1 bg-rose-600 hover:bg-rose-700 text-white rounded text-xs font-semibold"
              >
                Do Not Contact
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Leads Table */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-2xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600 border-collapse">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-700 font-bold uppercase tracking-wider text-[11px]">
              <tr>
                <th className="p-3.5 w-10 text-center">
                  <input
                    type="checkbox"
                    checked={leads.length > 0 && selectedIds.length === leads.length}
                    onChange={handleSelectAll}
                    className="rounded text-blue-600 focus:ring-blue-500"
                  />
                </th>
                <th className="p-3.5">Company & Provenance</th>
                <th className="p-3.5">Category Segment</th>
                <th className="p-3.5">Pipeline Stage</th>
                <th className="p-3.5">Website Verification</th>
                <th className="p-3.5">Observable Opportunity</th>
                <th className="p-3.5">Scores Breakdown</th>
                <th className="p-3.5">Decision Maker</th>
                <th className="p-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading && leads.length === 0 ? (
                <tr>
                  <td colSpan={9} className="text-center py-12 text-slate-400">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto text-blue-600 mb-2" />
                    Loading verified lead records...
                  </td>
                </tr>
              ) : leads.length === 0 ? (
                <tr>
                  <td colSpan={9} className="text-center py-12 text-slate-400">
                    No lead records matched the specified quality filters.
                  </td>
                </tr>
              ) : (
                leads.map((l) => {
                  const isSelected = selectedIds.includes(l.id);
                  const isSalesReady = l.pipeline_stage === "SALES_READY" || l.is_sales_ready;
                  const catBadge = getCategoryBadge(l.lead_category);

                  return (
                    <tr
                      key={l.id}
                      onClick={() => setSelectedLeadId(l.id)}
                      className={`hover:bg-blue-50/40 transition-colors cursor-pointer ${
                        isSelected ? "bg-blue-50/60" : ""
                      }`}
                    >
                      <td className="p-3.5 text-center" onClick={(e) => e.stopPropagation()}>
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => handleToggleSelect(l.id)}
                          className="rounded text-blue-600 focus:ring-blue-500"
                        />
                      </td>

                      {/* Company Name & Provenance */}
                      <td className="p-3.5">
                        <div className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
                          <span>{l.company.business_name}</span>
                          {isSalesReady && (
                            <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-emerald-100 text-emerald-800 font-mono">
                              READY
                            </span>
                          )}
                        </div>
                        <div className="text-[11px] text-slate-500 flex items-center gap-2 mt-0.5">
                          <span>{l.company.city || "—"}, {l.company.country || "Worldwide"}</span>
                          <span>•</span>
                          <span className="font-semibold text-slate-600">{l.company.source}</span>
                        </div>
                      </td>

                      {/* Category Segment */}
                      <td className="p-3.5">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${catBadge.className}`}>
                          {catBadge.label}
                        </span>
                      </td>

                      {/* Pipeline Stage */}
                      <td className="p-3.5">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border uppercase tracking-wider ${getStageBadge(l.pipeline_stage || "DISCOVERED")}`}>
                          {l.pipeline_stage || "DISCOVERED"}
                        </span>
                      </td>

                      {/* Website Reachability */}
                      <td className="p-3.5">
                        {l.company.website ? (
                          <div className="space-y-1">
                            <a
                              href={l.company.website.startsWith("http") ? l.company.website : `https://${l.company.website}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              onClick={(e) => e.stopPropagation()}
                              className="font-mono text-blue-600 hover:underline flex items-center gap-1 truncate max-w-[180px]"
                            >
                              <Globe className="w-3 h-3 text-slate-400 shrink-0" />
                              <span className="truncate">{l.company.domain || l.company.website}</span>
                              <ExternalLink className="w-2.5 h-2.5 shrink-0" />
                            </a>
                            <div className="flex items-center gap-1 text-[10px]">
                              <span className={`px-1.5 py-0.2 rounded font-semibold ${l.company.website_reachable ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"}`}>
                                {l.company.website_reachable ? "Reachable" : "Unreachable"}
                              </span>
                              {l.company.website_official_verified && (
                                <span className="px-1.5 py-0.2 rounded bg-blue-50 text-blue-700 font-semibold" title="Brand Matched on Page">
                                  Matched
                                </span>
                              )}
                            </div>
                          </div>
                        ) : (
                          <span className="text-[11px] font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                            Zero Website Found
                          </span>
                        )}
                      </td>

                      {/* Observable Opportunity */}
                      <td className="p-3.5">
                        <div className="font-semibold text-slate-800 text-xs truncate max-w-[200px]">
                          {l.primary_opportunity || "General Modernization"}
                        </div>
                        <div className="text-[11px] text-slate-500 mt-0.5 truncate max-w-[200px]">
                          Rec: {l.recommended_service || "Responsive Redesign"}
                        </div>
                      </td>

                      {/* Scores Breakdown */}
                      <td className="p-3.5">
                        {l.score ? (
                          <div className="space-y-1">
                            <LeadScoreBadge score={l.score.total_score} category={l.score.category} />
                            <div className="flex items-center gap-1 text-[10px] text-slate-500 font-mono">
                              <span>Fit: {l.score.business_fit_score || 0}</span>
                              <span>•</span>
                              <span>Opp: {l.score.opportunity_score || 0}</span>
                            </div>
                          </div>
                        ) : (
                          <span className="text-slate-400 text-[11px]">Uncalculated</span>
                        )}
                      </td>

                      {/* Decision Maker Contact */}
                      <td className="p-3.5">
                        {l.contacts && l.contacts.length > 0 ? (
                          <div className="space-y-0.5">
                            <div className="font-semibold text-slate-800 flex items-center gap-1">
                              <span>{l.contacts[0].full_name}</span>
                              {l.contacts[0].is_decision_maker && (
                                <span className="text-[9px] bg-slate-100 text-slate-600 px-1 rounded">DM</span>
                              )}
                            </div>
                            <div className="text-[11px] text-blue-600 font-mono truncate max-w-[150px]">
                              {l.contacts[0].email || l.contacts[0].phone || "—"}
                            </div>
                          </div>
                        ) : l.company.business_email || l.company.phone ? (
                          <div className="text-[11px] text-slate-700 font-mono">
                            <div>{l.company.business_email || "—"}</div>
                            <div className="text-[10px] text-slate-400">{l.company.phone || ""}</div>
                          </div>
                        ) : (
                          <span className="text-slate-400 text-[11px]">Pending Public Contact</span>
                        )}
                      </td>

                      {/* Actions */}
                      <td className="p-3.5 text-right" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-end gap-1.5">
                          <button
                            onClick={() => setReportModalLeadId(l.id)}
                            className="px-2 py-1 bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-700 rounded text-xs font-semibold shadow-2xs inline-flex items-center gap-1"
                            title="Inspect Technical R&D Audit Report"
                          >
                            <FileText className="w-3 h-3 text-slate-600" />
                            <span>Report</span>
                          </button>

                          <button
                            onClick={() => {
                              if (l.contacts?.[0]?.email || l.company.business_email) {
                                setComposerLead(l);
                              } else {
                                setSelectedLeadId(l.id);
                              }
                            }}
                            className="px-2.5 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-semibold shadow-2xs inline-flex items-center gap-1"
                          >
                            <Send className="w-3 h-3" />
                            <span>Outreach</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="p-3.5 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs text-slate-600">
          <div>
            Showing <span className="font-bold text-slate-900">{leads.length}</span> of{" "}
            <span className="font-bold text-slate-900">{total}</span> records (Page {page} of {totalPages})
          </div>

          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="p-1.5 bg-white border border-slate-200 rounded disabled:opacity-40 hover:bg-slate-100"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="px-2 font-mono font-bold text-slate-800">{page}</span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="p-1.5 bg-white border border-slate-200 rounded disabled:opacity-40 hover:bg-slate-100"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Technical R&D Report Modal */}
      {reportModalLeadId && (
        <TechnicalAuditReportModal
          leadId={reportModalLeadId}
          onClose={() => setReportModalLeadId(null)}
          onOpenComposer={(leadId) => {
            const l = leads.find((item) => item.id === leadId);
            if (l) setComposerLead(l);
          }}
        />
      )}

      {/* Lead Detail Modal */}
      {selectedLeadId && (
        <LeadDetailModal
          leadId={selectedLeadId}
          onClose={() => setSelectedLeadId(null)}
          onOpenEmailComposer={(lead) => setComposerLead(lead)}
          onRefreshList={fetchLeads}
        />
      )}

      {/* Email Composer Modal */}
      {composerLead && (
        <EmailComposerModal
          lead={composerLead}
          onClose={() => setComposerLead(null)}
          onSent={() => {
            setComposerLead(null);
            fetchLeads();
          }}
        />
      )}
    </div>
  );
}
