# 08 - 小版本迭代（Small-Batch Iterations / Micro-Batching）

## 概述

AI 在多个文件间来回拉扯、陷入「长尾混乱」的根因，是 Task Batch 对人类而言「小」，对 AI 而言「太大」。本规范把对 AI 的执行粒度从 Transaction Flow（TF，见 `docs/02-version-rules.md` §2.2）向下细分为**单文件重构 / 单函数修复**级，并规定 Commit 级 Micro-Batching 与 Context Flush 纪律。

本规范与 `docs/06-contract-based-dev.md` §2.8（契约只读）、`docs/07-observability-driven-dev.md`（可观测性）构成 **AI 协作三支柱**：契约只读让 AI 改前有界，可观测让 AI 改后可见，Micro-Batching 让 AI 改中可控。

> 以上「小版本迭代 / Micro-Batching」为**唯一权威**；模板与 skill 只引用本规范，不重定义。

## 1. 核心概念 — AI 小批定义

| 视角 | 「小版本」粒度 | 典型批次 |
|------|---------------|----------|
| 人类 / 产品 | 一个需求 Sprint | 5+ 文件的功能闭环 |
| **AI 执行** | **单文件重构 / 单函数修复** | 1 文件、1 函数、1 契约条目 |

**AI 最小批次（Micro-Batch）** = 一次单文件重构，或一次单点函数修复。一旦批次包含「跨 3+ 文件且彼此无直接调用关系」的改动，就超出了 AI 的安全执行粒度，必须拆分。

## 2. Commit 级 Micro-Batching（三 Batch）

一个 AI 可安全承接的 TF 内改动，按依赖顺序拆为三个 Batch，每完成一个**绿灯 Batch** 即提交（提交动作由用户触发，见 §2.4 护栏）：

| Batch | 内容 | 卡口校验 |
|-------|------|----------|
| **Batch 1** | 契约接口与数据模型（如 `DetectorContract.swift` 新增字段、`*.schema.json` 字段） | 编译检查 / Schema 校验通过，不破坏已有构建 |
| **Batch 2** | Core 逻辑实现（**单文件**） | 单元测试通过 |
| **Batch 3** | 接入 UI / 调用点（多文件适配） | 集成校验通过 |

- 顺序不可逆：先契约、再 Core、后接入（与 `docs/02-version-rules.md` 的 `400-build.md` 执行顺序矩阵一致）。
- 多个绿灯 Batch 的 commit 均 `Refs #同一TF`（见 `docs/03-git-flow-rules.md` §2.3）。

### 2.1 混乱回退纪律

若下一个 Batch 陷入「来回拉扯 / 越改越乱」，**由用户显式执行**退回上一个绿灯 Commit，并在新会话中继续：

```bash
git reset --hard <上一个绿灯 commit>
```

- 这是破坏性操作，**仅限用户显式请求**；AI 不自发执行 `reset --hard` / `push --force`（遵守 git 安全协议与「AI 不主动 commit」护栏）。
- 回退后走 §3 Context Flush，开 New Session 而非在同一长对话里硬救。

## 3. Context Flush / 一文一议（New Session）

小 Task（如「修齐 `docs/` 与 `dist/` 一致性」）完成后，立即清空对话历史（New Session），斩断长对话导致的上下文污染。

新会话只携带：

1. **当前最新 Commit 的核心契约文件**（SSOT，呼应 `docs/06` §2.8 契约只读——新会话只带契约，不带历史噪音）；
2. **下一个小版本的 Single Task 说明**（单文件 / 单函数级）。

绝不把上一会话的完整聊天记录作为上下文延续。

## 4. 引用关系

| 文档 / Skill | 关系 |
|--------------|------|
| `docs/01-project-dev-flow.md` §3.5 | AI 执行粒度须缩到单文件/单函数，详见本规范 |
| `docs/02-version-rules.md` §2.2 | TF 为 dev 工作包原子；Batch 是 TF 内的更小执行纪律，不冲突 |
| `docs/03-git-flow-rules.md` §2.3 | TF 内 micro-batch 多 commit 均 `Refs` 同一 TF；`reset --hard` 仅用户显式 |
| `docs/06-contract-based-dev.md` §2.8 | 契约只读：新会话只带契约 SSOT（呼应 §3 Context Flush） |
| `docs/07-observability-driven-dev.md` | 可观测性：日志是 AI 的眼睛，Batch 卡口校验产物即观测数据 |
| `skills/dm-dev-tf.md` | 三 Batch 执行纪律入口 |
| `skills/dm-commit.md` | 每绿灯 Batch 即 commit（用户触发） |
| `skills/dm-plan-ver.md` | 版本计划须可拆成单文件批次 |
