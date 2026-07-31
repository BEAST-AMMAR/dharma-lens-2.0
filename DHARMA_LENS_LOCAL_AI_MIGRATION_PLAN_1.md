# Dharma Lens — Local/Offline AI Migration & Remediation Plan (v2)

**Target Hardware:** Acer Predator Helios Neo 16S AI — Intel Core Ultra 7 255HX, 16GB DDR5-6400 RAM, NVIDIA RTX 5070 Laptop (8GB VRAM), 1TB SSD
**Purpose:** Replace cloud/free-tier LLM dependency with a local, updateable, hardware-safe stack; fix audited defects; design real RAG + RLHF; add historical/handwritten document recognition.
**For use in:** Antigravity IDE, as an implementation reference and checklist.

---

## 0. Governing Principle

> **Decouple reasoning from knowledge.** The LLM is a fixed reasoning/writing engine that never needs retraining. Legal knowledge (statutes, case law, IPC↔BNS mappings) lives in a vector store, re-ingestable in minutes. "Updated" happens in retrieval, not model weights.

Everything below — including the new historical-document track — follows this rule: recognition/transcription models are specialists that feed *into* the same RAG pipeline; they are not replacements for it.

---

## 1. Hardware Reality Check

| Resource | Budget | Rule |
|---|---|---|
| VRAM (8GB) | LLM weights + KV cache | Keep resident model weights ≤5–5.5GB quantized. Leave ~2.5GB headroom. |
| System RAM (16GB) | OS + IDE + browser + services | Don't run full `docker-compose` (Postgres, Redis, Celery, Node, Python) + local LLM + heavy IDE simultaneously. |
| Disk (1TB SSD) | Models + embeddings + corpora | Not a constraint. |

**Deployment shape:** hybrid. Supabase (Auth/Storage/Postgres+pgvector) stays cloud — free RAM-wise, already working. Only inference (LLM, embeddings, ASR, OCR/HTR) runs local. Training/fine-tuning jobs run on rented cloud GPU, then adapters/weights come back to run locally — training and inference have very different hardware demands, don't conflate them.

---

## 2. Local Model Stack

### 2.1 Generator (reasoning / summarization / synthesis / chat)
**Primary: Qwen2.5-7B-Instruct**, Q4_K_M GGUF, via Ollama. Apache 2.0, ~4.5–5GB, fits your 8GB card with headroom, reliable JSON output for the synthesizer node.
**Fallback (VRAM pressure / thermal throttling):** Phi-4-mini (3.8B) or Mistral-7B-Instruct-v0.3, Q4_K_M.
**Avoid as daily driver:** anything 14B+ (Gemma 3 27B, Qwen3.6-27B, Llama 4 Scout) — needs 16–24GB+ VRAM classes.

### 2.2 Embedding model (fixes the English-only bug in `ingest_law.py`)
**`BAAI/bge-m3`** (or lighter `intfloat/multilingual-e5-base`), run on **CPU** — small (~300–600M params), frees the GPU entirely for the generator. 100+ languages including major Indic ones. Drop-in replacement for `all-mpnet-base-v2` in the same pgvector table shape.

### 2.3 Translation model
**AI4Bharat `IndicTrans2`**, or the legal-domain-tuned **`InLegalTrans-En2Indic-1B`** — don't route translation through the chat LLM; legal register needs terminological consistency a generalist model won't reliably hold.

### 2.4 Serving layer
**Ollama** — best Windows support, OpenAI-compatible local API at `http://localhost:11434/v1/chat/completions`. Your existing `call_openrouter()` in `ai_pipeline.py` needs only a base-URL swap.

---

## 3. Exact Downloads — Offline Setup Commands

Run once, on a wired/fast connection; everything after this works fully offline.

