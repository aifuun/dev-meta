---
name: dm-arch-design
description: 创建或调整产品架构时使用，定义人的架构设计规范与 AI 执行边界（单向分层、Facade 极简暴露、事件总线）。触发于「设计架构」「规划模块边界」「生成 AI 防腐规则」。
---

# dm-arch-design

## 概述

架构设计 skill，定义「人的架构设计规范」与「AI 的执行边界」两份约束，二者对同一套结构负责——人定边界、AI 填内部。供人与 AI 在创建或调整产品架构设计时参考，把 06（契约只读）、07（可观测性）、08（小版本迭代）三套 AI 协作纪律落到「架构形状」上。

## 职责边界

| 职责 | 归属 |
|------|------|
| 定义架构设计原则与 AI 防腐规则 | ✅ 本 skill |
| 模块边界 / Interface / DTO 设计 | ✅ 本 skill（产出落入 06 契约 SSOT） |
| 防腐测试生成 | 委托 dm-dev-tf（依据 06/08 落地） |
| 模块内部实现 | 委托 dm-dev-tf（按 08 三 Batch 推进） |
| 版本计划拆分 | 委托 dm-plan-ver（计划须可拆成单文件批次） |

## 触发

- "设计架构"
- "规划模块边界"
- "调整代码结构"
- "做高内聚低耦合拆分"
- "生成 AI 防腐规则 / .cursorrules / CLAUDE.md"

## 核心概念

### AI 协作双约束

本文定义两份正交约束，二者对同一套结构负责：

- **人的架构设计规范**：单向分层、高内聚低耦合、Facade 极简暴露、契约优先——人定边界与交互契约。
- **AI 的执行边界**：在边界内填实现，拒绝跨层/跨模块越界，单文件/单函数粒度推进（见 08）。

### 架构设计四原则

| 原则 | 规范要求（人） | AI 协作执行标准（AI） |
|------|--------------|---------------------|
| **单向分层（Clean Architecture）** | 严格遵循 `Domain → Use Case → Adapter → Infrastructure` 依赖方向，禁止逆向或跨层调用 | 拒绝编写跨层直接访问（如禁止 Controller 直连 DB） |
| **高内聚低耦合** | 按业务领域（限界上下文）划分子模块，而非仅按技术组件划分 | 单模块代码量控制在 AI 上下文可高效理解的范围内（见 08） |
| **极简暴露（Facade）** | 每个子模块仅通过统一 `Facade` / API 接口对外暴露，内部实现全部私有化 | 生成新功能时，优先查询已有暴露接口，禁止直接调用私有函数 |
| **契约优先（Contract-First）** | 模块交互必须先定义 Interface、DTO 及事件结构，再写实现 | 写实现前，必须先把 Interface 作为 Context 喂给 AI（见 06 §2.8 契约只读） |

### 核心机制

- **模块隐蔽性与接口收窄**：每个子模块根目录提供唯一 `index` / `facade` 文件；除 Facade 显式导出的类型与函数外，其余子文件夹（`internal/`、`services/`）不对外公开。呼应 08 §2.2：仅核心算法层需测试，UI/视图不写 TDD——Facade 之内的私有实现由 AI 在小批内完成，人只 Review 边界。
- **专用通信模块（解耦跨模块交互）**：同步通信用中介者（Mediator）或轻量 RPC 代理，禁止模块间硬编码互相引用；异步通信用**事件总线（Event Bus）**——变更方仅发布领域事件（如 `OrderCreatedEvent`），消费方订阅独立处理，实现零直接依赖。
- **可观测性内建（不另起炉灶）**：模块内部关键路径必须携带结构化日志/状态留痕，禁止静默吞错（见 07 §2.5）；跨模块事件建议携带 `trace_id`，使事件总线上的链路可被 AI 还原（呼应 07 §3 黑匣子诊断）。

### 决策点收敛

在产出架构契约（Interface / DTO / 事件结构）前，对影响 AI 执行边界的决策点做显式「提问 → 回答 → 沉淀」三步，**不依赖 AI 自问自答**（原则见 skill-doc-principles §7）：

- 提问范围：模块边界、跨模块通信方式（同步/异步）、Facade 暴露面、事件结构设计、技术选型。
- 技术选型类回答触发 `dm-adr` 记录；问答不得留在对话流中丢失。

## 执行流程

### 步骤 1：架构与接口设计（人工主导，AI 辅助）

明确模块边界，与 AI 共同产出 Interface 与 DTO——产出即落入 `docs/06` 契约 SSOT。此处执行「决策点收敛」。

### 步骤 2：生成防腐测试（AI 生成，人工复核）

依据 Interface 生成单元/集成测试用例，锁定预期行为（见 08 §2.2 Agentic TDD：仅核心逻辑、独立进程跑、Assert 受 07 约束）。委托 dm-dev-tf 落地。

