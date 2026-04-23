from app import rag
from app.celery_app import celery_app


@celery_app.task(name="app.tasks.ingest_pdf_task")
def ingest_pdf_task(pdf_path: str, pdf_id: str) -> dict:
    message = rag.ingest_pdf(pdf_path, pdf_id)
    return {"pdf_id": pdf_id, "message": message}
