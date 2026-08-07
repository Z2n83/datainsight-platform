"""
Data Source business logic.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.data_source import DataSource


class DataSourceService:
    """CRUD and operations for data sources."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_sources(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        source_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> tuple[list[DataSource], int]:
        """Paginated list of data sources."""
        query = select(DataSource).where(DataSource.deleted_at.is_(None))

        if keyword:
            query = query.where(DataSource.name.contains(keyword))
        if source_type:
            query = query.where(DataSource.type == source_type)
        if status:
            query = query.where(DataSource.status == status)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = (
            query
            .options(selectinload(DataSource.owner))
            .order_by(DataSource.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_by_id(self, source_id: str) -> Optional[DataSource]:
        """Get a single data source by ID."""
        result = await self.db.execute(
            select(DataSource)
            .options(selectinload(DataSource.owner))
            .where(DataSource.id == source_id, DataSource.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> DataSource:
        """Create a new data source."""
        source = DataSource(
            name=data["name"],
            type=data["type"],
            description=data.get("description"),
            connection_config=data.get("connection_config", {}),
            sync_method=data.get("sync_method", "full"),
            sync_frequency=data.get("sync_frequency", "manual"),
            owner_id=data.get("owner_id"),
        )
        self.db.add(source)
        await self.db.flush()
        return source

    async def update(self, source: DataSource, data: dict) -> DataSource:
        """Update an existing data source (partial update)."""
        for field in ["name", "type", "description", "connection_config",
                       "sync_method", "sync_frequency", "owner_id"]:
            if field in data and data[field] is not None:
                setattr(source, field, data[field])
        source.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return source

    async def soft_delete(self, source: DataSource) -> None:
        """Soft delete a data source."""
        source.deleted_at = datetime.now(timezone.utc)
        source.updated_at = datetime.now(timezone.utc)
        await self.db.flush()

    async def test_connection(self, source: DataSource) -> dict:
        """Simulate connection test. Returns success/latency/message."""
        # In production this would actually connect. For MVP, simulate.
        import time, random
        start = time.time()
        # Simulate network latency
        await self.db.execute(select(DataSource).where(DataSource.id == source.id))
        latency = int((time.time() - start) * 1000) + random.randint(10, 80)

        # Simulate connection result
        if source.status == "error":
            return {"success": False, "latency_ms": latency, "message": "连接失败: 无法连接到主机"}
        return {"success": True, "latency_ms": latency, "message": "连接成功"}

    async def trigger_sync(self, source: DataSource) -> dict:
        """Trigger a manual sync for the data source."""
        source.status = "connected"
        source.last_sync_at = datetime.now(timezone.utc)
        source.last_sync_status = "success"
        source.data_volume = source.data_volume + 100  # Simulate new data
        source.updated_at = datetime.now(timezone.utc)
        await self.db.flush()

        return {
            "sync_log_id": str(uuid.uuid4()),
            "status": "success",
            "message": "同步完成",
        }
