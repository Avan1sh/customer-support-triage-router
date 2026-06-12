"""SQLAlchemy ORM models - Python classes mapped to database tables.

ORM (Object-Relational Mapper): instead of writing raw SQL strings, we define
a Python class; SQLAlchemy translates it to a table and turns rows into objects.
"""
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Parent for all ORM models. SQLAlchemy collects table definitions here."""


class Ticket(Base):
    __tablename__ = "tickets"  # the actual table name in the database

    # Mapped[...] declares the Python type; mapped_column(...) the SQL column.
    id: Mapped[int] = mapped_column(primary_key=True)  # auto-incrementing PK
    text: Mapped[str] = mapped_column(Text)            # the raw ticket body
    category: Mapped[str] = mapped_column(String(50))
    priority: Mapped[str] = mapped_column(String(20))
    summary: Mapped[str] = mapped_column(Text)
    reasoning: Mapped[str] = mapped_column(Text)
    assigned_team: Mapped[str] = mapped_column(String(80))
    sla_hours: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="Open")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<Ticket #{self.id} {self.category}/{self.priority} {self.status}>"
