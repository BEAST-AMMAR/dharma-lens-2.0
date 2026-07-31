import os
from celery import Celery
from services.ai_pipeline import process_document_pipeline

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "dharma_lens_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

@celery_app.task(bind=True, name="process_document_task")
def process_document_task(self, document_path: str, config: dict, auth_token: str):
    try:
        result = process_document_pipeline(document_path, config, auth_token)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
