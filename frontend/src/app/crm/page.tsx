"use client";

import React, { useState, useEffect } from "react";
import {
  Kanban,
  DollarSign,
  Plus,
  ArrowRight,
  Flame,
  Globe,
  Building2,
  Calendar,
  CheckSquare,
  Award,
  ChevronRight
} from "lucide-react";
import { LeadScoreBadge } from "@/components/LeadScoreBadge";
import { apiFetch } from "@/lib/api";
import { LeadDetailModal } from "@/components/LeadDetailModal";

interface KanbanCard {
  id: number;
  company_id: number;
  company_name: string;
  city?: string;
  website?: string;
  opportunity?: string;
  recommended_service?: string;
  score: number;
  score_category: string;
  contact_name?: string;
  contact_email?: string;
  freshness_state: string;
  created_at: string;
}

interface KanbanStage {
  stage_id: number;
  name: string;
  color_code: string;
  order: number;
  count: number;
  cards: KanbanCard[];
}

export default function CRMPage() {
  const [board, setBoard] = useState<KanbanStage[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLeadId, setSelectedLeadId] = useState<number | null>(null);

  const fetchBoard = async () => {
    try {
      const data = await apiFetch<KanbanStage[]>("/crm/kanban");
      setBoard(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBoard();
  }, []);

  const moveStage = async (leadId: number, targetStage: string) => {
    try {
      await apiFetch(`/leads/${leadId}/stage`, {
        method: "PATCH",
        body: JSON.stringify({ stage: targetStage })
      });
      fetchBoard();
    } catch (err) {
      alert("Failed to update lead stage: " + err);
    }
  };

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">CRM Kanban Pipeline</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Progress qualified opportunities from initial discovery to discovery calls, proposals, and won contracts.
          </p>
        </div>
      </div>

      {/* Kanban Board Container */}
      {loading ? (
        <div className="py-20 text-center text-xs text-slate-400">Loading CRM Kanban Pipeline...</div>
      ) : (
        <div className="flex gap-4 overflow-x-auto pb-6 pt-1">
          {board.map((column) => (
            <div
              key={column.stage_id}
              className="w-72 shrink-0 bg-slate-100/70 rounded-lg border border-slate-200 flex flex-col max-h-[calc(100vh-210px)]"
            >
              {/* Column Header */}
              <div className="p-3 border-b border-slate-200 flex items-center justify-between bg-white rounded-t-lg">
                <div className="flex items-center gap-2">
                  <span
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: column.color_code }}
                  ></span>
                  <span className="text-xs font-bold text-slate-800">{column.name}</span>
                </div>
                <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
                  {column.cards.length}
                </span>
              </div>

              {/* Cards Container */}
              <div className="p-2.5 space-y-2 overflow-y-auto flex-1">
                {column.cards.length === 0 ? (
                  <div className="py-8 text-center text-[11px] text-slate-400">No leads in stage.</div>
                ) : (
                  column.cards.map((card) => (
                    <div
                      key={card.id}
                      onClick={() => setSelectedLeadId(card.id)}
                      className="p-3 rounded-md bg-white border border-slate-200/90 shadow-2xs hover:shadow-xs hover:border-blue-300 transition cursor-pointer space-y-2 text-xs"
                    >
                      <div className="flex items-start justify-between gap-1">
                        <div className="font-bold text-slate-900 leading-tight">
                          {card.company_name}
                        </div>
                        <LeadScoreBadge score={card.score} category={card.score_category} size="sm" />
                      </div>

                      <div className="text-[11px] text-blue-700 font-semibold truncate">
                        {card.opportunity || "Website Modernization"}
                      </div>

                      <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-500">
                        <span>{card.city || "—"}</span>
                        <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                          {/* Quick Advance Stage Button */}
                          {column.name === "Qualified" && (
                            <button
                              onClick={() => moveStage(card.id, "Contacted")}
                              title="Move to Contacted"
                              className="px-1.5 py-0.5 rounded bg-blue-50 text-blue-600 font-semibold hover:bg-blue-100"
                            >
                              Contact &rarr;
                            </button>
                          )}
                          {column.name === "Contacted" && (
                            <button
                              onClick={() => moveStage(card.id, "Interested")}
                              title="Move to Interested"
                              className="px-1.5 py-0.5 rounded bg-amber-50 text-amber-600 font-semibold hover:bg-amber-100"
                            >
                              Interested &rarr;
                            </button>
                          )}
                          {column.name === "Interested" && (
                            <button
                              onClick={() => moveStage(card.id, "Meeting")}
                              title="Move to Meeting"
                              className="px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-600 font-semibold hover:bg-emerald-100"
                            >
                              Meeting &rarr;
                            </button>
                          )}
                          {column.name === "Meeting" && (
                            <button
                              onClick={() => moveStage(card.id, "Proposal")}
                              title="Move to Proposal"
                              className="px-1.5 py-0.5 rounded bg-cyan-50 text-cyan-600 font-semibold hover:bg-cyan-100"
                            >
                              Proposal &rarr;
                            </button>
                          )}
                          {column.name === "Proposal" && (
                            <button
                              onClick={() => moveStage(card.id, "Won")}
                              title="Move to Won"
                              className="px-1.5 py-0.5 rounded bg-emerald-600 text-white font-semibold hover:bg-emerald-700"
                            >
                              Won Deal ✓
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Lead Detail Modal */}
      <LeadDetailModal
        leadId={selectedLeadId}
        onClose={() => setSelectedLeadId(null)}
        onRefreshList={fetchBoard}
      />
    </div>
  );
}
