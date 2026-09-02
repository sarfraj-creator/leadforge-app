# 🚀 LeadForge — Enterprise B2B Lead Intelligence, Technical Website Auditing & Autonomous Outreach Engine

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000.svg?logo=next.js&logoColor=white)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org)
[![Tests](https://img.shields.io/badge/Tests-52%2F52%20Passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-blue.svg)]()

**LeadForge** is a complete, self-hosted B2B Lead Discovery, Multi-Source Enrichment, Deterministic Website Intelligence, Technical R&D Auditing, and Autonomous Multi-Day Follow-Up Outreach platform.

Built specifically for digital agencies (**Website Redesigns, UI/UX, Speed/Core Web Vitals Optimization, SEO, Maintenance, and Custom Web Engineering**), LeadForge automatically discovers qualified businesses with *observable, verifiable digital service needs* without fabricating data.

---

## 📚 Specialized Documentation & Guides

* 📘 **[Step-by-Step User Manual & How to Run](HOW_TO_USE_AND_RUN_GUIDE.md)** &mdash; Complete beginner-friendly guide on how to start each terminal and execute end-to-end prospecting workflows.
* 📖 **[Comprehensive Architecture & Deployment Guide](DEPLOYMENT_AND_ARCHITECTURE.md)** &mdash; Full system diagrams, folder maps, real SMTP setup, and free hosting blueprints.
* 🧠 **[Hugging Face Multi-Model Ensemble Guide](HUGGINGFACE_MODELS_GUIDE.md)** &mdash; Details on the 4 task-specialized model slots, curated model catalog, and instructions for swapping models in the future.
* ⚙️ **[Environment Configuration Blueprint](.env.example)** &mdash; Complete `.env` template with all keys and options documented.

---

## 📑 Table of Contents
1. [System Overview & Architecture Diagram](#-system-overview--architecture-diagram)
2. [Complete Project Folder & File Structure](#-complete-project-folder--file-structure)
3. [Environment Configuration (`.env`)](#-environment-configuration-env)
4. [Hugging Face Multi-Model Suite & How to Swap Models in the Future](#-hugging-face-multi-model-suite--how-to-swap-models-in-the-future)
5. [Real SMTP Email Setup Guide](#-real-smtp-email-setup-guide)
6. [How to Run Locally (Frontend & Backend)](#-how-to-run-locally-frontend--backend)
7. [How to Deploy the Entire Project to Vercel for Free](#-how-to-deploy-the-entire-project-to-vercel-for-free)
8. [Docker & Containerized Deployment](#-docker--containerized-deployment)
9. [Automated Testing & Verification](#-automated-testing--verification)

---

## 🏗️ System Overview & Architecture Diagram

```
                                  LEADFORGE AUTONOMOUS LIFECYCLE
                                  
  [1. MULTI-SOURCE INGESTION]
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

## 📁 Complete Project Folder & File Structure

```
d:/ai-system-s/
├── .env                                  # Active environment configuration (local)
├── .env.example                          # Blueprint environment file with documentation
├── .gitignore                            # Production git ignore rules
├── README.md                             # Complete master project manual
├── DEPLOYMENT_AND_ARCHITECTURE.md        # Supplementary architecture & deployment guide
├── HUGGINGFACE_MODELS_GUIDE.md           # Deep dive into Hugging Face model options
├── vercel.json                           # Unified Vercel Monorepo build & routing configuration
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
│   │   │   ├── config.py                 # Dynamic Pydantic settings & env loaders
│   │   │   ├── database.py               # Async SQLAlchemy engine & session factory
│   │   │   ├── security.py               # Password hashing (bcrypt) & JWT token handling
│   │   │   └── bootstrap.py              # System bootstrap initialization
│   │   │
│   │   ├── models/                       # SQLAlchemy Async ORM Models
│   │   │   ├── user.py                   # User, Organization & Role models
│   │   │   ├── company.py                # Company & LeadSourceRecord models
│   │   │   ├── contact.py                # Contact & EmailVerificationRecord models
│   │   │   ├── lead.py                   # Lead, LeadScore & LeadOpportunity models
│   │   │   ├── website.py                # Website, WebsiteAudit, WebsiteIssue, WebsiteTech
│   │   │   ├── campaign.py               # Campaign, SequenceStep & CampaignLead models
│   │   │   ├── email.py                  # EmailThread, EmailMessage, EmailEvent, UnsubscribeRecord
│   │   │   └── crm.py                    # Activity, Task, Note & StageHistory models
│   │   │
│   │   ├── schemas/                      # Pydantic Request & Response Validation Schemas
│   │   │   └── common.py                 # Complete validation schemas for all endpoints
│   │   │
│   │   ├── api/                          # REST API Endpoints
│   │   │   ├── leads.py                  # Lead search, category filtering & bulk actions
│   │   │   ├── audits.py                 # Technical website audits & R&D report endpoints
│   │   │   ├── campaigns.py              # Sequence runner, auto-enroll & cycle dispatch
│   │   │   ├── emails.py                 # Email generation & MIME attachment dispatch
│   │   │   ├── inbox.py                  # Unified inbox, direct reply & reply simulator
│   │   │   ├── crm.py                    # Kanban board, tasks, notes & activity timeline
│   │   │   ├── settings.py               # AI multi-model & SMTP settings management
│   │   │   └── health.py                 # System health probe
│   │   │
│   │   ├── services/                     # Business Logic & Intelligence Engines
│   │   │   ├── ai/                       # Multi-Model AI Ensemble (Hugging Face / Perplexity / Gemini)
│   │   │   │   ├── factory.py            # AI factory with task-specialized routing
│   │   │   │   ├── huggingface.py        # Hugging Face Multi-Model Ensemble provider
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
│   │   │   └── scoring/                  # Deterministic Scoring Engines
│   │   │       ├── lead_scorer.py        # 5-Part decoupled lead scoring
│   │   │       └── opportunity_engine.py # Measurement-based opportunity engine
│   │   │
│   │   └── workers/                      # Background Task Runners
│   │       ├── task_runner.py            # Discovery & enrichment background pipeline
│   │       └── sequence_runner.py        # Autonomous 4-Step multi-day sequence worker
│   │
│   └── tests/                            # 52 Automated Pytest Test Suites (100% Passing)
│
└── frontend/                             # Next.js 15 App Router UI
    ├── package.json                      # Dependencies
    ├── tsconfig.json                     # TypeScript compiler configuration
    ├── src/
    │   ├── lib/api.ts                    # Universal API fetcher with auto-relative Vercel routing
    │   ├── types/index.ts                # Strict TypeScript interfaces
    │   ├── components/                   # Modals (Audit Report Viewer, Email Composer, Badges)
    │   └── app/                          # 14 Full Application Pages (Leads, Inbox, Audits, CRM)
```

---

## ⚙️ Environment Configuration (`.env`)

Create a `.env` file in the root directory (or copy from `.env.example`):

```ini
# ==============================================================================
# LEADFORGE ENVIRONMENT CONFIGURATION
# ==============================================================================
PROJECT_NAME=LeadForge
VERSION=1.0.0
ENVIRONMENT=production
DEBUG=False
API_V1_STR=/api

# ------------------------------------------------------------------------------
# 1. DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# For local development (Zero setup SQLite):
DATABASE_URL=sqlite+aiosqlite:///./leadforge.db

# For Production Managed PostgreSQL (Neon.tech / Supabase / AWS RDS):
# DATABASE_URL=postgresql+asyncpg://user:password@ep-host-name.neon.tech/leadforge?ssl=require

REDIS_URL=redis://localhost:6379/0

# ------------------------------------------------------------------------------
# 2. SECURITY & AUTHENTICATION
# ------------------------------------------------------------------------------
SECRET_KEY=leadforge-super-secret-production-key-change-this-2026
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ENCRYPTION_KEY=leadforge-secure-enc-key-32ch!

# ------------------------------------------------------------------------------
# 3. SMTP OUTBOUND EMAIL (For Real Prospect Emails)
# ------------------------------------------------------------------------------
# Gmail Configuration (App Password):
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=LeadForge Outreach Agency
SMTP_USE_TLS=True

# ------------------------------------------------------------------------------
# 4. HUGGING FACE MULTI-MODEL ENSEMBLE SUITE
# ------------------------------------------------------------------------------
# Free User Access Token from: https://huggingface.co/settings/tokens
HF_TOKEN=hf_your_token_here
HF_PROVIDER=huggingface

# Specialized Task Models:
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.3
HF_OUTREACH_MODEL=mistralai/Mistral-7B-Instruct-v0.3
HF_AUDIT_MODEL=Qwen/Qwen2.5-Coder-7B-Instruct
HF_CLASSIFICATION_MODEL=meta-llama/Meta-Llama-3-8B-Instruct
HF_EXTRACTION_MODEL=meta-llama/Meta-Llama-3-8B-Instruct

# ------------------------------------------------------------------------------
# 5. REAL-TIME AI SEARCH GROUNDING (Optional)
# ------------------------------------------------------------------------------
ACTIVE_AI_PROVIDER=auto
AI_SEARCH_PROVIDER=auto

# Perplexity AI: https://www.perplexity.ai/settings/api
PERPLEXITY_API_KEY=
PERPLEXITY_MODEL=sonar

# Google Gemini: https://aistudio.google.com/
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.0-flash

# SerpApi Key for Google Maps Scraping: https://serpapi.com/
SERPAPI_KEY=
GOOGLE_MAPS_API_KEY=
ENABLE_GOOGLE_MAPS_DISCOVERY=True

# ------------------------------------------------------------------------------
# 6. APPLICATION URLS
# ------------------------------------------------------------------------------
NEXT_PUBLIC_API_URL=
FRONTEND_URL=http://localhost:3005
BACKEND_URL=http://localhost:8000
```

---

## 🧠 Hugging Face Multi-Model Suite & How to Swap Models in the Future

LeadForge routes different tasks to **task-specialized open-source models** for maximum accuracy:

```
                            ┌───────────────────────────────────────────────┐
                            │    LeadForge Multi-Model Hugging Face Engine  │
                            └──────────────────────┬────────────────────────┘
                                                   │
        ┌──────────────────────────┬───────────────┴───────────────┬──────────────────────────┐
        ▼                          ▼                               ▼                          ▼
 ✍️ OUTREACH COPYWRITER     🔍 CODE & CWV AUDITOR         💬 SENTIMENT & INTENT CLASSIFIER   🧠 NLP QUERY EXTRACTOR
 Model: Mistral-7B / Llama3 Model: Qwen2.5-Coder / DeepSeek Model: Llama-3 / RoBERTa        Model: Llama-3 / Mistral
```

### 🛠️ The 4 Specialized Model Slots:

| Task Slot | Environment Variable | Default Model | Best Alternative Models | Why Specialized? |
| :--- | :--- | :--- | :--- | :--- |
| **1. Cold Outreach Copywriter** | `HF_OUTREACH_MODEL` | `mistralai/Mistral-7B-Instruct-v0.3` | `meta-llama/Meta-Llama-3-8B-Instruct`<br>`google/gemma-2-9b-it` | High-converting, concise cold email copy with no generic corporate filler. |
| **2. Technical Audit Analyst** | `HF_AUDIT_MODEL` | `Qwen/Qwen2.5-Coder-7B-Instruct` | `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`<br>`meta-llama/Meta-Llama-3.1-8B-Instruct` | Code defect diagnosis, DOM analysis, and modernization blueprints. |
| **3. Reply Sentiment Classifier** | `HF_CLASSIFICATION_MODEL` | `meta-llama/Meta-Llama-3-8B-Instruct` | `cardiffnlp/twitter-roberta-base-sentiment-latest`<br>`distilbert-base-uncased-finetuned-sst-2` | Evaluates inbound prospect replies (`Interested`, `Unsubscribe`) to pause sequences. |
| **4. NLP Query & Entity Extractor** | `HF_EXTRACTION_MODEL` | `meta-llama/Meta-Llama-3-8B-Instruct` | `mistralai/Mistral-7B-Instruct-v0.3`<br>`dslim/bert-base-NER` | Translates plain English queries into structured filters and extracts decision makers. |

---

### 🔄 How to Change or Swap Models in the Future:

You have **3 simple methods** to change any model anytime:

#### Method 1: Live in the Web Dashboard (Zero Downtime / Instant)
1. Navigate to **[Settings &rarr; AI Configuration](http://localhost:3005/settings?tab=ai)** (or your live app URL).
2. Scroll to the **HUGGING FACE Multi-Model Specialized Ensemble Suite** section.
3. Paste or type any Hugging Face model repository ID into any of the 4 slots.
4. Click **"Save AI Configuration"**.
   > *Changes take effect immediately across all background workers and live API requests without restarting the server!*

#### Method 2: Via `.env` Environment File
Open `.env` and change the desired model ID:
```ini
HF_OUTREACH_MODEL=meta-llama/Meta-Llama-3-8B-Instruct
HF_AUDIT_MODEL=deepseek-ai/DeepSeek-R1-Distill-Qwen-7B
HF_CLASSIFICATION_MODEL=meta-llama/Meta-Llama-3-8B-Instruct
HF_EXTRACTION_MODEL=mistralai/Mistral-7B-Instruct-v0.3
```

#### Method 3: Via REST API Request
```bash
curl -X POST http://localhost:8000/api/settings/ai \
  -H "Content-Type: application/json" \
  -d '{
    "hf_outreach_model": "meta-llama/Meta-Llama-3-8B-Instruct",
    "hf_audit_model": "Qwen/Qwen2.5-Coder-7B-Instruct"
  }'
```

---

## ✉️ Real SMTP Email Setup Guide

### Why was email in simulation mode?
By default, if `SMTP_HOST` is blank, LeadForge runs in **Safe Local Simulation Mode** so you can test campaigns without sending spam or requiring credentials.

### How to configure real outbound emails:

#### Option A: Gmail (Free & Fast)
1. Go to your **Google Account** &rarr; **Security** &rarr; Enable **2-Step Verification**.
2. Search for **App Passwords** &rarr; Create an App Password named `LeadForge`.
3. Put the 16-character password into `.env` (or configure in **Settings &rarr; SMTP**):
   ```ini
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-16-char-app-password
   SMTP_FROM_EMAIL=your-email@gmail.com
   SMTP_FROM_NAME=Your Agency Name
   SMTP_USE_TLS=True
   ```

#### Option B: SendGrid / Brevo / Amazon SES
```ini
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.your-sendgrid-api-key
SMTP_FROM_EMAIL=outreach@yourdomain.com
SMTP_FROM_NAME=Alex Mercer | Digital Agency
SMTP_USE_TLS=True
```

---

## ⚡ How to Run Locally (Frontend & Backend)

### Prerequisites:
- Python 3.10+
- Node.js 18+ and npm

### 1. Start Backend Server (FastAPI):
```bash
# Open terminal in project root:
python -m venv .venv

# Activate virtual environment:
# Windows:
.venv\Scripts\activate
# Mac/Linux:
# source .venv/bin/activate

# Install Python dependencies:
pip install -r backend/requirements.txt

# Start FastAPI server on port 8000:
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
* **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

### 2. Start Frontend Server (Next.js):
```bash
# Open a second terminal:
cd frontend
npm install
npm run dev
```
* **Web Dashboard**: [http://localhost:3000](http://localhost:3000)

---

## 🔑 Default Administrator Login Credentials

When LeadForge boots up for the first time, it automatically creates the default administrator account:

| Field | Default Value | Description |
| :--- | :--- | :--- |
| **Email / Username** | `admin@leadforge.local` | Master administrative user |
| **Password** | `password123` | Default bootstrap password |
| **Full Name** | `Alex Mercer` | Agency Lead & Software Architect |
| **Role** | `ADMIN` | Superuser permissions |
| **Default Organization** | `Acme Growth Agency` | Default agency organization workspace |

> *You can change your password or create additional agency team members anytime from the API or database.*

---

## 🌐 How to Deploy the Entire Project to Vercel for Free

The repository is pre-configured with [`vercel.json`](vercel.json) as a **Unified Monorepo** that packages both the Next.js Frontend and the FastAPI Serverless Backend together.

### 📋 1-Click Deployment Steps:

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Deploy LeadForge to Vercel"
   git push origin main
   ```

2. **Deploy on Vercel**:
   * Go to **[vercel.com/new](https://vercel.com/new)** and log in with GitHub.
   * Click **Import** next to your repository.
   * **Root Directory**: Leave as `.` (root directory &mdash; do **not** select `frontend`).
   * **Framework Preset**: Will auto-detect Next.js + Python Serverless.

3. **Configure Environment Variables in Vercel**:
   Under **Environment Variables**, paste the keys from [`.env.example`](.env.example):
   * `HF_TOKEN`: Your Hugging Face access token.
   * `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`: Your SMTP credentials.
   * *(Optional)* `DATABASE_URL`: Free PostgreSQL connection string from [Neon.tech](https://neon.tech) or [Supabase](https://supabase.com) for permanent cloud database storage.
   * *(Optional)* `PERPLEXITY_API_KEY` / `GEMINI_API_KEY`.

4. Click **Deploy**!
   * Vercel will build and deploy the entire project at `https://your-project.vercel.app` at **$0.00 / month**.

---

## 🐳 Docker & Containerized Deployment

To run the entire system with Docker Compose:

```bash
docker-compose up --build -d
```

Services started:
* **PostgreSQL**: Port `5432`
* **Redis**: Port `6379`
* **LeadForge Backend**: Port `8000`
* **LeadForge Frontend**: Port `3000`

---

## 🧪 Automated Testing & Verification

Run the comprehensive 52-test automated suite covering SSRF safety, deterministic scoring, R&D report compilation, 4-step sequence cadences, and multi-model AI fallbacks:

```bash
python -m pytest backend/tests -v
```

* **Automated Tests**: **52 / 52 Passing in 8.9s with 0 warnings**.
* **Frontend TypeScript**: `npx tsc --noEmit` &mdash; **0 errors**.
* **Frontend ESLint**: `npm run lint` &mdash; **0 warnings**.

---

## 📄 License
MIT License. Built for high-performance agency prospecting and client acquisition.