```bash
# --- 1. Ollama + generator model ---
# Windows: download installer from ollama.com, then:
ollama pull qwen2.5:7b-instruct-q4_K_M
ollama pull phi4-mini:q4_K_M          # fallback/safety-valve model

# --- 2. Embedding model (CPU) ---
pip install -U sentence-transformers huggingface_hub
huggingface-cli download BAAI/bge-m3 --local-dir ./models/bge-m3
# lighter alternative:
huggingface-cli download intfloat/multilingual-e5-base --local-dir ./models/e5-base

# --- 3. Translation model ---
huggingface-cli download ai4bharat/indictrans2-en-indic-1B --local-dir ./models/indictrans2
# legal-domain fine-tune (check current HF repo id under the MILPaC/InLegalTrans project page before pulling):
huggingface-cli download law-ai/InLegalTrans-En2Indic-1B --local-dir ./models/inlegaltrans

# --- 4. Speech-to-text (see §7) ---
pip install faster-whisper
python -c "from faster_whisper import WhisperModel; WhisperModel('medium', download_root='./models/whisper')"

# --- 5. OCR / HTR base models (see §9) ---
huggingface-cli download microsoft/trocr-base-handwritten --local-dir ./models/trocr-base-handwritten
huggingface-cli download microsoft/trocr-large-handwritten --local-dir ./models/trocr-large-handwritten
```

All `--local-dir` paths are then loaded with `from_pretrained("./models/...")` in code — no internet call at runtime. Verify with Wi-Fi off after the first pull.

---

## 4. Exact Datasets — What to Use and How to Get Them

### 4.1 Legal-text corpus (feeds `legal_knowledge` / RAG)

| Dataset | Contents | Download |
|---|---|---|
| **India Code** (indiacode.nic.in) | Canonical IPC/BNS/BNSS/BSA/Constitution text — your ground truth | Manual/scripted scrape of the official portal; not on HF. Use this as the source of truth for statute text specifically. |
| **`harshitv804/Indian_Penal_Code`** | Structured IPC sections | `huggingface-cli download harshitv804/Indian_Penal_Code --repo-type dataset --local-dir ./data/ipc` |
| **ILDC + `law-ai/InLegalBERT`** (IIT Kharagpur) | ~5.4M Indian court judgments, 1950–2019 | `huggingface-cli download law-ai/InLegalBERT --local-dir ./models/inlegalbert` ; ILDC corpus access via the Law-AI Lab's GitHub/paper page (registration may be required — check current terms) |
| **IL-TUR** (`Exploration-Lab/IL-TUR`) | 8-task Indian legal understanding benchmark | `huggingface-cli download Exploration-Lab/IL-TUR --repo-type dataset --local-dir ./data/il-tur` |
| **NyayaAnumana** | Largest Indian judgment-prediction dataset | Via Law-AI Lab GitHub release page |
| **MILPaC** | English↔9-Indic-language parallel legal corpus | Via the MILPaC/InLegalTrans project page (paper + GitHub) |
| **OpenNyAI `Legal-NLP-EkStep`** (incl. `InLegalNER`) | Legal NER + statute-name normalization | `git clone https://github.com/OpenNyAI/Legal_NLP_EkStep` |

**Do not scrape case-law aggregator sites directly** — check ToS; the above already did clean data collection.

### 4.2 Handwritten / historical-script datasets (feeds §9, new)

| Dataset | Contents | Why it matters here |
|---|---|---|
| **DohaScript** | Large-scale, multi-writer, page-level continuous handwritten **Hindi/Devanagari** text | Modern handwritten Devanagari land records, applications, affidavits |
| **AnciDev** | Handwritten text recognition dataset for **ancient Devanagari manuscripts** | Directly targets old/manuscript-era Devanagari — your "ancient documents" case |
| **MODI-HHDoc** | 3,350 handwritten **ancient Modi script** document images | Modi was the actual administrative/land-record script of Maharashtra, 17th–mid-20th century — this is the single most relevant dataset to your "old land deeds" goal |
| **MoDeTrans + MoScNet** | 2,043 Modi-script images with Devanagari transliterations, plus a pretrained knowledge-distilled VLM (MoScNet) that transliterates Modi→Devanagari, ~163× smaller than its teacher model | Ready-to-use starting model for Modi land-deed transcription, small enough to run inference on your 8GB card |
| **PLATTER** | Page-level HTR framework/dataset covering multiple Indic scripts | General-purpose baseline for whichever regional script your source documents use beyond Devanagari/Modi |
| **Lipi Gnani + `MILE-IISc/Kannada-OCR-test-images-with-ground-truth`** (IISc MILE Lab) | Printed Kannada OCR trained on 35 books (1970–2002) including **Halegannada (Old Kannada)** and Kannada-script Sanskrit ślokas; a 250-image benchmark with Halegannada pages | Best available starting point for **Halegannada** — old Kannada land records, inscription-derived administrative text, temple/grant documents |
| **`OpenITI/MAKHZAN`** | Large open annotated ground-truth corpus of **Arabic, Persian (Farsi), Ottoman Turkish, and Urdu** print + manuscript data; built to work with the open-source **Kraken** OCR/HTR engine and **eScriptorium** platform | Persian/Farsi and Urdu were the administrative and land-revenue languages across large parts of Mughal, Deccan Sultanate, Nizam's Hyderabad, and other princely-state territories — directly relevant to Perso-Arabic-script land deeds |
| **Urdu Katib Handwritten Dataset (UKHD)** | Historical Urdu handwritten text dataset with a CRNN baseline | Handwritten (not just printed) Urdu/Persian-script historical documents specifically |
| **600K-KS-OCR** | ~602K synthetic word-image dataset for **Kashmiri** (Perso-Arabic-derived script) | Example of the same low-resource-script pattern if your documents ever extend to Kashmir-region records |

