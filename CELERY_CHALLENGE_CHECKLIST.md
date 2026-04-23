# Celery wiring: `main.py` vs `celery_app.py` vs `tasks.py`

Use this as a challenge checklist. Your FastAPI side is already calling Celery; the questions below are about making the **worker** reliably see your tasks and behave well in production.

---

## What `main.py` is already doing

- Imports `celery_app` from `app.celery_app`.
- On `/upload`, saves the PDF, then calls `ingest_pdf_task.delay(pdf_path, pdf_id)` from `app.tasks`.
- Exposes `/status/{task_id}` using `AsyncResult(task_id, app=celery_app)` so status matches the same broker/backend as the app.

You do **not** need extra Celery-specific code in `main.py` for this basic flow unless you add features (e.g. revoke task, custom states, websockets for progress).

---

## `celery_app.py` — things to verify or add (challenge items)

1. **Task registration (important)**  
   The worker process only loads what Celery imports. If nothing ever imports `app.tasks`, your `@celery_app.task` may **not** be registered when you start the worker with `-A app.celery_app`.  
   - **Challenge:** Confirm how you start the worker (`celery -A ... worker`) and whether `ingest_pdf_task` appears in the worker logs at startup.  
   - **Typical fix pattern:** either explicitly import the tasks module from your Celery app module, or use Celery’s autodiscover/include mechanism so `app.tasks` is always loaded with the app.

2. **Broker and result backend**  
   You already read `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` from the environment with Redis defaults.  
   - **Challenge:** Ensure `.env` (or the shell that runs **both** uvicorn and the worker) sets the same URLs so API and worker talk to the same Redis DBs.

3. **Optional production-oriented settings** (only if you want the extra challenge)  
   Things people often add later: task time limits, result expiry, timezone/UTC, worker prefetch, routing for multiple queues. None are strictly required for a minimal “enqueue + poll status” demo.

---

## `tasks.py` — what you have vs optional extensions

**What you already have**

- Task bound to the same `celery_app` instance as `main.py`.
- Task calls `rag.ingest_pdf` and returns a dict (good for JSON result backend).

**Optional challenges (not required for “it works”)**

1. **Retries** — If ingestion can fail transiently (network, API limits), consider retry policy on the task.  
2. **`bind=True`** — Lets the task update state (`self.update_state`) for richer `/status` than PENDING/STARTED/SUCCESS.  
3. **Idempotency** — Same `pdf_id` enqueued twice: should the second run skip or overwrite? That logic can live in `rag` or in the task.  
4. **Large files / long runs** — Soft and hard time limits on the task if you worry about stuck workers.

---

## Operational checklist (outside these three files)

- Redis running and reachable at the URLs you configured.
- Worker command uses the **same** Celery app object path you configured (same `broker`/`backend` as `celery_app.py`).
- Same Python environment and env vars for FastAPI and the worker (especially anything `rag.ingest_pdf` needs: API keys, paths to `uploads/`, Chroma paths, etc.).
- `uploads/` path: worker cwd should resolve `uploads/{pdf_id}.pdf` the same way the API saved it (relative vs absolute paths is a common pitfall).

---

## Short answers to “do I need to add something?”

| File            | Required for minimal flow                         | Common gap to fix yourself                          |
|-----------------|---------------------------------------------------|-----------------------------------------------------|
| `main.py`       | Already sufficient for enqueue + status poll    | Only if you add new endpoints or error handling     |
| `celery_app.py` | Broker/backend + `celery_app` instance is enough| **Ensure tasks module is loaded** on worker startup |
| `tasks.py`      | Your task definition is enough for the demo      | Retries, progress, limits — when you want them    |

Work through the **task registration** and **same Redis + same paths** items first; they are the usual reasons “it works in main but the worker says unknown task or never finishes.”
