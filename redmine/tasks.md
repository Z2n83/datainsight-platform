# DataInsight — Task 拆解

> **Project**：DataInsight | **Tracker**：Task | **日期**：2026-08-06

---

## Task 列表（按 Story 拆解）

### STORY-001：前端项目脚手架搭建

| Task ID | 标题 | 类型 | 优先级 | 负责人 | 预估(h) |
|---------|------|------|--------|--------|---------|
| TASK-001 | 使用 Vite 创建 React + TypeScript 项目 | Task | Urgent | 前端 Lead | 2 |
| TASK-002 | 配置 ESLint + Prettier + Husky | Task | Urgent | 前端 Lead | 2 |
| TASK-003 | 集成 Ant Design 5 + 主题配置 | Task | Urgent | 前端 | 3 |
| TASK-004 | 配置 React Router v6 路由表 | Task | Urgent | 前端 | 3 |
| TASK-005 | 集成 Zustand 全局状态管理 | Task | High | 前端 | 2 |
| TASK-006 | 集成 React Query 服务端状态管理 | Task | High | 前端 | 2 |
| TASK-007 | 封装 Axios HTTP Client（拦截器+Token管理） | Task | Urgent | 前端 | 3 |
| TASK-008 | 配置路径别名和 Vite 构建优化 | Task | Medium | 前端 | 1 |

### STORY-002：后端项目脚手架搭建

| Task ID | 标题 | 类型 | 优先级 | 负责人 | 预估(h) |
|---------|------|------|--------|--------|---------|
| TASK-009 | 初始化 Node.js + TypeScript 项目 | Task | Urgent | 后端 Lead | 2 |
| TASK-010 | 集成 Prisma ORM + PostgreSQL 连接 | Task | Urgent | 后端 Lead | 3 |
| TASK-011 | 实现请求日志中间件 | Task | High | 后端 | 2 |
| TASK-012 | 实现统一错误处理中间件 | Task | Urgent | 后端 | 3 |
| TASK-013 | 实现 CORS + Rate Limit 中间件 | Task | High | 后端 | 2 |
| TASK-014 | 实现请求参数校验中间件（Joi/Zod） | Task | High | 后端 | 3 |
| TASK-015 | 搭建模块化路由结构 | Task | Urgent | 后端 Lead | 3 |
| TASK-016 | 配置环境变量管理（dotenv） | Task | Medium | 后端 | 1 |

### STORY-003：数据库 Migration 体系搭建

| Task ID | 标题 | 类型 | 优先级 | 负责人 | 预估(h) |
|---------|------|------|--------|--------|---------|
| TASK-017 | 编写 users 表 Migration | Task | Urgent | 后端 | 1 |
| TASK-018 | 编写 roles + permissions 表 Migration | Task | Urgent | 后端 | 2 |
| TASK-019 | 编写 user_roles + role_permissions 表 Migration | Task | Urgent | 后端 | 1 |
| TASK-020 | 编写 data_sources + datasets 表 Migration | Task | Urgent | 后端 | 2 |
| TASK-021 | 编写 devices + metrics + metric_values 表 Migration | Task | High | 后端 | 3 |
| TASK-022 | 编写 alerts + alert_rules 表 Migration | Task | High | 后端 | 2 |
| TASK-023 | 编写 inspection 相关表 Migration | Task | Medium | 后端 | 2 |
| TASK-024 | 编写 dashboards + widgets 表 Migration | Task | High | 后端 | 2 |
| TASK-025 | 编写 reports + logs + settings + versions 表 Migration | Task | Medium | 后端 | 3 |
| TASK-026 | 编写种子数据脚本（角色+权限+管理员） | Task | Urgent | 后端 | 4 |
| TASK-027 | 编写种子数据脚本（Demo数据） | Task | Medium | 后端 | 4 |

### STORY-004：JWT 认证系统实现

| Task ID | 标题 | 类型 | 优先级 | 负责人 | 预估(h) |
|---------|------|------|--------|--------|---------|
| TASK-028 | 实现 AuthController（login/logout/refresh/me） | Task | Urgent | 后端 | 4 |
| TASK-029 | 实现 AuthService（密码验证 + Token 生成） | Task | Urgent | 后端 | 4 |
| TASK-030 | 实现 JWT 认证中间件 | Task | Urgent | 后端 | 3 |
| TASK-031 | 实现 Refresh Token 机制 | Task | High | 后端 | 3 |
| TASK-032 | 实现登录失败锁定逻辑 | Task | Medium | 后端 | 2 |

