# Technical Requirement Document (TRD)
## VidhiChakshu (विधि-चक्षु) 3.0: Architectural Blueprint & System Engineering Specifications
**Version:** 3.0.0  
**Status:** Production / Active  
**Author:** Lead AI Systems Architect  
**Date:** November 2026  

---

## 1. System Architecture Overview

VidhiChakshu is implemented as an enterprise-grade, privacy-respecting microservices architecture configured for dual-mode deployment: 100% air-gapped local offline execution, or high-throughput hybrid cloud failover.

```
+-------------------------------------------------------------------------+
|                         TIER 1: FRONTEND UI                            |
|             React 18 + TypeScript + Vite + Tailwind CSS + Radix UI       |
|  - 🧭 Interactive 2D Chauhaddi Boundary Visualizer (Cardinal Grid)      |
|  - 🌳 Ancestral Lineage & Pedigree Tree Generator (Shajra-e-Nasab)      |
|  - ⛓️ Chain-of-Title Audit & Defect Alert Console (Title Health Meter)   |
|  - 📥 Certified Legal PDF Report Downloader                             |
|  - 🎙️ Voice Input (Speech-to-Text via Web Speech Recognition)           |
|  - 🔊 Vernacular Audio Playback (Text-to-Speech via SpeechSynthesis)    |
|  - 📖 Archaic Revenue Lexicon Inspector (250+ historical terms)         |
+-------------------------------------------------------------------------+
                                    |
                                    | HTTP / REST (JWT Auth)
                                    v
+-------------------------------------------------------------------------+
|                     TIER 2: API GATEWAY SERVICE                         |
|                 Express.js + Node.js (Port 3000)                        |
|   - Fail-Fast Startup Validation (Zero hardcoded credentials)           |
|   - Supabase JWT Bearer Verification                                    |
|   - Dynamic Reverse Proxy & ArrayBuffer Streaming (`/api/export-pdf`)   |
|   - Rate Limiting, Helmet Security Headers, and Health Checks           |
+-------------------------------------------------------------------------+
                                    |
                                    | HTTP / REST (Internal Container Bus)
                                    v
+-------------------------------------------------------------------------+
|                  TIER 3: PYTHON ML INTELLIGENCE ENGINE                 |
|                   FastAPI + Uvicorn (Port 8000)                         |
|                                                                         |
|  +---------------------+  +---------------------+  +-----------------+  |
|  | Document Ingestion  |  | PII Anonymization   |  | Speech-to-Text  |  |
|  | - PyMuPDF (fitz)    |  | - Microsoft Presidio|  | - faster-whisper|  |
|  | - PIL Contrast/Sharp|  | - Indian PII Regex  |  |   (medium/INT8) |  |
|  +---------------------+  +---------------------+  +-----------------+  |
|  +---------------------+  +---------------------+  +-----------------+  |
|  | Historical Paleogr. |  | Multi-Agent RAG     |  | Certified PDF   |  |
|  | - Modi VLM Engine   |  | - NetworkX Graph    |  | - ReportLab 5.0 |  |
|  | - Halegannada VLM   |  | - TPA & Reg. Act    |  | - Seals & Tables|  |
|  | - Nastaliq VLM      |  | - BNS/BNSS/BSA/300A |  | - Title Health  |  |
|  +---------------------+  +---------------------+  +-----------------+  |
|  +---------------------+  +---------------------+  +-----------------+  |
|  | Archaic Lexicon Svc |  | Heritage Deed Intel |  | Hybrid LLM Hub  |  |
|  | - 250+ Terms DB     |  | - Chauhaddi Parser  |  | - Local Ollama  |  |
|  | - Modern Legal Maps |  | - Shajra Pedigree   |  |   (Qwen2.5-7B)  |  |
|  | - Citizen Plain-Lang|  | - Title Chain Audit |  | - OpenRouter    |  |
|  +---------------------+  +---------------------+  +-----------------+  |
+-------------------------------------------------------------------------+
           |                                             |
           | Postgres Protocol                           | HTTP / REST
           v                                             v
+------------------------------------+      +-----------------------------+
|        SUPABASE BACKEND            |      |     LOCAL / CLOUD LLMS      |
|  - PostgreSQL 15 + pgvector        |      |  - Ollama (Local:11434)     |
|  - Supabase Auth (JWT Services)    |      |  - OpenRouter API (Cloud)   |
|  - Storage Buckets ('documents')   |      +-----------------------------+
+------------------------------------+
```

