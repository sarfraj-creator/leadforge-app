# 🏗️ LeadForge: Enterprise B2B Lead Intelligence, Technical Website Auditing & Autonomous Outreach Platform

Complete technical architecture, file system blueprint, environment variables guide, and deployment handbook.

---

## 📑 Table of Contents
1. [System Overview & Workflow Architecture](#1-system-overview--workflow-architecture)
2. [Complete Project Folder & File Structure](#2-complete-project-folder--file-structure)
3. [SMTP & Real Email Sending Guide](#3-smtp--real-email-sending-guide)
4. [Environment Variables Reference (`.env.example`)](#4-environment-variables-reference-envexample)
5. [Multi-Model Hugging Face Architecture](#5-multi-model-hugging-face-architecture)
6. [How to Build & Run Locally](#6-how-to-build--run-locally)
7. [How to Deploy on Vercel (100% Free Monorepo)](#7-how-to-deploy-on-vercel-100-free-monorepo)
8. [Docker & Containerized Deployment](#8-docker--containerized-deployment)

---

## 1. System Overview & Workflow Architecture

LeadForge is a self-hosted B2B prospecting engine that combines deterministic website intelligence, evidence-based qualification scoring, multi-model AI synthesis, and autonomous multi-day follow-up outreach.

### 🔄 End-to-End Data Lifecycle Flow:

```
                                  LEADFORGE AUTONOMOUS LIFECYCLE
                                  
  [1. MULTI-SOURCE DISCOVERY]
  ├── OpenStreetMap (Global geospatial places & amenities)
  ├── Google Maps / Places API (Local business phone, address, ratings)
  ├── Autonomous AI Search (Live grounded web research via Perplexity/Gemini)
  └── Social Intent Hunter (Live LinkedIn/Twitter RFQs & hiring intent)
         │
         ▼
  [2. DETERMINISTIC CRAWLING & HARDENING]
  ├── SSRF-Safe Crawler (Zero private IP traversal, RFC 1918 blocking)
  ├── Reachability & Official Brand Domain Match Verification
  └── DNS MX Records & Mailbox Verification
         │
         ▼
  [3. WEBSITE INTELLIGENCE & TECHNICAL AUDIT]
  ├── Core Web Vitals & Loading Speed Measurement
  ├── Viewport Inspection (Mobile responsiveness & navigation defects)
  ├── Security & SSL Certificate Validation
  └── Wappalyzer-style Technology & CMS Stack Detection
         │
         ▼
  [4. EVIDENCE-BASED 5-PART LEAD SCORING]
  ├── Business Fit Score (0-100)
  ├── Opportunity Score (0-100 derived exclusively from measured defects)
  ├── Data Confidence Score (0-100 based on verified provenance)
  ├── Buying Intent Score (0-100 based on real intent posts)
  └── Contactability Score (0-100 based on verified direct phone/email)
         │
         ▼
  [5. LEAD CATEGORY SEGREGATION]
  ├── 🎨 HAS_WEBSITE_REDESIGN (Existing website with measurable deficiencies)
  ├── 🚀 NO_WEBSITE_NEW_BUILD (Verified brick-and-mortar with zero web presence)
  └── 🔥 BUYER_INTENT_POST (Live social RFQ / immediate buyer intent)
         │
         ▼
  [6. TECHNICAL R&D AUDIT REPORT GENERATOR]
  ├── Executive Health Scorecards (0-100)
  ├── Observable Defect Evidence Snippets (Zero hallucinations)
  ├── Strategic 4-Phase Modernization Blueprint
  └── Printable Executive HTML / PDF Document Generation
         │
         ▼
  [7. AUTONOMOUS 4-STEP SEQUENCE DISPATCHER (DAY 0, 3, 7, 14)]
  ├── Day 0: Initial Outreach + Attached Technical R&D Audit Report Document
  ├── Day 3: Value-Add UX Wireframe Solution Preview
  ├── Day 7: Case Study & Competitor Benchmark Insight
  ├── Day 14: Polite Breakup & Permanent Report Access Link
  └── 🛑 AUTO-STOP: Automatically pauses sequences on prospect reply or unsubscribe
         │
         ▼
  [8. UNIFIED INBOX, CRM KANBAN & ACTIVITY TIMELINE]
  ├── Multi-folder Inbox (All, Replies, Sent, Bounces, Unsubscribes)
  ├── Inbound Reply Sentiment Classifier (Interested, Meeting Request, Unsubscribe)
  └── Direct Outbound Reply Composer & Kanban Board Sync
```

---

## 2. Complete Project Folder & File Structure

```
d:/ai-system-s/
├── .env                                  # Active environment configuration (local)
├── .env.example                          # Blueprint environment file with documentation
├── README.md                             # Repository overview and quickstart
├── DEPLOYMENT_AND_ARCHITECTURE.md        # Comprehensive architecture & deployment blueprint
├── vercel.json                           # Vercel Monorepo build & routing configuration
├── requirements.txt                      # Root Python dependencies for Vercel Serverless
├── docker-compose.yml                    # Docker containerization configuration
├── leadforge.db                          # SQLite database file (auto-created if SQLite used)
│
├── api/                                  # Serverless API Entrypoint
│   └── index.py                          # Vercel Python Serverless ASGI handler
│
├── backend/                              # FastAPI Python Backend Engine
│   ├── requirements.txt                  # Python dependencies manifest
│   ├── app/
│   │   ├── main.py                       # FastAPI application setup, CORS, lifespan & router mounting
│   │   │
│   │   ├── core/                         # Core Foundation & Database
│   │   │   ├── config.py                 # Pydantic Settings with dynamic env loaders
│   │   │   ├── database.py               # Async SQLAlchemy engine & session factory
│   │   │   ├── security.py               # Password hashing (bcrypt) & JWT token handling
│   │   │   └── bootstrap.py              # System bootstrap initialization (Default Org, Admin, Stages)
│   │   │
│   │   ├── models/                       # SQLAlchemy Async ORM Models
│   │   │   ├── user.py                   # User, Organization & Role models
│   │   │   ├── company.py                # Company & LeadSourceRecord models
│   │   │   ├── contact.py                # Contact & EmailVerificationRecord models
│   │   │   ├── lead.py                   # Lead, LeadScore & LeadOpportunity models
│   │   │   ├── website.py                # Website, WebsiteAudit, WebsiteIssue, WebsiteTechnology
│   │   │   ├── campaign.py               # Campaign, SequenceStep & CampaignLead models
│   │   │   ├── email.py                  # EmailThread, EmailMessage, EmailEvent, UnsubscribeRecord
│   │   │   ├── crm.py                    # Activity, Task, Note & StageHistory models
│   │   │   ├── discovery.py              # DiscoveryJob & LeadSourceConfig models
│   │   │   ├── provenance.py             # FieldProvenanceRecord model
│   │   │   └── service_need.py           # ServiceNeedEvidence model
│   │   │
│   │   ├── schemas/                      # Pydantic Request & Response Schemas
│   │   │   └── common.py                 # Complete validation schemas for all endpoints
│   │   │
│   │   ├── api/                          # REST API Endpoints
│   │   │   ├── auth.py                   # Authentication & token endpoints
│   │   │   ├── leads.py                  # Lead search, category filtering & bulk actions
│   │   │   ├── audits.py                 # Technical website audits & R&D report endpoints
│   │   │   ├── companies.py              # Company intelligence endpoints
│   │   │   ├── contacts.py               # Verified contact endpoints
│   │   │   ├── discovery.py              # Discovery job dispatch & source health
│   │   │   ├── sources.py                # Multi-source ingestion endpoints
│   │   │   ├── campaigns.py              # Sequence runner, auto-enroll & cycle dispatch
│   │   │   ├── emails.py                 # Email generation & MIME attachment dispatch
│   │   │   ├── inbox.py                  # Unified inbox, direct reply & reply simulator
│   │   │   ├── crm.py                    # Kanban board, tasks, notes & activity timeline
│   │   │   ├── analytics.py              # Real-time conversion & discovery analytics
│   │   │   ├── data_quality.py           # Data confidence & contradiction audits
│   │   │   ├── settings.py               # AI multi-model & SMTP settings management
│   │   │   ├── search.py                 # Global omnibar search
│   │   │   ├── admin.py                  # Database reset & admin utilities
│   │   │   └── health.py                 # System health probe
│   │   │
│   │   ├── services/                     # Business Logic & Intelligence Engines
│   │   │   ├── ai/                       # Multi-Model AI Ensemble
│   │   │   │   ├── base.py               # Abstract base AI provider
│   │   │   │   ├── factory.py            # AI factory with task-specialized routing
│   │   │   │   ├── huggingface.py        # Hugging Face Multi-Model Ensemble provider
│   │   │   │   ├── perplexity.py         # Perplexity Sonar live web search provider
│   │   │   │   ├── gemini.py             # Google Gemini search grounding provider
│   │   │   │   └── prompt_engine.py      # Structured prompt synthesis engine
│   │   │   │
│   │   │   ├── audit/                    # Technical Website Audit Engine
│   │   │   │   ├── engine.py             # Deterministic HTML crawler & defect detector
│   │   │   │   └── report_generator.py   # R&D Technical Audit Report Document generator
│   │   │   │
│   │   │   ├── email/                    # Email Formatting & Dispatch
│   │   │   │   ├── sender.py             # Multipart MIME EmailSender with attachments
│   │   │   │   └── formatter.py          # Responsive HTML email layout & scorecard embeds
│   │   │   │
│   │   │   ├── crawler/                  # SSRF-Protected Web Crawler
│   │   │   │   └── safe_crawler.py       # Safe HTTP client with private IP filtering
│   │   │   │
│   │   │   ├── contact/                  # Contact & Email Verification
│   │   │   │   ├── verifier.py           # MX DNS, SMTP handshake & disposable email check
│   │   │   │   ├── phone_verifier.py     # E.164 phone formatting & carrier check
│   │   │   │   └── decision_maker.py     # Executive & owner extraction
│   │   │   │
│   │   │   ├── scoring/                  # Deterministic Scoring Engines
│   │   │   │   ├── lead_scorer.py        # 5-Part decoupled lead scoring
│   │   │   │   ├── opportunity_engine.py # Measurement-based opportunity engine
│   │   │   │   ├── service_need_engine.py# Service recommendation engine
│   │   │   │   └── data_quality_scorer.py# Factual confidence scorer
│   │   │   │
│   │   │   ├── verification/             # Business Identity Verification
│   │   │   │   ├── website_verifier.py   # Domain match & brand name verification
│   │   │   │   └── identity_verifier.py  # Cross-source entity resolution
│   │   │   │
│   │   │   ├── discovery/                # Ingestion Source Adapters
│   │   │   │   ├── registry.py           # Ingestion adapter registry
│   │   │   │   ├── osm_adapter.py        # OpenStreetMap Overpass API adapter
│   │   │   │   ├── google_maps_adapter.py# Google Places & SerpApi adapter
│   │   │   │   ├── ai_search_adapter.py  # Autonomous AI discovery adapter
│   │   │   │   └── social_intent_adapter.py # LinkedIn & Social RFQ intent hunter
│   │   │   │
│   │   │   └── freshness/                # Freshness & Stale Data Tracker
│   │   │       └── field_freshness.py    # Field-level timestamp & decay engine
│   │   │
│   │   └── workers/                      # Background Task Runners
│   │       ├── task_runner.py            # Discovery & enrichment background pipeline
│   │       └── sequence_runner.py        # Autonomous 4-Step multi-day sequence worker
│   │
│   └── tests/                            # Comprehensive Automated Pytest Suite
│       ├── conftest.py                   # Pytest fixtures & test database setup
│       ├── test_autonomous_pipeline.py   # R&D report, categories & sequence tests
│       ├── test_core.py                  # SSRF, deduplication & scoring unit tests
│       ├── test_data_truth.py            # Anti-fabrication & evidence boundary tests
│       ├── test_global_discovery.py      # Multi-source discovery tests
│       ├── test_integration.py           # Full end-to-end integration workflow test
│       ├── test_intent_hunter.py         # Social intent adapter tests
│       ├── test_lead_hardening.py        # Website audit & qualification tests
│       ├── test_new_discovery_adapters.py# Google Maps & AI search adapter tests
│       ├── test_qualification_and_taxonomy.py # Pipeline stage boundary tests
│       └── test_realtime_ai_and_linkedin.py # AI provider fallback & health tests
│
└── frontend/                             # Next.js 14 App Router UI
    ├── package.json                      # Next.js, React, Tailwind & Lucide dependencies
    ├── tsconfig.json                     # TypeScript compiler configuration
    ├── next.config.ts                    # Next.js build & standalone settings
    ├── eslint.config.mjs                 # ESLint rules
    ├── postcss.config.mjs                # PostCSS configuration
    ├── src/
    │   ├── types/
    │   │   └── index.ts                  # TypeScript interfaces for all data structures
    │   │
    │   ├── lib/
    │   │   └── api.ts                    # Universal API fetcher with auto Vercel resolution
    │   │
    │   ├── components/                   # Reusable UI Component Library
    │   │   ├── AppLayout.tsx             # Sidebar navigation, header & live status indicators
    │   │   ├── LeadScoreBadge.tsx        # Color-coded lead quality score badge
    │   │   ├── FreshnessBadge.tsx        # Data freshness pill (Fresh, Recent, Stale)
    │   │   ├── LeadDetailModal.tsx       # Comprehensive lead 360-degree inspection modal
    │   │   ├── EmailComposerModal.tsx    # Dual-mode composer (Plain + Rich HTML Preview + Attachments)
    │   │   └── TechnicalAuditReportModal.tsx # Interactive R&D Audit Report doc viewer & PDF export
    │   │
    │   └── app/                          # 14 Full Application Routes
    │       ├── layout.tsx                # Root HTML layout with Inter font
    │       ├── page.tsx                  # Executive Dashboard with live KPI counters
    │       ├── leads/page.tsx            # Lead intelligence table with category tabs
    │       ├── discovery/page.tsx        # Multi-source discovery launcher & job progress
    │       ├── audits/page.tsx           # Technical website audits grid with R&D doc triggers
    │       ├── companies/page.tsx        # Company directory and domain overview
    │       ├── contacts/page.tsx         # Decision maker directory & email status
    │       ├── review/page.tsx           # Human-in-the-loop lead review & approval queue
    │       ├── data-quality/page.tsx     # Contradiction audits & confidence breakdown
    │       ├── campaigns/page.tsx        # 4-Step sequence timeline & execution runner
    │       ├── inbox/page.tsx            # Unified 3-pane inbox with direct reply & AI classification
    │       ├── crm/page.tsx              # Kanban stage board (drag & drop) & task manager
    │       ├── analytics/page.tsx        # Discovery performance & rejection analytics
    │       ├── search/page.tsx           # Omnibar deep search
    │       └── settings/page.tsx         # Multi-Model Hugging Face, Perplexity, Gemini & SMTP configuration
```

---

## 3. SMTP & Real Email Sending Guide

### ❓ Why was email running in simulation mode?
By default, when `SMTP_HOST` and `SMTP_USER` are left blank, LeadForge runs in **Safe Local Development Mode**. It generates realistic simulated message IDs, records outbound threads in the Unified Inbox, and attaches generated R&D reports without requiring external credentials.

### ✉️ How to Send Real Emails to Real Inboxes:

#### Option A: Using Gmail (Free & Fast)
1. Go to your **Google Account** &rarr; **Security** &rarr; Enable **2-Step Verification**.
2. Search for **App Passwords** &rarr; Create a password named `LeadForge`.
3. Configure these values in your `.env` or in **Settings &rarr; SMTP**:
   ```ini
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-16-char-app-password
   SMTP_FROM_EMAIL=your-email@gmail.com
   SMTP_FROM_NAME=Your Name | Digital Agency
   SMTP_USE_TLS=True
   ```

#### Option B: Using SendGrid / Brevo / Amazon SES
```ini
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.your_sendgrid_api_key
SMTP_FROM_EMAIL=outreach@yourverifiedagencydomain.com
SMTP_FROM_NAME=Alex Mercer | Acme Digital
SMTP_USE_TLS=True
```

---

## 4. Environment Variables Reference (`.env.example`)

Create a `.env` file in the project root by copying the template below:

```ini
# ==============================================================================
# LEADFORGE PRODUCTION CONFIGURATION
# ==============================================================================

PROJECT_NAME=LeadForge
VERSION=1.0.0
ENVIRONMENT=production
DEBUG=False
API_V1_STR=/api

# ------------------------------------------------------------------------------
# 1. DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# For local SQLite:
DATABASE_URL=sqlite+aiosqlite:///./leadforge.db

# For Production Managed PostgreSQL (Neon.tech / Supabase / AWS RDS):
# DATABASE_URL=postgresql+asyncpg://user:password@ep-host-name.neon.tech/leadforge?ssl=require

REDIS_URL=redis://localhost:6379/0

# ------------------------------------------------------------------------------
# 2. SECURITY & AUTHENTICATION
# ------------------------------------------------------------------------------
SECRET_KEY=leadforge-production-super-secret-key-change-this-in-prod-2026
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ENCRYPTION_KEY=leadforge-secure-enc-key-32ch!

# ------------------------------------------------------------------------------
# 3. SMTP OUTBOUND EMAIL CONFIGURATION (Real Emails)
# ------------------------------------------------------------------------------
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=LeadForge Outreach Agency
SMTP_USE_TLS=True

# ------------------------------------------------------------------------------
# 4. HUGGING FACE MULTI-MODEL SUITE
# ------------------------------------------------------------------------------
# Free token from: https://huggingface.co/settings/tokens
HF_TOKEN=hf_your_hugging_face_token_here
HF_PROVIDER=huggingface

# Task-Specialized Models:
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.3
HF_OUTREACH_MODEL=mistralai/Mistral-7B-Instruct-v0.3
HF_AUDIT_MODEL=Qwen/Qwen2.5-Coder-7B-Instruct
HF_CLASSIFICATION_MODEL=meta-llama/Meta-Llama-3-8B-Instruct
HF_EXTRACTION_MODEL=meta-llama/Meta-Llama-3-8B-Instruct

# ------------------------------------------------------------------------------
# 5. REAL-TIME AI & LIVE SEARCH GROUNDING (Optional)
# ------------------------------------------------------------------------------
ACTIVE_AI_PROVIDER=auto
AI_SEARCH_PROVIDER=auto

# Perplexity AI (Live web citations): https://www.perplexity.ai/settings/api
PERPLEXITY_API_KEY=
PERPLEXITY_MODEL=sonar

# Google Gemini (Google Search grounding): https://aistudio.google.com/
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.0-flash

# ------------------------------------------------------------------------------
# 6. EXTERNAL DISCOVERY PROVIDERS (Optional)
# ------------------------------------------------------------------------------
# SerpApi Key for Google Maps & Local Business Scraping: https://serpapi.com/
SERPAPI_KEY=
GOOGLE_MAPS_API_KEY=
ENABLE_GOOGLE_MAPS_DISCOVERY=True
```

---

## 5. Multi-Model Hugging Face Architecture

LeadForge dynamically routes specific prompt types to specialized open-source models:

| Task Area | Default Model | Alternative Models | Why Specialized? |
| :--- | :--- | :--- | :--- |
| **Outreach Copywriter** | `mistralai/Mistral-7B-Instruct-v0.3` | `meta-llama/Meta-Llama-3-8B-Instruct` | Generates engaging, personalized cold outreach. |
| **Technical Auditor** | `Qwen/Qwen2.5-Coder-7B-Instruct` | `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B` | Analyzes code structure, Core Web Vitals, and SSL. |
| **Sentiment Classifier** | `meta-llama/Meta-Llama-3-8B-Instruct` | `cardiffnlp/twitter-roberta-base-sentiment-latest` | Evaluates replies (`Interested`, `Unsubscribe`) to pause sequences. |
| **NLP Query Extractor** | `meta-llama/Meta-Llama-3-8B-Instruct` | `mistralai/Mistral-7B-Instruct-v0.3` | Parses plain English into structured database filters. |

---

## 6. How to Build & Run Locally

### Prerequisites:
- Python 3.10+
- Node.js 18+ & npm

### Step 1: Clone & Setup Backend
```bash
# Open terminal in project root
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
# source .venv/bin/activate

# Install Python dependencies
pip install -r backend/requirements.txt

# Run FastAPI Backend (Port 8000)
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 2: Setup Frontend
```bash
# In a second terminal:
cd frontend
npm install
npm run dev
```

* **Frontend Dashboard**: `http://localhost:3005` (or `http://localhost:3000`)
* **Backend Swagger Docs**: `http://localhost:8000/docs`

---

## 7. How to Deploy on Vercel (100% Free Monorepo)

The repository is pre-configured with [`vercel.json`](file:///d:/ai-system-s/vercel.json) to deploy both the Next.js Frontend and the FastAPI Serverless Backend in a single project.

### 1-Click Deployment Steps:

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Deploy LeadForge to Vercel"
   git push origin main
   ```

2. **Import into Vercel**:
   * Navigate to **[vercel.com/new](https://vercel.com/new)**.
   * Click **Import** next to your repository.
   * **Root Directory**: Leave as `.` (root directory).
   * Click **Deploy**.

3. **Configure Environment Variables in Vercel Settings**:
   * Go to your Project on Vercel &rarr; **Settings** &rarr; **Environment Variables**.
   * Add any of the keys from [`.env.example`](#4-environment-variables-reference-envexample) (e.g., `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `HF_TOKEN`, `DATABASE_URL`).

---

## 8. Docker & Containerized Deployment

To deploy using Docker Compose:

```bash
docker-compose up --build -d
```

* Backend container runs on port `8000`.
* Frontend container runs on port `3000`.
