# Customer Support Triage & Resolution Router

An AI-powered system that reads incoming customer-support tickets and automatically
**classifies**, **prioritizes**, **summarizes**, and **routes** them to the right team —
built with LangChain on top of Groq-hosted LLMs.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![LangChain](https://img.shields.io/badge/LangChain-LCEL-green)
![LLM](https://img.shields.io/badge/LLM-Groq%20(Llama%203.3)-orange)
![Status](https://img.shields.io/badge/status-in%20development-yellow)

---

## Why this exists

Support teams waste hours manually tagging, prioritizing, and routing tickets.
This system automates that triage layer so human agents spend time *resolving*
issues, not sorting them — the same pattern used by Zendesk AI, Intercom Fin, and
Salesforce Einstein.

---

## Features

| Capability | Status |
|---|---|
| Classify ticket category (Billing / Technical / Account / Feature Request / Complaint) | ✅ |
| Detect priority / urgency (Low → Critical) | ✅ |
| One-sentence issue summary | ✅ |
| Validated, typed output (Pydantic schema, not fragile strings) | ✅ |
| Deterministic routing to team + SLA assignment | ✅ |
| Auto-escalation of Critical tickets | ✅ |
| Single LCEL pipeline (`prompt | model | route`) | ✅ |
| Concurrent processing via `.batch()` | ✅ |
| Few-shot prompting for edge-case accuracy | ✅ |
| Embeddings + semantic similarity (sentence-transformers) | ✅ |
| Vector store of past tickets (ChromaDB, persistent) | ✅ |
| Ticket history & persistence (SQLite + SQLAlchemy) | ✅ |
| RAG-augmented triage (retrieve precedent → ground the decision) | ✅ |
| Dual-store sync (SQLite system-of-record + Chroma semantic index) | ✅ |
| LangGraph stateful workflow (nodes + edges + state) | ✅ |
| Escalation detector + conditional branch (senior queue, tighter SLA) | ✅ |
| Response-drafting agent (RAG + generative, with human-review skip) | ✅ |
| FastAPI service: POST /tickets, GET /tickets, GET /tickets/{id} | ✅ |
| Analytics endpoint (SQL GROUP BY: by priority/category/status/team) | ✅ |
| Routers + dependency injection + input guardrails + auto OpenAPI docs | ✅ |
| Observability: structured JSON logs, request middleware, LangSmith-ready | ✅ |
| Per-ticket cost + latency capture (token accounting across the graph) | ✅ |
| Evaluation harness: golden set, accuracy, per-class P/R/F1, confusion matrix | ✅ |
| Dockerized: one-command `docker compose up`, persistent volume, healthcheck | ✅ |
| E-commerce storefront (React + Vite + Tailwind) with "Raise a query" | ✅ |
| Email the customer: query-registered confirmation + AI reply (Gmail SMTP) | ✅ |

---

## Architecture (current)

```
                         new ticket text
                              │
                              ▼
              ┌──────────────────────────────────┐
              │ RETRIEVE similar past tickets      │◀── ChromaDB (vector index)
              │ (semantic search, top-k)           │
              └──────────────┬─────────────────────┘
                             ▼  precedent as context
   ChatPromptTemplate ──▶ ChatGroq.with_structured_output(TicketTriage)
                             │   (RAG: classify + prioritize + summarize)
                             ▼
                       TicketTriage ──▶ route() ──▶ RoutedTicket
                             (pure Python: team + SLA, no LLM)
                                          │
                          ┌───────────────┴───────────────┐
                          ▼                               ▼
                  SQLite (full record)            ChromaDB (re-indexed
                  = system of record               as precedent for
                                                   future tickets)
```

`app/service.py::process_ticket()` orchestrates the whole flow.

---

## Tech stack

- **Python 3.13**
- **LangChain** (LCEL) + **langchain-groq**
- **Groq** (Llama 3.3 70B) — fast, free-tier LLM inference
- **Pydantic v2** — typed schemas & validation
- **sentence-transformers** (`all-MiniLM-L6-v2`) — local embeddings
- **ChromaDB** — persistent vector store
- **SQLAlchemy 2.0 + SQLite** — relational system of record
- **FastAPI** + **Uvicorn** — HTTP service
- **React** + **Vite** + **Tailwind CSS** — e-commerce storefront client
- **smtplib** (Gmail SMTP) — customer email notifications
- **Docker** + **docker-compose** — containerized, one-command deploy

---

## Project structure

```
app/
├── config.py        # env loading + key check (once)
├── llm.py           # model factory — the only place that builds the LLM client
├── schemas.py       # Pydantic contracts: Category, Priority, TicketTriage, RoutedTicket
├── triage.py        # triage_chain: prompt | structured model (few-shot)
├── routing.py       # deterministic team + SLA rules (no LLM)
├── pipeline.py      # full chain: triage | route
├── embeddings.py    # embedding model factory (sentence-transformers)
├── vector_store.py  # ChromaDB persistent store + retriever
├── rag.py           # RAG-augmented triage chain (retrieve → augment → generate)
├── escalation.py    # cheap LLM detector for senior-human escalation signals
├── draft.py         # response-drafting chain (RAG + generative, temp=0.3)
├── graph.py         # LangGraph workflow: triage → escalation → [branch] → persist → [skip|draft]
├── service.py       # process_ticket(): pre-LangGraph orchestrator (now superseded by graph.py)
├── db/
│   ├── models.py        # SQLAlchemy ORM: Ticket
│   ├── session.py       # engine + SessionLocal + init_db
│   └── repository.py    # TicketRepository — the only SQL-speaking code (+ analytics)
├── api/
│   ├── main.py          # FastAPI app (thin): lifespan + middleware + include_router
│   ├── schemas.py       # API DTOs: TicketRequest/Response, TicketRecord, AnalyticsResponse
│   ├── dependencies.py  # get_ticket_repository (dependency injection)
│   └── routers/
│       ├── health.py    # GET /health
│       ├── tickets.py   # POST /tickets, GET /tickets, GET /tickets/{id}
│       └── analytics.py # GET /analytics
├── observability/
│   ├── logger.py        # structured JSON logging
│   ├── tracing.py       # LangSmith tracing status
│   └── runner.py        # run_triage(): graph + latency + token-cost logging
└── eval/
    └── harness.py       # golden-set load + accuracy / P-R-F1 / confusion matrix
data/eval/golden_set.jsonl  # 18 human-labeled tickets (ground truth)
scripts/run_eval.py         # CLI: prints the triage scorecard
Dockerfile                  # CPU-torch, layer-cached deps, baked model, non-root
docker-compose.yml          # one-command run + persistent volume + healthcheck
.dockerignore               # keeps .venv/secrets/local DBs out of the image
store/                      # e-commerce storefront (React + Vite + Tailwind)
├── src/App.jsx             # the store + "Raise a query" modal (calls /api/tickets)
└── vite.config.js          # dev server + /api proxy to the backend (no CORS in dev)
app/notifications/email.py  # customer email (smtplib; dry-run without SMTP creds)
experiments/         # learning scripts (Modules 1–9)
run_triage.py        # demo: triage only
run_pipeline.py      # demo: triage + routing (batched)
```

---

## Setup

```powershell
# 1. Create & activate a virtual environment (Python 3.13)
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 3. Add your Groq API key
Copy-Item .env.example .env
notepad .env          # paste your key from https://console.groq.com/keys
```

## Usage

### CLI demo

```powershell
python run_pipeline.py
```

```
[High    ] Billing         -> Billing Team                 (SLA 4h)
[Critical] Technical       -> Technical Support (Escalation) (SLA 1h)
...
```

### Run the API

```powershell
$env:PYTHONPATH="."
python -m uvicorn app.api.main:app
# interactive Swagger UI at http://127.0.0.1:8000/docs
```

| Method | Path | Description |
|---|---|---|
| `POST` | `/tickets` | Triage, route, escalate, draft a reply |
| `GET` | `/tickets` | List tickets (paginated: `?limit=&offset=`) |
| `GET` | `/tickets/{id}` | Fetch one ticket (404 if missing) |
| `GET` | `/analytics` | Aggregate counts by priority/category/status/team |
| `GET` | `/health` | Liveness probe |

```bash
curl -X POST http://127.0.0.1:8000/tickets \
  -H "Content-Type: application/json" \
  -d '{"text": "I was double-charged and want a refund."}'
```

### Run with Docker (one command)

```bash
docker compose up --build        # builds image + starts the API
# API at http://localhost:8001  (host port 8001 -> container 8000)
docker compose down              # stop (keeps data in the named volume)
docker compose down -v           # stop and wipe the volume
```

The image bakes in the embedding model (works offline); the Groq key is injected
at runtime from `.env` (never baked in); tickets + vectors persist in a named volume.

### Run the storefront (React + Vite + Tailwind)

```powershell
cd store
npm install
npm run dev        # opens http://localhost:5173
```

A demo e-commerce site with a "Raise a query" form. The Vite dev server proxies
`/api/*` to the backend (set `VITE_API_TARGET`, default `http://localhost:8001`),
so submitting a query triages it live, shows the result, and emails the customer.

> On Windows, if the project folder contains spaces or `&`, `npm run dev` can
> break — run `node node_modules/vite/bin/vite.js` instead, or use a hyphenated
> folder name (as a cloned GitHub repo would have).

### Email notifications

Set Gmail SMTP in `.env` (see `.env.example` for app-password steps). With no
`SMTP_PASSWORD`, the app runs in dry-run (composes + logs the email, never sends).

### Evaluation

```powershell
$env:PYTHONPATH="."; python scripts\run_eval.py
```

Triage is measured against a human-labeled golden set (`data/eval/golden_set.jsonl`):

```
== ACCURACY ==
  Category            :  94.4%
  Priority (exact)    :  66.7%
  Priority (within 1) : 100.0%   (priority is ordinal + subjective)
```

Reports per-category precision/recall/F1 and a confusion matrix so prompt/model
changes can be evaluated as a measurable regression test, not a guess.

---

## Roadmap

- [x] **Phase 1** — Classifier, summarizer, priority detector (structured output)
- [x] **Phase 2** — Routing engine, LCEL pipeline, batching, few-shot prompting
- [x] **Phase 3** — Embeddings, ChromaDB vector store, SQLite persistence, RAG-augmented triage
- [x] **Phase 4** — LangGraph workflow, escalation branching, response-drafting agent *(analytics next)*
- [x] **Phase 5** — FastAPI service, analytics, observability, evaluation, Docker
- [ ] **Phase 6** — Docs, system-design write-up, polish

---

*Built as a hands-on study of production LLM application engineering.*
