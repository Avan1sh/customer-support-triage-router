"""Model factory - the ONE place that knows how to build the LLM client."""
from functools import lru_cache
from langchain_groq import ChatGroq
from app.config import GROQ_MODEL


@lru_cache  # build the client once and reuse it, instead of per-call
def get_model(temperature: float = 0.0) -> ChatGroq:
    return ChatGroq(model=GROQ_MODEL, temperature=temperature)