These are on GitHub/Mendeley/arXiv project pages rather than a single HF hub in most cases — check each paper's linked repo for the current download link, since Mendeley/institutional hosting URLs change more often than HF repos.

---

## 5. Codebase Problems → Root Causes → Resolutions

*(Unchanged from prior audit pass — still the correct priority order; do these before any local-model work.)*

### 5.1 — CRITICAL — Auth chain broken end-to-end as shipped
`docker-compose.yml` needs `VITE_SUPABASE_ANON_KEY`; only `.env.local`'s `VITE_SUPABASE_PUBLISHABLE_KEY` exists. Standardize the name everywhere (`client.ts`, `DocumentUpload.tsx`, `.env.local`, `.env.example`), remove hardcoded fallback URLs/keys, fail fast on boot if missing. **Rotate the exposed Supabase anon key** — it was shared outside your machine in the project zip.

### 5.2 — CRITICAL — No real auth on job status / chat endpoints
`GET /api/job/:jobId` (gateway) and `POST /chat` (Python) don't validate tokens properly. Add `supabase.auth.getUser()` / `supabase.auth.get_user()` checks on both, plus `/job/{job_id}` in Python. Make `ProcessingConfig.tsx`'s polling `fetch()` actually send the `Authorization` header.

### 5.3 — CRITICAL — RAG fabricates a citation on every document
See full deep-dive in §6. Root fix: populate real data, un-stub `vector_retrieval_node`/`graph_retrieval_node`. **Until done, disable `enableLegalAnalysis` or show a "demo data" banner.**

### 5.4 — HIGH — Dead Celery/Redis, in-memory job store
`worker.py` is never called; `docker-compose.yml` still runs `redis`/`celery_worker`, wasting RAM you don't have. Remove both services. Keep in-memory `job_store` for single-laptop dev; persist to SQLite if you need restart-durability, not Redis.

### 5.5 — HIGH — Image OCR unconditionally fails
`ai_pipeline.py` has an empty `pass` for non-PDF images. Add Tesseract (`pytesseract`) for printed images; route handwritten/historical images to the new §9 pipeline instead.

### 5.6 — HIGH — Silent PII redaction fallback
Presidio failure currently sends raw text to the LLM silently. Raise an explicit exception instead; never degrade silently, local or cloud.

### 5.7 — MEDIUM — Infinite frontend polling loop
Add `maxAttempts` cap (~100 iterations) to `ProcessingConfig.tsx`'s `while(!jobFinished)` loop.

### 5.8 — MEDIUM — PII redaction only protects the LLM call, not stored data
`result_data["text"]` stores raw `extracted_text`. Store `redacted_text` as a separate labeled field.

### 5.9 — LOW — Brittle URL string replacement; RLHF feedback missing `document_id`
Use `new URL()` parsing instead of `.replace('/process','')`. See §7 for the full RLHF fix, which subsumes this.

---

## 6. RAG Deep-Dive: Purpose, Current Design, Where It Lags, How to Fix It

### 6.1 What it's *for*
The point of RAG here is to stop the LLM from answering legal questions out of its own (possibly wrong, possibly outdated, possibly non-Indian-law-trained) parametric memory. Instead: retrieve the actual relevant statute/case text, hand it to the LLM as context, and have it *synthesize from what's in front of it* — which is also how the IPC→BNS transition gets handled correctly (retrieval reflects current law; the model itself never needs to "learn" the transition happened).

