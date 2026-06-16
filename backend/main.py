"""
FastAPI app.

Two jobs:
1. Serve the single-page frontend (so it's the SAME origin as the API ->
   the browser's fetch() can never be blocked by CORS -> no "unable to fetch").
2. Expose /api/health and /api/chat.

Run:  uvicorn main:app --reload     (from the backend/ folder)
Open: http://127.0.0.1:8000
"""
# --- Vercel/Serverless SQLite3 patch ---
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import config
import rag

app = FastAPI(title="Healthcare Knowledge Navigator", version="0.1.0")

# Permissive CORS as a *backup* (the same-origin serving already prevents the
# common failure; this just means calling the API from elsewhere also works).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


@app.get("/api/health")
def health():
    """Quick status the UI polls on load: is the server up + key present + indexed?"""
    return {
        "ok": True,
        "has_key": config.HAS_KEY,
        "num_chunks": rag.count_chunks(),
        "chat_model": config.CHAT_MODEL,
    }


@app.get("/api/topics")
def topics():
    """The topics the assistant currently specializes in (from the index)."""
    try:
        return {"topics": rag.list_topics()}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"{type(e).__name__}: {e}"})


@app.post("/api/chat")
def chat(req: ChatRequest):
    """
    RAG endpoint. We catch every error and return it as readable JSON with a
    200/400/500 status so the frontend can DISPLAY the real reason instead of
    showing a generic 'unable to fetch'.
    """
    try:
        result = rag.answer_question(req.question)
        if "error" in result:
            return JSONResponse(status_code=400, content=result)
        return result
    except RuntimeError as e:
        # e.g. missing API key -- a known, user-fixable problem
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        # anything unexpected (network, OpenAI outage, bad model name, ...)
        return JSONResponse(
            status_code=500,
            content={"error": f"{type(e).__name__}: {e}"},
        )


# --- Serve the frontend (mounted LAST so it doesn't shadow /api routes) ------
if config.FRONTEND_DIR.exists():
    @app.get("/")
    def index():
        return FileResponse(config.FRONTEND_DIR / "index.html")

    app.mount("/", StaticFiles(directory=str(config.FRONTEND_DIR)), name="frontend")
