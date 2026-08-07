"""
Alert business logic.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.alert import Alert, AlertRule


class AlertService:
    """Alert query and processing."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_alerts(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        level: Optional[str] = None,
    ) -> tuple[list[Alert], int, dict]:
        """Paginated list of alerts with statistics."""
        query = select(Alert)

        if status:
            query = query.where(Alert.status == status)
        if level:
            query = query.where(Alert.level == level)

        # Statistics by level
        stats = {}
        for lvl in ["critical", "high", "medium", "low"]:
            stat_query = select(func.count(Alert.id)).where(Alert.level == lvl)
            if status:
                stat_query = stat_query.where(Alert.status == status)
            result = await self.db.execute(stat_query)
            stats[lvl] = result.scalar() or 0

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = (
            query
            .options(
                selectinload(Alert.rule),
                selectinload(Alert.assignee),
                selectinload(Alert.metric),
            )
            .order_by(Alert.triggered_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total, stats

    async def get_by_id(self, alert_id: str) -> Optional[Alert]:
        """Get a single alert with all relations loaded."""
        result = await self.db.execute(
            select(Alert)
            .options(
                selectinload(Alert.rule),
                selectinload(Alert.assignee),
                selectinload(Alert.processor),
                selectinload(Alert.metric),
            )
            .where(Alert.id == alert_id)
        )
        return result.scalar_one_or_none()

    async def process_alert(self, alert: Alert, note: Optional[str] = None) -> Alert:
        """Mark an alert as processing."""
        alert.status = "processing"
        alert.process_note = note
        alert.processed_at = datetime.now(timezone.utc)
        alert.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return alert

    async def close_alert(
        self,
        alert: Alert,
        process_note: Optional[str] = None,
        resolution: Optional[str] = None,
    ) -> Alert:
        """Close an alert."""
        alert.status = "closed"
        alert.process_note = process_note
        alert.closed_at = datetime.now(timezone.utc)
        alert.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return alert
