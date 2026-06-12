"""Phase 3 - Module 1 - Embeddings: text -> vectors -> semantic similarity.

Run from the PROJECT ROOT so 'app' is importable:
    $env:PYTHONPATH="."; python experiments\\06_embeddings.py

Lesson: absolute cosine values cluster high & close together; what matters
for retrieval is the RANKING - the right match comes out on top.
"""
import math
from app.embeddings import get_embeddings

emb = get_embeddings()


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb)


# --- Part 1: a single pair comparison ---
pair = emb.embed_documents(
    ["I was charged twice for my subscription.", "My card got double-billed this month."]
)
print("Vector dimensions:", len(pair[0]))
print(f"two billing tickets (different words): {cosine(pair[0], pair[1]):.3f}\n")

# --- Part 2: ranked retrieval (how the vector DB will actually work) ---
query = "I got billed twice this month and want a refund."
candidates = [
    "My card was double-charged for the subscription.",  # billing  <- should rank #1
    "How do I reset my forgotten password?",             # account
    "The mobile app keeps crashing on startup.",         # technical
    "Can you please add a dark mode feature?",           # feature request
]

q_vec = emb.embed_query(query)
scored = [(cosine(q_vec, emb.embed_query(c)), c) for c in candidates]
scored.sort(reverse=True)

print(f"QUERY: {query}\n")
print("Most similar past tickets (ranked):")
for rank, (score, text) in enumerate(scored, 1):
    print(f"  {rank}. [{score:.3f}] {text}")
