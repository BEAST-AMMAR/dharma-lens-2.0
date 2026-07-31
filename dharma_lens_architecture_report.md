# Dharma Lens — System Architecture & File Analysis Document

**Project Name:** Dharma Lens  
**Description:** Enterprise-grade Multi-Agent AI Legal Processing System for Indian Legal Documents  
**Date:** July 2026  

---

## Executive Summary

**Dharma Lens** is an advanced AI platform designed specifically for the legal domain in India. It handles complex, high-throughput processing of legal assets including court judgments, statutory provisions (IPC, BNS, Constitution of India), police reports, and audio recordings of judicial proceedings. 

Key capabilities include:
- High-accuracy Optical Character Recognition (OCR) across scanned PDF & image formats.
- Whisper-based Speech-to-Text audio transcription for court proceedings.
- Microsoft Presidio automated PII anonymization (Aadhaar, PAN cards, phone numbers, names, emails).
- Domain-specific AI summarization and 22+ Indian language legal translation.
- LangGraph Multi-Agent RAG with hybrid search (BM25 full-text + PostgreSQL `pgvector` HNSW index).
- Statutory mapping graph (`NetworkX`) connecting legacy IPC sections to updated BNS counterparts.
- Reinforcement Learning from Human Feedback (RLHF) thumb rating mechanism.

---

## 1. High-Level System Architecture

Dharma Lens is constructed as a decoupled, multi-tier microservices architecture containerized via Docker Compose.

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

## 2. Directory & File Inventory Analysis

### A. Frontend Layer (`src/`)

- `src/App.tsx`: Application entry point setting up React Router routes (`/`, `/auth`, `/dashboard`), TanStack Query client, and toast notifications.
- `src/pages/Index.tsx`: Modern landing page displaying feature highlights, platform capabilities, and quick access buttons.
- `src/pages/Auth.tsx`: Authentication screen for user login and signup with password validation and Supabase Auth integration.
- `src/pages/Dashboard.tsx`: Main user control panel featuring active document history, file upload dropzones, processing configuration cards, and real-time execution results.
- `src/components/DocumentUpload.tsx`: Handles file dropzone actions for PDF, Images, and Audio. Features `sanitizeFileName` logic to ensure file keys are clean before streaming files directly to Supabase Storage via `XMLHttpRequest` with upload progress metrics.
- `src/components/ProcessingConfig.tsx`: Provides configurable execution parameters (summary word count, language selection, OCR, Audio, RAG, Entity Extraction). Initiates POST requests to the Express gateway and manages continuous polling loops.
- `src/components/ResultsDisplay.tsx`: Tabbed view rendering AI Summaries, Interactive Context-Aware Document Chat Q&A, Full Text, Translations, Entity Badges, Constitutional Analysis, and RLHF feedback buttons.
- `src/integrations/supabase/client.ts`: Instantiates the Supabase client with persistent local storage session auto-refresh.
- `src/index.css`: HSL color variables defining the Indian Legal design theme (Navy Blue `#1B2A4A`, Legal Gold `#E5A93C`, dark/light themes).

---

### B. Gateway API Layer (`node_backend/`)

- `node_backend/index.js`: Express API Gateway running on port 3000.
  - Intercepts requests and enforces zero-trust authentication by validating Supabase JWT tokens via `supabase.auth.getUser()`.
  - Proxies `/api/process-document` requests to the Python engine (`http://python_engine:8000/process`).
  - Proxies job status polling (`/api/job/:jobId`) and document Q&A chat requests (`/api/chat`).
- `node_backend/package.json`: Node dependencies (`express`, `cors`, `@supabase/supabase-js`, `axios`, `dotenv`).
- `node_backend/Dockerfile`: Node 18 Alpine Docker image configuration.

---

### C. AI / Machine Learning Engine (`python_backend/`)

- `python_backend/main.py`: FastAPI server running on port 8000.
  - Exposes `/process`, `/job/{job_id}`, and `/chat` endpoints.
  - Implements an asynchronous job queue using `FastAPI BackgroundTasks` or `Celery`.
  - Enforces zero-trust token validation against Supabase Auth.