### STORY-005：前端登录页面

| Task ID | 标题 | 类型 | 优先级 | 负责人 | 预估(h) |
|---------|------|------|--------|--------|---------|
| TASK-033 | 实现 LoginPage UI（Ant Design Form） | Task | Urgent | 前端 | 4 |
| TASK-034 | 实现登录逻辑（API 调用 + Token 存储） | Task | Urgent | 前端 | 2 |
| TASK-035 | 实现 Token 自动刷新 + 401 拦截跳转 | Task | Urgent | 前端 | 2 |
| TASK-036 | 实现路由守卫（AuthGuard） | Task | Urgent | 前端 | 2 |

### STORY-006：通用 Layout 与导航

| Task ID | 标题 | 类型 | 优先级 | 负责人 | 预估(h) |
|---------|------|------|--------|--------|---------|
| TASK-037 | 实现 AppLayout 组件（Sider + Header + Content） | Task | Urgent | 前端 | 4 |
| TASK-038 | 实现侧边导航菜单（根据路由+权限生成） | Task | Urgent | 前端 | 3 |
| TASK-039 | 实现顶部栏（用户头像下拉 + 通知Badge + 退出） | Task | High | 前端 | 3 |
| TASK-040 | 实现面包屑导航组件 | Task | Medium | 前端 | 2 |
| TASK-041 | 实现 403/404 页面 | Task | Medium | 前端 | 2 |

### STORY-013：数据源 CRUD API

| Task ID | 标题 | 类型 | 优先级 | 负责人 | 预估(h) |
|---------|------|------|--------|--------|---------|
| TASK-042 | 实现 DataSource Model + Repository | Task | Urgent | 后端 | 2 |
| TASK-043 | 实现 DataSourceController（CRUD） | Task | Urgent | 后端 | 4 |
| TASK-044 | 实现 DataSourceService（业务逻辑） | Task | Urgent | 后端 | 4 |
| TASK-045 | 实现数据源参数校验（Zod Schema） | Task | High | 后端 | 2 |

### STORY-014：MySQL 数据源连接测试

| Task ID | 标题 | 类型 | 优先级 | 负责人 | 预估(h) |
|---------|------|------|--------|--------|---------|
| TASK-046 | 实现 MySQL 连接驱动封装 | Task | Urgent | 后端 | 3 |
| TASK-047 | 实现连接测试接口逻辑 | Task | Urgent | 后端 | 2 |
| TASK-048 | 实现连接信息加密存储 | Task | High | 后端 | 2 |

### STORY-016：数据源列表页面

| Task ID | 标题 | 类型 | 优先级 | 负责人 | 预估(h) |
|---------|------|------|--------|--------|---------|
| TASK-049 | 实现 DataSourceListPage UI | Task | Urgent | 前端 | 6 |
| TASK-050 | 实现 DataSourceTable 组件（状态标签+操作按钮） | Task | Urgent | 前端 | 3 |
| TASK-051 | 实现 SearchBar + FilterBar 组件 | Task | High | 前端 | 3 |
| TASK-052 | 实现 CreateDataSourceModal 组件 | Task | Urgent | 前端 | 4 |

### STORY-026：指标计算引擎

| Task ID | 标题 | 类型 | 优先级 | 负责人 | 预估(h) |
|---------|------|------|--------|--------|---------|
| TASK-053 | 实现动态 SQL 查询构建器 | Task | Urgent | 后端 | 6 |
| TASK-054 | 实现聚合函数计算逻辑（SUM/AVG/COUNT/MAX/MIN） | Task | Urgent | 后端 | 4 |
| TASK-055 | 实现时间粒度聚合（时/日/周/月/季/年） | Task | Urgent | 后端 | 4 |
| TASK-056 | 实现多维度分组查询 | Task | High | 后端 | 4 |
| TASK-057 | 实现指标摘要计算（均值/最大/最小/趋势） | Task | High | 后端 | 3 |
| TASK-058 | 实现查询结果缓存（Redis） | Task | Medium | 后端 | 3 |

### STORY-027：指标分析工作台页面

