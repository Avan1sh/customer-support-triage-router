"""Phase 3 - Module 4 - RAG-augmented triage.

Run from PROJECT ROOT:
    $env:PYTHONPATH="."; python experiments\\09_rag.py
"""
from app.db.session import init_db
from app.vector_store import get_vector_store
from app.rag import rag_triage_chain
from app.service import process_ticket

init_db()

new_ticket = "I keep getting double billed and I just want my money returned."
print(f"NEW TICKET: {new_ticket}\n")

# 1) Show WHAT precedent gets retrieved (the 'R' in RAG).
print("Retrieved precedent:")
retriever = get_vector_store().as_retriever(search_kwargs={"k": 3})
for d in retriever.invoke(new_ticket):
    print(f"  - ({d.metadata.get('category', '?')}) {d.page_content}")

# 2) RAG triage - retrieval feeds the prompt automatically inside the chain.
print("\nRAG triage result:")
triage = rag_triage_chain.invoke({"ticket": new_ticket})
print(f"  category={triage.category.value}  priority={triage.priority.value}")
print(f"  summary={triage.summary}")

# 3) Full lifecycle: triage + route + persist (SQL) + index (vector).
print("\nFull pipeline (process_ticket):")
saved = process_ticket(new_ticket)
print(f"  saved to SQLite as {saved!r}")
print("  -> also indexed in the vector store (now precedent for future tickets)")
