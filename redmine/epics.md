# DataInsight — Redmine Epic 规划

> **Project**：DataInsight | **Tracker**：Epic | **日期**：2026-08-06

---

## Epic 总览

| Epic ID | 名称 | 模块 | 版本 | 优先级 | 状态 |
|---------|------|------|------|--------|------|
| EPIC-001 | 产品基础架构 | Product + Backend + Frontend | v1.0 MVP | Urgent | In Progress |
| EPIC-002 | 数据管理 | Data + Backend + Frontend | v1.0 MVP | Urgent | In Progress |
| EPIC-003 | 数据分析 | Backend + Frontend | v1.0 MVP | High | Planned |
| EPIC-004 | 可视化看板 | Frontend | v1.0 MVP | High | Planned |
| EPIC-005 | 预警中心 | Backend + Frontend | v1.1 Analysis | High | Planned |
| EPIC-006 | 智能巡检 | Backend + Frontend | v1.2 | Medium | Planned |
| EPIC-007 | 数据报表 | Backend + Frontend | v1.2 | Medium | Planned |
| EPIC-008 | 权限管理 | Backend + Frontend | v1.2 | High | Planned |
| EPIC-009 | 测试与性能优化 | Testing | v1.0 ~ v1.2 | High | Planned |
| EPIC-010 | 产品上线与版本迭代 | Release | v1.0 ~ v2.0 | Medium | Planned |

---

## EPIC-001：产品基础架构

**描述**：
搭建 DataInsight 平台的基础技术架构，包括前端项目脚手架、后端项目脚手架、数据库初始化、认证系统、通用组件库。本 Epic 是所有后续功能开发的基础。

**优先级**：Urgent  
**版本**：v1.0 MVP  
**负责人**：技术负责人 + 前端 Lead + 后端 Lead

### 包含的 Story

| Story ID | 标题 | 优先级 | 负责人 |
|----------|------|--------|--------|
| STORY-001 | 前端项目脚手架搭建（React + TypeScript + Vite） | Urgent | 前端 Lead |
| STORY-002 | 后端项目脚手架搭建（Node.js + Express/NestJS + Prisma） | Urgent | 后端 Lead |
| STORY-003 | 数据库 Migration 体系搭建 | Urgent | 后端 Lead |
| STORY-004 | JWT 认证系统实现 | Urgent | 后端 |
| STORY-005 | 前端登录页面与认证流程 | Urgent | 前端 |
| STORY-006 | 通用 Layout 与导航组件 | High | 前端 |
| STORY-007 | RBAC 基础权限模型（用户/角色/权限表 + 种子数据） | Urgent | 后端 |
| STORY-008 | Docker Compose 开发环境搭建 | High | 后端 |
| STORY-009 | API 通用响应格式与错误处理中间件 | High | 后端 |
| STORY-010 | 前端 HTTP Client 封装（Axios + 拦截器） | High | 前端 |
| STORY-011 | 操作日志中间件 | High | 后端 |
| STORY-012 | 系统配置管理（KV 存储） | Medium | 后端 |

### 验收标准
- [ ] 前后端项目可本地启动并通信
- [ ] JWT 登录/登出/刷新流程完整可用
- [ ] 5 个预置角色和 50+ 权限的种子数据正确加载
- [ ] Docker Compose 一键启动所有基础设施服务
- [ ] API 错误响应格式统一
- [ ] 前端 Axios 拦截器正确处理 401/403
- [ ] 所有 API 调用可被操作日志记录

---

## EPIC-002：数据管理

**描述**：
实现数据源连接管理、数据集管理、基础数据清洗、数据同步功能。建立从外部数据到可分析数据集的完整数据链路。

**优先级**：Urgent  
**版本**：v1.0 MVP  
**负责人**：后端 Lead + 数据分析师

### 包含的 Story

| Story ID | 标题 | 优先级 | 负责人 |
|----------|------|--------|--------|
| STORY-013 | 数据源 CRUD API | Urgent | 后端 |
| STORY-014 | MySQL 数据源连接与测试 | Urgent | 后端 |
| STORY-015 | CSV 文件导入数据源 | Urgent | 后端 |
| STORY-016 | 数据源列表页面 | Urgent | 前端 |
| STORY-017 | 数据源详情页面 | Urgent | 前端 |
| STORY-018 | 数据源手动全量同步 | High | 后端 |
| STORY-019 | 数据集 CRUD API | Urgent | 后端 |
| STORY-020 | 数据集列表页面 | Urgent | 前端 |
| STORY-021 | 数据集详情页面 | Urgent | 前端 |
| STORY-022 | 数据集数据预览 API | High | 后端 |
| STORY-023 | 基础数据清洗（去重检测 + 缺失值检测） | High | 后端 |
| STORY-024 | 数据同步日志记录 | Medium | 后端 |
| STORY-025 | 数据同步日志页面 | Medium | 前端 |

