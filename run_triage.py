"""Demo: run the triage pipeline on a few sample tickets."""
from app.triage import triage_ticket

TICKETS = [
    "Hi, I was charged twice for my subscription this month. Please help!",
    "The app crashes every time I upload a photo.",
    "Just wondering how I change my profile picture?",
    "Your service has been down for 2 hours and my business is losing money!",
]

for t in TICKETS:
    r = triage_ticket(t)
    print(f"[{r.priority.value:8}] {r.category.value:15} | {r.summary}")
