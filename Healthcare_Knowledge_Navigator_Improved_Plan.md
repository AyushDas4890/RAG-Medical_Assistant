# 🏥 Healthcare Knowledge Navigator — Improved Project Plan

> **RAG system for clinical professionals. Evidence-based. Zero hallucination. Next-level UI.**

---

## 📋 Executive Summary

The **Healthcare Knowledge Navigator** is a specialized RAG assistant for healthcare professionals. It synthesizes evidence-based answers from verified clinical guidelines, research papers, and treatment protocols. This improved plan upgrades the original architecture with:

- ✅ Production-grade data pipeline
- ✅ Advanced hybrid retrieval with medical ontology expansion
- ✅ NLI-based confidence scoring
- ✅ **Fully redesigned UI/UX** — clinical-grade, dark mode, streaming, interactive citations
- ✅ HIPAA-compliant deployment

---

## 📊 What Changed from Original Plan

| Area | Original | Upgraded |
|---|---|---|
| UI description | "EMR aesthetic" — no detail | Full design system, dark mode, Framer Motion |
| Evidence panel | "Side panel with scores" | Color-coded, filterable, click-to-highlight |
| Confidence display | Numbers only | Visual meter + badge + NLI reasoning shown |
| Citations | `[1]` markers in text | Click → modal → highlighted source PDF viewer |
| Chat UX | Basic chat input | Streaming SSE, shortcuts, templates, export |
| Onboarding | None mentioned | Landing page + query templates + quick-starts |
| State management | Unstated | Zustand: session history, filter persistence |
| Streaming | Not mentioned | FastAPI SSE → React token-by-token streaming |

---

## Phase 1: Real Data Acquisition & Pipeline (Weeks 1–3)

*Foundation. No synthetic data. All sources authoritative.*

### Primary Data Sources

**Medical Literature:**
- **PubMed Central (PMC) Open Access Subset** — full-text biomedical articles via NCBI FTP or E-utilities API
- **arXiv (q-bio)** — latest computational biology preprints

**Clinical Guidelines & Protocols:**
- **NICE Guidelines** — UK-based, structured evidence-based recommendations
- **CDC Stacks** — public health guidelines, MMWR reports
- **WHO Guidelines** — global health and epidemic protocols

**Clinical Trials Data:**
- **ClinicalTrials.gov (API v2)** — trial results, interventions, phase status

### Data Ingestion Pipeline

1. **Scraping & API Integration** — automated crawlers (`BeautifulSoup`, `Scrapy`) + API polling scripts (`requests`, `Biopython`) fetching PDFs, XML, JSON on weekly CRON schedule

2. **Document Parsing & OCR** — `Unstructured.io` or `Nougat` (optimized for scientific text) to extract text from complex PDFs while preserving tables and medical equations

3. **Semantic Chunking** — LlamaIndex `SemanticSplitterNodeParser` (500–1000 tokens, 100-token overlap) to keep clinical paragraphs, trial summaries, and protocol steps intact

### Milvus Metadata Schema

```python
fields = [
    "doc_id",      # Unique document identifier
    "source",      # "NICE" | "PubMed" | "CDC" | "WHO" | "ClinicalTrials"
    "year",        # Publication year (for recency filtering)
    "doc_type",    # "RCT" | "Guideline" | "Systematic_Review" | "Preprint"
    "chunk_text",  # Extracted text chunk
    "embedding",   # BioLinkBERT/MedCPT vector (768-dim)
    "doi",         # DOI for citation linking
    "evidence_level"  # "A" | "B" | "C" | "Expert Opinion"
]
```

**Verify:** Query returns top-50 chunks with full metadata in < 2 seconds

---

## Phase 2: Domain-Specific Vectorization (Weeks 4–5)

*Standard embedding models fail on medical ontology. Use domain-specific models.*

### Embedding Strategy

