# 🏥 Healthcare Knowledge Navigator — Working Plan v2 (MVP-first)

> Goal: get a **running** medical RAG app today, then layer the fancy parts. Built to kill the "unable to fetch" bug.

---

## 1. Review of the old plan — what to keep, fix, cut

| Area | Old plan | Verdict | Why |
|---|---|---|---|
| Vector DB | Milvus / Zilliz Cloud | **Cut → ChromaDB** | Milvus needs Docker + a server. Chroma is a local file. Zero infra to fail. |
| Embeddings | BioLinkBERT / MedCPT (local) | **Cut for MVP → OpenAI `text-embedding-3-small`** | Local medical models pull `torch` (~2GB) and often OOM on a laptop. One of your past blockers. |
| LLM | MedLM / GPT-4o / Llama-3 70B | **→ OpenAI `gpt-4o-mini`** | You chose OpenAI. `4o-mini` is cheap + reliable + supports the format we need. |
| Query expansion | UMLS / MeSH / quickumls | **Defer to Phase 2** | `quickumls` needs a licensed UMLS download. Big setup, not needed to prove RAG works. |
| Hybrid + rerank | BM25 + RRF + Cohere | **Defer to Phase 2** | Another API key (Cohere) + more failure points. Dense-only retrieval is fine for MVP. |
| NLI confidence | DeBERTa-v3 | **Cut → lightweight confidence** | Another `torch` model. MVP uses retrieval-score + source evidence-level instead. |
| Streaming | FastAPI SSE → React stream | **Defer** | SSE is a common source of "unable to fetch"/timeout bugs. MVP returns the full answer in one clean JSON response. Add streaming once stable. |
| Frontend | Separate Next.js app | **Change → single page served BY FastAPI** | **This is the real fix for your bug.** Two servers (Next.js + FastAPI) on different ports = CORS = "unable to fetch". One server, one origin → fetch always works. |
| UI quality | Full design system | **Keep** | Motion-design dark clinical UI, just built as one served page for now. |
| Citations / evidence panel | Click → highlighted source | **Keep (simplified)** | Citations `[1]` + evidence cards. Modal highlight later. |

### Root cause of "unable to fetch"
It's a **frontend → backend connection failure**, not the LLM. Top causes and how v2 prevents each:
1. **CORS blocked** → we serve the page from the same FastAPI origin, *and* enable permissive CORS as backup.
2. **Backend not running / wrong URL** → frontend calls a relative path `/api/chat`, never a hardcoded `localhost:port`.
3. **Bad API key → 500 → generic "unable to fetch"** → backend catches errors and returns a readable message the UI displays (e.g. "OPENAI_API_KEY not set"), so you always know the real cause.
4. **Health unknown** → a `/api/health` endpoint + a status dot in the UI tell you instantly if the server and key are OK.

---

## 2. MVP architecture (what we build now)

```
Browser (one page, served by FastAPI)
        │  fetch('/api/chat')   ← relative, same origin, no CORS
        ▼
FastAPI  ──────────────────────────────────────────
  /              → serves the motion-design frontend
  /api/health    → { ok, has_key, num_chunks }
  /api/chat      → RAG: retrieve → build prompt → OpenAI → answer + citations
        │
        ▼
ChromaDB (local folder)  ←  ingest.py builds it from data/*.md
        ▲
        │  OpenAI text-embedding-3-small
   OpenAI gpt-4o-mini  → grounded answer with [1][2] citations
```

**Stack (MVP):** FastAPI · Uvicorn · ChromaDB · OpenAI (embeddings + chat) · vanilla HTML/CSS/JS frontend (motion design). No torch, no Docker, one API key.

---

## 3. Build phases

**Phase 0 — MVP (today)**
- FastAPI app that serves the UI + `/api/health` + `/api/chat`
- Chroma vector store, OpenAI embeddings, `gpt-4o-mini` answers
- Citations + a basic confidence signal from retrieval scores
- Motion-design dark clinical single-page UI
- Sample sourced medical guideline data
- ✅ Done = you type a question, get a grounded answer with sources, no "unable to fetch"

**Phase 1 — quality**
- More real data (PubMed/NICE/CDC ingestion scripts)
- Token-by-token streaming (SSE) once base is stable
- Better confidence (self-reflection score)

**Phase 2 — advanced (the original ambition)**
- Hybrid search (BM25 + dense) + RRF
- Cohere / bge reranking
- UMLS/MeSH query expansion
- NLI (DeBERTa) confidence
- RAGAS evaluation harness

---

## 4. Run it (Windows)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env        # then paste your OpenAI key into .env
python ingest.py              # builds the vector store from data/
uvicorn main:app --reload     # open http://127.0.0.1:8000
```

If the chat ever errors, the UI now shows the **real** reason — no more guessing.

---

*v2 — MVP-first, reliability-first. June 2026.*
