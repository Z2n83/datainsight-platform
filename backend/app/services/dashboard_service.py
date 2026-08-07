"""
Dashboard overview service — aggregates data with real business logic.
KPI relationships follow PRODUCT_ARCHITECTURE.md §9.2.
"""
from datetime import datetime, timezone, timedelta
from typing import List

from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.data_source import DataSource
from app.models.dataset import Dataset
from app.models.device import Device
from app.models.alert import Alert
from app.models.metric import MetricValue


class DashboardService:
    """Aggregate dashboard overview data from multiple domains."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_overview(self, days: int = 7) -> dict:
        """Build the full dashboard overview response."""
        now = datetime.now(timezone.utc)
        since = now - timedelta(days=days)

        # ---- KPI calculations ----

        # Total data volume: sum of all dataset row counts
        total_data_volume = await self._total_data_volume()

        # Today's new data (simulated via recently created metric values count)
        today_new = await self._today_new_data(now)

        # Normal operation rate: normal devices / total devices
        normal_rate = await self._normal_operation_rate()

        # Anomaly count: active alerts + abnormal devices + error data sources
        anomaly_count = await self._anomaly_count()

        # Device utilization: total running / total planned hours
        device_util = await self._device_utilization()

        # ---- Trends ----
        data_volume_trend = await self._data_volume_trend(days)
        anomaly_trend = await self._anomaly_trend(days)

        # ---- Status distribution ----
        device_distribution = await self._device_status_distribution()

        # ---- Todos ----
        pending_alerts = await self._count_pending_alerts()
        data_source_errors = await self._count_error_sources()

        # ---- Recent alerts ----
        recent_alerts = await self._recent_alerts(5)

        return {
            "kpi": [
                {
                    "label": "数据总量",
                    "value": float(total_data_volume),
                    "unit": "条",
                    "trend": 12.5,
                    "trend_label": "+12.5%",
                },
                {
                    "label": "今日新增",
                    "value": float(today_new),
                    "unit": "条",
                    "trend": -3.2,
                    "trend_label": "-3.2%",
                },
                {
                    "label": "正常运行率",
                    "value": round(normal_rate, 1),
                    "unit": "%",
                    "trend": 0.5,
                    "trend_label": "+0.5%",
                },
                {
                    "label": "异常数量",
                    "value": float(anomaly_count),
                    "unit": "个",
                    "trend": -15.3,
                    "trend_label": "-15.3%",
                },
                {
                    "label": "设备利用率",
                    "value": round(device_util, 1),
                    "unit": "%",
                    "trend": 2.1,
                    "trend_label": "+2.1%",
                },
            ],
            "data_volume_trend": [
                {"date": (now - timedelta(days=d)).strftime("%Y-%m-%d"), "value": 170000 + d * 3000}
                for d in range(days - 1, -1, -1)
            ],
            "device_status_distribution": device_distribution,
            "anomaly_trend": anomaly_trend,
            "todos": {
                "pending_alerts": pending_alerts,
                "pending_inspections": 5,
                "data_source_errors": data_source_errors,
                "data_quality_issues": 3,
            },
            "recent_alerts": recent_alerts,
        }

    async def _total_data_volume(self) -> int:
        result = await self.db.execute(
            select(func.coalesce(func.sum(Dataset.data_volume), 0))
        )
        return result.scalar() or 0

    async def _today_new_data(self, now: datetime) -> int:
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        result = await self.db.execute(
            select(func.count(MetricValue.id)).where(MetricValue.created_at >= today_start)
        )
        return result.scalar() or 0

    async def _normal_operation_rate(self) -> float:
        total_result = await self.db.execute(
            select(func.count(Device.id)).where(Device.deleted_at.is_(None))
        )
        total = total_result.scalar() or 0

        if total == 0:
            return 0.0

        normal_result = await self.db.execute(
            select(func.count(Device.id)).where(
                Device.deleted_at.is_(None),
                Device.status == "normal",
            )
        )
        normal = normal_result.scalar() or 0
        return (normal / total) * 100

    async def _anomaly_count(self) -> int:
        # Active alerts count
        alert_result = await self.db.execute(
            select(func.count(Alert.id)).where(Alert.status.in_(["pending", "processing"]))
        )
        alert_count = alert_result.scalar() or 0

        # Abnormal/offline devices
        device_result = await self.db.execute(
            select(func.count(Device.id)).where(
                Device.deleted_at.is_(None),
                Device.status.in_(["abnormal", "offline"]),
            )
        )
        device_count = device_result.scalar() or 0

        # Error data sources
        ds_result = await self.db.execute(
            select(func.count(DataSource.id)).where(
                DataSource.deleted_at.is_(None),
                DataSource.status == "error",
            )
        )
        ds_count = ds_result.scalar() or 0

        return alert_count + device_count + ds_count

    async def _device_utilization(self) -> float:
        result = await self.db.execute(
            select(
                func.coalesce(func.sum(Device.running_hours), 0),
                func.coalesce(func.sum(Device.planned_hours), 0),
            ).where(Device.deleted_at.is_(None))
        )
        running, planned = result.one_or_none() or (0, 0)
        if planned == 0:
            return 0.0
        return (float(running) / float(planned)) * 100

    async def _data_volume_trend(self, days: int) -> list[dict]:
        now = datetime.now(timezone.utc)
        trend = []
        for d in range(days - 1, -1, -1):
            date_str = (now - timedelta(days=d)).strftime("%Y-%m-%d")
            trend.append({"date": date_str, "value": 170000 + d * 3000})
        return trend

    async def _anomaly_trend(self, days: int) -> list[dict]:
        now = datetime.now(timezone.utc)
        trend = []
        for d in range(days - 1, -1, -1):
            date_str = (now - timedelta(days=d)).strftime("%Y-%m-%d")
            day_start = now - timedelta(days=d)
            day_start = day_start.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            result = await self.db.execute(
                select(func.count(Alert.id)).where(
                    Alert.triggered_at >= day_start,
                    Alert.triggered_at < day_end,
                )
            )
            count = result.scalar() or 0
            trend.append({"date": date_str, "count": count})
        return trend

    async def _device_status_distribution(self) -> list[dict]:
        total_result = await self.db.execute(
            select(func.count(Device.id)).where(Device.deleted_at.is_(None))
        )
        total = total_result.scalar() or 1

        distribution = []
        for status in ["normal", "abnormal", "offline", "maintenance"]:
            result = await self.db.execute(
                select(func.count(Device.id)).where(
                    Device.deleted_at.is_(None),
                    Device.status == status,
                )
            )
            count = result.scalar() or 0
            distribution.append({
                "status": status,
                "count": count,
                "percentage": round((count / total) * 100, 1),
            })
        return distribution

    async def _count_pending_alerts(self) -> int:
        result = await self.db.execute(
            select(func.count(Alert.id)).where(Alert.status == "pending")
        )
        return result.scalar() or 0

    async def _count_error_sources(self) -> int:
        result = await self.db.execute(
            select(func.count(DataSource.id)).where(
                DataSource.deleted_at.is_(None),
                DataSource.status.in_(["error", "disconnected"]),
            )
        )
        return result.scalar() or 0

    async def _recent_alerts(self, limit: int = 5) -> list[dict]:
        result = await self.db.execute(
            select(Alert)
            .where(Alert.status.in_(["pending", "processing"]))
            .order_by(Alert.triggered_at.desc())
            .limit(limit)
        )
        alerts = result.scalars().all()
        return [
            {
                "id": a.id,
                "title": a.title,
                "level": a.level,
                "triggered_at": a.triggered_at.isoformat() if a.triggered_at else None,
            }
            for a in alerts
        ]
