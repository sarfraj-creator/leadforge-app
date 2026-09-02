"use client";

import React, { useState, useEffect, useCallback } from "react";
import { 
  ShieldCheck, 
  CheckCircle2, 
  XCircle, 
  RefreshCw, 
  AlertTriangle, 
  ExternalLink, 
  Eye, 
  Building2, 
  Mail, 
  Phone, 
  Sparkles,
  Ban,
  RotateCcw,
  MessageSquare
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { LeadDetailModal } from "@/components/LeadDetailModal";

interface LeadItem {
  id: number;
  pipeline_stage: string;
  is_qualified: boolean;
  is_sales_ready: boolean;
  review_status: string;
  data_quality_score: number;
  data_quality_breakdown?: any;
  company: {
    id: number;
    business_name: string;
    industry?: string;
    discovered_industry?: string;
    verified_industry?: string;
    operating_status?: string;
    website?: string;
    phone?: string;
    normalized_phone_e164?: string;
    phone_validation_status?: string;
    city?: string;
    country?: string;
    source: string;
    identity_verification_status: string;
    website_verification_status?: string;
    has_conflicts: boolean;
  };
  score?: {
    total_score: number;
    category: string;
    opportunity_score: number;
    business_fit_score: number;
    buying_intent: string;
  };
  primary_opportunity?: string;
  recommended_service?: string;
  freshness_state: string;
  review_notes?: string;
  contacts: Array<{
    id: number;
    full_name?: string;
    job_title?: string;
    email?: string;
    phone?: string;
    email_status?: string;
    contact_source?: string;
    source_url?: string;
  }>;
}

export default function ReviewQueuePage() {
  const [leads, setLeads] = useState<LeadItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLeadId, setSelectedLeadId] = useState<number | null>(null);
  const [processingId, setProcessingId] = useState<number | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>("PENDING");
  
  // Note dialog state
  const [actionDialog, setActionDialog] = useState<{
    leadId: number;
    leadName: string;
    action: "APPROVE" | "REJECT" | "NEEDS_RECHECK" | "MARK_DNC";
    note: string;
  } | null>(null);

  const fetchReviewQueue = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiFetch<{ total: number; leads: LeadItem[] }>(`/leads?review_status=${filterStatus}&limit=100`);
      setLeads(res.leads || []);
    } catch (err) {
      console.error("Failed to fetch review queue:", err);
    } finally {
      setLoading(false);
    }
  }, [filterStatus]);

  useEffect(() => {
    fetchReviewQueue();
  }, [fetchReviewQueue]);

  const executeReviewAction = async (leadId: number, action: "APPROVE" | "REJECT" | "NEEDS_RECHECK" | "MARK_DNC", note?: string) => {
    setProcessingId(leadId);
    try {
      await apiFetch(`/leads/${leadId}/review`, {
        method: "PATCH",
        body: JSON.stringify({ action, note })
      });
      if (filterStatus === "PENDING") {
        setLeads(prev => prev.filter(l => l.id !== leadId));
      } else {
        fetchReviewQueue();
      }
    } catch (err) {
      console.error(`Failed to execute review action ${action}:`, err);
    } finally {
      setProcessingId(null);
      setActionDialog(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold tracking-tight text-slate-900">Human Review & Outreach Gate</h1>
            <span className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
              <ShieldCheck className="w-3.5 h-3.5" />
              Source Truth Gate
            </span>
          </div>
          <p className="text-slate-500 text-xs mt-1">
            Review company identity signals, official website reachability, contact provenance, and service need evidence before approving leads for automated outreach campaigns.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex rounded-lg bg-slate-100 border border-slate-200 p-1">
            {["PENDING", "APPROVED", "REJECTED", "NEEDS_RECHECK"].map(status => (
              <button
                key={status}
                onClick={() => setFilterStatus(status)}
                className={`px-3 py-1 rounded-md text-xs font-semibold transition-all ${
                  filterStatus === status
                    ? "bg-white text-blue-700 shadow-xs border border-slate-200"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                {status.replace("_", " ")}
              </button>
            ))}
          </div>

          <button
            onClick={fetchReviewQueue}
            className="p-2 rounded-lg bg-white border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition"
            title="Refresh Review Queue"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-blue-600" : ""}`} />
          </button>
        </div>
      </div>

      {/* Leads List */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 text-slate-400">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-600 mb-3" />
          <p className="text-xs font-medium">Loading verifiable review records...</p>
        </div>
      ) : leads.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center rounded-lg bg-white border border-slate-200 p-8 shadow-xs">
          <CheckCircle2 className="w-12 h-12 text-emerald-600 mb-3" />
          <h3 className="text-base font-bold text-slate-900">Review Queue is Clear</h3>
          <p className="text-slate-500 text-xs max-w-md mt-1">
            No leads currently in <span className="text-blue-700 font-semibold">{filterStatus}</span> status requiring verification.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3.5">
          {leads.map(lead => {
            const primaryContact = lead.contacts[0];
            const isProcessing = processingId === lead.id;

            return (
              <div
                key={lead.id}
                className="flex flex-col lg:flex-row lg:items-center justify-between gap-5 p-5 rounded-lg bg-white border border-slate-200 hover:border-slate-300 transition shadow-xs"
              >
                {/* Company & Identity */}
                <div className="space-y-1.5 lg:max-w-md">
                  <div className="flex items-center gap-2.5 flex-wrap">
                    <h3 className="font-bold text-slate-900 text-sm truncate">
                      {lead.company.business_name}
                    </h3>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                      lead.company.identity_verification_status === "HIGH"
                        ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                        : lead.company.identity_verification_status === "MEDIUM"
                        ? "bg-blue-50 text-blue-800 border-blue-200"
                        : "bg-slate-100 text-slate-700 border-slate-200"
                    }`}>
                      ID: {lead.company.identity_verification_status}
                    </span>

                    {lead.company.operating_status && (
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        lead.company.operating_status === "ACTIVE" ? "bg-emerald-50 text-emerald-700 border border-emerald-200" :
                        lead.company.operating_status === "PROBABLY_ACTIVE" ? "bg-blue-50 text-blue-700 border border-blue-200" :
                        "bg-slate-100 text-slate-600"
                      }`}>
                        {lead.company.operating_status}
                      </span>
                    )}

                    {lead.company.has_conflicts && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-800 border border-amber-200 flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3 text-amber-600" /> Conflict
                      </span>
                    )}
                  </div>

                  <div className="flex flex-wrap items-center gap-2.5 text-xs text-slate-500">
                    {lead.company.website ? (
                      <a
                        href={lead.company.website.startsWith("http") ? lead.company.website : `https://${lead.company.website}`}
                        target="_blank"
                        rel="noreferrer"
                        className="flex items-center gap-1 text-blue-600 hover:underline font-medium"
                      >
                        {lead.company.website}
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    ) : (
                      <span className="text-slate-400 italic">No public website registered</span>
                    )}

                    {lead.company.city && (
                      <span>• {lead.company.city}, {lead.company.country || "Worldwide"}</span>
                    )}

                    <span>• Source: <strong className="text-slate-700">{lead.company.source}</strong></span>
                  </div>

                  {lead.recommended_service && (
                    <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs bg-slate-50 text-slate-700 border border-slate-200">
                      <Sparkles className="w-3 h-3 text-blue-600" />
                      <span>Opportunity: <strong>{lead.recommended_service}</strong></span>
                    </div>
                  )}
                </div>

                {/* Contact & Verification Provenance */}
                <div className="space-y-1 text-xs text-slate-700 lg:min-w-[200px]">
                  <div className="font-semibold text-slate-400 uppercase tracking-wider text-[10px]">
                    Verified Contact Channel
                  </div>
                  {primaryContact ? (
                    <div>
                      <div className="font-bold text-slate-900">
                        {primaryContact.full_name || <span className="text-slate-500 font-normal italic">General Inbox</span>}
                      </div>
                      {primaryContact.email && (
                        <div className="text-slate-600 flex items-center gap-1.5 mt-0.5">
                          <span className="font-mono">{primaryContact.email}</span>
                          <span className="text-[10px] px-1 py-0.2 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 font-mono">
                            {primaryContact.email_status === "MAILBOX_VERIFIED" ? "Mailbox OK" : "Domain MX"}
                          </span>
                        </div>
                      )}
                    </div>
                  ) : lead.company.phone ? (
                    <div className="text-slate-600">
                      Phone: <span className="text-slate-900 font-mono font-medium">{lead.company.normalized_phone_e164 || lead.company.phone}</span>
                    </div>
                  ) : (
                    <div className="text-slate-400 italic">No direct public contact found</div>
                  )}
                </div>

                {/* Data Quality & Scores */}
                <div className="flex items-center gap-4 text-xs">
                  <div className="text-center p-2 rounded-lg bg-slate-50 border border-slate-100 min-w-[75px]">
                    <div className="text-[10px] text-slate-400 font-semibold uppercase">Quality</div>
                    <div className="text-sm font-bold font-mono text-slate-900">{lead.data_quality_score}/100</div>
                  </div>

                  <div className="text-center p-2 rounded-lg bg-slate-50 border border-slate-100 min-w-[75px]">
                    <div className="text-[10px] text-slate-400 font-semibold uppercase">Opp Score</div>
                    <div className="text-sm font-bold font-mono text-blue-700">{lead.score?.opportunity_score || 0}/100</div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setSelectedLeadId(lead.id)}
                    className="p-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition flex items-center gap-1"
                    title="Inspect Full Provenance & Evidence"
                  >
                    <Eye className="w-4 h-4" />
                    <span>Inspect</span>
                  </button>

                  <button
                    disabled={isProcessing}
                    onClick={() => setActionDialog({
                      leadId: lead.id,
                      leadName: lead.company.business_name,
                      action: "APPROVE",
                      note: ""
                    })}
                    className="px-3 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold transition flex items-center gap-1.5 disabled:opacity-50"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Approve</span>
                  </button>

                  <button
                    disabled={isProcessing}
                    onClick={() => setActionDialog({
                      leadId: lead.id,
                      leadName: lead.company.business_name,
                      action: "NEEDS_RECHECK",
                      note: ""
                    })}
                    className="p-2 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-700 border border-amber-200 transition"
                    title="Send for Recheck"
                  >
                    <RotateCcw className="w-4 h-4" />
                  </button>

                  <button
                    disabled={isProcessing}
                    onClick={() => setActionDialog({
                      leadId: lead.id,
                      leadName: lead.company.business_name,
                      action: "REJECT",
                      note: ""
                    })}
                    className="p-2 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 transition"
                    title="Reject Lead"
                  >
                    <XCircle className="w-4 h-4" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Reviewer Note Confirmation Dialog */}
      {actionDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs">
          <div className="w-full max-w-md bg-white rounded-lg border border-slate-200 shadow-xl p-5 space-y-4">
            <div>
              <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-blue-600" />
                <span>Confirm Review Action: {actionDialog.action}</span>
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                Target Business: <strong className="text-slate-800">{actionDialog.leadName}</strong>
              </p>
            </div>

            <div>
              <label className="block text-[11px] font-bold text-slate-700 uppercase mb-1">
                Reviewer Notes (Optional Audit Trail)
              </label>
              <textarea
                value={actionDialog.note}
                onChange={(e) => setActionDialog({ ...actionDialog, note: e.target.value })}
                placeholder="Add audit justification or notes regarding business identity / website verification..."
                rows={3}
                className="w-full p-2.5 rounded border border-slate-300 text-xs focus:ring-1 focus:ring-blue-500 focus:outline-none"
              />
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setActionDialog(null)}
                className="px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-100 rounded font-medium"
              >
                Cancel
              </button>

              <button
                type="button"
                onClick={() => executeReviewAction(actionDialog.leadId, actionDialog.action, actionDialog.note)}
                className={`px-4 py-1.5 text-xs font-bold text-white rounded shadow-xs ${
                  actionDialog.action === "APPROVE" ? "bg-emerald-600 hover:bg-emerald-700" :
                  actionDialog.action === "REJECT" ? "bg-rose-600 hover:bg-rose-700" :
                  "bg-amber-600 hover:bg-amber-700"
                }`}
              >
                Confirm {actionDialog.action}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Lead Detail Modal */}
      {selectedLeadId && (
        <LeadDetailModal
          leadId={selectedLeadId}
          onClose={() => setSelectedLeadId(null)}
          onRefreshList={fetchReviewQueue}
        />
      )}
    </div>
  );
}
