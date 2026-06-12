"""Instrumented entrypoint to the triage graph.

Wraps triage_graph.invoke() with the three observability pillars:
  - LATENCY: wall-clock time of the whole workflow
  - COST:    total LLM tokens across all calls in the graph (triage + escalation + draft)
  - LOGS:    a structured success/failure event, incl. the REAL exception on failure

This is the function the API should call instead of the raw graph, so every
request is measured and every failure is captured (not swallowed).
"""
import time

from langchain_core.callbacks import get_usage_metadata_callback

from app.graph import triage_graph
from app.observability.logger import get_logger

_log = get_logger()


def run_triage(text: str) -> dict:
    """Run the triage graph with latency + token logging. Returns the final state."""
    start = time.perf_counter()
    try:
        # The callback accumulates token usage across EVERY LLM call inside the
        # graph for the duration of this context - keyed by model name.
        with get_usage_metadata_callback() as cb:
            state = triage_graph.invoke({"ticket": text})
        usage = cb.usage_metadata
    except Exception:
        elapsed_ms = (time.perf_counter() - start) * 1000
        # Log the FULL exception server-side; the API turns this into a clean 502.
        _log.error(
            "triage_failed",
            extra={"fields": {
                "latency_ms": round(elapsed_ms, 1),
                "text_preview": text[:80],
            }},
            exc_info=True,  # attaches the traceback to the JSON log
        )
        raise

    elapsed_ms = (time.perf_counter() - start) * 1000
    total_tokens = sum(m.get("total_tokens", 0) for m in usage.values())

    _log.info(
        "triage_completed",
        extra={"fields": {
            "ticket_id": state.get("ticket_id"),
            "category": state["triage"].category.value,
            "priority": state["triage"].priority.value,
            "escalated": state["escalation"].should_escalate,
            "drafted": "draft_reply" in state,
            "latency_ms": round(elapsed_ms, 1),
            "total_tokens": total_tokens,
            "llm_calls_by_model": {k: v.get("total_tokens", 0) for k, v in usage.items()},
        }},
    )
    return state
