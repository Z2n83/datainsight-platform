"""
Data Source Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class DataSourceCreate(BaseModel):
    """POST /api/data-sources request body."""
    name: str = Field(..., min_length=1, max_length=100, description="数据源名称")
    type: str = Field(..., description="类型: mysql / csv")
    description: Optional[str] = None
    connection_config: Dict[str, Any] = Field(..., description="连接配置")
    sync_method: str = Field(default="full", description="同步方式: full / incremental")
    sync_frequency: Optional[str] = Field(default="manual", description="同步频率")
    owner_id: Optional[str] = None


class DataSourceUpdate(BaseModel):
    """PUT /api/data-sources/:id request body."""
    name: Optional[str] = Field(None, max_length=100)
    type: Optional[str] = None
    description: Optional[str] = None
    connection_config: Optional[Dict[str, Any]] = None
    sync_method: Optional[str] = None
    sync_frequency: Optional[str] = None
    owner_id: Optional[str] = None


class OwnerInfo(BaseModel):
    id: str
    real_name: str

    class Config:
        from_attributes = True


class DataSourceOut(BaseModel):
    """GET data source response."""
    id: str
    name: str
    type: str
    description: Optional[str] = None
    status: str
    data_volume: int
    sync_method: str
    sync_frequency: Optional[str] = None
    last_sync_at: Optional[datetime] = None
    last_sync_status: Optional[str] = None
    owner: Optional[OwnerInfo] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConnectionTestResult(BaseModel):
    """POST /api/data-sources/:id/test response."""
    success: bool
    latency_ms: Optional[int] = None
    message: str


class SyncResult(BaseModel):
    """POST /api/data-sources/:id/sync response."""
    sync_log_id: str
    status: str
    message: str
