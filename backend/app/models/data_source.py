"""
Data Source model.
Based on DATABASE_DESIGN.md §4.1.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _new_uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    connection_config: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="disconnected", nullable=False, index=True)
    data_volume: Mapped[int] = mapped_column(Integer, default=0)
    sync_method: Mapped[str] = mapped_column(String(20), default="full")
    sync_frequency: Mapped[Optional[str]] = mapped_column(String(50))
    sync_cron: Mapped[Optional[str]] = mapped_column(String(50))
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True)
    last_sync_status: Mapped[Optional[str]] = mapped_column(String(20))
    last_sync_error: Mapped[Optional[str]] = mapped_column(Text)
    owner_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    owner: Mapped[Optional["User"]] = relationship("User", lazy="selectin")  # noqa: F821
    datasets: Mapped[list["Dataset"]] = relationship("Dataset", back_populates="source", lazy="selectin")  # noqa: F821

    def __repr__(self) -> str:
        return f"<DataSource {self.name}>"
