"""Phase 3 - Module 2 - ChromaDB vector store + retriever.

Run from the PROJECT ROOT so 'app' is importable:
    $env:PYTHONPATH="."; python experiments\\07_vector_store.py

Demonstrates:
  1. Seeding past tickets into a persistent vector DB.
  2. similarity_search_with_score()  -> raw distances (lower = closer).
  3. .as_retriever()                 -> a Runnable that drops into LCEL chains.
"""
from app.vector_store import get_vector_store, add_tickets, search_similar

# --- A small 'history' of past resolved tickets, with metadata ---
PAST_TICKETS = [
    ("My card was double-charged for the subscription.", {"category": "Billing", "id": 1}),
    ("I want a refund for last month's duplicate payment.", {"category": "Billing", "id": 2}),
    ("How do I reset my forgotten password?", {"category": "Account", "id": 3}),
    ("The mobile app keeps crashing on startup.", {"category": "Technical", "id": 4}),
    ("Please add a dark mode feature to the dashboard.", {"category": "Feature Request", "id": 5}),
    ("My invoice shows the wrong billing address.", {"category": "Billing", "id": 6}),
]

# Seed only if the store is empty, so re-runs don't duplicate data.
store = get_vector_store()
if len(store.get()["ids"]) == 0:
    texts = [t for t, _ in PAST_TICKETS]
    metas = [m for _, m in PAST_TICKETS]
    add_tickets(texts, metas)
    print(f"Seeded {len(texts)} past tickets into ChromaDB.\n")
else:
    print(f"Store already has {len(store.get()['ids'])} tickets (skipping seed).\n")

# --- 1) Raw similarity search with scores (distance: lower = closer) ---
query = "I was billed twice and need my money back"
print(f"QUERY: {query}\n")
print("similarity_search_with_score (distance, lower=closer):")
for doc, score in search_similar(query, k=3):
    print(f"  [dist={score:.3f}] ({doc.metadata['category']}) {doc.page_content}")

# --- 2) The retriever interface (a Runnable - this is what feeds RAG chains) ---
retriever = store.as_retriever(search_kwargs={"k": 3})
print("\n.as_retriever().invoke(query) -> top-k Documents:")
for doc in retriever.invoke(query):
    print(f"  ({doc.metadata['category']}) {doc.page_content}")