### 验收标准
- [ ] 支持 MySQL 数据源连接测试成功/失败的正确反馈
- [ ] CSV 文件上传后正确解析并在数据集中可预览
- [ ] 数据同步过程有完整的状态反馈（running → success/failed）
- [ ] 数据集字段映射正确，类型识别准确
- [ ] 数据清洗检测结果在数据质量页面正确展示
- [ ] 同步日志记录完整（时间、记录数、状态、错误信息）

---

## EPIC-003：数据分析

**描述**：
实现核心的数据分析引擎，支持灵活的多维度指标分析。包括指标分析工作台、数据聚合计算、分析结果可视化。

**优先级**：High  
**版本**：v1.0 MVP  
**负责人**：后端 + 前端 + 数据分析师

### 包含的 Story

| Story ID | 标题 | 优先级 | 负责人 |
|----------|------|--------|--------|
| STORY-026 | 指标计算引擎（聚合函数 + 时间粒度） | Urgent | 后端 |
| STORY-027 | 指标分析工作台页面（配置面板） | Urgent | 前端 |
| STORY-028 | 分析结果图表渲染（ECharts） | Urgent | 前端 |
| STORY-029 | 分析结果数据表格 | High | 前端 |
| STORY-030 | 多维度分组分析 API | High | 后端 |
| STORY-031 | 筛选条件构建器（Filter Builder） | High | 前端 |
| STORY-032 | 分析配置保存与加载 | Medium | 全栈 |
| STORY-033 | 数据导出（CSV） | Medium | 后端 |

### 验收标准
- [ ] 用户可选择数据集→指标→维度→时间范围→筛选条件→分析方式
- [ ] 聚合函数（SUM/AVG/COUNT/MAX/MIN）计算正确
- [ ] 多粒度（时/日/周/月/季/年）聚合结果正确
- [ ] 图表交互正常（hover 数据点、缩放、切换图表类型）
- [ ] 筛选条件支持多条件组合（AND/OR）
- [ ] 1000 条数据分析 < 5 秒

---

## EPIC-004：可视化看板

**描述**：
实现可视化看板系统，包括预置看板（企业总览）和基础的看板管理功能。

**优先级**：High  
**版本**：v1.0 MVP  
**负责人**：前端 Lead + UI 设计

### 包含的 Story

| Story ID | 标题 | 优先级 | 负责人 |
|----------|------|--------|--------|
| STORY-034 | 运营总览 Dashboard 页面 | Urgent | 前端 |
| STORY-035 | Dashboard KPI 卡片组件 | Urgent | 前端 |
| STORY-036 | Dashboard 趋势图组件 | Urgent | 前端 |
| STORY-037 | Dashboard 待办列表组件 | High | 前端 |
| STORY-038 | 看板列表页面 | High | 前端 |
| STORY-039 | 看板详情页面（组件网格渲染） | High | 前端 |
| STORY-040 | 看板 CRUD API | High | 后端 |
| STORY-041 | 看板组件 CRUD API | High | 后端 |
| STORY-042 | 看板数据聚合 API | Urgent | 后端 |
| STORY-043 | 看板自动刷新（WebSocket） | Medium | 后端 |

### 验收标准
- [ ] Dashboard KPI 之间存在业务逻辑关系，不是随机数
- [ ] Dashboard 首屏加载时间 < 2s
- [ ] 趋势图可切换时间范围（7天/30天/90天）
- [ ] 看板详情页组件按配置的网格布局正确渲染
- [ ] 点击 KPI 卡片可下钻到详情
- [ ] 待办数据与预警/巡检模块实时联动

---

## EPIC-005：预警中心

**描述**：
实现预警规则引擎、实时预警检测、预警处理闭环、多渠道通知。建立主动发现异常的完整预警体系。

**优先级**：High  
**版本**：v1.1 Analysis  
**负责人**：后端 Lead + 前端

### 包含的 Story

