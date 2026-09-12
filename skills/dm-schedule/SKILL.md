---
name: dm-schedule
description: This skill should be used when the user wants to create or update a version schedule. It builds a flat priority-ordered work package list for a Roadmap version, with work package IDs (dev/product/marketing/biz/qa/goal), effort estimates, acceptance criteria, and anti-procrastination guardrails. Target audience is the solo developer — it functions as a tactical backlog, not a Gantt chart.
---

# dm-schedule — Version Work Package Scheduler

Generate a flat, priority-ordered work package schedule for a Roadmap version, for scheduling and reconciliation. Target audience is the solo developer — a tactical backlog, not a Gantt chart.

## When to Use

- User says "schedule / 排程"
- User says "安排版本工作" / "generate work packages"
- User says "为 v1.0 做排程"
- User says "create/update a version schedule"

## Core Concepts

Work packages are built on two orthogonal dimensions: **category** (领域, who) and **stage** (环节, when).

### Category & Work Package ID

ID format: `v<X.Y>-<domain>-<NN>`

版本号作命名空间在前，域在后。ID 出现在 commit message、dm-log、TF issue 中时无需额外上下文即可知道所属版本；任何排序列表中同版本 WP 自然聚簇。

| Domain | Scope |
|--------|-------|
| `dev` | Development & architecture |
| `product` | Product & UI design |
| `marketing` | Marketing & outreach |
| `biz` | Business / monetization |
| `qa` | Testing & quality |
| `goal` | Version milestone targets |

Examples: `v1.0-dev-01`, `v1.0-marketing-02`, `v1.0-goal-01`

### Delivery Stage (验证环节)

Every work package also carries a **stage** — the phase of the delivery pipeline it belongs to:

```
调研 → 定位 → 设计 → 规格 → 开发 → 构建 → 部署 → 联调 → 测试 → 发布
```

> **This table is the single source of truth** for stage↔category mapping. `02-version-rules.md` §2.2, `400-build.md` execution order matrix, and `dm-plan-ver` all follow it. Each stage has one **primary category** (lead); a few stages have a secondary (helper) category. Update this table first when changing stages or categories.

| Stage | Primary category | Pipeline position | Helper category | Example |
|-------|------------------|-------------------|-----------------|---------|
| 调研 research | marketing | first | — | user interviews, pain-point validation, competitor analysis |
| 定位 positioning | marketing | early | — | target segment, value prop, market position |
| 设计 design | product | early | dev | UI design, wireframes, design tokens, architecture |
| 规格 spec | product | early | — | PRD, requirements, acceptance criteria |
| 开发 develop | dev | middle | — | implement TF (completion = code + deploy + integrate) |
| 构建 build | dev | middle | — | local build, packaging, compile |
| 部署 deploy | dev | middle | — | publish functions/services to target env |
| 联调 integrate | dev | middle | — | frontend ↔ deployed service, fix bugs |
| 测试 test | qa | late | dev | qa accepts deployed feature; dev backfills unit/regression |
| 发布 release | marketing | last | biz / dev | launch, store submission, promotion, monetization |

> Stage decides *when*; primary category decides *who*. Helper category is used only in collaboration (e.g. 设计 is product-led with dev helping on implementation; 测试 is qa-led with dev backfilling unit/regression).

### Dev Work Package Rules

#### Granularity: TF-Level Atomic Units

dev 工作包必须以 **Transaction Flow (TF)** 为单位组织，每个 TF 是不可分割的原子工作包：

| 粒度 | 例子 | 是否允许 |
|------|------|----------|
| TF 级 | `TF-1.1 — Monorepo 基础设施搭建（45m）` | ✅ 必须 |
| 步骤级 | `pnpm-workspace.yaml 创建（5m）` | ❌ 禁止 |

- 每个 dev 工作包 = 一个 TF，工作内容栏写 TF 名称 + 一行摘要 + `详见 400-build §N`
- TF 内部的具体步骤由 `400-build.md` 承载，不在 schedule 表格中展开
- 工时取 400-build 中该 TF 的总和
- 非 dev 工作包（product/marketing/biz/qa/goal）不受此限制

#### Completion: Code + Deploy + Integrate

dev 工作包**完成定义** = **代码 + 部署 + 联调** 三者缺一不可：

| 交付物 | 内容 | 验收信号 |
|--------|------|---------|
| 代码 | 按 400-build 实现 TF 逻辑 | 单测/回归通过 |
| 部署 | 函数/服务发布到目标环境 | 部署成功可访问 |
| 联调 | 前端 ↔ 已部署服务打通 | 端到端链路验证通过 |

