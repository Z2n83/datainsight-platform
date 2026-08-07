"""
Dataset Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DatasetFieldCreate(BaseModel):
    """Field definition when creating a dataset."""
    field_name: str
    field_alias: Optional[str] = None
    field_type: str
    is_dimension: bool = False
    is_metric: bool = False
    aggregation: Optional[str] = None
    unit: Optional[str] = None
    sort_order: int = 0


class DatasetCreate(BaseModel):
    """POST /api/datasets request body."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    source_id: str
    source_table: str
    query_config: Optional[Dict[str, Any]] = None
    fields: List[DatasetFieldCreate] = []
    owner_id: Optional[str] = None


class DatasetUpdate(BaseModel):
    """PUT /api/datasets/:id request body."""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    query_config: Optional[Dict[str, Any]] = None
    fields: Optional[List[DatasetFieldCreate]] = None
    owner_id: Optional[str] = None


class DatasetFieldOut(BaseModel):
    """Dataset field in response."""
    id: str
    field_name: str
    field_alias: Optional[str] = None
    field_type: str
    is_dimension: bool
    is_metric: bool
    aggregation: Optional[str] = None
    unit: Optional[str] = None
    sort_order: int

    class Config:
        from_attributes = True


class SourceBrief(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True


class DatasetOut(BaseModel):
    """GET dataset response."""
    id: str
    name: str
    description: Optional[str] = None
    source: Optional[SourceBrief] = None
    source_table: str
    field_count: int
    data_volume: int
    last_refresh_at: Optional[datetime] = None
    owner: Optional["OwnerInfo"] = None  # noqa: F821
    fields: List[DatasetFieldOut] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DatasetPreview(BaseModel):
    """GET /api/datasets/:id/preview response."""
    fields: List[str]
    rows: List[List[Any]]
    total_rows: int