### 6.2 How it's designed (as built)
A LangGraph state graph in `agent_rag.py`:
```
router_node → { vector_retrieval_node, graph_retrieval_node } → synthesizer_node
```
- `router_node`: classifies document scope (Constitutional vs. Criminal).
- `vector_retrieval_node`: intended to run hybrid search (BM25 + pgvector HNSW) via the `hybrid_search_legal_knowledge` Postgres function.
- `graph_retrieval_node`: intended to traverse a NetworkX graph of IPC↔BNS statutory relationships.
- `synthesizer_node`: compiles both retrieval streams into the final structured JSON legal analysis.

This is a reasonable design on paper — hybrid retrieval (semantic + lexical) plus a symbolic graph for exact statutory cross-referencing is a legitimately good pattern for this domain.

### 6.3 Where it's actually lagging (verified against source)
1. **It's fake.** `vector_retrieval_node` returns one hardcoded result (`"BNS 303"`, 0.95 similarity) regardless of input; the real Supabase RPC call is commented out. `graph_retrieval_node` traverses a 4-node hardcoded graph. (§5.3 / prior audit BUG-03.)
2. **Even fixed, there's almost nothing to retrieve.** `ingest_law.py`'s ingestion pipeline has exactly 3 hardcoded law rows. The knowledge base doesn't exist yet at any real scale.
3. **English-only embeddings.** `all-mpnet-base-v2` can't meaningfully embed non-English source text, undermining retrieval for the stated 22+ language support.
4. **No re-ranking.** Hybrid search returns a raw ranked list straight into the prompt; there's no cross-encoder re-ranking pass to catch cases where the embedding/BM25 scores disagree with actual relevance.
5. **No query rewriting/decomposition.** The retrieval query is just a slice of the raw document text (`document_text[:500]`) — no LLM-assisted query reformulation, so ambiguous or long documents produce poor retrieval queries.
6. **Context truncation loses information.** Slicing document text to fixed character counts (`[:500]`, `[:2000]`, etc.) for a long judgment or FIR silently drops most of the document from consideration.
7. **No temporal/version awareness.** Nothing in the schema currently distinguishes "this section was valid until 2024" from "this section is the current BNS replacement" — a query could easily retrieve a superseded IPC section without flagging that it's superseded.
8. **No retrieval evaluation loop.** There's no way to measure whether retrieval quality is actually good or bad — no eval harness comparing retrieved chunks against a labeled set (IL-TUR is exactly suited for this, see §4.1).
9. **No source-attribution surfaced to the user.** Even once retrieval is real, the UI doesn't show *which* retrieved chunk supports which claim — for a legal tool, users should be able to click through to verify a citation, not just trust the synthesized paragraph.

### 6.4 How to fix it (in order)
1. Populate `legal_knowledge` from §4.1 sources with proper metadata (`source_type`, `section_number`, `effective_date`, `superseded_by`).
2. Un-stub `vector_retrieval_node` — call the real `hybrid_search_legal_knowledge` RPC with a `bge-m3` embedding of the query.
3. Build `graph_retrieval_node`'s NetworkX graph dynamically from the `superseded_by` metadata field, not hardcoded edges.
4. Add a lightweight **cross-encoder re-ranker** (`BAAI/bge-reranker-v2-m3` — small, CPU-viable) between retrieval and synthesis: retrieve top-20 candidates, re-rank to top-5, only those go to the LLM. This is usually the single highest-ROI addition to a RAG system's precision.
5. Add a **query rewriting node** before retrieval: one cheap LLM call that turns "here's a 10-page FIR" into a focused 1–2 sentence legal question, rather than blindly truncating raw text.
6. Add **temporal filtering**: when a query resolves to a section with a `superseded_by` value, surface both the historical and current version, labeled, rather than picking one silently.
7. Return **chunk-level citations** (source id, section, snippet) alongside the synthesized answer so `ResultsDisplay.tsx` can render clickable, verifiable sources — not just prose.
8. Build a small **eval set** from IL-TUR/ILDC and track retrieval precision/recall over time as you tune weights — don't tune `hybrid_search_legal_knowledge`'s BM25/semantic weight balance blind.

---

## 7. RLHF: Current State and How to Actually Integrate It

