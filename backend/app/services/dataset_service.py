"""
Dataset business logic.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.dataset import Dataset, DatasetField


class DatasetService:
    """CRUD and operations for datasets."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_datasets(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        source_id: Optional[str] = None,
    ) -> tuple[list[Dataset], int]:
        """Paginated list of datasets."""
        query = select(Dataset).where(Dataset.deleted_at.is_(None))

        if keyword:
            query = query.where(Dataset.name.contains(keyword))
        if source_id:
            query = query.where(Dataset.source_id == source_id)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = (
            query
            .options(selectinload(Dataset.source), selectinload(Dataset.owner))
            .order_by(Dataset.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_by_id(self, dataset_id: str) -> Optional[Dataset]:
        """Get a single dataset with fields loaded."""
        result = await self.db.execute(
            select(Dataset)
            .options(
                selectinload(Dataset.source),
                selectinload(Dataset.owner),
                selectinload(Dataset.fields),
            )
            .where(Dataset.id == dataset_id, Dataset.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> Dataset:
        """Create a new dataset with fields."""
        fields_data = data.pop("fields", [])

        dataset = Dataset(
            name=data["name"],
            description=data.get("description"),
            source_id=data["source_id"],
            source_table=data["source_table"],
            query_config=data.get("query_config"),
            field_count=len(fields_data),
            owner_id=data.get("owner_id"),
        )
        self.db.add(dataset)
        await self.db.flush()

        # Create fields
        for i, fd in enumerate(fields_data):
            field = DatasetField(
                dataset_id=dataset.id,
                field_name=fd["field_name"],
                field_alias=fd.get("field_alias"),
                field_type=fd["field_type"],
                is_dimension=fd.get("is_dimension", False),
                is_metric=fd.get("is_metric", False),
                aggregation=fd.get("aggregation"),
                unit=fd.get("unit"),
                sort_order=fd.get("sort_order", i),
            )
            self.db.add(field)

        await self.db.flush()
        return dataset

    async def update(self, dataset: Dataset, data: dict) -> Dataset:
        """Update an existing dataset (partial update)."""
        fields_data = data.pop("fields", None)

        for field in ["name", "description", "query_config", "owner_id"]:
            if field in data and data[field] is not None:
                setattr(dataset, field, data[field])

        if fields_data is not None:
            # Remove old fields
            for f in list(dataset.fields):
                await self.db.delete(f)
            # Create new fields
            for i, fd in enumerate(fields_data):
                new_field = DatasetField(
                    dataset_id=dataset.id,
                    field_name=fd["field_name"],
                    field_alias=fd.get("field_alias"),
                    field_type=fd["field_type"],
                    is_dimension=fd.get("is_dimension", False),
                    is_metric=fd.get("is_metric", False),
                    aggregation=fd.get("aggregation"),
                    unit=fd.get("unit"),
                    sort_order=fd.get("sort_order", i),
                )
                self.db.add(new_field)
            dataset.field_count = len(fields_data)

        dataset.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return dataset

    async def soft_delete(self, dataset: Dataset) -> None:
        """Soft delete a dataset."""
        dataset.deleted_at = datetime.now(timezone.utc)
        dataset.updated_at = datetime.now(timezone.utc)
        await self.db.flush()

    async def get_preview(self, dataset: Dataset, limit: int = 100) -> dict:
        """Get a preview of dataset fields and sample rows."""
        fields = [f.field_name for f in dataset.fields]
        # In production, query the actual source table.
        # For MVP, return simulated preview data.
        rows = []
        for i in range(min(limit, 10)):  # Simulate 10 rows
            row = [f"sample_{i}_{f}" for f in fields]
            rows.append(row)

        return {
            "fields": fields,
            "rows": rows,
            "total_rows": min(limit, 10),
        }
