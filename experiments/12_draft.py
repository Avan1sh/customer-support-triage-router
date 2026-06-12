"""Phase 4 - Module 3 - Response-drafting agent.

Run from PROJECT ROOT:
    $env:PYTHONPATH="."; python experiments\\12_draft.py

Three tickets. Two should be drafted; one (escalated) should be SKIPPED.
"""
from app.db.session import init_db
from app.graph import triage_graph

init_db()

TICKETS = [
    "Hi, just wondering how I change my profile picture?",
    "The dashboard won't load after the latest update. Could you take a look?",
    "I've been double-charged THREE times now and your support is USELESS. "
    "Cancelling my account TODAY and posting all over Twitter.",
]

for t in TICKETS:
    print("=" * 70)
    print(f"TICKET: {t}\n")
    s = triage_graph.invoke({"ticket": t})

    print(f"  triage   : {s['triage'].category.value} / {s['triage'].priority.value}")
    print(f"  escalate?: {s['escalation'].should_escalate}")
    print(f"  routed   : {s['routed'].assigned_team} (SLA {s['routed'].sla_hours}h)")
    print(f"  saved    : #{s['ticket_id']}")

    if "draft_reply" in s:
        d = s["draft_reply"]
        print(f"\n  DRAFT REPLY  (tone: {d.tone.value})")
        print(f"  Subject: {d.subject}")
        print( "  Body:")
        for line in d.body.split("\n"):
            print(f"    {line}")
    else:
        print("\n  (drafting skipped - ticket escalated; human will reply personally)")

print("\n" + "=" * 70)
print("GRAPH (paste at mermaid.live):")
print(triage_graph.get_graph().draw_mermaid())
