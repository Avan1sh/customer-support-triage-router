"""Phase 5 - Module 2 - read + analytics endpoints (via TestClient).

Run from PROJECT ROOT:
    $env:PYTHONPATH="."; python experiments\\14_api_read.py
"""
import json
from fastapi.testclient import TestClient
from app.api.main import app

with TestClient(app) as client:
    # Seed a couple of fresh tickets so the read endpoints have data.
    for text in ["My invoice is wrong again this month.", "The app crashes on login."]:
        client.post("/tickets", json={"text": text})

    # 1) GET list (paginated).
    print("GET /tickets?limit=5 ->")
    listing = client.get("/tickets", params={"limit": 5}).json()
    for t in listing:
        print(f"  #{t['id']:>3} [{t['priority']:<8}/{t['category']:<14}] "
              f"{t['status']:<8} {t['assigned_team']}")

    # 2) GET one by id (use the first from the list, so it always exists).
    first_id = listing[0]["id"]
    print(f"\nGET /tickets/{first_id} ->")
    print(json.dumps(client.get(f"/tickets/{first_id}").json(), indent=2, default=str))

    # 3) GET a missing id -> 404.
    print("\nGET /tickets/999999 ->", client.get("/tickets/999999").status_code, "(not found)")

    # 4) GET analytics (SQL GROUP BY aggregations).
    print("\nGET /analytics ->")
    print(json.dumps(client.get("/analytics").json(), indent=2))