### 步骤 3：模块内部实现（AI 主导，人做 Code Review）

仅把 Interface + 局部上下文喂给 AI，让其在模块内部完成实现，直至测试通过（执行粒度见 08 三 Batch；陷入混乱时由人 `git reset --hard` 退回，见 08 §2.1）。委托 dm-dev-tf 推进。

### 步骤 4：全局集成（人主导）

通过事件总线或 API Gateway 连接各模块，做全链路校验（校验产物即 07 观测数据）。

> SOP 与 `docs/01` §3.5 小版本执行步骤对齐：步骤 1–2 ≈ Batch 1（契约+数据模型），步骤 3 ≈ Batch 2（Core 单文件），步骤 4 ≈ Batch 3（接入 UI/调用点）。

## 关键规则速查（单一权威）

| 规则 | 来源 |
|------|------|
| 单向分层：Domain→Use Case→Adapter→Infrastructure，禁止逆向/跨层 | 本文 §核心概念 |
| 高内聚低耦合：按限界上下文划分子模块，非仅按技术组件 | 本文 §核心概念 |
| 极简暴露：每模块仅经 Facade/API 暴露，内部全部私有 | 本文 §核心概念 |
| 契约优先：先 Interface/DTO/事件，再实现；实现前把 Interface 喂给 AI | docs/06 §2.8 |
| 模块隐蔽：唯一 index/facade 入口，internal/services 不公开 | 本文 §核心概念 |
| 跨模块解耦：同步用 Mediator/RPC，异步用 Event Bus，禁止硬编码互引 | 本文 §核心概念 |
| 可观测性内建：关键路径结构化日志 + 不静默吞错 + 跨模块事件带 trace_id | docs/07 §2.5/§3 |
| 决策点显式「提问→回答→沉淀」，技术选型触发 dm-adr | skill-doc-principles §7 |
| 防腐测试仅核心逻辑；UI/视图不写 TDD | docs/08 §2.2 |
| 模块实现单文件/单函数粒度，混乱由人 reset --hard | docs/08 §2.1 |

## 产出与完成判据

**产出**：

- 架构设计结论：模块边界、分层、Facade 暴露面、跨模块通信方式
- 可选：AI 防腐规则（可写入 `.cursorrules` / `CLAUDE.md`）

**完成判据**：

- [ ] 单向分层成立，无逆向或跨层依赖
- [ ] 每个子模块只有**唯一** Facade / 入口文件，内部实现私有
- [ ] 跨模块通信走 Mediator / RPC 或事件总线，无硬编码互相引用
- [ ] 关键路径已登记「须被观测」项，并指向 `06_OBSERVABILITY.md`
- [ ] 决策点已通过「提问 → 回答 → 沉淀」收敛（不依赖 AI 自问自答），技术选型类已触发 `dm-adr`

## 资源映射

| 资源 | 来源 | 用途 |
|------|------|------|
| SKILL.md | — | 流程指令 + 规则速查 |
| `docs/06-contract-based-dev.md` |  docs/ | 契约只读 SSOT |
| `docs/07-observability-driven-dev.md` | docs/ | 可观测性内建 |
| `docs/08-small-batch-iteration.md` | docs/ | AI 执行粒度与三 Batch |
| `docs/01-project-dev-flow.md` §3.5 | docs/ | 小版本执行步骤对齐 |
| dm-adr | skills/ | 技术选型决策记录 |
| `references/ai-collab-pillars.md` | ~/.codebuddy/skills/dm-arch-design/references/ | 06/07/08/09 索引卡（纯指针+关键条款，应用即对齐，按需加载） |

## 使用示例

### 示例 1：新建模块架构

```
用户: "给订单域设计模块边界与接口"

AI:  1. 决策点收敛（提问）：模块边界？同步/异步通信？Facade 暴露面？
     2. 产出 Interface + DTO（落入 06 契约 SSOT）
     3. 给出架构防腐规则（可写入 .cursorrules）
     4. 委托 dm-dev-tf 生成防腐测试 + 模块实现（按 08 三 Batch）
```

### 示例 2：生成 AI 防腐规则

```
用户: "生成 AI 防腐规则给项目用"

AI:  输出可直接复制到 .cursorrules / CLAUDE.md 的护栏：
     [AI Coding Guardrails]
     1. Do Not Cross Boundaries: 只通过 index/facade 的公共导出访问模块
     2. Contract First: 实现前先查 Interface（见 docs/06）
     3. Layering Rule: 内层(Domain)不依赖外层(Infrastructure/API)
     4. Minimal Surface Area: 公共方法最小化，默认 private/internal
     5. Event-Driven Coupling: 跨域通信用 Event Bus，不直接调用别域 service
     6. Write Observability In: 每个非平凡分支结构化日志，不静默吞错（见 docs/07）
     7. Stay In Scope: 只实现给定的单文件/单函数，扩大影响面先问（见 docs/08）
```
