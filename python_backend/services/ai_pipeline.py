import os
import requests
import json
import tempfile
import fitz  # PyMuPDF
from supabase import create_client, ClientOptions

# ──────────────────────────────────────────────────────────────────
# FAIL-FAST ENVIRONMENT — No hardcoded fallback credentials
# ──────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("VITE_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("VITE_SUPABASE_ANON_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL:
    raise RuntimeError("CRITICAL: VITE_SUPABASE_URL environment variable is missing.")
if not SUPABASE_KEY:
    raise RuntimeError("CRITICAL: VITE_SUPABASE_ANON_KEY environment variable is missing.")

def get_supabase_client(auth_token: str = None):
    """
    Creates a Supabase client. Uses provided JWT auth_token, with fallback
    to SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY for background storage tasks.
    """
    if auth_token:
        token = auth_token.replace("Bearer ", "")
        opts = ClientOptions(headers={"Authorization": f"Bearer {token}"})
        return create_client(SUPABASE_URL, SUPABASE_KEY, options=opts)
    
    key = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY
    return create_client(SUPABASE_URL, key)

def call_ollama(system_prompt: str, user_prompt: str, is_json: bool = False, model: str = "qwen2.5:7b-instruct-q4_K_M"):
    """
    Calls local Ollama instance running Qwen2.5-7B or fallback models.
    """
    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False
    }
    if is_json:
        payload["format"] = "json"

    try:
        response = requests.post(url, json=payload, timeout=120)
    except requests.exceptions.ConnectionError:
        raise Exception(f"Local Ollama service is not running at {OLLAMA_BASE_URL}. Please start Ollama or switch to Hybrid / Cloud mode.")
    except Exception as e:
        raise Exception(f"Failed to connect to local Ollama: {str(e)}")

    if response.status_code != 200:
        raise Exception(f"Ollama Error ({response.status_code}): {response.text}")
    
    result = response.json()
    content = result.get("message", {}).get("content", "").strip()
    if is_json:
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    return content

def call_openrouter(system_prompt: str, user_prompt: str, is_json: bool = False):
    """
    Calls OpenRouter multi-provider API for cloud-based inference with updated active free candidate models.
    Includes automatic JSON extraction fallback when response_format parameter is unsupported by free provider.
    """
    if not OPENROUTER_API_KEY:
        raise Exception("OPENROUTER_API_KEY is not set in environment.")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://dharma-lens.vercel.app",
        "X-Title": "Dharma Lens Engine"
    }
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    candidate_models = [
        "openrouter/free",
        "google/gemma-4-31b-it:free",
        "google/gemma-4-26b-a4b-it:free",
        "inclusionai/ling-3.0-flash:free",
        "nvidia/nemotron-3-nano-30b-a3b:free",
        "openai/gpt-oss-20b:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "openrouter/auto"
    ]
    
    last_exception = None
    
    for model_id in candidate_models:
        # First attempt with response_format if requested
        attempts = [{"use_rf": True}] if is_json else [{"use_rf": False}]
        if is_json:
            attempts.append({"use_rf": False}) # Fallback without response_format

        for attempt in attempts:
            payload = {
                "model": model_id,
                "messages": messages
            }
            if is_json and attempt["use_rf"]:
                payload["response_format"] = {"type": "json_object"}
                
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    if is_json:
                        content = content.replace("```json", "").replace("```", "").strip()
                        # Clean leading/trailing text around JSON block if present
                        start = content.find("{")
                        end = content.rfind("}")
                        if start != -1 and end != -1 and end > start:
                            content = content[start:end+1]
                        return json.loads(content)
                    return content
                else:
                    last_exception = Exception(f"OpenRouter Error ({response.status_code}): {response.text}")
                    print(f"[OpenRouter Warning] Model {model_id} (rf={attempt['use_rf']}) returned status {response.status_code}.")
            except Exception as e:
                last_exception = e
                print(f"[OpenRouter Warning] Request to {model_id} failed: {e}.")

    if last_exception:
        raise last_exception
    raise Exception("OpenRouter request failed for all candidate models.")

