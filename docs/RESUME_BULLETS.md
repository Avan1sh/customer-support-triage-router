# Résumé bullets — Customer Support Triage & Resolution Router

Copy-paste these into the **Projects** section of your résumé. Pick 3–4; lead
with the metric-bearing ones. Tailor the wording to each job description.

---

## Project header line

**Customer Support Triage & Resolution Router** — *Python, LangChain, LangGraph,
FastAPI, ChromaDB, Docker, React* · [GitHub](https://github.com/Avan1sh/customer-support-triage-router)

## Bullets (strongest first)

- Built an end-to-end **AI support-triage system** (LangChain + LangGraph on
  Groq/Llama-3.3) that classifies, prioritizes, summarizes, routes, escalates,
  and drafts replies for customer tickets — **94% category accuracy** on a
  hand-labeled evaluation set with per-class precision/recall tracking.
- Designed a **RAG pipeline** over historical tickets (ChromaDB +
  sentence-transformer embeddings) for precedent-grounded triage, using a
  **dual-store architecture** (SQLite system-of-record + vector index) kept
  consistent through a single write path.
- Implemented a **multi-agent LangGraph workflow** with conditional escalation
  and a human-in-the-loop reply-drafting agent; enforced reliability with
  Pydantic structured outputs and prompt-level guardrails against unsafe
  promises.
- Added **production observability** — structured JSON logging with per-request
  token-cost and latency capture — and a **regression-grade evaluation harness**
  (golden set, accuracy, confusion matrix) to make prompt changes measurable.
- **Containerized** the service with Docker (layer-cached build, non-root user,
  healthcheck) and shipped a **React + Vite + Tailwind** storefront plus
  automated **SMTP email notifications**, delivering a full customer → resolution demo.

## One-line version (for a dense résumé)

> Built an AI customer-support triage system (LangChain/LangGraph, FastAPI,
> RAG over ChromaDB, Docker, React) — 94% classification accuracy, multi-agent
> escalation + reply drafting, full observability and evaluation.

## Skills this project demonstrates (for your Skills section)

LLM application engineering · LangChain (LCEL) · LangGraph · RAG · vector
databases · prompt engineering · structured outputs / function calling ·
FastAPI · SQLAlchemy · evaluation & metrics · observability · Docker · React
