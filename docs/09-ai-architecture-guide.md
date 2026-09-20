# AI 辅助开发下的高内聚低耦合架构设计指南

> **已沉淀为 skill**：本文内容已结构化沉淀为 `skills/dm-arch-design.md`（中文设计文档）+ `~/.codebuddy/skills/dm-arch-design/SKILL.md`（由中文源自动生成的部署版），创建/调整产品架构设计时优先调用该 skill。本文保留为方法论文档源。

> **唯一权威**：本文定义「人的架构设计规范」与「AI 的执行边界」两份约束，二者对同一套结构负责——人定边界、AI 填内部。
> 本文与 `docs/06`（契约只读）、`docs/07`（可观测性）、`docs/08`（小版本迭代）**互指不重定义**：06/07/08 是 AI 协作纪律，本文是把它们落到「架构形状」上的设计总纲。

---

## 1. 核心目标

- **控制复杂度**：防止 AI 在生成代码时盲目膨胀与跨层耦合（"泥潭代码"）。
- **上下文隔离**：确保每个模块的尺寸与边界符合 AI 上下文窗口的最佳处理范围（呼应 `docs/08` 单文件/单函数执行粒度）。
- **开发可控性**：通过契约与测试护栏，实现「AI 负责内部实现，人负责结构设计」。

---

## 2. 架构设计原则

| 原则 | 规范要求（人） | AI 协作执行标准（AI） |
| --- | --- | --- |
| **单向分层（Clean Architecture）** | 严格遵循 `Domain → Use Case → Adapter → Infrastructure` 依赖方向，禁止逆向或跨层调用。 | 拒绝编写跨层直接访问（如禁止 Controller 直连 DB）。 |
| **高内聚低耦合** | 按业务领域（限界上下文）划分子模块，而非仅按技术组件划分。 | 单模块代码量控制在 AI 上下文可高效理解的范围内（见 `docs/08`）。 |
| **极简暴露（Facade）** | 每个子模块仅通过统一的 `Facade` / API 接口对外暴露，内部实现全部私有化。 | 生成新功能时，优先查询已有暴露接口，禁止直接调用私有函数。 |
| **契约优先（Contract-First）** | 模块交互必须先定义 Interface、DTO 及事件结构，再写实现。 | 写实现前，必须先把 Interface 作为 Context 喂给 AI（见 `docs/06` §2.8 契约只读）。 |
| **数据驱动阈值（Data-Driven Thresholds）** | 性能 / 精度 / 误差类门禁必须由 Harness **实测数据**定案，留 1.5–2.5× 余量，**严禁凭空预设**。 | 不得在无实测依据时写入断言阈值；阈值须可执行、可回归。 |

---

## 3. 核心机制与模式设计

### 3.1 模块隐蔽性与接口收窄

- **单入口原则**：每个子模块在根目录提供唯一 `index` / `facade` 文件。
- **私有保护**：除 Facade 显式导出的类型与函数外，其余子文件夹（`internal/`、`services/`）不对外公开。
- 呼应 `docs/08` §2.2：仅核心算法层需测试，UI/视图不写 TDD——Facade 之内的私有实现由 AI 在小批内完成，人只 Review 边界。

### 3.2 专用通信模块（解耦跨模块交互）

- **同步通信**：统一使用中介者（Mediator）或轻量 RPC 代理，禁止模块间硬编码互相引用。
- **异步通信**：引入**事件总线（Event Bus）**。
  - 变更方仅发布领域事件（如 `OrderCreatedEvent`）。
  - 消费方通过订阅独立处理，实现零直接依赖。

### 3.3 可观测性内建（不另起炉灶）

- 模块内部的关键路径必须携带结构化日志/状态留痕，禁止静默吞错（见 `docs/07` §2.5）。
- 跨模块事件建议携带 `trace_id`，使事件总线上的链路可被 AI 在排查时还原（呼应 `docs/07` §3 黑匣子诊断）。

### 3.4 自底向上演进顺序（Step 内强制）

每个涉及代码改动的 Step 内部，必须按此顺序推进，**禁止逆向**（见 `docs/02-version-rules.md` §6.2）：

```
1. Pure Model / Domain      底层算法、纯数据结构，无 UI 依赖，可极速单测
2. Use Case / Application   用例门面，封装干净出口，隔离底层细节，防止 UI 越级调用
3. ViewModel / State        状态流水线（防抖、异步并发、状态机）
4. UI / Presentation        仅数据绑定与视图合成，不含任何计算逻辑
```

---

## 4. AI 协作标准 SOP（研发操作流程）

为避免 AI 污染架构，研发人员按以下四步开发：

1. **步骤 1：架构与接口设计（人工主导，AI 辅助）**
   明确模块边界，与 AI 共同产出 Interface 与 DTO（产出即落入 `docs/06` 契约 SSOT）。

2. **步骤 2：生成防腐测试（AI 生成，人工复核）**
   依据 Interface 生成单元/集成测试用例，锁定预期行为（见 `docs/08` §2.2 Agentic TDD：仅核心逻辑、独立进程跑、Assert 受 `docs/07` 约束）。

3. **步骤 3：模块内部实现（AI 主导，人做 Code Review）**
   仅把 Interface + 局部上下文喂给 AI，让其在模块内部完成实现，直至测试通过（执行粒度见 `docs/08` 三 Batch；陷入混乱时由人 `git reset --hard` 退回，见 `docs/08` §2.1）。

4. **步骤 4：全局集成（人主导）**
   通过事件总线或 API Gateway 连接各模块，做全链路校验（校验产物即 `docs/07` 观测数据）。

> SOP 与 `docs/01` §3.5 小版本执行步骤对齐：步骤 1–2 ≈ Batch 1（契约+数据模型），步骤 3 ≈ Batch 2（Core 单文件），步骤 4 ≈ Batch 3（接入 UI/调用点）。

---

## 5. 架构防腐规则（可直接配置给 AI）

以下内容可直接复制到项目的 `.cursorrules`、`CLAUDE.md` 或系统 Prompt 中，作为 AI 行为准则：

```text
[AI Coding Guardrails]
1. Do Not Cross Boundaries: Never import internal files from other modules. Only use the public exports defined in `index` or `facade`.
2. Contract First: Always request or check the Interface before implementing business logic (see docs/06 contract-read-only).
3. Layering Rule: Inner layers (Domain) must not depend on outer layers (Infrastructure/API).
4. Minimal Surface Area: Keep public methods to a minimum. Default to private or internal scope for all helper functions.
5. Event-Driven Coupling: For cross-domain communication, publish an Event to the EventBus instead of directly calling another domain's service.
6. Write Observability In: Every non-trivial branch logs a structured event and never swallows errors silently (see docs/07).
7. Stay In Scope: Implement only the single file / single function you were given; ask before expanding the blast radius (see docs/08).
```

---

## 6. 引用关系

| 文档 | 关系 |
| --- | --- |
| `docs/06-contract-based-dev.md` | 契约优先的 SSOT 纪律；本文 §2 契约优先、§4 步骤 1–2 落到其 §2.8 |
| `docs/07-observability-driven-dev.md` | 可观测性内建；本文 §3.3、§4 步骤 4、§5 规则 6 指向其 §2.5/§3 |
| `docs/08-small-batch-iteration.md` | AI 执行粒度与三 Batch；本文 §1/§2/§3.1/§4 步骤 3、§5 规则 7 指向其定义 |
| `docs/01-project-dev-flow.md` | 小版本执行步骤；本文 §4 SOP 与其 §3.5 对齐 |
