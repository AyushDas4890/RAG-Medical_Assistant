# 🧠 PROJECT_CONTEXT — Healthcare Knowledge Navigator

> **Read this first in any new session.** It is the single source of truth for what this
> project is, how it's wired, why decisions were made, and where the traps are.
> Pair it with the interactive map in `knowledge-graph.html` and the data in
> `.project/knowledge-graph.json`.

_Last updated: 2026-06-16 · Owner: AYuSh (Thāne, MH, India) · Stage: MVP working._

---

## 1. One-paragraph summary

A **medical RAG (Retrieval-Augmented Generation) assistant**. A clinician asks a question;
the app retrieves matching chunks from a local vector store of clinical guideline text,
feeds them to an LLM with a strict "answer only from these sources" prompt, and returns a
**citation-grounded** answer plus a **ranked evidence panel** and a **confidence signal**.
If the corpus doesn't cover the question, it says so instead of hallucinating. Frontend is a
**motion-design single page served by the same FastAPI server** as the API.

---

## 2. Tech stack (and why)

| Layer | Choice | Why this, not the fancy thing |
|---|---|---|
| Embeddings | OpenAI `text-embedding-3-small` | No local `torch`/GPU; avoids OOM on a laptop |
| Vector DB | **ChromaDB** (local persistent file) | No Docker/Milvus server to fail |
| LLM | OpenAI `gpt-4o-mini` | Cheap, reliable formatting + citations |
| Backend | **FastAPI + Uvicorn** | Async; serves the UI *and* the API (one origin) |
| Frontend | **Vanilla** HTML/CSS/JS | No build step; premium motion design by hand |
| Deploy | Vercel (serverless) | `pysqlite3-binary` shim patches Chroma's sqlite need |

Everything runs on **one OpenAI API key**. No second service, no Cohere, no UMLS — those are
deferred to Phase 2 (see `WORKING_PLAN_v2.md`).

---

## 3. The defining design decision: kill "unable to fetch"

The owner's recurring blocker on past attempts was the chatbot showing **`unable to fetch`**.
Root cause: that's a browser→backend connection failure (usually CORS from a separate
frontend server on a different port), **not** the LLM.

**Fix baked into the architecture:**
1. FastAPI **serves the frontend itself** (`StaticFiles` + `/` route) → page and API share an
   origin → CORS can't block the call.
2. Frontend calls **relative paths** (`/api/chat`), never `http://localhost:PORT`.
3. Backend **catches every error** and returns readable JSON; the UI prints the *real* reason
   (e.g. "OPENAI_API_KEY is not set") instead of a generic failure.
4. `/api/health` + a status dot surface problems (no key / no data / offline) before asking.

> If you ever refactor to a separate frontend host, you reintroduce the bug. Keep it
> same-origin, or wire CORS + health checks deliberately.

---

## 4. Architecture & data flow

```
Browser (served by FastAPI)
  │  fetch('/api/chat')  ── relative, same origin
  ▼
FastAPI  (backend/main.py)
  ├─ GET  /              → serves frontend/index.html
  ├─ GET  /api/health    → {ok, has_key, num_chunks, chat_model}
  ├─ GET  /api/topics    → distinct indexed docs (auto "Specialised in" list)
  └─ POST /api/chat      → rag.answer_question(question)
                              │
        rag.py:  retrieve() ─┤  embed query (OpenAI) → Chroma cosine query → top-k chunks+scores
                 answer_question() → build grounded prompt → gpt-4o-mini → answer + [n] citations
                 confidence_from() → score from retrieval similarity
                              ▼
                       ChromaDB (backend/chroma_store/, built by ingest.py from backend/data/*.md)
```

---

## 5. File-by-file map (responsibilities)

### backend/
- **`main.py`** — FastAPI app. Routes: `/`, `/api/health`, `/api/topics`, `/api/chat`.
  Permissive CORS (backup), serves `frontend/` via StaticFiles, catches errors → JSON.
  Top of file has a **serverless sqlite3 patch** (`pysqlite3` → `sqlite3`) for Vercel and a
  `sys.path` insert so `import config/rag` works in serverless.
- **`rag.py`** — the RAG core. Key functions:
  - `get_openai()` — lazy client; raises a readable error if no key (never crashes on import).
  - `get_collection()` — Chroma persistent collection, `embedding_function=None` (we embed
    ourselves to avoid Chroma silently downloading a model).
  - `embed_texts()` — OpenAI batch embeddings.
  - `chunk_text()` — ~900-char overlapping chunks on clean boundaries.
  - `retrieve()` — cosine query → chunks with similarity score.
  - `list_topics()` — groups indexed metadata into distinct topics (powers `/api/topics`).
  - `confidence_from()` — MVP confidence from retrieval scores (Phase 2 → NLI).
  - `answer_question()` — full turn; always returns a dict (error or answer+sources+confidence).
