"""
Data Sources router: /api/data-sources/*
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.data_source import DataSourceCreate, DataSourceUpdate
from app.services.data_source_service import DataSourceService
from app.utils.pagination import PaginatedResponse
from app.models.user import User

router = APIRouter()


@router.get("/")
async def list_sources(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: str | None = Query(default=None),
    type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """GET /api/data-sources — List data sources."""
    svc = DataSourceService(db)
    items, total = await svc.list_sources(
        page=page, page_size=page_size, keyword=keyword,
        source_type=type, status=status,
    )

    result = PaginatedResponse.create(
        items=[_source_to_dict(s) for s in items],
        total=total, page=page, page_size=page_size,
    )

    return {"code": 0, "message": "success", "data": result.model_dump()}


@router.post("/")
async def create_source(
    body: DataSourceCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """POST /api/data-sources — Create a data source."""
    svc = DataSourceService(db)
    source = await svc.create(body.model_dump())
    # Reload with owner
    source = await svc.get_by_id(source.id)
    return {"code": 0, "message": "success", "data": _source_to_dict(source)}


@router.get("/{source_id}")
async def get_source(
    source_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """GET /api/data-sources/:id — Get data source detail."""
    svc = DataSourceService(db)
    source = await svc.get_by_id(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="数据源不存在")
    return {"code": 0, "message": "success", "data": _source_to_dict(source)}


@router.put("/{source_id}")
async def update_source(
    source_id: str,
    body: DataSourceUpdate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """PUT /api/data-sources/:id — Update a data source."""
    svc = DataSourceService(db)
    source = await svc.get_by_id(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="数据源不存在")
    source = await svc.update(source, body.model_dump(exclude_none=True))
    return {"code": 0, "message": "success", "data": _source_to_dict(source)}


@router.delete("/{source_id}")
async def delete_source(
    source_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """DELETE /api/data-sources/:id — Soft delete a data source."""
    svc = DataSourceService(db)
    source = await svc.get_by_id(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="数据源不存在")
    await svc.soft_delete(source)
    return {"code": 0, "message": "已删除", "data": None}


@router.post("/{source_id}/test")
async def test_connection(
    source_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """POST /api/data-sources/:id/test — Test connection."""
    svc = DataSourceService(db)
    source = await svc.get_by_id(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="数据源不存在")
    result = await svc.test_connection(source)
    return {"code": 0, "message": "success", "data": result}


@router.post("/{source_id}/sync")
async def sync_source(
    source_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """POST /api/data-sources/:id/sync — Trigger manual sync."""
    svc = DataSourceService(db)
    source = await svc.get_by_id(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="数据源不存在")
    result = await svc.trigger_sync(source)
    return {"code": 0, "message": "success", "data": result}


def _source_to_dict(source) -> dict:
    """Convert DataSource ORM object to API response dict."""
    return {
        "id": source.id,
        "name": source.name,
        "type": source.type,
        "description": source.description,
        "status": source.status,
        "data_volume": source.data_volume,
        "sync_method": source.sync_method,
        "sync_frequency": source.sync_frequency,
        "last_sync_at": source.last_sync_at.isoformat() if source.last_sync_at else None,
        "last_sync_status": source.last_sync_status,
        "owner": {"id": source.owner.id, "real_name": source.owner.real_name} if source.owner else None,
        "created_at": source.created_at.isoformat() if source.created_at else None,
        "updated_at": source.updated_at.isoformat() if source.updated_at else None,
    }
