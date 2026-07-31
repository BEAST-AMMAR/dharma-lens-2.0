import sys
import os
import glob
import site
import pydantic
from dotenv import load_dotenv

# LangChain Core / LangGraph Pydantic v1 compatibility shim
try:
    import langchain_core
    try:
        import pydantic.v1 as pydantic_v1
    except ImportError:
        pydantic_v1 = pydantic
    sys.modules['langchain_core.pydantic_v1'] = pydantic_v1
except Exception as _lc_err:
    pass

# 1. Import binary/core framework dependencies first using active interpreter environment
from fastapi import FastAPI, HTTPException, Header, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid

# Append user site-packages for the current Python interpreter version if present
user_site = site.getusersitepackages()
if os.path.exists(user_site) and user_site not in sys.path:
    sys.path.append(user_site)

# Ensure active hermes-agent venv site-packages is included
hermes_venv_site = os.path.expanduser(r"~\AppData\Local\hermes\hermes-agent\venv\Lib\site-packages")
if os.path.exists(hermes_venv_site) and hermes_venv_site not in sys.path:
    sys.path.append(hermes_venv_site)

from supabase import create_client

load_dotenv()

# ──────────────────────────────────────────────────────────────────
# FAIL-FAST STARTUP VALIDATION — No hardcoded fallback credentials
# ──────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("VITE_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("VITE_SUPABASE_ANON_KEY")

if not SUPABASE_URL:
    raise RuntimeError("CRITICAL: VITE_SUPABASE_URL environment variable is missing. Refusing to start.")
if not SUPABASE_KEY:
    raise RuntimeError("CRITICAL: VITE_SUPABASE_ANON_KEY environment variable is missing. Refusing to start.")

app = FastAPI(title="Dharma Lens ML Engine", version="3.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:3000", "http://localhost:5173", "https://dharma-lens.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProcessConfig(BaseModel):
    targetLanguage: str
    summaryLength: int
    enableOCR: bool
    enableSummarization: bool
    enableTranslation: bool
    enableAudioTranscription: bool
    enableLegalAnalysis: bool
    enableEntityExtraction: bool
    processingMode: str = "hybrid"
    enableHistoricalHTR: bool = False
    historicalScriptType: str = "auto"

class ProcessRequest(BaseModel):
    documentPath: str
    config: ProcessConfig

class ChatRequest(BaseModel):
    document_text: str
    query: str
    chat_history: list
    config: dict = None

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Dharma Lens ML Engine", "version": "3.0.0"}

# Instantiate module-level Supabase client once at startup
supabase_auth_client = create_client(SUPABASE_URL, SUPABASE_KEY)

def verify_supabase_token(authorization: str):
    """
    Validates the JWT token against Supabase Auth.
    Uses environment-validated SUPABASE_URL and SUPABASE_KEY (no hardcoded fallbacks).
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized - Missing Authorization Header")
    token = authorization.replace("Bearer ", "")
    
    try:
        user = supabase_auth_client.auth.get_user(token)
        if not user or not getattr(user, 'user', None):
            raise HTTPException(status_code=401, detail="Invalid Authentication Token")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication Failed: {str(e)}")

@app.post("/chat")
async def chat_with_document(request: ChatRequest, authorization: str = Header(None)):
    verify_supabase_token(authorization)
    
    try:
        from services.ai_pipeline import call_llm_hybrid
        
        system_prompt = f"You are an expert Indian Legal AI assistant. Answer the user's query precisely using ONLY the following document context:\n\n{request.document_text[:15000]}"
        
        user_prompt = "History:\n"
        for msg in request.chat_history:
            user_prompt += f"{msg.get('role', 'user')}: {msg.get('content', '')}\n"
        user_prompt += f"\nUser: {request.query}"

        config = request.config or {}
        response = call_llm_hybrid(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            config=config
        )
        
        return {"success": True, "reply": response}
    except Exception as e:
        print(f"Chat Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# In-memory job store for local development (replaces Redis/Celery)
job_store = {}

def background_process(job_id: str, document_path: str, config: dict, auth_token: str):
    try:
        from services.ai_pipeline import process_document_pipeline
        job_store[job_id] = {"status": "processing"}
        result = process_document_pipeline(document_path, config, auth_token)
        job_store[job_id] = {"status": "completed", "result": result}
    except Exception as e:
        print(f"[Background Job {job_id} FAILED]: {str(e)}")
        job_store[job_id] = {"status": "failed", "error": str(e)}

@app.post("/process")
async def process_document(request: ProcessRequest, background_tasks: BackgroundTasks, authorization: str = Header(None)):
    verify_supabase_token(authorization)
    
    try:
        job_id = str(uuid.uuid4())
        job_store[job_id] = {"status": "pending"}
        background_tasks.add_task(background_process, job_id, request.documentPath, request.config.dict(), authorization)
        
        return {"success": True, "job_id": job_id}
    except Exception as e:
        print(f"Error in python ML engine: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/job/{job_id}")
async def get_job_status(job_id: str, authorization: str = Header(None)):
    verify_supabase_token(authorization)
    job = job_store.get(job_id)
    if not job:
        return {"status": "failed", "error": "Job not found"}
    return job

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