- **Model:** Deploy **BioLinkBERT**, **PubMedBERT**, or **MedCPT** (Medical Contrastive Pre-training for Text) — pre-trained on medical literature, understand disease/drug/symptom relationships
- **Vector DB:** **Milvus** or **Qdrant** for scalable, precise vector search

### Metadata Filtering Examples

```python
# Doctors can filter by evidence quality and recency
filters = {
    "year": {"$gte": 2022},
    "source": {"$in": ["NICE", "WHO"]},
    "doc_type": {"$in": ["RCT", "Guideline"]}
}
```

**Verify:** Domain-specific embeddings outperform `text-embedding-ada-002` on MedQA benchmark

---

## Phase 3: Advanced RAG Pipeline (Weeks 6–8)

*Simple retrieve-and-generate is insufficient for medical queries.*

### Pipeline Components

**1. Query Expansion (Medical Ontology)**

Use **UMLS** or **MeSH** to expand queries automatically:

```
"heart attack" → "myocardial infarction" | "STEMI" | "NSTEMI" | "acute coronary syndrome"
"stomach ache" → "abdominal pain" | "epigastric pain" | "dyspepsia"
```

Tools: `quickumls` library or UMLS REST API

**2. Hybrid Search**

- **Dense (Vector) Search** — captures semantic meaning
- **Sparse (BM25) Search** — ensures exact matches for drug names (e.g., `Apixaban`) and gene mutations
- **Merge strategy:** Reciprocal Rank Fusion (RRF) to combine scores

**3. Re-Ranking**

Initial retrieval → top 50 chunks → **Cohere Rerank** or fine-tuned `bge-reranker` → top 5–10 clinically relevant chunks → LLM

**Verify:** RAGAS Faithfulness > 0.85, Context Precision > 0.80

---

## Phase 4: LLM Integration & Confidence Scoring (Weeks 9–11)

### LLM Selection

- **Proprietary:** Google **MedLM** / GPT-4o (complex reasoning, long context)
- **Open Source (HIPAA self-hosted):** **Llama-3 (70B)** fine-tuned for medical instruction, or **Meditron**

### Confidence Scoring Engine

**NLI Entailment (DeBERTa-v3):**

```python
# Pass LLM answer + retrieved context → NLI model
# "Entailment" → High Confidence (85-95%)
# "Neutral"    → Medium Confidence (40-60%)
# "Contradiction" → Low Confidence (10-30%) → FLAG for human review
```

**LLM Self-Reflection:**

```
Prompt: "On a scale of 0-100, rate how well your answer is supported 
by the provided context. Output only a number."
```

**Combined Score:** Weighted average of NLI score + self-reflection score + source evidence level

---

## Phase 5: Citation & Evidence Traceability (Weeks 12–13)

1. **Inline Citation Markers** — LLM appends `[1]`, `[2]` directly after claims
2. **Citation Mapping** — markers → chunk metadata (DOI, PMID, page number, paragraph)
3. **Interactive Highlighting** — clicking `[1]` opens source modal with exact paragraph highlighted

### Citation Prompt Template

```
System: You are a medical AI assistant. When making claims, always append 
citation markers [1], [2], etc. immediately after the claim. 
Never make claims without citation support from the provided context.
```

---

## Phase 6: 🎨 UI/UX Complete Redesign (Weeks 7–10)

*This is the major upgrade. From "basic chat" to "clinical-grade intelligence interface".*

### Design System

| Token | Value |
|---|---|
| Base background | `#0A1628` (Deep Navy) |
| Primary accent | `#00D4FF` (Electric Teal) |
| Surface | `#111B2E` |
| Warning | `#F59E0B` (Amber) |
| Danger/Low confidence | `#EF4444` |
| Success/High confidence | `#10B981` |
| Text primary | `#F1F5F9` |
| Text muted | `#94A3B8` |
| UI Font | `Inter` |
| Code/Citation Font | `JetBrains Mono` |

**Motion:** Framer Motion — subtle, purposeful. No distracting animations in clinical context.

---

### 6.1 — Landing / Onboarding Screen

