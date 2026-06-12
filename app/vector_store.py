"""Vector store layer - persistent ChromaDB wired to our embedding model.

This is the 'memory' of the system: past tickets live here as vectors so we
can later retrieve the most semantically similar ones (the core of RAG).
"""
import os
from functools import lru_cache
from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.embeddings import get_embeddings

# Where Chroma persists its files on disk (env-configurable for Docker volumes).
# Git-ignored locally (see .gitignore: chroma_db/).
_PERSIST_DIR = os.getenv("CHROMA_DIR", "chroma_db")
# A 'collection' is like a table - a named bucket of vectors.
_COLLECTION = "tickets"


@lru_cache  # one shared store instance for the whole process
def get_vector_store() -> Chroma:
    """Open (or create) the persistent ticket vector store."""
    return Chroma(
        collection_name=_COLLECTION,
        embedding_function=get_embeddings(),  # SAME model for store AND query
        persist_directory=_PERSIST_DIR,
    )


def add_tickets(texts: list[str], metadatas: list[dict] | None = None) -> list[str]:
    """Embed and store a batch of past tickets. Returns their generated IDs."""
    store = get_vector_store()
    docs = [
        Document(page_content=text, metadata=(metadatas[i] if metadatas else {}))
        for i, text in enumerate(texts)
    ]
    return store.add_documents(docs)  # embedding happens here, automatically


def search_similar(query: str, k: int = 3) -> list[tuple[Document, float]]:
    """Return the k most similar past tickets, each with its distance score.

    NOTE: the score is a DISTANCE (lower = more similar), not cosine similarity.
    """
    return get_vector_store().similarity_search_with_score(query, k=k)
