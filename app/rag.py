"""RAG-augmented triage: retrieve similar PAST tickets, inject them as
precedent, then triage the new ticket consistently.

Classic RAG shape:  retrieve -> augment prompt -> generate.
"""
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel

from app.llm import get_model
from app.schemas import TicketTriage
from app.vector_store import get_vector_store

_K = 3  # how many similar past tickets to retrieve as context


def _format_similar(docs: list[Document]) -> str:
    """Turn retrieved tickets into a readable precedent block for the prompt."""
    if not docs:
        return "No similar past tickets found."
    return "\n".join(
        f"- (previously categorized as {d.metadata.get('category', 'Unknown')}) "
        f"{d.page_content}"
        for d in docs
    )


_RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a senior customer-support triage assistant. "
            "Use the SIMILAR PAST TICKETS as precedent so your triage stays "
            "consistent with how comparable issues were handled - but judge the "
            "new ticket on its own merits; ignore precedent if it doesn't fit.",
        ),
        (
            "human",
            "Similar past tickets:\n{context}\n\n---\nNew ticket to triage:\n{ticket}",
        ),
    ]
)

# A retriever is a Runnable:  query string -> list[Document]
_retriever = get_vector_store().as_retriever(search_kwargs={"k": _K})

# The RAG chain in canonical LCEL form.
#   input: {"ticket": "<text>"}
#   - context branch: extract text -> retrieve docs -> format to a string
#   - ticket branch : pass the text through unchanged
#   both keys feed the prompt -> structured model -> TicketTriage
rag_triage_chain = (
    RunnableParallel(
        context=RunnableLambda(lambda x: x["ticket"]) | _retriever | RunnableLambda(_format_similar),
        ticket=RunnableLambda(lambda x: x["ticket"]),
    )
    | _RAG_PROMPT
    | get_model().with_structured_output(TicketTriage)
)