```
┌─────────────────────────────────────────────────┐
│                                                 │
│   🏥  Healthcare Knowledge Navigator           │
│   Evidence-based answers. Zero hallucination.  │
│                                                 │
│   ┌───────────────────────────────────────┐    │
│   │  Ask a clinical question...       🔍  │    │
│   └───────────────────────────────────────┘    │
│                                                 │
│   Quick starts:                                 │
│   [💊 Drug Interactions]  [🧬 Dosing Guide]    │
│   [📋 Treatment Protocol] [⚠️ Contraindic.]    │
│                                                 │
│   Data sources: PubMed · NICE · CDC · WHO      │
│   Last index update: Jun 15, 2026              │
└─────────────────────────────────────────────────┘
```

---

### 6.2 — Main Chat Interface Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  🏥 MedNav AI          [🌙 Dark Mode]  [📋 History]  [⚙️ Cfg]  │
├───────────────┬─────────────────────────────┬───────────────────┤
│               │                             │                   │
│  HISTORY      │   CHAT AREA                 │  EVIDENCE         │
│  (collapsible)│                             │  PANEL            │
│               │   User: What's first-line   │                   │
│  • Session 1  │   treatment for T2DM        │  (see 6.3)        │
│  • Session 2  │   with CKD?                 │                   │
│  • Session 3  │                             │                   │
│               │   AI: [streaming...]        │                   │
│               │   Metformin remains         │                   │
│               │   first-line [1] unless     │                   │
│               │   GFR <30 [2]. SGLT2...    │                   │
│               │                             │                   │
│               │   ━━━━━━━━━━━━━━━━━━━━━━   │                   │
│               │   [Search medical lit.  🔍] │                   │
└───────────────┴─────────────────────────────┴───────────────────┘
```

**Chat features:**
- Token-by-token streaming via FastAPI SSE → React `ReadableStream`
- Animated typing indicator (pulsing dots) during retrieval
- Auto-scroll with sticky "↓ Jump to bottom" button when user scrolls up
- Markdown rendering via `react-markdown` + `remark-gfm` (tables, lists, bold)
- Code blocks with syntax highlighting for drug formulas/dosing calculations

---

### 6.3 — Evidence Panel (Side Panel — Major Upgrade)

```
┌─────────────────────────────────────┐
│  📚 EVIDENCE                        │
│  ─────────────────────────────────  │
│                                     │
│  CONFIDENCE                         │
│  ████████████░░░░░░  84%            │
│  🟢 HIGH — Supported by 3 RCTs     │
│                                     │
│  ─────────────────────────────────  │
│                                     │
│  [1] NICE Guidelines NG28 (2023)   │
│  🔵 Clinical Guideline             │
│  Evidence Level: A  |  Year: 2023  │
│                                     │
│  "Metformin is recommended as       │
│   first-line therapy to all adults  │
│   with T2DM and eGFR ≥30..."       │
│                                     │
│  [📄 View Source]  [📋 Copy Cite]  │
│                                     │
│  ─────────────────────────────────  │
│                                     │
│  [2] NEJM 2022 — EMPA-REG OUTCOME  │
│  🟢 Randomized Controlled Trial     │
│  Impact Factor: 91.2  |  Year: 2022│
│                                     │
│  "In patients with CKD stage 3,     │
│   empagliflozin reduced..."         │
│                                     │
│  [📄 View Source]  [📋 Copy Cite]  │
│                                     │
│  ─────────────────────────────────  │
│  FILTERS                            │
│  📅 Year: [2019] ──────────── [Now]│
│  📋 ☑ RCT  ☑ Guideline  ☐ Preprint│
│  🏥 ☑ NICE  ☑ CDC  ☑ WHO  ☐ arXiv │
└─────────────────────────────────────┘
```

**Evidence type color coding:**
- 🔵 Clinical Guidelines (highest trust)
- 🟢 RCTs / Systematic Reviews
- 🟡 Observational Studies / Reviews
- 🔴 Case Reports / Expert Opinion

**Confidence badge logic:**
- `85–100%` → 🟢 HIGH
- `60–84%`  → 🟡 MEDIUM
- `30–59%`  → 🟠 LOW — REVIEW RECOMMENDED
- `< 30%`   → 🔴 INSUFFICIENT EVIDENCE — DO NOT USE CLINICALLY

---

### 6.4 — Source Highlight Modal

Click `[1]` → modal opens with full source context:

```
┌──────────────────────────────────────────────────────┐
│  📄 NICE Guidelines NG28 (2023)                       │
│  Section 1.2: Pharmacological Management             │
│  ──────────────────────────────────────────────────  │
│                                                      │
│  "Adults with type 2 diabetes should be offered      │
│   metformin as first-line pharmacological            │
│   therapy. ████████████████████████████████████     │  ← highlighted
│   Continue if eGFR remains ≥30 mL/min/1.73m².       │
│   [Grade A Recommendation — Adapted from UKPDS]"    │
│                                                      │
│  ──────────────────────────────────────────────────  │
│  DOI: 10.xxxx/nice.ng28   |   PMID: 12345678        │
│  [📖 Open Full PDF]  [📋 Copy APA]  [📋 Copy AMA]  │
└──────────────────────────────────────────────────────┘
```

---

### 6.5 — Power Features

| Feature | Implementation | Priority |
|---|---|---|
| **Keyboard shortcuts** | `Cmd+K` = new query, `Cmd+/` = toggle evidence panel, `Cmd+E` = export | High |
| **PDF export** | Download conversation + citations as formatted PDF | High |
| **Query templates** | "Drug interaction check", "Dosing by weight", "Contraindications for..." | High |
| **Differential diagnosis mode** | Structured output with probability ranking per diagnosis | Medium |
| **Dark / Light mode** | CSS variables toggle + `localStorage` persistence | High |
| **Session history** | Left sidebar: saved conversations, searchable | Medium |
| **Copy citation** | APA / AMA / Vancouver format copy buttons per source | High |
| **Filter persistence** | Filters saved per session via Zustand | Medium |

---

## Phase 7: Frontend Implementation (Weeks 10–12)

### Tech Stack

```
Framework:    Next.js 14 (App Router)
Styling:      Tailwind CSS + shadcn/ui
Animation:    Framer Motion
Markdown:     react-markdown + remark-gfm
PDF viewer:   react-pdf
State:        Zustand
Icons:        Lucide React
Streaming:    Native ReadableStream (FastAPI SSE)
```

### Component Architecture

```
src/
├── app/
│   ├── page.tsx                  # Landing / onboarding
│   └── chat/
│       └── page.tsx              # Main interface
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx           # History panel (collapsible)
│   │   └── EvidencePanel.tsx     # Right panel
│   ├── chat/
│   │   ├── ChatInterface.tsx     # Streaming chat area
│   │   ├── MessageBubble.tsx     # Individual message + citation markers
│   │   ├── TypingIndicator.tsx   # Pulsing dots during retrieval
│   │   └── QueryInput.tsx        # Input + query templates
│   ├── evidence/
│   │   ├── ConfidenceMeter.tsx   # Gradient bar + badge
│   │   ├── SourceCard.tsx        # Individual source card
│   │   ├── CitationModal.tsx     # Click [1] → highlighted source
│   │   └── FilterBar.tsx         # Year / type / source toggles
│   └── ui/
│       └── (shadcn components)
├── lib/
│   ├── api.ts                    # FastAPI SSE client
│   ├── store.ts                  # Zustand state management
│   └── citations.ts              # Citation format converters (APA/AMA)
└── styles/
    └── globals.css               # CSS variables, dark/light themes
