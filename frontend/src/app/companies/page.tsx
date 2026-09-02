"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Building2, Globe, ExternalLink, Phone, Mail, Search, Layers, ShieldCheck } from "lucide-react";
import { Company } from "@/types";
import { apiFetch } from "@/lib/api";

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);

  const fetchCompanies = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiFetch<Company[]>(`/companies?search=${encodeURIComponent(search)}`);
      setCompanies(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    fetchCompanies();
  }, [fetchCompanies]);

  return (
    <div className="space-y-4 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Company Directory & Provenance</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Unified business records merged across multiple public sources with complete origin history.
        </p>
      </div>

      {/* Search Toolbar */}
      <div className="p-3 bg-white rounded-lg border border-slate-200 shadow-xs flex items-center gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
          <input
            type="text"
            placeholder="Search company name, industry, domain, location..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 rounded border border-slate-200 text-xs bg-slate-50 outline-none focus:border-blue-500"
          />
        </div>
      </div>

      {/* Companies Table */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-xs overflow-hidden">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50 text-slate-500 font-bold uppercase tracking-wider text-[10px]">
              <th className="p-3">Company Name</th>
              <th className="p-3">Industry</th>
              <th className="p-3">City / Region</th>
              <th className="p-3">Website</th>
              <th className="p-3">Primary Source</th>
              <th className="p-3">Multi-Source Records</th>
              <th className="p-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-700">
            {loading ? (
              <tr>
                <td colSpan={7} className="p-10 text-center text-slate-400 text-xs">
                  Loading company records...
                </td>
              </tr>
            ) : companies.length === 0 ? (
              <tr>
                <td colSpan={7} className="p-10 text-center text-slate-400 text-xs">
                  No company records found.
                </td>
              </tr>
            ) : (
              companies.map((c) => (
                <tr key={c.id} className="hover:bg-slate-50 transition">
                  <td className="p-3 font-bold text-slate-900">{c.business_name}</td>
                  <td className="p-3 text-slate-600">{c.industry || "—"}</td>
                  <td className="p-3 text-slate-600">{c.city || "—"}, {c.country || "India"}</td>
                  <td className="p-3">
                    {c.website ? (
                      <a
                        href={c.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline flex items-center gap-1 font-mono text-[11px]"
                      >
                        <span>{c.domain || c.website}</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    ) : (
                      <span className="text-slate-400">—</span>
                    )}
                  </td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-medium text-[11px]">
                      {c.source}
                    </span>
                  </td>
                  <td className="p-3">
                    <span className="font-bold text-blue-700">
                      {c.source_records?.length || 1} sources
                    </span>
                  </td>
                  <td className="p-3 text-right">
                    <button
                      onClick={() => setSelectedCompany(c)}
                      className="px-2.5 py-1 text-xs font-medium text-blue-600 hover:bg-blue-50 rounded"
                    >
                      View Provenance
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Provenance Drawer/Modal */}
      {selectedCompany && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
          <div className="w-full max-w-lg bg-white rounded-lg shadow-xl border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="font-bold text-sm text-slate-900">{selectedCompany.business_name}</h3>
                <div className="text-xs text-slate-500">Multi-Source Provenance & Audit Trail</div>
              </div>
              <button onClick={() => setSelectedCompany(null)} className="p-1 text-slate-400 hover:text-slate-600">
                ✕
              </button>
            </div>

            <div className="space-y-2">
              <div className="text-xs font-bold text-slate-700">Discovered Source Records:</div>
              {selectedCompany.source_records?.map((sr, i) => (
                <div key={i} className="p-3 rounded-md bg-slate-50 border border-slate-200 text-xs space-y-1">
                  <div className="flex items-center justify-between font-semibold text-slate-900">
                    <span>Source: {sr.source_name}</span>
                    <span className="text-[10px] text-slate-400">{new Date(sr.collected_at).toLocaleDateString()}</span>
                  </div>
                  {sr.source_url && (
                    <a href={sr.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline block truncate text-[11px]">
                      {sr.source_url}
                    </a>
                  )}
                  <div className="text-[10px] text-slate-500">Confidence: {Math.round(sr.confidence * 100)}%</div>
                </div>
              ))}
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedCompany(null)}
                className="px-4 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
