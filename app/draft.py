"""Response-drafting agent.

Given a triaged ticket + similar past tickets as precedent, draft a reply
for a HUMAN agent to review. Temperature is slightly raised (0.3) - draft
text benefits from a bit of variety; triage benefits from determinism.
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from app.llm import get_model
from app.schemas import DraftReply
from app.vector_store import get_vector_store

_K = 3
_retriever = get_vector_store().as_retriever(search_kwargs={"k": _K})


def _format_precedent(docs) -> str:
    if not docs:
        return "No similar past tickets found."
    return "\n".join(
        f"- ({d.metadata.get('category', '?')}) {d.page_content}" for d in docs
    )


def _build_inputs(inputs: dict) -> dict:
    """Take {ticket, category, priority, summary} -> add 'precedent' from RAG."""
    docs = _retriever.invoke(inputs["ticket"])
    return {**inputs, "precedent": _format_precedent(docs)}


_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful, empathetic customer-support agent drafting a "
            "reply for a HUMAN COLLEAGUE to review before sending. "
            "Keep the body to 2-5 short paragraphs. Acknowledge the issue, "
            "explain the likely next step, and set realistic expectations. "
            "Match the tone to the situation. Do NOT add a signoff or signature "
            "- the human will. Do NOT promise actions outside support's scope.",
        ),
        (
            "human",
            "Ticket category: {category}\n"
            "Ticket priority: {priority}\n"
            "Summary: {summary}\n\n"
            "Similar past tickets (precedent):\n{precedent}\n\n"
            "Original ticket:\n{ticket}",
        ),
    ]
)

# temperature=0.3 - a touch of variety for natural prose. Still mostly grounded.
draft_chain = (
    RunnableLambda(_build_inputs)
    | _PROMPT
    | get_model(temperature=0.3).with_structured_output(DraftReply)
)
