# VidhiChakshu (विधि-चक्षु) 3.0 - Environment Variables Guide

## Overview

VidhiChakshu uses environment variables to configure services across environments without baking credentials into container images. All sensitive variables must be defined in `.env` (which is excluded from Git via `.gitignore`). A template is provided in `.env.example`.

## Required Configuration

### 1. Supabase Cloud Configuration
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGc...your-anon-key...
VITE_SUPABASE_PROJECT_ID=your-project-id
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```
- **Purpose**: User authentication, Storage buckets (`documents`), and PostgreSQL vector store (`legal_knowledge`).
- **Access**: Project Settings → API in Supabase dashboard.

### 2. Multi-Modal AI Engine Configuration
```env
OPENROUTER_API_KEY=sk-or-v1-...
OLLAMA_BASE_URL=http://host.docker.internal:11434
```
- **`OPENROUTER_API_KEY`**: Cloud failover LLM & multi-modal paleography vision access.
- **`OLLAMA_BASE_URL`**: Local offline LLM endpoint (`Qwen2.5-7B`, `Phi-4-mini`) for 100% air-gapped sovereign execution.

### 3. API Gateway Configuration
```env
VITE_API_GATEWAY_URL=http://localhost:3000
PYTHON_ENGINE_URL=http://localhost:8000/process
PORT=3000
```
- **`VITE_API_GATEWAY_URL`**: Exposed to the Vite frontend for API dispatch.
- **`PYTHON_ENGINE_URL`**: Used by the Express gateway to route processing and PDF export requests to FastAPI.

### 4. Database & Caching (Extended Docker Stack)
```env
DB_PASSWORD=your-secure-password
DB_USER=admin
DB_NAME=vidhichakshu
DB_HOST=database
DB_PORT=5432
DATABASE_URL=postgresql://admin:${DB_PASSWORD}@database:5432/vidhichakshu
REDIS_URL=redis://redis:6379
```
