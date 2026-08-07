"""
Inspection models: plans, tasks, records.
Based on DATABASE_DESIGN.md §7.
"""
import uuid
from datetime import datetime, timezone, date
from typing import Optional, List

from sqlalchemy import String, Integer, Text, DateTime, Date, ForeignKey, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _new_uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class InspectionPlan(Base):
    __tablename__ = "inspection_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    scope: Mapped[str] = mapped_column(String(50), nullable=False)
    scope_config: Mapped[Optional[dict]] = mapped_column(JSON)
    device_ids: Mapped[Optional[list]] = mapped_column(JSON)  # UUID[] → JSON for MySQL
    inspection_metrics: Mapped[Optional[dict]] = mapped_column(JSON)
    assignee_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"))
    frequency: Mapped[str] = mapped_column(String(20), nullable=False)
    cron_expression: Mapped[Optional[str]] = mapped_column(String(50))
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    creator_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    assignee: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assignee_id], lazy="selectin")  # noqa: F821
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[creator_id], lazy="selectin")  # noqa: F821
    tasks: Mapped[List["InspectionTask"]] = relationship(
        "InspectionTask", back_populates="plan", lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<InspectionPlan {self.name}>"


class InspectionTask(Base):
    __tablename__ = "inspection_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    plan_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("inspection_plans.id"), index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    scope: Mapped[str] = mapped_column(String(50), nullable=False)
    scope_config: Mapped[Optional[dict]] = mapped_column(JSON)
    assignee_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    overall_result: Mapped[Optional[str]] = mapped_column(String(20))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)

    # Relationships
    plan: Mapped[Optional["InspectionPlan"]] = relationship("InspectionPlan", back_populates="tasks", lazy="selectin")
    assignee: Mapped[Optional["User"]] = relationship("User", lazy="selectin")  # noqa: F821
    records: Mapped[List["InspectionRecord"]] = relationship(
        "InspectionRecord", back_populates="task", lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<InspectionTask {self.name}>"


class InspectionRecord(Base):
    __tablename__ = "inspection_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("inspection_tasks.id"), nullable=False, index=True)
    device_id: Mapped[str] = mapped_column(String(36), ForeignKey("devices.id"), nullable=False, index=True)
    inspector_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"))
    result: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    detail: Mapped[Optional[dict]] = mapped_column(JSON)
    anomaly_desc: Mapped[Optional[str]] = mapped_column(Text)
    images: Mapped[Optional[list]] = mapped_column(JSON)
    inspected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)

    # Relationships
    task: Mapped["InspectionTask"] = relationship("InspectionTask", back_populates="records", lazy="selectin")
    device: Mapped["Device"] = relationship("Device", lazy="selectin")  # noqa: F821
    inspector: Mapped[Optional["User"]] = relationship("User", lazy="selectin")  # noqa: F821

    def __repr__(self) -> str:
        return f"<InspectionRecord {self.id}>"
