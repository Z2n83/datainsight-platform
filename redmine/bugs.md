# DataInsight — Bug 跟踪与预防规划

> **Project**：DataInsight | **Tracker**：Bug | **日期**：2026-08-06

---

## Bug 管理规范

### Bug 严重程度

| 等级 | 标签 | 说明 | 响应时间 | 解决时间 |
|------|------|------|---------|---------|
| **Blocker** | 阻塞 | 系统不可用，核心功能完全无法使用 | 1h | 4h |
| **Critical** | 严重 | 核心功能异常，影响主要业务流程 | 2h | 24h |
| **Major** | 重要 | 非核心功能异常，有 workaround | 1d | 3d |
| **Minor** | 轻微 | UI 问题、文案错误、边缘场景 | 3d | 7d |
| **Trivial** | 建议 | 体验优化建议 | 不紧急 | 下个版本 |

### Bug 状态流转

```
New → Confirmed → In Progress → Resolved → Verified → Closed
  │                    │              │
  └──→ Rejected        └──→ Feedback  └──→ Reopened
```

---

## v1.0 MVP 预计 Bug 类型与预防措施

### 1. 认证与权限类 Bug

| Bug ID | 预判场景 | 严重程度 | 预防措施 |
|--------|---------|---------|---------|
| BUG-AUTH-001 | Token 过期后前端未正确跳转登录页 | Major | AuthGuard 组件 + 拦截器双重校验 |
| BUG-AUTH-002 | 刷新 Token 时出现竞态条件导致多次刷新 | Major | Token 刷新加锁机制 |
| BUG-AUTH-003 | 密码未加密存储 | Blocker | 使用 bcrypt，代码审查必须检查 |
| BUG-AUTH-004 | 不同用户可看到对方数据 | Critical | API 级别用户数据隔离校验 |
| BUG-AUTH-005 | 登录失败错误信息过于详细（用户名存在/密码错误） | Minor | 统一返回"用户名或密码错误" |

### 2. 数据源与数据同步类 Bug

| Bug ID | 预判场景 | 严重程度 | 预防措施 |
|--------|---------|---------|---------|
| BUG-DS-001 | 数据库连接池耗尽导致新连接失败 | Critical | 连接池大小配置 + 超时回收机制 |
| BUG-DS-002 | 大数据量同步时内存溢出 (OOM) | Critical | 流式读取 + 分批处理 |
| BUG-DS-003 | 同步中断后数据不一致 | Major | 事务包装 + 断点续传 |
| BUG-DS-004 | 数据库密码在日志中明文输出 | Blocker | 日志脱敏中间件 |
| BUG-DS-005 | CSV 文件编码问题导致中文乱码 | Major | 自动检测编码 + UTF-8 转换 |
| BUG-DS-006 | SQL 注入风险 | Blocker | 参数化查询 100% 覆盖，代码审查必检项 |

### 3. 数据分析类 Bug

| Bug ID | 预判场景 | 严重程度 | 预防措施 |
|--------|---------|---------|---------|
| BUG-ANA-001 | 聚合计算结果不准确（浮点数精度） | Critical | 使用 DECIMAL 类型 + 精度验证测试 |
| BUG-ANA-002 | 时间粒度聚合边界错误（周/月边界） | Major | 单元测试覆盖所有粒度边界 |
| BUG-ANA-003 | 空数据集分析时接口 500 错误 | Major | 空值保护，返回空结果而非报错 |
| BUG-ANA-004 | 大数据量分析超时 | Major | 查询超时设置 + 数据量限制提示 |
| BUG-ANA-005 | 筛选条件组合导致 SQL 语法错误 | Major | 查询构建器单元测试全覆盖 |

### 4. 可视化与 Dashboard 类 Bug