```

### Streaming Implementation

```typescript
// FastAPI SSE → React token-by-token streaming
async function streamQuery(query: string) {
  const response = await fetch('/api/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, filters: activeFilters })
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader!.read();
    if (done) break;
    const chunk = decoder.decode(value);
    // Append chunk to message state → React re-renders token by token
    setCurrentMessage(prev => prev + chunk);
  }
}
```

---

## Phase 8: Backend & Infrastructure (Weeks 12–14)

### API Layer (FastAPI)

```python
# FastAPI with SSE streaming
@app.post("/api/query")
async def query_medical(request: QueryRequest):
    async def generate():
        # 1. UMLS query expansion
        # 2. Hybrid search (dense + BM25)
        # 3. Cohere rerank → top 5-10 chunks
        # 4. NLI confidence scoring
        # 5. Stream LLM response token by token
        async for token in llm.astream(prompt):
            yield f"data: {token}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

### Deployment Architecture

```
User Browser
    │
    ▼
Vercel (Next.js)
    │
    ▼
FastAPI on AWS ECS Fargate (or GCP Cloud Run)
    ├── Milvus (Zilliz Cloud managed)
    ├── Cohere API (reranking)
    └── LLM API (MedLM / GPT-4o / self-hosted Llama-3)

Compliance:
    ├── AWS HealthLake OR GCP Healthcare API
    ├── Encryption at rest (AES-256) + in transit (TLS 1.3)
    └── Zero data retention — no query logging, ephemeral sessions only
```