def call_llm_hybrid(system_prompt: str, user_prompt: str, is_json: bool = False, config: dict = None):
    """
    Hybrid Model Dispatcher:
    - mode == 'local': Ollama local execution
    - mode == 'cloud': OpenRouter API execution
    - mode == 'hybrid' (default): Try Ollama local first; failover to OpenRouter if local fails.
    """
    mode = (config or {}).get("processingMode", "hybrid").lower()

    if mode == "local":
        try:
            return call_ollama(system_prompt, user_prompt, is_json=is_json)
        except Exception as e:
            if "not running" in str(e):
                raise Exception(f"Local Offline Mode failed: {str(e)}")
            print(f"[Ollama Primary Failed]: {e}. Attempting Phi-4 mini local fallback...")
            return call_ollama(system_prompt, user_prompt, is_json=is_json, model="phi4-mini:q4_K_M")

    elif mode == "cloud":
        return call_openrouter(system_prompt, user_prompt, is_json=is_json)

    else:
        # Default Hybrid Mode: Try local first, seamless cloud failover
        try:
            print("[Hybrid Mode] Dispatching query to local Ollama...")
            return call_ollama(system_prompt, user_prompt, is_json=is_json)
        except Exception as local_err:
            print(f"[Hybrid Mode Warning] Local Ollama unavailable ({local_err}). Failing over to Cloud OpenRouter...")
            return call_openrouter(system_prompt, user_prompt, is_json=is_json)

def extract_text_from_pdf(file_bytes):
    """
    Robust PDF text extraction using PyMuPDF (fitz).
    If extracted raw text is empty/insufficient (scanned PDF), automatically renders pages to images
    and processes via PyTesseract OCR.
    """
    text = ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(file_bytes)
        temp_pdf.flush()
        try:
            doc = fitz.open(temp_pdf.name)
            for page in doc:
                text += page.get_text()
            
            # Scanned PDF check: If page text is empty or under 30 chars, perform Tesseract OCR on rendered images
            if not text or len(text.strip()) < 30:
                print("[PDF Processing] Scanned PDF detected (no embedded text). Rendering pages for Tesseract OCR...")
                ocr_text = ""
                from services.htr_pipeline import process_printed_image_ocr
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap(dpi=150)
                    img_bytes = pix.tobytes("png")
                    page_ocr = process_printed_image_ocr(img_bytes)
                    ocr_text += f"\n--- Page {page_num + 1} ---\n" + page_ocr.get("transcribed_text", "")
                if ocr_text.strip():
                    text = ocr_text
            doc.close()
        except Exception as e:
            print(f"[PDF PyMuPDF warning]: {e}. Attempting pypdf fallback...")
            try:
                import pypdf
                reader = pypdf.PdfReader(temp_pdf.name)
                for page in reader.pages:
                    text += page.extract_text() or ""
            except Exception as e2:
                os.remove(temp_pdf.name)
                raise Exception(f"Failed to extract PDF text: {str(e2)}")
    os.remove(temp_pdf.name)
    return text


