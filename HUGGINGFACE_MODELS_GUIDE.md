# 🧠 LeadForge: Hugging Face Multi-Model Ensemble Guide & Model Swapping Manual

Complete technical guide to the **Task-Specialized Multi-Model Hugging Face Architecture** in LeadForge, curated open-source model recommendations, and step-by-step instructions on how to swap or customize models in the future.

---

## 📑 Table of Contents
1. [Why a Multi-Model Architecture?](#1-why-a-multi-model-architecture)
2. [The 4 Specialized AI Task Slots](#2-the-4-specialized-ai-task-slots)
3. [Curated Model Catalog & Recommended Swaps](#3-curated-model-catalog--recommended-swaps)
4. [How to Change / Swap Models in the Future](#4-how-to-change--swap-models-in-the-future)
5. [How to Get Your Free Hugging Face Token](#5-how-to-get-your-free-hugging-face-token)
6. [Offline & Local LLM Integration (Ollama / vLLM)](#6-offline--local-llm-integration-ollama--vllm)
7. [Deterministic Fallback & Failure Protection](#7-deterministic-fallback--failure-protection)

---

## 1. Why a Multi-Model Architecture?

In traditional systems, a single general-purpose LLM is used for everything. This leads to mediocre results: code models make stiff copywriters, and creative models hallucinate technical audit diagnostics.

LeadForge implements **Task-Specialized Model Routing**:

```
                             ┌───────────────────────────────────────────────┐
                             │    LeadForge Multi-Model Hugging Face Engine  │
                             └──────────────────────┬────────────────────────┘
                                                    │
         ┌──────────────────────────┬───────────────┴───────────────┬──────────────────────────┐
         ▼                          ▼                               ▼                          ▼
  ✍️ OUTREACH COPYWRITER     🔍 CODE & CWV AUDITOR         💬 SENTIMENT & INTENT CLASSIFIER   🧠 NLP QUERY EXTRACTOR
  Model: Mistral-7B / Llama3 Model: Qwen2.5-Coder / DeepSeek Model: Llama-3 / RoBERTa        Model: Llama-3 / Mistral
  • High-conversion cold     • Deep code defect diagnosis  • Inbound reply classification     • Translates natural language
    email synthesis          • Performance optimization    • Automatic sequence stopping        search queries into filters
  • Personalized hooks       • Modernization blueprints    • Multi-class intent categorization• Decision-maker mining
```

---

## 2. The 4 Specialized AI Task Slots

### ✍️ Slot 1: Cold Outreach Copywriter
* **Internal Setting Key**: `HF_OUTREACH_MODEL`
* **Purpose**: Generates persuasive, concise cold emails (under 125 words) personalized strictly with observed website defect evidence and low-friction calls to action.
* **Default Model**: `mistralai/Mistral-7B-Instruct-v0.3`

---

### 🔍 Slot 2: Technical Audit & Defect Analyst
* **Internal Setting Key**: `HF_AUDIT_MODEL`
* **Purpose**: Analyzes measured performance metrics, DOM structure, SSL certificates, Core Web Vitals, and synthesizes 4-phase strategic modernization roadmaps with ROI estimates.
* **Default Model**: `Qwen/Qwen2.5-Coder-7B-Instruct`

---

### 💬 Slot 3: Inbound Reply & Sentiment Classifier
* **Internal Setting Key**: `HF_CLASSIFICATION_MODEL`
* **Purpose**: Reads incoming prospect replies and accurately classifies them into categories (`Interested`, `Meeting Request`, `Pricing Request`, `Question`, `Not Interested`, `Unsubscribe`) to automatically pause sequence cadences.
* **Default Model**: `meta-llama/Meta-Llama-3-8B-Instruct`

---

### 🧠 Slot 4: NLP Query & Entity Mining
* **Internal Setting Key**: `HF_EXTRACTION_MODEL`
* **Purpose**: Translates conversational plain-English search queries (e.g. *"Find 500 dentists in Miami with slow mobile websites"*) into structured query filters.
* **Default Model**: `meta-llama/Meta-Llama-3-8B-Instruct`

---

## 3. Curated Model Catalog & Recommended Swaps

You can plug in **ANY** open-source model available on Hugging Face Serverless Inference. Here are the top tested recommendations:

### 🏆 Best Models for Copywriting & Email Outreach (Slot 1)
| Model ID | Provider | Parameters | Strengths |
| :--- | :--- | :--- | :--- |
| `mistralai/Mistral-7B-Instruct-v0.3` | Mistral AI | 7B | **(Default)** High conversion tone, concise, no corporate fluff. |
| `meta-llama/Meta-Llama-3-8B-Instruct` | Meta | 8B | Exceptionally natural conversational English and personalization. |
| `google/gemma-2-9b-it` | Google | 9B | Sophisticated vocabulary and structured reasoning. |
| `microsoft/Phi-3.5-mini-instruct` | Microsoft | 3.8B | Ultra-fast inference with minimal latency. |

---

### 🏆 Best Models for Technical Audits & Code Analysis (Slot 2)
| Model ID | Provider | Parameters | Strengths |
| :--- | :--- | :--- | :--- |
| `Qwen/Qwen2.5-Coder-7B-Instruct` | Alibaba / Qwen | 7B | **(Default)** State-of-the-art coding and technical defect diagnosis. |
| `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B` | DeepSeek | 7B | Chain-of-thought technical reasoning and architectural blueprints. |
| `meta-llama/Meta-Llama-3.1-8B-Instruct` | Meta | 8B | 128k context window for large DOM and audit payloads. |
| `bigcode/starcoder2-7b` | BigCode | 7B | High accuracy for technology stack analysis. |

---

### 🏆 Best Models for Reply Sentiment & Intent Classification (Slot 3)
| Model ID | Provider | Parameters | Strengths |
| :--- | :--- | :--- | :--- |
| `meta-llama/Meta-Llama-3-8B-Instruct` | Meta | 8B | **(Default)** Multi-intent nuance detection (detects subtle buying signals). |
| `cardiffnlp/twitter-roberta-base-sentiment-latest` | Cardiff NLP | 125M | Dedicated micro-classifier with sub-50ms inference. |
| `distilbert-base-uncased-finetuned-sst-2-english` | Hugging Face | 66M | Lightweight, zero-latency binary sentiment scoring. |

---

### 🏆 Best Models for NLP Discovery & Extraction (Slot 4)
| Model ID | Provider | Parameters | Strengths |
| :--- | :--- | :--- | :--- |
| `meta-llama/Meta-Llama-3-8B-Instruct` | Meta | 8B | **(Default)** Perfect JSON adherence for search compilation. |
| `mistralai/Mistral-7B-Instruct-v0.3` | Mistral AI | 7B | Rapid entity mining from unstructured website crawls. |
| `dslim/bert-base-NER` | Hugging Face | 110M | Specialized Named Entity Recognition (Persons, Places, Orgs). |

---

## 4. How to Change / Swap Models in the Future

You have **3 simple ways** to swap models anytime:

### Method 1: Via the Web Dashboard (Recommended & Instant)
1. Open your browser to **[http://localhost:3005/settings?tab=ai](http://localhost:3005/settings?tab=ai)** (or your deployed URL).
2. Scroll to the **HUGGING FACE Multi-Model Specialized Ensemble Suite** card.
3. Type or paste your desired Hugging Face Model ID in any of the 4 slots.
4. Click **"Save AI Configuration"**.
   > *Changes take effect immediately across all background workers and live API requests without restarting the server!*

---

### Method 2: Via the `.env` Configuration File
Edit your root `.env` file with any model repository ID:

```ini
# Primary User Token
HF_TOKEN=hf_your_token_here

# Swap any model slot:
HF_OUTREACH_MODEL=meta-llama/Meta-Llama-3-8B-Instruct
HF_AUDIT_MODEL=deepseek-ai/DeepSeek-R1-Distill-Qwen-7B
HF_CLASSIFICATION_MODEL=meta-llama/Meta-Llama-3-8B-Instruct
HF_EXTRACTION_MODEL=mistralai/Mistral-7B-Instruct-v0.3
```

---

### Method 3: Via REST API
Send an authenticated `POST` request to `/api/settings/ai`:

```bash
curl -X POST http://localhost:8000/api/settings/ai \
  -H "Content-Type: application/json" \
  -d '{
    "hf_outreach_model": "google/gemma-2-9b-it",
    "hf_audit_model": "Qwen/Qwen2.5-Coder-7B-Instruct",
    "hf_classification_model": "meta-llama/Meta-Llama-3-8B-Instruct",
    "hf_extraction_model": "mistralai/Mistral-7B-Instruct-v0.3"
  }'
```

---

## 5. How to Get Your Free Hugging Face Token

Hugging Face provides free Serverless Inference for open-source models:

1. Create a free account at **[huggingface.co](https://huggingface.co)**.
2. Go to **Settings &rarr; Access Tokens**: [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
3. Click **"New token"** &rarr; Select **Type: Read** &rarr; Name it `LeadForge`.
4. Copy the generated token (`hf_...`).
5. Paste it in your `.env` or in **Settings &rarr; AI Configuration** in LeadForge.

> [!TIP]
> **Gated Models (e.g. Meta Llama 3):** To use Llama 3 models, visit the model page on Hugging Face (e.g., [meta-llama/Meta-Llama-3-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct)), click **"Accept License"**, and your `HF_TOKEN` will instantly have access!

---

## 6. Offline & Local LLM Integration (Ollama / vLLM)

If you wish to run completely offline without sending any data over the internet:

1. Install **[Ollama](https://ollama.ai)** on your local machine.
2. Pull your desired models:
   ```bash
   ollama pull mistral
   ollama pull qwen2.5-coder:7b
   ollama pull llama3:8b
   ```
3. Set your provider in `.env`:
   ```ini
   HF_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   ```

---

## 7. Deterministic Fallback & Failure Protection

LeadForge includes built-in **Cascading Fallback Protection**:

* If a Hugging Face model experiences cold-start latency or network timeouts, LeadForge automatically falls back to:
  1. Primary Chat Completion Endpoint (`/v1/chat/completions`)
  2. Standard Inference Endpoint (`/models/{model}`)
  3. Deterministic Factual Rule-Based Synthesizer (guaranteeing your pipeline **never crashes or halts** even if offline).
