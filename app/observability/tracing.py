"""LangSmith tracing status.

LangChain auto-traces EVERY chain/LLM/graph call to LangSmith when these env
vars are set - NO code changes needed:
    LANGSMITH_TRACING=true
    LANGSMITH_API_KEY=ls__...
    LANGSMITH_PROJECT=support-triage-router   (optional grouping)

LangSmith then shows each run's exact prompt, response, token counts, latency,
and the full graph tree. This module just reports whether it's wired up.
"""
import os


def tracing_status() -> str:
    """Human-readable description of whether LangSmith tracing is active."""
    enabled = os.getenv("LANGSMITH_TRACING", "").lower() == "true" or (
        os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true"
    )
    has_key = bool(os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY"))
    if enabled and has_key:
        return "ON"
    if enabled and not has_key:
        return "REQUESTED but no API key set (LANGSMITH_API_KEY)"
    return "OFF (set LANGSMITH_TRACING=true + LANGSMITH_API_KEY to enable)"
