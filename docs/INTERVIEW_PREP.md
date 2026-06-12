# Interview Prep — LLM / AI Engineer questions

Questions you can expect, answered using **this project** as the concrete
example. Practice saying each answer out loud in 2–3 sentences.

---

## LangChain & LCEL

**Q: What problem does LangChain solve, and when would you *not* use it?**
It standardizes the glue around LLM apps — prompts, structured output, retries,
retrieval, tool calling — behind composable `Runnable` primitives, and lets you
swap providers in one line. I'd skip it for a single prompt/single call (just use
the raw SDK) or a latency-critical hot path where the abstraction adds overhead.

**Q: What is LCEL?**
The expression language that composes runnables with `|` — e.g.
`prompt | model | parser`. Everything (prompts, models, retrievers, plain
functions via `RunnableLambda`) shares the same `.invoke()/.batch()/.stream()`
interface, so I get batching and async for free on the whole chain.

**Q: How did you get reliable JSON out of the model?**
`with_structured_output(PydanticSchema)` — it binds the schema as a tool the
model must call, so output is validated against my types. Far more reliable than
asking for JSON in the prompt and parsing text. I hit two real bugs that taught
this: a small model returned `"False"` (string) for a bool, and a large model
*paraphrased* a long enum value — fixed with short enum values + an exact-label
instruction.

## RAG & vector databases

**Q: What is RAG and what problem does it solve?**
Retrieve relevant context, augment the prompt with it, then generate. It lets the
model reason over private/recent data it was never trained on, reduces
hallucination (open-book vs from-memory), and is instantly updatable. Here I
retrieve similar past tickets as precedent so triage is consistent.

**Q: RAG vs fine-tuning?**
RAG adds *knowledge* cheaply and updatably; fine-tuning changes *behavior/style*
and is expensive/static. Rule of thumb: RAG for facts, fine-tuning for behavior.
This system needs precedent (knowledge), so RAG fits.

**Q: How does a vector DB find neighbors so fast?**
Approximate nearest-neighbor search (e.g. HNSW graphs) — roughly O(log n) instead
of scanning every vector. Query and documents must use the *same* embedding model
so they share a vector space.

**Q: How would you improve a RAG system giving bad answers?**
Inspect retrieval first — most "RAG is broken" issues are retrieval issues. Then:
rerank, hybrid (semantic + keyword) search, tune k/chunking, and watch for data
leakage in evaluation.

## Agents & LangGraph

**Q: Chains vs agents vs LangGraph — when each?**
Chain = fixed pipeline (cheap, predictable). Agent = the LLM chooses actions
(flexible, expensive, less predictable). LangGraph = a stateful graph in between:
explicit nodes/edges with conditional branching — debuggable, checkpointable,
visualizable. Most production "agents" are mostly-deterministic graphs with a few
decision points.

**Q: Where should LLM judgment live vs branching logic?**
LLM judgment goes in a *node* that writes a decision to state; the branching
(`conditional edge`) is a tiny pure function reading that state. Keeps routing
fast, testable, and observable.

**Q: How do you decide where to put a human in the loop?**
Anywhere the LLM could cause irreversible harm — sending a message, issuing a
refund, changing account state. Here, replies are drafts for human review, and
escalated tickets get no AI reply at all.

## Structured output, guardrails, reliability

**Q: How do you stop an LLM from making promises it can't keep?**
Prompt-level guardrails ("don't promise actions outside scope"), structured
output separating *what to do* from *what to say*, post-generation filters, and
human review before send.

**Q: Why temperature 0 for triage but higher for drafts?**
Classification needs determinism and testability (same input → same label).
Draft prose reads stiff at 0, so ~0.3 adds natural variation. Temperature is a
per-task choice, never one global value.

## Evaluation

**Q: How do you evaluate an LLM classifier?**
A human-labeled golden set + metrics: accuracy, per-class precision/recall/F1,
and a confusion matrix to see *which* classes get confused. The point is the
measure → change → measure loop, so prompt changes are evidence-based.

**Q: What's data leakage in eval, and how did you avoid it?**
Evaluating on data the system can effectively look up. My golden tickets resemble
ones in the vector store, so I evaluate the *base* triage chain (no RAG) to
measure real capability, not retrieval of a leaked answer.

**Q: Your accuracy is 94% — is that good?**
Depends on class balance and the baseline; show the confusion matrix. My one miss
was a genuinely ambiguous Account-vs-Technical ticket — a labeling issue as much
as a model error. Priority "accuracy" is lower because priority is subjective, so
I also report within-one-level agreement.

**Q: How do you evaluate generated text (the draft replies)?**
There's no single correct answer, so accuracy doesn't apply — use LLM-as-judge
against a rubric (helpfulness/tone/accuracy) plus human review.

## Production / backend

**Q: Walk me through a request.**
Uvicorn → FastAPI validates the body via Pydantic (422 on bad input, before any
LLM cost) → `run_triage` runs the LangGraph workflow with token/latency capture →
result mapped to a response DTO → email sent in a background task → JSON returned.

**Q: How do you track and control LLM cost?**
Capture `usage_metadata` tokens per request via a callback, log them structured,
persist for dashboards, and enforce budgets (input caps, rate limits, smaller
models for easy cases, caching).

**Q: Why a separate response DTO instead of returning your DB/internal models?**
Stability (clients don't break when internals change), control (expose only
intended fields), and security (no accidental field leaks). It's the DTO/boundary
pattern.

**Q: Image vs container? How does Docker layer caching help?**
An image is the built snapshot; a container is a running instance. Ordering the
Dockerfile least-changing → most-changing (deps before app code) means code edits
reuse the cached dependency layer, so rebuilds take seconds.

**Q: How would you scale this to thousands of tickets/min?**
Stateless API replicas behind a load balancer; SQLite→Postgres and local
Chroma→a managed vector DB so state is shared; a queue (SQS/Kafka) with workers so
the API returns immediately; cost controls and observability at scale. (See
SYSTEM_DESIGN.md.)