### 7.1 What exists today
`ResultsDisplay.tsx` inserts a row into `rlhf_feedback` on thumbs up/down: `retrieval_strategy`, `reward_score` (+1/–1), and — per the audit — no `document_id`. **This is data collection, not RLHF.** Nothing currently consumes this table to change model behavior. Calling it "RLHF" in the architecture doc is aspirational, not implemented.

### 7.2 Why classic RLHF (PPO + reward model) isn't the right target here
Classic RLHF needs a separately trained reward model plus an unstable, resource-heavy PPO loop, and typically wants thousands of preference judgments to be worth doing. Neither your data volume (early-stage thumbs up/down clicks) nor your hardware (8GB VRAM laptop) makes this a good first move. Don't build toward PPO.

### 7.3 What to actually build, in order

**Step 1 — Fix data collection first (no ML yet).**
```typescript
await supabase.from('rlhf_feedback').insert({
  document_id: documentId,              // currently missing — fix this first
  query_text,
  retrieved_chunk_ids: retrievedChunkIds, // NEW: which chunks fed this answer
  response_text: analysisText,           // NEW: what the model actually said
  retrieval_strategy: "agentic_graph",
  reward_score: type === 'up' ? 1.0 : -1.0
});
```
Without `retrieved_chunk_ids` and `response_text` stored alongside the vote, you have a bare score with nothing to learn from later — fix the schema before collecting more data.

**Step 2 — Use feedback as a curation signal, not a training signal, at first.**
With a handful to a few hundred votes, the highest-value use isn't training — it's periodically reviewing thumbs-down cases to find bad chunks in `legal_knowledge` (wrong section, outdated text, bad OCR) and removing/fixing them, and tuning `hybrid_search_legal_knowledge`'s BM25/semantic weight balance based on where retrieval is failing. This is cheap, immediately useful, and doesn't require any GPU training time.

**Step 3 — Once you have a real preference dataset (hundreds+ labeled pairs), use DPO, not PPO.**
Direct Preference Optimization trains directly on (chosen, rejected) response pairs without a separate reward model — far more tractable than PPO on limited hardware/data:
```python
# Training happens on a rented cloud GPU, not the laptop — bring the adapter back after.
from trl import DPOTrainer, DPOConfig
from peft import LoraConfig

peft_config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj","v_proj"])
dpo_config = DPOConfig(output_dir="./dpo-qwen2.5-7b", per_device_train_batch_size=2)
trainer = DPOTrainer(model, args=dpo_config, train_dataset=preference_dataset, peft_config=peft_config)
trainer.train()
```
Build `preference_dataset` from pairs where the same `query_text`/`document_id` has both an up-voted and a down-voted response — thumbs-up becomes `chosen`, thumbs-down becomes `rejected`. Export the LoRA adapter and load it locally on top of your Ollama-served Qwen2.5-7B for inference.

**Step 4 — Apply DPO to the re-ranker before the generator.**
Because retrieval quality is your real bottleneck (§6), if you only fine-tune one thing, fine-tune the re-ranker (§6.4 step 4) on thumbs up/down-derived (query, good-chunk, bad-chunk) triples before you touch the generator — cheaper, faster feedback loop, and fixes the part of the pipeline most likely to be wrong.

---

## 8. Speech-to-Text (and Text-to-Speech)

### 8.1 STT — the actual priority (court audio transcription is a stated feature)
**`faster-whisper`** (CTranslate2-optimized Whisper), `medium` model size as the default — meaningfully faster and lighter than stock `openai-whisper` for the same accuracy, runs comfortably on your 8GB card or even CPU-only if the GPU is busy with the LLM:
```python
from faster_whisper import WhisperModel
model = WhisperModel("medium", device="cuda", compute_type="int8_float16")
segments, info = model.transcribe(audio_path, language=None)  # auto-detect
```
Use `large-v3` only when accuracy matters more than speed and you're not running the LLM concurrently (VRAM contention). For regional-language court proceedings specifically, generic Whisper's Indic-language accuracy is inconsistent — evaluate **AI4Bharat's Indic-ASR models** as an upgrade path once you have real audio samples to test against; they're trained specifically on Indian accents/languages and typically outperform generic Whisper on regional speech.

