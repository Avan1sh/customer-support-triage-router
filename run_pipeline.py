"""Demo: full triage + routing pipeline."""
from app.pipeline import pipeline

TICKETS = [
    "Hi, I was charged twice for my subscription this month. Please help!",
    "The app crashes every time I upload a photo.",
    "Just wondering how I change my profile picture?",
    "Your service has been down for 2 hours and my business is losing money!",
]

# .batch() runs all tickets concurrently and returns results in the same order.
results = pipeline.batch([{"ticket": t} for t in TICKETS])

for r in results:
    print(f"[{r.priority.value:8}] {r.category.value:15} -> {r.assigned_team:28} (SLA {r.sla_hours}h)")