| Task ID | 标题 | 类型 | 优先级 | 负责人 | 预估(h) |
|---------|------|------|--------|--------|---------|
| TASK-059 | 实现 AnalysisWorkbench 页面布局 | Task | Urgent | 前端 | 4 |
| TASK-060 | 实现 DatasetSelector 组件 | Task | Urgent | 前端 | 3 |
| TASK-061 | 实现 MetricSelector 组件（多选+聚合函数） | Task | Urgent | 前端 | 3 |
| TASK-062 | 实现 DimensionSelector 组件 | Task | Urgent | 前端 | 2 |
| TASK-063 | 实现 TimeRangePicker 组件（预设+自定义） | Task | Urgent | 前端 | 3 |
| TASK-064 | 实现 FilterBuilder 组件（字段+操作符+值+AND/OR） | Task | High | 前端 | 5 |
| TASK-065 | 实现 AnalysisResult 区域（Chart + Table + Summary） | Task | Urgent | 前端 | 6 |
| TASK-066 | 实现 InsightCard 数据洞察组件 | Task | Medium | 前端 | 3 |

### STORY-034：运营总览 Dashboard

| Task ID | 标题 | 类型 | 优先级 | 负责人 | 预估(h) |
|---------|------|------|--------|--------|---------|
| TASK-067 | 实现 DashboardPage 整体布局 | Task | Urgent | 前端 | 2 |
| TASK-068 | 实现 StatCard KPI 卡片组件 | Task | Urgent | 前端 | 3 |
| TASK-069 | 实现 TrendChart 趋势图组件 | Task | Urgent | 前端 | 4 |
| TASK-070 | 实现 StatusPieChart 状态分布图组件 | Task | High | 前端 | 3 |
| TASK-071 | 实现 TodoList 待办列表组件 | Task | High | 前端 | 3 |
| TASK-072 | 实现 Dashboard 数据聚合 API | Task | Urgent | 后端 | 5 |
| TASK-073 | 实现时间范围切换联动 | Task | High | 前端 | 2 |

### STORY-044：预警规则引擎（v1.1）

| Task ID | 标题 | 类型 | 优先级 | 负责人 | 预估(h) |
|---------|------|------|--------|--------|---------|
| TASK-074 | 实现 AlertRuleEngine 规则评估逻辑 | Task | Urgent | 后端 | 6 |
| TASK-075 | 实现冷却时间机制 | Task | High | 后端 | 2 |
| TASK-076 | 实现预警检测定时任务（Cron） | Task | Urgent | 后端 | 4 |
| TASK-077 | 实现 AlertRule CRUD API | Task | Urgent | 后端 | 4 |

### STORY-048：实时预警列表（v1.1）

| Task ID | 标题 | 类型 | 优先级 | 负责人 | 预估(h) |
|---------|------|------|--------|--------|---------|
| TASK-078 | 实现 AlertListPage UI | Task | Urgent | 前端 | 4 |
| TASK-079 | 实现 AlertStatCards 统计卡片 | Task | High | 前端 | 2 |
| TASK-080 | 实现 AlertTable 组件（实时刷新） | Task | Urgent | 前端 | 4 |
| TASK-081 | 实现 WebSocket 实时预警推送（前端） | Task | High | 前端 | 3 |
| TASK-082 | 实现 WebSocket 实时预警推送（后端） | Task | High | 后端 | 4 |
| TASK-083 | 实现 AlertDetailDrawer 详情抽屉 | Task | High | 前端 | 3 |

---

## Task 统计

| 模块 | Task 数量 | 总预估工时(h) |
|------|-----------|---------------|
| 前端脚手架 | 8 | 18 |
| 后端脚手架 | 8 | 19 |
| 数据库 | 11 | 26 |
| 认证系统 | 9 | 22 |
| 前端 Layout | 5 | 14 |
| 数据源 | 11 | 28 |
| 数据集 | 8 | 22 |
| 数据分析 | 16 | 48 |
| 可视化看板 | 15 | 43 |
| 预警中心 | 10 | 30 |
| 巡检 | 8 | 24 |
| 报表 | 6 | 18 |
| 权限管理 | 8 | 24 |
| 测试 | 6 | 20 |
| 部署与文档 | 5 | 14 |
| **合计** | **134** | **370** |

---

> **文档维护**：Task 状态在 Redmine 中每日更新，本文档提供规划概览。
