"""
Phase 1 - Module 3 - Structured Output
--------------------------------------
Goal: replace fragile free-text answers with a validated, typed object.
We also fold all THREE Phase-1 skills (classify + prioritize + summarize)
into a SINGLE structured call.

Run:  python experiments/03_structured_output.py
"""

import os
from enum import Enum
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
model = ChatGroq(model=GROQ_MODEL, temperature=0)


# 1) ENUMS - fix the universe of allowed values. The model literally
#    cannot return anything outside these sets.
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


# 2) THE SCHEMA - our typed contract for one triaged ticket.
#    The Field(description=...) text is sent to the model as guidance,
#    so write these descriptions like instructions, not afterthoughts.
class TicketTriage(BaseModel):
    """Structured triage result for a single customer-support ticket."""

    category: Category = Field(
        description="The single best-fit category for the ticket."
    )
    priority: Priority = Field(
        description="Urgency based on customer impact, money at risk, and tone. "
        "Critical = service down or money lost; Low = minor question."
    )
    summary: str = Field(
        description="A neutral one-sentence summary of the customer's issue."
    )
    reasoning: str = Field(
        description="A brief justification for the chosen category and priority."
    )


# 3) Bind the schema to the model. This returns a NEW runnable whose
#    output is forced to match TicketTriage.
triage_model = model.with_structured_output(TicketTriage)

# 4) A prompt that describes the TASK. Note: we DON'T need to describe the
#    JSON format here - the schema handles that for us.
triage_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a senior customer-support triage assistant. "
            "Read the ticket and triage it accurately and consistently.",
        ),
        ("human", "Ticket:\n{ticket}"),
    ]
)

ticket = "URGENT! Your billing system charged my card 3 times and now I'm overdrawn. Fix this NOW or I'm disputing the charge and leaving."

prompt_value = triage_prompt.invoke({"ticket": ticket})

# 5) Invoke. result is a VALIDATED TicketTriage object, not a string.
result = triage_model.invoke(prompt_value)

print("RETURN TYPE :", type(result).__name__)
print("CATEGORY    :", result.category.value)
print("PRIORITY    :", result.priority.value)
print("SUMMARY     :", result.summary)
print("REASONING   :", result.reasoning)
print()
print("Whole object as a dict:", result.model_dump())
