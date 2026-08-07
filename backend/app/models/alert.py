"""
AlertRule and Alert models.
Based on DATABASE_DESIGN.md §6.1 and §6.2.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Boolean, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _new_uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    metric_id: Mapped[str] = mapped_column(String(36), ForeignKey("metrics.id"), nullable=False, index=True)
    condition: Mapped[str] = mapped_column(String(10), nullable=False)
    threshold: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    duration: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    assignee_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"))
    notify_methods: Mapped[dict] = mapped_column(JSON, default=lambda: ["system"])
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    cooldown: Mapped[int] = mapped_column(Integer, default=300)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    metric: Mapped["Metric"] = relationship("Metric", lazy="selectin")  # noqa: F821
    assignee: Mapped[Optional["User"]] = relationship("User", lazy="selectin")  # noqa: F821
    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="rule", lazy="selectin")

    def __repr__(self) -> str:
        return f"<AlertRule {self.name}>"


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    rule_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("alert_rules.id"), index=True)
    metric_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("metrics.id"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    level: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    current_value: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    threshold_value: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    assignee_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    processor_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"))
    process_note: Mapped[Optional[str]] = mapped_column(Text)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)

    # Relationships
    rule: Mapped[Optional["AlertRule"]] = relationship("AlertRule", back_populates="alerts", lazy="selectin")
    metric: Mapped[Optional["Metric"]] = relationship("Metric", lazy="selectin")  # noqa: F821
    assignee: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assignee_id], lazy="selectin")  # noqa: F821
    processor: Mapped[Optional["User"]] = relationship("User", foreign_keys=[processor_id], lazy="selectin")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Alert {self.title}>"
