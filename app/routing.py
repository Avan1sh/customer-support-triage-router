"""Routing rules: triaged ticket -> team + SLA. Pure Python, NO LLM call."""
from app.schemas import Category, Priority, TicketTriage, RoutedTicket

_TEAM_BY_CATEGORY = {
    Category.BILLING: "Billing Team",
    Category.TECHNICAL: "Technical Support",
    Category.ACCOUNT: "Account Management",
    Category.FEATURE_REQUEST: "Product Team",
    Category.COMPLAINT: "Customer Success",
}

_SLA_HOURS = {
    Priority.CRITICAL: 1,
    Priority.HIGH: 4,
    Priority.MEDIUM: 24,
    Priority.LOW: 72,
}


def route(triage: TicketTriage) -> RoutedTicket:
    team = _TEAM_BY_CATEGORY[triage.category]
    # Business rule: Critical tickets always jump to a senior escalation queue.
    if triage.priority == Priority.CRITICAL:
        team = f"{team} (Escalation)"
    return RoutedTicket(
        **triage.model_dump(),
        assigned_team=team,
        sla_hours=_SLA_HOURS[triage.priority],
    )