### 8.2 TTS — lower priority, include only if there's an accessibility/read-aloud need
No current Dharma Lens feature requires TTS output. If you add one (e.g., reading a summary aloud): **Coqui XTTS-v2** or AI4Bharat's Indic TTS models — both open, both runnable locally, both with growing Indic-language coverage. Don't build this before the higher-priority items above.

---

## 9. NEW GOAL: Handwritten, Historical & Ancient Document Recognition (Old Land Deeds, Manuscripts)

### 9.1 Set expectations honestly first
This is a genuinely hard, research-frontier problem — not a "swap a library" fix like printed-text OCR (§5.5). Generic tools (Tesseract, PyMuPDF) fail almost completely on handwriting and historical/ceased-use scripts. Treat this as a **phased, script-by-script R&D track**, validated incrementally, not a single feature you ship in one pass. A misread word or boundary in a land deed has real legal consequences — low-confidence output must never silently flow into legal analysis as if it were verified text.

### 9.2 Break the problem down by document type

| Type | Difficulty | Approach |
|---|---|---|
| Printed/typed, aged (faded ink, foxing, colonial-era print) | Moderate | Tesseract + preprocessing: binarization, deskew, contrast/denoise. Usually workable with tuning — not the hard part. |
| Handwritten, modern script (e.g. handwritten Devanagari/Hindi land records, British-era English cursive) | Hard | Transformer HTR (TrOCR-family), fine-tuned per script/era on datasets below. |
| Historical/administrative script, no longer in common use — **Modi script** (Maharashtra land records, 17th–mid-20th c.) | Hard, but has dedicated resources | Directly relevant to your stated goal — see §9.3. |
| **Halegannada (Old Kannada)** — used in Karnataka-region grants, inscriptions-derived records, older land/temple documents | Hard, but has a real reference OCR system | See §9.3b — Lipi Gnani (IISc) already handles printed Halegannada; handwritten Halegannada is less solved. |
| **Persian/Farsi and Urdu (Perso-Arabic, Nastaliq script)** — administrative/revenue language under the Mughals, Deccan Sultanates, Nizam's Hyderabad, and other princely states | Hard — cursive, right-to-left, historically the least-solved script family in this list | See §9.3c — real open corpora and tooling (OpenITI MAKHZAN + Kraken/eScriptorium) exist, but accuracy on handwritten manuscripts is still notably behind Latin/Devanagari HTR (see caveats). |
| Other historical Indic scripts (Grantha, Sharada, Kaithi, historical Bengali/Tamil variants, Tulu, Brahmi, Kashmiri) | Hard, sparse resources | Scope to whichever scripts actually appear in your target document set — don't try to cover all of them upfront. Treat each as its own mini-project following the same pattern as §9.3/§9.3b/§9.3c. |

### 9.3 Why Modi script is your strongest starting point
Modi was the *actual* administrative and land-record script of Maharashtra for roughly three centuries — this is close to a direct match for "old land deeds." Real, current, open resources exist:
- **MODI-HHDoc**: 3,350 handwritten ancient Modi document images (§4.2).
- **MoDeTrans + MoScNet**: 2,043 Modi-script images with Devanagari transliterations, plus a pretrained, knowledge-distilled VLM that does Modi→Devanagari transliteration directly, ~163× smaller than its teacher — meaning inference is genuinely light enough for your 8GB card. This is your fastest path to a working demo on real historical land-deed-style documents.

### 9.3b Halegannada (Old Kannada)
Relevant for Karnataka-region old land grants, temple endowment records, and pre-modern administrative documents. Unlike Modi, there's no single distilled "ready to deploy" model, but there is a real, usable OCR system: **Lipi Gnani** (IISc MILE Lab) was explicitly trained on real printed books spanning 1970–2002 that include Halegannada text and Kannada-script Sanskrit ślokas, and the lab's `Kannada-OCR-test-images-with-ground-truth` benchmark (GitHub) includes Halegannada pages for evaluation. Two honest caveats: (1) Lipi Gnani targets **printed** Halegannada well; **handwritten** Halegannada recognition is a thinner, more experimental research area — recent work on Halegannada→modern-Kannada translation itself only reaches ~78% accuracy with a hybrid LSTM+dictionary approach, so treat this as "usable with review," not "solved." (2) If your source documents are inscriptions (stone/copper-plate) rather than paper, that's a different, harder sub-problem (epigraphy, not document HTR) — scope that out separately if it comes up.

