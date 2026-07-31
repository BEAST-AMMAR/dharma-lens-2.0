# Dharma Lens — Comprehensive Security, Bug & Vulnerability Audit Report

**Target System:** Dharma Lens (LegalAI Platform)  
**Audit Date:** July 2026  
**Auditor:** AntiGravity Security & Software Engineering Inspection Suite  
**Scope:** Full-Stack Repository Audit (`src/`, `node_backend/`, `python_backend/`, `supabase/`)  
**Assessment Result:** ⚠️ **ACTION REQUIRED** — Multiple Critical Security Flaws, Hardcoded Credentials, Broken Endpoints, and Mock Fallbacks Identified.

---

## Executive Summary

A comprehensive code and architecture audit was conducted across all files, APIs, database schemas, and service integrations of the **Dharma Lens** platform. While the project exhibits a strong architectural layout (decoupled React frontend, Express API Gateway, FastAPI engine, LangGraph RAG, and Supabase Postgres/Vector), several **critical security vulnerabilities, authentication bypass risks, hardcoded credentials, unhandled image OCR failures, mock RAG stubs, and infinite client polling loops** were discovered.

This document details all identified findings categorized by severity, along with precise line locations and code remediation guidance.

---

## 1. Vulnerability & Severity Matrix Summary

| Severity | Category | Count | Primary Impact |
| :--- | :--- | :---: | :--- |
| 🔴 **CRITICAL** | Authentication & Access Control | 2 | Authorization bypass in Job Polling & Chat endpoints |
| 🟠 **HIGH** | Hardcoded Secrets & Credentials | 3 | Exposure of project Supabase URLs & fallback key vulnerabilities |
| 🟠 **HIGH** | Unhandled Application Exceptions | 2 | Image OCR crash & Presidio Spacy missing model startup crash |
| 🟡 **MEDIUM** | Stubbed & Mock Implementations | 2 | Vector RAG & Knowledge Graph returning dummy hardcoded results |
| 🟡 **MEDIUM** | Frontend Reliability & UX | 2 | Infinite polling loops & inconsistent environment variable keys |
| 🔵 **LOW** | Code Cleanup & Schema Gaps | 2 | Unlinked RLHF document IDs & brittle string endpoint replacement |

---

## 2. Deep-Dive Security Vulnerabilities & Threats

### 🔴 [CRITICAL] SEC-01: Unauthorized Access Control Bypass in Job Status Endpoint
- **Location:** `node_backend/index.js` — Lines 66–78 (`GET /api/job/:jobId`)
- **Vulnerability Type:** Missing Authentication & Authorization (Broken Object Level Authorization - BOLA)
- **Description:** The `/api/job/:jobId` endpoint on the API Gateway does **not** check for a `Bearer` token or validate the user's identity. Anyone who obtains or guesses a valid UUID `jobId` can query job status and view extracted document text, legal analyses, PII summaries, and translations without authentication.
- **Remediation Code:**
  ```javascript
  // Fix in node_backend/index.js
  app.get('/api/job/:jobId', async (req, res) => {
    const authHeader = req.headers.authorization;
    if (!authHeader) return res.status(401).json({ error: 'Unauthorized' });
    
    const { data: { user }, error } = await supabase.auth.getUser(authHeader.replace('Bearer ', ''));
    if (error || !user) return res.status(401).json({ error: 'Invalid token' });
    
    // Proceed with proxying to Python ML engine
  });
  ```

---

### 🔴 [CRITICAL] SEC-02: Pseudo-Authentication Token Check in Python Chat Endpoint
- **Location:** `python_backend/main.py` — Lines 44–48 (`POST /chat`)
- **Vulnerability Type:** Authentication Bypass via Token Header Inspection Omission
- **Description:** In `main.py`, the `/process` endpoint (lines 89–98) correctly validates the JWT with Supabase (`supabase.auth.get_user(token)`). However, the `/chat` endpoint only checks `if not authorization: raise HTTPException(401)`. Any arbitrary, forged non-empty string in the `Authorization` header (e.g., `Authorization: Bearer dummy_fake_token`) satisfies this check, allowing unauthenticated API consumers to execute chat requests and burn model API credits.
- **Remediation Code:**
  ```python
  # Fix in python_backend/main.py
  @app.post("/chat")
  async def chat_with_document(request: ChatRequest, authorization: str = Header(None)):
      if not authorization:
          raise HTTPException(status_code=401, detail="Unauthorized")
      
      token = authorization.replace("Bearer ", "")
      user = supabase.auth.get_user(token)
      if not user:
          raise HTTPException(status_code=401, detail="Invalid token")
  ```

