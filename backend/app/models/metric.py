"""
Metric and MetricValue models.
Based on DATABASE_DESIGN.md §5.2 and §5.3.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _new_uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Metric(Base):
    __tablename__ = "metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    dataset_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("datasets.id"), index=True)
    device_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("devices.id"))
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    aggregation: Mapped[str] = mapped_column(String(20), nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(20))
    decimal_places: Mapped[int] = mapped_column(Integer, default=2)
    is_key_metric: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)

    # Relationships
    dataset: Mapped[Optional["Dataset"]] = relationship("Dataset", lazy="selectin")  # noqa: F821
    device: Mapped[Optional["Device"]] = relationship("Device", lazy="selectin")  # noqa: F821
    values: Mapped[list["MetricValue"]] = relationship("MetricValue", back_populates="metric", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Metric {self.name}>"


class MetricValue(Base):
    __tablename__ = "metric_values"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    metric_id: Mapped[str] = mapped_column(String(36), ForeignKey("metrics.id"), nullable=False, index=True)
    time_bucket: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    granularity: Mapped[str] = mapped_column(String(10), nullable=False)
    value: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    dimension_key: Mapped[Optional[str]] = mapped_column(String(100))
    dimension_value: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)

    # Relationships
    metric: Mapped["Metric"] = relationship("Metric", back_populates="values", lazy="selectin")

    def __repr__(self) -> str:
        return f"<MetricValue {self.metric_id} @ {self.time_bucket}>"
