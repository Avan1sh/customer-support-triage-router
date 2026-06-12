"""Phase 4 - Module 1 - LangGraph fundamentals.

Run from PROJECT ROOT:
    $env:PYTHONPATH="."; python experiments\\10_langgraph.py

Demonstrates: TypedDict state, nodes, edges, compile, invoke,
and visualizing the graph as a Mermaid diagram.
"""
from app.db.session import init_db
from app.graph import triage_graph

init_db()

text = "I cannot log into my account; it says my password is wrong but I just reset it."

# .invoke() works the same as on chains - the final state dict comes back.
final = triage_graph.invoke({"ticket": text})

print("FINAL STATE keys:", list(final.keys()))
print(f"  triage   : {final['triage'].category.value} / {final['triage'].priority.value}")
print(f"  routed   : {final['routed'].assigned_team} (SLA {final['routed'].sla_hours}h)")
print(f"  ticket_id: #{final['ticket_id']}")

# Free visualization - LangGraph can emit a Mermaid diagram of itself.
print("\nGRAPH (paste into mermaid.live to view):")
print(triage_graph.get_graph().draw_mermaid())