- `python_backend/worker.py`: Celery background task worker connected to Redis (`redis://redis:6379/0`).
- `python_backend/services/ai_pipeline.py`: Orchestrates document download, text extraction (`PyMuPDF` / `Whisper`), PII redaction, agentic RAG, and OpenRouter model cascades (`google/gemini-2.0-pro-exp-02-05:free`, `meta-llama/llama-3.1-8b-instruct:free`).
- `python_backend/services/agent_rag.py`: Multi-agent RAG workflow constructed with **LangGraph**:
  - `router_node`: Classifies document scope (Constitutional vs. Criminal Law).
  - `vector_retrieval_node`: Conducts hybrid semantic vector and BM25 searches.
  - `graph_retrieval_node`: Queries statutory cross-references (IPC to BNS mappings) via `NetworkX`.
  - `synthesizer_node`: Compiles agent findings into structured JSON legal reports.
- `python_backend/services/pii_redactor.py`: Uses Microsoft Presidio Analyzer & Anonymizer to strip sensitive data (Aadhaar, PAN, emails, phone numbers, names, IBANs) before LLM prompt submission.
- `python_backend/services/ingest_law.py`: Embeds legal texts using `sentence-transformers` (`all-mpnet-base-v2`, 768 dimensions) and stores vectors in Supabase.
- `python_backend/requirements.txt`: Python dependencies (`fastapi`, `uvicorn`, `supabase`, `PyMuPDF`, `langgraph`, `networkx`, `sentence-transformers`, `presidio-analyzer`, `presidio-anonymizer`, `celery`, `redis`).

---

### D. Database & Storage Layer (`supabase/migrations/`)

- `20251025110416_...sql`: Storage bucket configuration (`documents`, 50MB limit) with user folder isolation policies (`auth.uid()`) and user `profiles` table.
- `20251025111154_...sql`: Creates `processing_jobs` and `processing_results` tables with RLS policies and indexed foreign keys.
- `20260715150000_legal_knowledge_pgvector.sql`: Enables `pgvector` extension and creates `legal_knowledge` table with an HNSW cosine similarity index.
- `20260715150100_rlhf_feedback.sql`: Schema for storing RLHF user feedback (thumbs up/down ratings, reward scores, retrieval strategy).
- `20260715161700_hybrid_search.sql`: Adds full-text search `tsvector` columns, GIN index, and the PL/pgSQL function `hybrid_search_legal_knowledge` combining BM25 keyword relevance and vector similarity scores.
- `20251101...sql` & `20260715...sql`: Revokes public execute rights and hides system tables from GraphQL schemas for security compliance.

---

## 3. End-to-End Execution Flow

```
1. Document Upload (Browser ──► Supabase Storage)
   │
2. Trigger Processing (Browser ──► Node Gateway ──► Python FastAPI)
   │
3. Asynchronous Job Allocation (Python ──► Job ID Created ──► Background Task)
   │
4. Ingestion & Extraction (PyMuPDF for PDF / Whisper for Audio)
   │
5. PII Anonymization (Presidio Filter ──► Aadhaar, PAN, Names Removed)
   │
6. Multi-Agent RAG (LangGraph Router ──► Hybrid Vector Search + NetworkX Graph Traversal)
   │
7. Synthesis & LLM Cascade (OpenRouter Gemini 2.0 / Llama 3.1 ──► Legal Analysis Payload)
   │
8. DB Storage & UI Rendering (Results Stored in Supabase ──► Dashboard Polling Complete ──► Render Tabs)
```

---

## 4. Key Architectural Strengths

1. **Zero-Trust Security & PII Protection**: Authentication is strictly validated at both Gateway and ML engine tiers, while Presidio prevents privacy leakages.
2. **Hybrid RAG Intelligence**: Combines exact BM25 keyword matching with dense 768-dim vector embeddings and graph traversal for maximum statutory precision.
3. **Asynchronous Scalability**: Non-blocking background worker queues ensure fast client responses and zero request timeouts during heavy document processing.
4. **Modern UX/UI**: Clean React interface built with Shadcn primitives and tailored Indian legal palette tokens.