---

## Phase 9: Evaluation & Clinical Validation (Weeks 15–16)

### RAGAS Automated Evaluation

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision

# Run on 100 gold-standard Q&A pairs validated by medical professionals
results = evaluate(
    dataset=medical_qa_dataset,
    metrics=[faithfulness, answer_relevancy, context_precision]
)

# Target thresholds
assert results["faithfulness"] > 0.85
assert results["context_precision"] > 0.80
assert results["answer_relevancy"] > 0.75
```

### Human-in-the-Loop (HITL) Panel

Panel of 3–5 healthcare professionals grading on:

| Criterion | Scale |
|---|---|
| Clinical accuracy | 1–5 |
| Evidence quality shown | 1–5 |
| Usability / UX | 1–5 |
| Would use in practice? | Yes / No |
| Concern about hallucination? | Yes / No |

Feedback loop → prompt engineering iteration → re-evaluate

---

## Delivery Timeline

| Week | Milestone |
|---|---|
| 1–3 | Data pipeline live (PubMed, NICE, CDC, WHO) |
| 4–5 | BioLinkBERT embeddings + Milvus indexed |
| 6–8 | Hybrid search + rerank + UMLS expansion working |
| 7–10 | **UI/UX redesign** (parallel track) |
| 9–11 | NLI confidence scoring + citation mapping |
| 10–12 | Frontend components built + streaming integrated |
| 12–14 | FastAPI backend + SSE streaming deployed |
| 14–15 | RAGAS evaluation pass |
| 15–16 | HITL clinical panel beta test |
| 16 | **v1.0 launch** |

---

## Tech Stack Summary

| Layer | Technology |
|---|---|
| **Embedding** | BioLinkBERT / PubMedBERT / MedCPT |
| **Vector DB** | Milvus (Zilliz Cloud) or Qdrant |
| **Sparse search** | BM25 via `rank_bm25` or Milvus sparse |
| **Query expansion** | UMLS REST API / `quickumls` |
| **Reranking** | Cohere Rerank / `bge-reranker` |
| **Confidence** | DeBERTa-v3 NLI |
| **LLM** | MedLM / GPT-4o / Llama-3 (70B) |
| **Backend** | FastAPI + SSE streaming |
| **Frontend** | Next.js 14 + Tailwind + shadcn/ui |
| **Animation** | Framer Motion |
| **State** | Zustand |
| **Evaluation** | RAGAS |
| **Deployment** | AWS ECS + Vercel + Zilliz Cloud |
| **Compliance** | AWS HealthLake / GCP Healthcare API |

---

*Document generated for architecture, planning, and portfolio purposes.*  
*Last updated: June 2026*