### 9.3c Persian/Farsi and Urdu (Perso-Arabic script)
Relevant across a large share of historical Indian land/administrative records outside Maharashtra and Karnataka — Persian was the Mughal court and revenue-administration language for centuries, and Urdu carried that role into the 19th–20th century in many regions (Hyderabad State, Awadh, parts of Punjab and the Deccan). This is genuinely the **hardest** script family in this document to get right:
- **`OpenITI/MAKHZAN`** is the strongest current open resource — large annotated ground truth spanning Arabic, Persian, Ottoman Turkish, and Urdu print *and* manuscript data, purpose-built to work with two open-source tools worth installing directly: **Kraken** (OCR/HTR engine) and **eScriptorium** (a browser-based annotation/transcription platform that sits on top of Kraken) — both run locally, no cloud dependency, and both are designed specifically for exactly this kind of historical non-Latin-script work.
- **Urdu Katib Handwritten Dataset (UKHD)** adds handwritten-specific Urdu ground truth with a CRNN baseline if MAKHZAN's manuscript coverage isn't enough on its own.
- **Be realistic about accuracy.** Published research on Arabic-script HTR/OCR generally reports meaningfully lower accuracy than Latin or Devanagari HTR — historical benchmarks have shown open-source engines under 75% character accuracy on print, and worse on handwritten historical material, with cursive Nastaliq (the calligraphic style Urdu/Persian documents typically use) being particularly difficult due to right-to-left flow and heavy character-joining. Budget for this being the slowest, most review-heavy branch of the pipeline, and weight the human-confidence-review step (§9.4 Step 5) especially heavily here.

### 9.4 Recommended pipeline architecture — a new branch, feeding the existing system
Add this as a parallel branch to the existing OCR/audio ingestion step in `ai_pipeline.py`, not a replacement:

```
Uploaded scan
   │
   ▼
[Step 1: Document Triage] ── classify: printed-modern / printed-historical /
   │                          handwritten-modern-script / handwritten-historical-script
   │  (cheap local vision-language model call, e.g. Qwen2.5-VL small variant, or a
   │   lightweight image classifier if you want to avoid VLM overhead)
   ▼
[Step 2: Script Identification] ── which script: Devanagari / Modi / Halegannada / Perso-Arabic / Tamil / etc.
   ▼
[Step 3: Route to specialist model]
   ├─ printed-historical (general) → Tesseract + preprocessing (§5.5 pipeline, tuned)
   ├─ handwritten-modern-script → TrOCR fine-tuned on DohaScript/PLATTER
   ├─ Modi script → MoScNet (Modi → Devanagari transliteration)
   ├─ Halegannada → Lipi Gnani (printed); flag handwritten Halegannada as review-heavy (§9.3b)
   └─ Persian/Farsi/Urdu (Perso-Arabic) → Kraken + eScriptorium, trained/fine-tuned on OpenITI MAKHZAN (§9.3c)
   ▼
[Step 4: Transliteration/normalization] ── e.g. Modi→Devanagari output feeds straight into
   │                                          your existing translation (§2.3) and legal-analysis
   │                                          pipeline unchanged — this is the integration point.
   ▼
[Step 5: Confidence scoring + human review flag] ── low-confidence transcriptions MUST be
        flagged in the UI for manual verification before entering legal analysis.
        Never present HTR output as ground truth the way the current RAG stub does (§5.3/§6.3).
```

Step 4 is the key integration point: once handwriting/historical script is transliterated into modern Devanagari (or whichever target script), it re-enters the **existing** pipeline (translation → PII redaction → RAG → synthesis) unchanged. You're not building a second product — you're building a specialist "reader" that feeds the one you already have.

### 9.5 Hardware split for this track
- **Inference** (running MoScNet or a fine-tuned TrOCR on new documents): light enough for your RTX 5070 — these are small, often distilled models by design.
- **Fine-tuning per script** (adapting TrOCR to your own real document scans, or extending MoScNet to a new script): heavier — use the same cloud-rental pattern as QLoRA (§7.3): train on a rented GPU, bring the resulting weights back for local inference.
- **Real land-deed scans you own** are more valuable for fine-tuning than the public datasets alone — but never upload them to any cloud service for this purpose; do cloud-rented training on synthetic/public data first, and keep any fine-tuning on your own real documents to a local or strictly-controlled private environment given the property/ownership PII they likely contain.

