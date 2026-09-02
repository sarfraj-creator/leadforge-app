"use client";

import React, { useState, useEffect } from "react";
import { Send, Plus, Clock, Users, Play, Pause, CheckCircle2, Layers, Sparkles, RefreshCw, Paperclip, ShieldAlert, CheckCheck } from "lucide-react";
import { Campaign } from "@/types";
import { apiFetch } from "@/lib/api";

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // New Campaign Form State
  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [creating, setCreating] = useState(false);

  // Action status
  const [runningCycle, setRunningCycle] = useState(false);
  const [cycleResult, setCycleResult] = useState<any>(null);
  const [enrolling, setEnrolling] = useState(false);

  const fetchCampaigns = async () => {
    setLoading(true);
    try {
      const data = await apiFetch<Campaign[]>("/campaigns");
      setCampaigns(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const handleRunSequenceCycle = async () => {
    setRunningCycle(true);
    try {
      const res = await apiFetch<any>("/campaigns/run-cycle", { method: "POST" });
      setCycleResult(res);
      fetchCampaigns();
    } catch (err: any) {
      alert("Failed to run sequence cycle: " + err.message);
    } finally {
      setRunningCycle(false);
    }
  };

  const handleAutoEnroll = async (category?: string) => {
    setEnrolling(true);
    try {
      const res = await apiFetch<any>("/campaigns/auto-enroll", {
        method: "POST",
        body: JSON.stringify({ category })
      });
      alert(`Successfully enrolled ${res.enrolled_count} leads into the 4-step sequence.`);
      fetchCampaigns();
    } catch (err: any) {
      alert("Failed to auto-enroll leads: " + err.message);
    } finally {
      setEnrolling(false);
    }
  };

  const handleCreateCampaign = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    setCreating(true);
    try {
      await apiFetch("/campaigns", {
        method: "POST",
        body: JSON.stringify({
          name: newTitle.trim(),
          description: newDesc.trim(),
          daily_limit: 50,
          hourly_limit: 10,
          approval_mode: "AUTOMATIC"
        })
      });
      setShowCreateModal(false);
      setNewTitle("");
      setNewDesc("");
      fetchCampaigns();
    } catch (err: any) {
      alert("Failed to create campaign: " + err.message);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Autonomous Outreach Campaigns & Multi-Day Sequences</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Automated 4-step cadence (Day 0, 3, 7, 14) with attached technical R&D reports, personalized AI copy, and auto-reply stop.
          </p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => handleAutoEnroll()}
            disabled={enrolling}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold border border-slate-300 shadow-2xs transition disabled:opacity-50"
          >
            <Users className="w-3.5 h-3.5" />
            <span>{enrolling ? "Enrolling..." : "Auto-Enroll Leads"}</span>
          </button>

          <button
            onClick={handleRunSequenceCycle}
            disabled={runningCycle}
            className="flex items-center gap-1.5 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-xs transition disabled:opacity-50"
          >
            <Sparkles className={`w-3.5 h-3.5 ${runningCycle ? "animate-spin" : ""}`} />
            <span>{runningCycle ? "Processing Steps..." : "Execute Sequence Cycle"}</span>
          </button>

          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold shadow-xs"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>New Custom Campaign</span>
          </button>
        </div>
      </div>

      {/* Cycle Result Alert */}
      {cycleResult && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs flex items-center justify-between shadow-2xs">
          <div className="flex items-center gap-2 font-medium">
            <CheckCheck className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>
              Sequence dispatch cycle finished: <strong>{cycleResult.processed}</strong> steps processed, <strong>{cycleResult.sent}</strong> emails dispatched with attached R&D documents, <strong>{cycleResult.skipped}</strong> paused/replied.
            </span>
          </div>
          <button onClick={() => setCycleResult(null)} className="text-slate-400 hover:text-slate-600 text-xs font-bold">
            Dismiss
          </button>
        </div>
      )}

      {/* Sequence Cadence Blueprint Info Card */}
      <div className="p-4 rounded-xl bg-slate-900 text-white shadow-xs space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-xs uppercase font-bold tracking-wider text-blue-400 flex items-center gap-2">
            <Clock className="w-4 h-4" />
            <span>Standard Agency Multi-Day Cadence (Day 0 &bull; Day 3 &bull; Day 7 &bull; Day 14)</span>
          </div>
          <span className="text-[11px] text-slate-400">Autonomous Execution Engine Active</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-1">
          <div className="p-3 rounded-lg bg-slate-800/80 border border-slate-700 text-xs space-y-1">
            <div className="font-bold text-blue-300 flex items-center justify-between">
              <span>Day 0: Initial Outreach</span>
              <Paperclip className="w-3 h-3 text-blue-400" />
            </div>
            <div className="text-slate-300 text-[11px]">Problem diagnosis from website audit + attached technical R&D report brief.</div>
          </div>

          <div className="p-3 rounded-lg bg-slate-800/80 border border-slate-700 text-xs space-y-1">
            <div className="font-bold text-blue-300">Day 3: Wireframe Value-Add</div>
            <div className="text-slate-300 text-[11px]">Interactive UX concept addressing specific mobile responsiveness bottlenecks.</div>
          </div>

          <div className="p-3 rounded-lg bg-slate-800/80 border border-slate-700 text-xs space-y-1">
            <div className="font-bold text-blue-300">Day 7: Competitor Benchmark</div>
            <div className="text-slate-300 text-[11px]">Industry case study and conversion framework comparison.</div>
          </div>

          <div className="p-3 rounded-lg bg-slate-800/80 border border-slate-700 text-xs space-y-1">
            <div className="font-bold text-blue-300">Day 14: Polite Breakup</div>
            <div className="text-slate-300 text-[11px]">Low-pressure final check-in with permanent access link to audit report.</div>
          </div>
        </div>
      </div>

      {/* Campaigns List */}
      <div className="space-y-4">
        {loading ? (
          <div className="py-16 text-center text-xs text-slate-400">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto text-blue-600 mb-2" />
            Loading outreach campaigns...
          </div>
        ) : campaigns.length === 0 ? (
          <div className="py-16 text-center text-xs text-slate-400">No campaigns created yet.</div>
        ) : (
          campaigns.map((camp) => (
            <div key={camp.id} className="p-6 bg-white rounded-xl border border-slate-200 shadow-2xs space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-base font-bold text-slate-900">{camp.name}</h2>
                    <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-emerald-100 text-emerald-800 font-mono">
                      {camp.status}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5">{camp.description || "Multi-step automated sequence"}</p>
                </div>

                <div className="text-right text-xs text-slate-500 shrink-0">
                  <div>Enrolled: <span className="font-bold text-slate-900">{camp.enrolled_leads_count} Leads</span></div>
                  <div>Daily Limit: <span className="font-bold text-slate-800">{camp.daily_limit} emails/day</span></div>
                  <div className="text-[11px] text-slate-400">Approval: <span className="font-semibold text-slate-700">{camp.approval_mode}</span></div>
                </div>
              </div>

              {/* Sequence Steps Flow */}
              <div className="pt-3 border-t border-slate-100 space-y-2">
                <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                  Configured Sequence Steps:
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                  {camp.sequence_steps?.map((step) => (
                    <div key={step.id} className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs space-y-1">
                      <div className="flex items-center justify-between font-bold text-slate-900">
                        <span>Step {step.step_number} (Day {step.delay_days})</span>
                        <span className="text-[10px] text-blue-700 font-semibold bg-blue-100/60 px-1.5 py-0.2 rounded border border-blue-200">
                          AI Active
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-700 font-medium truncate">{step.subject_template}</div>
                      <div className="text-[10px] text-slate-500 line-clamp-3 leading-relaxed">{step.body_template}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs">
          <div className="w-full max-w-md bg-white rounded-xl shadow-2xl border border-slate-200 p-6 space-y-4">
            <h2 className="font-bold text-sm text-slate-900">Create Custom Outreach Sequence</h2>
            <form onSubmit={handleCreateCampaign} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-600 font-medium mb-1">Campaign Name:</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Website Redesign Follow-Up Sequence"
                  className="w-full px-3 py-1.5 rounded border border-slate-300 outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-slate-600 font-medium mb-1">Description:</label>
                <textarea
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  rows={3}
                  placeholder="Campaign target criteria, angle, and notes..."
                  className="w-full p-2 rounded border border-slate-300 outline-none focus:border-blue-500"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-3 py-1.5 text-slate-600 hover:text-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="px-4 py-1.5 bg-blue-600 text-white font-semibold rounded hover:bg-blue-700 disabled:opacity-50"
                >
                  {creating ? "Creating..." : "Create Sequence"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
