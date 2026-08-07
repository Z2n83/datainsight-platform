"""
Seed script: populate ALL 24 tables with demo data.
Strictly follows DATABASE_DESIGN.md §12.2 seed data requirements.
Run: python seed_data.py
"""
import asyncio
import uuid
from datetime import datetime, timezone, timedelta, date

from app.core.database import AsyncSessionLocal, init_db
from app.core.security import hash_password

# Import all models
from app.models.user import User, Role, Permission, user_roles_table, role_permissions_table
from app.models.data_source import DataSource
from app.models.dataset import Dataset, DatasetField
from app.models.device import Device
from app.models.metric import Metric, MetricValue
from app.models.alert import AlertRule, Alert
from app.models.inspection import InspectionPlan, InspectionTask, InspectionRecord
from app.models.dashboard import Dashboard, DashboardWidget
from app.models.report import Report
from app.models.operation_log import OperationLog
from app.models.system import Version, DataSyncLog, SystemSetting, Notification


def _uid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ===================================================================
# Permission definitions (module:page:action — 26 permissions)
# ===================================================================
PERMISSIONS = [
    ("查看运营总览", "dashboard:overview:view", "dashboard", "overview", "view"),
    ("查看数据源列表", "datasource:list:view", "datasource", "list", "view"),
    ("新增数据源", "datasource:list:create", "datasource", "list", "create"),
    ("编辑数据源", "datasource:detail:edit", "datasource", "detail", "edit"),
    ("删除数据源", "datasource:detail:delete", "datasource", "detail", "delete"),
    ("查看数据集列表", "dataset:list:view", "dataset", "list", "view"),
    ("新增数据集", "dataset:list:create", "dataset", "list", "create"),
    ("编辑数据集", "dataset:detail:edit", "dataset", "detail", "edit"),
    ("删除数据集", "dataset:detail:delete", "dataset", "detail", "delete"),
    ("查看数据质量", "dataquality:report:view", "dataquality", "report", "view"),
    ("执行数据分析", "analysis:execute:view", "analysis", "execute", "view"),
    ("查看看板列表", "dashboard:list:view", "dashboard", "list", "view"),
    ("创建看板", "dashboard:list:create", "dashboard", "list", "create"),
    ("编辑看板", "dashboard:detail:edit", "dashboard", "detail", "edit"),
    ("查看预警列表", "alert:list:view", "alert", "list", "view"),
    ("处理预警", "alert:detail:process", "alert", "detail", "process"),
    ("关闭预警", "alert:detail:close", "alert", "detail", "close"),
    ("查看预警规则", "alertrule:list:view", "alertrule", "list", "view"),
    ("创建预警规则", "alertrule:list:create", "alertrule", "list", "create"),
    ("查看巡检任务", "inspection:task:view", "inspection", "task", "view"),
    ("创建巡检任务", "inspection:task:create", "inspection", "task", "create"),
    ("执行巡检", "inspection:task:execute", "inspection", "task", "execute"),
    ("查看用户列表", "user:list:view", "user", "list", "view"),
    ("管理用户", "user:detail:edit", "user", "detail", "edit"),
    ("查看角色列表", "role:list:view", "role", "list", "view"),
    ("管理角色", "role:detail:edit", "role", "detail", "edit"),
    ("查看操作日志", "log:list:view", "log", "list", "view"),
    ("导出日志", "log:list:export", "log", "list", "export"),
    ("查看报表", "report:list:view", "report", "list", "view"),
    ("生成报表", "report:list:generate", "report", "list", "generate"),
]

# Role -> permission codes
ROLE_PERMS = {
    "admin": [p[1] for p in PERMISSIONS],
    "ops_manager": [
        "dashboard:overview:view", "datasource:list:view", "dataset:list:view",
        "dataquality:report:view", "analysis:execute:view",
        "dashboard:list:view", "dashboard:list:create", "dashboard:detail:edit",
        "alert:list:view", "alert:detail:process", "alert:detail:close",
        "alertrule:list:view", "alertrule:list:create",
        "inspection:task:view", "report:list:view", "report:list:generate",
    ],
    "analyst": [
        "dashboard:overview:view", "datasource:list:view", "datasource:list:create",
        "datasource:detail:edit", "dataset:list:view", "dataset:list:create",
        "dataset:detail:edit", "dataquality:report:view", "analysis:execute:view",
        "dashboard:list:view", "dashboard:list:create", "dashboard:detail:edit",
        "alert:list:view", "alertrule:list:view", "alertrule:list:create",
    ],
    "device_admin": [
        "dashboard:overview:view", "alert:list:view", "alert:detail:process",
        "inspection:task:view", "inspection:task:create", "inspection:task:execute",
    ],
    "staff": [
        "dashboard:overview:view", "dashboard:list:view",
    ],
}