---

### 🟠 [HIGH] SEC-03: Hardcoded Supabase Project URLs & Insecure Fallback Keys
- **Location:**
  - `node_backend/index.js` (Lines 15–16)
  - `python_backend/main.py` (Lines 92–93)
  - `python_backend/services/ai_pipeline.py` (Lines 9–10)
  - `python_backend/services/ingest_law.py` (Lines 5–6)
- **Vulnerability Type:** Hardcoded Default Credentials & Environment Injection Risks
- **Description:** Across multiple backend services, the fallback for missing environment variables is hardcoded to a specific Supabase project URL (`https://harbkllyyyatxqwolsea.supabase.co`) and dummy strings like `"YOUR_ANON_KEY"` or `"YOUR_SERVICE_ROLE_KEY"`. If environment loading fails in production, requests will attempt connections against hardcoded URLs or fail unpredictably.
- **Remediation:** Enforce strict validation on service boot. If required environment variables are missing, fail startup explicitly:
  ```python
  SUPABASE_URL = os.environ.get("VITE_SUPABASE_URL")
  if not SUPABASE_URL:
      raise RuntimeError("CRITICAL: VITE_SUPABASE_URL environment variable is missing!")
  ```

---

## 3. Application Bugs & Unintentional Failure Modes

### 🟠 [HIGH] BUG-01: Image OCR Processing Hard Exception Crash
- **Location:** `python_backend/services/ai_pipeline.py` — Lines 95–103
- **Issue:** The pipeline handles PDF files via PyMuPDF (`extract_text_from_pdf`). However, when `config.enableOCR` is true for non-PDF images (e.g., `.png`, `.jpg`, `.tiff`), line 99 contains an omitted fallback comment (`pass`). Consequently, `extracted_text` remains empty (`""`), triggering line 102:
  ```python
  raise Exception("Failed to extract text or transcribe audio from the document...")
  ```
  Any image uploaded for OCR processing **unconditionally fails**.
- **Remediation:** Implement Tesseract or Vision model OCR for images in `ai_pipeline.py`:
  ```python
  from PIL import Image
  import pytesseract
  
  # Inside process_document_pipeline for images:
  image = Image.open(io.BytesIO(file_bytes))
  extracted_text = pytesseract.image_to_string(image)
  ```

---

### 🟠 [HIGH] BUG-02: Silent PII Redaction Fallback Exposure Vulnerability
- **Location:** `python_backend/services/ai_pipeline.py` — Lines 106–111
- **Issue:** If Microsoft Presidio anonymization fails (e.g. if the SpaCy English NLP model `en_core_web_lg` is missing), `ai_pipeline.py` catches the exception and silently falls back to raw, unredacted document text:
  ```python
  except Exception as e:
      print(f"PII Redaction failed, falling back to raw text: {e}")
      safe_text = extracted_text
  ```
  This creates a privacy leak where sensitive PII (Aadhaar cards, PAN cards, phone numbers) is submitted directly to external OpenRouter model endpoints without warning the user.
- **Remediation:** Fail the pipeline or require explicit user consent if PII redaction fails when privacy mode is enabled.

---

### 🟡 [MEDIUM] BUG-03: Mocked Hybrid Vector RAG & Hardcoded Knowledge Graph
- **Location:** `python_backend/services/agent_rag.py` — Lines 53–71 & Lines 73–88
- **Issue:**
  1. In `vector_retrieval_node`, the actual Supabase database RPC call to `hybrid_search_legal_knowledge` is commented out (lines 58–66). It returns hardcoded mock results:
     ```python
     state["vector_results"] = [
         {"section": "BNS 303", "similarity": 0.95, "content": "Theft punishment provisions."}
     ]
     ```
  2. In `graph_retrieval_node`, the `legal_graph` NetworkX instance only contains 4 hardcoded nodes (`IPC_378`, `BNS_303`, `Article_21`).
  As a result, constitutional and legal analysis outputs are based on static stub data rather than actual document content.
- **Remediation:** Uncomment and activate the Supabase vector search RPC integration in `agent_rag.py` and populate the graph dynamically from statutory tables.

---

