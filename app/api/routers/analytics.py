"""Analytics endpoint - aggregate counts for a dashboard.

All aggregation is done in SQL (GROUP BY) inside the repository, NOT by
pulling rows into Python. This is the data layer for the Phase 4 analytics.
"""
from fastapi import APIRouter, Depends

from app.db.repository import TicketRepository
from app.api.dependencies import get_ticket_repository
from app.api.schemas import AnalyticsResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsResponse)
def analytics(
    repo: TicketRepository = Depends(get_ticket_repository),
) -> AnalyticsResponse:
    return AnalyticsResponse(
        total=repo.total_count(),
        by_priority=repo.count_by_priority(),
        by_category=repo.count_by_category(),
        by_status=repo.count_by_status(),
        by_team=repo.count_by_team(),
    )
