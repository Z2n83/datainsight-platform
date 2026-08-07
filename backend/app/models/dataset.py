"""
Dataset and DatasetField models.
Based on DATABASE_DESIGN.md §4.2 and §4.3.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _new_uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("data_sources.id"), nullable=False, index=True)
    source_table: Mapped[str] = mapped_column(String(100), nullable=False)
    query_config: Mapped[Optional[dict]] = mapped_column(JSON)
    field_count: Mapped[int] = mapped_column(Integer, default=0)
    data_volume: Mapped[int] = mapped_column(Integer, default=0)
    last_refresh_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    owner_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    source: Mapped["DataSource"] = relationship("DataSource", back_populates="datasets", lazy="selectin")  # noqa: F821
    owner: Mapped[Optional["User"]] = relationship("User", lazy="selectin")  # noqa: F821
    fields: Mapped[list["DatasetField"]] = relationship(
        "DatasetField", back_populates="dataset", lazy="selectin", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Dataset {self.name}>"


class DatasetField(Base):
    __tablename__ = "dataset_fields"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    dataset_id: Mapped[str] = mapped_column(String(36), ForeignKey("datasets.id"), nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    field_alias: Mapped[Optional[str]] = mapped_column(String(100))
    field_type: Mapped[str] = mapped_column(String(30), nullable=False)
    is_dimension: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_metric: Mapped[bool] = mapped_column(Boolean, default=False)
    aggregation: Mapped[Optional[str]] = mapped_column(String(20))
    unit: Mapped[Optional[str]] = mapped_column(String(20))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)

    # Relationships
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="fields", lazy="selectin")

    def __repr__(self) -> str:
        return f"<DatasetField {self.field_name}>"
