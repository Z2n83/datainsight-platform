# DataInsight — API 接口规划文档

> **版本**：v1.0 | **Base URL**：`/api` | **认证方式**：JWT Bearer Token | **日期**：2026-08-06

---

## 目录

1. [API 设计规范](#1-api-设计规范)
2. [通用约定](#2-通用约定)
3. [认证模块](#3-认证模块)
4. [工作台模块](#4-工作台模块)
5. [数据源模块](#5-数据源模块)
6. [数据集模块](#6-数据集模块)
7. [数据质量模块](#7-数据质量模块)
8. [数据分析模块](#8-数据分析模块)
9. [看板模块](#9-看板模块)
10. [预警模块](#10-预警模块)
11. [预警规则模块](#11-预警规则模块)
12. [巡检模块](#12-巡检模块)
13. [报表模块](#13-报表模块)
14. [用户管理模块](#14-用户管理模块)
15. [角色管理模块](#15-角色管理模块)
16. [日志模块](#16-日志模块)
17. [系统配置模块](#17-系统配置模块)
18. [版本模块](#18-版本模块)
19. [通用模块](#19-通用模块)
20. [WebSocket 事件](#20-websocket-事件)

---

## 1. API 设计规范

| 规范项 | 说明 |
|--------|------|
| **Base URL** | `/api` |
| **协议** | HTTPS（生产）+ HTTP（本地开发） |
| **数据格式** | JSON（Request/Response） |
| **字符编码** | UTF-8 |
| **认证方式** | Header: `Authorization: Bearer <token>` |
| **分页参数** | `?page=1&pageSize=20` 或游标 `?cursor=xxx&limit=20` |
| **排序参数** | `?sortBy=createdAt&order=desc` |
| **时间格式** | ISO 8601: `2026-08-06T10:30:00+08:00` |
| **版本控制** | URL 前缀 `/api/v1/`（预留，MVP 可省略） |

### 1.1 通用响应格式

```json
// 成功
{
  "code": 0,
  "message": "success",
  "data": { },
  "timestamp": "2026-08-06T10:30:00+08:00"
}

// 列表（分页）
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [],
    "total": 100,
    "page": 1,
    "pageSize": 20,
    "totalPages": 5
  },
  "timestamp": "2026-08-06T10:30:00+08:00"
}

// 错误
{
  "code": 40001,
  "message": "用户名或密码错误",
  "data": null,
  "timestamp": "2026-08-06T10:30:00+08:00"
}
```

### 1.2 错误码规范

| 范围 | 说明 |
|------|------|
| 0 | 成功 |
| 40000-40099 | 参数校验错误 |
| 40100-40199 | 认证/授权错误 |
| 40300-40399 | 权限不足 |
| 40400-40499 | 资源不存在 |
| 40900-40999 | 冲突（重复等） |
| 50000-50099 | 服务器内部错误 |
| 50300-50399 | 服务不可用 |

### 1.3 HTTP 状态码使用

| 方法 | 成功 | 说明 |
|------|------|------|
| GET | 200 | 获取成功 |
| POST | 201 | 创建成功 |
| PUT | 200 | 更新成功 |
| DELETE | 200 | 删除成功（软删除） |
| 所有 | 400 | 参数错误 |
| 所有 | 401 | 未认证 |
| 所有 | 403 | 无权限 |
| 所有 | 404 | 资源不存在 |
| 所有 | 500 | 服务器错误 |

---

## 2. 通用约定

### 2.1 请求头

```
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Accept-Language: zh-CN
```

### 2.2 分页查询参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| page | integer | 1 | 页码 |
| pageSize | integer | 20 | 每页条数（max 100） |
| sortBy | string | createdAt | 排序字段 |
| order | string | desc | asc / desc |
| keyword | string | | 搜索关键词 |

### 2.3 权限标注说明

每个 API 标注所需权限，格式：`module:page:action`

| 层级 | 示例 |
|------|------|
| 模块 | `datasource` |
| 页面 | `datasource:list` |
| 操作 | `datasource:list:view`, `datasource:list:create`, `datasource:list:edit`, `datasource:list:delete` |

---

## 3. 认证模块

### POST /api/auth/login

| 属性 | 说明 |
|------|------|
| **用途** | 用户登录，获取 JWT Token |
| **权限** | 公开 |

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "accessToken": "eyJhbGciOi...",
    "refreshToken": "eyJhbGciOi...",
    "expiresIn": 7200,
    "user": {
      "id": "uuid",
      "username": "admin",
      "realName": "系统管理员",
      "email": "admin@example.com",
      "avatarUrl": "https://...",
      "roles": ["admin"],
      "permissions": ["datasource:list:view", "datasource:list:create", "..."]
    }
  }
}
```

### POST /api/auth/logout

| 属性 | 说明 |
|------|------|
| **用途** | 用户登出，Token 加入黑名单 |
| **权限** | 已登录 |

**Request:** (无 Body)

**Response:**
```json
{
  "code": 0,
  "message": "已登出"
}
```

### POST /api/auth/refresh

| 属性 | 说明 |
|------|------|
| **用途** | 使用 refreshToken 刷新 accessToken |
| **权限** | 公开（使用 refreshToken） |

**Request:**
```json
{
  "refreshToken": "eyJhbGciOi..."
}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "accessToken": "eyJhbGciOi...",
    "expiresIn": 7200
  }
}
```

### GET /api/auth/me

| 属性 | 说明 |
|------|------|
| **用途** | 获取当前登录用户信息 |
| **权限** | 已登录 |

**Response:**
```json
{
  "code": 0,
  "data": {
    "id": "uuid",
    "username": "admin",
    "realName": "系统管理员",
    "email": "admin@example.com",
    "phone": "13800138000",
    "avatarUrl": "https://...",
    "roles": [{"id": "uuid", "name": "admin", "description": "系统管理员"}],
    "permissions": ["*:*:*"],
    "lastLoginAt": "2026-08-06T08:00:00+08:00"
  }
}
```

---

## 4. 工作台模块

### GET /api/dashboard/overview

| 属性 | 说明 |
|------|------|
| **用途** | 获取运营总览数据（Dashboard 首页） |
| **权限** | `dashboard:overview:view` |

**Request:**
```
?timeRange=7d     // 7d / 30d / 90d
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "kpi": {
      "totalDataVolume": 1250000,
      "totalDataVolumeTrend": 12.5,
      "todayNewData": 3456,
      "todayNewDataTrend": -3.2,
      "normalOperationRate": 96.8,
      "normalOperationRateTrend": 0.5,
      "anomalyCount": 23,
      "anomalyCountTrend": -15.3,
      "deviceUtilization": 87.2,
      "deviceUtilizationTrend": 2.1
    },
    "dataVolumeTrend": [
      {"date": "2026-07-31", "value": 178000},
      {"date": "2026-08-01", "value": 182000},
      "..."
    ],
    "deviceStatusDistribution": [
      {"status": "normal", "count": 142, "percentage": 71.0},
      {"status": "abnormal", "count": 18, "percentage": 9.0},
      {"status": "offline", "count": 8, "percentage": 4.0},
      {"status": "maintenance", "count": 32, "percentage": 16.0}
    ],
    "anomalyTrend": [
      {"date": "2026-07-31", "count": 5},
      {"date": "2026-08-01", "count": 3},
      "..."
    ],
    "todos": {
      "pendingAlerts": 12,
      "pendingInspections": 5,
      "dataSourceErrors": 2,
      "dataQualityIssues": 3
    },
    "recentAlerts": [
      {
        "id": "uuid",
        "title": "设备 A-203 温度过高",
        "level": "critical",
        "triggeredAt": "2026-08-06T09:15:00+08:00"
      }
    ]
  }
}
```

### GET /api/dashboard/my-tasks

| 属性 | 说明 |
|------|------|
| **用途** | 获取当前用户的待办任务 |
| **权限** | 已登录 |

**Response:**
```json
{
  "code": 0,
  "data": {
    "alerts": [],
    "inspections": [],
    "reports": []
  }
}
```

### GET /api/dashboard/recent-views

| 属性 | 说明 |
|------|------|
| **用途** | 获取当前用户最近访问记录 |
| **权限** | 已登录 |

**Response:**
```json
{
  "code": 0,
  "data": [
    {"type": "dashboard", "id": "uuid", "name": "企业总览", "visitedAt": "..."},
    {"type": "dataset", "id": "uuid", "name": "设备运行数据", "visitedAt": "..."}
  ]
}
```

---

## 5. 数据源模块

### GET /api/data-sources

| 属性 | 说明 |
|------|------|
| **用途** | 获取数据源列表 |
| **权限** | `datasource:list:view` |

**Request:**
```
?page=1&pageSize=20&type=mysql&status=connected&keyword=生产
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": "uuid",
        "name": "生产环境 MySQL",
        "type": "mysql",
        "status": "connected",
        "dataVolume": 500000,
        "syncMethod": "incremental",
        "syncFrequency": "hourly",
        "lastSyncAt": "2026-08-06T09:00:00+08:00",
        "owner": {"id": "uuid", "realName": "张三"},
        "createdAt": "2026-06-01T10:00:00+08:00"
      }
    ],
    "total": 15,
    "page": 1,
    "pageSize": 20,
    "totalPages": 1
  }
}
```

### POST /api/data-sources

| 属性 | 说明 |
|------|------|
| **用途** | 新增数据源 |
| **权限** | `datasource:list:create` |

**Request:**
```json
{
  "name": "生产环境 MySQL",
  "type": "mysql",
  "description": "生产环境主数据库",
  "connectionConfig": {
    "host": "192.168.1.100",
    "port": 3306,
    "database": "production",
    "username": "readonly_user",
    "password": "encrypted_password"
  },
  "syncMethod": "incremental",
  "syncFrequency": "hourly",
  "ownerId": "uuid"
}
```

**Response:** (201)
```json
{
  "code": 0,
  "data": {
    "id": "uuid",
    "name": "生产环境 MySQL",
    "type": "mysql",
    "status": "disconnected",
    "..."
  }
}
```

### GET /api/data-sources/:id

| 属性 | 说明 |
|------|------|
| **用途** | 获取数据源详情 |
| **权限** | `datasource:detail:view` |

**Response:**
```json
{
  "code": 0,
  "data": {
    "id": "uuid",
    "name": "生产环境 MySQL",
    "type": "mysql",
    "description": "...",
    "connectionConfig": {
      "host": "192.168.1.100",
      "port": 3306,
      "database": "production",
      "username": "readonly_user"
    },
    "status": "connected",
    "dataVolume": 500000,
    "syncMethod": "incremental",
    "syncFrequency": "hourly",
    "lastSyncAt": "2026-08-06T09:00:00+08:00",
    "lastSyncStatus": "success",
    "owner": {"id": "uuid", "realName": "张三"},
    "tables": ["table1", "table2"],
    "syncHistory": [
      {"status": "success", "recordsSynced": 1234, "startedAt": "...", "finishedAt": "..."}
    ],
    "createdAt": "2026-06-01T10:00:00+08:00",
    "updatedAt": "2026-08-06T09:00:00+08:00"
  }
}
```

### PUT /api/data-sources/:id

| 属性 | 说明 |
|------|------|
| **用途** | 编辑数据源 |
| **权限** | `datasource:detail:edit` |

**Request:** (同 POST，部分字段可选)
```json
{
  "name": "生产环境 MySQL - 更新",
  "connectionConfig": { "...(部分更新)" },
  "syncFrequency": "daily"
}
```

### DELETE /api/data-sources/:id

| 属性 | 说明 |
|------|------|
| **用途** | 删除数据源（软删除） |
| **权限** | `datasource:detail:delete` |

### POST /api/data-sources/:id/test

| 属性 | 说明 |
|------|------|
| **用途** | 测试数据源连接 |
| **权限** | `datasource:detail:edit` |

**Response:**
```json
{
  "code": 0,
  "data": {
    "success": true,
    "latency": 45,
    "serverVersion": "MySQL 8.0.35",
    "message": "连接成功"
  }
}
```

### POST /api/data-sources/:id/sync

| 属性 | 说明 |
|------|------|
| **用途** | 手动触发数据同步 |
| **权限** | `datasource:detail:edit` |

**Response:**
```json
{
  "code": 0,
  "data": {
    "syncLogId": "uuid",
    "status": "running",
    "message": "同步任务已启动"
  }
}
```

---

## 6. 数据集模块

### GET /api/datasets

| 属性 | 说明 |
|------|------|
| **用途** | 获取数据集列表 |
| **权限** | `dataset:list:view` |

**Request:**
```
?page=1&pageSize=20&sourceId=uuid&keyword=设备
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": "uuid",
        "name": "设备运行数据集",
        "sourceName": "生产环境 MySQL",
        "fieldCount": 25,
        "dataVolume": 120000,
        "updatedAt": "2026-08-06T09:00:00+08:00",
        "owner": {"id": "uuid", "realName": "李四"}
      }
    ],
    "total": 30,
    "page": 1,
    "pageSize": 20,
    "totalPages": 2
  }
}
```

### POST /api/datasets

| 属性 | 说明 |
|------|------|
| **用途** | 新增数据集 |
| **权限** | `dataset:list:create` |

**Request:**
```json
{
  "name": "设备运行数据集",
  "description": "汇总设备运行数据",
  "sourceId": "uuid",
  "sourceTable": "device_operations",
  "queryConfig": {
    "joins": [],
    "defaultFilters": []
  },
  "fields": [
    {"fieldName": "device_id", "fieldAlias": "设备ID", "fieldType": "string", "isDimension": true},
    {"fieldName": "temperature", "fieldAlias": "温度", "fieldType": "number", "isMetric": true, "aggregation": "avg", "unit": "°C"}
  ]
}
```

### GET /api/datasets/:id

| 属性 | 说明 |
|------|------|
| **用途** | 获取数据集详情 |
| **权限** | `dataset:detail:view` |

### PUT /api/datasets/:id

| 属性 | 说明 |
|------|------|
| **用途** | 编辑数据集 |
| **权限** | `dataset:detail:edit` |

### DELETE /api/datasets/:id

| 属性 | 说明 |
|------|------|
| **用途** | 删除数据集（软删除） |
| **权限** | `dataset:detail:delete` |

### GET /api/datasets/:id/preview

| 属性 | 说明 |
|------|------|
| **用途** | 预览数据集数据（前 100 行） |
| **权限** | `dataset:detail:view` |

**Response:**
```json
{
  "code": 0,
  "data": {
    "fields": ["device_id", "temperature", "pressure", "timestamp"],
    "rows": [
      ["D001", 85.2, 101.3, "2026-08-06T09:00:00+08:00"],
      "..."
    ],
    "totalRows": 100
  }
}
```

---

## 7. 数据质量模块

### GET /api/data-quality/report

| 属性 | 说明 |
|------|------|
| **用途** | 获取数据质量总览报告 |
| **权限** | `dataquality:report:view` |

**Response:**
```json
{
  "code": 0,
  "data": {
    "overallScore": 95.8,
    "completenessRate": 98.5,
    "accuracyRate": 99.2,
    "duplicateRate": 0.8,
    "anomalyCount": 15,
    "bySource": [
      {
        "sourceId": "uuid",
        "sourceName": "生产环境 MySQL",
        "completenessRate": 98.5,
        "accuracyRate": 99.2,
        "duplicateRate": 0.8,
        "anomalyCount": 3
      }
    ]
  }
}
```

### GET /api/data-quality/details/:datasetId

| 属性 | 说明 |
|------|------|
| **用途** | 获取指定数据集的数据质量详情 |
| **权限** | `dataquality:report:view` |

---

## 8. 数据分析模块

### POST /api/analysis/trend

| 属性 | 说明 |
|------|------|
| **用途** | 执行趋势分析 |
| **权限** | `analysis:trend:view` |

**Request:**
```json
{
  "datasetId": "uuid",
  "metrics": [
    {"fieldName": "temperature", "aggregation": "avg"}
  ],
  "dimensions": ["time"],
  "timeRange": {
    "start": "2026-07-01T00:00:00+08:00",
    "end": "2026-08-06T23:59:59+08:00"
  },
  "granularity": "day",
  "filters": [
    {"field": "device_type", "operator": "eq", "value": "泵机"}
  ]
}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "chartData": [
      {"time": "2026-07-01", "value": 78.5},
      {"time": "2026-07-02", "value": 79.1},
      "..."
    ],
    "summary": {
      "avg": 80.2,
      "max": 92.5,
      "min": 65.3,
      "trend": "up",
      "changeRate": 5.2
    },
    "insights": [
      "温度在 7 月中旬出现明显上升趋势，涨幅约 8%",
      "8月1日出现异常峰值 92.5°C，需关注"
    ],
    "tableData": {
      "columns": ["time", "value"],
      "rows": []
    }
  }
}
```

### POST /api/analysis/compare

| 属性 | 说明 |
|------|------|
| **用途** | 执行对比分析（同比/环比/自定义） |
| **权限** | `analysis:compare:view` |

**Request:**
```json
{
  "datasetId": "uuid",
  "metrics": [{"fieldName": "device_utilization", "aggregation": "avg"}],
  "compareType": "yoy",
  "currentPeriod": {"start": "2026-08-01", "end": "2026-08-06"},
  "basePeriod": {"start": "2025-08-01", "end": "2025-08-06"},
  "granularity": "day"
}
```

### POST /api/analysis/anomaly

| 属性 | 说明 |
|------|------|
| **用途** | 执行异常分析 |
| **权限** | `analysis:anomaly:view` |

**Request:**
```json
{
  "datasetId": "uuid",
  "metric": {"fieldName": "temperature", "aggregation": "avg"},
  "timeRange": {"start": "2026-07-01T00:00:00+08:00", "end": "2026-08-06T23:59:59+08:00"},
  "method": "statistical",
  "sensitivity": 0.95
}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "anomalies": [
      {
        "time": "2026-08-01T14:00:00+08:00",
        "actualValue": 92.5,
        "expectedValue": 80.2,
        "deviation": 15.3,
        "severity": "high",
        "anomalyType": "spike"
      }
    ],
    "summary": {
      "totalAnomalies": 5,
      "bySeverity": {"critical": 1, "high": 2, "medium": 2, "low": 0},
      "byType": {"spike": 3, "drop": 1, "trend_change": 1}
    }
  }
}
```

### POST /api/analysis/ranking

| 属性 | 说明 |
|------|------|
| **用途** | 执行排名分析（Top N / Bottom N） |
| **权限** | `analysis:ranking:view` |

**Request:**
```json
{
  "datasetId": "uuid",
  "metric": {"fieldName": "device_utilization", "aggregation": "avg"},
  "dimension": "device_type",
  "timeRange": {"start": "2026-07-01", "end": "2026-08-06"},
  "limit": 10,
  "order": "desc"
}
```

---

## 9. 看板模块

### GET /api/dashboards

| 属性 | 说明 |
|------|------|
| **用途** | 获取看板列表 |
| **权限** | `dashboard:list:view` |

### POST /api/dashboards

| 属性 | 说明 |
|------|------|
| **用途** | 创建自定义看板 |
| **权限** | `dashboard:list:create` |

**Request:**
```json
{
  "name": "我的运营看板",
  "description": "个人关注的运营指标",
  "category": "custom",
  "layout": {"cols": 12, "rowHeight": 100}
}
```

### GET /api/dashboards/:id

| 属性 | 说明 |
|------|------|
| **用途** | 获取看板详情（含所有组件配置和数据） |
| **权限** | `dashboard:detail:view` |

**Response:**
```json
{
  "code": 0,
  "data": {
    "id": "uuid",
    "name": "企业运营总览",
    "description": "...",
    "category": "enterprise",
    "autoRefresh": true,
    "refreshInterval": 60,
    "widgets": [
      {
        "id": "uuid",
        "name": "正常运行率",
        "type": "stat_card",
        "config": {
          "datasetId": "uuid",
          "metric": {"fieldName": "normal_rate", "aggregation": "avg"},
          "unit": "%",
          "precision": 1
        },
        "position": {"x": 0, "y": 0, "w": 3, "h": 2},
        "data": {"value": 96.8, "trend": 0.5}
      }
    ],
    "createdAt": "...",
    "updatedAt": "..."
  }
}
```

### PUT /api/dashboards/:id

| 属性 | 说明 |
|------|------|
| **用途** | 编辑看板（名称、布局等） |
| **权限** | `dashboard:detail:edit` |

### DELETE /api/dashboards/:id

| 属性 | 说明 |
|------|------|
| **用途** | 删除看板 |
| **权限** | `dashboard:detail:delete` |

### POST /api/dashboards/:id/widgets

| 属性 | 说明 |
|------|------|
| **用途** | 向看板添加图表组件 |
| **权限** | `dashboard:detail:edit` |

**Request:**
```json
{
  "name": "温度趋势图",
  "type": "line_chart",
  "config": {
    "datasetId": "uuid",
    "metrics": [{"fieldName": "temperature", "aggregation": "avg"}],
    "dimensions": ["time"],
    "timeRange": {"preset": "last_7_days"},
    "granularity": "hour"
  },
  "position": {"x": 3, "y": 0, "w": 6, "h": 4}
}
```

### PUT /api/dashboards/:id/widgets/:widgetId

| 属性 | 说明 |
|------|------|
| **用途** | 编辑看板组件 |
| **权限** | `dashboard:detail:edit` |

### DELETE /api/dashboards/:id/widgets/:widgetId

| 属性 | 说明 |
|------|------|
| **用途** | 删除看板组件 |
| **权限** | `dashboard:detail:edit` |

---

## 10. 预警模块

### GET /api/alerts

| 属性 | 说明 |
|------|------|
| **用途** | 获取活跃预警列表 |
| **权限** | `alert:list:view` |

**Request:**
```
?status=pending&level=critical&page=1&pageSize=20&sortBy=triggeredAt&order=desc
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": "uuid",
        "title": "设备 A-203 温度过高",
        "level": "critical",
        "status": "pending",
        "metricName": "温度",
        "currentValue": 92.5,
        "thresholdValue": 80.0,
        "condition": "gt",
        "triggeredAt": "2026-08-06T09:15:00+08:00",
        "duration": "15分钟",
        "assignee": {"id": "uuid", "realName": "王五"}
      }
    ],
    "total": 23,
    "statistics": {
      "critical": 1,
      "high": 3,
      "medium": 8,
      "low": 11
    }
  }
}
```

### GET /api/alerts/:id

| 属性 | 说明 |
|------|------|
| **用途** | 获取预警详情 |
| **权限** | `alert:detail:view` |

### PUT /api/alerts/:id/process

| 属性 | 说明 |
|------|------|
| **用途** | 标记预警为处理中 |
| **权限** | `alert:detail:process` |

**Request:**
```json
{
  "note": "已联系现场人员核实"
}
```

### PUT /api/alerts/:id/close

| 属性 | 说明 |
|------|------|
| **用途** | 关闭预警 |
| **权限** | `alert:detail:close` |

**Request:**
```json
{
  "processNote": "散热风扇已更换，温度恢复正常",
  "resolution": "repaired"
}
```

### GET /api/alerts/records

| 属性 | 说明 |
|------|------|
| **用途** | 获取预警历史记录（含已关闭） |
| **权限** | `alert:records:view` |

### GET /api/alerts/processed

| 属性 | 说明 |
|------|------|
| **用途** | 获取已处理的预警列表 |
| **权限** | `alert:records:view` |

---

## 11. 预警规则模块

### GET /api/alert-rules

| 属性 | 说明 |
|------|------|
| **用途** | 获取预警规则列表 |
| **权限** | `alertrule:list:view` |

### POST /api/alert-rules

| 属性 | 说明 |
|------|------|
| **用途** | 创建预警规则 |
| **权限** | `alertrule:list:create` |

**Request:**
```json
{
  "name": "设备温度过高预警",
  "description": "当设备温度超过 80°C 且持续 5 分钟时触发",
  "metricId": "uuid",
  "condition": "gt",
  "threshold": 80.0,
  "duration": 300,
  "level": "high",
  "assigneeId": "uuid",
  "notifyMethods": ["system", "email", "sms"],
  "cooldown": 600
}
```

### GET /api/alert-rules/:id

| 属性 | 说明 |
|------|------|
| **用途** | 获取预警规则详情 |
| **权限** | `alertrule:detail:view` |

### PUT /api/alert-rules/:id

| 属性 | 说明 |
|------|------|
| **用途** | 编辑预警规则 |
| **权限** | `alertrule:detail:edit` |

### DELETE /api/alert-rules/:id

| 属性 | 说明 |
|------|------|
| **用途** | 删除预警规则 |
| **权限** | `alertrule:detail:delete` |

### PUT /api/alert-rules/:id/toggle

| 属性 | 说明 |
|------|------|
| **用途** | 启用/禁用预警规则 |
| **权限** | `alertrule:detail:edit` |

**Request:**
```json
{
  "enabled": false
}
```

---

## 12. 巡检模块

### GET /api/inspections/tasks

| 属性 | 说明 |
|------|------|
| **用途** | 获取巡检任务列表 |
| **权限** | `inspection:task:view` |

**Request:**
```
?status=pending&assigneeId=uuid&page=1&pageSize=20
```

### POST /api/inspections/tasks

| 属性 | 说明 |
|------|------|
| **用途** | 创建巡检任务（手动创建） |
| **权限** | `inspection:task:create` |

**Request:**
```json
{
  "planId": "uuid",
  "name": "8月6日设备温度巡检",
  "scope": "by_device",
  "deviceIds": ["uuid1", "uuid2"],
  "assigneeId": "uuid",
  "scheduledAt": "2026-08-06T14:00:00+08:00"
}
```

### PUT /api/inspections/tasks/:id

| 属性 | 说明 |
|------|------|
| **用途** | 更新巡检任务 |
| **权限** | `inspection:task:edit` |

### PUT /api/inspections/tasks/:id/execute

| 属性 | 说明 |
|------|------|
| **用途** | 执行巡检并记录结果 |
| **权限** | `inspection:task:execute` |

**Request:**
```json
{
  "records": [
    {
      "deviceId": "uuid",
      "result": "abnormal",
      "detail": {"temperature": 85.2, "pressure": 101.3},
      "anomalyDesc": "温度超过正常范围"
    }
  ],
  "overallResult": "abnormal",
  "notes": "已通知维修团队"
}
```

### GET /api/inspections/plans

| 属性 | 说明 |
|------|------|
| **用途** | 获取巡检计划列表 |
| **权限** | `inspection:plan:view` |

### POST /api/inspections/plans

| 属性 | 说明 |
|------|------|
| **用途** | 创建巡检计划 |
| **权限** | `inspection:plan:create` |

### GET /api/inspections/records

| 属性 | 说明 |
|------|------|
| **用途** | 获取巡检记录列表 |
| **权限** | `inspection:record:view` |

### GET /api/inspections/abnormal-devices

| 属性 | 说明 |
|------|------|
| **用途** | 获取异常设备列表 |
| **权限** | `inspection:device:view` |

---

## 13. 报表模块

### GET /api/reports

| 属性 | 说明 |
|------|------|
| **用途** | 获取报表列表 |
| **权限** | `report:list:view` |

### POST /api/reports/generate

| 属性 | 说明 |
|------|------|
| **用途** | 生成报表 |
| **权限** | `report:list:generate` |

**Request:**
```json
{
  "name": "8月第一周运营周报",
  "type": "weekly",
  "config": {
    "dashboardId": "uuid",
    "metrics": [],
    "timeRange": {"start": "2026-08-01", "end": "2026-08-07"}
  },
  "fileFormat": "pdf"
}
```

### GET /api/reports/:id/download

| 属性 | 说明 |
|------|------|
| **用途** | 下载报表文件 |
| **权限** | `report:list:view` |
| **响应** | 文件流 (Content-Disposition: attachment) |

### POST /api/reports/schedules

| 属性 | 说明 |
|------|------|
| **用途** | 创建定时报表 |
| **权限** | `report:schedule:create` |

### GET /api/reports/schedules

| 属性 | 说明 |
|------|------|
| **用途** | 获取定时报表配置列表 |
| **权限** | `report:schedule:view` |

### GET /api/reports/export-records

| 属性 | 说明 |
|------|------|
| **用途** | 获取导出记录 |
| **权限** | `report:export:view` |

---

## 14. 用户管理模块

### GET /api/users

| 属性 | 说明 |
|------|------|
| **用途** | 获取用户列表 |
| **权限** | `user:list:view` |

### POST /api/users

| 属性 | 说明 |
|------|------|
| **用途** | 新增用户 |
| **权限** | `user:list:create` |

**Request:**
```json
{
  "username": "new_analyst",
  "password": "Temp@123456",
  "realName": "张分析",
  "email": "analyst@example.com",
  "phone": "13900001111",
  "roleIds": ["uuid-of-analyst-role"]
}
```

### GET /api/users/:id

| 属性 | 说明 |
|------|------|
| **用途** | 获取用户详情 |
| **权限** | `user:detail:view` |

### PUT /api/users/:id

| 属性 | 说明 |
|------|------|
| **用途** | 编辑用户信息 |
| **权限** | `user:detail:edit` |

### PUT /api/users/:id/status

| 属性 | 说明 |
|------|------|
| **用途** | 禁用/启用用户 |
| **权限** | `user:detail:edit` |

**Request:**
```json
{
  "status": "disabled"
}
```

### POST /api/users/:id/reset-password

| 属性 | 说明 |
|------|------|
| **用途** | 重置用户密码 |
| **权限** | `user:detail:edit` |

**Request:**
```json
{
  "newPassword": "NewPass@123456"
}
```

---

## 15. 角色管理模块

### GET /api/roles

| 属性 | 说明 |
|------|------|
| **用途** | 获取角色列表 |
| **权限** | `role:list:view` |

**Response:**
```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": "uuid",
        "name": "admin",
        "description": "系统管理员",
        "isSystem": true,
        "userCount": 2,
        "createdAt": "..."
      }
    ]
  }
}
```

### POST /api/roles

| 属性 | 说明 |
|------|------|
| **用途** | 新增角色 |
| **权限** | `role:list:create` |

### GET /api/roles/:id

| 属性 | 说明 |
|------|------|
| **用途** | 获取角色详情（含权限树） |
| **权限** | `role:detail:view` |

### PUT /api/roles/:id

| 属性 | 说明 |
|------|------|
| **用途** | 编辑角色 |
| **权限** | `role:detail:edit` |

### PUT /api/roles/:id/permissions

| 属性 | 说明 |
|------|------|
| **用途** | 配置角色权限 |
| **权限** | `role:detail:edit` |

**Request:**
```json
{
  "permissionIds": ["uuid1", "uuid2", "uuid3"]
}
```

### DELETE /api/roles/:id

| 属性 | 说明 |
|------|------|
| **用途** | 删除角色（系统角色不可删除） |
| **权限** | `role:detail:delete` |

### GET /api/permissions

| 属性 | 说明 |
|------|------|
| **用途** | 获取所有权限列表（用于权限配置树） |
| **权限** | `role:list:view` |

---

## 16. 日志模块

### GET /api/logs

| 属性 | 说明 |
|------|------|
| **用途** | 查询操作日志 |
| **权限** | `log:list:view` |

**Request:**
```
?userId=uuid&module=datasource&action=delete&startDate=2026-08-01&endDate=2026-08-06&page=1&pageSize=20
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": "uuid",
        "username": "admin",
        "module": "datasource",
        "action": "delete",
        "targetType": "data_source",
        "targetId": "uuid",
        "detail": {"before": {"name": "旧名称"}, "after": null},
        "ipAddress": "192.168.1.50",
        "status": "success",
        "createdAt": "2026-08-06T10:00:00+08:00"
      }
    ],
    "total": 500,
    "page": 1,
    "pageSize": 20,
    "totalPages": 25
  }
}
```

### GET /api/logs/:id

| 属性 | 说明 |
|------|------|
| **用途** | 获取日志详情 |
| **权限** | `log:detail:view` |

### POST /api/logs/export

| 属性 | 说明 |
|------|------|
| **用途** | 导出操作日志 |
| **权限** | `log:list:export` |

---

## 17. 系统配置模块

### GET /api/settings

| 属性 | 说明 |
|------|------|
| **用途** | 获取系统配置 |
| **权限** | `setting:view` |

### PUT /api/settings

| 属性 | 说明 |
|------|------|
| **用途** | 更新系统配置 |
| **权限** | `setting:edit` |

**Request:**
```json
{
  "settings": [
    {"key": "system.name", "value": "DataInsight"},
    {"key": "system.logoUrl", "value": "https://..."},
    {"key": "alert.defaultCooldown", "value": "600"}
  ]
}
```

---

## 18. 版本模块

### GET /api/versions

| 属性 | 说明 |
|------|------|
| **用途** | 获取版本列表 |
| **权限** | 已登录 |

**Response:**
```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": "uuid",
        "versionNumber": "1.0.0",
        "versionName": "MVP",
        "releaseDate": "2026-09-01",
        "status": "developing",
        "isCurrent": true,
        "changelog": [
          {"type": "feature", "description": "数据源管理与数据采集"},
          {"type": "feature", "description": "数据集管理与数据预览"},
          "..."
        ]
      }
    ]
  }
}
```

### GET /api/versions/current

| 属性 | 说明 |
|------|------|
| **用途** | 获取当前版本信息 |
| **权限** | 公开 |

---

## 19. 通用模块

### GET /api/notifications

| 属性 | 说明 |
|------|------|
| **用途** | 获取当前用户通知列表 |
| **权限** | 已登录 |

### PUT /api/notifications/:id/read

| 属性 | 说明 |
|------|------|
| **用途** | 标记通知已读 |
| **权限** | 已登录 |

### PUT /api/notifications/read-all

| 属性 | 说明 |
|------|------|
| **用途** | 全部标为已读 |
| **权限** | 已登录 |

### GET /api/notifications/unread-count

| 属性 | 说明 |
|------|------|
| **用途** | 获取未读通知数量 |
| **权限** | 已登录 |

### POST /api/upload

| 属性 | 说明 |
|------|------|
| **用途** | 文件上传（图片、CSV等） |
| **权限** | 已登录 |
| **请求格式** | multipart/form-data |

### GET /api/export/:type

| 属性 | 说明 |
|------|------|
| **用途** | 通用数据导出 |
| **权限** | 按模块 |
| **Query** | 各模块的筛选参数 |

---

## 20. WebSocket 事件

| 事件名 | 方向 | 说明 |
|--------|------|------|
| `connect` | C→S | 建立连接（携带 Token 认证） |
| `alert:new` | S→C | 新预警推送 |
| `alert:update` | S→C | 预警状态更新 |
| `dashboard:refresh` | S→C | 看板数据刷新 |
| `datasource:sync-status` | S→C | 数据同步状态更新 |
| `notification:new` | S→C | 新通知推送 |
| `system:status` | S→C | 系统状态变更 |

### WebSocket 连接

```javascript
const socket = io('ws://localhost:3000', {
  auth: {
    token: 'eyJhbGciOi...'
  }
});

socket.on('alert:new', (data) => {
  console.log('新预警:', data);
  // data: { id, title, level, triggeredAt }
});
```

---

## 附录 A: 状态枚举

### 数据源类型
```
mysql, postgresql, mongodb, api, csv, excel
```

### 数据源状态
```
connected, disconnected, error
```

### 同步方式
```
full, incremental
```

### 同步频率
```
manual, hourly, daily, weekly, custom
```

### 设备状态
```
normal, abnormal, offline, maintenance
```

### 预警等级
```
low, medium, high, critical
```

### 预警状态
```
pending, processing, closed
```

### 预警条件
```
gt (>), lt (<), gte (>=), lte (<=), eq (=), neq (!=)
```

### 巡检结果
```
normal, abnormal, attention_needed
```

### 报表类型
```
daily, weekly, monthly, custom
```

### 报表状态
```
pending, generating, completed, failed
```

### 用户状态
```
active, disabled
```

### 版本状态
```
planning, developing, testing, released, deprecated
```

---

> **文档维护**：API 变更必须同步更新本文档。所有接口需在实现前完成评审。