### 9.6 Scope discipline
Don't try to build a universal ancient-script reader. Pick the scripts your actual target documents use — Modi + Devanagari, Halegannada, and Perso-Arabic (Persian/Urdu) are the four covered in detail above, each with real datasets and tooling — validate one at a time against real samples before expanding. Each new script is effectively a new specialist model with its own dataset — budget for that rather than assuming one architecture generalizes. Suggested build order by current tooling maturity: **Modi → Halegannada → Perso-Arabic**, since that's the order of decreasing accuracy/tooling readiness per §9.3/9.3b/9.3c.

---

## 10. Implementation Roadmap

- [ ] **Phase 0 — Stop the bleeding (no local-model work needed):**
  - [ ] Fix env var naming (§5.1); rotate exposed Supabase key
  - [ ] Add auth to job status + chat endpoints (§5.2)
  - [ ] Add polling timeout (§5.7); fail loudly on PII redaction failure (§5.6)
  - [ ] Disable/banner the legal-analysis tab until §6.4 steps 1–3 are done

- [ ] **Phase 1 — Local model plumbing:**
  - [ ] Install Ollama + pull generator model (§3)
  - [ ] Swap embedding model to `bge-m3` on CPU (§2.2/§3)
  - [ ] Point `call_openrouter()` at local Ollama endpoint

- [ ] **Phase 2 — Real RAG (§6.4):**
  - [ ] Ingest real legal corpus (§4.1)
  - [ ] Un-stub retrieval nodes; build graph from metadata
  - [ ] Add re-ranker, query rewriting, temporal filtering, chunk-level citations
  - [ ] Build eval set from IL-TUR/ILDC

- [ ] **Phase 3 — Remaining bugs (§5.4, 5.5, 5.8, 5.9):**
  - [ ] Tesseract for printed images; remove dead Celery/Redis
  - [ ] Store `redacted_text` separately; URL parsing fix

- [ ] **Phase 4 — RLHF, done right (§7):**
  - [ ] Fix `rlhf_feedback` schema (add `document_id`, `retrieved_chunk_ids`, `response_text`)
  - [ ] Use feedback for manual curation first
  - [ ] Once volume is sufficient: DPO the re-ranker, then optionally the generator (cloud-rented training)

- [ ] **Phase 5 — STT integration (§8.1):**
  - [ ] `faster-whisper` medium as default; evaluate AI4Bharat Indic-ASR on real regional-language audio samples

- [ ] **Phase 6 — Historical/handwritten document track (§9):**
  - [ ] Scope to the scripts your real documents actually use — start with Modi + Devanagari (§9.3), then Halegannada (§9.3b), then Persian/Urdu (§9.3c), in that order
  - [ ] Stand up the triage → script-ID → specialist-model → transliteration → confidence-flag pipeline
  - [ ] Install Kraken + eScriptorium locally if/when the Perso-Arabic branch is needed
  - [ ] Validate against real samples before trusting output in legal analysis
  - [ ] Fine-tune (cloud-rented) only once the public-dataset baseline is validated and found insufficient

- [ ] **Phase 7 (optional) — TTS (§8.2):** only if an accessibility/read-aloud requirement actually emerges.

---

## 11. Caveats Worth Keeping in Mind

- Local inference solves **privacy/offline**, not **correctness** — a local model hallucinates exactly as confidently as a cloud one. §6's grounding fixes matter more, not less, once everything feels self-contained.
- 8GB VRAM is a real ceiling — build around a model that reliably fits with headroom, not one that occasionally OOMs.
- RLHF is aspirational marketing language in the current codebase, not a working system — §7 is the actual path to making the label true, and it starts with fixing a database schema, not training anything.
- The handwritten/historical-script goal (§9) is the most open-ended item in this document. Resist the urge to scope it broadly at the start — Modi-script land deeds specifically have real, usable datasets and a working reference model (MoScNet) today; ancient scripts with no digitized dataset at all are a much longer research effort and should not block shipping the rest of the system.
- Never let low-confidence HTR/OCR output reach a user as if it were verified — for documents establishing legal rights (land ownership, boundaries), a flagged-for-review low-confidence transcription is the responsible default, not an edge case to handle later.
