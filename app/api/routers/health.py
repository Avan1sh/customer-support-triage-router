"""Health/liveness endpoint - cheap, no LLM, no DB. Pinged by LBs/Docker/k8s."""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}
