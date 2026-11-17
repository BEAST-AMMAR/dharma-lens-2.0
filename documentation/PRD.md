# Product Requirement Document (PRD)
## VidhiChakshu (विधि-चक्षु) 3.0: AI-Powered Indian Legal & Heritage Document Intelligence Platform
**Version:** 3.0.0  
**Status:** Production / Active  
**Author:** AI Engineering & Legal Tech Architecture Team  
**Date:** November 2026  

---

## 1. Executive Summary & Product Vision

### 1.1 Executive Summary
**VidhiChakshu (विधि-चक्षु)** (*The AI Vision for Indian Legal & Heritage Documents*) is an enterprise-grade AI platform specifically built to decipher, transcribe, analyze, audit, and explain complex Indian legal records, century-old handwritten property deeds (*Bainama, Khasra, Sanad, Watandar*), ancient script grants (Modi, Halegannada, Perso-Arabic Nastaliq), and verbatim court proceedings. 

Unlike generic document processing tools, VidhiChakshu addresses the twin needs of the Indian legal ecosystem:
1. **Statutory & Cadastral Precision for Legal Practitioners & Courts**: Multi-agent RAG graph traversal over IPC $\leftrightarrow$ BNS, Evidence Act $\leftrightarrow$ BSA, Transfer of Property Act 1882, Indian Registration Act 1908, Indian Stamp Act 1899, and Constitutional property guarantees (Article 300A).
2. **Everyday Clarity for Citizens & Farmers**: Plain-language vernacular explanations answering practical ownership, boundary, and encumbrance questions, accompanied by interactive 2D parcel visualizers, ancestral pedigree trees, voice input, and audio playback.

### 1.2 Product Vision
To democratize access to justice and land rights across India by bridging century-old vernacular scripts and arcane colonial laws with an offline-resilient, privacy-enforced, multi-agent AI engine.

---

## 2. Target Audience & User Personas

| Persona | Role / Description | Primary Needs | Key Platform Touchpoints |
| :--- | :--- | :--- | :--- |
| **Citizens & Farmers** | Everyday landowners, agricultural heirs, rural citizens | Plain-language explanation (*सरल व्याख्या*), boundary clarity, audio playback in vernacular, title defect warnings | Citizen Summary, Audio Playback (TTS), Voice Input (STT), Chauhaddi 2D Map |
| **Advocate & Judiciary** | Supreme Court / High Court Advocate, District Judge | Statutory mapping (IPC $\leftrightarrow$ BNS, TPA, Registration Act), precedent validation, certified court-ready briefs | Statutory & Land Laws Tab, Q&A Chat, Certified PDF Export |
| **Revenue & Land Officer** | Tehsildar, Patwari, Sub-Registrar, Revenue Clerk | Deciphering archaic revenue terms (*Bainama, Khasra, Sanad, Watandar*), four-sided boundary validation | Archaic Lexicon, 2D Chauhaddi Mapper, Chain-of-Title Audit |
| **Genealogist & Title Examiner** | Title investigator, Bank legal empanelment counsel | Tracing root of title, detecting title gaps, verifying legal heir pedigree | Ancestral Lineage Tree (*Shajra-e-Nasab*), Title Health Score |

---

## 3. Core Capabilities & Architectural Pillars

### 3.1 Advanced Paleography & Historical Script Recognition (HTR Track)
- Multi-tier computer vision pipeline combining contrast stretching, unsharp stroke sharpening, and multi-modal Vision Language Models (VLMs).
- Native support for **Modi Script** (17th–20th century Marathi land deeds and Peshwa records).
- Native support for **Halegannada (Old Kannada)** epigraphy, copper-plate grants, and temple records.
- Native support for **Perso-Arabic Nastaliq** Mughal and Princely State revenue documents.
- Automatic paleographic confidence scoring and certified human verification alerts.

### 3.2 Archaic Revenue & Conveyancing Lexicon (250+ Terms)
- Catalog of historical Persian, Urdu, Marathi (Modi), and Kannada revenue terms.
- Translates historical revenue vocabulary (*Bainama, Khasra, Khatauni, Sanad, Watandar, Jamabandi, Inam, Chauhaddi, Mohatarma, Peshkash*) into modern legal significance under the Transfer of Property Act 1882, Indian Registration Act 1908, and State Land Revenue Codes.

### 3.3 Interactive 2D Plot & Boundary Visualizer (Chauhaddi Mapper)
- Extracts and maps four demarcated cardinal boundaries: **उत्तर (North)**, **दक्षिण (South)**, **पूर्व (East)**, and **पश्चिम (West)**.
- Renders an interactive 2D cadastral boundary parcel showing Survey/Khasra/Gat numbers, recorded extent (Bighas, Acres, Gunthas, Sq. Ft), and registered revenue village.
- Conducts automated boundary clarity and encroachment risk audits under TPA Section 54 and Registration Act Section 21.

