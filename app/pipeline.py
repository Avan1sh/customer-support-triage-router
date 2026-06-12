"""Full pipeline: ticket text -> triaged AND routed, as one LCEL chain."""
from langchain_core.runnables import RunnableLambda
from app.triage import triage_chain
from app.routing import route

# LCEL: the output of triage_chain (a TicketTriage) flows into route().
# RunnableLambda wraps a plain Python function so it can live inside a chain.
pipeline = triage_chain | RunnableLambda(route)
