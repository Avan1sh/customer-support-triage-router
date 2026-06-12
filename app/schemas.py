"""Typed contracts - single source of truth for ticket data shapes."""
from enum import Enum
from pydantic import BaseModel, Field


class Category(str, Enum):
    BILLING = "Billing"
    TECHNICAL = "Technical"
    ACCOUNT = "Account"
    FEATURE_REQUEST = "Feature Request"
    COMPLAINT = "Complaint"


class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class TicketTriage(BaseModel):
    """Structured triage result for one support ticket."""

    category: Category = Field(description="The single best-fit category.")
    priority: Priority = Field(
        description="Urgency: Critical=service down/money lost; Low=minor question."
    )
    summary: str = Field(description="Neutral one-sentence summary of the issue.")
    reasoning: str = Field(description="Brief justification for category and priority.")


class RoutedTicket(TicketTriage):
    """A triaged ticket plus its routing decision. Inherits all triage fields."""

    assigned_team: str
    sla_hours: int


# --- Escalation (Phase 4) -------------------------------------------------
class EscalationSignal(str, Enum):
    # Keep values SHORT and SINGLE-CONCEPT - long compound values invite
    # the model to paraphrase them, breaking structured-output validation.
    ANGRY_TONE = "Angry tone"
    CHURN_RISK = "Churn risk"
    LEGAL_THREAT = "Legal threat"
    PUBLIC_THREAT = "Public threat"
    REPEAT_CONTACT = "Repeat contact"
    VIP_CUSTOMER = "VIP customer"
    MULTIPLE_ISSUES = "Multiple issues"


class EscalationSeverity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class EscalationDecision(BaseModel):
    """Whether a ticket needs senior-human attention beyond normal queue routing."""

    should_escalate: bool = Field(
        description="True if a senior agent should personally own this ticket."
    )
    signals: list[EscalationSignal] = Field(
        default_factory=list,
        description="Specific signals detected. Empty if should_escalate is False.",
    )
    severity: EscalationSeverity = Field(
        description="How urgent the escalation is, independent of priority."
    )
    reasoning: str = Field(description="One-sentence justification.")


# --- Draft reply (Phase 4 Module 3) --------------------------------------
class ReplyTone(str, Enum):
    APOLOGETIC = "Apologetic"
    INFORMATIVE = "Informative"
    REASSURING = "Reassuring"
    NEUTRAL = "Neutral"


class DraftReply(BaseModel):
    """A suggested reply for a HUMAN agent to review/edit before sending."""

    subject: str = Field(description="Concise email subject line.")
    body: str = Field(
        description="The full reply body, 2-5 short paragraphs. No signoff/signature."
    )
    tone: ReplyTone = Field(description="The tone the reply takes.")
