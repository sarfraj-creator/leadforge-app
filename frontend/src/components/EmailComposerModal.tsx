"use client";

import React, { useState, useEffect } from "react";
import { X, Send, Sparkles, AlertCircle, CheckCircle, FileText, Paperclip, Eye, Edit3, ExternalLink, ShieldCheck, Gauge, Smartphone, Zap } from "lucide-react";
import { Lead } from "@/types";
import { apiFetch } from "@/lib/api";

interface EmailComposerModalProps {
  lead: Lead | null;
  onClose: () => void;
  onSuccess?: () => void;
  onSent?: () => void;
}

export function EmailComposerModal({ lead, onClose, onSuccess }: EmailComposerModalProps) {
  const [toEmail, setToEmail] = useState("");
  const [subject, setSubject] = useState("");
  const [bodyText, setBodyText] = useState("");
  const [attachReport, setAttachReport] = useState(true);
  const [viewMode, setViewMode] = useState<"edit" | "preview">("edit");
  const [generatingAI, setGeneratingAI] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (lead) {
      const email = lead.contacts?.[0]?.email || lead.company.business_email || "";
      const contactName = lead.contacts?.[0]?.full_name?.split(" ")[0] || "there";
      const issue = lead.audit?.issues?.[0]?.evidence || "your mobile smartphone viewports and page load performance";
      const rec = lead.recommended_service || lead.primary_opportunity || "Responsive Redesign & Speed Modernization";

      setToEmail(email);
      setSubject(`Quick question regarding ${lead.company.business_name} website & mobile experience`);
      setBodyText(
        `Hi ${contactName},\n\nI was analyzing digital presence for companies in ${lead.company.city || "your area"} and ran an engineering audit on ${lead.company.website || "your website"}.\n\nOur analysis identified ${issue}, which impacts how effectively prospective clients can contact you.\n\nWe prepared a technical R&D Audit Report with a step-by-step modernization blueprint for ${lead.company.business_name} (attached below):\n• Service Recommendation: ${rec}\n• Turnaround: 2-3 weeks\n• Target ROI: 2.5x increase in inbound inquiries\n\nWould you be open to a 10-minute call this Thursday to walk through the findings?\n\nBest regards,\nAlex Mercer\nAcme Digital & Web Engineering`
      );
    }
  }, [lead]);

  if (!lead) return null;

  const handleGenerateAI = async () => {
    setGeneratingAI(true);
    setError(null);
    try {
      const res = await apiFetch<{ subject: string; body_text: string }>(`/emails/generate-ai-outreach`, {
        method: "POST",
        body: JSON.stringify({
          lead_id: lead.id,
          opportunity_type: lead.primary_opportunity
        })
      });
      setSubject(res.subject);
      setBodyText(res.body_text);
    } catch (err: any) {
      setError(err.message || "Failed to generate AI outreach");
    } finally {
      setGeneratingAI(false);
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!toEmail.trim()) {
      setError("Please provide a valid recipient email address.");
      return;
    }
    setSending(true);
    setError(null);
    try {
      await apiFetch(`/emails/send`, {
        method: "POST",
        body: JSON.stringify({
          lead_id: lead.id,
          to_email: toEmail.trim(),
          subject: subject.trim(),
          body_text: bodyText.trim(),
          attach_report: attachReport
        })
      });
      if (onSuccess) onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to send email");
    } finally {
      setSending(false);
    }
  };

  const audit = lead.audit;
  const companySlug = lead.company.business_name.replace(/[^a-zA-Z0-9_-]/g, "_").slice(0, 30);
  const reportDocName = `Technical-Audit-Report-${companySlug}.html`;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
      <div className="w-full max-w-3xl bg-white rounded-xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-3.5 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div>
            <h2 className="text-sm font-bold text-slate-900">Personalized Outreach & Technical Document Dispatch</h2>
            <div className="text-xs text-slate-500">
              Recipient: <span className="font-semibold text-slate-700">{lead.company.business_name}</span> &bull; {lead.company.domain || lead.company.website || "No domain"}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center bg-slate-200 p-0.5 rounded-lg text-xs font-semibold">
              <button
                type="button"
                onClick={() => setViewMode("edit")}
                className={`flex items-center gap-1 px-2.5 py-1 rounded-md transition ${
                  viewMode === "edit" ? "bg-white text-slate-900 shadow-2xs" : "text-slate-600 hover:text-slate-900"
                }`}
              >
                <Edit3 className="w-3.5 h-3.5" />
                <span>Edit Copy</span>
              </button>
              <button
                type="button"
                onClick={() => setViewMode("preview")}
                className={`flex items-center gap-1 px-2.5 py-1 rounded-md transition ${
                  viewMode === "preview" ? "bg-white text-blue-700 shadow-2xs" : "text-slate-600 hover:text-slate-900"
                }`}
              >
                <Eye className="w-3.5 h-3.5" />
                <span>Rich HTML Email Preview</span>
              </button>
            </div>
            <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-600 rounded">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Composer Form */}
        <form onSubmit={handleSend} className="flex-1 flex flex-col overflow-hidden">
          {error && (
            <div className="mx-6 mt-4 p-3 rounded-md bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="p-6 space-y-4 overflow-y-auto flex-1 text-xs">
            {/* Top Toolbar */}
            <div className="flex items-center justify-between">
              <button
                type="button"
                onClick={handleGenerateAI}
                disabled={generatingAI}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 text-blue-700 border border-blue-200 font-semibold hover:bg-blue-100 disabled:opacity-50 transition"
              >
                <Sparkles className={`w-3.5 h-3.5 ${generatingAI ? "animate-spin" : ""}`} />
                <span>{generatingAI ? "Grounding in Evidence..." : "AI Generate from Technical Audit"}</span>
              </button>
              <div className="text-[11px] text-slate-400">Tokens: &#123;&#123;company_name&#125;&#125;, &#123;&#123;first_name&#125;&#125;</div>
            </div>

            {/* Recipient and Subject Fields */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-500 font-medium mb-1">To Email Recipient:</label>
                <input
                  type="email"
                  required
                  value={toEmail}
                  onChange={(e) => setToEmail(e.target.value)}
                  placeholder="prospect@company.com"
                  className="w-full px-3 py-1.5 rounded-md border border-slate-300 text-slate-900 font-mono outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-slate-500 font-medium mb-1">Subject Line:</label>
                <input
                  type="text"
                  required
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="Subject line..."
                  className="w-full px-3 py-1.5 rounded-md border border-slate-300 text-slate-900 font-medium outline-none focus:border-blue-500"
                />
              </div>
            </div>

            {/* View Mode Switching */}
            {viewMode === "edit" ? (
              <div>
                <label className="block text-slate-500 font-medium mb-1">Email Body Copy (Plain / Markdown):</label>
                <textarea
                  required
                  rows={10}
                  value={bodyText}
                  onChange={(e) => setBodyText(e.target.value)}
                  className="w-full p-3 rounded-lg border border-slate-300 text-slate-900 leading-relaxed font-sans outline-none focus:border-blue-500"
                />
              </div>
            ) : (
              /* Rich Formatted HTML Email Preview */
              <div className="rounded-xl border border-slate-300 overflow-hidden bg-slate-100 p-4 space-y-3">
                <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500 flex items-center justify-between">
                  <span>Simulated Inbox HTML Rendering</span>
                  <span className="text-blue-600 font-mono">UTF-8 Responsive</span>
                </div>

                <div className="bg-white rounded-lg border border-slate-200 shadow-xs p-6 space-y-4 max-w-xl mx-auto text-slate-800">
                  {/* Header */}
                  <div className="p-3.5 rounded-lg bg-slate-900 text-white flex items-center justify-between">
                    <div>
                      <div className="font-extrabold text-sm">Acme Growth & Engineering</div>
                      <div className="text-[10px] text-slate-400">B2B Website Intelligence & Modernization</div>
                    </div>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-400/30">
                      R&D AUDIT BRIEF
                    </span>
                  </div>

                  {/* Body Paragraphs */}
                  <div className="space-y-2 text-xs leading-relaxed text-slate-700 whitespace-pre-line">
                    {bodyText}
                  </div>

                  {/* Embedded Scorecard */}
                  {audit && (
                    <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Observed Technical Scorecard</span>
                        <span className="text-xs font-bold font-mono px-2 py-0.5 rounded bg-blue-100 text-blue-800">
                          Health: {audit.overall_score}/100
                        </span>
                      </div>
                      <div className="grid grid-cols-4 gap-2 text-center text-[10px]">
                        <div className="p-1.5 bg-white rounded border border-slate-200">
                          <div className="text-slate-400">Mobile</div>
                          <div className={`font-bold font-mono ${audit.mobile_score < 60 ? "text-rose-600" : "text-slate-800"}`}>{audit.mobile_score}/100</div>
                        </div>
                        <div className="p-1.5 bg-white rounded border border-slate-200">
                          <div className="text-slate-400">Speed</div>
                          <div className={`font-bold font-mono ${audit.performance_score < 60 ? "text-amber-600" : "text-slate-800"}`}>{audit.performance_score}/100</div>
                        </div>
                        <div className="p-1.5 bg-white rounded border border-slate-200">
                          <div className="text-slate-400">SEO</div>
                          <div className="font-bold font-mono text-slate-800">{audit.seo_score}/100</div>
                        </div>
                        <div className="p-1.5 bg-white rounded border border-slate-200">
                          <div className="text-slate-400">Security</div>
                          <div className="font-bold font-mono text-slate-800">{audit.security_score}/100</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Attachment Callout */}
                  {attachReport && (
                    <div className="p-3 rounded-lg bg-blue-50/70 border border-dashed border-blue-300 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Paperclip className="w-4 h-4 text-blue-600 shrink-0" />
                        <div>
                          <div className="font-bold text-blue-950">{reportDocName}</div>
                          <div className="text-[10px] text-blue-700">MIME Attachment: Standalone Printable Technical R&D Audit Report Document</div>
                        </div>
                      </div>
                      <a
                        href={`http://127.0.0.1:8000/api/audits/lead/${lead.id}/report/html`}
                        target="_blank"
                        rel="noreferrer"
                        className="px-2.5 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-[11px] font-semibold flex items-center gap-1"
                      >
                        <span>Inspect Doc</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Document Attachment Widget */}
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={attachReport}
                  onChange={(e) => setAttachReport(e.target.checked)}
                  className="rounded text-blue-600 focus:ring-blue-500"
                />
                <div className="flex items-center gap-1.5 text-xs text-slate-700 font-medium">
                  <Paperclip className="w-3.5 h-3.5 text-blue-600" />
                  <span>Attach Generated Technical R&D Audit Report Document ({reportDocName})</span>
                </div>
              </label>
              {attachReport && (
                <span className="text-[11px] font-mono font-semibold text-blue-700 bg-blue-100/60 px-2 py-0.5 rounded border border-blue-200">
                  RND-{lead.id}-{lead.company_id}
                </span>
              )}
            </div>
          </div>

          {/* Footer Controls */}
          <div className="px-6 py-3.5 border-t border-slate-200 flex items-center justify-between bg-slate-50">
            <div className="text-[11px] text-slate-400">
              Outbound will be logged to CRM and 4-step sequence (Day 0, 3, 7, 14) will be scheduled.
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onClose}
                className="px-3 py-1.5 text-xs text-slate-600 hover:text-slate-800 font-medium"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={sending}
                className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-xs disabled:opacity-50 transition"
              >
                <Send className="w-3.5 h-3.5" />
                <span>{sending ? "Dispatching..." : "Send Formatted Outreach"}</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
