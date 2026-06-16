<!-- ╔══════════════════════════════════════════════════════════════╗ -->
<!--                        BANNER                                    -->
<!-- ╚══════════════════════════════════════════════════════════════╝ -->

<p align="center">
  <img src="./assets/banner.svg" alt="Healthcare Knowledge Navigator" width="100%" />
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=22&pause=1000&color=00D4FF&center=true&vCenter=true&width=820&lines=Evidence-based+answers.+Zero+hallucination.;Retrieval-Augmented+Generation+for+clinicians.;Every+claim+cited.+Every+source+ranked.;Built+MVP-first+%E2%80%94+reliable%2C+not+over-engineered." alt="typing" />
</p>

<!-- ╔══════════════════════════════════════════════════════════════╗ -->
<!--                        BADGES                                    -->
<!-- ╚══════════════════════════════════════════════════════════════╝ -->

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenAI-gpt--4o--mini-412991?style=for-the-badge&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/ChromaDB-Vector_Store-FF6B6B?style=for-the-badge&logo=databricks&logoColor=white" />
  <img src="https://img.shields.io/badge/Deploy-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-MVP_Live-10B981?style=flat-square" />
  <img src="https://img.shields.io/badge/RAG-Citation_Grounded-00D4FF?style=flat-square" />
  <img src="https://img.shields.io/badge/UI-Motion_Design-7C3AED?style=flat-square" />
  <img src="https://img.shields.io/badge/PRs-welcome-F59E0B?style=flat-square" />
</p>

<!-- ╔══════════════════════════════════════════════════════════════╗ -->
<!--                     LIVE DEMO BUTTON                             -->
<!--  👉 After deploying on Vercel, replace YOUR_VERCEL_URL below.    -->
<!-- ╚══════════════════════════════════════════════════════════════╝ -->

<p align="center">
  <a href="https://rag-medical-assistant-five.vercel.app">
    <img src="https://img.shields.io/badge/🚀_LIVE_DEMO-Open_the_App-00D4FF?style=for-the-badge&labelColor=0A1628" height="42" />
  </a>
  &nbsp;
  <a href="#-quick-start">
    <img src="https://img.shields.io/badge/⚡_Run_Locally-5_min_setup-111B2E?style=for-the-badge" height="42" />
  </a>
</p>

<p align="center"><sub>🔗 <b>Live demo link:</b> <code>https://rag-medical-assistant-five.vercel.app</code></sub></p>

<p align="center">
  <a href="#-why-this-exists">Why</a> ·
  <a href="#-features">Features</a> ·
  <a href="#-how-it-works">How it works</a> ·
  <a href="#-quick-start">Quick start</a> ·
  <a href="#-deploy-to-vercel">Deploy</a> ·
  <a href="#-roadmap">Roadmap</a>
</p>

---

## 💡 Why this exists

Plain chatbots **hallucinate** — they invent drug doses and fake citations from memory. That's a dealbreaker in medicine.

**Healthcare Knowledge Navigator** answers *only* from a verified corpus of clinical guidelines. Every claim carries a `[1]` citation you can click and inspect, every source is ranked, and a confidence meter flags weak evidence. If it doesn't know, it **says so** instead of guessing.

> It's not a know-everything bot — it's a **trustworthy librarian**. 📚

<br/>

<table>
<tr>
<td width="50%" valign="top">

### 🧠 The problem
- LLMs answer from memory → invented facts & citations
- No way to trace *where* an answer came from
- "Confidence" is invisible
- Classic setups die with a vague **`unable to fetch`**

</td>
<td width="50%" valign="top">

### ✅ This build
- Answers grounded in retrieved guideline text only
- Clickable `[n]` citations → exact source snippet
- Live confidence meter + evidence levels
- **Same-origin architecture → `unable to fetch` can't happen**

</td>
</tr>
</table>

---

## ✨ Features

| | Feature | Detail |
|---|---|---|
| 🎯 | **Citation-grounded RAG** | Answers cite `[1] [2]` mapped to real source chunks |
| 📊 | **Confidence signal** | Color-coded meter: 🟢 HIGH · 🟡 MEDIUM · 🔴 INSUFFICIENT |
| 🔍 | **Ranked evidence panel** | Match %, evidence level, year, click-to-expand source |
| 🧭 | **Auto topic discovery** | Site reads its own index → shows *exactly* what it can answer |
| 🛡️ | **Zero-hallucination prompt** | Refuses to answer outside the provided sources |
| 🎨 | **Motion-design UI** | Custom magnetic cursor, 3D tilt, parallax mesh, scroll reveals |
| ⚡ | **One-server design** | FastAPI serves the page *and* the API → no CORS, no fetch errors |
| ♿ | **Accessible** | Full `prefers-reduced-motion` fallback |

---

## 🏗️ How it works

```mermaid
flowchart LR
    A([🧑‍⚕️ Question]) --> B[FastAPI<br/>same origin]
    B --> C[OpenAI<br/>embeddings]
    C --> D[(ChromaDB<br/>vector store)]
    D --> E[Top-k chunks<br/>+ scores]
    E --> F[Grounded prompt<br/>+ citations]
    F --> G[gpt-4o-mini]
    G --> H([💬 Answer + 1 2 3<br/>+ confidence])
    style A fill:#00D4FF,stroke:#0A1628,color:#021018
    style H fill:#10B981,stroke:#0A1628,color:#021018
    style D fill:#7C3AED,stroke:#0A1628,color:#fff
    style B fill:#111B2E,stroke:#00D4FF,color:#fff
    style G fill:#111B2E,stroke:#00D4FF,color:#fff
```

