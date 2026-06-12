"""Repository pattern - the ONLY place that talks SQL/ORM for tickets.

Why: business logic and API routes should ask for data in plain terms
('save this ticket', 'list open ones') without knowing HOW it's stored.
If we later switch DBs or queries, only this file changes.
"""
from sqlalchemy import select, func

from app.db.models import Ticket
from app.db.session import SessionLocal
from app.schemas import RoutedTicket


class TicketRepository:
    def add(self, raw_text: str, routed: RoutedTicket) -> Ticket:
        """Persist a triaged + routed ticket; return the saved row (with id)."""
        with SessionLocal() as session:  # opens a transaction; auto-closes
            ticket = Ticket(
                text=raw_text,
                category=routed.category.value,
                priority=routed.priority.value,
                summary=routed.summary,
                reasoning=routed.reasoning,
                assigned_team=routed.assigned_team,
                sla_hours=routed.sla_hours,
            )
            session.add(ticket)      # stage the insert
            session.commit()         # write to disk (transaction commits here)
            session.refresh(ticket)  # reload DB-generated fields (id, created_at)
            return ticket

    def get(self, ticket_id: int) -> Ticket | None:
        with SessionLocal() as session:
            return session.get(Ticket, ticket_id)  # primary-key lookup

    def list_all(self, limit: int = 50, offset: int = 0) -> list[Ticket]:
        """Most-recent-first, PAGINATED. Never return an unbounded result set."""
        with SessionLocal() as session:
            stmt = (
                select(Ticket)
                .order_by(Ticket.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            return list(session.scalars(stmt))

    def list_by_status(self, status: str) -> list[Ticket]:
        with SessionLocal() as session:
            stmt = select(Ticket).where(Ticket.status == status)
            return list(session.scalars(stmt))

    # --- Analytics: aggregate queries (the data layer for the dashboard) ----

    def total_count(self) -> int:
        with SessionLocal() as session:
            return session.scalar(select(func.count()).select_from(Ticket)) or 0

    def _count_by(self, column) -> dict[str, int]:
        """GROUP BY <column> -> {value: count}. Aggregation happens IN the DB,
        not by pulling every row into Python - that's the whole point of SQL."""
        with SessionLocal() as session:
            stmt = select(column, func.count()).group_by(column)
            return {key: count for key, count in session.execute(stmt).all()}

    def count_by_priority(self) -> dict[str, int]:
        return self._count_by(Ticket.priority)

    def count_by_category(self) -> dict[str, int]:
        return self._count_by(Ticket.category)

    def count_by_status(self) -> dict[str, int]:
        return self._count_by(Ticket.status)

    def count_by_team(self) -> dict[str, int]:
        return self._count_by(Ticket.assigned_team)
