"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Users, Mail, Phone, CheckCircle, AlertTriangle, ShieldCheck, RefreshCw } from "lucide-react";
import { Contact } from "@/types";
import { apiFetch } from "@/lib/api";

export default function ContactsPage() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [decisionMakerOnly, setDecisionMakerOnly] = useState(false);
  const [loading, setLoading] = useState(true);
  const [verifyingId, setVerifyingId] = useState<number | null>(null);

  const fetchContacts = useCallback(async () => {
    setLoading(true);
    try {
      const endpoint = decisionMakerOnly ? "/contacts?is_decision_maker=true" : "/contacts";
      const data = await apiFetch<Contact[]>(endpoint);
      setContacts(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [decisionMakerOnly]);

  useEffect(() => {
    fetchContacts();
  }, [fetchContacts]);

  const handleVerify = async (contactId: number) => {
    setVerifyingId(contactId);
    try {
      const res = await apiFetch(`/contacts/${contactId}/verify-email`, { method: "POST" });
      setContacts((prev) =>
        prev.map((c) => (c.id === contactId ? { ...c, email_status: res.status } : c))
      );
    } catch (err) {
      alert("Verification failed: " + err);
    } finally {
      setVerifyingId(null);
    }
  };

  return (
    <div className="space-y-4 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Verified Business Contacts</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Public decision maker contacts discovered from company websites with MX and syntax verification.
          </p>
        </div>
        <label className="flex items-center gap-2 text-xs font-semibold text-slate-700 bg-white px-3 py-1.5 rounded-md border border-slate-200 cursor-pointer">
          <input
            type="checkbox"
            checked={decisionMakerOnly}
            onChange={(e) => setDecisionMakerOnly(e.target.checked)}
            className="rounded border-slate-300 text-blue-600 focus:ring-0"
          />
          <span>Decision Makers Only (Founders / CEOs / Directors)</span>
        </label>
      </div>

      {/* Contacts Table */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-xs overflow-hidden">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50 text-slate-500 font-bold uppercase tracking-wider text-[10px]">
              <th className="p-3">Full Name</th>
              <th className="p-3">Job Title & Role</th>
              <th className="p-3">Email Address</th>
              <th className="p-3">Verification Status</th>
              <th className="p-3">Phone</th>
              <th className="p-3">Source Provenance</th>
              <th className="p-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-700">
            {loading ? (
              <tr>
                <td colSpan={7} className="p-10 text-center text-slate-400 text-xs">
                  Loading contacts directory...
                </td>
              </tr>
            ) : contacts.length === 0 ? (
              <tr>
                <td colSpan={7} className="p-10 text-center text-slate-400 text-xs">
                  No contacts found.
                </td>
              </tr>
            ) : (
              contacts.map((c) => (
                <tr key={c.id} className="hover:bg-slate-50 transition">
                  <td className="p-3 font-bold text-slate-900">{c.full_name}</td>
                  <td className="p-3">
                    <div className="text-slate-800 font-medium">{c.job_title || "Team Member"}</div>
                    {c.is_decision_maker && (
                      <span className="text-[10px] text-blue-700 bg-blue-50 px-1.5 py-0.2 rounded font-bold">
                        Decision Maker
                      </span>
                    )}
                  </td>
                  <td className="p-3 font-mono text-[11px] text-slate-800">{c.email || "—"}</td>
                  <td className="p-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        c.email_status === "VALID"
                          ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                          : c.email_status === "INVALID"
                          ? "bg-rose-50 text-rose-700 border border-rose-200"
                          : "bg-slate-100 text-slate-600 border border-slate-200"
                      }`}
                    >
                      {c.email_status}
                    </span>
                  </td>
                  <td className="p-3 text-slate-600">{c.phone || "—"}</td>
                  <td className="p-3 text-slate-500 text-[11px]">{c.source || "Official Website"}</td>
                  <td className="p-3 text-right">
                    {c.email && (
                      <button
                        onClick={() => handleVerify(c.id)}
                        disabled={verifyingId === c.id}
                        className="px-2.5 py-1 text-xs font-semibold rounded bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 disabled:opacity-50"
                      >
                        {verifyingId === c.id ? "Verifying..." : "Verify MX"}
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
