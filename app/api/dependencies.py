"""FastAPI dependencies (the 'D' in dependency injection).

A dependency is a function FastAPI CALLS for you and injects the result into
a route. Benefits:
  - routes declare WHAT they need, not how to build it
  - one place to change construction (e.g. swap repo, inject a per-request session)
  - trivially overridable in tests:  app.dependency_overrides[get_ticket_repository] = fake
"""
from app.db.repository import TicketRepository


def get_ticket_repository() -> TicketRepository:
    """Provide a repository instance to any route that asks for one.

    The repo is stateless (it opens its own short-lived session per call), so a
    fresh instance per request is cheap. The next-level pattern injects the DB
    *session* itself per request (yield + close) - same idea, finer scope.
    """
    return TicketRepository()