- **`ingest.py`** — reads `data/*.md` (+ `--- front matter ---`), chunks, embeds, writes Chroma.
  Run after any data change. Rebuilds the collection from scratch each run.
- **`config.py`** — reads `.env`; exposes `OPENAI_API_KEY`, models, paths, chunk sizes,
  `HAS_KEY`. Never raises if the key is missing.
- **`data/*.md`** — sourced clinical guideline snippets with metadata header
  (`source, title, year, evidence_level, url`). Currently: T2DM, hypertension, AF, headache.
- **`requirements.txt`** — fastapi, uvicorn, openai, chromadb, python-dotenv, pydantic,
  `pysqlite3-binary` (Vercel).
- **`.env.example`** — template; copy to `.env`, paste key.

### frontend/  (all served at the same origin)
- **`index.html`** — landing (hero, search, quick-starts, **"Specialised in"** topics, marquee)
  + app shell (topbar, chat column, evidence panel) + citation modal + custom cursor divs.
- **`style.css`** — design system (navy/teal tokens), aurora mesh bg, glassmorphism, motion
  (cursor, tilt, reveals, shimmer, marquee), full `prefers-reduced-motion` fallback.
- **`app.js`** — all logic: health polling + status dot, view switching, `/api/chat` call with
  real-error display, evidence panel render, confidence meter, citation modal, **auto topics**
  (`loadTopics()` → `/api/topics`), and the motion layer (custom cursor, magnetic buttons, 3D
  tilt, scroll reveals, background parallax, marquee duplication).

### docs / meta
- **`README.md`** — public GitHub readme (banner, badges, Mermaid, Vercel deploy, demo link).
- **`WORKING_PLAN_v2.md`** — the reviewed, lean, MVP-first plan + what was cut from v1.
- **`Healthcare_Knowledge_Navigator_Plan.md` / `_Improved_Plan.md`** — original ambitious plans
  (Milvus, UMLS, rerank, NLI, Next.js). Kept as the Phase-2 north star.
- **`assets/banner.svg`** — README banner.
- **`PROJECT_CONTEXT.md`** (this file) + **`knowledge-graph.html`** + **`.project/knowledge-graph.json`**.

---

## 6. Conventions

- **Data = Markdown + front matter.** To teach a new topic: add `data/<name>.md` with the
  header, then `python ingest.py`. The site's topic list updates itself (no code change).
- **Citations** are `[n]` markers the LLM appends; the frontend turns them into clickable chips
  mapped to `sources[n-1]`.
- **Confidence colors:** 🟢 ≥80 HIGH · 🟡 ≥60 MEDIUM · 🟠 ≥40 LOW · 🔴 <40 INSUFFICIENT.
- **No secrets in git.** `.env` holds the key; only `.env.example` is committed.

---

## 7. Known gotchas / traps

- **"It can't answer X"** is usually correct behavior — X isn't in `data/`. Add a doc + re-ingest.
  Refusing to answer beyond sources is the whole point (zero hallucination).
- **Serverless filesystem is read-only** on Vercel → build/ship the Chroma index at deploy time;
  don't expect to write `chroma_store/` at runtime.
- **Chroma + sqlite on Vercel** needs the `pysqlite3` shim at the very top of `main.py`/`rag.py`
  (already added). Don't remove it.
- **Embeddings are paid API calls.** `ingest.py` and every query hit OpenAI. Batch on ingest.
- **Sandbox mount lag** (dev-only, not your machine): the Linux sandbox sometimes shows files
  truncated at 8 KB — the file tools write the full file to the real disk regardless.

---

## 8. Current state & next steps

**Done:** MVP RAG (retrieve→cite→answer), confidence, motion-design UI, auto topic discovery,
README + banner, Vercel patches.

**Next (Phase 1→2, see WORKING_PLAN_v2.md):**
- [ ] Token-by-token streaming (SSE) — only after base is stable
- [ ] "I don't cover that yet → here's what I do" off-topic fallback with topic chips
- [ ] Hybrid search (BM25 + dense) + reranking
- [ ] UMLS/MeSH query expansion · NLI confidence · RAGAS eval
- [ ] Real bulk data ingestion (PubMed/NICE/CDC/WHO)

---

## 9. Fast re-onboarding checklist (for future me)

1. Read this file + open `knowledge-graph.html`.
2. `cd backend` → venv → `pip install -r requirements.txt` → `.env` key → `python ingest.py` →
   `uvicorn main:app --reload` → http://127.0.0.1:8000.
3. Status dot green? Good. Ask a quick-start question. Inspect a citation.
4. To extend coverage: add `data/*.md` + re-ingest. To change behavior: edit `rag.py`.
