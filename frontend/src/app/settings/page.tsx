"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Settings, Sparkles, Mail, Shield, CheckCircle2, AlertCircle, RefreshCw, Trash2, ShieldAlert, ShieldCheck } from "lucide-react";
import { apiFetch } from "@/lib/api";

function SettingsContent() {
  const searchParams = useSearchParams();
  const tabParam = searchParams.get("tab") as "ai" | "smtp" | "scoring" | "sources" | "admin" | null;
  const [activeTab, setActiveTab] = useState<"ai" | "smtp" | "scoring" | "sources" | "admin">(tabParam || "ai");

  useEffect(() => {
    if (tabParam && ["ai", "smtp", "scoring", "sources", "admin"].includes(tabParam)) {
      setActiveTab(tabParam);
    }
  }, [tabParam]);
  const [aiSettings, setAiSettings] = useState<any>(null);
  const [smtpSettings, setSmtpSettings] = useState<any>(null);
  const [sourceCoverage, setSourceCoverage] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);
  const [testing, setTesting] = useState(false);

  // SMTP Settings State
  const [smtpSaving, setSmtpSaving] = useState(false);
  const [smtpTesting, setSmtpTesting] = useState(false);
  const [smtpTestResult, setSmtpTestResult] = useState<any>(null);

  // Admin Reset State
  const [resetting, setResetting] = useState(false);
  const [resetResult, setResetResult] = useState<any>(null);

  useEffect(() => {
    Promise.all([
      apiFetch("/settings/ai"),
      apiFetch("/settings/smtp"),
      apiFetch("/analytics/source-coverage")
    ])
      .then(([aiData, smtpData, srcData]) => {
        setAiSettings(aiData);
        setSmtpSettings(smtpData);
        setSourceCoverage(srcData || []);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleSaveAI = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await apiFetch("/settings/ai", {
        method: "POST",
        body: JSON.stringify(aiSettings)
      });
      alert("AI settings saved successfully!");
    } catch (err) {
      alert("Failed to save: " + err);
    } finally {
      setSaving(false);
    }
  };

  const handleTestAI = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await apiFetch("/settings/ai/test", { method: "POST" });
      setTestResult(res);
    } catch (err: any) {
      setTestResult({ status: "ERROR", error: err.message });
    } finally {
      setTesting(false);
    }
  };

  const handleSaveSMTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setSmtpSaving(true);
    try {
      await apiFetch("/settings/smtp", {
        method: "POST",
        body: JSON.stringify(smtpSettings)
      });
      alert("SMTP settings saved successfully!");
    } catch (err) {
      alert("Failed to save SMTP settings: " + err);
    } finally {
      setSmtpSaving(false);
    }
  };

  const handleTestSMTP = async () => {
    setSmtpTesting(true);
    setSmtpTestResult(null);
    try {
      const res = await apiFetch("/settings/smtp/test", {
        method: "POST",
        body: JSON.stringify({ host: smtpSettings.smtp_host })
      });
      setSmtpTestResult(res);
    } catch (err: any) {
      setSmtpTestResult({ status: "ERROR", message: err.message });
    } finally {
      setSmtpTesting(false);
    }
  };

  const handleResetDemoData = async () => {
    if (!confirm("Are you sure you want to purge all demo/lead/discovery data? Users, organizations, and configuration settings will be preserved.")) {
      return;
    }
    setResetting(true);
    setResetResult(null);
    try {
      const res = await apiFetch("/admin/data/reset-demo", {
        method: "POST",
        body: JSON.stringify({ confirm: true })
      });
      setResetResult(res);
      alert("All demo leads, companies, and mock audits have been safely reset!");
    } catch (err: any) {
      alert("Reset failed: " + err.message);
    } finally {
      setResetting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Platform Settings & Administration</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Configure AI inference providers, SMTP email dispatch, deterministic scoring weights, and manage production data.
        </p>
      </div>

      {/* Tabs Header */}
      <div className="flex border-b border-slate-200 gap-6 text-xs font-semibold overflow-x-auto">
        {[
          { id: "ai", label: "AI Intelligence & Live Search", icon: Sparkles },
          { id: "smtp", label: "Email Accounts & SMTP", icon: Mail },
          { id: "scoring", label: "Lead Scoring Rules", icon: Shield },
          { id: "sources", label: "Source Coverage Dashboard", icon: ShieldCheck },
          { id: "admin", label: "Admin & Data Reset", icon: ShieldAlert },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-3 flex items-center gap-2 border-b-2 transition ${
                isActive ? "border-blue-600 text-blue-600 font-bold" : "border-transparent text-slate-500 hover:text-slate-800"
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Body */}
      {loading ? (
        <div className="py-12 text-center text-xs text-slate-400">Loading settings...</div>
      ) : (
        <div className="p-6 bg-white rounded-lg border border-slate-200 shadow-xs">
          {/* AI SETTINGS */}
          {activeTab === "ai" && aiSettings && (
            <form onSubmit={handleSaveAI} className="space-y-6 text-xs">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div>
                  <h2 className="font-bold text-sm text-slate-900">Real-Time AI & Executive Search Engines</h2>
                  <p className="text-[11px] text-slate-500">
                    Configure Perplexity AI (live web citations) and Google Gemini (search grounding) for real-time lead discovery and verified LinkedIn hunting.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleTestAI}
                  disabled={testing}
                  className="px-3 py-1.5 rounded bg-blue-50 text-blue-700 font-semibold border border-blue-200 hover:bg-blue-100 transition flex items-center gap-1.5"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${testing ? "animate-spin" : ""}`} />
                  <span>{testing ? "Testing Engines..." : "Test AI Connections"}</span>
                </button>
              </div>

              {testResult && (
                <div className={`p-3 rounded border flex items-center gap-2 ${
                  testResult.status === "CONNECTED" || testResult.status === "HEALTHY" || testResult.active_ai_provider
                    ? "bg-emerald-50 border-emerald-200 text-emerald-800"
                    : "bg-amber-50 border-amber-200 text-amber-800"
                }`}>
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  <div>
                    <div className="font-bold">Engine Status: {testResult.active_ai_provider || testResult.status || "READY"}</div>
                    <div className="text-[11px]">
                      {testResult.message || `Active Engine: ${testResult.active_ai_provider || 'Configured'}. Search Provider: ${testResult.active_search_provider || 'Live'}.`}
                    </div>
                  </div>
                </div>
              )}

              {/* Provider Selection & Routing */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-3 bg-slate-50 rounded-lg border border-slate-200">
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Active AI Outreach & Reasoning Engine:</label>
                  <select
                    value={aiSettings.active_ai_provider || "auto"}
                    onChange={(e) => setAiSettings({ ...aiSettings, active_ai_provider: e.target.value })}
                    className="w-full px-3 py-1.5 rounded border border-slate-300 bg-white outline-none font-medium"
                  >
                    <option value="auto">Auto (Cascading: Perplexity → Gemini → Hugging Face)</option>
                    <option value="perplexity">Perplexity AI (Sonar / Sonar-Pro)</option>
                    <option value="gemini">Google Gemini (Gemini 2.0 Flash)</option>
                    <option value="huggingface">Hugging Face Serverless Inference</option>
                  </select>
                  <div className="text-[10px] text-slate-400 mt-1">Selects primary LLM for qualification, cold email synthesis, and reply classification.</div>
                </div>

                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Active Live Web Search Provider:</label>
                  <select
                    value={aiSettings.ai_search_provider || "auto"}
                    onChange={(e) => setAiSettings({ ...aiSettings, ai_search_provider: e.target.value })}
                    className="w-full px-3 py-1.5 rounded border border-slate-300 bg-white outline-none font-medium"
                  >
                    <option value="auto">Auto (Perplexity Sonar / Gemini Grounding / Fallback)</option>
                    <option value="perplexity">Perplexity AI (Real-time Live Web Citations)</option>
                    <option value="gemini">Google Gemini (Google Search Grounding)</option>
                  </select>
                  <div className="text-[10px] text-slate-400 mt-1">Powers real-time business discovery, executive LinkedIn matching, and domain intelligence.</div>
                </div>
              </div>

              {/* Engine 1: Perplexity AI Card */}
              <div className="p-4 rounded-lg border border-slate-200 bg-white space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-800">PERPLEXITY AI</span>
                    <span className="font-bold text-slate-800 text-xs">Sonar Real-Time Web Engine</span>
                  </div>
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${aiSettings.perplexity_configured ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-500"}`}>
                    {aiSettings.perplexity_configured ? "Configured" : "Not Configured"}
                  </span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-slate-600 font-medium mb-1">Perplexity API Key:</label>
                    <input
                      type="password"
                      placeholder={aiSettings.perplexity_configured ? "••••••••••••••••" : "pplx-..."}
                      value={aiSettings.perplexity_api_key || ""}
                      onChange={(e) => setAiSettings({ ...aiSettings, perplexity_api_key: e.target.value })}
                      className="w-full px-3 py-1.5 rounded border border-slate-300 outline-none font-mono text-xs"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-600 font-medium mb-1">Perplexity Model:</label>
                    <select
                      value={aiSettings.perplexity_model || "sonar"}
                      onChange={(e) => setAiSettings({ ...aiSettings, perplexity_model: e.target.value })}
                      className="w-full px-3 py-1.5 rounded border border-slate-300 bg-white outline-none font-mono text-xs"
                    >
                      <option value="sonar">sonar (Fast Real-time Web Search)</option>
                      <option value="sonar-pro">sonar-pro (High-Precision Deep Research)</option>
                      <option value="sonar-reasoning">sonar-reasoning (Complex Reasoning + Search)</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Engine 2: Google Gemini Card */}
              <div className="p-4 rounded-lg border border-slate-200 bg-white space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800">GOOGLE GEMINI</span>
                    <span className="font-bold text-slate-800 text-xs">Gemini 2.0 Flash + Search Grounding</span>
                  </div>
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${aiSettings.gemini_configured ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-500"}`}>
                    {aiSettings.gemini_configured ? "Configured" : "Not Configured"}
                  </span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-slate-600 font-medium mb-1">Gemini API Key:</label>
                    <input
                      type="password"
                      placeholder={aiSettings.gemini_configured ? "••••••••••••••••" : "AIzaSy..."}
                      value={aiSettings.gemini_api_key || ""}
                      onChange={(e) => setAiSettings({ ...aiSettings, gemini_api_key: e.target.value })}
                      className="w-full px-3 py-1.5 rounded border border-slate-300 outline-none font-mono text-xs"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-600 font-medium mb-1">Gemini Model:</label>
                    <select
                      value={aiSettings.gemini_model || "gemini-2.0-flash"}
                      onChange={(e) => setAiSettings({ ...aiSettings, gemini_model: e.target.value })}
                      className="w-full px-3 py-1.5 rounded border border-slate-300 bg-white outline-none font-mono text-xs"
                    >
                      <option value="gemini-2.0-flash">gemini-2.0-flash (Ultra-fast Search Grounding)</option>
                      <option value="gemini-1.5-pro">gemini-1.5-pro (Deep Document Reasoning)</option>
                      <option value="gemini-1.5-flash">gemini-1.5-flash (Standard Grounded)</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Engine 3: Hugging Face Multi-Model Suite Card */}
              <div className="p-4 rounded-xl border border-slate-200 bg-white space-y-4 shadow-2xs">
                <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800">HUGGING FACE</span>
                    <span className="font-bold text-slate-800 text-xs">Multi-Model Specialized Ensemble Suite</span>
                  </div>
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${aiSettings.hf_configured ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-500"}`}>
                    {aiSettings.hf_configured ? "Active & Configured" : "Not Configured"}
                  </span>
                </div>

                <div className="p-3 bg-amber-50/60 rounded-lg border border-amber-200/70 text-[11px] text-amber-900">
                  <span className="font-bold">Multi-Model Architecture:</span> LeadForge routes each pipeline step to a specialized open-source model optimized for copywriting, code auditing, or sentiment classification.
                </div>

                {/* Master API Token */}
                <div>
                  <label className="block text-slate-600 font-medium mb-1">Hugging Face User Access Token (HF_TOKEN):</label>
                  <input
                    type="password"
                    placeholder={aiSettings.hf_configured ? "••••••••••••••••" : "hf_..."}
                    value={aiSettings.hf_token || ""}
                    onChange={(e) => setAiSettings({ ...aiSettings, hf_token: e.target.value })}
                    className="w-full px-3 py-1.5 rounded border border-slate-300 outline-none font-mono text-xs focus:border-amber-500"
                  />
                  <div className="text-[10px] text-slate-400 mt-0.5">Applies to all configured Hugging Face serverless inference endpoints.</div>
                </div>

                {/* 4 Specialized Model Slots Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                  {/* Model 1: Outreach */}
                  <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 space-y-1.5">
                    <div className="font-bold text-slate-800 flex items-center justify-between">
                      <span>✍️ 1. Cold Outreach Copywriter</span>
                      <span className="text-[9px] px-1.5 py-0.2 rounded bg-blue-100 text-blue-800 font-mono">Outreach</span>
                    </div>
                    <input
                      type="text"
                      placeholder="e.g. mistralai/Mistral-7B-Instruct-v0.3"
                      value={aiSettings.hf_outreach_model || "mistralai/Mistral-7B-Instruct-v0.3"}
                      onChange={(e) => setAiSettings({ ...aiSettings, hf_outreach_model: e.target.value })}
                      className="w-full px-2.5 py-1.5 rounded border border-slate-300 outline-none font-mono text-[11px] bg-white"
                    />
                    <div className="text-[10px] text-slate-400">Recommended: mistralai/Mistral-7B-Instruct-v0.3 or meta-llama/Meta-Llama-3-8B-Instruct</div>
                  </div>

                  {/* Model 2: Technical Audit */}
                  <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 space-y-1.5">
                    <div className="font-bold text-slate-800 flex items-center justify-between">
                      <span>🔍 2. Technical Audit & Defect Analyst</span>
                      <span className="text-[9px] px-1.5 py-0.2 rounded bg-purple-100 text-purple-800 font-mono">Code / CWV</span>
                    </div>
                    <input
                      type="text"
                      placeholder="e.g. Qwen/Qwen2.5-Coder-7B-Instruct"
                      value={aiSettings.hf_audit_model || "Qwen/Qwen2.5-Coder-7B-Instruct"}
                      onChange={(e) => setAiSettings({ ...aiSettings, hf_audit_model: e.target.value })}
                      className="w-full px-2.5 py-1.5 rounded border border-slate-300 outline-none font-mono text-[11px] bg-white"
                    />
                    <div className="text-[10px] text-slate-400">Recommended: Qwen/Qwen2.5-Coder-7B-Instruct or deepseek-ai/DeepSeek-R1-Distill-Qwen-7B</div>
                  </div>

                  {/* Model 3: Sentiment & Reply */}
                  <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 space-y-1.5">
                    <div className="font-bold text-slate-800 flex items-center justify-between">
                      <span>💬 3. Reply Sentiment & Intent Classifier</span>
                      <span className="text-[9px] px-1.5 py-0.2 rounded bg-emerald-100 text-emerald-800 font-mono">Classifier</span>
                    </div>
                    <input
                      type="text"
                      placeholder="e.g. meta-llama/Meta-Llama-3-8B-Instruct"
                      value={aiSettings.hf_classification_model || "meta-llama/Meta-Llama-3-8B-Instruct"}
                      onChange={(e) => setAiSettings({ ...aiSettings, hf_classification_model: e.target.value })}
                      className="w-full px-2.5 py-1.5 rounded border border-slate-300 outline-none font-mono text-[11px] bg-white"
                    />
                    <div className="text-[10px] text-slate-400">Recommended: meta-llama/Meta-Llama-3-8B-Instruct or RoBERTa</div>
                  </div>

                  {/* Model 4: NLP Extraction */}
                  <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 space-y-1.5">
                    <div className="font-bold text-slate-800 flex items-center justify-between">
                      <span>🧠 4. NLP Query & Entity Mining</span>
                      <span className="text-[9px] px-1.5 py-0.2 rounded bg-indigo-100 text-indigo-800 font-mono">Extraction</span>
                    </div>
                    <input
                      type="text"
                      placeholder="e.g. meta-llama/Meta-Llama-3-8B-Instruct"
                      value={aiSettings.hf_extraction_model || "meta-llama/Meta-Llama-3-8B-Instruct"}
                      onChange={(e) => setAiSettings({ ...aiSettings, hf_extraction_model: e.target.value })}
                      className="w-full px-2.5 py-1.5 rounded border border-slate-300 outline-none font-mono text-[11px] bg-white"
                    />
                    <div className="text-[10px] text-slate-400">Recommended: meta-llama/Meta-Llama-3-8B-Instruct or Mistral-7B</div>
                  </div>
                </div>
              </div>

              {/* Model Hyperparameters */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                <div>
                  <label className="block text-slate-600 font-medium mb-1">
                    Temperature: <span className="font-bold text-slate-800">{aiSettings.temperature}</span>
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={aiSettings.temperature}
                    onChange={(e) => setAiSettings({ ...aiSettings, temperature: parseFloat(e.target.value) })}
                    className="w-full accent-blue-600"
                  />
                  <div className="text-[10px] text-slate-400">Low temperature (0.1-0.3) enforces factual evidence adherence & eliminates hallucinations</div>
                </div>

                <div>
                  <label className="block text-slate-600 font-medium mb-1">Max Output Tokens:</label>
                  <input
                    type="number"
                    value={aiSettings.max_tokens}
                    onChange={(e) => setAiSettings({ ...aiSettings, max_tokens: parseInt(e.target.value) })}
                    className="w-full px-3 py-1.5 rounded border border-slate-300 outline-none"
                  />
                </div>
              </div>

              {/* Toggles */}
              <div className="pt-3 border-t border-slate-100 space-y-2">
                <div className="font-bold text-slate-700">AI Task Triggers:</div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={aiSettings.enable_ai_search_discovery !== false}
                    onChange={(e) => setAiSettings({ ...aiSettings, enable_ai_search_discovery: e.target.checked })}
                    className="rounded border-slate-300 text-blue-600 focus:ring-0"
                  />
                  <span>Enable Live Grounded AI Search & Executive LinkedIn Discovery</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={aiSettings.enable_ai_analysis}
                    onChange={(e) => setAiSettings({ ...aiSettings, enable_ai_analysis: e.target.checked })}
                    className="rounded border-slate-300 text-blue-600 focus:ring-0"
                  />
                  <span>Enable AI Lead Scoring Justification & Opportunity Interpretation</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={aiSettings.enable_ai_email_gen}
                    onChange={(e) => setAiSettings({ ...aiSettings, enable_ai_email_gen: e.target.checked })}
                    className="rounded border-slate-300 text-blue-600 focus:ring-0"
                  />
                  <span>Enable AI Evidence-Based Cold Email Outreach Generator</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={aiSettings.enable_ai_reply_classification}
                    onChange={(e) => setAiSettings({ ...aiSettings, enable_ai_reply_classification: e.target.checked })}
                    className="rounded border-slate-300 text-blue-600 focus:ring-0"
                  />
                  <span>Enable Automated AI Inbound Reply Sentiment Classifier</span>
                </label>
              </div>

              <div className="flex justify-end pt-3 border-t border-slate-100">
                <button
                  type="submit"
                  disabled={saving}
                  className="px-4 py-1.5 bg-blue-600 text-white rounded font-semibold hover:bg-blue-700 disabled:opacity-50"
                >
                  {saving ? "Saving..." : "Save AI Configuration"}
                </button>
              </div>
            </form>
          )}

          {/* SMTP SETTINGS */}
          {activeTab === "smtp" && smtpSettings && (
            <form onSubmit={handleSaveSMTP} className="space-y-4 text-xs">
              <div className="border-b border-slate-100 pb-3 flex items-center justify-between">
                <div>
                  <h2 className="font-bold text-sm text-slate-900">Outreach Email Account (SMTP)</h2>
                  <p className="text-[11px] text-slate-500">
                    Configure the outbound SMTP server for scheduled sequence outreach.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleTestSMTP}
                  disabled={smtpTesting}
                  className="px-3 py-1.5 border border-slate-300 rounded font-semibold text-slate-700 hover:bg-slate-50 flex items-center gap-1.5"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${smtpTesting ? "animate-spin" : ""}`} />
                  {smtpTesting ? "Testing..." : "Test Connection"}
                </button>
              </div>

              {smtpTestResult && (
                <div className={`p-3 rounded border text-xs flex items-center gap-2 ${
                  smtpTestResult.status === "SUCCESS" ? "bg-emerald-50 text-emerald-800 border-emerald-200" : "bg-rose-50 text-rose-800 border-rose-200"
                }`}>
                  {smtpTestResult.status === "SUCCESS" ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
                  )}
                  <span>{smtpTestResult.message || (smtpTestResult.status === "SUCCESS" ? "SMTP connection verified!" : "Connection test failed.")}</span>
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-slate-600 font-medium mb-1">SMTP Server Host:</label>
                  <input
                    type="text"
                    value={smtpSettings.smtp_host || ""}
                    onChange={(e) => setSmtpSettings({ ...smtpSettings, smtp_host: e.target.value })}
                    className="w-full px-3 py-1.5 rounded border border-slate-300 outline-none focus:border-blue-500"
                    placeholder="smtp.gmail.com"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 font-medium mb-1">Port:</label>
                  <input
                    type="number"
                    value={smtpSettings.smtp_port || 587}
                    onChange={(e) => setSmtpSettings({ ...smtpSettings, smtp_port: parseInt(e.target.value) || 587 })}
                    className="w-full px-3 py-1.5 rounded border border-slate-300 outline-none focus:border-blue-500"
                    placeholder="587"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 font-medium mb-1">From Email Address:</label>
                  <input
                    type="email"
                    value={smtpSettings.smtp_from_email || ""}
                    onChange={(e) => setSmtpSettings({ ...smtpSettings, smtp_from_email: e.target.value })}
                    className="w-full px-3 py-1.5 rounded border border-slate-300 outline-none focus:border-blue-500"
                    placeholder="prospecting@leadforge.io"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 font-medium mb-1">Sender Name:</label>
                  <input
                    type="text"
                    value={smtpSettings.smtp_from_name || ""}
                    onChange={(e) => setSmtpSettings({ ...smtpSettings, smtp_from_name: e.target.value })}
                    className="w-full px-3 py-1.5 rounded border border-slate-300 outline-none focus:border-blue-500"
                    placeholder="LeadForge Outreach"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2 pt-2">
                <input
                  type="checkbox"
                  id="smtp_use_tls"
                  checked={smtpSettings.use_tls ?? true}
                  onChange={(e) => setSmtpSettings({ ...smtpSettings, use_tls: e.target.checked })}
                  className="rounded text-blue-600"
                />
                <label htmlFor="smtp_use_tls" className="text-slate-700 font-medium">Use TLS Encryption</label>
              </div>

              <div className="p-3 bg-blue-50 text-blue-800 rounded border border-blue-200">
                <span className="font-bold">Development Mode:</span> If SMTP credentials are left empty, LeadForge runs in safe local delivery simulation mode.
              </div>

              <div className="flex justify-end pt-3 border-t border-slate-100">
                <button
                  type="submit"
                  disabled={smtpSaving}
                  className="px-4 py-1.5 bg-blue-600 text-white rounded font-semibold hover:bg-blue-700 disabled:opacity-50"
                >
                  {smtpSaving ? "Saving..." : "Save SMTP Configuration"}
                </button>
              </div>
            </form>
          )}

          {/* SCORING RULES */}
          {activeTab === "scoring" && (
            <div className="space-y-4 text-xs">
              <div className="border-b border-slate-100 pb-3">
                <h2 className="font-bold text-sm text-slate-900">Deterministic Lead Scoring Weights</h2>
                <p className="text-[11px] text-slate-500">
                  Custom rules that map technical deficiencies directly to 0-100 prospect urgency scores.
                </p>
              </div>

              <div className="space-y-2">
                {[
                  { rule: "No Website Detected", points: "+25 pts", desc: "No active domain or website found" },
                  { rule: "Poor Mobile Experience", points: "+15 pts", desc: "Mobile health score is under 60/100" },
                  { rule: "Slow Performance / Page Speed", points: "+10 pts", desc: "Response time > 3000ms or page payload > 3MB" },
                  { rule: "SEO Deficiencies", points: "+10 pts", desc: "Missing page title, H1 or meta descriptions" },
                  { rule: "Missing Call-to-Action / Booking Flow", points: "+10 pts", desc: "No booking form or prominent CTA" },
                  { rule: "Direct Business Email Discovered", points: "+10 pts", desc: "Valid corporate email found on official site" },
                  { rule: "Fresh Data Verification", points: "+5 pts", desc: "Discovered and checked within 7 days" },
                  { rule: "Modern High-Performance Site", points: "-20 pts", desc: "Site is fast, responsive and well optimized" },
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 rounded-md bg-slate-50 border border-slate-200">
                    <div>
                      <div className="font-bold text-slate-900">{item.rule}</div>
                      <div className="text-[11px] text-slate-500">{item.desc}</div>
                    </div>
                    <span className={`font-mono font-bold px-2 py-0.5 rounded text-xs ${
                      item.points.startsWith("+") ? "bg-blue-100 text-blue-800" : "bg-slate-200 text-slate-700"
                    }`}>
                      {item.points}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* SOURCE COVERAGE DASHBOARD TAB */}
          {activeTab === "sources" && (
            <div className="space-y-5 text-xs">
              <div className="border-b border-slate-100 pb-3 flex items-center justify-between">
                <div>
                  <h2 className="font-bold text-sm text-slate-900">Public Lead Source Coverage & Adapter Health</h2>
                  <p className="text-[11px] text-slate-500">
                    Live operational health, rate limit enforcement, and yield metrics for permitted public sources.
                  </p>
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                  Zero Scraping Claims • Exact Coverage
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-200 text-[10px] text-slate-500 uppercase bg-slate-50">
                      <th className="p-2.5 font-semibold">Source Adapter</th>
                      <th className="p-2.5 font-semibold">Status</th>
                      <th className="p-2.5 font-semibold">Discovered</th>
                      <th className="p-2.5 font-semibold">Accepted</th>
                      <th className="p-2.5 font-semibold">Duplicates</th>
                      <th className="p-2.5 font-semibold">Websites</th>
                      <th className="p-2.5 font-semibold">Verified</th>
                      <th className="p-2.5 font-semibold">Contacts</th>
                      <th className="p-2.5 font-semibold">Rate Limit</th>
                      <th className="p-2.5 font-semibold">Last Success</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {sourceCoverage.map((src, idx) => (
                      <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                        <td className="p-2.5 font-bold text-slate-900">{src.source}</td>
                        <td className="p-2.5">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            src.status === "OPERATIONAL" ? "bg-emerald-100 text-emerald-800" : "bg-slate-100 text-slate-600"
                          }`}>
                            {src.status}
                          </span>
                        </td>
                        <td className="p-2.5 font-mono font-semibold text-slate-800">{src.records_discovered}</td>
                        <td className="p-2.5 font-mono text-emerald-700 font-semibold">{src.records_accepted}</td>
                        <td className="p-2.5 font-mono text-slate-500">{src.duplicates}</td>
                        <td className="p-2.5 font-mono text-slate-700">{src.websites_found}</td>
                        <td className="p-2.5 font-mono text-purple-700 font-semibold">{src.websites_verified}</td>
                        <td className="p-2.5 font-mono text-amber-700 font-semibold">{src.contacts_found}</td>
                        <td className="p-2.5 font-mono text-slate-500">{src.rate_limit}</td>
                        <td className="p-2.5 text-slate-500 text-[11px]">
                          {src.last_successful_run ? new Date(src.last_successful_run).toLocaleDateString() : "Active"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ADMIN & DATA RESET TAB */}
          {activeTab === "admin" && (
            <div className="space-y-5 text-xs">
              <div className="border-b border-slate-100 pb-3">
                <h2 className="font-bold text-sm text-slate-900">Production Data Management & Reset</h2>
                <p className="text-[11px] text-slate-500">
                  Safely reset all mock leads, companies, and discovery audits to prepare the workspace for real global discovery.
                </p>
              </div>

              <div className="p-4 rounded-lg bg-rose-50 border border-rose-200 text-rose-900 space-y-3">
                <div className="flex items-center gap-2 font-bold text-sm text-rose-800">
                  <AlertCircle className="w-4 h-4 text-rose-600" />
                  <span>Purge Lead & Discovery Data</span>
                </div>
                <p className="text-xs text-rose-700 leading-relaxed">
                  This action completely clears all companies, contacts, website audits, lead scores, opportunities, discovery jobs, and campaigns.
                  <br />
                  <strong>Preserved:</strong> Admin users, organization credentials, authentication tokens, and source configuration.
                </p>
                <div className="pt-2">
                  <button
                    type="button"
                    onClick={handleResetDemoData}
                    disabled={resetting}
                    className="flex items-center gap-1.5 px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded font-bold shadow-xs transition disabled:opacity-50"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    <span>{resetting ? "Resetting Data..." : "Reset All Lead & Demo Data"}</span>
                  </button>
                </div>
              </div>

              {resetResult && (
                <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded">
                  <div className="font-bold">Reset Status: {resetResult.status}</div>
                  <div className="text-[11px]">{resetResult.message}</div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function SettingsPage() {
  return (
    <Suspense fallback={<div className="py-12 text-center text-xs text-slate-400">Loading settings...</div>}>
      <SettingsContent />
    </Suspense>
  );
}

