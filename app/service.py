"""Application service - orchestrates the full ticket lifecycle.

This is the layer the FastAPI routes will call in Phase 5. It wires together
the RAG triage chain, deterministic routing, the relational store, and the
vector index - so callers just say process_ticket(text).
"""
from app.rag import rag_triage_chain
from app.routing import route
from app.db.models import Ticket
from app.db.repository import TicketRepository
from app.vector_store import add_tickets

_repo = TicketRepository()


def process_ticket(text: str) -> Ticket:
    """Full lifecycle: RAG triage -> route -> persist (SQL) -> index (vector)."""
    # 1) Triage using retrieved precedent (the RAG chain retrieves internally).
    triage = rag_triage_chain.invoke({"ticket": text})
    # 2) Deterministic routing (pure Python, no LLM).
    routed = route(triage)
    # 3) Persist to the system of record; this assigns the primary-key id.
    saved = _repo.add(text, routed)
    # 4) Index in the vector store so THIS ticket becomes precedent for future
    #    ones. Store the SQLite id in metadata to link the two stores together.
    add_tickets([text], [{"category": routed.category.value, "ticket_id": saved.id}])
    return saved
