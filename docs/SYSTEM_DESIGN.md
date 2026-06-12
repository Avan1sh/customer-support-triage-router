# System Design — Customer Support Triage & Resolution Router

A walkthrough of the architecture, the decisions behind it, and how it would
scale. Written to be the document you talk through in a system-design interview.

---

## 1. Problem

Support teams spend hours manually tagging, prioritizing, and routing tickets
before anyone starts *solving* them. The goal: automate that triage layer so
humans spend time resolving issues, not sorting them — while keeping a human in
the loop for anything sensitive.

**Functional requirements**
- Ingest a ticket (free text) and return: category, priority, summary, owning
  team, SLA, escalation decision, and (when appropriate) a draft reply.
- Persist every ticket; expose history and analytics.
- Notify the customer by email.

**Non-functional requirements**
- Reliable structured output (no brittle string parsing).
- Observable (cost, latency, failures) and evaluable (measurable accuracy).
- Deployable as a container; horizontally scalable later.

---

## 2. High-level architecture

```
 Customer (storefront)                       Support team
        │                                         ▲
        ▼  POST /tickets                          │ history / analytics
 ┌─────────────────────────────────────────────────────────────┐
 │ FastAPI service                                              │
 │  • validation (Pydantic) + input guardrails                 │
 │  • request logging middleware                               │
 │  • routers: tickets / analytics / health                    │
 └───────────────┬─────────────────────────────┬───────────────┘
                 │ run_triage()                 │ repository
                 ▼                              ▼
 ┌─────────────────────────────────┐   ┌──────────────────────┐
 │ LangGraph workflow              │   │ SQLite (system of     │
 │  triage(RAG) → escalation →     │   │ record) — tickets,    │
 │  [branch] → persist →           │   │ status, timestamps    │
 │  [skip | draft]                 │   └──────────────────────┘
 └───────┬─────────────────────────┘   ┌──────────────────────┐
         │ retrieve precedent          │ ChromaDB (vector      │
         └────────────────────────────▶│ index) — semantic     │
                 ▲ index new ticket     │ similarity search     │
                 └──────────────────────┴──────────────────────┘
                 │ background task
                 ▼
            Email (SMTP)
```

The LLM is **one component** inside a mostly-deterministic system. Routing,
SLA assignment, and persistence are plain code; the LLM is used only where
judgment is genuinely required (classification, summarization, escalation
signals, drafting).

---

## 3. Key design decisions & trade-offs

**Structured output over text parsing.** Every LLM call that drives control flow
uses Pydantic schemas via tool-calling (`with_structured_output`). This makes
category/priority *typed and validated* — invalid output errors loudly instead
of silently misrouting. Trade-off: requires a tool-calling-capable model.

**Dual store (SQLite + ChromaDB).** Relational DB answers exact/structured
queries ("all open Critical billing tickets", analytics); the vector store
answers semantic ones ("similar past tickets"). They serve different query
shapes, so we run both and keep them in sync via one write path
(`service` / `persist` node). Trade-off: two stores to keep consistent.

**Chains where possible, agents where necessary.** Phases 1–3 are deterministic
chains (LCEL). Only Phase 4 introduces LangGraph, and even then branching is
driven by cheap pure functions reading state — the LLM's judgment is captured
in a *node* that writes to state, not in the routing logic. This keeps the
system debuggable and cheap versus an open-ended ReAct loop.

**Deterministic routing, not LLM routing.** Once category + priority are known,
mapping to a team + SLA is a lookup table — faster, cheaper, auditable. Knowing
*not* to use the LLM here is deliberate.

**Human-in-the-loop for replies.** Drafts are suggestions for a human to review;
escalated tickets get no AI reply at all. Prevents the LLM from making
unauthorized promises (refunds, commitments).

**Email as a background task.** SMTP runs in a FastAPI `BackgroundTask` so a slow
or failing mail server never blocks (or breaks) the customer's request.

---

## 4. Reliability, cost, and observability

- **Cost/latency capture:** each request logs total tokens (summed across all
  LLM calls in the graph) and wall-clock latency. This makes cost per ticket
  and p95 latency measurable — and surfaced an architectural win (escalated
  tickets skip drafting → fewer tokens).
- **Failure handling:** the workflow runner logs the full traceback on error and
  re-raises; the API translates it into a clean `502` without leaking internals.
- **Evaluation:** a labeled golden set + harness reports accuracy, per-class
  precision/recall/F1, and a confusion matrix — so prompt/model changes are a
  measured regression test, not a guess.
- **Tracing:** LangSmith auto-traces every LLM/graph call when enabled.

---

## 5. Scaling to ~10,000 tickets/min

The current single-node design (SQLite + local Chroma + in-process model) is
right for a demo. To scale:

1. **Stateless API + horizontal scale.** Run many API replicas behind a load
   balancer. This requires moving state out of the process:
   - **SQLite → Postgres** (one URL change via SQLAlchemy; add indexes on
     `status`, `category`, `created_at`; connection pooling).
   - **Local Chroma → managed vector DB** (pgvector / Pinecone / Qdrant) shared
     across replicas.
2. **Decouple with a queue.** Accept tickets to a queue (SQS/Kafka); workers run
   the triage graph. The API returns `202 Accepted` immediately; results are
   delivered via webhook/email. Smooths spikes and isolates LLM latency.
3. **Control LLM spend.** Rate-limit per client; cache by ticket-text hash; route
   easy tickets to a smaller/cheaper model and hard ones to the large model;
   batch where possible. Enforce a per-request token budget.
4. **Hosted embeddings or an embedding service** so API images stay lean and the
   model isn't loaded per replica.
5. **Reranking + hybrid search** in RAG as the ticket corpus grows, to keep
   retrieval precise.
6. **Observability at scale:** ship structured logs to Datadog/Loki; dashboards
   for cost/latency/error-rate; sample traces (100% of errors, ~1–10% of success).

---

## 6. What I'd do differently / next

- Persist `latency_ms` and `total_tokens` per ticket to power a real cost
  dashboard via `/analytics`.
- Add **LLM-as-judge** evaluation for the *draft replies* (no single correct
  answer, so accuracy metrics don't apply).
- Index **resolved** tickets with their resolutions so drafts are grounded in
  how issues were actually fixed.
- Add authentication, per-tenant isolation, and PII redaction before embedding.
- CI gate: fail the build if eval accuracy regresses.
