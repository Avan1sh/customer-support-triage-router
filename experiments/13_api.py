"""Phase 5 - Module 1 - FastAPI surface, exercised in-process via TestClient.

TestClient runs the real ASGI app WITHOUT binding a network port - perfect for
demos and (later) pytest. Using it as a context manager runs the lifespan
(startup/shutdown) so init_db() fires.

Run from PROJECT ROOT:
    $env:PYTHONPATH="."; python experiments\\13_api.py
"""
import json
from fastapi.testclient import TestClient
from app.api.main import app

with TestClient(app) as client:
    # 1) Health check - no LLM, instant.
    print("GET /health ->", client.get("/health").json())

    # 2) Input guardrail: empty/too-short text is rejected with 422 BEFORE the
    #    request ever reaches the LLM. That is validation AND cost control.
    r = client.post("/tickets", json={"text": ""})
    print(f"POST /tickets (empty)   -> {r.status_code} (rejected pre-LLM, no cost)")

    # 3) A real ticket - full triage + route + escalation + draft.
    r = client.post(
        "/tickets",
        json={"text": "I was double charged for my subscription and want a refund."},
    )
    print(f"\nPOST /tickets (real)    -> {r.status_code}")
    print(json.dumps(r.json(), indent=2))

    # 4) An escalation case - draft_reply should be null.
    r = client.post(
        "/tickets",
        json={"text": "Third time reporting this and you keep ignoring me. "
                      "Cancelling and telling everyone on Twitter how terrible you are."},
    )
    body = r.json()
    print(f"\nPOST /tickets (angry)   -> {r.status_code}")
    print(f"  escalated   : {body['escalated']}  signals={body['escalation_signals']}")
    print(f"  draft_reply : {body['draft_reply']}  (None = human handles it)")
