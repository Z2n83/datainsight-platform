# DataInsight — 数据库设计文档

> **版本**：v1.0 | **数据库**：PostgreSQL 16 | **ORM**：Prisma | **日期**：2026-08-06

---

## 目录

1. [设计原则](#1-设计原则)
2. [ER 关系总览](#2-er-关系总览)
3. [核心业务表](#3-核心业务表)
4. [用户与权限表](#4-用户与权限表)
5. [数据管理表](#5-数据管理表)
6. [指标与分析表](#6-指标与分析表)
7. [预警表](#7-预警表)
8. [巡检表](#8-巡检表)
9. [看板与报表表](#9-看板与报表表)
10. [系统表](#10-系统表)
11. [索引策略](#11-索引策略)
12. [查询优化建议](#12-查询优化建议)

---

## 1. 设计原则

| 原则 | 说明 |
|------|------|
| **命名规范** | 表名小写+下划线，字段名小写+下划线，索引名 `idx_表名_字段` |
| **主键策略** | 统一使用 UUID v4（便于分布式扩展） |
| **时间字段** | 每表必有 `created_at`、`updated_at`，部分表有 `deleted_at`（软删除） |
| **状态字段** | 使用枚举字符串，不用数字（可读性优先） |
| **外键约束** | 核心关系使用外键 + 索引，保证数据一致性 |
| **软删除** | 核心业务表使用 `deleted_at` 软删除 |
| **分页查询** | 游标分页 + 传统偏移分页双支持 |
| **JSON 字段** | 灵活配置类数据使用 JSONB（如看板配置、规则参数） |

---

## 2. ER 关系总览

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐
│   users  │────→│  user_roles  │←────│    roles     │
└──────────┘     └──────────────┘     └──────────────┘
      │                                      │
      │                                      ▼
      │                              ┌──────────────┐
      │                              │  permissions  │
      │                              └──────────────┘
      │                                      │
      │                                      ▼
      │                              ┌──────────────────┐
      │                              │ role_permissions │
      │                              └──────────────────┘
      │
      ├────→ operation_logs
      │
      ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ data_sources │────→│   datasets   │────→│ dataset_fields│
└──────────────┘     └──────────────┘     └──────────────┘
      │                     │
      │                     ▼
      │              ┌──────────────┐
      │              │ metric_values│
      │              └──────────────┘
      │
      ▼
┌──────────────┐     ┌──────────────┐
│   devices    │────→│  metrics     │
└──────────────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐     ┌──────────────┐
                     │ alert_rules  │────→│    alerts    │
                     └──────────────┘     └──────────────┘
                                                │
                                                ▼
┌──────────────────┐     ┌──────────────────┐
│ inspection_plans │────→│ inspection_tasks │
└──────────────────┘     └──────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │inspection_records│
                         └──────────────────┘

┌──────────────┐     ┌──────────────────┐
│  dashboards  │────→│ dashboard_widgets│
└──────────────┘     └──────────────────┘

┌──────────────┐
│   reports    │
└──────────────┘

┌──────────────┐
│   versions   │
└──────────────┘
```

### 核心关系说明

| 关系 | 类型 | 说明 |
|------|------|------|
| users ↔ roles | N:N | 通过 user_roles 关联 |
| roles ↔ permissions | N:N | 通过 role_permissions 关联 |
| data_sources → datasets | 1:N | 一个数据源可创建多个数据集 |
| datasets → dataset_fields | 1:N | 一个数据集包含多个字段 |
| datasets → metrics | 1:N | 一个数据集可定义多个指标 |
| metrics → metric_values | 1:N | 一个指标有多个时间点的值 |
| alert_rules → alerts | 1:N | 一个规则可触发多次预警 |
| inspection_plans → inspection_tasks | 1:N | 一个计划生成多个任务 |
| inspection_tasks → inspection_records | 1:N | 一个任务有多条执行记录 |
| dashboards → dashboard_widgets | 1:N | 一个看板包含多个组件 |
| users → operation_logs | 1:N | 一个用户有多条操作日志 |

---

## 3. 核心业务表

### 3.1 users（用户表）

| 属性 | 说明 |
|------|------|
| **用途** | 存储系统用户基本信息 |
| **主键** | `id` (UUID) |
| **索引** | `idx_users_username` (唯一), `idx_users_email` (唯一), `idx_users_status`, `idx_users_created_at` |
| **软删除** | 否（使用 status 字段控制） |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK, DEFAULT gen_random_uuid() | 用户唯一标识 |
| username | VARCHAR(50) | NOT NULL, UNIQUE | 用户名 |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt 加密密码 |
| real_name | VARCHAR(100) | NOT NULL | 真实姓名 |
| email | VARCHAR(255) | UNIQUE | 邮箱 |
| phone | VARCHAR(20) | | 手机号 |
| avatar_url | VARCHAR(500) | | 头像 URL |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'active' | active / disabled |
| last_login_at | TIMESTAMPTZ | | 最后登录时间 |
| last_login_ip | VARCHAR(45) | | 最后登录 IP |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 更新时间 |
| deleted_at | TIMESTAMPTZ | | 软删除时间 |

### 3.2 roles（角色表）

| 属性 | 说明 |
|------|------|
| **用途** | 存储系统角色定义 |
| **主键** | `id` (UUID) |
| **索引** | `idx_roles_name` (唯一) |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 角色唯一标识 |
| name | VARCHAR(50) | NOT NULL, UNIQUE | 角色名称（admin/ops_manager/analyst/device_admin/staff） |
| description | VARCHAR(255) | | 角色描述 |
| is_system | BOOLEAN | DEFAULT false | 是否为系统内置角色（不可删除） |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 更新时间 |

### 3.3 permissions（权限表）

| 属性 | 说明 |
|------|------|
| **用途** | 存储系统权限定义 |
| **主键** | `id` (UUID) |
| **索引** | `idx_permissions_code` (唯一), `idx_permissions_module` |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 权限唯一标识 |
| name | VARCHAR(100) | NOT NULL | 权限名称（中文） |
| code | VARCHAR(100) | NOT NULL, UNIQUE | 权限编码（module:page:action） |
| module | VARCHAR(50) | NOT NULL | 所属模块 |
| page | VARCHAR(100) | | 所属页面 |
| action | VARCHAR(50) | NOT NULL | 操作类型（view/create/edit/delete/export） |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |

### 3.4 user_roles（用户角色关联表）

| 属性 | 说明 |
|------|------|
| **用途** | 用户与角色的多对多关联 |
| **主键** | 复合主键 (user_id, role_id) |
| **外键** | user_id → users.id, role_id → roles.id |
| **索引** | `idx_user_roles_user_id`, `idx_user_roles_role_id` |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| user_id | UUID | PK, FK → users.id | 用户 ID |
| role_id | UUID | PK, FK → roles.id | 角色 ID |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 关联时间 |

### 3.5 role_permissions（角色权限关联表）

| 属性 | 说明 |
|------|------|
| **用途** | 角色与权限的多对多关联 |
| **主键** | 复合主键 (role_id, permission_id) |
| **外键** | role_id → roles.id, permission_id → permissions.id |
| **索引** | `idx_role_permissions_role_id`, `idx_role_permissions_permission_id` |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| role_id | UUID | PK, FK → roles.id | 角色 ID |
| permission_id | UUID | PK, FK → permissions.id | 权限 ID |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 关联时间 |

---

## 4. 数据管理表

### 4.1 data_sources（数据源表）

| 属性 | 说明 |
|------|------|
| **用途** | 存储数据源连接信息和状态 |
| **主键** | `id` (UUID) |
| **外键** | owner_id → users.id |
| **索引** | `idx_data_sources_type`, `idx_data_sources_status`, `idx_data_sources_owner`, `idx_data_sources_last_sync_at` |
| **软删除** | 是 |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 数据源唯一标识 |
| name | VARCHAR(100) | NOT NULL | 数据源名称 |
| type | VARCHAR(20) | NOT NULL | 类型：mysql / postgresql / mongodb / api / csv / excel |
| description | TEXT | | 描述 |
| connection_config | JSONB | NOT NULL | 连接配置（host/port/db/user/password 等） |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'disconnected' | connected / disconnected / error |
| data_volume | BIGINT | DEFAULT 0 | 数据量（行数） |
| sync_method | VARCHAR(20) | DEFAULT 'full' | 同步方式：full / incremental |
| sync_frequency | VARCHAR(50) | | 同步频率：manual / hourly / daily / weekly / custom(cron表达式) |
| sync_cron | VARCHAR(50) | | 自定义 Cron 表达式 |
| last_sync_at | TIMESTAMPTZ | | 最近同步时间 |
| last_sync_status | VARCHAR(20) | | success / failed / running |
| last_sync_error | TEXT | | 最近同步错误信息 |
| owner_id | UUID | FK → users.id | 负责人 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 更新时间 |
| deleted_at | TIMESTAMPTZ | | 软删除时间 |

### 4.2 datasets（数据集表）

| 属性 | 说明 |
|------|------|
| **用途** | 存储可供分析的数据集定义 |
| **主键** | `id` (UUID) |
| **外键** | source_id → data_sources.id, owner_id → users.id |
| **索引** | `idx_datasets_source_id`, `idx_datasets_owner`, `idx_datasets_updated_at` |
| **软删除** | 是 |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 数据集唯一标识 |
| name | VARCHAR(100) | NOT NULL | 数据集名称 |
| description | TEXT | | 描述 |
| source_id | UUID | FK → data_sources.id | 所属数据源 |
| source_table | VARCHAR(100) | NOT NULL | 源表名（或 SQL 视图名） |
| query_config | JSONB | | 查询配置（JOIN 关系、WHERE 默认条件等） |
| field_count | INTEGER | DEFAULT 0 | 字段数量 |
| data_volume | BIGINT | DEFAULT 0 | 数据量 |
| last_refresh_at | TIMESTAMPTZ | | 最后刷新时间 |
| owner_id | UUID | FK → users.id | 负责人 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 更新时间 |
| deleted_at | TIMESTAMPTZ | | 软删除时间 |

### 4.3 dataset_fields（数据集字段表）

| 属性 | 说明 |
|------|------|
| **用途** | 存储数据集的字段定义与映射 |
| **主键** | `id` (UUID) |
| **外键** | dataset_id → datasets.id |
| **索引** | `idx_dataset_fields_dataset_id`, `idx_dataset_fields_is_dimension` |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 字段唯一标识 |
| dataset_id | UUID | FK → datasets.id, NOT NULL | 所属数据集 |
| field_name | VARCHAR(100) | NOT NULL | 原始字段名 |
| field_alias | VARCHAR(100) | | 字段别名（展示用） |
| field_type | VARCHAR(30) | NOT NULL | 数据类型：string/number/date/boolean/category |
| is_dimension | BOOLEAN | DEFAULT false | 是否为维度字段 |
| is_metric | BOOLEAN | DEFAULT false | 是否可做指标字段 |
| aggregation | VARCHAR(20) | | 默认聚合方式：sum/avg/count/max/min/none |
| unit | VARCHAR(20) | | 单位 |
| sort_order | INTEGER | DEFAULT 0 | 排序 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 更新时间 |

---

## 5. 设备与指标表

### 5.1 devices（设备表）

| 属性 | 说明 |
|------|------|
| **用途** | 存储设备基础信息与运行状态 |
| **主键** | `id` (UUID) |
| **索引** | `idx_devices_status`, `idx_devices_type`, `idx_devices_location` |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 设备唯一标识 |
| device_code | VARCHAR(50) | NOT NULL, UNIQUE | 设备编号 |
| device_name | VARCHAR(100) | NOT NULL | 设备名称 |
| device_type | VARCHAR(50) | NOT NULL | 设备类型 |
| location | VARCHAR(255) | | 位置/区域 |
| department | VARCHAR(100) | | 所属部门 |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'normal' | normal / abnormal / offline / maintenance |
| running_hours | DECIMAL(10,2) | DEFAULT 0 | 累计运行时长（小时） |
| planned_hours | DECIMAL(10,2) | DEFAULT 0 | 计划运行时长（小时） |
| last_heartbeat_at | TIMESTAMPTZ | | 最后心跳时间 |
| metadata | JSONB | | 扩展属性（厂商、型号、参数等） |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 更新时间 |
| deleted_at | TIMESTAMPTZ | | 软删除时间 |

### 5.2 metrics（指标定义表）

| 属性 | 说明 |
|------|------|
| **用途** | 存储指标定义（计算逻辑） |
| **主键** | `id` (UUID) |
| **外键** | dataset_id → datasets.id, device_id → devices.id（可选） |
| **索引** | `idx_metrics_dataset_id`, `idx_metrics_device_id`, `idx_metrics_category` |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 指标唯一标识 |
| name | VARCHAR(100) | NOT NULL | 指标名称 |
| code | VARCHAR(50) | NOT NULL | 指标编码 |
| description | TEXT | | 指标说明 |
| category | VARCHAR(50) | | 指标分类：operation/device/quality/business |
| dataset_id | UUID | FK → datasets.id | 所属数据集 |
| device_id | UUID | FK → devices.id, NULLABLE | 关联设备（设备指标时） |
| field_name | VARCHAR(100) | NOT NULL | 计算字段 |
| aggregation | VARCHAR(20) | NOT NULL | 聚合函数：sum/avg/count/max/min |
| unit | VARCHAR(20) | | 单位（%、h、次 等） |
| decimal_places | INTEGER | DEFAULT 2 | 小数位数 |
| is_key_metric | BOOLEAN | DEFAULT false | 是否为核心 KPI 指标 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 更新时间 |

### 5.3 metric_values（指标值表）

| 属性 | 说明 |
|------|------|
| **用途** | 存储指标在不同时间点的计算结果（时序数据） |
| **主键** | `id` (UUID) |
| **外键** | metric_id → metrics.id |
| **索引** | `idx_mv_metric_time` (metric_id, time_bucket), `idx_mv_time_bucket` |
| **分区** | 按月分区（数据量大时） |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 值唯一标识 |
| metric_id | UUID | FK → metrics.id, NOT NULL | 所属指标 |
| time_bucket | TIMESTAMPTZ | NOT NULL | 时间桶（聚合后的时间点） |
| granularity | VARCHAR(10) | NOT NULL | 粒度：hour/day/week/month/quarter/year |
| value | DECIMAL(18,4) | NOT NULL | 指标值 |
| dimension_key | VARCHAR(100) | | 维度键（如 device_type=泵机） |
| dimension_value | VARCHAR(255) | | 维度值 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 计算时间 |

---

## 6. 预警表

### 6.1 alert_rules（预警规则表）

| 属性 | 说明 |
|------|------|
| **用途** | 存储预警规则定义 |
| **主键** | `id` (UUID) |
| **外键** | metric_id → metrics.id, assignee_id → users.id |
| **索引** | `idx_alert_rules_enabled`, `idx_alert_rules_metric_id`, `idx_alert_rules_level` |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 规则唯一标识 |
| name | VARCHAR(100) | NOT NULL | 规则名称 |
| description | TEXT | | 规则描述 |
| metric_id | UUID | FK → metrics.id, NOT NULL | 监控指标 |
| condition | VARCHAR(10) | NOT NULL | 条件：gt(>)、lt(<)、gte(>=)、lte(<=)、eq(=)、neq(!=) |
| threshold | DECIMAL(18,4) | NOT NULL | 阈值 |
| duration | INTEGER | NOT NULL, DEFAULT 0 | 持续时间（秒），0=立即触发 |
| level | VARCHAR(10) | NOT NULL | 等级：low / medium / high / critical |
| assignee_id | UUID | FK → users.id | 默认负责人 |
| notify_methods | JSONB | DEFAULT '["system"]' | 通知方式：system/email/sms/dingtalk/wecom |
| enabled | BOOLEAN | DEFAULT true | 是否启用 |
| cooldown | INTEGER | DEFAULT 300 | 冷却时间（秒），避免重复预警 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 更新时间 |
| deleted_at | TIMESTAMPTZ | | 软删除时间 |

### 6.2 alerts（预警记录表）

| 属性 | 说明 |
|------|------|
| **用途** | 存储实际触发的预警记录 |
| **主键** | `id` (UUID) |
| **外键** | rule_id → alert_rules.id, metric_id → metrics.id, assignee_id → users.id |
| **索引** | `idx_alerts_status`, `idx_alerts_level`, `idx_alerts_triggered_at`, `idx_alerts_rule_id`, `idx_alerts_assignee` |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 预警唯一标识 |
| rule_id | UUID | FK → alert_rules.id | 触发规则 |
| metric_id | UUID | FK → metrics.id | 触发指标 |
| title | VARCHAR(200) | NOT NULL | 预警标题 |
| description | TEXT | | 预警描述 |
| level | VARCHAR(10) | NOT NULL | 等级：low / medium / high / critical |
| current_value | DECIMAL(18,4) | NOT NULL | 当前值 |
| threshold_value | DECIMAL(18,4) | NOT NULL | 触发阈值 |
| triggered_at | TIMESTAMPTZ | NOT NULL | 触发时间 |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | pending / processing / closed |
| assignee_id | UUID | FK → users.id | 负责人 |
| processor_id | UUID | FK → users.id | 处理人 |
| process_note | TEXT | | 处理备注 |
| processed_at | TIMESTAMPTZ | | 处理时间 |
| closed_at | TIMESTAMPTZ | | 关闭时间 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 更新时间 |

---

## 7. 巡检表

### 7.1 inspection_plans（巡检计划表）

| 属性 | 说明 |
|------|------|
| **用途** | 存储巡检计划定义 |
| **主键** | `id` (UUID) |
| **外键** | creator_id → users.id |
| **索引** | `idx_ip_enabled`, `idx_ip_creator` |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 计划唯一标识 |
| name | VARCHAR(100) | NOT NULL | 计划名称 |
| description | TEXT | | 计划描述 |
| scope | VARCHAR(50) | NOT NULL | 巡检范围：all / by_device / by_location / by_type |
| scope_config | JSONB | | 范围配置（设备ID列表、位置等） |
| device_ids | UUID[] | | 关联设备 ID 数组 |
| inspection_metrics | JSONB | | 巡检指标配置 |
| assignee_id | UUID | FK → users.id | 默认负责人 |
| frequency | VARCHAR(20) | NOT NULL | 执行频率：daily / weekly / monthly / custom |
| cron_expression | VARCHAR(50) | | Cron 表达式 |
| start_date | DATE | NOT NULL | 开始日期 |
| end_date | DATE | | 结束日期 |
| enabled | BOOLEAN | DEFAULT true | 是否启用 |
| creator_id | UUID | FK → users.id | 创建人 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 更新时间 |
| deleted_at | TIMESTAMPTZ | | 软删除时间 |

### 7.2 inspection_tasks（巡检任务表）

| 属性 | 说明 |
|------|------|
| **用途** | 存储具体巡检任务（由计划生成） |
| **主键** | `id` (UUID) |
| **外键** | plan_id → inspection_plans.id, assignee_id → users.id |
| **索引** | `idx_it_status`, `idx_it_plan_id`, `idx_it_assignee`, `idx_it_scheduled_at` |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 任务唯一标识 |
| plan_id | UUID | FK → inspection_plans.id | 所属计划 |
| name | VARCHAR(100) | NOT NULL | 任务名称 |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | pending / in_progress / completed / cancelled |
| scope | VARCHAR(50) | NOT NULL | 巡检范围 |
| scope_config | JSONB | | 范围配置 |
| assignee_id | UUID | FK → users.id | 负责人 |
| scheduled_at | TIMESTAMPTZ | NOT NULL | 计划执行时间 |
| executed_at | TIMESTAMPTZ | | 实际执行时间 |
| overall_result | VARCHAR(20) | | normal / abnormal / attention_needed |
| notes | TEXT | | 备注 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 更新时间 |

### 7.3 inspection_records（巡检记录表）

| 属性 | 说明 |
|------|------|
| **用途** | 存储巡检执行记录（明细） |
| **主键** | `id` (UUID) |
| **外键** | task_id → inspection_tasks.id, device_id → devices.id, inspector_id → users.id |
| **索引** | `idx_ir_task_id`, `idx_ir_device_id`, `idx_ir_result`, `idx_ir_inspected_at` |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 记录唯一标识 |
| task_id | UUID | FK → inspection_tasks.id | 所属任务 |
| device_id | UUID | FK → devices.id | 巡检设备 |
| inspector_id | UUID | FK → users.id | 巡检人 |
| result | VARCHAR(20) | NOT NULL | 结果：normal / abnormal / attention_needed |
| detail | JSONB | | 巡检明细（指标名→值） |
| anomaly_desc | TEXT | | 异常描述 |
| images | JSONB | | 现场照片 URL 数组 |
| inspected_at | TIMESTAMPTZ | NOT NULL | 巡检时间 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |

---

## 8. 看板与报表表

### 8.1 dashboards（看板表）

| 属性 | 说明 |
|------|------|
| **用途** | 存储可视化看板定义 |
| **主键** | `id` (UUID) |
| **外键** | creator_id → users.id |
| **索引** | `idx_dashboards_creator`, `idx_dashboards_category` |
| **软删除** | 是 |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 看板唯一标识 |
| name | VARCHAR(100) | NOT NULL | 看板名称 |
| description | TEXT | | 看板描述 |
| category | VARCHAR(30) | NOT NULL | 分类：enterprise / device / custom |
| layout | JSONB | | 布局配置 |
| thumbnail_url | VARCHAR(500) | | 缩略图 |
| is_system | BOOLEAN | DEFAULT false | 是否系统预置 |
| auto_refresh | BOOLEAN | DEFAULT false | 是否自动刷新 |
| refresh_interval | INTEGER | DEFAULT 60 | 刷新间隔（秒） |
| creator_id | UUID | FK → users.id | 创建人 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 更新时间 |
| deleted_at | TIMESTAMPTZ | | 软删除时间 |

### 8.2 dashboard_widgets（看板组件表）

| 属性 | 说明 |
|------|------|
| **用途** | 存储看板中的图表组件配置 |
| **主键** | `id` (UUID) |
| **外键** | dashboard_id → dashboards.id |
| **索引** | `idx_dw_dashboard_id`, `idx_dw_type` |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 组件唯一标识 |
| dashboard_id | UUID | FK → dashboards.id, NOT NULL | 所属看板 |
| name | VARCHAR(100) | NOT NULL | 组件名称 |
| type | VARCHAR(30) | NOT NULL | 类型：stat_card / line_chart / bar_chart / pie_chart / table / gauge / heatmap / ... |
| config | JSONB | NOT NULL | 组件配置（数据源、指标、维度、图表样式） |
| position | JSONB | NOT NULL | 位置 {x, y, w, h} |
| sort_order | INTEGER | DEFAULT 0 | 排序 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 更新时间 |

### 8.3 reports（报表表）

| 属性 | 说明 |
|------|------|
| **用途** | 存储生成的报表信息 |
| **主键** | `id` (UUID) |
| **外键** | creator_id → users.id |
| **索引** | `idx_reports_type`, `idx_reports_status`, `idx_reports_created_at`, `idx_reports_creator` |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 报表唯一标识 |
| name | VARCHAR(100) | NOT NULL | 报表名称 |
| type | VARCHAR(20) | NOT NULL | 类型：daily / weekly / monthly / custom |
| description | TEXT | | 描述 |
| config | JSONB | | 报表配置（包含的指标、图表） |
| file_format | VARCHAR(10) | NOT NULL | 格式：pdf / excel / csv |
| file_url | VARCHAR(500) | | 文件下载 URL |
| file_size | BIGINT | | 文件大小（字节） |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | pending / generating / completed / failed |
| is_scheduled | BOOLEAN | DEFAULT false | 是否定时生成 |
| schedule_config | JSONB | | 定时配置（cron, 接收人） |
| creator_id | UUID | FK → users.id | 创建人 |
| generated_at | TIMESTAMPTZ | | 生成时间 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 更新时间 |
| deleted_at | TIMESTAMPTZ | | 软删除时间 |

---

## 9. 系统表

### 9.1 operation_logs（操作日志表）

| 属性 | 说明 |
|------|------|
| **用途** | 存储所有用户操作的审计日志 |
| **主键** | `id` (UUID) |
| **外键** | user_id → users.id |
| **索引** | `idx_ol_user_id`, `idx_ol_module`, `idx_ol_action`, `idx_ol_created_at` |
| **归档策略** | 按月分区，保留 12 个月后归档 |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 日志唯一标识 |
| user_id | UUID | FK → users.id | 操作用户 |
| username | VARCHAR(50) | NOT NULL | 用户名（冗余，方便查询） |
| module | VARCHAR(50) | NOT NULL | 操作模块 |
| action | VARCHAR(50) | NOT NULL | 操作类型：view / create / update / delete / export / login / logout |
| target_type | VARCHAR(50) | | 操作对象类型 |
| target_id | UUID | | 操作对象 ID |
| detail | JSONB | | 操作详情（变更前后对比） |
| ip_address | VARCHAR(45) | | 操作 IP |
| user_agent | VARCHAR(500) | | 浏览器 UA |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'success' | success / failed |
| error_message | TEXT | | 错误信息 |
| duration_ms | INTEGER | | 操作耗时（毫秒） |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 操作时间 |

### 9.2 versions（版本表）

| 属性 | 说明 |
|------|------|
| **用途** | 存储系统版本和更新日志 |
| **主键** | `id` (UUID) |
| **索引** | `idx_versions_released_at` |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 版本唯一标识 |
| version_number | VARCHAR(20) | NOT NULL, UNIQUE | 版本号（如 1.0.0） |
| version_name | VARCHAR(50) | | 版本代号（如 MVP） |
| release_date | DATE | NOT NULL | 发布日期 |
| status | VARCHAR(20) | NOT NULL | planning / developing / testing / released / deprecated |
| changelog | JSONB | NOT NULL | 更新日志 [{type, description}] |
| is_current | BOOLEAN | DEFAULT false | 是否为当前版本 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 更新时间 |

### 9.3 data_sync_logs（数据同步日志表）

| 属性 | 说明 |
|------|------|
| **用途** | 存储数据源同步的执行日志 |
| **主键** | `id` (UUID) |
| **外键** | source_id → data_sources.id |
| **索引** | `idx_dsl_source_id`, `idx_dsl_status`, `idx_dsl_started_at` |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 日志唯一标识 |
| source_id | UUID | FK → data_sources.id | 数据源 ID |
| status | VARCHAR(20) | NOT NULL | running / success / failed |
| sync_method | VARCHAR(20) | NOT NULL | full / incremental |
| records_synced | INTEGER | DEFAULT 0 | 同步记录数 |
| records_failed | INTEGER | DEFAULT 0 | 失败记录数 |
| error_message | TEXT | | 错误信息 |
| started_at | TIMESTAMPTZ | NOT NULL | 开始时间 |
| finished_at | TIMESTAMPTZ | | 结束时间 |
| duration_ms | INTEGER | | 耗时（毫秒） |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |

### 9.4 system_settings（系统配置表）

| 属性 | 说明 |
|------|------|
| **用途** | 存储系统级配置参数（KV 结构） |
| **主键** | `id` (UUID) |
| **索引** | `idx_ss_key` (唯一) |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 配置唯一标识 |
| key | VARCHAR(100) | NOT NULL, UNIQUE | 配置键 |
| value | TEXT | NOT NULL | 配置值 |
| type | VARCHAR(20) | DEFAULT 'string' | 值类型：string/number/boolean/json |
| description | VARCHAR(255) | | 配置说明 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 更新时间 |

### 9.5 notifications（通知表）

| 属性 | 说明 |
|------|------|
| **用途** | 存储系统内通知 |
| **主键** | `id` (UUID) |
| **外键** | recipient_id → users.id, alert_id → alerts.id (可选) |
| **索引** | `idx_notif_recipient`, `idx_notif_read`, `idx_notif_created_at` |

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 通知唯一标识 |
| recipient_id | UUID | FK → users.id, NOT NULL | 接收人 |
| alert_id | UUID | FK → alerts.id | 关联预警 |
| title | VARCHAR(200) | NOT NULL | 通知标题 |
| content | TEXT | NOT NULL | 通知内容 |
| type | VARCHAR(30) | NOT NULL | 类型：alert / system / task / report |
| is_read | BOOLEAN | DEFAULT false | 是否已读 |
| read_at | TIMESTAMPTZ | | 阅读时间 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |

---

## 10. 索引策略

### 10.1 索引设计原则

| 原则 | 说明 |
|------|------|
| **高频查询字段建索引** | WHERE 条件中频繁出现的字段（status, type, user_id 等） |
| **外键必建索引** | 所有 FK 字段需要索引以加速 JOIN |
| **时间字段建索引** | created_at, triggered_at 等时间范围查询 |
| **复合索引按选择性排** | 高选择性字段在前 |
| **避免过多索引** | 写入密集型表控制索引数量（< 6 个） |
| **部分索引** | 对软删除场景使用 `WHERE deleted_at IS NULL` |

### 10.2 关键查询场景索引覆盖

| 查询场景 | 索引 |
|---------|------|
| 用户登录 | `idx_users_username` (UNIQUE) |
| 数据源状态筛选 | `idx_data_sources_status` |
| 数据集按数据源查询 | `idx_datasets_source_id` |
| 活跃预警列表 | `idx_alerts_status` + `idx_alerts_triggered_at` |
| 预警按规则查询 | `idx_alerts_rule_id` |
| 指标值时序查询 | `idx_mv_metric_time` (metric_id, time_bucket) |
| 操作日志按用户查询 | `idx_ol_user_id` + `idx_ol_created_at` |
| 看板组件查询 | `idx_dw_dashboard_id` |
| 巡检任务按状态 | `idx_it_status` + `idx_it_scheduled_at` |
| 通知按接收人 | `idx_notif_recipient` + `idx_notif_read` |

---

## 11. 查询优化建议

### 11.1 分页查询

```sql
-- 传统偏移分页（小数据量）
SELECT * FROM alerts
WHERE deleted_at IS NULL
ORDER BY triggered_at DESC
LIMIT 20 OFFSET 0;

-- 游标分页（大数据量，推荐）
SELECT * FROM alerts
WHERE deleted_at IS NULL
  AND triggered_at < '2026-01-01T00:00:00Z'  -- 上一页最后一条的时间
ORDER BY triggered_at DESC
LIMIT 20;
```

### 11.2 软删除查询规范

```sql
-- 所有查询都需要过滤软删除记录
SELECT * FROM data_sources WHERE deleted_at IS NULL;

-- 可以在应用层使用 Scope 自动添加
-- 或者创建视图（不推荐，会影响写入性能）
```

### 11.3 时序数据查询优化

```sql
-- 使用索引 + 分区裁剪
SELECT
  time_bucket,
  AVG(value) as avg_value
FROM metric_values
WHERE metric_id = 'xxx'
  AND time_bucket BETWEEN '2026-01-01' AND '2026-01-31'
  AND granularity = 'day'
GROUP BY time_bucket
ORDER BY time_bucket;
```

### 11.4 大表统计优化

```sql
-- 使用物化视图缓存聚合结果
CREATE MATERIALIZED VIEW mv_daily_device_stats AS
SELECT
  device_id,
  DATE_TRUNC('day', time_bucket) as day,
  AVG(value) as avg_value,
  MAX(value) as max_value,
  MIN(value) as min_value
FROM metric_values
WHERE granularity = 'hour'
GROUP BY device_id, DATE_TRUNC('day', time_bucket);

-- 定期刷新
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_device_stats;
```

---

## 12. 数据迁移计划

### 12.1 Migration 文件命名

```
0001_create_users_table
0002_create_roles_table
0003_create_permissions_table
0004_create_user_roles_table
0005_create_role_permissions_table
0006_create_data_sources_table
0007_create_datasets_table
0008_create_dataset_fields_table
0009_create_devices_table
0010_create_metrics_table
0011_create_metric_values_table
0012_create_alert_rules_table
0013_create_alerts_table
0014_create_inspection_plans_table
0015_create_inspection_tasks_table
0016_create_inspection_records_table
0017_create_dashboards_table
0018_create_dashboard_widgets_table
0019_create_reports_table
0020_create_operation_logs_table
0021_create_versions_table
0022_create_data_sync_logs_table
0023_create_system_settings_table
0024_create_notifications_table
```

### 12.2 种子数据

系统初始化时需预置：

1. **5 个默认角色**：admin, ops_manager, analyst, device_admin, staff
2. **50+ 默认权限**：按模块×操作生成
3. **默认角色权限映射**：每个角色预设权限
4. **1 个管理员账号**：admin / admin123（首次登录强制修改）
5. **系统配置项**：系统名称、Logo URL、默认刷新间隔等
6. **演示数据**：示例数据源、数据集、看板（可选，用于演示）

---

> **文档维护**：数据库设计变更必须同步更新本文档。Migration 文件使用 Prisma Migrate 管理。