### 3.4 Ancestral Lineage & Pedigree Tree Generator (*Shajra-e-Nasab / Vansh-Vriksha*)
- Automatically extracts multi-generational genealogical trees from partition deeds, sanads, and mutation records.
- Renders hierarchical tree nodes from the original patriarch down through successive generations of coparceners and legal heirs.
- Computes and displays legal share allocations (e.g., 1/2 share, undivided interest) adhering to Section 6 of the Hindu Succession Act (including daughters' equal coparcenary rights) and the Indian Succession Act 1925.

### 3.5 Chain-of-Title Audit & Proactive Defect Detection
- Sequentially traces the historical devolution of ownership across conveyances, crown grants, partition deeds, and revenue mutations.
- Computes a dynamic 0–100 **Title Health Score**.
- Proactively flags critical title defects: breaks in root of title, unmutated revenue entries, non-registration under Registration Act Section 17, and stamp duty insufficiency under Stamp Act Section 33/35.

### 3.6 Certified Legal Intelligence PDF Report Generation
- ReportLab-powered document generator compiling official court-ready intelligence briefs.
- Features official VidhiChakshu seal, title health meter, Chauhaddi boundary table, lineage schedule, chain-of-title timeline, defect alerts, archaic lexicon, and statutory transitions.

### 3.7 Voice Input (STT) & Audio Playback (TTS) in Regional Vernacular
- **Voice Input (Speech-to-Text)**: Real-time speech recognition for bilingual legal queries (`hi-IN` / `en-IN`) within the document chat interface.
- **Audio Playback (Text-to-Speech)**: Integrated speech synthesis engine reading aloud plain-language citizen explanations for rural citizens, farmers, and visually impaired users.

### 3.8 Multi-Agent Statutory RAG & Constitutional Graph
- **Router Agent**: Evaluates criminal, property, constitutional, and revenue applicability.
- **NetworkX Legal Knowledge Graph**: Explicit statutory mapping between legacy codes (IPC, CrPC, IEA) and modern statutes (BNS 2023, BNSS 2023, BSA 2023), Property Laws (TPA 1882, Registration Act 1908, Stamp Act 1899), and Constitutional guarantees (Articles 14, 19, 21, 300A).
- **Fail-Closed PII Redaction Guard**: Redacts 12-digit Aadhaar, 10-character PAN, phone numbers, and email addresses with zero unredacted cloud transmissions.

---

## 4. Functional Requirements Traceability

```
[F-01] Document Upload & Storage: Supports PDFs, images, and audio up to 50MB with secure Supabase storage.
[F-02] OCR & Vision Extraction: PyMuPDF high-density text extraction with fallback PIL stroke enhancement.
[F-03] Historical Script Paleography: Specialized Modi, Halegannada, and Nastaliq transliteration.
[F-04] Fail-Closed PII Privacy Guard: Regex + Presidio masking of Aadhaar and PAN before external dispatch.
[F-05] Citizen Plain-Language Summary: Structured answers to 7 core citizen ownership and risk questions.
[F-06] Archaic Revenue Lexicon: Detection and modern legal mapping of 250+ revenue vocabulary terms.
[F-07] 2D Chauhaddi Boundary Visualizer: Interactive cadastral parcel visualizer with N, S, E, W borders.
[F-08] Ancestral Pedigree Generator: Shajra-e-Nasab hierarchy tree with coparcenary share calculation.
[F-09] Chain-of-Title & Defect Detection: Sequential devolution timeline with 0-100 Title Health Score.
[F-10] Certified PDF Report Export: ReportLab generation of certified legal briefs.
[F-11] Voice Input & Audio Playback: Web Speech STT for chat queries and TTS for citizen summaries.
[F-12] Statutory Transition RAG: Knowledge graph traversal across BNS, BNSS, BSA, TPA, and Registration Act.
[F-13] Multi-Language Translation: Translation across 22 official Indian languages.
[F-14] Structured Entity Extraction: Automatic identification of Parties, Courts, Survey Nos, and Dates.
[F-15] Document History & Multi-Tenancy: Persistent session history stored in Supabase with RLS policies.
```

---

## 5. Non-Functional Requirements & Security
- **Data Sovereignty & Air-Gap Mode**: Support for 100% offline local processing using Ollama (`Qwen2.5-7B`, `Phi-4-mini`).
- **Fail-Safe Startup**: Rejection of startup if required authentication credentials or environment configurations are missing.
- **Latency Targets**: Sub-2s text extraction, sub-8s local inference, sub-3s cloud failover inference.
- **Cross-Platform Compatibility**: Complete containerization via Docker, Docker Compose, and AWS CloudFormation.
