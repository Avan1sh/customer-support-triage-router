"""Embedding model factory - turns text into vectors that capture meaning."""
from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings


@lru_cache  # load the model once (it's expensive to initialize)
def get_embeddings() -> HuggingFaceEmbeddings:
    # all-MiniLM-L6-v2: 384-dim, fast, runs locally & free, great size/quality tradeoff.
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
