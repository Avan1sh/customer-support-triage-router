"""Database engine + session factory.

- engine: the connection manager to the actual DB file.
- SessionLocal: a factory that hands out short-lived 'sessions' (work units).
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Base

# Config from the environment (12-factor): defaults to a local file, but in
# Docker we point it at a mounted volume so data survives container restarts.
# To move to Postgres later, ONLY this URL changes (e.g. postgresql+psycopg://...).
_DB_URL = os.getenv("DATABASE_URL", "sqlite:///support.db")

engine = create_engine(_DB_URL, echo=False)  # echo=True prints every SQL statement

# expire_on_commit=False -> objects stay usable after the session closes,
# so we can return them from the repository without surprise lazy-load errors.
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db() -> None:
    """Create tables that don't exist yet. Safe to call repeatedly (idempotent)."""
    Base.metadata.create_all(engine)