**The reliability trick:** the browser loads the page *from FastAPI itself* and calls the API with **relative paths** (`/api/chat`). Same origin → CORS can never block it. Every backend error is caught and returned as readable JSON the UI displays — so you always see the real reason, never a blank `unable to fetch`.

---

## 🧰 Tech stack

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Uvicorn-2C2C2C?style=flat-square" />
  <img src="https://img.shields.io/badge/ChromaDB-FF6B6B?style=flat-square" />
  <img src="https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white" />
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black" />
  <img src="https://img.shields.io/badge/Vercel-000000?style=flat-square&logo=vercel&logoColor=white" />
</p>

| Layer | Choice | Why |
|---|---|---|
| **Embeddings** | `text-embedding-3-small` | Lightweight, no local `torch`/GPU |
| **Vector DB** | ChromaDB (local file) | Zero infra — no Docker, no server |
| **LLM** | `gpt-4o-mini` | Cheap, fast, reliable formatting |
| **Backend** | FastAPI + Uvicorn | Async, serves UI + API together |
| **Frontend** | Vanilla HTML/CSS/JS | No build step, premium motion design |

---

## ⚡ Quick start

> **Prereq:** Python 3.10+ and an [OpenAI API key](https://platform.openai.com/api-keys).

```bash
# 1 — clone
git clone https://github.com/AYuSh/healthcare-knowledge-navigator.git
cd healthcare-knowledge-navigator/backend

# 2 — environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt

# 3 — add your key
copy .env.example .env        # macOS/Linux: cp .env.example .env
#   → open .env and paste your key (starts with sk-)

# 4 — build the knowledge base
python ingest.py

# 5 — run  →  http://127.0.0.1:8000
uvicorn main:app --reload
```

<details>
<summary><b>🩺 The status dot tells you everything (click to expand)</b></summary>

<br/>

| Dot | Meaning | Fix |
|---|---|---|
| 🟢 green | online, data indexed | — |
| 🟠 amber | server up, **no data** | run `python ingest.py` |
| 🔴 red — *no key* | key missing/invalid | paste key into `backend/.env`, restart |
| 🔴 red — *offline* | server not running | start `uvicorn main:app --reload` |

If a query fails, the chat shows the **real reason** (quota, bad model name, etc.) — never a generic error.

</details>

<details>
<summary><b>📁 Project structure (click to expand)</b></summary>

```
healthcare-knowledge-navigator/
├── assets/
│   └── banner.svg            # this README's banner
├── backend/
│   ├── main.py               # FastAPI: serves UI + /api/health, /api/topics, /api/chat
│   ├── rag.py                # chunk → embed → Chroma retrieve → answer
│   ├── ingest.py             # build the vector store from data/
│   ├── config.py             # reads .env (never crashes if key is missing)
│   ├── data/*.md             # sourced clinical guideline snippets
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html            # motion-design single page
│   ├── style.css             # design system + animations
│   └── app.js                # chat, evidence panel, cursor, tilt, reveals
└── WORKING_PLAN_v2.md         # the lean, reviewed plan
```

</details>

<details>
<summary><b>🧠 Add your own topics (click to expand)</b></summary>

<br/>

The assistant only knows what you feed it. To teach it a new topic, drop a Markdown file in `backend/data/` with a small header:

```markdown
---
source: NICE NG28
title: Type 2 diabetes in adults — management
year: 2022
evidence_level: A
url: https://www.nice.org.uk/guidance/ng28
---

Your guideline text here...
```

Then re-index — the website's **"Specialised in"** list updates itself automatically:

```bash
python ingest.py
```

</details>

---

## 🚀 Deploy to Vercel

This repo is Vercel-ready (includes the `pysqlite3-binary` patch ChromaDB needs on serverless).

1. Push to GitHub.
2. Import the repo on [vercel.com](https://vercel.com/new).
3. Add an environment variable: `OPENAI_API_KEY`.
4. Deploy → copy your URL.
5. **Paste that URL into this README** (the Live Demo button + the link line near the top).

> ℹ️ Note: serverless filesystems are read-only, so build the Chroma index at deploy time or ship a prebuilt `chroma_store/` — see `WORKING_PLAN_v2.md` for the production data path.

---

## 🗺️ Roadmap

- [x] MVP: grounded RAG + citations + confidence
- [x] Motion-design UI (cursor, tilt, parallax, reveals)
- [x] Auto topic discovery from the index
- [ ] Token-by-token streaming (SSE)
- [ ] Hybrid search (BM25 + dense) + reranking
- [ ] UMLS / MeSH query expansion
- [ ] NLI-based confidence (DeBERTa)
- [ ] RAGAS evaluation harness

---

## ⚠️ Disclaimer

The bundled `data/` snippets are short, illustrative summaries for demonstrating the pipeline. **This is a software demo, not a clinical tool** — do not use it for real patient decisions. Replace `data/` with your own verified corpus before any serious use.

---

<p align="center">
  <sub>Built with ☕ and a lot of <code>print()</code> by <b>AYuSh</b> · Thāne, Maharashtra 🇮🇳</sub><br/>
  <sub>⭐ Star this repo if the citation-grounded approach helped you.</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Made_with-FastAPI_+_OpenAI-00D4FF?style=flat-square" />
  <img src="https://img.shields.io/badge/License-MIT-94A3B8?style=flat-square" />
</p>
