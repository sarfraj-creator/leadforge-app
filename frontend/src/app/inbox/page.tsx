"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Inbox as InboxIcon,
  Send,
  MessageSquare,
  AlertOctagon,
  UserX,
  Sparkles,
  RefreshCw,
  Building2,
  Mail,
  CheckCircle2,
  Clock,
  Reply,
  Paperclip,
  ExternalLink,
  FileText
} from "lucide-react";
import { EmailThread } from "@/types";
import { apiFetch } from "@/lib/api";

export default function InboxPage() {
  const [folder, setFolder] = useState<"inbox" | "sent" | "replies" | "bounces" | "unsubscribes">("inbox");
  const [threads, setThreads] = useState<EmailThread[]>([]);
  const [selectedThread, setSelectedThread] = useState<EmailThread | null>(null);
  const [loading, setLoading] = useState(true);

  // Reply State
  const [replyText, setReplyText] = useState("");
  const [sendingReply, setSendingReply] = useState(false);

  // Simulate Inbound State
  const [simulateText, setSimulateText] = useState("Hi, we are interested in discussing a website redesign. When are you free for a call?");
  const [simulating, setSimulating] = useState(false);

  const fetchThreads = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiFetch<EmailThread[]>(`/inbox/threads?folder=${folder}`);
      setThreads(data);
      if (data.length > 0 && !selectedThread) {
        setSelectedThread(data[0]);
      } else if (selectedThread) {
        const found = data.find((t) => t.id === selectedThread.id);
        if (found) setSelectedThread(found);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [folder, selectedThread]);

  useEffect(() => {
    fetchThreads();
  }, [fetchThreads]);

  const handleSendManualReply = async () => {
    if (!selectedThread || !replyText.trim()) return;
    setSendingReply(true);
    try {
      await apiFetch(`/emails/send`, {
        method: "POST",
        body: JSON.stringify({
          lead_id: selectedThread.lead_id || 1,
          to_email: selectedThread.recipient_email,
          subject: selectedThread.subject.startsWith("Re:") ? selectedThread.subject : `Re: ${selectedThread.subject}`,
          body_text: replyText.trim()
        })
      });
      setReplyText("");
      fetchThreads();
    } catch (err: any) {
      alert("Failed to send reply: " + err.message);
    } finally {
      setSendingReply(false);
    }
  };

  const handleSimulateReply = async () => {
    if (!selectedThread || !simulateText.trim()) return;
    setSimulating(true);
    try {
      await apiFetch(`/inbox/threads/${selectedThread.id}/simulate-inbound`, {
        method: "POST",
        body: JSON.stringify({ body_text: simulateText.trim() })
      });
      fetchThreads();
    } catch (err) {
      alert("Simulation failed: " + err);
    } finally {
      setSimulating(false);
    }
  };

  return (
    <div className="space-y-4 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Unified Outreach Inbox</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Centralized email communication with automated AI reply sentiment classification and automatic sequence stopping.
        </p>
      </div>

      {/* 3-Pane Inbox Container */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-xs flex h-[calc(100vh-210px)] overflow-hidden">
        {/* Left Pane: Folders */}
        <div className="w-48 border-r border-slate-200 p-3 space-y-1 bg-slate-50/50 shrink-0">
          {[
            { id: "inbox", label: "All Messages", icon: InboxIcon },
            { id: "replies", label: "Replies", icon: MessageSquare, badge: "1" },
            { id: "sent", label: "Sent Outreach", icon: Send },
            { id: "bounces", label: "Bounces", icon: AlertOctagon },
            { id: "unsubscribes", label: "Unsubscribed", icon: UserX },
          ].map((f) => {
            const Icon = f.icon;
            const isActive = folder === f.id;
            return (
              <button
                key={f.id}
                onClick={() => setFolder(f.id as any)}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-md text-xs font-semibold transition ${
                  isActive
                    ? "bg-blue-600 text-white shadow-xs"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }`}
              >
                <div className="flex items-center gap-2">
                  <Icon className="w-3.5 h-3.5" />
                  <span>{f.label}</span>
                </div>
                {f.badge && (
                  <span className={`text-[10px] px-1.5 py-0.2 rounded-full font-bold ${
                    isActive ? "bg-white/20 text-white" : "bg-blue-100 text-blue-800"
                  }`}>
                    {f.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Center Pane: Thread List */}
        <div className="w-80 border-r border-slate-200 flex flex-col shrink-0">
          <div className="p-3 border-b border-slate-100 bg-slate-50/30 flex items-center justify-between">
            <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              {folder.toUpperCase()} ({threads.length})
            </span>
            <button onClick={fetchThreads} className="p-1 text-slate-400 hover:text-slate-600">
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="divide-y divide-slate-100 overflow-y-auto flex-1">
            {loading ? (
              <div className="py-8 text-center text-xs text-slate-400">Loading threads...</div>
            ) : threads.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-400">No email threads in this folder.</div>
            ) : (
              threads.map((t) => {
                const isSelected = selectedThread?.id === t.id;
                return (
                  <div
                    key={t.id}
                    onClick={() => setSelectedThread(t)}
                    className={`p-3 text-xs cursor-pointer transition ${
                      isSelected ? "bg-blue-50/70 border-l-4 border-blue-600" : "hover:bg-slate-50"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900 truncate">
                        {t.company_name || t.recipient_email}
                      </span>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {new Date(t.last_message_at).toLocaleDateString([], { month: "short", day: "numeric" })}
                      </span>
                    </div>

                    <div className="font-medium text-slate-700 truncate mt-0.5">{t.subject}</div>

                    {t.reply_classification && (
                      <div className="mt-1.5 flex items-center gap-1">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          t.reply_classification === "Interested" || t.reply_classification === "Meeting Request"
                            ? "bg-emerald-100 text-emerald-800"
                            : t.reply_classification === "Unsubscribe"
                            ? "bg-rose-100 text-rose-800"
                            : "bg-blue-100 text-blue-800"
                        }`}>
                          AI: {t.reply_classification}
                        </span>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right Pane: Message Viewer & Reply Composer */}
        <div className="flex-1 flex flex-col overflow-hidden bg-slate-50/30">
          {selectedThread ? (
            <>
              {/* Thread Header */}
              <div className="p-4 border-b border-slate-200 bg-white flex items-center justify-between">
                <div>
                  <h2 className="text-sm font-bold text-slate-900">{selectedThread.subject}</h2>
                  <div className="text-xs text-slate-500 mt-0.5">
                    Prospect: <span className="font-semibold text-slate-700">{selectedThread.recipient_email}</span> · {selectedThread.company_name || ""}
                  </div>
                </div>

                {selectedThread.reply_classification && (
                  <div className="text-right">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">AI Sentiment Classifier</span>
                    <div className="text-xs font-bold text-emerald-700 flex items-center gap-1">
                      <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
                      <span>{selectedThread.reply_classification}</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Message History */}
              <div className="p-6 space-y-4 overflow-y-auto flex-1">
                {selectedThread.messages.map((m) => (
                  <div
                    key={m.id}
                    className={`p-4 rounded-xl border text-xs max-w-xl space-y-2.5 ${
                      m.direction === "OUTBOUND"
                        ? "ml-auto bg-blue-50/70 border-blue-200 text-slate-900"
                        : "mr-auto bg-white border-slate-200 text-slate-900 shadow-2xs"
                    }`}
                  >
                    <div className="flex items-center justify-between text-[11px] text-slate-500 border-b border-slate-200/50 pb-1.5">
                      <span className="font-bold flex items-center gap-1">
                        {m.direction === "OUTBOUND" ? "Outbound Email Dispatch" : "Inbound Prospect Reply"}
                      </span>
                      <span>{m.sent_at ? new Date(m.sent_at).toLocaleString() : "Sent"}</span>
                    </div>
                    <div className="whitespace-pre-line leading-relaxed text-slate-800 font-sans">{m.body_text}</div>

                    {/* Attached R&D Document Pill for Outbound Messages */}
                    {m.direction === "OUTBOUND" && selectedThread.lead_id && (
                      <div className="pt-2 border-t border-blue-200/60 flex items-center justify-between">
                        <div className="flex items-center gap-1.5 text-[11px] text-blue-900 font-semibold">
                          <Paperclip className="w-3 h-3 text-blue-600" />
                          <span>Attached: Technical R&D Audit Report (HTML/PDF)</span>
                        </div>
                        <a
                          href={`http://127.0.0.1:8000/api/audits/lead/${selectedThread.lead_id}/report/html`}
                          target="_blank"
                          rel="noreferrer"
                          className="px-2 py-0.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-[10px] font-bold inline-flex items-center gap-1"
                        >
                          <span>Inspect Report</span>
                          <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Direct Outbound Reply Composer */}
              <div className="p-4 bg-white border-t border-slate-200 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-slate-800 flex items-center gap-1">
                    <Reply className="w-3.5 h-3.5 text-blue-600" />
                    <span>Send Direct Reply to {selectedThread.recipient_email}</span>
                  </span>
                </div>
                <div className="flex gap-2">
                  <textarea
                    rows={2}
                    value={replyText}
                    onChange={(e) => setReplyText(e.target.value)}
                    placeholder="Type your response to this prospect..."
                    className="flex-1 p-2 rounded border border-slate-300 text-xs outline-none focus:border-blue-500 font-sans"
                  />
                  <button
                    onClick={handleSendManualReply}
                    disabled={sendingReply || !replyText.trim()}
                    className="px-4 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-xs disabled:opacity-50 transition flex items-center gap-1.5 self-end"
                  >
                    <Send className="w-3.5 h-3.5" />
                    <span>{sendingReply ? "Sending..." : "Send Reply"}</span>
                  </button>
                </div>
              </div>

              {/* Simulation Sandbox Toolbar */}
              <div className="p-3 bg-slate-100/70 border-t border-slate-200 space-y-1.5 text-xs">
                <div className="flex items-center justify-between">
                  <div className="font-bold text-slate-700 flex items-center gap-1">
                    <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
                    <span>Simulate Inbound Reply (Tests AI Classification & Auto-Stop)</span>
                  </div>
                </div>

                <div className="flex gap-2">
                  <input
                    type="text"
                    value={simulateText}
                    onChange={(e) => setSimulateText(e.target.value)}
                    placeholder="e.g. Yes, we would like a redesign quote. Please schedule a meeting."
                    className="flex-1 px-3 py-1 rounded border border-slate-300 text-xs outline-none focus:border-blue-500 bg-white"
                  />
                  <button
                    onClick={handleSimulateReply}
                    disabled={simulating}
                    className="px-3 py-1 rounded bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold shadow-2xs disabled:opacity-50 transition shrink-0"
                  >
                    {simulating ? "Processing..." : "Simulate Inbound"}
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="py-20 text-center text-xs text-slate-400">Select an email thread to inspect.</div>
          )}
        </div>
      </div>
    </div>
  );
}
