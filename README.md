# VidhiChakshu (विधि-चक्षु) 3.0
### The AI Vision for Indian Legal & Heritage Documents

[![License: MIT](https://img.shields.io/badge/License-MIT-gold.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg?logo=docker&logoColor=white)](docker-compose.yml)
[![FastAPI](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](python_backend/)
[![Node.js](https://img.shields.io/badge/Node.js-20.x-339933.svg?logo=node.js&logoColor=white)](node_backend/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg?logo=react&logoColor=white)](src/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6.svg?logo=typescript&logoColor=white)](tsconfig.json)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg?logo=tailwind-css&logoColor=white)](tailwind.config.ts)

---

## 🏛️ Executive Overview

**VidhiChakshu (विधि-चक्षु)** (*"The Vision of Law & Righteous Knowledge"*) is an enterprise-grade AI platform specifically engineered to decipher, transcribe, analyze, audit, and explain complex Indian legal records, century-old handwritten property deeds (*Bainama, Khasra, Sanad, Watandar*), ancient script grants (*Modi, Halegannada, Perso-Arabic Nastaliq*), and verbatim court audio proceedings.

VidhiChakshu bridges the gap between historical heritage documentation and the modern Indian judicial system by serving two distinct user bases:
1. **Citizens & Farmers**: Demystifies century-old inheritance deeds, four-sided boundaries, and ownership shares without confusing revenue jargon through plain-language explanations, voice queries, and audio read-aloud.
2. **Courts & Advocates**: Precision statutory mapping between legacy colonial codes (IPC 1860, CrPC 1973, Evidence Act 1872) and new statutes (BNS 2023, BNSS 2023, BSA 2023), property law covenants (Transfer of Property Act 1882, Indian Registration Act 1908, Indian Stamp Act 1899), and constitutional property safeguards (Article 300A).

---

## ⚡ Groundbreaking Heritage Deed Capabilities

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       VIDHICHAKSHU CORE CAPABILITIES                        │
├──────────────────────┬──────────────────────┬───────────────────────────────┤
│ 🧭 Chauhaddi 2D Map  │ 🌳 Pedigree Tree     │ ⛓️ Title Chain & Defect Audit │
│ 4-Cardinal Boundary  │ Shajra-e-Nasab       │ Sequential Devolution Timeline│
│ Cadastral Visualizer │ Coparcenary Shares   │ 0-100 Title Health Score      │
├──────────────────────┼──────────────────────┼───────────────────────────────┤
│ 📖 Archaic Lexicon   │ 📥 Certified PDF     │ 🎙️ Vernacular Voice & Audio   │
│ 250+ Historical Terms│ ReportLab Legal Brief│ Web Speech STT & SpeechSynth  │
│ Persian/Modi/Kannada │ Court-Ready Schedules│ Listen Aloud in Hindi/English │
└──────────────────────┴──────────────────────┴───────────────────────────────┘
```

### 1. 🧭 Interactive 2D Plot & Boundary Visualizer (*Chauhaddi Mapper*)
* Extracts and maps four demarcated cardinal boundaries: **उत्तर (North)**, **दक्षिण (South)**, **पूर्व (East)**, and **पश्चिम (West)**.
* Renders an interactive 2D cadastral boundary parcel showing Survey/Khasra/Gat numbers, recorded extent (Bighas, Acres, Gunthas, Sq. Ft), and revenue village.
* Evaluates boundary descriptions against Section 54 of the Transfer of Property Act 1882 and Section 21 of the Indian Registration Act 1908.

### 2. 🌳 Ancestral Lineage & Pedigree Tree Generator (*Shajra-e-Nasab / Vansh-Vriksha*)
* Automatically parses genealogical trees from partition deeds, sanads, and mutation records.
* Visualizes generational hierarchy cards starting from the original grantor/patriarch (*कुलपति / मूल धारक*) down through successive tiers of coparceners and heirs.
* Calculates individual legal shares adhering to Section 6 of the Hindu Succession Act (including daughters' equal coparcenary rights) and the Indian Succession Act 1925.

### 3. ⛓️ Chain-of-Title Audit & Defect Detection
* Sequentially traces the historical devolution of ownership across conveyances, crown grants, partition deeds, and revenue mutations.
* Computes a dynamic 0–100 **Title Health Score**.
* Proactively flags critical title defects: breaks in root of title, unmutated revenue entries, non-registration under Registration Act Section 17, and stamp duty insufficiency under Stamp Act Section 33/35.

### 4. 📥 Certified Legal Intelligence PDF Report Generation
* Generates official court-ready intelligence briefs powered by ReportLab 5.0.
* Features the official VidhiChakshu seal, title health meter, Chauhaddi boundary table, lineage schedule, chain-of-title timeline, defect alerts, archaic lexicon, and statutory provisions.

### 5. 🎙️ Vernacular Voice Input (STT) & Audio Playback (TTS)
* **Voice Input (Speech-to-Text)**: Real-time speech recognition for bilingual legal queries (`hi-IN` / `en-IN`) within the document chat interface.
* **Audio Playback (Text-to-Speech)**: Integrated speech synthesis engine reading aloud plain-language citizen explanations for rural citizens, farmers, and visually impaired users.

### 6. 📜 Historical Script Paleography (HTR Track)
* Multi-tier paleography vision pipeline using contrast stretching, stroke sharpening, and multi-modal base64 image prompts.
* Specialized models for **Modi Script** (Maharashtra land deeds), **Halegannada** (Old Kannada epigraphy), and **Perso-Arabic Nastaliq** (Mughal and Princely State revenue records).

### 7. 📖 Archaic Revenue Lexicon (250+ Terms)
* Detects and explains historical terms (*Bainama, Khasra, Khatauni, Sanad, Watandar, Jamabandi, Inam, Chauhaddi, Mohatarma, Peshkash*) with their modern legal significance.

---

## 🏗️ System Architecture

```
+-------------------------------------------------------------------------+
|                         TIER 1: FRONTEND UI                            |
|             React 18 + TypeScript + Vite + Tailwind CSS + Radix UI       |
|  - 9-Tab Results Dashboard (Citizen, Chauhaddi, Pedigree, Title Chain)  |
|  - Real-Time Audio Playback (TTS) & Voice Input (STT)                   |
|  - Certified Legal PDF Report Downloader                                |
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

## 🚀 Quick Start

### 1. Prerequisites
- [Docker](https://www.docker.com/) & Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### 2. Clone & Environment Configuration
```bash
git clone https://github.com/BEAST-AMMAR/dharma-lens-2.0.git
cd "dharma-lens-2.0"

# Copy environment template
cp .env.example .env
```

Configure the following variables in `.env`:
```env
VITE_SUPABASE_URL="https://your-project.supabase.co"
VITE_SUPABASE_ANON_KEY="your-anon-key"
OPENROUTER_API_KEY="sk-or-v1-your-key"
OLLAMA_BASE_URL="http://host.docker.internal:11434"
```

### 3. Launch Services with Docker Compose
```bash
# Build and start all services in detached mode
make up

# Or using docker-compose directly
docker compose up -d --build
```

### 4. Access the Platform
* **Web UI**: [http://localhost:8080](http://localhost:8080)
* **API Gateway**: [http://localhost:3000](http://localhost:3000)
* **ML Engine & Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Testing & Verification

Run the automated test suites:

```bash
# Python AI Engine Test Suite (PII, Lexicon, NetworkX Graph, PDF Generator)
python python_backend/tests/test_pipeline.py

# Node.js API Gateway Test Suite (Auth, Fail-Fast Guards, Health Checks)
cd node_backend && npm test
```

---

## 🛡️ Security & Privacy Guard

* **Fail-Closed PII Redaction**: Sensitive Indian identifiers (12-digit Aadhaar, 10-character PAN, mobile numbers) are redacted before text is transmitted to any model.
* **100% Air-Gapped Mode**: The system can execute completely offline using Ollama (`Qwen2.5-7B`, `Phi-4-mini`) without network dependencies.
* **Fail-Fast Validation**: Backend services refuse to start if security credentials or configurations are missing.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
