"""
Alert-related Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class AlertRuleOut(BaseModel):
    """Alert rule in list/detail response."""
    id: str
    name: str
    description: Optional[str] = None
    metric_id: str
    condition: str
    threshold: float
    duration: int
    level: str
    enabled: bool
    notify_methods: List[str] = []
    cooldown: int
    created_at: datetime

    class Config:
        from_attributes = True


class AlertOut(BaseModel):
    """Alert in list/detail response."""
    id: str
    title: str
    description: Optional[str] = None
    level: str
    status: str
    current_value: float
    threshold_value: float
    triggered_at: datetime
    rule: Optional[AlertRuleOut] = None
    assignee: Optional["AssigneeInfo"] = None  # noqa: F821
    processed_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AssigneeInfo(BaseModel):
    """Brief user info for alert assignee."""
    id: str
    real_name: str

    class Config:
        from_attributes = True


class ProcessAlertRequest(BaseModel):
    """PUT /api/alerts/:id/process request body."""
    note: Optional[str] = None


class CloseAlertRequest(BaseModel):
    """PUT /api/alerts/:id/close request body."""
    process_note: Optional[str] = None
    resolution: Optional[str] = None


class AlertStatistics(BaseModel):
    """Alert count by level."""
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
