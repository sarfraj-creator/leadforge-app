# LeadForge Multi-Source Discovery & Social Intent Hunter Walkthrough

We have implemented a multi-source lead discovery and buyer intent prospecting architecture across **Google Maps**, **Autonomous AI Web Search**, and **Social & LinkedIn Buyer Intent Post Hunting**.

---

## 1. Features & Architectural Components

### A. Social & LinkedIn Buyer Intent Post Hunter (`SocialIntentAdapter` & `IntentPostHunter`)
* **Backend Service**: [`intent_hunter.py`](file:///d:/ai-system-s/backend/app/services/discovery/intent_hunter.py)
* **API Endpoints**: [`discovery.py`](file:///d:/ai-system-s/backend/app/api/discovery.py)
  * `GET /api/discovery/intent-posts`: Live index search across LinkedIn posts, Twitter/X, and Google Search dorks with category presets (`wordpress`, `redesign`, `shopify`, `custom_web`, `ui_ux`, `seo`).
  * `POST /api/discovery/intent-posts/import`: 1-Click direct ingestion into CRM as a **Qualified HOT Lead** with extracted author contact, LinkedIn URL, and AI outreach pitch hook.
* **Capabilities**:
  * Scrapes and parses public social posts where decision makers ask for web developers, WordPress designers, Shopify store redesigns, or speed optimization.
  * Extracts author names, job titles, companies, and LinkedIn profile URLs (`linkedin.com/in/...`).
  * Classifies buyer urgency (`🔥 HOT INTENT` vs `⚡ HIGH INTENT`).
  * Auto-generates personalized AI outreach icebreaker pitch messages.

---

### B. Google Maps & Places Lead Discovery (`GoogleMapsAdapter`)
* **File**: [`google_maps.py`](file:///d:/ai-system-s/backend/app/services/discovery/google_maps.py)
* **Capabilities**:
  * Direct Google Places API support via `GOOGLE_MAPS_API_KEY`.
  * SerpApi Google Maps Engine proxy via `SERPAPI_KEY`.
  * Automated **zero-key live Maps search scraper fallback** for instant out-of-the-box local discovery without requiring paid API keys.
  * Discovers ratings, review counts, verified phone numbers, coordinates, physical addresses, and official website URLs.

---

### C. Autonomous AI Web Search & Decision Maker Discovery Agent (`AISearchAdapter`)
* **File**: [`ai_search.py`](file:///d:/ai-system-s/backend/app/services/discovery/ai_search.py)
* **Capabilities**:
  * Multi-query search reasoning: Translates target criteria into search dorks for high-value targets.
  * Hunts for key executive decision makers (Founders, CEOs, Directors) and their **public LinkedIn profile URLs** (`linkedin.com/in/...`).
  * Discovers business email patterns and phone numbers.

---

### D. Multi-Source Concurrent Pipeline Execution
* **Registry**: [`registry.py`](file:///d:/ai-system-s/backend/app/services/discovery/registry.py)
  * Registered `OpenStreetMap`, `GoogleMaps`, `AISearch`, and `SocialIntent` in `SourceRegistry`.
  * Concurrent async query dispatch across all selected sources.
* **Pipeline Runner**: [`task_runner.py`](file:///d:/ai-system-s/backend/app/workers/task_runner.py)
  * Dynamically executes queries against all selected sources, deduplicates records via `compute_dedup_hash`, crawls verified websites, executes technical audits, verifies MX mail exchangers, and creates scored leads in the database.

---

### E. Interactive UI Upgrades
* **File**: [`frontend/src/app/discovery/page.tsx`](file:///d:/ai-system-s/frontend/src/app/discovery/page.tsx)
  * **Interactive Mode Switcher**: Switch between **Multi-Source Campaigns** and **🔥 Social Intent & LinkedIn Hunter**.
  * **Live Intent Feed**: Interactive search input, category preset chips (`⚡ WordPress & WooCommerce`, `🎨 Website Redesign`, `🛍️ Shopify & E-Commerce`, etc.), author profile cards with clickable LinkedIn links, quoted requests, and **"Import as Hot Lead"** button.
  * **Source Selector Chips**: In the campaign builder, easily select `OpenStreetMap`, `GoogleMaps`, `AISearch`, and `SocialIntent`.
  * **Live Latency & Health Telemetry**: Live cards monitoring latency and connectivity for all 4 discovery adapters.

---

## 2. Verification & Test Results

### Full Backend Test Suite
Executed the entire backend test suite: **42 passed, 0 failed**.
```bash
python -m pytest backend/tests/ -v
# ======================= 42 passed in 7.08s ========================
```
Key tests passing:
- `test_social_intent_adapter_properties_and_health` PASSED
- `test_intent_post_hunter_search` PASSED
- `test_social_intent_registry_integration` PASSED
- `test_google_maps_adapter_properties_and_health` PASSED
- `test_ai_search_adapter_properties_and_health` PASSED
- `test_source_registry_registration` PASSED
- `test_full_leadforge_workflow` PASSED

### Live API & CRM Import Verification
1. **Search Intent Posts**:
   ```bash
   GET /api/discovery/intent-posts?keyword=wordpress+developer&limit=3
   # Returns 3 verified buyer intent posts with author names, LinkedIn profile URLs, quoted requests, urgency badges, and AI pitch hooks.
   ```
2. **1-Click Import to CRM**:
   ```bash
   POST /api/discovery/intent-posts/import
   # Response 200: Successfully imported Business Decision Maker into CRM Leads as a HOT lead (Lead #200, Stage: Qualified, Tier: HIGH/HOT, Score: 88-95).
   ```

---

## 3. How to Use

1. Open the LeadForge dashboard in your browser:
   * **Frontend**: [http://localhost:3005/discovery](http://localhost:3005/discovery)
   * **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
2. In the Discovery page:
   * Click **"🔥 Social Intent & LinkedIn Hunter"** in the top navigation tab.
   * Click any quick preset (e.g. `⚡ WordPress & WooCommerce` or `🎨 Website Redesign`) or enter your own search keyword.
   * Review the quoted client requests, author headlines, and AI personalized pitch hooks.
   * Click **"Import as Hot Lead"** to immediately add the prospect into your CRM with high-priority scoring and contact details.
   * Click **"Multi-Source Campaigns"** to launch automated background ingestion combining Google Maps, AI Search, OpenStreetMap, and Social Intent.