| Bug ID | 预判场景 | 严重程度 | 预防措施 |
|--------|---------|---------|---------|
| BUG-DASH-001 | Dashboard KPI 数据不一致（缓存不同步） | Critical | 缓存失效策略 + 数据版本号 |
| BUG-DASH-002 | ECharts 图表在数据为空时显示异常 | Minor | 空数据占位图 |
| BUG-DASH-003 | 图表 resize 时出现重叠或错位 | Minor | debounce resize 处理 |
| BUG-DASH-004 | 看板组件拖拽后布局错乱 | Major | 布局序列化/反序列化校验 |

### 5. 前端通用 Bug

| Bug ID | 预判场景 | 严重程度 | 预防措施 |
|--------|---------|---------|---------|
| BUG-FE-001 | 页面切换后内存泄漏（未清理定时器/监听器） | Major | useEffect cleanup + ESLint 规则 |
| BUG-FE-002 | Ant Design 表单校验不生效 | Minor | 表单组件单元测试 |
| BUG-FE-003 | 日期选择器时区问题 | Major | 统一使用 ISO 8601 + 服务端时区 |
| BUG-FE-004 | 表格大数据量渲染卡顿 | Major | 虚拟滚动 + 分页 |

### 6. 性能类 Bug

| Bug ID | 预判场景 | 严重程度 | 预防措施 |
|--------|---------|---------|---------|
| BUG-PERF-001 | N+1 查询问题 | Critical | Prisma 查询 include/eager loading + 监控 |
| BUG-PERF-002 | 缺少索引导致全表扫描 | Critical | 所有外键 + 高频查询字段建索引 |
| BUG-PERF-003 | API 未设置 Rate Limit 导致被刷爆 | Critical | Rate Limit 中间件全局启用 |
| BUG-PERF-004 | React 组件不必要的重渲染 | Minor | React.memo + useMemo + Profiler |

---

## Bug 修复流程

```
1. 发现 Bug → 在 Redmine 创建 Issue（Tracker: Bug）
2. 填写：
   - 标题：[模块] 简短描述
   - 严重程度：Blocker/Critical/Major/Minor/Trivial
   - 复现步骤
   - 期望结果 vs 实际结果
   - 环境信息（浏览器、OS、版本）
   - 截图/日志
3. 开发确认 → 修复 → 提交代码（Commit 关联 Bug ID）
4. QA 验证 → 关闭或 Reopen
```

---

## 代码审查 Bug 检查清单

### 后端代码审查
- [ ] SQL 查询是否使用参数化（防注入）
- [ ] 敏感信息（密码、Token）是否在日志中脱敏
- [ ] API 是否有权限校验
- [ ] 是否有 N+1 查询
- [ ] 事务边界是否正确
- [ ] 错误处理是否完善（不暴露内部信息）
- [ ] 大数据量操作是否有分页/流式处理

### 前端代码审查
- [ ] useEffect 是否有 cleanup
- [ ] 表单校验是否完整
- [ ] 空数据/加载中/错误状态是否都处理
- [ ] Token 过期处理是否正确
- [ ] XSS 防护（dangerouslySetInnerHTML 使用是否安全）
- [ ] 大列表是否有性能优化

---

## 测试用例优先级

| 优先级 | 测试范围 | 示例 |
|--------|---------|------|
| P0 | 登录/认证流程 | 正确账号登录成功、错误密码登录失败、Token 过期跳转 |
| P0 | 核心数据链路 | 数据源→数据集→分析→看板 |
| P0 | 数据安全 | 密码加密、SQL 注入防护、跨用户数据隔离 |
| P1 | CRUD 操作 | 各模块的增删改查 |
| P1 | 数据同步 | 全量同步、失败重试 |
| P1 | 预警流程 | 规则触发→通知→处理→关闭 |
| P2 | UI 交互 | 响应式、空状态、错误状态 |
| P2 | 权限控制 | 不同角色看到不同菜单和数据 |
| P3 | 边缘场景 | 超大数据量、并发操作、网络异常 |

---

> **文档维护**：Bug 统计和修复进度在 Redmine 中实时更新。