| Story ID | 标题 | 优先级 | 负责人 |
|----------|------|--------|--------|
| STORY-044 | 预警规则引擎（条件+阈值+持续时间评估） | Urgent | 后端 |
| STORY-045 | 预警规则 CRUD API | Urgent | 后端 |
| STORY-046 | 预警规则管理页面 | Urgent | 前端 |
| STORY-047 | 预警检测定时任务 | Urgent | 后端 |
| STORY-048 | 实时预警列表页面 | Urgent | 前端 |
| STORY-049 | 预警处理流程（确认→处理→关闭） | Urgent | 全栈 |
| STORY-050 | 系统内通知功能 | High | 全栈 |
| STORY-051 | 邮件通知服务 | High | 后端 |
| STORY-052 | WebSocket 实时预警推送 | High | 后端 |
| STORY-053 | 预警记录查询与归档 | Medium | 全栈 |
| STORY-054 | 预警统计 Dashboard | Medium | 全栈 |

### 验收标准
- [ ] 预警规则支持 >、<、>=、<=、=、!= 六种条件
- [ ] 支持持续时间设置（如"持续 5 分钟"才触发）
- [ ] 四级预警（低/中/高/严重）正确分类
- [ ] 系统内通知实时推送（WebSocket 延迟 < 3s）
- [ ] 预警处理流程完整：pending → processing → closed
- [ ] 预警触发到通知推送延迟 < 30s
- [ ] 支持冷却时间避免重复预警

---

## EPIC-006：智能巡检

**描述**：
实现巡检计划管理、巡检任务自动生成、巡检执行与记录、异常设备追踪。将设备巡检从线下纸质管理转为线上系统化管理。

**优先级**：Medium  
**版本**：v1.2 Alert & Inspection  
**负责人**：后端 + 前端 + 设备管理领域专家

### 包含的 Story

| Story ID | 标题 | 优先级 | 负责人 |
|----------|------|--------|--------|
| STORY-055 | 巡检计划 CRUD API + 定时调度 | High | 后端 |
| STORY-056 | 巡检任务自动生成（由计划创建） | High | 后端 |
| STORY-057 | 巡检计划管理页面 | High | 前端 |
| STORY-058 | 巡检任务列表与执行页面 | High | 前端 |
| STORY-059 | 巡检记录 CRUD | High | 全栈 |
| STORY-060 | 异常设备列表与追踪 | Medium | 全栈 |
| STORY-061 | 巡检记录查询与导出 | Medium | 全栈 |
| STORY-062 | 巡检统计 Dashboard | Low | 全栈 |

### 验收标准
- [ ] 巡检计划按 Cron 表达式定时生成任务
- [ ] 巡检任务支持批量执行（多设备同时巡检）
- [ ] 巡检结果（正常/异常/需关注）正确记录
- [ ] 异常设备自动关联最近的巡检记录
- [ ] 巡检完成率统计准确

---

## EPIC-007：数据报表

**描述**：
实现报表模板管理、报表即时生成、多格式导出、定时报表推送。满足企业正式汇报场景的数据报表需求。

**优先级**：Medium  
**版本**：v1.2 Alert & Inspection  
**负责人**：后端 + 前端

### 包含的 Story

| Story ID | 标题 | 优先级 | 负责人 |
|----------|------|--------|--------|
| STORY-063 | 报表模板管理（日报/周报/月报） | High | 全栈 |
| STORY-064 | 报表即时生成 API（PDF/Excel/CSV） | High | 后端 |
| STORY-065 | 报表中心页面 | High | 前端 |
| STORY-066 | 报表预览与下载 | High | 前端 |
| STORY-067 | 定时报表配置 | Medium | 全栈 |
| STORY-068 | 导出记录查询 | Medium | 全栈 |

### 验收标准
- [ ] 报表生成成功率 ≥ 99%
- [ ] PDF 报表内容与看板数据一致
- [ ] 报表包含图表 + 数据表
- [ ] 定时报表准时生成并推送通知
- [ ] Excel 导出包含正确的数据格式

---

## EPIC-008：权限管理

**描述**：
实现完整的 RBAC 权限管理体系，包括用户管理、角色管理、权限配置、数据级权限隔离、操作日志审计。

**优先级**：High  
**版本**：v1.2 Alert & Inspection  
**负责人**：后端 Lead + 前端

### 包含的 Story

