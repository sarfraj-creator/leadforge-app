# 📘 LeadForge: Complete Step-by-Step User Manual, Pipeline Walkthrough & Real-World Example

Welcome to the **LeadForge Master User Guide**. This guide explains every step of the autonomous prospecting pipeline using a **concrete real-world agency example**, from initial discovery to auto-followups, auto-stopping on reply, and closing deals.

---

## 📑 Table of Contents
1. [Prerequisites & First-Time Installation](#1-prerequisites--first-time-installation)
2. [How to Run the Application (Terminal by Terminal)](#2-how-to-run-the-application-terminal-by-terminal)
3. [🎯 End-to-End Real-World Walkthrough Example: Dental Clinic Campaign](#3--end-to-end-real-world-walkthrough-example-dental-clinic-campaign)
   - [Phase 1: Ingesting Leads via Discovery](#phase-1-ingesting-leads-via-discovery)
   - [Phase 2: Automated Technical Website Audit & Hardening](#phase-2-automated-technical-website-audit--hardening)
   - [Phase 3: Lead Categorization & Segmentation](#phase-3-lead-categorization--segmentation)
   - [Phase 4: Generating the Standalone Technical R&D Audit Report](#phase-4-generating-the-standalone-technical-rd-audit-report)
   - [Phase 5: AI Outreach Email & Rich HTML Preview](#phase-5-ai-outreach-email--rich-html-preview)
   - [Phase 6: Autonomous 4-Step Follow-Up Sequence (Day 0, 3, 7, 14)](#phase-6-autonomous-4-step-follow-up-sequence-day-0-3-7-14)
   - [Phase 7: Automated Follow-Up Execution (Cycle Runner)](#phase-7-automated-follow-up-execution-cycle-runner)
   - [Phase 8: Inbound Reply, Auto-Stop & Sentiment Classification](#phase-8-inbound-reply-auto-stop--sentiment-classification)
   - [Phase 9: Unified Inbox & CRM Stage Progression to Closed Won](#phase-9-unified-inbox--crm-stage-progression-to-closed-won)
4. [How to Configure AI Multi-Models & SMTP in Settings](#4-how-to-configure-ai-multi-models--smtp-in-settings)
5. [Troubleshooting & FAQ](#5-troubleshooting--faq)

---

## 1. Prerequisites & First-Time Installation

Before starting, ensure you have:
* **Python 3.10+** installed: [python.org](https://www.python.org/downloads/)
* **Node.js 18+ & npm** installed: [nodejs.org](https://nodejs.org/)

Open your terminal inside the project directory:
```bash
cd d:/ai-system-s
```

---

## 2. How to Run the Application (Terminal by Terminal)

Start **two terminals**: one for the Python FastAPI backend (Port 8000), and one for the Next.js frontend (Port 3000).

### 🖥️ Terminal 1: Start Backend (FastAPI API Engine)
```bash
# 1. Activate virtual environment:
# On Windows (PowerShell / CMD):
.venv\Scripts\activate
# On macOS / Linux:
# source .venv/bin/activate

# 2. Install dependencies (if not installed):
pip install -r backend/requirements.txt

# 3. Start FastAPI server on port 8000:
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
* **Backend Live URL**: `http://127.0.0.1:8000`
* **Swagger API Documentation**: `http://127.0.0.1:8000/docs`

---

### 🌐 Terminal 2: Start Frontend (Next.js Web Dashboard)
```bash
# In a second terminal:
cd d:/ai-system-s/frontend

# Install dependencies (if not installed):
npm install

# Start Next.js dev server on port 3000:
npm run dev -- -p 3000
```
* **Frontend Web Dashboard**: **`http://localhost:3000`**

---

### 🔑 Default Administrator Login Credentials

| Field | Default Value | Description |
| :--- | :--- | :--- |
| **Email / Username** | `admin@leadforge.local` | Default administrator username |
| **Password** | `password123` | Default bootstrap password |
| **Full Name** | `Alex Mercer` | Agency Lead & Software Architect |
| **Role** | `ADMIN` | Superuser administrative privileges |
| **Organization** | `Acme Growth Agency` | Default agency organization workspace |

---

## 3. 🎯 End-to-End Real-World Walkthrough Example: Dental Clinic Campaign

Let's follow a complete, realistic agency campaign from start to finish:

> **Campaign Scenario:** You run a digital web agency (*Acme Web & Engineering*) offering high-performance website redesigns. You want to prospect **Dentists in London with broken mobile sites and slow page speeds**.

---

### Phase 1: Ingesting Leads via Discovery

1. Open your browser to **[http://localhost:3000/discovery](http://localhost:3000/discovery)**.
2. Select **"OpenStreetMap (OSM)"** or **"Autonomous AI Search"**.
3. Fill in the Discovery form:
   * **Campaign / Job Name**: `London Dental Redesign Sprint`
   * **Industry / Amenity**: `dentist`
   * **Location**: `London, UK`
   * **Max Leads**: `25`
4. Click **"Launch Discovery Job"**.

```
[SYSTEM ACTION]:
- Queries global OpenStreetMap Overpass API for London dentists.
- Discovers: "Dental Beauty Islington", "Smile Art Dental", "City Dental Practice".
- Extracts official domain: dentalbeauty.co.uk, direct phone, and GPS coordinates.
```

---

### Phase 2: Automated Technical Website Audit & Hardening

As soon as leads are ingested, LeadForge's automated crawler executes:

1. **SSRF Safety Check**: Validates that target domains resolve to public IPs (blocks private RFC 1918 addresses).
2. **Deterministic HTML Crawler**: Measures:
   * **Page Load Speed**: `3420 ms` (Slow &gt; 3000ms threshold &rarr; Core Web Vitals issue).
   * **Mobile Viewport**: Missing mobile breakpoint meta tags & small tap targets.
   * **SEO Structure**: Missing H1 hierarchy, empty image alt tags.
   * **Security**: SSL certificate expiration check.
   * **Tech Stack**: Detected WordPress 5.4 + unoptimized plugins.
3. **Decoupled 5-Part Lead Scoring**:
   * Business Fit: `95/100` | Opportunity Score: `90/100` | Confidence: `92/100`
   * **Overall Lead Score**: **`92/100 (HOT LEAD)`**

---

### Phase 3: Lead Categorization & Segmentation

Navigate to **[http://localhost:3000/leads](http://localhost:3000/leads)**.

LeadForge automatically segregates all leads into **3 dedicated tabs**:

```
 ┌────────────────────────────────┬───────────────────────────────┬──────────────────────────────┐
 │ 🎨 HAS_WEBSITE_REDESIGN (18)   │ 🚀 NO_WEBSITE_NEW_BUILD (4)   │ 🔥 BUYER_INTENT_POST (3)     │
 └────────────────────────────────┴───────────────────────────────┴──────────────────────────────┘
```

* **🎨 HAS_WEBSITE_REDESIGN**: `Dental Beauty Islington` appears here because it has an existing domain with measurable mobile and performance defects.
* **🚀 NO_WEBSITE_NEW_BUILD**: Verified businesses operating with no website found (pitching new digital builds).
* **🔥 BUYER_INTENT_POST**: Businesses with live RFQs or social posts seeking web developers.

---

### Phase 4: Generating the Standalone Technical R&D Audit Report

1. Click on `Dental Beauty Islington` &rarr; click **"Technical Audit Report"** (or view in **[http://localhost:3000/audits](http://localhost:3000/audits)**).
2. The modal instantly generates the **R&D Technical Audit Report**:
   * **Executive Scorecard Gauges**: Mobile (45/100), Speed (38/100), SEO (62/100), Security (85/100).
   * **Observed Evidence Snippet**: *"Observed server response time of 3.42s and viewport overflow causing 42% mobile booking abandonment."*
   * **4-Phase Strategic Modernization Blueprint**:
     * Phase 1: Next.js Responsive Architecture Migration.
     * Phase 2: Core Web Vitals Optimization (Sub-800ms LCP).
     * Phase 3: Mobile Booking & Appointment CRO Funnel.
     * Phase 4: Security Hardening & Zero-Downtime Cutover.
   * **Agency Commercial Proposal**: ROI analysis showing +35% patient booking increase.
3. Click **"Print / Export PDF"** if you want an offline client deliverable.

---

### Phase 5: AI Outreach Email & Rich HTML Preview

1. On the lead card, click **"Send Email"**.
2. Click **"Generate with AI"**:
   * LeadForge uses the configured Hugging Face Copywriting model (`Mistral-7B` / `Llama-3`) to generate factual, non-generic copy quoting the measured defects:
     > *"Hi Team at Dental Beauty Islington, while reviewing digital healthcare providers in London, I noticed your mobile site response time is currently 3.4s, which is impacting prospective patient bookings..."*
3. Toggle to the **"👁️ Rich HTML Email Preview"** tab:
   * View the branded executive layout: agency banner, embedded audit scorecard gauges, defect evidence quote, and the **"📎 Attached: Technical-Audit-Report-Dental-Beauty-Islington.html"** callout box.
4. Click **"Dispatch Email"**.

---

### Phase 6: Autonomous 4-Step Follow-Up Sequence (Day 0, 3, 7, 14)

Navigate to **[http://localhost:3000/campaigns](http://localhost:3000/campaigns)**.

When you enroll `Dental Beauty Islington` into the **Website Redesign Sequence**, the automated sequence cadence begins:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                      AUTONOMOUS 4-STEP SEQUENCE TIMELINE                               │
├───────────────┬───────────────────────────────────┬────────────────────────────────────┤
│ Cadence Step  │ Timing                            │ Content & Deliverables             │
├───────────────┼───────────────────────────────────┼────────────────────────────────────┤
│ 📨 Step 1     │ Day 0 (Immediate)                 │ Technical Audit Brief + Attached   │
│               │                                   │ Standalone HTML/PDF R&D Report     │
│ 📨 Step 2     │ Day 3 (3 days after Step 1)       │ UX Mobile Wireframe Solution       │
│               │                                   │ & Booking Conversion Preview       │
│ 📨 Step 3     │ Day 7 (4 days after Step 2)       │ Local London Dental Speed          │
│               │                                   │ & Competitor Benchmark Insight     │
│ 📨 Step 4     │ Day 14 (7 days after Step 3)      │ Polite Final Breakup & Permanent   │
│               │                                   │ Cloud Audit Link                   │
└───────────────┴───────────────────────────────────┴────────────────────────────────────┘
```

---

### Phase 7: Automated Follow-Up Execution (Cycle Runner)

The background worker ([`backend/app/workers/sequence_runner.py`](file:///d:/ai-system-s/backend/app/workers/sequence_runner.py)) operates automatically:

1. Checks the database every cycle for leads with `status="ACTIVE"`.
2. Calculates elapsed days since the last sent email:
   * If `current_step == 1` and `elapsed_days >= 3` &rarr; **Automatically compiles and dispatches Step 2**.
   * If `current_step == 2` and `elapsed_days >= 4` &rarr; **Automatically compiles and dispatches Step 3**.
   * If `current_step == 3` and `elapsed_days >= 7` &rarr; **Automatically compiles and dispatches Step 4**.
3. You can also trigger an immediate cycle evaluation anytime by clicking **"Run Automated Cycle Now"** on the Campaigns page.

---

### Phase 8: Inbound Reply, Auto-Stop & Sentiment Classification

Now imagine **Dental Beauty Islington** replies to your outreach:

> *"Hi Alex, thanks for the audit report. We noticed our mobile booking drop-off last month. Can we discuss this Thursday at 2:00 PM?"*

#### What Happens Automatically:
1. **🛑 Immediate Sequence Auto-Stop**:
   * LeadForge immediately sets `sequence_status = "STOPPED_REPLIED"`.
   * **No further automated follow-up emails (Step 2, 3, or 4) will be sent** to prevent embarrassing double-messaging.
2. **🧠 AI Sentiment & Intent Classification**:
   * The Hugging Face Classification model evaluates the response:
     * **Classification**: `Interested` / `Meeting Request`
     * **Sentiment Score**: `+0.92 (Extremely Positive)`
     * **Reasoning**: *"Prospect confirmed interest in discussing the mobile booking audit on Thursday."*
3. **📊 Automatic CRM Progression**:
   * The deal card moves automatically from `Contacted` &rarr; **`Interested / Meeting Scheduled`**.

---

### Phase 9: Unified Inbox & CRM Stage Progression to Closed Won

1. Navigate to **[http://localhost:3000/inbox](http://localhost:3000/inbox)**.
2. Click on the `Dental Beauty Islington` conversation thread:
   * Review the outbound sent message (with the attached report badge) and the inbound prospect reply.
3. Use the **Direct Reply Composer** at the bottom to send your meeting confirmation:
   > *"Hi Dr. Sarah, Thursday at 2:00 PM works perfectly. I will send over a calendar invite with the video link."*
4. Go to **[http://localhost:3000/crm](http://localhost:3000/crm)**:
   * Drag the card to **`Closed Won`** once the contract is signed!

---

## 4. How to Configure AI Multi-Models & SMTP in Settings

Navigate to **[http://localhost:3000/settings](http://localhost:3000/settings)**.

### 🧠 1. AI Multi-Model Tab (`/settings?tab=ai`):
* Enter your **`HF_TOKEN`** (Hugging Face User Access Token).
* Customize any of the 4 specialized open-source model slots:
  * ✍️ **1. Outreach Copywriter**: `mistralai/Mistral-7B-Instruct-v0.3` (or `meta-llama/Meta-Llama-3-8B-Instruct`)
  * 🔍 **2. Technical Audit Analyst**: `Qwen/Qwen2.5-Coder-7B-Instruct` (or `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`)
  * 💬 **3. Reply Sentiment Classifier**: `meta-llama/Meta-Llama-3-8B-Instruct` (or `cardiffnlp/twitter-roberta-base-sentiment-latest`)
  * 🧠 **4. NLP Query Extractor**: `meta-llama/Meta-Llama-3-8B-Instruct`
* Click **"Save AI Configuration"** (applied live with 0 downtime).

---

### ✉️ 2. Outbound SMTP Email Tab (`/settings?tab=smtp`):
* **Gmail Setup**:
  1. Google Account &rarr; Security &rarr; Enable 2-Step Verification.
  2. Search *App Passwords* &rarr; Create one named `LeadForge`.
  3. Enter:
     * **Host**: `smtp.gmail.com`
     * **Port**: `587`
     * **User**: `your-email@gmail.com`
     * **Password**: `your-16-char-app-password`
     * **From Email**: `your-email@gmail.com`
* Click **"Test Connection"** &rarr; Verify green handshake &rarr; Click **"Save Outbound SMTP Settings"**.

---

## 5. Troubleshooting & FAQ

### Q1: Why were emails not sending to real inboxes?
* **Answer**: If `SMTP_HOST` is left blank, LeadForge operates in **Safe Simulation Mode** so you can preview everything without sending spam. Once you enter your Gmail App Password or SendGrid credentials in Settings &rarr; SMTP, it sends real emails with attachments.

### Q2: How does Auto-Stop prevent emailing prospects who already replied?
* **Answer**: In [`backend/app/workers/sequence_runner.py`](file:///d:/ai-system-s/backend/app/workers/sequence_runner.py), the sequence worker checks if an inbound message exists in the thread. If found, the sequence is immediately marked `STOPPED_REPLIED` and skipped.

### Q3: How do I change an AI model in the future?
* **Answer**: Go to **[http://localhost:3000/settings?tab=ai](http://localhost:3000/settings?tab=ai)**, type the new Hugging Face model repository ID in any slot, and click Save.

### Q4: How do I deploy the whole project to Vercel for free?
* **Answer**: Follow the 1-Click guide in [README.md](README.md#-how-to-deploy-the-entire-project-to-vercel-for-free). Both Next.js and FastAPI deploy together using [`vercel.json`](vercel.json).
