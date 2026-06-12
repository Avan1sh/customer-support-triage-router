"""Ticket endpoints: create (POST) and read (GET list / GET by id).

An APIRouter is a mini-app: a group of related routes you mount onto the main
app with app.include_router(). It keeps main.py thin and features cohesive.
"""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query

from app.observability.runner import run_triage
from app.notifications.email import send_ticket_email, is_email_configured
from app.db.repository import TicketRepository
from app.api.dependencies import get_ticket_repository
from app.api.schemas import (
    TicketRequest,
    TicketResponse,
    TicketRecord,
    DraftReplyOut,
)

router = APIRouter(prefix="/tickets", tags=["tickets"])


def _state_to_response(state: dict) -> TicketResponse:
    """Map the LangGraph state (internal models) -> the API response (DTO)."""
    triage = state["triage"]
    esc = state["escalation"]
    routed = state["routed"]
    draft = state.get("draft_reply")  # absent on the escalated path
    return TicketResponse(
        ticket_id=state["ticket_id"],
        category=triage.category.value,
        priority=triage.priority.value,
        summary=triage.summary,
        reasoning=triage.reasoning,
        assigned_team=routed.assigned_team,
        sla_hours=routed.sla_hours,
        escalated=esc.should_escalate,
        escalation_severity=esc.severity.value,
        escalation_signals=[s.value for s in esc.signals],
        draft_reply=(
            DraftReplyOut(subject=draft.subject, body=draft.body, tone=draft.tone.value)
            if draft is not None
            else None
        ),
    )


@router.post("", response_model=TicketResponse)
def create_ticket(req: TicketRequest, background_tasks: BackgroundTasks) -> TicketResponse:
    """Triage, route, escalate, (if appropriate) draft a reply, and email the customer."""
    try:
        # run_triage() logs latency/tokens on success and the full exception on
        # failure, so here we only need to translate failure into a clean 502.
        state = run_triage(req.text)
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail="Triage failed; please retry."
        ) from exc

    resp = _state_to_response(state)
    # Only claim "emailed" if we can actually send (real SMTP configured).
    resp.email_queued = bool(req.email) and is_email_configured()

    # If the customer left an email, notify them IN THE BACKGROUND so the HTTP
    # response returns immediately instead of waiting on the SMTP round-trip.
    if req.email:
        background_tasks.add_task(
            send_ticket_email,
            to=req.email,
            ticket_id=resp.ticket_id,
            category=resp.category,
            priority=resp.priority,
            escalated=resp.escalated,
            draft_subject=(resp.draft_reply.subject if resp.draft_reply else None),
            draft_body=(resp.draft_reply.body if resp.draft_reply else None),
        )
    return resp


@router.get("", response_model=list[TicketRecord])
def list_tickets(
    limit: int = Query(50, ge=1, le=200, description="Max rows to return."),
    offset: int = Query(0, ge=0, description="Rows to skip (pagination)."),
    repo: TicketRepository = Depends(get_ticket_repository),
) -> list[TicketRecord]:
    """List tickets, most recent first. Paginated via limit/offset."""
    return repo.list_all(limit=limit, offset=offset)


@router.get("/{ticket_id}", response_model=TicketRecord)
def get_ticket(
    ticket_id: int,
    repo: TicketRepository = Depends(get_ticket_repository),
) -> TicketRecord:
    """Fetch one ticket by id, or 404 if it doesn't exist."""
    ticket = repo.get(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found.")
    return ticket
