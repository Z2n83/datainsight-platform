"""
Dashboard router: /api/dashboard/*
"""
from fastapi import APIRouter, Depends, Query

from app.core.database import get_db
from app.core.deps import get_current_user
from app.services.dashboard_service import DashboardService
from app.models.user import User

router = APIRouter()


@router.get("/overview")
async def overview(
    time_range: str = Query(default="7d", description="Time range: 7d / 30d / 90d"),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Get dashboard overview data (KPIs, trends, todos, status distribution).

    GET /api/dashboard/overview
    """
    days = {"7d": 7, "30d": 30, "90d": 90}.get(time_range, 7)
    svc = DashboardService(db)
    data = await svc.get_overview(days=days)

    return {
        "code": 0,
        "message": "success",
        "data": data,
    }
