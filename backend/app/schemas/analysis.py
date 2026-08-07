"""
Analysis request/response schemas.
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class MetricConfig(BaseModel):
    """A single metric to analyze."""
    field_name: str
    aggregation: str = "avg"  # sum, avg, count, max, min


class FilterCondition(BaseModel):
    """A single filter condition."""
    field: str
    operator: str = "eq"  # eq, neq, gt, gte, lt, lte, like, in
    value: Any


class TimeRange(BaseModel):
    """Time range for analysis."""
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    preset: Optional[str] = None  # last_7_days, last_30_days, last_90_days


class AnalysisRequest(BaseModel):
    """POST /api/analysis/execute request body."""
    dataset_id: str = Field(..., description="数据集 ID")
    metrics: List[MetricConfig] = Field(..., min_length=1, description="分析指标列表")
    dimensions: List[str] = Field(default=["time"], description="分析维度")
    time_range: Optional[TimeRange] = None
    granularity: str = Field(default="day", description="时间粒度: hour/day/week/month")
    filters: List[FilterCondition] = []
    analysis_type: str = Field(default="trend", description="分析类型: trend/compare/anomaly/ranking")
    limit: int = Field(default=100, description="返回结果数量上限")


class AnalysisSummary(BaseModel):
    """Statistical summary of analysis results."""
    avg: Optional[float] = None
    max: Optional[float] = None
    min: Optional[float] = None
    trend: Optional[str] = None  # up, down, stable
    change_rate: Optional[float] = None


class AnalysisResult(BaseModel):
    """POST /api/analysis/execute response data."""
    chart_data: List[dict]
    summary: AnalysisSummary
    insights: List[str]
    table_data: dict  # {columns: [...], rows: [[...], ...]}
    execution_time_ms: int
