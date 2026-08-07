"""
Import all 24 models so SQLAlchemy Base.metadata discovers them for create_all().
Strictly follows DATABASE_DESIGN.md table list and migration order (§12.1).
"""
# 0001-0005: Users & Permissions
from app.models.user import User, Role, Permission

# 0006-0008: Data Management
from app.models.data_source import DataSource
from app.models.dataset import Dataset, DatasetField

# 0009: Devices
from app.models.device import Device

# 0010-0011: Metrics
from app.models.metric import Metric, MetricValue

# 0012-0013: Alerts
from app.models.alert import AlertRule, Alert

# 0014-0016: Inspections
from app.models.inspection import InspectionPlan, InspectionTask, InspectionRecord

# 0017-0018: Dashboards
from app.models.dashboard import Dashboard, DashboardWidget

# 0019: Reports
from app.models.report import Report

# 0020: Operation Logs
from app.models.operation_log import OperationLog

# 0021-0024: System Tables
from app.models.system import Version, DataSyncLog, SystemSetting, Notification

__all__ = [
    # Users & Permissions (5)
    "User", "Role", "Permission",
    # Data Management (3)
    "DataSource", "Dataset", "DatasetField",
    # Devices (1)
    "Device",
    # Metrics (2)
    "Metric", "MetricValue",
    # Alerts (2)
    "AlertRule", "Alert",
    # Inspections (3)
    "InspectionPlan", "InspectionTask", "InspectionRecord",
    # Dashboards (2)
    "Dashboard", "DashboardWidget",
    # Reports (1)
    "Report",
    # Operation Logs (1)
    "OperationLog",
    # System Tables (4)
    "Version", "DataSyncLog", "SystemSetting", "Notification",
]
