"""Phase 4 - Module 2 - Conditional escalation in LangGraph.

Run from PROJECT ROOT:
    $env:PYTHONPATH="."; python experiments\\11_escalation.py

We feed three tickets and watch the graph TAKE DIFFERENT PATHS:
  1. calm, low-stakes  -> normal route
  2. angry + churn     -> escalation branch
  3. neutral technical -> normal route
"""
from app.db.session import init_db
from app.graph import triage_graph

init_db()

TICKETS = [
    "Hi, just wondering how I change my profile picture?",
    "I've been double-charged THREE times now and your support is USELESS. "
    "Cancelling my account TODAY and posting all over Twitter.",
    "The dashboard won't load after the latest update. Could you take a look?",
]

for t in TICKETS:
    print("=" * 70)
    print(f"TICKET: {t}\n")
    s = triage_graph.invoke({"ticket": t})

    esc = s["escalation"]
    routed = s["routed"]
    print(f"  triage   : {s['triage'].category.value} / {s['triage'].priority.value}")
    print(f"  escalate?: {esc.should_escalate}  severity={esc.severity.value}")
    print(f"  signals  : {[x.value for x in esc.signals]}")
    print(f"  routed   : {routed.assigned_team} (SLA {routed.sla_hours}h)")
    print(f"  ticket id: #{s['ticket_id']}")

print("\n" + "=" * 70)
print("GRAPH (paste at mermaid.live):")
print(triage_graph.get_graph().draw_mermaid())
