# {{PROJECT_NAME}} - 路线图与合规

> **文档流向纪律**：本文档**汇总引用** upstream `00`~`04`（及 `06`），是规划层文档；**不反向引用任何版本文档**（版本文档引用本文）。
> **占位符约定**：`{{FIELD}}` = 结构化命名字段；`<!-- TODO: [dm-init-docs] <说明> -->` = 待补充内容。
> **权威引用**：版本四件套结构与 TF 规则见 `dev-meta/docs/02-version-rules.md`；分支 / commit / PR 规则见 `dev-meta/docs/03-git-flow-rules.md`。本文只做项目级规划，不重定义。

---

## 1. Milestone 阶段规划

| 阶段 | 目标 | 范围 | 完成判据 | 状态 |
|------|------|------|----------|------|
| M1 | <!-- TODO: [dm-init-docs] 第一阶段目标 --> | <!-- TODO --> | <!-- TODO --> | ⬜ |
| M2 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | ⬜ |

---

## 2. 版本切分 (Epoch Plan)

> 版本群（Epoch）划分与编号规则；每个版本启动走 `dm-plan-ver` 生成四件套（`200-spec` / `300-design` / `400-build` / `500-schedule`）。
> 规划动作由 `dm-plan-roadmap` 执行。

| Epoch | 版本 | 目标 | 依赖 | 粒度校验 | 状态 |
|-------|------|------|------|----------|------|
| <!-- TODO --> | `v<!-- TODO -->` | <!-- TODO --> | <!-- TODO --> | <!-- TODO: 预估 S4/S5 各一次？场景可一句话？ --> | ⬜ |

- **版本编号规则**（唯一权威）：`dev-meta/docs/02-version-rules.md` §3.3 —— `v` 轴（feature）/ `r` 轴（refactor）双轨；Epoch 分配号段、群内连续、**群间留白 10 号**。
- **版本粒度红线**（唯一权威）：同上 §3.2 —— 一个版本只承载**单一核心业务场景**；判据与「实证失败须退回重切」见该节。
- **粒度校验分两次**：切版本时为**预估**（人工确认，填入上表「粒度校验」列）；`400-build` 完成后由 `dm-plan-ver` **实证**（S4 / S5 计数），失败须退回本文重切。
- **与 dm-plan-ver 的衔接**：本文定义「有哪些版本、先后顺序」；**每个版本的具体范围、验收、执行步骤由 `dm-plan-ver` 生成的四件套承载**，不在本文重复。

---

## 3. 合规与安全

| 项 | 要求 | 落点 | 状态 |
|----|------|------|------|
| 数据隐私 | <!-- TODO: [dm-init-docs] 收集的个人信息、处理方式 --> | <!-- TODO --> | ⬜ |
| 数据存储与传输 | <!-- TODO: [dm-init-docs] 加密、留存期限 --> | <!-- TODO --> | ⬜ |
| 第三方 SDK / 服务 | <!-- TODO: [dm-init-docs] 清单与合规声明 --> | <!-- TODO --> | ⬜ |
| 审计与日志 | <!-- TODO: [dm-init-docs] 哪些操作需留痕 --> | `06_OBSERVABILITY.md` | ⬜ |

---

## 4. 风险与依赖

| 风险 / 依赖 | 影响 | 应对 | 责任方 |
|-------------|------|------|--------|
| <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |

---

## 5. 引用声明

| 引用对象 | 方向 | 用途 |
|----------|------|------|
| `00_PRODUCT_REQUIREMENTS.md` | upstream | 用户故事与验收 |
| `01_TECHNICAL_SPEC.md` | upstream | 部署与测试约束 |
| `02_SYSTEM_DESIGN.md` | upstream | 架构边界 |
| `03_CONTRACTS_AND_API.md` | upstream | 契约范围 |
| `04_UI_UX_DESIGN.md`（如有） | upstream | 界面范围 |
| `06_OBSERVABILITY.md` | upstream | 审计留痕要求 |
| `dev-meta/docs/02-version-rules.md` | 外部权威 | 版本规则（只引用） |
| `dev-meta/docs/03-git-flow-rules.md` | 外部权威 | Git 流程（只引用） |