- **部署与联调属于 dev，不属于 qa**。qa 只验收「已部署 + 已联调」的功能，不负责让它跑起来。
- schedule 中必须为需要部署的 dev 工作包显式安排「部署 + 联调」行，不得隐含在 qa 里。

## Scheduling Rules

Order by stage position + cross-domain dependency, not by intuition:

1. **Market-validation stage (marketing / research) goes first** — it defines what the version must prove.
2. **dev / qa work packages come after** the market-validation stage (hypothesis confirmed before building).
3. **qa work packages come after** the deploy + integrate stages of the dev work packages they verify.
4. Each version must cover multiple categories (dev + product + marketing + biz + qa).

## Workflow

### Step 1: Gather context

Ask the user:
- Which Roadmap version? (`vX.Y-<slug>`)
- Launch deadline? (YYYY-MM-DD)
- Quantifiable launch target? (e.g., "sell 5 licenses", "get 100 signups")
- Key deliverables already planned?

### Step 2: Generate work package list

Create `docs/versions/vX.Y-<slug>/500-schedule.md` using the template structure in `assets/500-schedule-template.md`. Fill work packages in execution-priority order; ensure cross-domain coverage:

1. **Groundwork** — repo scaffold, design tokens, brand assets (early, unblocks everything)
2. **Core UX** — main user-facing flows (the thing users actually see)
3. **Integration** — third-party services, payment, deployment
4. **QA** — cross-device testing, bug fixing
5. **Launch** — store submission, marketing push

Every work package row must carry its **stage (环节)**, with the market-validation stage first (see Scheduling Rules).

### Step 3: Define guardrails

The template includes four red-line rules. Keep them unless the user explicitly overrides:

1. **Market-first lock**: no new code starts until current marketing tasks are done
2. **2-hour stop-loss**: any non-core UI/animation refactor exceeding 2 hours → downgrade to basic
3. **Closure over perfection**: happy path first, edge cases deferred
4. **每周日强制对账**：对照本表打勾，超时 Task 通过砍掉后续非核心 `vX.X-dev-*` 工作包来补偿时间。TF 内部步骤可重排优先级，但 TF 本身不可分割。

### Step 4: Confirm and save

Display the schedule for review. On confirmation, save to `docs/versions/vX.Y-<slug>/500-schedule.md`.

## Template Structure

```markdown
# 📅 versions/vX.X/500-schedule.md
## 🚀 <project> v<X.Y> — 版本排程

> **关联 Roadmap 版本：** `vX.Y-<slug>`
> **上线卡点：** YYYY-MM-DD
> **首期目标：** <quantifiable metric>

### 🚨 防沉迷红线

1. 市场任务不完成，严禁写新代码
2. 2 小时停损原则
3. 闭环高于完美
4. 每周日强制对账

### 📋 工作包列表（按执行顺序）

| # | ID | 类别 | 环节 | 工作内容 | 难度 | 预估工时 | 验收标准 | 状态 |
|---|-----|------|------|---------|------|---------|---------|------|
| 1 | vX.X-dev-01 | dev | 开发 | **TF-X.X — 名称**：摘要。详见 400-build §N | ★★★☆☆ | Nh | 验收标准 | ⬜ |
```

> 环节取值参考：调研 / 定位 / 设计 / 规格 / 开发 / 构建 / 部署 / 联调 / 测试 / 发布。market-validation 环节（营销/调研）排最前。

All work packages are in a single flat table. `#` column = recommended execution order (not a hard dependency chain — cross-references handle that). Status legend: ⬜ 待开始 / 🔄 进行中 / ✅ 已完成 / ❌ 已取消.

## Key Rules

| Rule | Source |
|------|--------|
| Work packages strictly belong to one Roadmap version | — |
| Cross-domain mandatory: dev + product + marketing + biz + qa per version | — |
| Flat priority list, no weekly grouping | — |
| Scope slash over date slip on delays | — |
| Market-validation stage first; dev/qa after it | 02-version-rules.md |
| qa work packages follow deploy+integrate of the dev work packages they verify | 02-version-rules.md |
| dev work package granularity = TF atomic unit | 02-version-rules.md |
| dev work package completion = code + deploy + integrate; deploy/integrate belong to dev, not qa | 02-version-rules.md |
| Stage↔category mapping lives in the Core Concepts table (single source of truth) | — |
| File path: `docs/versions/vX.Y-<slug>/500-schedule.md` | 02-version-rules.md |
| Commit via dm-commit: `docs(schedule): <scope text>` | dm-commit |

## Assets

- `assets/500-schedule-template.md` — Schedule template with guardrails and empty table
