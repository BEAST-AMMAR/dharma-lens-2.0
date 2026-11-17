# Project Design Report (PDR)
## VidhiChakshu (विधि-चक्षु) 3.0: Engineering Design & Architectural Blueprint
**Version:** 3.0.0  
**Status:** Production / Active  
**Author:** Lead AI Software Architect  
**Date:** November 2026  

---

## 1. Design Principles & High-Level Philosophy

VidhiChakshu was engineered from the ground up to solve the three greatest challenges facing AI adoption in the Indian legal and property sector:
1. **Absolute Privacy & Data Sovereignty**: Legal documents and property deeds contain sensitive personal and financial identifiers. VidhiChakshu enforces local-first PII redaction and supports 100% air-gapped offline local execution via Ollama.
2. **Statutory Transition & Property Law Mastery**: India is navigating a historic transition from colonial codes (IPC, CrPC, Evidence Act) to modern statutes (BNS, BNSS, BSA), coupled with intricate property frameworks (Transfer of Property Act 1882, Indian Registration Act 1908, Indian Stamp Act 1899). VidhiChakshu maps statutory interactions via an in-memory knowledge graph.
3. **Heritage Paleography & Vernacular Accessibility**: Rural citizens, farmers, and advocates regularly deal with century-old deeds written in ancient scripts (*Modi, Halegannada, Perso-Arabic Nastaliq*) and archaic revenue terms (*Bainama, Khasra, Sanad, Watandar*). VidhiChakshu provides automated transliteration, plain-language citizen summaries, voice input, and audio playback.

---

## 2. Frontend UI / UX Design System

### 2.1 Design Aesthetics & Palette
The frontend leverages a legal-themed visual identity implemented via Tailwind CSS and CSS variables:
- **Legal Navy (`#1B2A4A`)**: Represents judicial authority, structure, and clarity. Used in hero headers, primary navigation, and table headers.
- **Legal Gold (`#C5A059`)**: Represents fairness, prestige, and accent highlights. Used for buttons, icons, progress bars, and active states.
- **Legal Gold Light (`#F9F5EC`)**: Background tint for card headers, badge containers, and highlight boxes.
- **Slate Gray (`#64748B`)**: Secondary text and border accents.

### 2.2 Core UI Components Breakdown

```
+-------------------------------------------------------------------------+
|                        VIDHICHAKSHU DASHBOARD                           |
+-------------------------------------------------------------------------+
| [Header] Logo (Scale Icon) | User Email Badge | Logout Button          |
+-------------------------------------------------------------------------+
| [Feature Cards] Heritage Scripts | Citizen Summary | Lexicon | Statutes |
+-------------------------------------------------------------------------+
| [History Section] Grid of previously processed document cards           |
+-------------------------------------------------------------------------+
| [Document Upload Card] Dropzone (PDF/Images/Audio, Max 50MB)            |
+-------------------------------------------------------------------------+
| [Processing Configuration Card]                                         |
|  - AI Execution Engine (Hybrid / Local Offline / Cloud)                 |
|  - Target Translation Language Selector (22 Indian Languages)           |
|  - Historical Script Paleography Checkbox (Modi/Halegannada/Nastaliq)   |
|  - Summary Length Slider (50 - 500 words)                               |
|  - Feature Checkboxes: OCR, Summarization, Audio, Legal RAG, Entities   |
|  - "Start Processing" Execution Button                                  |
+-------------------------------------------------------------------------+
| [Results Display Card] (Appears upon processing completion)            |
|  - Top Action Bar: Title Health Score (0-100) | Download Certified PDF  |
|  - Paleography Alert Banner (HTR Script Confidence & Verification Flag) |
|  - 9 Specialized Inspection Tabs:                                       |
|    [Tab 1] 👥 Citizen: Plain-language explanation + Audio TTS Read Aloud|
|    [Tab 2] 🧭 Chauhaddi 2D: Interactive 4-cardinal boundary parcel map  |
|    [Tab 3] 🌳 Pedigree: Ancestral Lineage tree (Shajra-e-Nasab)         |
|    [Tab 4] ⛓️ Title Chain: Sequential devolution timeline + Defect audit|
|    [Tab 5] 📖 Lexicon: 250+ Archaic revenue terms with modern meanings  |
|    [Tab 6] 📄 Brief: Synthesized legal brief with RLHF rating buttons   |
|    [Tab 7] ⚖️ Statutes: IPC ↔ BNS, TPA, Registration & Stamp Act RAG    |
|    [Tab 8] 💬 Chat: Q&A Chat with Document + Voice Input Mic (STT)      |
|    [Tab 9] 📝 Raw Text: Extracted text with PII Redaction toggle       |
+-------------------------------------------------------------------------+
```

---

## 3. Visualizer Engineering Specifications

### 3.1 Chauhaddi 2D Parcel Visualizer
- **Cardinal Directional Orientation**: Positioned using compass coordinates (North at top, South at bottom, East at right, West at left).
- **Subject Property Card**: Centered within the boundary matrix displaying registered survey numbers, area units, village jurisdiction, and boundary demarcation integrity.
- **Encroachment Safeguard Audit**: Analyzes border descriptions against Section 54 of Transfer of Property Act 1882 to highlight boundary clarity or dispute risks.

### 3.2 Ancestral Lineage Tree (*Shajra-e-Nasab*)
- **Generational Grouping**: Displays the original grantee/patriarch at root with gold accent styling, branching into successive generational tiers (Gen 1, Gen 2, etc.).
- **Coparcenary Share Breakdown**: Parses fractional or percentage shares across legal heirs in compliance with Hindu Succession Act Sec 6 (including daughters' coparcenary rights) and Indian Succession Act 1925.

### 3.3 Chain-of-Title Audit & Defect Detection
- **Dynamic Title Health Meter**: Evaluates title continuity, encumbrance risks, stamp duty compliance, and registration validity.
- **Defect Alert Banners**: Flags missing revenue mutations, gaps in title chain, or lack of registration under Registration Act Section 17.
- **Chronological Timeline**: Step-by-step sequential mapping of all historical conveyances.