def transcribe_audio_file(file_bytes: bytes, extension: str) -> str:
    """Local Speech-to-Text transcription via faster-whisper (medium model)."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_audio:
        temp_audio.write(file_bytes)
        temp_audio.flush()
        
        try:
            from faster_whisper import WhisperModel
            model = WhisperModel("medium", device="cuda", compute_type="int8_float16")
            segments, info = model.transcribe(temp_audio.name)
            transcript = " ".join([segment.text for segment in segments])
            os.remove(temp_audio.name)
            return transcript
        except Exception as e:
            print(f"[faster-whisper local failed]: {e}. Falling back to standard Whisper API...")
            try:
                from openai import OpenAI
                client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
                with open(temp_audio.name, "rb") as audio_file:
                    res = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
                os.remove(temp_audio.name)
                return res.text
            except Exception as cloud_err:
                os.remove(temp_audio.name)
                raise Exception(f"Speech transcription failed: {str(cloud_err)}")

def process_document_pipeline(document_path: str, config: dict, auth_token: str):
    # 1. Download file from Supabase Storage with auth fallback
    try:
        supabase = get_supabase_client(auth_token)
        res = supabase.storage.from_("documents").download(document_path)
    except Exception as download_err:
        print(f"[Supabase Download Warning] User auth download failed ({download_err}). Retrying with service role client...")
        supabase = get_supabase_client(None)
        res = supabase.storage.from_("documents").download(document_path)

    file_bytes = res
    
    extracted_text = ""
    htr_metadata = None
    lower_path = document_path.lower()
    is_audio = lower_path.endswith(('.mp3', '.wav', '.m4a', '.mp4', '.flac', '.ogg'))
    is_image = lower_path.endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.webp'))
    is_pdf = lower_path.endswith('.pdf')
    is_text_file = lower_path.endswith(('.txt', '.md', '.json', '.csv', '.rtf', '.log', '.html'))
    
    # 2. Extract Text / Transcribe / HTR
    if is_audio and config.get("enableAudioTranscription"):
        ext = os.path.splitext(document_path)[1]
        extracted_text = transcribe_audio_file(file_bytes, ext)

    elif is_image or config.get("enableHistoricalHTR"):
        from services.htr_pipeline import triage_and_transcribe_historical_doc
        ext = os.path.splitext(document_path)[1]
        htr_result = triage_and_transcribe_historical_doc(file_bytes, ext, config)
        extracted_text = htr_result.get("transcribed_text", "")
        htr_metadata = {
            "script_type": htr_result.get("script_type"),
            "confidence_score": htr_result.get("confidence_score"),
            "needs_human_verification": htr_result.get("needs_human_verification")
        }

    elif is_pdf:
        extracted_text = extract_text_from_pdf(file_bytes)

    elif is_text_file:
        try:
            extracted_text = file_bytes.decode('utf-8', errors='ignore')
        except Exception:
            extracted_text = ""

    elif config.get("enableOCR") and not is_audio:
        from services.htr_pipeline import process_printed_image_ocr
        htr_res = process_printed_image_ocr(file_bytes)
        extracted_text = htr_res.get("transcribed_text", "")

    # Final fallback attempt for unclassified document types
    if not extracted_text or not extracted_text.strip():
        print("[Extraction Fallback] Attempting direct text decode & Tesseract OCR fallback...")
        try:
            raw_decoded = file_bytes.decode('utf-8', errors='ignore')
            if len(raw_decoded.strip()) > 10 and not any(ord(c) == 0 for c in raw_decoded[:100]):
                extracted_text = raw_decoded
        except Exception:
            pass

        if not extracted_text or not extracted_text.strip():
            try:
                from services.htr_pipeline import process_printed_image_ocr
                htr_res = process_printed_image_ocr(file_bytes)
                extracted_text = htr_res.get("transcribed_text", "")
            except Exception:
                pass

    if not extracted_text or not extracted_text.strip():
        raise Exception("Failed to extract text or transcribe audio from the document. Please ensure it is a valid format.")

    # ──────────────────────────────────────────────────────────────
    # FAIL-SAFE PII REDACTION — Halt pipeline on anonymization error
    # ──────────────────────────────────────────────────────────────
    from services.pii_redactor import redact_pii, PIIRedactionException
    try:
        safe_text = redact_pii(extracted_text)
    except PIIRedactionException as pii_err:
        raise Exception(
            f"PRIVACY GUARD: PII redaction failed. Document processing halted to prevent data leakage. "
            f"Details: {str(pii_err)}"
        )

    # Truncate safe text for LLM analysis window
    text_for_analysis = safe_text[:15000]
    
    summary = ""
    translation = ""
    legal_analysis = {}
    entities = {}
    
    if config.get("enableSummarization"):
        summary = call_llm_hybrid(
            f"You are a legal AI assistant. Summarize the following document in exactly {config.get('summaryLength', 200)} words.",
            text_for_analysis,
            config=config
        )
        
    if config.get("enableTranslation") and config.get("targetLanguage") and config.get("targetLanguage") != "auto":
        translation = call_llm_hybrid(
            f"You are an expert legal translator. Translate the text accurately to {config.get('targetLanguage')}.",
            text_for_analysis,
            config=config
        )
        
    if config.get("enableLegalAnalysis"):
        from services.agent_rag import run_agentic_rag
        legal_analysis = run_agentic_rag(text_for_analysis, config=config)
        
    if config.get("enableEntityExtraction"):
        entities = call_llm_hybrid(
            "Extract legal entities into JSON with keys: people, organizations, locations, dates.",
            text_for_analysis,
            is_json=True,
            config=config
        )
        
    result_data = {
        "text": extracted_text,
        "redacted_text": safe_text,
        "summary": summary,
        "translation": translation,
        "legalAnalysis": legal_analysis,
        "entities": entities,
        "htrMetadata": htr_metadata
    }
    
    return result_data
