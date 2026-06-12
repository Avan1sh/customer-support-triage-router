"""Phase 3 - Module 3 - relational persistence (SQLite + SQLAlchemy).

Run from PROJECT ROOT:
    $env:PYTHONPATH="."; python experiments\\08_persistence.py

Full flow:  raw text -> pipeline (triage + route) -> save to SQLite -> query history.
"""
from app.db.session import init_db
from app.db.repository import TicketRepository
from app.pipeline import pipeline

init_db()                       # create the 'tickets' table if needed
repo = TicketRepository()

NEW_TICKETS = [
    "I was charged twice for my subscription this month!",
    "The dashboard won't load after the latest update.",
]

print("--- Processing new tickets ---")
for text in NEW_TICKETS:
    routed = pipeline.invoke({"ticket": text})   # LLM triage + deterministic routing
    saved = repo.add(text, routed)               # persist to the relational DB
    print(f"Saved {saved!r}  (SLA {saved.sla_hours}h)")

print("\n--- Ticket history (most recent first) ---")
for t in repo.list_all():
    print(f"#{t.id} [{t.created_at:%Y-%m-%d %H:%M}] {t.priority:8} {t.category:16} -> {t.assigned_team}")

print("\n--- Open tickets only ---")
for t in repo.list_by_status("Open"):
    print(f"#{t.id} {t.summary}")
