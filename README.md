# Dharma Lens — LegalAI Platform

> Enterprise-grade, multi-agent AI system for OCR, legal summarization, PII anonymization, multi-language translation, statutory graph retrieval, and constitutional analysis of Indian legal documents.

---

## ⚖️ Overview

**Dharma Lens** is an advanced AI platform designed specifically for the legal ecosystem in India. It empowers legal professionals, advocates, and judicial researchers to process complex legal documents—ranging from scanned court judgments, FIRs, and police reports to audio recordings of judicial hearings—with extreme speed, precision, and data privacy.

---

## ✨ Key Features

- 📄 **Advanced Document OCR & Audio Transcription**: High-precision text extraction from PDFs and scanned images via PyMuPDF, plus speech-to-text audio processing powered by OpenAI Whisper.
- 🛡️ **Automated Indian PII Redaction**: Integrates Microsoft Presidio to automatically identify and redact sensitive identifiers (Aadhaar numbers, PAN cards, phone numbers, email addresses, and personal names) before sending data to LLM inference pipelines.
- 🧠 **LangGraph Multi-Agent RAG**:
  - **Router Agent**: Dynamically classifies legal contexts (Constitutional vs. Criminal Law).
  - **Hybrid Vector Retriever**: Executes dual-mode retrieval combining Postgres `BM25` full-text keywords with `pgvector` HNSW cosine similarity.
  - **Graph Retriever**: Uses NetworkX to map statutory cross-references (e.g. mapping legacy Indian Penal Code `IPC` sections to corresponding Bharatiya Nyaya Sanhita `BNS` provisions).
  - **Synthesizer Agent**: Aggregates statutory insights into structured legal analysis payloads.
- 🌐 **22+ Indian Language Translation**: Context-aware legal translation across major Indian languages (Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada, Malayalam, Punjabi, etc.).
- 💬 **Interactive Document Q&A**: Context-grounded chat drawer allowing users to ask natural-language questions directly about uploaded documents.
- 📊 **RLHF Feedback Loop**: Human-in-the-loop thumbs-up/down ratings captured directly into Postgres for continuous retrieval optimization.

---

## 🏗️ System Architecture

Dharma Lens is constructed as a decoupled, multi-tier microservices architecture:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          React / Vite Frontend                              │
│         (Tailwind CSS, Shadcn UI, React Query, Supabase JS Client)          │
└──────────────────────┬──────────────────────────────┬───────────────────────┘
                       │ (Auth / Direct Upload)       │ (Processing Requests)
                       ▼                              ▼
          ┌────────────────────────┐      ┌────────────────────────┐
          │    Supabase Storage    │      │  Node.js API Gateway   │
          │   (Buckets + RLS)      │      │ (Express - Port 3000)  │
          └────────────┬───────────┘      └───────────┬────────────┘
                       │                              │ (Authenticated Proxy)
                       │                              ▼
                       │                  ┌────────────────────────┐
                       │                  │  Python FastAPI Engine │
                       │                  │     (Port 8000)        │
                       │                  └───────────┬────────────┘
                       │                              │
                       ├──────────────────────────────┼──────────────────────────────┐
                       ▼                              ▼                              ▼
         ┌────────────────────────┐      ┌────────────────────────┐    ┌───────────────────────────┐
         │ Presidio PII Redactor  │      │ LangGraph Multi-Agent  │    │ OpenRouter / OpenAI APIs  │
         │ (Aadhaar, PAN, Names)  │      │  RAG + NetworkX Graph  │    │  (Gemini 2.0, Llama 3.1)  │
         └────────────────────────┘      └────────────┬───────────┘    └───────────────────────────┘
                                                      │ (BM25 + HNSW pgvector)
                                                      ▼
                                         ┌──────────────────────────┐
                                         │ Supabase Postgres DB     │
                                         │ (pgvector, RLS, Hybrid)  │
                                         └──────────────────────────┘
```

---

## 🛠️ Technology Stack

- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, Shadcn UI, Lucide Icons, TanStack Query
- **API Gateway**: Node.js, Express, Axios, `@supabase/supabase-js`
- **AI & ML Engine**: Python 3.10+, FastAPI, LangGraph, NetworkX, PyMuPDF, Microsoft Presidio, OpenAI Whisper SDK, SentenceTransformers (`all-mpnet-base-v2`)
- **LLM Integration**: OpenRouter API (`google/gemini-2.0-pro-exp`, `meta-llama/llama-3.1-8b-instruct`)
- **Database & Storage**: Supabase PostgreSQL with `pgvector` HNSW vector indexes, BM25 `tsvector` GIN indexes, Row Level Security (RLS) policies
- **Queue & Infrastructure**: Docker, Docker Compose, Redis, Celery

---

## 📁 Repository Directory Structure

```
Dharma Lens/
├── src/                      # React 18 / Vite Frontend Application
│   ├── components/           # UI Components (DocumentUpload, ProcessingConfig, ResultsDisplay)
│   ├── pages/                # Application Views (Index, Auth, Dashboard, NotFound)
│   ├── integrations/         # Supabase Client & TypeScript Schema Definitions
│   └── lib/                  # MIME type definitions, helper utilities, and theme tokens
├── node_backend/             # Express.js API Gateway & JWT Auth Perimeter (Port 3000)
├── python_backend/           # FastAPI Machine Learning Engine & Multi-Agent RAG (Port 8000)
│   └── services/             # AI Pipeline, LangGraph RAG, PII Redaction, Law Ingestion
├── supabase/                 # Database Migrations, RLS Policies, Vector Indexes & Hybrid Functions
├── docker-compose.yml        # Docker Multi-Container Orchestration Setup
└── DHARMA_LENS_ARCHITECTURE.md # Deep-dive Architectural & File Inventory Document
```

---

## 🚀 Getting Started

### Prerequisites

- Node.js (v18+)
- Python (v3.10+)
- Docker & Docker Compose (Optional, for full stack containerized run)
- Supabase Account & Project Keys
- OpenRouter API Key

---

### Environment Setup

Create `.env.local` in the project root:

```env
VITE_SUPABASE_URL=https://your-supabase-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
VITE_SUPABASE_PUBLISHABLE_KEY=your-supabase-anon-key
VITE_API_GATEWAY_URL=http://localhost:3000
OPENROUTER_API_KEY=your-openrouter-api-key
OPENAI_API_KEY=your-openai-api-key
```

---

### Running via Docker Compose (Recommended)

To launch Redis, Python ML Engine, Celery Worker, and Node Gateway in unified containers:

```bash
docker-compose up --build
```

---

### Running Manually for Local Development

#### 1. Frontend Setup
```bash
npm install
npm run dev
```
The frontend will start at `http://localhost:8080` (or `http://localhost:5173`).

#### 2. Node API Gateway Setup
```bash
cd node_backend
npm install
node index.js
```
The gateway will start on port `3000`.

#### 3. Python ML Engine Setup
```bash
cd python_backend
pip install -r requirements.txt
python -m spacy download en_core_web_lg
uvicorn main:app --reload --port 8000
```
The ML engine will start on port `8000`.

---

## 📖 Detailed Documentation

For a comprehensive technical analysis of each file, statutory graph structures, RLS policies, and end-to-end trace diagrams, see [DHARMA_LENS_ARCHITECTURE.md](file:///d:/website%20projects/Dharma%20lens/DHARMA_LENS_ARCHITECTURE.md).

---

## 📜 License

Built for Indian Legal Professionals. All rights reserved. © 2026 Dharma Lens Platform.
