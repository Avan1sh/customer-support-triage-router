"""API request/response models - the PUBLIC contract of the service.

These are deliberately SEPARATE from app/schemas.py (the internal domain
models) and app/db/models.py (the storage models). Why: the API contract
should stay stable and minimal even when internals change. This boundary is
the DTO (Data Transfer Object) pattern.
"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- POST /tickets -------------------------------------------------------
class TicketRequest(BaseModel):
    """What a client POSTs to create/triage a ticket."""

    text: str = Field(
        min_length=3,
        max_length=5000,  # input guardrail: reject absurd inputs BEFORE the LLM
        description="The raw customer-support ticket text.",
        examples=["I was double-charged for my subscription and want a refund."],
    )
    email: EmailStr | None = Field(
        default=None,
        description="Customer email; if given, we send a confirmation + reply.",
        examples=["customer@example.com"],
    )


class DraftReplyOut(BaseModel):
    subject: str
    body: str
    tone: str


class TicketResponse(BaseModel):
    """The live triage result returned from POST /tickets."""

    ticket_id: int
    category: str
    priority: str
    summary: str
    reasoning: str
    assigned_team: str
    sla_hours: int
    escalated: bool
    escalation_severity: str
    escalation_signals: list[str]
    draft_reply: DraftReplyOut | None = None
    email_queued: bool = False  # True only if a real email will actually be sent


# --- GET /tickets, GET /tickets/{id} -------------------------------------
class TicketRecord(BaseModel):
    """A persisted ticket row, as returned by the read endpoints.

    from_attributes=True lets Pydantic build this straight from a SQLAlchemy
    ORM object (reading .id, .category, ... as attributes). Note we omit
    'reasoning' - an internal justification the API consumer doesn't need.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    category: str
    priority: str
    summary: str
    assigned_team: str
    sla_hours: int
    status: str
    created_at: datetime


# --- GET /analytics ------------------------------------------------------
class AnalyticsResponse(BaseModel):
    total: int
    by_priority: dict[str, int]
    by_category: dict[str, int]
    by_status: dict[str, int]
    by_team: dict[str, int]
