# 08 - 小版本迭代（Small-Batch Iterations / Micro-Batching）

## 概述

AI 在多个文件间来回拉扯、陷入「长尾混乱」的根因，是 Task Batch 对人类而言「小」，对 AI 而言「太大」。本规范把对 AI 的执行粒度从 Step（见 `docs/02-version-rules.md` §6.2）向下细分为**单文件重构 / 单函数修复**级，并规定 Commit 级 Micro-Batching 与 Context Flush 纪律。

本规范与 `docs/06-contract-based-dev.md` §8（契约只读）、`docs/07-observability-driven-dev.md`（可观测性）构成 **AI 协作三支柱**：契约只读让 AI 改前有界，可观测让 AI 改后可见，Micro-Batching 让 AI 改中可控。

> 以上「小版本迭代 / Micro-Batching」为**唯一权威**；模板与 skill 只引用本规范，不重定义。

## 1. 核心概念 — AI 小批定义

| 视角 | 「小版本」粒度 | 典型批次 |
|------|---------------|----------|
| 人类 / 产品 | 一个需求 Sprint | 5+ 文件的功能闭环 |
| **AI 执行** | **单文件重构 / 单函数修复** | 1 文件、1 函数、1 契约条目 |

**AI 最小批次（Micro-Batch）** = 一次单文件重构，或一次单点函数修复。一旦批次包含「跨 3+ 文件且彼此无直接调用关系」的改动，就超出了 AI 的安全执行粒度，必须拆分。

## 2. Commit 级 Micro-Batching（三 Batch）

一个 AI 可安全承接的 Step 内改动，按依赖顺序拆为三个 Batch，每完成一个**绿灯 Batch** 即提交（提交动作由用户触发，见 §2.1 护栏）：

| Batch | 内容 | 卡口校验 |
|-------|------|----------|
| **Batch 1** | 契约接口与数据模型（如 `DetectorContract.swift` 新增字段、`*.schema.json` 字段） | 编译检查 / Schema 校验通过，不破坏已有构建 |
| **Batch 2** | Core 逻辑实现（**单文件**） | 单元测试通过（Agentic TDD 轻量范式，见 §2.2） |
| **Batch 3** | 接入 UI / 调用点（多文件适配） | 集成校验通过 |

- 顺序不可逆：先契约、再 Core、后接入（与 `docs/02-version-rules.md` §6.2 的 `400-build.md` Step 0–7 施工清单一致）。
- 多个绿灯 Batch 的 commit 均 `Refs #同一 Issue`（见 `docs/03-git-flow-rules.md` §2.3）。

### 2.1 混乱回退纪律

若下一个 Batch 陷入「来回拉扯 / 越改越乱」，**由用户显式执行**退回上一个绿灯 Commit，并在新会话中继续：

```bash
git reset --hard <上一个绿灯 commit>
```

- 这是破坏性操作，**仅限用户显式请求**；AI 不自发执行 `reset --hard` / `push --force`（遵守 git 安全协议与「AI 不主动 commit」护栏）。
- 回退后走 §3 Context Flush，开 New Session 而非在同一长对话里硬救。

### 2.2 Batch 2 逻辑断言 = Agentic TDD 轻量范式

传统人类主导的 TDD（Red-Green-Refactor 全流程）在 AI 辅助下太重：写测试的 Prompt 成本常高于写逻辑、AI 写的测试也会假 Pass（无真实 Assert / 预期写错）、测试与业务双线拉扯使维护成本翻倍。故**不引入全量 TDD**，仅以「契约即测试（Contract-as-a-Test）」轻量补全 `dm-contract-gate` 未覆盖的**业务逻辑断言**缺口（门禁已覆盖接口/类型/指纹合法性，但无法断言「1080p 输入后 BBox ∈ [0,1]」这类算法正确性）。

Agentic TDD 的落地纪律（挂载进 Batch 2 卡口，非独立流程）：

1. **仅核心算法层强制**：纯算法 / 数据转换 / 坐标映射 / 状态机 / 加解密等核心逻辑须有测试；**UI / 视图 / 布局绝对不写 TDD**，靠静态检查与人工 Preview。
2. **测试归项目自身，门禁只读取**：单测（`swift test` / `pytest`）是项目代码的一部分；`dm-contract-gate` 的 Gate 2（改后校验）只调用并读取其全绿结果，不"拥有"单测。
3. **独立进程跑，AI 不自证 Green**：测试必须在独立进程（门禁脚本 / CI）执行，非 0 即失败；禁止 AI 在同一会话内"表演" Red→Green 后自报通过。
4. **AI 生成的测试 Assert 同样受 07 §2.5 约束**：必须断言具体边界值（空输入、极值、越界），禁止无断言的假 Green——否则只是把"假 Pass 业务代码"换成"假 Pass 测试代码"。

> Agentic TDD 与 07 可观测性、06 契约门禁同构：测试进程是「真相源」，AI 是「生成器」，门禁是「卡口」，三者分离。

## 3. Context Flush / 一文一议（New Session）

小 Task（如「修齐 `docs/` 与 `dist/` 一致性」）完成后，立即清空对话历史（New Session），斩断长对话导致的上下文污染。

新会话只携带：

1. **当前最新 Commit 的核心契约文件**（SSOT，呼应 `docs/06` §8 契约只读——新会话只带契约，不带历史噪音）；
2. **下一个小版本的 Single Task 说明**（单文件 / 单函数级）。

绝不把上一会话的完整聊天记录作为上下文延续。

## 4. 引用关系

| 文档 / Skill | 关系 |
|--------------|------|
| `docs/01-project-dev-flow.md` §3.5 | AI 执行粒度须缩到单文件/单函数，详见本规范 |
| `docs/02-version-rules.md` §2 / §6.2 | Step 为 dev 工作包原子；Batch 是 Step 内的更小执行纪律，不冲突 |
| `docs/03-git-flow-rules.md` §2.3 | Step 内 micro-batch 多 commit 均 `Refs` 同一版本 Issue；`reset --hard` 仅用户显式 |
| `docs/06-contract-based-dev.md` §8 | 契约只读：新会话只带契约 SSOT（呼应 §3 Context Flush） |
| `docs/07-observability-driven-dev.md` | 可观测性：日志是 AI 的眼睛，Batch 卡口校验产物即观测数据；§2.5 约束 AI 生成的测试 Assert（见 §2.2 Agentic TDD） |
| `skills/dm-dev-step.md` | 三 Batch 执行纪律入口 |
| `skills/dm-commit.md` | 每绿灯 Batch 即 commit（用户触发） |
| `skills/dm-plan-ver.md` | 版本计划须可拆成单文件批次 |
