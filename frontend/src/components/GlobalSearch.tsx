"use client";

import React, { useState, useEffect, useRef } from "react";
import { Search, Building2, Users, Send, CheckSquare, X } from "lucide-react";
import { apiFetch } from "@/lib/api";
import Link from "next/link";

interface SearchResult {
  type: "company" | "contact" | "campaign" | "task";
  id: number;
  title: string;
  subtitle: string;
  link: string;
}

export function GlobalSearchModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
    } else {
      setQuery("");
      setResults([]);
    }
  }, [isOpen]);

  useEffect(() => {
    if (query.trim().length < 2) {
      setResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await apiFetch<SearchResult[]>(`/search?q=${encodeURIComponent(query)}`);
        setResults(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }, 250);
    return () => clearTimeout(timer);
  }, [query]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 bg-slate-900/40 backdrop-blur-sm">
      <div className="w-full max-w-xl bg-white rounded-lg shadow-xl border border-slate-200 overflow-hidden">
        <div className="flex items-center px-4 py-3 border-b border-slate-200 gap-3">
          <Search className="w-5 h-5 text-slate-400" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Search leads, companies, contacts, campaigns, tasks..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full text-sm text-slate-900 bg-transparent outline-none placeholder:text-slate-400"
          />
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-600 rounded">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="max-h-80 overflow-y-auto p-2">
          {loading && <div className="py-6 text-center text-xs text-slate-400">Searching platform records...</div>}
          {!loading && query.length >= 2 && results.length === 0 && (
            <div className="py-6 text-center text-xs text-slate-400">No matching records found.</div>
          )}
          {!loading && results.length > 0 && (
            <div className="space-y-1">
              {results.map((item, idx) => (
                <Link
                  key={idx}
                  href={item.link}
                  onClick={onClose}
                  className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-slate-50 transition text-left group"
                >
                  <div className="p-2 rounded bg-slate-100 text-slate-600 group-hover:bg-blue-50 group-hover:text-blue-600">
                    {item.type === "company" && <Building2 className="w-4 h-4" />}
                    {item.type === "contact" && <Users className="w-4 h-4" />}
                    {item.type === "campaign" && <Send className="w-4 h-4" />}
                    {item.type === "task" && <CheckSquare className="w-4 h-4" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-semibold text-slate-900 truncate">{item.title}</div>
                    <div className="text-[11px] text-slate-500 truncate">{item.subtitle}</div>
                  </div>
                  <span className="text-[10px] uppercase font-semibold text-slate-400 bg-slate-100 px-2 py-0.5 rounded">
                    {item.type}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </div>

        <div className="px-4 py-2 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-[11px] text-slate-500">
          <span>Navigate with arrow keys</span>
          <span>ESC to close</span>
        </div>
      </div>
    </div>
  );
}