| Story ID | 标题 | 优先级 | 负责人 |
|----------|------|--------|--------|
| STORY-069 | 用户管理 CRUD（完整版） | High | 全栈 |
| STORY-070 | 角色管理 + 权限树配置 | High | 全栈 |
| STORY-071 | 数据级权限隔离（按数据源/看板/报表） | High | 后端 |
| STORY-072 | 前端权限指令（按钮/菜单级） | High | 前端 |
| STORY-073 | 操作日志查询页面 | Medium | 全栈 |
| STORY-074 | 操作日志导出 | Medium | 后端 |
| STORY-075 | 密码复杂度策略 | Medium | 后端 |
| STORY-076 | 登录失败锁定策略 | Medium | 后端 |

### 验收标准
- [ ] 用户→角色→权限三级体系完整
- [ ] 权限粒度为 模块:页面:操作
- [ ] 前端按钮/菜单根据权限动态显示/隐藏
- [ ] 不同角色用户只能看到被授权的数据
- [ ] API 级别权限校验无遗漏
- [ ] 操作日志不可删除

---

## EPIC-009：测试与性能优化

**描述**：
建立测试体系（单元测试、集成测试、E2E 测试），进行性能优化和压测。确保产品质量和用户体验。

**优先级**：High  
**版本**：v1.0 ~ v1.2（持续）  
**负责人**：QA + 全栈开发

### 包含的 Story

| Story ID | 标题 | 优先级 | 负责人 |
|----------|------|--------|--------|
| STORY-077 | 后端单元测试（Jest + Supertest） | High | 后端 |
| STORY-078 | 前端组件测试（Vitest + Testing Library） | High | 前端 |
| STORY-079 | E2E 测试（Playwright/Cypress） | Medium | QA |
| STORY-080 | API 性能测试（k6/Artillery） | High | QA |
| STORY-081 | Dashboard 首屏加载优化（Lighthouse ≥ 90） | High | 前端 |
| STORY-082 | 数据库查询性能优化（索引 + 查询优化） | High | 后端 |
| STORY-083 | 大数据量分析性能优化（10万条 < 30s） | Medium | 后端 |
| STORY-084 | 前端打包优化（代码分割 + 懒加载） | Medium | 前端 |

### 验收标准
- [ ] 后端单元测试覆盖率 > 80%
- [ ] 核心业务流程 E2E 测试通过
- [ ] API P95 响应时间 < 500ms
- [ ] Dashboard Lighthouse Performance Score ≥ 90
- [ ] 500 并发用户下系统稳定
- [ ] 10 万条数据分析 < 30s

---

## EPIC-010：产品上线与版本迭代

**描述**：
管理产品发布流程、版本管理、部署文档、用户文档。确保产品从开发到上线的顺畅过渡。

**优先级**：Medium  
**版本**：v1.0 ~ v2.0（持续）  
**负责人**：产品经理 + 技术负责人

### 包含的 Story

| Story ID | 标题 | 优先级 | 负责人 |
|----------|------|--------|--------|
| STORY-085 | 产品部署文档编写 | High | 后端 |
| STORY-086 | 用户操作手册编写 | High | 产品经理 |
| STORY-087 | CI/CD 流水线搭建（GitHub Actions） | Medium | 后端 |
| STORY-088 | Demo 环境搭建与数据准备 | Medium | 后端 |
| STORY-089 | 版本管理页面开发 | Medium | 前端 |
| STORY-090 | UAT 用户验收测试 | High | 产品经理 + QA |

### 验收标准
- [ ] 部署文档新开发者可独立完成部署
- [ ] 用户手册覆盖所有核心流程
- [ ] CI/CD 自动运行测试 + 构建 + 部署
- [ ] Demo 环境可用且数据真实感强
- [ ] UAT 验收通过率 ≥ 95%

---

## 模块说明

| 模块 | 说明 |
|------|------|
| **Product** | 产品规划、需求分析、原型设计 |
| **Frontend** | 前端页面与组件开发 |
| **Backend** | 后端 API 与业务逻辑开发 |
| **Data** | 数据处理、ETL、数据分析 |
| **Testing** | 测试用例编写与执行 |
| **Release** | 发布管理、部署、文档 |

---

## 优先级定义

| 优先级 | 说明 |
|--------|------|
| **Urgent** | 阻塞性任务，必须最先完成 |
| **High** | 核心功能，版本内必须交付 |
| **Medium** | 重要但可适当延后 |
| **Low** | 锦上添花，资源允许时做 |

---

> **文档维护**：Epic 状态每周更新，由 PM 在 Redmine 中同步。
