from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from fastapi.staticfiles import StaticFiles
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from celery.result import AsyncResult
from app.celery_app import celery_app
from app.schemas import AskRequest, CacheRequest
from . import rag

import os
import uuid

# ------------------ Config ------------------
limiter = Limiter(key_func=get_remote_address)
MAX_SIZE = 10 * 1024 * 1024  # 10MB
UPLOAD_DIR = "uploads"

# ------------------ App Init ------------------
app = FastAPI()
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


os.makedirs(UPLOAD_DIR, exist_ok=True)

# ------------------ Exception Handler ------------------
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Too many requests. Max 5 uploads per minute."}
    )

# ------------------ CORS ------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ Health ------------------
@app.get("/")
def health():
    return {"status": "ok"}

# ------------------ Upload ------------------
@app.post("/upload")
@limiter.limit("5/minute")
async def upload_pdf(request: Request, file: UploadFile = File(...)):

    # Validate content type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    pdf_id = str(uuid.uuid4())
    pdf_path = os.path.join(UPLOAD_DIR, f"{pdf_id}.pdf")

    size = 0

    try:
        with open(pdf_path, "wb") as f:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                size += len(chunk)

                if size > MAX_SIZE:
                    os.remove(pdf_path)
                    raise HTTPException(status_code=400, detail="File too large. Max 10MB")

                f.write(chunk)

        await file.close()

    except HTTPException:
        raise
    except Exception:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        raise HTTPException(status_code=500, detail="File save failed")

    # Trigger Celery task
    from app.tasks import ingest_pdf_task
    task = ingest_pdf_task.delay(pdf_path, pdf_id)

    return {
        "pdf_id": pdf_id,
        "task_id": task.id,
        "status": "processing"
    }

# ------------------ Ask ------------------
@app.post("/ask")
async def ask_question(payload: AskRequest):

    pdf_id = payload.pdf_id

    if not pdf_id:
        pdf_id = rag.find_pdf_by_contact(
            email=payload.email,
            name=payload.name,
            phone=payload.phone
        )

    if not pdf_id:
        raise HTTPException(
            status_code=400,
            detail="Provide pdf_id or email/name/phone"
        )

    try:
        answer = rag.ask_question(
            payload.question,
            pdf_id,
            history=payload.history,
            cache_mode=payload.cache_mode,
        )
    except rag.DocumentQueryError as exc:
        return JSONResponse(
            status_code=503,
            content={"error": exc.message, "pdf_id": pdf_id}
        )

    return {"answer": answer, "pdf_id": pdf_id}

# ------------------ Cache Clear ------------------
@app.post("/cache/clear")
async def clear_cache(payload: CacheRequest):

    if payload.scope not in {"pdf", "all"}:
        raise HTTPException(
            status_code=400,
            detail="scope must be 'pdf' or 'all'"
        )

    if payload.scope == "all":
        rag.clear_answer_cache()
        return {
            "status": "ok",
            "scope": "all",
            "message": "All answer cache cleared"
        }

    if not payload.pdf_id:
        raise HTTPException(
            status_code=400,
            detail="pdf_id is required when scope is 'pdf'"
        )

    deleted = rag.clear_answer_cache(pdf_id=payload.pdf_id)

    return {
        "status": "ok",
        "scope": "pdf",
        "pdf_id": payload.pdf_id,
        "deleted_keys": deleted
    }

# ------------------ Task Status ------------------
@app.get("/status/{task_id}")
def get_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": result.status,
        "result": (
            str(result.result) if result.failed()
            else result.result if result.ready()
            else None
        )
    }

app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")
