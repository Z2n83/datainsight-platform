"""
Device model.
Based on DATABASE_DESIGN.md §5.1.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, DateTime, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _new_uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    device_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    device_name: Mapped[str] = mapped_column(String(100), nullable=False)
    device_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    department: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="normal", nullable=False, index=True)
    running_hours: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    planned_hours: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    last_heartbeat_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    metadata_info: Mapped[Optional[dict]] = mapped_column(JSON, name="metadata")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<Device {self.device_code}>"