async def seed():
    """Main seed function for all 24 tables."""
    await init_db()

    async with AsyncSessionLocal() as db:
        try:
            # ================================================
            # 1. PERMISSIONS (30 records)
            # ================================================
            print("[1/24] Creating permissions...")
            perm_map: dict[str, Permission] = {}
            for name, code, mod, page, action in PERMISSIONS:
                perm = Permission(id=_uid(), name=name, code=code, module=mod, page=page, action=action)
                db.add(perm)
                perm_map[code] = perm

            # ================================================
            # 2. ROLES (5 records)
            # ================================================
            print("[2/24] Creating roles...")
            role_defs = [
                ("admin", "系统管理员", True),
                ("ops_manager", "运营经理", True),
                ("analyst", "数据分析师", True),
                ("device_admin", "设备管理员", True),
                ("staff", "普通员工", True),
            ]
            role_map: dict[str, Role] = {}
            for name, desc, is_sys in role_defs:
                role = Role(id=_uid(), name=name, description=desc, is_system=is_sys)
                db.add(role)
                role_map[name] = role
            await db.flush()

            # ================================================
            # 3. ROLE-PERMISSIONS
            # ================================================
            print("[3/24] Assigning role permissions...")
            for role_name, perm_codes in ROLE_PERMS.items():
                role = role_map[role_name]
                for code in perm_codes:
                    perm = perm_map.get(code)
                    if perm:
                        stmt = role_permissions_table.insert().values(role_id=role.id, permission_id=perm.id)
                        await db.execute(stmt)

            # ================================================
            # 4. USERS (5 demo accounts)
            # ================================================
            print("[4/24] Creating users...")
            users_data = [
                ("admin", "admin123", "系统管理员", "admin@datainsight.dev", "13800001111", ["admin"]),
                ("ops_manager", "ops123", "张运营", "ops@datainsight.dev", "13800002222", ["ops_manager"]),
                ("analyst", "analyst123", "李分析", "analyst@datainsight.dev", "13800003333", ["analyst"]),
                ("device_admin", "device123", "王设备", "device@datainsight.dev", "13800004444", ["device_admin"]),
                ("staff", "staff123", "赵员工", "staff@datainsight.dev", "13800005555", ["staff"]),
            ]
            user_map: dict[str, User] = {}
            for uname, pwd, rname, email, phone, role_names in users_data:
                user = User(
                    id=_uid(), username=uname,
                    password_hash=hash_password(pwd),
                    real_name=rname, email=email, phone=phone,
                    status="active",
                    last_login_at=_now() - timedelta(hours=1),
                )
                db.add(user)
                user_map[uname] = user
            await db.flush()

            # ================================================
            # 5. USER-ROLES
            # ================================================
            print("[5/24] Assigning user roles...")
            for uname, _, _, _, _, role_names in users_data:
                u = user_map[uname]
                for rname in role_names:
                    r = role_map[rname]
                    stmt = user_roles_table.insert().values(user_id=u.id, role_id=r.id)
                    await db.execute(stmt)

            # ================================================
            # 6. DEVICES (20 devices)
            # ================================================
            print("[6/24] Creating devices...")
            device_types = ["泵机", "压缩机", "风机", "输送带", "变压器"]
            locations = ["A区-1号车间", "A区-2号车间", "B区-1号车间", "B区-2号车间", "C区-配电房"]
            device_list: list[Device] = []
            for i in range(20):
                dtype = device_types[i % 5]
                loc = locations[i % 5]
                status = "normal"
                if i == 3:
                    status = "abnormal"
                elif i == 7:
                    status = "abnormal"
                elif i == 12:
                    status = "offline"
                elif i == 15:
                    status = "maintenance"

                d = Device(
                    id=_uid(),
                    device_code=f"DEV-{i+1:03d}",
                    device_name=f"{dtype}-{i+1}号",
                    device_type=dtype,
                    location=loc,
                    department="运营部",
                    status=status,
                    running_hours=round(2000.0 + i * 150.5, 2),
                    planned_hours=float(2400 + i * 100),
                    last_heartbeat_at=_now() - timedelta(minutes=i * 30),
                    metadata_info={"manufacturer": "通用电气", "model": f"GEM-{2020 + (i % 5)}"},
                )
                db.add(d)
                device_list.append(d)
            await db.flush()

            # ================================================
            # 7. DATA SOURCES (3 sources)
            # ================================================
            print("[7/24] Creating data sources...")
            ds1 = DataSource(
                id=_uid(), name="生产环境 MySQL", type="mysql",
                description="生产环境主数据库，存储设备运行数据",
                connection_config={"host": "192.168.1.100", "port": 3306, "database": "production"},
                status="connected", data_volume=500000,
                sync_method="incremental", sync_frequency="hourly",
                last_sync_at=_now() - timedelta(hours=1),
                last_sync_status="success",
                owner_id=user_map["admin"].id,
            )
            ds2 = DataSource(
                id=_uid(), name="设备传感器 CSV", type="csv",
                description="设备传感器定时导出数据文件",
                connection_config={"file_path": "/data/sensor_export.csv"},
                status="connected", data_volume=120000,
                sync_method="full", sync_frequency="daily",
                last_sync_at=_now() - timedelta(hours=3),
                last_sync_status="success",
                owner_id=user_map["analyst"].id,
            )
            ds3 = DataSource(
                id=_uid(), name="测试数据库", type="mysql",
                description="已断开的测试环境数据源",
                connection_config={"host": "10.0.0.50", "port": 3306, "database": "test"},
                status="error", data_volume=0,
                sync_method="full", sync_frequency="manual",
                owner_id=user_map["admin"].id,
            )
            db.add_all([ds1, ds2, ds3])
            await db.flush()

            # ================================================
            # 8. DATASETS (2 datasets) + 9. DATASET_FIELDS
            # ================================================
            print("[8/24] Creating datasets...")
            dset1 = Dataset(
                id=_uid(), name="设备运行数据集",
                description="汇总设备运行指标：温度、压力、振动、运行时长",
                source_id=ds1.id, source_table="device_operations",
                field_count=5, data_volume=120000,
                last_refresh_at=_now() - timedelta(hours=2),
                owner_id=user_map["analyst"].id,
            )
            dset2 = Dataset(
                id=_uid(), name="设备故障记录",
                description="设备历史故障与维修记录",
                source_id=ds2.id, source_table="device_faults",
                field_count=4, data_volume=8500,
                last_refresh_at=_now() - timedelta(days=1),
                owner_id=user_map["analyst"].id,
            )
            db.add_all([dset1, dset2])
            await db.flush()

            print("[9/24] Creating dataset fields...")
            fields_dset1 = [
                ("device_id", "设备ID", "string", True, False, None, None),
                ("temperature", "温度", "number", False, True, "avg", "°C"),
                ("pressure", "压力", "number", False, True, "avg", "kPa"),
                ("vibration", "振动", "number", False, True, "max", "mm/s"),
                ("recorded_at", "记录时间", "date", True, False, None, None),
            ]
            for i, (fn, fa, ft, dim, met, agg, unit) in enumerate(fields_dset1):
                f = DatasetField(
                    id=_uid(), dataset_id=dset1.id,
                    field_name=fn, field_alias=fa, field_type=ft,
                    is_dimension=dim, is_metric=met,
                    aggregation=agg, unit=unit, sort_order=i,
                )
                db.add(f)

            fields_dset2 = [
                ("device_id", "设备ID", "string", True, False, None, None),
                ("fault_type", "故障类型", "string", True, False, None, None),
                ("downtime_hours", "停机时长", "number", False, True, "sum", "h"),
                ("fault_date", "故障日期", "date", True, False, None, None),
            ]
            for i, (fn, fa, ft, dim, met, agg, unit) in enumerate(fields_dset2):
                f = DatasetField(
                    id=_uid(), dataset_id=dset2.id,
                    field_name=fn, field_alias=fa, field_type=ft,
                    is_dimension=dim, is_metric=met,
                    aggregation=agg, unit=unit, sort_order=i,
                )
                db.add(f)
            await db.flush()

            # ================================================
            # 10. METRICS (4 metrics)
            # ================================================
            print("[10/24] Creating metrics...")
            m1 = Metric(
                id=_uid(), name="平均温度", code="avg_temp",
                description="设备运行平均温度", category="device",
                dataset_id=dset1.id, device_id=device_list[0].id,
                field_name="temperature", aggregation="avg", unit="°C",
                decimal_places=1, is_key_metric=True,
            )
            m2 = Metric(
                id=_uid(), name="设备利用率", code="device_util",
                description="设备实际利用率 = 运行时长/计划时长", category="device",
                dataset_id=dset1.id,
                field_name="running_hours", aggregation="avg", unit="%",
                decimal_places=1, is_key_metric=True,
            )
            m3 = Metric(
                id=_uid(), name="最大振动", code="max_vibration",
                description="设备最大振动值", category="device",
                dataset_id=dset1.id, device_id=device_list[3].id,
                field_name="vibration", aggregation="max", unit="mm/s",
                decimal_places=2, is_key_metric=False,
            )
            m4 = Metric(
                id=_uid(), name="故障停机时长", code="downtime",
                description="设备因故障停机总时长", category="device",
                dataset_id=dset2.id,
                field_name="downtime_hours", aggregation="sum", unit="h",
                decimal_places=1, is_key_metric=False,
            )
            db.add_all([m1, m2, m3, m4])
            await db.flush()

            # ================================================
            # 11. METRIC_VALUES (28 records: 7 days x 4 per day)
            # ================================================
            print("[11/24] Creating metric values...")
            for d in range(7):
                day = _now() - timedelta(days=6 - d)
                for hour in [0, 6, 12, 18]:
                    ts = day.replace(hour=hour, minute=0, second=0, microsecond=0)
                    mv = MetricValue(
                        id=_uid(), metric_id=m1.id,
                        time_bucket=ts, granularity="hour",
                        value=round(75.0 + d * 0.3 + hour * 0.5, 1),
                    )
                    db.add(mv)
            await db.flush()

            # ================================================
            # 12. ALERT_RULES (3 rules)
            # ================================================
            print("[12/24] Creating alert rules...")
            r1 = AlertRule(
                id=_uid(), name="设备温度过高预警",
                description="设备温度超过 80°C 持续 5 分钟触发",
                metric_id=m1.id, condition="gt", threshold=80.0,
                duration=300, level="high",
                assignee_id=user_map["device_admin"].id,
                notify_methods=["system", "email"], enabled=True, cooldown=600,
            )
            r2 = AlertRule(
                id=_uid(), name="设备利用率过低预警",
                description="设备利用率低于 60% 时触发",
                metric_id=m2.id, condition="lt", threshold=60.0,
                duration=0, level="medium",
                assignee_id=user_map["ops_manager"].id,
                notify_methods=["system"], enabled=True, cooldown=300,
            )
            r3 = AlertRule(
                id=_uid(), name="设备振动异常预警",
                description="振动值超过 5.0 mm/s 时触发",
                metric_id=m3.id, condition="gt", threshold=5.0,
                duration=60, level="critical",
                assignee_id=user_map["device_admin"].id,
                notify_methods=["system", "email", "sms"], enabled=True, cooldown=300,
            )
            db.add_all([r1, r2, r3])
            await db.flush()

            # ================================================
            # 13. ALERTS (5 alerts)
            # ================================================
            print("[13/24] Creating alerts...")
            alert_data = [
                ("设备 DEV-004 温度过高", "温度 92.5°C 超过阈值 80.0°C，持续 15 分钟",
                 "critical", r1.id, m1.id, 92.5, 80.0, "pending",
                 user_map["device_admin"].id, _now() - timedelta(minutes=30)),
                ("设备 DEV-008 温度过高", "温度 85.1°C 超过阈值 80.0°C",
                 "high", r1.id, m1.id, 85.1, 80.0, "processing",
                 user_map["device_admin"].id, _now() - timedelta(hours=2)),
                ("设备利用率偏低", "设备利用率 55.3% 低于阈值 60.0%",
                 "medium", r2.id, m2.id, 55.3, 60.0, "pending",
                 user_map["ops_manager"].id, _now() - timedelta(hours=5)),
                ("设备振动严重超标", "振动值 7.2 mm/s 超过阈值 5.0 mm/s",
                 "critical", r3.id, m3.id, 7.2, 5.0, "pending",
                 user_map["device_admin"].id, _now() - timedelta(minutes=10)),
                ("数据源连接异常", "测试数据库无法连接",
                 "low", None, None, 0, 0, "closed",
                 user_map["admin"].id, _now() - timedelta(days=1)),
            ]
            alert_list = []
            for title, desc, level, rid, mid, cv, tv, status, aid, triggered in alert_data:
                a = Alert(
                    id=_uid(), rule_id=rid, metric_id=mid,
                    title=title, description=desc, level=level,
                    current_value=cv, threshold_value=tv,
                    status=status, assignee_id=aid,
                    triggered_at=triggered,
                    closed_at=_now() if status == "closed" else None,
                )
                db.add(a)
                alert_list.append(a)
            await db.flush()

            # ================================================
            # 14. INSPECTION_PLANS (2 plans)
            # ================================================
            print("[14/24] Creating inspection plans...")
            ip1 = InspectionPlan(
                id=_uid(), name="每日设备巡检计划",
                description="每日上午对全部设备进行例行巡检",
                scope="all", scope_config={"all": True},
                device_ids=[d.id for d in device_list[:10]],
                inspection_metrics={"temperature": "avg", "vibration": "max"},
                assignee_id=user_map["device_admin"].id,
                frequency="daily", cron_expression="0 9 * * *",
                start_date=date.today() - timedelta(days=30),
                enabled=True, creator_id=user_map["admin"].id,
            )
            ip2 = InspectionPlan(
                id=_uid(), name="每周重点设备巡检",
                description="每周五对重点区域设备进行深度巡检",
                scope="by_location", scope_config={"locations": ["A区-1号车间"]},
                device_ids=[d.id for d in device_list[:5]],
                inspection_metrics={"temperature": "max", "vibration": "max", "pressure": "avg"},
                assignee_id=user_map["device_admin"].id,
                frequency="weekly", cron_expression="0 14 * * 5",
                start_date=date.today() - timedelta(days=60),
                enabled=True, creator_id=user_map["ops_manager"].id,
            )
            db.add_all([ip1, ip2])
            await db.flush()

            # ================================================
            # 15. INSPECTION_TASKS (3 tasks)
            # ================================================
            print("[15/24] Creating inspection tasks...")
            it1 = InspectionTask(
                id=_uid(), plan_id=ip1.id,
                name="8月6日 每日例行巡检",
                status="pending", scope="all",
                assignee_id=user_map["device_admin"].id,
                scheduled_at=_now().replace(hour=9, minute=0, second=0, microsecond=0),
            )
            it2 = InspectionTask(
                id=_uid(), plan_id=ip1.id,
                name="8月5日 每日例行巡检",
                status="completed", scope="all",
                assignee_id=user_map["device_admin"].id,
                scheduled_at=_now().replace(hour=9, minute=0, second=0, microsecond=0) - timedelta(days=1),
                executed_at=_now() - timedelta(days=1, hours=-1),
                overall_result="abnormal",
                notes="发现 DEV-004 温度异常，已创建预警",
            )
            it3 = InspectionTask(
                id=_uid(), plan_id=ip2.id,
                name="8月2日 重点设备周巡检",
                status="completed", scope="by_location",
                assignee_id=user_map["device_admin"].id,
                scheduled_at=_now() - timedelta(days=4),
                executed_at=_now() - timedelta(days=4, hours=-2),
                overall_result="normal",
            )
            db.add_all([it1, it2, it3])
            await db.flush()

            # ================================================
            # 16. INSPECTION_RECORDS (5 records)
            # ================================================
            print("[16/24] Creating inspection records...")
            rec_data = [
                (it2.id, device_list[0].id, user_map["device_admin"].id, "normal",
                 {"temperature": 76.5, "vibration": 2.1}, None, _now() - timedelta(days=1)),
                (it2.id, device_list[3].id, user_map["device_admin"].id, "abnormal",
                 {"temperature": 91.2, "vibration": 6.8}, "温度严重超标，建议停机检查",
                 _now() - timedelta(days=1)),
                (it2.id, device_list[7].id, user_map["device_admin"].id, "attention_needed",
                 {"temperature": 79.0, "vibration": 4.5}, "温度接近阈值，需关注",
                 _now() - timedelta(days=1)),
                (it3.id, device_list[0].id, user_map["device_admin"].id, "normal",
                 {"temperature": 75.0, "vibration": 2.0, "pressure": 100.5}, None,
                 _now() - timedelta(days=4)),
                (it3.id, device_list[1].id, user_map["device_admin"].id, "normal",
                 {"temperature": 74.5, "vibration": 1.8, "pressure": 99.8}, None,
                 _now() - timedelta(days=4)),
            ]
            for tid, did, iid, res, detail, anom, insp_at in rec_data:
                rec = InspectionRecord(
                    id=_uid(), task_id=tid, device_id=did,
                    inspector_id=iid, result=res,
                    detail=detail, anomaly_desc=anom,
                    inspected_at=insp_at,
                )
                db.add(rec)
            await db.flush()

            # ================================================
            # 17. DASHBOARDS (2 dashboards)
            # ================================================
            print("[17/24] Creating dashboards...")
            db1 = Dashboard(
                id=_uid(), name="企业运营总览",
                description="默认企业运营看板，展示核心 KPI",
                category="enterprise", is_system=True,
                auto_refresh=True, refresh_interval=60,
                creator_id=user_map["admin"].id,
            )
            db2 = Dashboard(
                id=_uid(), name="设备运营看板",
                description="设备运行状态与利用率监控",
                category="device", is_system=True,
                auto_refresh=True, refresh_interval=30,
                creator_id=user_map["admin"].id,
            )
            db.add_all([db1, db2])
            await db.flush()

            # ================================================
            # 18. DASHBOARD_WIDGETS (8 widgets)
            # ================================================
            print("[18/24] Creating dashboard widgets...")
            widget_data = [
                # Dashboard 1 widgets
                (db1.id, "正常运行率", "stat_card",
                 {"metric": "normal_rate"}, {"x": 0, "y": 0, "w": 3, "h": 2}, 0),
                (db1.id, "异常数量", "stat_card",
                 {"metric": "anomaly_count"}, {"x": 3, "y": 0, "w": 3, "h": 2}, 1),
                (db1.id, "设备利用率", "gauge",
                 {"metric": "device_utilization"}, {"x": 6, "y": 0, "w": 3, "h": 2}, 2),
                (db1.id, "数据量趋势", "line_chart",
                 {"dataset_id": dset1.id, "metric": "data_volume", "granularity": "day"},
                 {"x": 0, "y": 2, "w": 6, "h": 4}, 3),
                (db1.id, "设备状态分布", "pie_chart",
                 {"dataset_id": dset1.id, "dimension": "device_status"},
                 {"x": 6, "y": 2, "w": 6, "h": 4}, 4),
                # Dashboard 2 widgets
                (db2.id, "设备运行状态", "stat_card",
                 {"metric": "device_status"}, {"x": 0, "y": 0, "w": 3, "h": 2}, 0),
                (db2.id, "温度趋势", "line_chart",
                 {"dataset_id": dset1.id, "metric": "temperature", "dimension": "device_id"},
                 {"x": 3, "y": 0, "w": 9, "h": 4}, 1),
                (db2.id, "设备告警列表", "table",
                 {"dataset_id": dset1.id, "columns": ["device_name", "temperature", "status"]},
                 {"x": 0, "y": 4, "w": 12, "h": 4}, 2),
            ]
            for did, name, wtype, cfg, pos, so in widget_data:
                w = DashboardWidget(
                    id=_uid(), dashboard_id=did,
                    name=name, type=wtype,
                    config=cfg, position=pos, sort_order=so,
                )
                db.add(w)
            await db.flush()

            # ================================================
            # 19. REPORTS (2 reports)
            # ================================================
            print("[19/24] Creating reports...")
            rpt1 = Report(
                id=_uid(), name="2026年8月第一周运营周报",
                type="weekly", description="8月第一周设备运营数据汇总",
                file_format="pdf", status="completed",
                creator_id=user_map["ops_manager"].id,
                generated_at=_now() - timedelta(days=4),
            )
            rpt2 = Report(
                id=_uid(), name="2026年8月6日运营日报",
                type="daily", description="今日运营数据日报",
                file_format="excel", status="pending",
                creator_id=user_map["ops_manager"].id,
                is_scheduled=True,
                schedule_config={"cron": "0 8 * * *", "recipients": ["ops_manager", "admin"]},
            )
            db.add_all([rpt1, rpt2])
            await db.flush()

            # ================================================
            # 20. OPERATION_LOGS (10 logs)
            # ================================================
            print("[20/24] Creating operation logs...")
            log_entries = [
                ("admin", "auth", "login", "user", None, "success",
                 _now() - timedelta(hours=1)),
                ("admin", "datasource", "view", "data_source", ds1.id, "success",
                 _now() - timedelta(minutes=55)),
                ("analyst", "dataset", "create", "dataset", dset1.id, "success",
                 _now() - timedelta(hours=3)),
                ("ops_manager", "dashboard", "view", "dashboard", db1.id, "success",
                 _now() - timedelta(minutes=30)),
                ("device_admin", "inspection", "execute", "inspection_task", it2.id, "success",
                 _now() - timedelta(days=1)),
                ("device_admin", "alert", "process", "alert", alert_list[1].id, "success",
                 _now() - timedelta(hours=2)),
                ("admin", "user", "view", "user", None, "success",
                 _now() - timedelta(hours=6)),
                ("ops_manager", "alert", "view", "alert", alert_list[0].id, "success",
                 _now() - timedelta(minutes=25)),
                ("analyst", "analysis", "execute", "dataset", dset1.id, "success",
                 _now() - timedelta(hours=4)),
                ("admin", "datasource", "sync", "data_source", ds1.id, "success",
                 _now() - timedelta(hours=1, minutes=30)),
            ]
            for uname, mod, act, ttype, tid, status, ts in log_entries:
                log = OperationLog(
                    id=_uid(),
                    user_id=user_map[uname].id,
                    username=uname,
                    module=mod,
                    action=act,
                    target_type=ttype,
                    target_id=tid,
                    ip_address="192.168.1.100",
                    status=status,
                    created_at=ts,
                )
                db.add(log)
            await db.flush()

            # ================================================
            # 21. VERSIONS (3 versions)
            # ================================================
            print("[21/24] Creating versions...")
            ver_data = [
                ("1.0.0", "MVP", date.today(), "developing", True, [
                    {"type": "feature", "description": "数据源管理与数据采集"},
                    {"type": "feature", "description": "数据集管理与数据预览"},
                    {"type": "feature", "description": "基础数据分析与指标计算"},
                    {"type": "feature", "description": "运营总览 Dashboard"},
                ]),
                ("0.2.0", "Alpha 2", date.today() - timedelta(days=60), "released", False, [
                    {"type": "feature", "description": "用户认证与权限框架"},
                    {"type": "feature", "description": "数据源连接测试"},
                ]),
                ("0.1.0", "Alpha 1", date.today() - timedelta(days=120), "released", False, [
                    {"type": "feature", "description": "项目初始化与基础框架搭建"},
                ]),
            ]
            for vnum, vname, rdate, vstatus, is_cur, clog in ver_data:
                v = Version(
                    id=_uid(), version_number=vnum,
                    version_name=vname, release_date=rdate,
                    status=vstatus, is_current=is_cur,
                    changelog=clog,
                )
                db.add(v)
            await db.flush()

            # ================================================
            # 22. DATA_SYNC_LOGS (5 logs)
            # ================================================
            print("[22/24] Creating data sync logs...")
            sync_logs_data = [
                (ds1.id, "success", "incremental", 1234, 0, _now() - timedelta(hours=1),
                 _now() - timedelta(hours=1) + timedelta(seconds=45), 45000),
                (ds1.id, "success", "incremental", 1100, 0, _now() - timedelta(hours=2),
                 _now() - timedelta(hours=2) + timedelta(seconds=42), 42000),
                (ds2.id, "success", "full", 8500, 0, _now() - timedelta(hours=3),
                 _now() - timedelta(hours=3) + timedelta(seconds=120), 120000),
                (ds1.id, "failed", "incremental", 500, 200, _now() - timedelta(days=1),
                 _now() - timedelta(days=1) + timedelta(seconds=10), 10000,
                 "连接超时: 无法连接到 192.168.1.100:3306"),
                (ds2.id, "success", "full", 8400, 0, _now() - timedelta(days=1, hours=3),
                 _now() - timedelta(days=1, hours=3) + timedelta(seconds=115), 115000),
            ]
            for data in sync_logs_data:
                if len(data) == 9:
                    sid, status, method, synced, failed, started, finished, dur, err = data
                else:
                    sid, status, method, synced, failed, started, finished, dur = data
                    err = None
                sl = DataSyncLog(
                    id=_uid(), source_id=sid, status=status,
                    sync_method=method,
                    records_synced=synced, records_failed=failed,
                    started_at=started, finished_at=finished,
                    duration_ms=dur, error_message=err,
                )
                db.add(sl)
            await db.flush()

            # ================================================
            # 23. SYSTEM_SETTINGS (5 settings)
            # ================================================
            print("[23/24] Creating system settings...")
            settings_data = [
                ("system.name", "DataInsight", "string", "系统名称"),
                ("system.logo_url", "/logo.png", "string", "系统 Logo URL"),
                ("dashboard.refresh_interval", "60", "number", "Dashboard 默认刷新间隔（秒）"),
                ("alert.default_cooldown", "300", "number", "预警默认冷却时间（秒）"),
                ("system.enable_notification", "true", "boolean", "是否启用系统通知"),
            ]
            for key, val, typ, desc in settings_data:
                s = SystemSetting(id=_uid(), key=key, value=val, type=typ, description=desc)
                db.add(s)
            await db.flush()

            # ================================================
            # 24. NOTIFICATIONS (8 notifications)
            # ================================================
            print("[24/24] Creating notifications...")
            notif_data = [
                (user_map["device_admin"].id, alert_list[0].id,
                 "新预警: 设备 DEV-004 温度过高",
                 "温度 92.5°C 超过阈值 80.0°C，等级: 严重",
                 "alert", False, _now() - timedelta(minutes=30)),
                (user_map["device_admin"].id, alert_list[1].id,
                 "预警更新: 设备 DEV-008 温度过高",
                 "预警状态更新为: 处理中",
                 "alert", True, _now() - timedelta(hours=2)),
                (user_map["ops_manager"].id, alert_list[2].id,
                 "新预警: 设备利用率偏低",
                 "设备利用率 55.3% 低于阈值 60.0%",
                 "alert", False, _now() - timedelta(hours=5)),
                (user_map["device_admin"].id, None,
                 "巡检任务提醒",
                 "您有 1 个待执行的巡检任务: 8月6日 每日例行巡检",
                 "task", False, _now() - timedelta(hours=1)),
                (user_map["ops_manager"].id, None,
                 "报表生成完成",
                 "2026年8月第一周运营周报 已生成",
                 "report", True, _now() - timedelta(days=4)),
                (user_map["admin"].id, None,
                 "数据源异常提醒",
                 "数据源 测试数据库 连接状态异常",
                 "system", False, _now() - timedelta(hours=6)),
                (user_map["device_admin"].id, alert_list[3].id,
                 "新预警: 设备振动严重超标",
                 "振动值 7.2 mm/s 超过阈值 5.0 mm/s，等级: 严重",
                 "alert", False, _now() - timedelta(minutes=10)),
                (user_map["analyst"].id, None,
                 "数据同步完成",
                 "设备传感器 CSV 数据同步完成，新增 8500 条记录",
                 "system", False, _now() - timedelta(hours=3)),
            ]
            for rid, aid, title, content, ntype, is_read, created in notif_data:
                n = Notification(
                    id=_uid(), recipient_id=rid,
                    alert_id=aid, title=title,
                    content=content, type=ntype,
                    is_read=is_read,
                    read_at=_now() if is_read else None,
                    created_at=created,
                )
                db.add(n)
            await db.flush()

            # ================================================
            # COMMIT
            # ================================================
            await db.commit()
            print("\n" + "=" * 60)
            print("  DataInsight Database Seeding Complete!")
            print("=" * 60)
            print(f"  Permissions:     {len(PERMISSIONS)}")
            print(f"  Roles:           {len(role_defs)}")
            print(f"  Users:           5")
            print(f"  Devices:         20")
            print(f"  Data Sources:    3")
            print(f"  Datasets:        2")
            print(f"  Metrics:         4")
            print(f"  Metric Values:   28")
            print(f"  Alert Rules:     3")
            print(f"  Alerts:          5")
            print(f"  Inspection Plans: 2")
            print(f"  Inspection Tasks: 3")
            print(f"  Inspection Recs: 5")
            print(f"  Dashboards:      2")
            print(f"  Widgets:         8")
            print(f"  Reports:         2")
            print(f"  Operation Logs:  10")
            print(f"  Versions:        3")
            print(f"  Data Sync Logs:  5")
            print(f"  System Settings: 5")
            print(f"  Notifications:   8")
            print("=" * 60)
            print("  Demo Accounts:")
            for uname, pwd, rname, _, _, _ in users_data:
                print(f"    {uname} / {pwd}  ({rname})")
            print("=" * 60)

        except Exception as e:
            await db.rollback()
            print(f"\n[ERROR] Seed failed: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(seed())
