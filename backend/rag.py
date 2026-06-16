"""
The RAG core: chunk -> embed -> store/retrieve (Chroma) -> answer (OpenAI).

Design choices that keep this reliable for a beginner:
- We compute embeddings ourselves with OpenAI and hand them to Chroma.
  (Chroma's *default* embedder would silently download a ~80MB model the
  first time -- a classic "why is it hanging?" trap. We avoid it entirely.)
- Every OpenAI call is wrapped so failures return a clear Python exception
  with a readable message instead of a raw stack trace to the browser.
"""
# --- Vercel/Serverless SQLite3 patch ---
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

from __future__ import annotations

import re
from typing import List, Dict, Any

import chromadb

import config

# ---------------------------------------------------------------------------
# OpenAI client (created lazily so importing this file never crashes)
# ---------------------------------------------------------------------------
_client = None


def get_openai():
    """Return a cached OpenAI client, or raise a clear error if no key."""
    global _client
    if not config.HAS_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Open backend/.env and paste your key "
            "(it should start with 'sk-'), then restart the server."
        )
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(api_key=config.OPENAI_API_KEY)
    return _client


# ---------------------------------------------------------------------------
# Chroma (local, persistent vector store)
# ---------------------------------------------------------------------------
_chroma = None


def get_collection():
    """Open (or create) the persistent collection. No network needed."""
    global _chroma
    if _chroma is None:
        _chroma = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    # embedding_function=None -> we always supply embeddings ourselves
    return _chroma.get_or_create_collection(
        name=config.COLLECTION_NAME,
        embedding_function=None,
        metadata={"hnsw:space": "cosine"},
    )


def count_chunks() -> int:
    try:
        return get_collection().count()
    except Exception:
        return 0


def list_topics() -> List[Dict[str, Any]]:
    """
    Inspect the indexed metadata and return the distinct documents/topics the
    assistant can actually answer about. Auto-derived -> add data + re-ingest
    and the website's topic list updates itself. No OpenAI call needed.
    """
    col = get_collection()
    if col.count() == 0:
        return []
    data = col.get(include=["metadatas"])  # all chunks' metadata
    groups: Dict[tuple, Dict[str, Any]] = {}
    for m in (data.get("metadatas") or []):
        m = m or {}
        key = (m.get("source", "Unknown"), m.get("title", ""))
        g = groups.get(key)
        if g is None:
            g = {
                "source": m.get("source", "Unknown"),
                "title": m.get("title", ""),
                "year": m.get("year", ""),
                "evidence_level": m.get("evidence_level", ""),
                "chunks": 0,
            }
            groups[key] = g
        g["chunks"] += 1
    return sorted(groups.values(), key=lambda g: (g["source"], g["title"]))


# ---------------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------------
def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a list of strings with OpenAI in one batched call."""
    client = get_openai()
    resp = client.embeddings.create(model=config.EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------
def chunk_text(text: str, size: int = config.CHUNK_SIZE,
               overlap: int = config.CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping character windows, trying to break on
    paragraph/sentence boundaries so chunks stay readable.
    """
    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    if len(text) <= size:
        return [text] if text else []

    chunks, start = [], 0
    while start < len(text):
        end = start + size
        window = text[start:end]
        # try to end on a clean boundary
        if end < len(text):
            for sep in ("\n\n", "\n", ". "):
                idx = window.rfind(sep)
                if idx > size * 0.5:
                    end = start + idx + len(sep)
                    window = text[start:end]
                    break
        chunk = window.strip()
        if chunk:
            chunks.append(chunk)
        start = max(end - overlap, start + 1)
    return chunks


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------
def retrieve(question: str, top_k: int = config.TOP_K) -> List[Dict[str, Any]]:
    """Return the most relevant chunks for a question, with metadata + score."""
    col = get_collection()
    if col.count() == 0:
        return []
    q_emb = embed_texts([question])[0]
    res = col.query(
        query_embeddings=[q_emb],
        n_results=min(top_k, col.count()),
        include=["documents", "metadatas", "distances"],
    )
    out: List[Dict[str, Any]] = []
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    dists = res["distances"][0]
    for doc, meta, dist in zip(docs, metas, dists):
        # cosine distance -> similarity in [0,1]
        similarity = max(0.0, 1.0 - float(dist))
        out.append({"text": doc, "meta": meta or {}, "score": round(similarity, 3)})
    return out


# ---------------------------------------------------------------------------
# Answering
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = (
    "You are a careful medical knowledge assistant for healthcare professionals. "
    "Answer ONLY using the numbered context provided. "
    "After each claim, cite the source it came from using its number in square "
    "brackets, e.g. [1] or [2]. "
    "If the context does not contain the answer, say clearly that the provided "
    "sources do not cover it -- do NOT use outside knowledge and never invent "
    "facts, doses, or citations. Be concise and clinical."
)


def build_context_block(chunks: List[Dict[str, Any]]) -> str:
    lines = []
    for i, c in enumerate(chunks, 1):
        src = c["meta"].get("source", "Unknown")
        title = c["meta"].get("title", "")
        header = f"[{i}] {src}" + (f" - {title}" if title else "")
        lines.append(f"{header}\n{c['text']}")
    return "\n\n".join(lines)


def confidence_from(chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    A lightweight, honest confidence signal for the MVP based on how well
    the retrieved sources match the question. (Phase 2 replaces this with NLI.)
    """
    if not chunks:
        return {"score": 0, "label": "INSUFFICIENT EVIDENCE", "color": "red"}
    top = chunks[0]["score"]
    avg = sum(c["score"] for c in chunks) / len(chunks)
    pct = round((0.6 * top + 0.4 * avg) * 100)
    if pct >= 80:
        label, color = "HIGH", "green"
    elif pct >= 60:
        label, color = "MEDIUM", "amber"
    elif pct >= 40:
        label, color = "LOW - REVIEW", "orange"
    else:
        label, color = "INSUFFICIENT EVIDENCE", "red"
    return {"score": pct, "label": label, "color": color}


def answer_question(question: str) -> Dict[str, Any]:
    """
    Full RAG turn. Always returns a dict; on a recoverable problem it returns
    an 'error' message instead of throwing, so the API can show it to the user.
    """
    question = (question or "").strip()
    if not question:
        return {"error": "Please type a question."}

    chunks = retrieve(question)
    if not chunks:
        return {
            "answer": "No documents are indexed yet. Run `python ingest.py` "
                      "first to build the knowledge base.",
            "sources": [],
            "confidence": confidence_from([]),
        }

    context = build_context_block(chunks)
    user_prompt = (
        "Context:\n" + context + "\n\n"
        "Question: " + question + "\n\n"
        "Answer using only the context above, with [n] citations."
    )

    client = get_openai()
    completion = client.chat.completions.create(
        model=config.CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
    )
    answer = completion.choices[0].message.content

    sources = [
        {
            "n": i,
            "source": c["meta"].get("source", "Unknown"),
            "title": c["meta"].get("title", ""),
            "evidence_level": c["meta"].get("evidence_level", ""),
            "year": c["meta"].get("year", ""),
            "url": c["meta"].get("url", ""),
            "score": c["score"],
            "snippet": c["text"][:400] + ("…" if len(c["text"]) > 400 else ""),
        }
        for i, c in enumerate(chunks, 1)
    ]
    return {"answer": answer, "sources": sources, "confidence": confidence_from(chunks)}
