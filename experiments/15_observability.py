"""Phase 5 - Module 3 - observability: structured logs + latency + token cost.

Run from PROJECT ROOT:
    $env:PYTHONPATH="."; python experiments\\15_observability.py

Each run_triage() call emits a structured JSON log line with latency_ms and
total_tokens. On the API, the same data is logged per request automatically.
"""
from app.db.session import init_db
from app.observability.runner import run_triage
from app.observability.tracing import tracing_status

init_db()
print(f"LangSmith tracing: {tracing_status()}\n")
print("--- structured logs (one JSON line per ticket) ---")

for text in [
    "I was double charged and want a refund.",
    "Third time asking and still no fix. Cancel my account, this is unacceptable!",
]:
    run_triage(text)  # the JSON log prints to stdout from inside the runner