---

## 2. Component Specifications

### 2.1 Backend Services Layout (`python_backend/services/`)
- `ai_pipeline.py`: Central orchestrator coordinating text extraction, PII anonymization, multi-modal LLM calling, citizen layman explanations, and structured heritage deed intelligence extraction.
- `htr_pipeline.py`: Paleographic vision pipeline applying contrast stretching and unsharp masking before dispatching base64 image prompts to multi-modal VLMs for Modi, Halegannada, and Nastaliq scripts.
- `lexicon_service.py`: In-memory catalog of 250+ historical Persian, Urdu, Marathi (Modi), and Kannada revenue terms, mapping archaic vocabulary into modern statutory equivalents.
- `pdf_generator.py`: ReportLab 5.0.1 document compiler rendering certified legal intelligence briefs with seals, Chauhaddi boundary tables, lineage schedules, chain-of-title timelines, defect alerts, and statutory citations.
- `agent_rag.py`: Multi-agent knowledge graph powered by NetworkX. Encodes statutory cross-mappings between IPC $\leftrightarrow$ BNS, CrPC $\leftrightarrow$ BNSS, Evidence Act $\leftrightarrow$ BSA, Transfer of Property Act 1882 (Sec 54, 58, 105, 122, 53A), Indian Registration Act 1908 (Sec 17, 49), Indian Stamp Act 1899 (Sec 33, 35), and Constitution Articles 14, 19, 21, and 300A.
- `pii_redactor.py`: High-assurance PII anonymizer masking Aadhaar and PAN numbers via lazy-loaded Presidio analyzer and strict regex guards.

### 2.2 API Gateway Endpoints (`node_backend/index.js`)
- `GET /health`: Gateway status and service version checks.
- `POST /api/process-document`: Dispatches file processing jobs to the Python engine.
- `GET /api/job/:jobId`: Polls job progress and retrieves structured results from memory/Supabase.
- `POST /api/chat`: Multi-turn conversational interface over document context.
- `POST /api/export-pdf`: Streams ReportLab-generated certified legal PDFs as `application/pdf`.

### 2.3 Frontend Application Layer (`src/`)
- `src/components/ResultsDisplay.tsx`: Modular results dashboard providing 9 specialized inspection tabs (Citizen Summary, Chauhaddi 2D Map, Pedigree Tree, Title Chain Audit, Archaic Lexicon, Legal Brief, Statutes, Q&A Chat, and Extracted Text).
- `src/components/ProcessingConfig.tsx`: Fine-grained paleography and engine configuration panel.
- `src/pages/Dashboard.tsx`: Document upload, persistent history gallery, and session management.

---

## 3. Data Schema & Supabase Database Tables

### 3.1 `processing_jobs`
```sql
CREATE TABLE processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id TEXT NOT NULL,
    user_id UUID REFERENCES auth.users(id),
    status TEXT NOT NULL CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    progress FLOAT DEFAULT 0.0,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3.2 `processing_results`
```sql
CREATE TABLE processing_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id TEXT NOT NULL,
    user_id UUID REFERENCES auth.users(id),
    extracted_text TEXT,
    summary TEXT,
    translation TEXT,
    entities JSONB,
    legal_analysis JSONB,
    metadata JSONB, -- Stores chauhaddi, lineage, title_chain, title_health_score, title_defects, archaic_terms, layman_summary
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3.3 `legal_knowledge` (Vector Store)
```sql
CREATE TABLE legal_knowledge (
    id BIGSERIAL PRIMARY KEY,
    source_type TEXT NOT NULL,
    section_number TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    superseded_by TEXT,
    replaces TEXT,
    embedding VECTOR(768),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 4. Security & Compliance
- **Zero Raw Data Persistence**: Unredacted documents never leave the local environment without explicit PII redaction.
- **Fail-Fast Validation**: Gateways and engines fail immediately upon initialization if required environment variables or authentication keys are missing.
- **JWT Protection**: All inter-service calls require validated Supabase authentication tokens.
