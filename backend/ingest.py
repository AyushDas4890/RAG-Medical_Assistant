"""
Build the vector store from the documents in backend/data/.

Run once (and again whenever you add/change data):
    python ingest.py

Each .md/.txt file may start with a small metadata header like:

    ---
    source: NICE NG28
    title: Type 2 diabetes in adults
    year: 2022
    evidence_level: A
    url: https://www.nice.org.uk/guidance/ng28
    ---
    <the actual text...>

That header becomes searchable metadata + citation info. It's optional.
"""
import sys
import re

import config
import rag


def parse_front_matter(text: str):
    """Return (metadata_dict, body). Supports a simple --- key: value --- block."""
    meta = {}
    body = text
    m = re.match(r"^\s*---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if m:
        block, body = m.group(1), m.group(2)
        for line in block.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta, body


def main():
    if not config.HAS_KEY:
        print("ERROR: OPENAI_API_KEY not set. Copy .env.example to .env and "
              "paste your key, then run again.")
        sys.exit(1)

    files = sorted(list(config.DATA_DIR.glob("*.md")) + list(config.DATA_DIR.glob("*.txt")))
    if not files:
        print(f"No .md/.txt files found in {config.DATA_DIR}. Add some and retry.")
        sys.exit(1)

    # Fresh build: drop and recreate the collection so re-runs are clean.
    client = rag.chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    try:
        client.delete_collection(config.COLLECTION_NAME)
    except Exception:
        pass
    col = client.get_or_create_collection(
        name=config.COLLECTION_NAME,
        embedding_function=None,
        metadata={"hnsw:space": "cosine"},
    )

    ids, docs, metas = [], [], []
    for f in files:
        raw = f.read_text(encoding="utf-8", errors="ignore")
        meta, body = parse_front_matter(raw)
        meta.setdefault("source", f.stem)
        chunks = rag.chunk_text(body)
        print(f"  {f.name}: {len(chunks)} chunks")
        for i, ch in enumerate(chunks):
            ids.append(f"{f.stem}-{i}")
            docs.append(ch)
            metas.append(dict(meta))

    if not docs:
        print("No text chunks produced. Are the files empty?")
        sys.exit(1)

    print(f"Embedding {len(docs)} chunks with {config.EMBED_MODEL} ...")
    # Batch embeddings to stay well under request limits.
    embeddings = []
    B = 64
    for i in range(0, len(docs), B):
        embeddings.extend(rag.embed_texts(docs[i:i + B]))
        print(f"    embedded {min(i + B, len(docs))}/{len(docs)}")

    col.add(ids=ids, documents=docs, embeddings=embeddings, metadatas=metas)
    print(f"\nDone. Indexed {col.count()} chunks into {config.CHROMA_DIR}")


if __name__ == "__main__":
    main()
