"""FastAPI application entrypoint.

Thin by design: it wires startup, metadata, and routers together. All route
logic lives in app/api/routers/*. This is the composition root.

Run the live server (Swagger UI at http://127.0.0.1:8000/docs):
    $env:PYTHONPATH="."
    python -m uvicorn app.api.main:app
(use the venv's python; add --reload while developing)
"""
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import init_db
from app.api.routers import health, tickets, analytics
from app.observability.logger import get_logger
from app.observability.tracing import tracing_status

_log = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup work that must finish before the first request: create tables."""
    init_db()
    _log.info("startup", extra={"fields": {"langsmith_tracing": tracing_status()}})
    yield
    # (shutdown cleanup would go here)


app = FastAPI(
    title="Customer Support Triage & Resolution Router",
    description="Classifies, prioritizes, routes, escalates, and drafts replies "
    "for incoming customer-support tickets.",
    version="0.6.0",
    lifespan=lifespan,
)

# CORS: allow a browser frontend on another origin to call this API directly.
# The Vite dev proxy already avoids CORS in dev; this covers prod/other origins.
# Tighten allow_origins to your real frontend domain(s) in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware = cross-cutting logic that wraps EVERY request. This one logs
# method/path/status/latency for all endpoints in one place (DRY observability).
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    _log.info(
        "http_request",
        extra={"fields": {
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "latency_ms": round(elapsed_ms, 1),
        }},
    )
    return response


# Mount each feature's router. Order doesn't matter; paths are unique.
app.include_router(health.router)
app.include_router(tickets.router)
app.include_router(analytics.router)
