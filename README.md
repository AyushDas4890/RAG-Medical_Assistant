# 🏥 Healthcare Knowledge Navigator

A lean, **working** medical RAG assistant. Ask a clinical question → get an
answer grounded only in indexed sources, with citations, an evidence panel,
and a confidence signal. Motion-design dark clinical UI.

Built MVP-first to be reliable for a beginner. The whole thing is **one
FastAPI server** (it serves the web page *and* the API), so the browser and
backend share an origin — the classic **"unable to fetch"** error can't happen.

---

## What's inside

```
backend/
  main.py          FastAPI: serves the UI + /api/health + /api/chat
  rag.py           chunk → embed (OpenAI) → Chroma retrieve → answer
  ingest.py        build the vector store from data/
  config.py        reads .env (never crashes if the key is missing)
  data/*.md        sample sourced guideline snippets (NICE)
  requirements.txt
  .env.example
frontend/
  index.html  style.css  app.js     motion-design single page
WORKING_PLAN_v2.md  the reviewed, leaner plan
```

**Stack:** FastAPI · ChromaDB (local file) · OpenAI (`text-embedding-3-small`
+ `gpt-4o-mini`). No Docker, no torch, one API key.

---

## Run it (Windows)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

copy .env.example .env
# open .env and paste your OpenAI key (starts with sk-)

python ingest.py            # builds the knowledge base (needs the key)
uvicorn main:app --reload   # then open http://127.0.0.1:8000
```

macOS/Linux: `source .venv/bin/activate` and `cp .env.example .env`.

Try a quick-start chip, or ask: *"What is first-line treatment for type 2
diabetes with CKD?"*

---

## The status dot tells you everything

Top-right of the app shows live server health:

| Dot | Meaning | Fix |
|---|---|---|
| 🟢 green | online, data indexed | — |
| 🟠 amber | server up, **no data** | run `python ingest.py` |
| 🔴 red — no key | key missing/invalid | paste key into `backend/.env`, restart |
| 🔴 red — offline | server not running | start `uvicorn main:app --reload` |

If a question ever fails, the chat shows the **real reason** (e.g. quota,
bad model name) instead of a generic error — so you always know what to fix.

---

## "Unable to fetch" — why it won't happen here

That error means the browser couldn't reach the backend. This build prevents it:
1. The page is served **by FastAPI itself** → same origin → no CORS block.
2. The frontend calls **relative paths** (`/api/chat`), never `localhost:port`.
3. Backend **catches every error** and returns readable JSON the UI displays.
4. A `/api/health` check + status dot surface problems before you even ask.

---

## Next steps (Phase 1 → 2)

Streaming answers (SSE) · more real data (PubMed/CDC/WHO ingest) · hybrid
search + reranking · UMLS query expansion · NLI confidence · RAGAS eval.
See `WORKING_PLAN_v2.md`.

---

> ⚠️ **Note:** The bundled `data/` snippets are short, illustrative summaries
> for demonstrating the pipeline. This is a software demo, **not a clinical
> tool** — do not use it for real patient decisions. Replace `data/` with your
> own verified corpus before any serious use.
