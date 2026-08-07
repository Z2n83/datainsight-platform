"""
System models: DataSyncLog, SystemSetting, Version, Notification.
Based on DATABASE_DESIGN.md §9.
"""
import uuid
from datetime import datetime, timezone, date
from typing import Optional

from sqlalchemy import String, Integer, Text, DateTime, Date, ForeignKey, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _new_uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DataSyncLog(Base):
    """Data sync execution log. DATABASE_DESIGN.md §9.3."""
    __tablename__ = "data_sync_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("data_sources.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    sync_method: Mapped[str] = mapped_column(String(20), nullable=False)
    records_synced: Mapped[int] = mapped_column(Integer, default=0)
    records_failed: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)

    # Relationships
    source: Mapped["DataSource"] = relationship("DataSource", lazy="selectin")  # noqa: F821

    def __repr__(self) -> str:
        return f"<DataSyncLog {self.source_id} {self.status}>"


class SystemSetting(Base):
    """Key-value system configuration. DATABASE_DESIGN.md §9.4."""
    __tablename__ = "system_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(20), default="string")
    description: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<SystemSetting {self.key}>"


class Version(Base):
    """System version and changelog. DATABASE_DESIGN.md §9.2."""
    __tablename__ = "versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    version_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    version_name: Mapped[Optional[str]] = mapped_column(String(50))
    release_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    changelog: Mapped[list] = mapped_column(JSON, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Version {self.version_number}>"


class Notification(Base):
    """In-app notification. DATABASE_DESIGN.md §9.5."""
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    recipient_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    alert_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("alerts.id"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False, index=True)

    # Relationships
    recipient: Mapped["User"] = relationship("User", lazy="selectin")  # noqa: F821
    alert: Mapped[Optional["Alert"]] = relationship("Alert", lazy="selectin")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Notification {self.title}>"
