"""
Dashboard overview schemas.
KPI data with real business logic (see PRODUCT_ARCHITECTURE.md §9.2).
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class KpiItem(BaseModel):
    """A single KPI card on the dashboard."""
    label: str
    value: float
    unit: str
    trend: float           # positive = up, negative = down (percentage)
    trend_label: str       # e.g. "+12.5%" or "-3.2%"


class TrendPoint(BaseModel):
    """A single point in a trend chart."""
    date: str
    value: float


class StatusDistribution(BaseModel):
    """Distribution of device statuses."""
    status: str
    count: int
    percentage: float


class RecentAlert(BaseModel):
    """Brief alert info for the dashboard todo section."""
    id: str
    title: str
    level: str
    triggered_at: datetime


class TodoSection(BaseModel):
    """Pending tasks summary."""
    pending_alerts: int
    pending_inspections: int
    data_source_errors: int
    data_quality_issues: int


class DashboardOverview(BaseModel):
    """GET /api/dashboard/overview response data."""
    kpi: List[KpiItem]
    data_volume_trend: List[TrendPoint]
    device_status_distribution: List[StatusDistribution]
    anomaly_trend: List[TrendPoint]
    todos: TodoSection
    recent_alerts: List[RecentAlert]
