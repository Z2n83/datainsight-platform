"""
Alerts router: /api/alerts/*
"""
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.alert import ProcessAlertRequest, CloseAlertRequest
from app.services.alert_service import AlertService
from app.utils.pagination import PaginatedResponse
from app.models.user import User

router = APIRouter()


@router.get("/")
async def list_alerts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    level: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """GET /api/alerts — List alerts with optional filters."""
    svc = AlertService(db)
    items, total, stats = await svc.list_alerts(
        page=page, page_size=page_size, status=status, level=level,
    )

    result = PaginatedResponse.create(
        items=[_alert_to_dict(a) for a in items],
        total=total, page=page, page_size=page_size,
    )

    return {
        "code": 0,
        "message": "success",
        "data": {
            **result.model_dump(),
            "statistics": stats,
        },
    }


@router.get("/{alert_id}")
async def get_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """GET /api/alerts/:id — Get alert detail."""
    svc = AlertService(db)
    alert = await svc.get_by_id(alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="预警不存在")
    return {"code": 0, "message": "success", "data": _alert_to_dict(alert)}


@router.put("/{alert_id}/process")
async def process_alert(
    alert_id: str,
    body: ProcessAlertRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """PUT /api/alerts/:id/process — Mark alert as processing."""
    svc = AlertService(db)
    alert = await svc.get_by_id(alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="预警不存在")
    alert = await svc.process_alert(alert, body.note)
    return {"code": 0, "message": "success", "data": _alert_to_dict(alert)}


@router.put("/{alert_id}/close")
async def close_alert(
    alert_id: str,
    body: CloseAlertRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """PUT /api/alerts/:id/close — Close an alert."""
    svc = AlertService(db)
    alert = await svc.get_by_id(alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="预警不存在")
    alert = await svc.close_alert(alert, body.process_note, body.resolution)
    return {"code": 0, "message": "success", "data": _alert_to_dict(alert)}


def _alert_to_dict(alert) -> dict:
    """Convert Alert ORM object to API response dict."""
    return {
        "id": alert.id,
        "title": alert.title,
        "description": alert.description,
        "level": alert.level,
        "status": alert.status,
        "current_value": float(alert.current_value) if alert.current_value else None,
        "threshold_value": float(alert.threshold_value) if alert.threshold_value else None,
        "triggered_at": alert.triggered_at.isoformat() if alert.triggered_at else None,
        "rule": {
            "id": alert.rule.id,
            "name": alert.rule.name,
        } if alert.rule else None,
        "assignee": {
            "id": alert.assignee.id,
            "real_name": alert.assignee.real_name,
        } if alert.assignee else None,
        "processed_at": alert.processed_at.isoformat() if alert.processed_at else None,
        "closed_at": alert.closed_at.isoformat() if alert.closed_at else None,
    }
