"""The triage pipeline: ticket text -> validated TicketTriage object."""
from langchain_core.prompts import ChatPromptTemplate
from app.llm import get_model
from app.schemas import TicketTriage

# A few labeled examples that teach the model our TRICKY distinctions.
# Few-shot beats longer rules: the model copies patterns from examples.
_FEWSHOT = [
    ("human", "Ticket:\nI have emailed three times about my wrong invoice and nobody replies. Disgusted."),
    ("ai", "category: Complaint | priority: High | summary: Customer is frustrated by repeated unanswered invoice queries. | reasoning: Repeated ignored contacts and a strongly negative tone make this a service complaint, not a routine billing question."),
    ("human", "Ticket:\nIt would be nice if the dashboard had a dark mode option."),
    ("ai", "category: Feature Request | priority: Low | summary: User suggests adding dark mode to the dashboard. | reasoning: A request for new functionality with no current malfunction; low urgency."),
]

_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a senior customer-support triage assistant. "
            "Triage each ticket accurately and consistently. "
            "Study the examples, then triage the final ticket.",
        ),
        *_FEWSHOT,
        ("human", "Ticket:\n{ticket}"),
    ]
)

# Compose once: prompt -> structured model. The "|" is LCEL.
triage_chain = _PROMPT | get_model().with_structured_output(TicketTriage)


def triage_ticket(ticket: str) -> TicketTriage:
    """Classify, prioritize, and summarize a single support ticket."""
    return triage_chain.invoke({"ticket": ticket})
