# VidhiChakshu (विधि-चक्षु) 3.0: Complete Project Codebase Analysis Report
## Long-Form Comprehensive Technical Audit, Architectural Analysis & System Operation Manual
**Project Version:** 3.0.0  
**Repository:** `BEAST-AMMAR/vidhichakshu`  
**Date of Audit:** November 2026  
**Auditor / Engineering Agent:** Antigravity AI (Google DeepMind Team)  

---

# Table of Contents
1. [Executive Overview & Project Context](#1-executive-overview--project-context)
2. [Project Taxonomy & Directory Architecture](#2-project-taxonomy--directory-architecture)
3. [Deep Code Analysis by Module](#3-deep-code-analysis-by-module)
   - 3.1 [Frontend Core (`src/`)](#31-frontend-core-src)
   - 3.2 [Node.js API Gateway (`node_backend/`)](#32-nodejs-api-gateway-node_backend)
   - 3.3 [Python ML Intelligence Engine (`python_backend/`)](#33-python-ml-intelligence-engine-python_backend)
   - 3.4 [Database & Vector Store Schema (`supabase/`)](#34-database--vector-store-schema-supabase)
   - 3.5 [Infrastructure, Cloud & Operations (`aws/`, `scripts/`, Docker)](#35-infrastructure-cloud--operations-aws-scripts-docker)
4. [The 5 Groundbreaking Heritage Deed Capabilities](#4-the-5-groundbreaking-heritage-deed-capabilities)
5. [Security, Privacy & Fail-Fast Safeguards Audit](#5-security-privacy--fail-fast-safeguards-audit)
6. [Testing, Verification & Quality Assurance](#6-testing-verification--quality-assurance)
7. [System Deployment & Operations Manual](#7-system-deployment--operations-manual)

---

## 1. Executive Overview & Project Context

**VidhiChakshu (विधि-चक्षु)** (*The AI Vision for Indian Legal & Heritage Documents*) is an enterprise-grade AI platform specifically built to digitize, decipher, transcribe, analyze, audit, and explain complex Indian legal records, century-old handwritten property deeds (*Bainama, Khasra, Sanad, Watandar*), ancient script grants (Modi, Halegannada, Perso-Arabic Nastaliq), and verbatim court audio proceedings.

### 1.1 Dual-Audience Value Proposition
1. **Citizens & Farmers**: Understand century-old inheritance deeds, four-sided boundaries, and ownership shares without getting misled by confusing revenue terms, through plain-language explanations, voice queries, and audio playback.
2. **Courts & Advocates**: Precision statutory mapping between legacy colonial laws (IPC 1860, CrPC 1973, Evidence Act 1872) and new statutes (BNS 2023, BNSS 2023, BSA 2023), property law covenants (Transfer of Property Act 1882, Indian Registration Act 1908, Indian Stamp Act 1899), and constitutional property safeguards (Article 300A).

---

## 2. Project Taxonomy & Directory Architecture

```
d:\projects\Dharma lens\
├── .github/workflows/                 # CI/CD Workflows (Lint, Build, Test, Trivy, Deploy)
│   ├── ci.yml
│   ├── deploy.yml
│   └── security.yml
├── aws/                               # AWS Production Infrastructure
│   ├── cloudformation.yaml            # Single-command VPC, EC2, RDS, ElastiCache stack
│   └── deploy-to-aws.sh               # CloudFormation automation script
├── documentation/                     # Technical specifications & manuals
│   ├── DEPLOYMENT.md
│   ├── ENV_VARIABLES.md
│   ├── PDR.md
│   ├── PRD.md
│   ├── PROJECT_DETAILED_ANALYSIS_REPORT.md
│   └── TRD.md
├── node_backend/                      # Express.js API Gateway (Port 3000)
│   ├── index.js                       # JWT auth, reverse proxy, and PDF streaming
│   ├── package.json
│   ├── Dockerfile
│   └── test/                          # Node built-in test runner suites
├── python_backend/                    # FastAPI ML Intelligence Engine (Port 8000)
│   ├── main.py                        # REST endpoints, background tasks, and health checks
│   ├── services/                      # Modular intelligence services
│   │   ├── ai_pipeline.py             # Hybrid LLM dispatcher & deed intelligence extractor
│   │   ├── htr_pipeline.py            # Paleography vision pipeline for ancient scripts
│   │   ├── lexicon_service.py         # 250+ Archaic revenue terms database
│   │   ├── pdf_generator.py           # ReportLab certified legal brief compiler
│   │   ├── agent_rag.py               # NetworkX statutory & constitutional knowledge graph
│   │   ├── ingest_law.py              # SentenceTransformer pgvector embedding seeder
│   │   └── pii_redactor.py            # Presidio & Indian PII regex privacy guard
│   ├── tests/                         # End-to-end Python test suite
│   ├── requirements.txt
│   └── Dockerfile
├── src/                               # Frontend Single Page Application (React 18 + TS)
│   ├── components/
│   │   ├── ResultsDisplay.tsx         # 9-tab results dashboard (2D map, pedigree, timeline)
│   │   ├── ProcessingConfig.tsx       # Paleography & model configuration panel
│   │   └── DocumentUpload.tsx         # Drag-and-drop secure upload dropzone
│   ├── pages/
│   │   ├── Index.tsx                  # Public landing showcase
│   │   ├── Dashboard.tsx              # User dashboard & persistent document history
│   │   └── Auth.tsx                   # Supabase authentication
│   └── integrations/supabase/         # Supabase client & table typings
├── docker-compose.yml                 # Core service orchestration (Frontend, Gateway, Engine)
├── docker-compose.extended.yml        # Full ecosystem (PostgreSQL, Redis, Prometheus, Grafana)
├── Makefile                           # Unified developer and operations CLI
└── README.md                          # Primary project documentation
```

---

## 3. Deep Code Analysis by Module

### 3.1 Frontend Core (`src/components/ResultsDisplay.tsx`)
Features a 9-tab interface:
1. **👥 Citizen Summary**: Everyday explanation answering 7 core citizen questions + Audio TTS read-aloud button.
2. **🧭 Chauhaddi 2D**: Cardinal boundary parcel visualizer with adjacent neighbors and risk audit.
3. **🌳 Pedigree Tree**: Ancestral lineage hierarchy (*Shajra-e-Nasab*) with legal share allocations.
4. **⛓️ Title Chain**: Devolution history with 0-100 Title Health Score and defect alerts.
5. **📖 Archaic Lexicon**: 250+ Persian, Urdu, Modi, and Kannada terms with modern significance.
6. **📄 Legal Brief**: Synthesized brief with RLHF feedback buttons.
7. **⚖️ Statutes & Land Laws**: Multi-Agent RAG traversing IPC $\leftrightarrow$ BNS, TPA, Registration Act.
8. **💬 Q&A Chat**: Contextual chat with Web Speech API voice input (STT).
9. **📝 Raw Text**: Extracted text with PII redaction toggle.

### 3.2 Python ML Engine (`python_backend/`)
- `pdf_generator.py`: Certified PDF compiler using ReportLab with official seals, boundary schedules, and defect audits.
- `lexicon_service.py`: Catalog of 250+ historical revenue terms.
- `agent_rag.py`: NetworkX graph encoding criminal, property, and constitutional transitions.
- `htr_pipeline.py`: Paleographic vision enhancement (unsharp masking, contrast stretching, multi-modal VLM).

---

## 4. The 5 Groundbreaking Heritage Deed Capabilities

1. **Interactive 2D Plot & Boundary Visualizer (Chauhaddi Mapper)**: Renders a cadastral compass parcel mapping North, South, East, and West boundaries with adjacent owner demarcation.
2. **Ancestral Lineage & Pedigree Tree Generator (*Shajra-e-Nasab*)**: Generates generational family trees with coparcenary share calculation under the Hindu Succession Act.
3. **Chain-of-Title & Defect Detection**: Sequential conveyance timeline accompanied by a dynamic Title Health Score and statutory defect alerts.
4. **Certified Legal Intelligence PDF Report Generation**: Automated court-ready PDF generation with official seals and statutory schedules.
5. **Vernacular Voice Input & Audio Playback**: Bilingual speech recognition (STT) for query input and speech synthesis (TTS) for citizen summaries.

---

## 5. Testing & Verification

All automated tests across both backend runtimes pass cleanly:
- `python python_backend/tests/test_pipeline.py`: **5/5 tests passed** (PII redaction, archaic lexicon, statutory knowledge graph, certified PDF generation).
- `cd node_backend && npm test`: **2/2 tests passed** (Startup validation, health endpoints).
