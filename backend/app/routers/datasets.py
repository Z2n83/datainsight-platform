"""
Datasets router: /api/datasets/*
"""
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.dataset import DatasetCreate, DatasetUpdate
from app.services.dataset_service import DatasetService
from app.utils.pagination import PaginatedResponse
from app.models.user import User

router = APIRouter()


@router.get("/")
async def list_datasets(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: str | None = Query(default=None),
    source_id: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """GET /api/datasets — List datasets."""
    svc = DatasetService(db)
    items, total = await svc.list_datasets(
        page=page, page_size=page_size, keyword=keyword, source_id=source_id,
    )

    result = PaginatedResponse.create(
        items=[_dataset_to_dict(d) for d in items],
        total=total, page=page, page_size=page_size,
    )

    return {"code": 0, "message": "success", "data": result.model_dump()}


@router.post("/")
async def create_dataset(
    body: DatasetCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """POST /api/datasets — Create a dataset."""
    svc = DatasetService(db)
    dataset = await svc.create(body.model_dump())
    dataset = await svc.get_by_id(dataset.id)
    return {"code": 0, "message": "success", "data": _dataset_to_dict(dataset)}


@router.get("/{dataset_id}")
async def get_dataset(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """GET /api/datasets/:id — Get dataset detail with fields."""
    svc = DatasetService(db)
    dataset = await svc.get_by_id(dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="数据集不存在")
    return {"code": 0, "message": "success", "data": _dataset_to_dict(dataset)}


@router.put("/{dataset_id}")
async def update_dataset(
    dataset_id: str,
    body: DatasetUpdate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """PUT /api/datasets/:id — Update a dataset."""
    svc = DatasetService(db)
    dataset = await svc.get_by_id(dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="数据集不存在")
    dataset = await svc.update(dataset, body.model_dump(exclude_none=True))
    dataset = await svc.get_by_id(dataset.id)
    return {"code": 0, "message": "success", "data": _dataset_to_dict(dataset)}


@router.delete("/{dataset_id}")
async def delete_dataset(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """DELETE /api/datasets/:id — Soft delete a dataset."""
    svc = DatasetService(db)
    dataset = await svc.get_by_id(dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="数据集不存在")
    await svc.soft_delete(dataset)
    return {"code": 0, "message": "已删除", "data": None}


@router.get("/{dataset_id}/preview")
async def preview_dataset(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """GET /api/datasets/:id/preview — Preview dataset data."""
    svc = DatasetService(db)
    dataset = await svc.get_by_id(dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="数据集不存在")
    preview = await svc.get_preview(dataset)
    return {"code": 0, "message": "success", "data": preview}


def _dataset_to_dict(dataset) -> dict:
    """Convert Dataset ORM object to API response dict."""
    return {
        "id": dataset.id,
        "name": dataset.name,
        "description": dataset.description,
        "source": {"id": dataset.source.id, "name": dataset.source.name} if dataset.source else None,
        "source_table": dataset.source_table,
        "field_count": dataset.field_count,
        "data_volume": dataset.data_volume,
        "last_refresh_at": dataset.last_refresh_at.isoformat() if dataset.last_refresh_at else None,
        "owner": {"id": dataset.owner.id, "real_name": dataset.owner.real_name} if dataset.owner else None,
        "fields": [
            {
                "id": f.id,
                "field_name": f.field_name,
                "field_alias": f.field_alias,
                "field_type": f.field_type,
                "is_dimension": f.is_dimension,
                "is_metric": f.is_metric,
                "aggregation": f.aggregation,
                "unit": f.unit,
                "sort_order": f.sort_order,
            }
            for f in (dataset.fields or [])
        ],
        "created_at": dataset.created_at.isoformat() if dataset.created_at else None,
        "updated_at": dataset.updated_at.isoformat() if dataset.updated_at else None,
    }
