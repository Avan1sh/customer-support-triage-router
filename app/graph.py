"""LangGraph triage workflow with conditional escalation AND optional drafting.

Phase 4 progression:
  - Module 1: linear graph (triage -> route -> persist)
  - Module 2: + escalation node + conditional branch
  - Module 3: + draft node + conditional skip for escalated tickets
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from app.rag import rag_triage_chain
from app.routing import route
from app.escalation import escalation_chain
from app.draft import draft_chain
from app.db.repository import TicketRepository
from app.vector_store import add_tickets
from app.schemas import TicketTriage, RoutedTicket, EscalationDecision, DraftReply


class TriageState(TypedDict, total=False):
    ticket: str                     # input
    triage: TicketTriage            # set by triage_node
    escalation: EscalationDecision  # set by escalation_node
    routed: RoutedTicket            # set by route_node OR handle_escalation_node
    ticket_id: int                  # set by persist_node
    draft_reply: DraftReply         # set by draft_node (only on non-escalated path)


_repo = TicketRepository()


# --- Nodes ---------------------------------------------------------------

def triage_node(state: TriageState) -> dict:
    return {"triage": rag_triage_chain.invoke({"ticket": state["ticket"]})}


def escalation_node(state: TriageState) -> dict:
    return {"escalation": escalation_chain.invoke({"ticket": state["ticket"]})}


def route_node(state: TriageState) -> dict:
    return {"routed": route(state["triage"])}


def handle_escalation_node(state: TriageState) -> dict:
    base = route(state["triage"])
    return {
        "routed": base.model_copy(
            update={
                "assigned_team": f"Senior Escalation - {base.assigned_team}",
                "sla_hours": max(1, base.sla_hours // 2),
            }
        )
    }


def persist_node(state: TriageState) -> dict:
    routed = state["routed"]
    saved = _repo.add(state["ticket"], routed)
    add_tickets(
        [state["ticket"]],
        [{"category": routed.category.value, "ticket_id": saved.id}],
    )
    return {"ticket_id": saved.id}


def draft_node(state: TriageState) -> dict:
    """Draft a suggested reply (non-escalated path only)."""
    t = state["triage"]
    reply = draft_chain.invoke(
        {
            "ticket": state["ticket"],
            "category": t.category.value,
            "priority": t.priority.value,
            "summary": t.summary,
        }
    )
    return {"draft_reply": reply}


# --- Dispatchers ---------------------------------------------------------

def should_escalate(state: TriageState) -> str:
    return "handle_escalation" if state["escalation"].should_escalate else "route"


def should_draft(state: TriageState) -> str:
    """Skip drafting for escalated tickets - humans should write those personally."""
    return "skip" if state["escalation"].should_escalate else "draft"


# --- Graph ---------------------------------------------------------------

def build_graph():
    g = StateGraph(TriageState)
    g.add_node("triage", triage_node)
    g.add_node("escalation", escalation_node)
    g.add_node("handle_escalation", handle_escalation_node)
    g.add_node("route", route_node)
    g.add_node("persist", persist_node)
    g.add_node("draft", draft_node)

    g.add_edge(START, "triage")
    g.add_edge("triage", "escalation")
    g.add_conditional_edges(
        "escalation",
        should_escalate,
        {"handle_escalation": "handle_escalation", "route": "route"},
    )
    g.add_edge("handle_escalation", "persist")
    g.add_edge("route", "persist")
    # NEW: after persist, decide whether to draft a reply.
    g.add_conditional_edges(
        "persist",
        should_draft,
        {"draft": "draft", "skip": END},
    )
    g.add_edge("draft", END)

    return g.compile()


triage_graph = build_graph()
