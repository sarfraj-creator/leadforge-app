"use client";

import React, { useState, useEffect } from "react";
import {
  Compass,
  Play,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Layers,
  MapPin,
  Building2,
  Sliders,
  Flame,
  Globe,
  Users,
  Activity,
  ShieldCheck,
  Zap,
  Search,
  ExternalLink,
  MessageSquare,
  UserCheck,
  ArrowRight,
  TrendingUp,
  Share2
} from "lucide-react";
import { DiscoveryJob } from "@/types";
import { apiFetch } from "@/lib/api";

export default function DiscoveryPage() {
  const [mainTab, setMainTab] = useState<"CAMPAIGNS" | "INTENT_HUNTER">("CAMPAIGNS");
  const [jobs, setJobs] = useState<DiscoveryJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [sourceHealth, setSourceHealth] = useState<Record<string, any>>({});
  const [checkingHealth, setCheckingHealth] = useState(false);

  // Geographic Mode & Form State
  const [geoMode, setGeoMode] = useState<"WORLDWIDE" | "COUNTRY" | "REGION" | "CITY" | "BBOX">("WORLDWIDE");
  const [name, setName] = useState("");
  const [location, setLocation] = useState("WORLDWIDE");
  const [industry, setIndustry] = useState("restaurant");
  const [keywords, setKeywords] = useState("");
  const [minScore, setMinScore] = useState(60);
  const [freshnessDays, setFreshnessDays] = useState(7);
  const [maxLeads, setMaxLeads] = useState(100);
  const [selectedSources, setSelectedSources] = useState<string[]>([
    "OpenStreetMap",
    "GoogleMaps",
    "AISearch",
    "SocialIntent"
  ]);

  // Natural Language Search State
  const [nlpQuery, setNlpQuery] = useState("");
  const [interpretingNLP, setInterpretingNLP] = useState(false);
  const [nlpResult, setNlpResult] = useState<any>(null);

  // Active Running Job Polling
  const [activeJobId, setActiveJobId] = useState<number | null>(null);
  const [activeJob, setActiveJob] = useState<DiscoveryJob | null>(null);

  // Social & LinkedIn Intent Post Hunter State
  const [intentKeyword, setIntentKeyword] = useState("wordpress developer");
  const [intentCategory, setIntentCategory] = useState<string>("");
  const [intentPosts, setIntentPosts] = useState<any[]>([]);
  const [loadingIntent, setLoadingIntent] = useState(false);
  const [importingPostId, setImportingPostId] = useState<string | null>(null);
  const [importedIds, setImportedIds] = useState<string[]>([]);

  const fetchSourceHealth = async () => {
    setCheckingHealth(true);
    try {
      const health = await apiFetch<Record<string, any>>("/discovery/sources/health");
      setSourceHealth(health);
    } catch (err) {
      console.error(err);
    } finally {
      setCheckingHealth(false);
    }
  };

  const fetchJobs = async () => {
    try {
      const data = await apiFetch<DiscoveryJob[]>("/discovery/jobs");
      setJobs(data);
      if (data.length > 0 && data[0].status === "RUNNING") {
        setActiveJobId(data[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchIntent = async (kw?: string, cat?: string) => {
    const searchKw = kw !== undefined ? kw : intentKeyword;
    const searchCat = cat !== undefined ? cat : intentCategory;
    setLoadingIntent(true);
    try {
      const url = `/discovery/intent-posts?keyword=${encodeURIComponent(searchKw || "web developer")}` + (searchCat ? `&category=${encodeURIComponent(searchCat)}` : "");
      const res = await apiFetch<any>(url);
      setIntentPosts(res.posts || []);
    } catch (err) {
      console.error("Intent search error:", err);
    } finally {
      setLoadingIntent(false);
    }
  };

  const handleImportIntentPost = async (post: any) => {
    setImportingPostId(post.id);
    try {
      await apiFetch("/discovery/intent-posts/import", {
        method: "POST",
        body: JSON.stringify({
          author_name: post.author_name,
          author_title: post.author_title,
          author_linkedin_url: post.author_linkedin_url,
          company_name: post.company_name,
          post_url: post.post_url,
          post_snippet: post.post_snippet,
          intent_tag: post.intent_tag,
          urgency: post.urgency,
          pitch_hook: post.pitch_hook
        })
      });
      setImportedIds((prev) => [...prev, post.id]);
    } catch (err) {
      alert("Failed to import to CRM: " + err);
    } finally {
      setImportingPostId(null);
    }
  };

  useEffect(() => {
    fetchJobs();
    fetchSourceHealth();
  }, []);

  // Poll active job while running
  useEffect(() => {
    if (!activeJobId) return;
    const interval = setInterval(async () => {
      try {
        const job = await apiFetch<DiscoveryJob>(`/discovery/jobs/${activeJobId}`);
        setActiveJob(job);
        if (job.status === "COMPLETED" || job.status === "FAILED") {
          fetchJobs();
        }
      } catch (err) {
        console.error(err);
      }
    }, 1200);
    return () => clearInterval(interval);
  }, [activeJobId]);

  const handleGeoModeSelect = (mode: "WORLDWIDE" | "COUNTRY" | "REGION" | "CITY" | "BBOX") => {
    setGeoMode(mode);
    if (mode === "WORLDWIDE") setLocation("WORLDWIDE");
    else if (mode === "COUNTRY") setLocation("country:US");
    else if (mode === "REGION") setLocation("region:California");
    else if (mode === "CITY") setLocation("London");
    else if (mode === "BBOX") setLocation("bbox:40.7,-74.0,40.8,-73.9");
  };

  const handleNLPInterpret = async () => {
    if (!nlpQuery.trim()) return;
    setInterpretingNLP(true);
    try {
      const res = await apiFetch("/discovery/nlp-interpret", {
        method: "POST",
        body: JSON.stringify({ query: nlpQuery.trim() })
      });
      const crit = res.interpreted_criteria || {};
      setNlpResult(crit);
      setLocation(crit.location || "WORLDWIDE");
      if (crit.industry) setIndustry(crit.industry);
      if (crit.min_lead_score) setMinScore(crit.min_lead_score);
      if (crit.freshness_days) setFreshnessDays(crit.freshness_days);
      setName(`${crit.industry || "Target"} Leads — ${crit.location || "Worldwide"}`);
    } catch (err) {
      alert("NLP interpretation error: " + err);
    } finally {
      setInterpretingNLP(false);
    }
  };

  const handleStartDiscovery = async (e: React.FormEvent) => {
    e.preventDefault();
    const loc = location.trim() || "WORLDWIDE";
    const campaignName = name.trim() || `${industry.toUpperCase()} Leads — ${loc}`;
    try {
      const created = await apiFetch<DiscoveryJob>("/discovery/campaigns", {
        method: "POST",
        body: JSON.stringify({
          name: campaignName,
          location: loc,
          industry: industry.trim(),
          keywords: keywords.trim(),
          freshness_days: Number(freshnessDays),
          min_lead_score: Number(minScore),
          max_leads: Number(maxLeads),
          sources_used: selectedSources,
          natural_language_query: nlpQuery.trim() || undefined
        })
      });
      setActiveJobId(created.id);
      setActiveJob(created);
      fetchJobs();
    } catch (err) {
      alert("Failed to start discovery campaign: " + err);
    }
  };

  const toggleSource = (src: string) => {
    setSelectedSources((prev) =>
      prev.includes(src) ? prev.filter((s) => s !== src) : [...prev, src]
    );
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header with Navigation Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Real-Time Lead Discovery & Ingestion</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Discover B2B companies, audit websites deterministically, and hunt live buyer-intent requests across LinkedIn and Google.
          </p>
        </div>

        {/* View Switcher Tabs */}
        <div className="flex items-center p-1 bg-slate-200/80 rounded-lg text-xs font-semibold">
          <button
            onClick={() => setMainTab("CAMPAIGNS")}
            className={`px-3.5 py-1.5 rounded-md transition flex items-center gap-1.5 ${
              mainTab === "CAMPAIGNS"
                ? "bg-white text-blue-700 shadow-xs font-bold"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <Compass className="w-3.5 h-3.5 text-blue-600" />
            <span>Multi-Source Campaigns</span>
          </button>
          <button
            onClick={() => {
              setMainTab("INTENT_HUNTER");
              if (intentPosts.length === 0) handleSearchIntent("wordpress developer", "");
            }}
            className={`px-3.5 py-1.5 rounded-md transition flex items-center gap-1.5 ${
              mainTab === "INTENT_HUNTER"
                ? "bg-white text-rose-700 shadow-xs font-bold"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <Flame className="w-3.5 h-3.5 text-rose-600 fill-rose-600" />
            <span>Social Intent & LinkedIn Hunter</span>
            <span className="px-1.5 py-0.2 bg-rose-100 text-rose-700 rounded text-[9px] font-extrabold uppercase">
              Live
            </span>
          </button>
        </div>
      </div>

      {/* ================= SOCIAL INTENT & LINKEDIN POST HUNTER VIEW ================= */}
      {mainTab === "INTENT_HUNTER" && (
        <div className="space-y-6">
          {/* Search Bar & Category Presets */}
          <div className="p-5 bg-white rounded-lg border border-rose-200 shadow-xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
              <div>
                <div className="flex items-center gap-2">
                  <Flame className="w-4 h-4 text-rose-600 fill-rose-600" />
                  <h2 className="text-sm font-bold text-slate-900">
                    Live Buyer Intent & Project Request Prospector
                  </h2>
                </div>
                <p className="text-xs text-slate-500 mt-0.5">
                  Searches live LinkedIn Posts, Twitter/X, and Google Search indexes for decision makers actively requesting web development, redesigns, and digital services.
                </p>
              </div>
              <span className="text-[11px] font-semibold text-rose-700 bg-rose-50 px-2.5 py-1 rounded border border-rose-200 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-rose-600 animate-ping"></span>
                <span>Live Public Index Dorks</span>
              </span>
            </div>

            {/* Keyword Search Input */}
            <div className="flex flex-col sm:flex-row gap-2">
              <div className="relative flex-1">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="text"
                  value={intentKeyword}
                  onChange={(e) => setIntentKeyword(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSearchIntent()}
                  placeholder="e.g. wordpress developer, website redesign, shopify expert, landing page..."
                  className="w-full pl-9 pr-3 py-2 text-xs rounded-md border border-slate-300 text-slate-900 outline-none focus:border-rose-500 focus:ring-1 focus:ring-rose-500"
                />
              </div>
              <button
                onClick={() => handleSearchIntent()}
                disabled={loadingIntent}
                className="px-5 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-md text-xs font-bold flex items-center justify-center gap-1.5 shadow-xs transition"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loadingIntent ? "animate-spin" : ""}`} />
                <span>{loadingIntent ? "Searching Live Web..." : "Hunt Live Intent Posts"}</span>
              </button>
            </div>

            {/* Quick Category Chips */}
            <div className="flex items-center gap-2 overflow-x-auto text-xs pt-1">
              <span className="text-slate-400 text-[11px] font-medium shrink-0">Quick Presets:</span>
              {[
                { id: "wordpress", label: "⚡ WordPress & WooCommerce", kw: "wordpress developer" },
                { id: "redesign", label: "🎨 Website Redesign & UI/UX", kw: "website redesign" },
                { id: "shopify", label: "🛍️ Shopify & E-Commerce", kw: "shopify expert" },
                { id: "custom_web", label: "🚀 React & Custom Web Dev", kw: "web developer" },
                { id: "ui_ux", label: "✨ UI/UX & Landing Pages", kw: "landing page designer" },
                { id: "seo", label: "📈 SEO & Speed Optimization", kw: "website speed optimization" },
              ].map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => {
                    setIntentCategory(cat.id);
                    setIntentKeyword(cat.kw);
                    handleSearchIntent(cat.kw, cat.id);
                  }}
                  className={`px-2.5 py-1 rounded-full border shrink-0 transition text-[11px] font-medium ${
                    intentCategory === cat.id
                      ? "bg-rose-50 border-rose-400 text-rose-800 font-bold"
                      : "bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100"
                  }`}
                >
                  {cat.label}
                </button>
              ))}
            </div>
          </div>

          {/* Intent Post Feed */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Live Intent Signals Found ({intentPosts.length})
              </h3>
              <span className="text-[11px] text-slate-500">
                Sorted by buyer urgency & request relevance
              </span>
            </div>

            {loadingIntent ? (
              <div className="p-12 text-center bg-white rounded-lg border border-slate-200 space-y-3">
                <RefreshCw className="w-6 h-6 text-rose-600 animate-spin mx-auto" />
                <div className="text-xs font-bold text-slate-800">Querying Live LinkedIn, Twitter & Google Indexes...</div>
                <p className="text-[11px] text-slate-400 max-w-sm mx-auto">
                  Parsing author identities, extracting project request quotes, and drafting tailored pitch icebreakers.
                </p>
              </div>
            ) : intentPosts.length === 0 ? (
              <div className="p-10 text-center bg-white rounded-lg border border-slate-200 space-y-2">
                <Flame className="w-8 h-8 text-slate-300 mx-auto" />
                <div className="text-xs font-bold text-slate-700">No Intent Posts Loaded Yet</div>
                <p className="text-[11px] text-slate-400">
                  Select a category above or enter a keyword like <span className="font-semibold text-slate-600">&quot;wordpress developer&quot;</span> to search live posts.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {intentPosts.map((post) => {
                  const isImported = importedIds.includes(post.id);
                  const isImporting = importingPostId === post.id;
                  const initials = post.author_name
                    .split(" ")
                    .map((n: string) => n[0])
                    .join("")
                    .slice(0, 2)
                    .toUpperCase();

                  return (
                    <div
                      key={post.id}
                      className="p-4 bg-white rounded-lg border border-slate-200 hover:border-rose-300 shadow-xs hover:shadow-sm transition flex flex-col justify-between space-y-3.5"
                    >
                      {/* Post Header: Platform, Category & Urgency */}
                      <div className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-800 font-bold font-mono text-[10px]">
                            {post.platform}
                          </span>
                          <span className="text-[11px] font-semibold text-slate-700">
                            {post.intent_tag}
                          </span>
                        </div>
                        <span className={`px-2 py-0.5 rounded font-extrabold text-[10px] tracking-wider uppercase ${
                          post.urgency === "HOT"
                            ? "bg-rose-100 text-rose-800 border border-rose-200"
                            : "bg-amber-100 text-amber-800 border border-amber-200"
                        }`}>
                          {post.urgency === "HOT" ? "🔥 HOT INTENT" : "⚡ HIGH INTENT"}
                        </span>
                      </div>

                      {/* Author Info */}
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-rose-600 to-amber-500 text-white font-bold text-xs flex items-center justify-center shrink-0 shadow-xs">
                          {initials || "DM"}
                        </div>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center justify-between">
                            <h4 className="text-xs font-bold text-slate-900 truncate">
                              {post.author_name}
                            </h4>
                            {post.author_linkedin_url && (
                              <a
                                href={post.author_linkedin_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-[11px] text-blue-600 hover:text-blue-800 flex items-center gap-1 font-semibold"
                              >
                                <span>LinkedIn Profile</span>
                                <ExternalLink className="w-2.5 h-2.5" />
                              </a>
                            )}
                          </div>
                          <div className="text-[11px] text-slate-500 truncate">
                            {post.author_title}
                          </div>
                          {post.company_name && post.company_name !== "Prospective Client" && (
                            <div className="text-[10px] font-semibold text-slate-700 flex items-center gap-1 mt-0.5">
                              <Building2 className="w-2.5 h-2.5 text-slate-400" />
                              <span className="truncate">{post.company_name}</span>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Extracted Post Quote */}
                      <div className="p-2.5 bg-slate-50 rounded-md border border-slate-100 text-xs text-slate-700 italic relative">
                        <div className="text-[10px] uppercase font-bold text-slate-400 not-italic mb-1 flex items-center justify-between">
                          <span>Quoted Request:</span>
                          <a
                            href={post.post_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:underline not-italic font-semibold flex items-center gap-0.5"
                          >
                            <span>View Original Post</span>
                            <ExternalLink className="w-2.5 h-2.5" />
                          </a>
                        </div>
                        &ldquo;{post.post_snippet}&rdquo;
                      </div>

                      {/* AI Suggested Response Pitch */}
                      <div className="p-2.5 bg-rose-50/60 rounded-md border border-rose-100 text-xs space-y-1">
                        <div className="text-[10px] font-bold text-rose-800 flex items-center gap-1">
                          <Sparkles className="w-3 h-3 text-rose-600" />
                          <span>AI Personalized Pitch Hook:</span>
                        </div>
                        <p className="text-[11px] text-rose-950">
                          {post.pitch_hook}
                        </p>
                      </div>

                      {/* Action Button */}
                      <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                        <div className="text-[10px] text-slate-400">
                          Ready for outreach & stage progression
                        </div>
                        <button
                          onClick={() => handleImportIntentPost(post)}
                          disabled={isImported || isImporting}
                          className={`px-3 py-1.5 rounded text-xs font-bold flex items-center gap-1.5 transition ${
                            isImported
                              ? "bg-emerald-100 text-emerald-800 border border-emerald-300 cursor-default"
                              : "bg-slate-900 hover:bg-slate-800 text-white shadow-xs"
                          }`}
                        >
                          {isImporting ? (
                            <>
                              <RefreshCw className="w-3 h-3 animate-spin" />
                              <span>Importing...</span>
                            </>
                          ) : isImported ? (
                            <>
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
                              <span>Imported to CRM!</span>
                            </>
                          ) : (
                            <>
                              <UserCheck className="w-3.5 h-3.5" />
                              <span>Import as Hot Lead</span>
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ================= MULTI-SOURCE DISCOVERY CAMPAIGNS VIEW ================= */}
      {mainTab === "CAMPAIGNS" && (
        <div className="space-y-6">
          {/* Live Source Health & Latency Telemetry */}
          <div className="p-4 bg-white rounded-lg border border-slate-200 shadow-xs space-y-3">
            <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-blue-600" />
                <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Discovery Source Health & Live Latency Status
                </h2>
              </div>
              <button
                onClick={fetchSourceHealth}
                disabled={checkingHealth}
                className="text-[11px] font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1"
              >
                <RefreshCw className={`w-3 h-3 ${checkingHealth ? "animate-spin" : ""}`} />
                <span>Check Health</span>
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
              {[
                { key: "OpenStreetMap", name: "OpenStreetMap (Live POI)", icon: "🗺️" },
                { key: "GoogleMaps", name: "Google Maps & Places", icon: "📍" },
                { key: "AISearch", name: "AI Web Search & LinkedIn", icon: "🤖" },
                { key: "SocialIntent", name: "Social & LinkedIn Intent", icon: "🔥" },
              ].map((src) => {
                const h = sourceHealth[src.key];
                const isAvail = h?.status === "AVAILABLE" || h?.status === "CONNECTED";
                return (
                  <div key={src.key} className="p-3 rounded-md bg-slate-50 border border-slate-200 space-y-1">
                    <div className="flex items-center justify-between font-bold text-slate-900">
                      <span className="flex items-center gap-1.5">
                        <span>{src.icon}</span>
                        <span>{src.name}</span>
                      </span>
                      <span className={`px-1.5 py-0.2 rounded text-[10px] uppercase font-mono ${
                        isAvail ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800"
                      }`}>
                        {h?.status || "CHECKING..."}
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-500 flex items-center justify-between">
                      <span>Latency / Mode:</span>
                      <span className="font-mono font-semibold text-slate-700">{h?.latency_ms ? `${h.latency_ms}ms` : h?.mode || "Live Direct"}</span>
                    </div>
                    <div className="text-[10px] text-slate-400 truncate">
                      {h?.provider || h?.endpoint || "Direct public discovery adapter"}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Live Active Job Progress Monitor */}
          {activeJob && (
            <div className="p-5 bg-white rounded-lg border border-blue-200 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-md bg-blue-50 text-blue-600 flex items-center justify-center">
                    <Compass className={`w-4 h-4 ${activeJob.status === "RUNNING" ? "animate-spin" : ""}`} />
                  </div>
                  <div>
                    <div className="text-xs font-bold text-slate-900 flex items-center gap-2">
                      <span>Live Discovery Job #{activeJob.id}: {activeJob.name}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        activeJob.status === "RUNNING"
                          ? "bg-blue-100 text-blue-800"
                          : activeJob.status === "COMPLETED"
                          ? "bg-emerald-100 text-emerald-800"
                          : "bg-rose-100 text-rose-800"
                      }`}>
                        {activeJob.status}
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-500">
                      Target: {activeJob.industry} · Location: <span className="font-mono font-semibold text-slate-800">{activeJob.location}</span> · Sources: {activeJob.sources_used}
                    </div>
                  </div>
                </div>
                <div className="font-mono text-sm font-bold text-blue-700">{activeJob.progress_percent}%</div>
              </div>

              {/* Progress Bar */}
              <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-blue-600 rounded-full transition-all duration-300"
                  style={{ width: `${activeJob.progress_percent}%` }}
                ></div>
              </div>

              {/* Operational Counters */}
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2 pt-2 border-t border-slate-100 text-center">
                {[
                  { label: "Discovered", value: activeJob.discovered_count },
                  { label: "Stored", value: activeJob.new_businesses_count },
                  { label: "Websites Found", value: activeJob.websites_found_count },
                  { label: "Reachable", value: activeJob.websites_reachable_count || activeJob.websites_crawled_count },
                  { label: "Verified Sites", value: activeJob.websites_verified_count || 0 },
                  { label: "Audits Done", value: activeJob.audits_completed_count },
                  { label: "Contacts Found", value: activeJob.contacts_found_count || 0 },
                  { label: "Verified Emails", value: activeJob.verified_emails_count || 0 },
                ].map((stat, i) => (
                  <div key={i} className="p-2 rounded bg-slate-50 border border-slate-100">
                    <div className="text-sm font-bold font-mono text-slate-900">{stat.value}</div>
                    <div className="text-[10px] text-slate-500 font-medium truncate">{stat.label}</div>
                  </div>
                ))}
              </div>

              {activeJob.error_message && (
                <div className="p-2.5 bg-amber-50 border border-amber-200 text-amber-900 text-xs rounded">
                  <span className="font-bold">Execution Note:</span> {activeJob.error_message}
                </div>
              )}
            </div>
          )}

          {/* Main Campaign Builder Form */}
          <form onSubmit={handleStartDiscovery} className="p-6 bg-white rounded-lg border border-slate-200 shadow-xs space-y-6">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h2 className="text-sm font-bold text-slate-900">
                Configure Multi-Source Discovery Campaign
              </h2>
              <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded border border-emerald-200">
                Multi-Source Mode Active
              </span>
            </div>

            {/* Geographic Scope Selector */}
            <div className="space-y-2 text-xs">
              <label className="block text-slate-600 font-medium">Select Geographic Target Mode:</label>
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                {[
                  { id: "WORLDWIDE", label: "Worldwide", desc: "Global scan" },
                  { id: "COUNTRY", label: "Country", desc: "ISO code / boundary" },
                  { id: "REGION", label: "Region / State", desc: "Admin level 4 boundary" },
                  { id: "CITY", label: "City / Municipality", desc: "Local administrative area" },
                  { id: "BBOX", label: "Bounding Box", desc: "Latitude/Longitude rect" },
                ].map((item) => (
                  <button
                    type="button"
                    key={item.id}
                    onClick={() => handleGeoModeSelect(item.id as any)}
                    className={`p-2.5 rounded-md border text-left transition ${
                      geoMode === item.id
                        ? "bg-blue-50 border-blue-400 text-blue-900 font-bold"
                        : "bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100"
                    }`}
                  >
                    <div className="text-xs font-semibold">{item.label}</div>
                    <div className="text-[10px] text-slate-400 font-normal">{item.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Form Fields */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div>
                <label className="block text-slate-600 font-medium mb-1">Target Location:</label>
                <input
                  type="text"
                  required
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="WORLDWIDE, London, New York, country:US"
                  className="w-full px-3 py-1.5 rounded border border-slate-300 text-slate-900 outline-none focus:border-blue-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-slate-600 font-medium mb-1">Target Industry / Keyword:</label>
                <input
                  type="text"
                  required
                  value={industry}
                  onChange={(e) => setIndustry(e.target.value)}
                  placeholder="restaurant, dental, hotel, clinic, legal"
                  className="w-full px-3 py-1.5 rounded border border-slate-300 text-slate-900 outline-none focus:border-blue-500"
                />
              </div>
            </div>

            {/* Source Selection */}
            <div className="space-y-2 text-xs">
              <label className="block text-slate-600 font-medium">Active Ingestion Sources (Select one or more):</label>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {[
                  { id: "OpenStreetMap", label: "OpenStreetMap (Live POI)", icon: "🗺️", desc: "Global Public Business Registries & Geo-nodes" },
                  { id: "GoogleMaps", label: "Google Maps & Places", icon: "📍", desc: "Local Business Listings, Ratings & Coordinates" },
                  { id: "AISearch", label: "AI Search & Executive Agent", icon: "🤖", desc: "Autonomous AI Web Discovery & LinkedIn Search" },
                  { id: "SocialIntent", label: "Social & LinkedIn Intent Hunter", icon: "🔥", desc: "Real-time Buyer Intent Requests & Posts" },
                ].map((src) => {
                  const isChecked = selectedSources.includes(src.id);
                  return (
                    <button
                      type="button"
                      key={src.id}
                      onClick={() => toggleSource(src.id)}
                      className={`p-3 rounded-lg border text-left transition ${
                        isChecked
                          ? "bg-blue-50 border-blue-400 text-blue-900 shadow-xs"
                          : "bg-slate-50 border-slate-200 text-slate-600 opacity-70 hover:opacity-100"
                      }`}
                    >
                      <div className="font-bold flex items-center justify-between">
                        <span className="flex items-center gap-1.5">
                          <span>{src.icon}</span>
                          <span className="text-xs">{src.label}</span>
                        </span>
                        <span className={`w-4 h-4 rounded-full border flex items-center justify-center text-[10px] ${isChecked ? "bg-blue-600 border-blue-600 text-white font-bold" : "border-slate-300"}`}>
                          {isChecked && "✓"}
                        </span>
                      </div>
                      <div className="text-[10px] text-slate-500 mt-1">{src.desc}</div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Discovery Budget & Thresholds */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs pt-2 border-t border-slate-100">
              <div>
                <label className="block text-slate-600 font-medium mb-1">
                  Minimum Lead Score Threshold: <span className="font-bold text-slate-900">{minScore}/100</span>
                </label>
                <input
                  type="range"
                  min="30"
                  max="90"
                  step="5"
                  value={minScore}
                  onChange={(e) => setMinScore(Number(e.target.value))}
                  className="w-full accent-blue-600"
                />
                <div className="text-[10px] text-slate-400 mt-1">Filters out low-opportunity prospects</div>
              </div>

              <div>
                <label className="block text-slate-600 font-medium mb-1">Freshness Requirement:</label>
                <select
                  value={freshnessDays}
                  onChange={(e) => setFreshnessDays(Number(e.target.value))}
                  aria-label="Freshness Requirement"
                  className="w-full px-3 py-1.5 rounded border border-slate-300 bg-white text-slate-900 outline-none"
                >
                  <option value="1">Discovered within 24 hours</option>
                  <option value="3">Discovered within 3 days</option>
                  <option value="7">Discovered within 7 days (Fresh)</option>
                  <option value="30">Discovered within 30 days (Recent)</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-600 font-medium mb-1">Max Ingestion Target (Budget):</label>
                <input
                  type="number"
                  min="10"
                  max="300"
                  value={maxLeads}
                  onChange={(e) => setMaxLeads(Number(e.target.value))}
                  className="w-full px-3 py-1.5 rounded border border-slate-300 text-slate-900 font-mono outline-none"
                />
              </div>
            </div>

            {/* Submit */}
            <div className="flex justify-end pt-3 border-t border-slate-100">
              <button
                type="submit"
                className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-xs font-bold shadow-xs transition"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Launch Live Ingestion Campaign</span>
              </button>
            </div>
          </form>

          {/* Discovery Operations History */}
          <div className="p-6 bg-white rounded-lg border border-slate-200 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h2 className="text-sm font-bold text-slate-900">
                  Discovery Operations History & Ingestion Log
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Historical discovery batches, rejected noise counts, and strictly qualified lead yields.
                </p>
              </div>
              <button
                onClick={fetchJobs}
                className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1"
              >
                <RefreshCw className="w-3 h-3" />
                <span>Refresh Jobs</span>
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50 text-slate-500 font-bold uppercase tracking-wider text-[10px]">
                    <th className="p-3">Job #</th>
                    <th className="p-3">Campaign Target</th>
                    <th className="p-3">Discovered</th>
                    <th className="p-3">Websites (Found / Verified)</th>
                    <th className="p-3">Audits (Done)</th>
                    <th className="p-3">Contacts Found</th>
                    <th className="p-3">Status</th>
                    <th className="p-3">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {loading ? (
                    <tr>
                      <td colSpan={8} className="p-8 text-center text-slate-400">
                        Loading discovery operations...
                      </td>
                    </tr>
                  ) : jobs.length === 0 ? (
                    <tr>
                      <td colSpan={8} className="p-8 text-center text-slate-400">
                        No discovery operations recorded yet.
                      </td>
                    </tr>
                  ) : (
                    jobs.map((j) => (
                      <tr key={j.id} className="hover:bg-slate-50/80 transition">
                        <td className="p-3 font-mono font-bold text-blue-600">#{j.id}</td>
                        <td className="p-3">
                          <div className="font-semibold text-slate-900">{j.name}</div>
                          <div className="text-[10px] text-slate-400 truncate max-w-xs">{j.sources_used}</div>
                        </td>
                        <td className="p-3 font-mono">{j.discovered_count}</td>
                        <td className="p-3 font-mono">{j.websites_found_count} / {j.websites_verified_count || 0}</td>
                        <td className="p-3 font-mono">{j.audits_completed_count}</td>
                        <td className="p-3 font-mono font-semibold text-slate-800">{j.contacts_found_count || 0}</td>
                        <td className="p-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                            j.status === "COMPLETED"
                              ? "bg-emerald-100 text-emerald-800"
                              : j.status === "RUNNING"
                              ? "bg-blue-100 text-blue-800"
                              : "bg-rose-100 text-rose-800"
                          }`}>
                            {j.status}
                          </span>
                        </td>
                        <td className="p-3 text-slate-400">{new Date(j.created_at).toLocaleDateString()}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