### 🟡 [MEDIUM] BUG-04: Infinite Frontend Job Polling Loop
- **Location:** `src/components/ProcessingConfig.tsx` — Lines 119–140
- **Issue:** The document polling logic uses a `while (!jobFinished)` loop with no maximum iteration limit or timeout. If a job hangs on the backend or encounters an unhandled status state (e.g., database connection timeout), the browser tab will poll the backend every 3 seconds indefinitely, freezing resources and draining API capacity.
- **Remediation:** Add a retry counter and maximum timeout limit:
  ```typescript
  let attempts = 0;
  const maxAttempts = 100; // 5 minutes timeout
  while (!jobFinished && attempts < maxAttempts) {
    attempts++;
    await new Promise(resolve => setTimeout(resolve, 3000));
    // check status...
  }
  if (attempts >= maxAttempts) {
    toast({ title: "Processing timed out", variant: "destructive" });
  }
  ```

---

### 🟡 [MEDIUM] BUG-05: Inconsistent Environment Variable Key Naming (`PUBLISHABLE_KEY` vs `ANON_KEY`)
- **Location:**
  - `src/components/DocumentUpload.tsx` (Line 84: `import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY`)
  - `src/integrations/supabase/client.ts` (Line 6: `import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY`)
  - `.env.example` / `.env.local` / Backend services: `VITE_SUPABASE_ANON_KEY`
- **Issue:** The project uses two different key names (`VITE_SUPABASE_PUBLISHABLE_KEY` and `VITE_SUPABASE_ANON_KEY`). If a developer only defines `VITE_SUPABASE_ANON_KEY` in `.env.local`, the custom XHR upload in `DocumentUpload.tsx` sends an `undefined` API key header to Supabase Storage, causing HTTP 401 upload failures.
- **Remediation:** Standardize all frontend files to use `import.meta.env.VITE_SUPABASE_ANON_KEY`.

---

## 4. API & Data Flow Issues

### 🔵 [LOW] API-01: Brittle Base URL String Replacement in API Gateway
- **Location:** `node_backend/index.js` — Lines 70 & 91
- **Issue:** The gateway derives python backend URLs using string replacement:
  ```javascript
  const baseUrl = pythonEngineUrl.replace('/process', '');
  ```
  If `PYTHON_ENGINE_URL` is configured without `/process` (e.g. `http://python_engine:8000`), or configured with a trailing slash, the string replacement logic breaks endpoint construction for `/job/:jobId` or `/chat`.
- **Remediation:** Use standard URL parsing:
  ```javascript
  const parsedUrl = new URL(process.env.PYTHON_ENGINE_URL || 'http://localhost:8000/process');
  const baseUrl = `${parsedUrl.protocol}//${parsedUrl.host}`;
  ```

---

### 🔵 [LOW] DATA-02: RLHF Feedback Missing Document ID Context
- **Location:** `src/components/ResultsDisplay.tsx` — Lines 43–47
- **Issue:** When users click thumbs up/down feedback on a result, the insert query into `rlhf_feedback` passes `query_text`, `retrieval_strategy`, and `reward_score`, but omits `document_id`. Consequently, human feedback ratings in the database cannot be traced back to specific documents.
- **Remediation:** Pass `document_id` into `ResultsDisplay` props and include it in the `rlhf_feedback` payload.

---

## 5. Comprehensive Fix Roadmap & Priority Checklist

1. **[P0 - Immediate Fix]**: Add JWT verification to `GET /api/job/:jobId` in `node_backend/index.js` and `POST /chat` in `python_backend/main.py`.
2. **[P0 - Immediate Fix]**: Standardize environment key names across frontend (`VITE_SUPABASE_ANON_KEY`) to resolve XHR upload failure risks.
3. **[P1 - High Priority]**: Add image OCR (Tesseract / Vision LLM) in `python_backend/services/ai_pipeline.py` to prevent image processing crashes.
4. **[P1 - High Priority]**: Remove hardcoded fallback credentials and URLs across all services; raise runtime exceptions on boot if missing.
5. **[P2 - Medium Priority]**: Connect real Supabase `hybrid_search_legal_knowledge` database query in `agent_rag.py` to replace stubbed vector results.
6. **[P2 - Medium Priority]**: Enforce timeout limits (max 100 iterations) in frontend job polling loops in `ProcessingConfig.tsx`.

---
*Report generated and validated for Dharma Lens project codebase.*
