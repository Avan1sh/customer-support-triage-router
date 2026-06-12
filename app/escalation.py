"""Escalation detector - a fast, cheap LLM check for senior-human signals.

Cost-discipline lesson: this is a near-binary judgment that runs on EVERY
ticket, so we use a SMALLER/CHEAPER model than the main triage. Big models
for hard reasoning, small models for filters/classifiers.
"""
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from app.schemas import EscalationDecision

# Cost-vs-reliability lesson (real bug we hit): the 8B "instant" model
# returned "False" (string) instead of false (bool) for structured output,
# breaking schema validation. The honest fix is to fall back to the same
# reliable model as triage. Override via GROQ_DETECTOR_MODEL once you find
# a small model that handles this schema (try gemma2-9b-it or json_mode).
_DETECTOR_MODEL = os.getenv("GROQ_DETECTOR_MODEL") or os.getenv(
    "GROQ_MODEL", "llama-3.3-70b-versatile"
)

_detector = ChatGroq(model=_DETECTOR_MODEL, temperature=0).with_structured_output(
    EscalationDecision
)

_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You decide whether a customer-support ticket needs SENIOR-HUMAN "
            "escalation beyond normal queue routing. Escalate ONLY for genuine "
            "signals: explicit anger or insults, churn threats ('canceling', "
            "'switching providers'), legal/regulatory threats, public-shaming "
            "threats, repeated contact (e.g. 'third time'), or known VIP. "
            "Calm tickets - EVEN Critical technical ones - usually do not need "
            "escalation; they need fast normal handling. "
            "IMPORTANT: when filling the 'signals' field, copy values EXACTLY "
            "from the allowed enum; do not paraphrase or invent new labels.",
        ),
        ("human", "Ticket:\n{ticket}"),
    ]
)

escalation_chain = _PROMPT | _detector
