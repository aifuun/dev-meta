---
name: dm-commit
description: 提交变更时使用：type(scope): subject 格式向导、格式校验、footer 关联 Issue（Closes/Refs）。触发于「commit」「帮我 commit」或询问 commit 格式。
---

# dm-commit

## 概述

Commit 规范 skill，确保每次提交遵循 dev-meta commit 约定。是 commit 格式的单一事实来源 — dm-plan-ver、dm-log、dm-init-docs、dm-report、dm-adr 的 commit 步骤均委托至此。

## 职责边界

| 职责 | 归属 |
|------|------|
| 确定 `type(scope): subject` 格式 | ✅ 本 skill |
| 格式校验（type 集合 / scope / subject 长度 / footer） | ✅ 本 skill |
| 执行 `git commit`（用户确认后） | ✅ 本 skill |
| commit 内容的组织与分批（三 Batch） | ❌ `dm-dev-step`，见 `docs/08-small-batch-iteration.md` |
| 契约门禁（改前 diff / 改后校验） | ❌ `dm-contract-gate`（本 skill 的前序卡口） |
| 版本收尾、分支清理、打 tag | ❌ `dm-close-ver` |
| 未获用户明确要求时**不主动** commit | 硬约束（见「关键规则速查」） |

## 触发

- "commit"
- "提交代码"
- "帮我 commit"
- 询问 commit message 格式
- dm-dev-step 步骤 5（Step 收尾提交）
- dm-log 步骤 6（worklog 提交）
- dm-init-docs 步骤 7（初始化提交）
- dm-report 步骤 6（报告提交）
- dm-adr 步骤 7（ADR 提交）

## 核心概念

### commit 结构

```
type(scope): subject

body（可选）

Closes #42
```

| 部分 | 要求 |
|------|------|
| `type` | 来自允许集合（8 种） |
| `scope` | 必填，简短小写标识符（如 `auth`、`storage`） |
| `subject` | 祈使语气（"add" 而非 "added"，"fix" 而非 "fixed"），≤ 50 字符 |
| `body` | 说明为什么改、影响与迁移信息；细小变更可省略 |
| `footer` | Step 相关用 `Closes #id`（完成）或 `Refs #id`（部分） |

### Closes 与 Refs

- `Closes #N`：本次提交**完成**该 Step，合并时由托管平台自动关闭 Issue。
- `Refs #N`：本次提交是该 Step 的一部分但未完成（Micro-Batching 中间批次用 `Refs` 同一 Issue）。

### Micro-Batching 节奏

一个 Step 拆为三 Batch，每完成一个**绿灯 Batch** 即生成一个 commit（均 `Refs #同一 Issue`），最后一个绿灯 Batch 用 `Closes`。详见 `docs/08-small-batch-iteration.md`。

### AI 不主动提交

本 skill 仅在用户显式说 commit / 调用 `dm-commit` 时触发。下个 Batch 陷入混乱时由**用户**执行 `git reset --hard` 退回上一个绿灯 commit（AI 不自发，遵守 git 安全协议）。

## 执行流程

### 1. 确定 type

分析暂存区变更，推荐 type：

| Type | 使用场景 |
|------|----------|
| `feat` | 新功能、新特性 |
| `fix` | 缺陷修复 |
| `docs` | 仅文档变更 |
| `refactor` | 代码重构，不改变外部行为 |
| `test` | 新增或修改测试 |
| `chore` | 构建、依赖、工具、worklog、项目初始化 |
| `perf` | 性能优化 |
| `ci` | CI/CD 变更 |

### 2. 确定 scope

选取一个简短的小写标识符描述影响的模块或区域。

示例：`auth`、`storage`、`ui`、`api`、`worklog`、`git-flow`、`version-rules`

不可省略，必须明确。

### 3. 编写 subject

- 使用**祈使语气**（"add" 而非 "added"，"fix" 而非 "fixed"）
- ≤ 50 字符
- 简洁描述做了什么
- docs/worklog 可用中文，代码建议用英文

### 4. 编写 body（按需）

说明为什么改、影响与迁移信息。细小变更可省略。

### 5. 编写 footer（按需）

Step 相关提交：

| Footer | 含义 |
|--------|------|
| `Closes #N` | 本次提交**完成**该 Step |
| `Refs #N` | 本次提交是 Step 的一部分，但未完成 |

非 Step 提交（worklog、项目初始化、独立修复）可省略 footer。

### 6. 构建并执行

构建完整的 commit message，执行 `git commit`。**除非用户明确要求，否则不主动 commit。**

> 在 `docs/08-small-batch-iteration.md` 的 Micro-Batching 节奏下，一个 Step 拆为三 Batch，每完成一个**绿灯 Batch** 即生成一个 commit（均 `Refs #同一 Issue`）。本步骤仍在用户显式说 commit / 调 dm-commit 时触发，AI 不自发提交；下个 Batch 混乱时由**用户** `git reset --hard` 退回上一个绿灯 commit（AI 不自发，遵守 git 安全协议）。

### 7. 校验

提交后验证：

- `type` 在允许集合中
- `scope` 存在且非空
- `subject` ≤ 50 字符
- 如有 `Closes`/`Refs`，格式正确

## 关键规则速查

| 规则 | 来源 |
|------|------|
| 强制格式 `type(scope): subject` | 03-git-flow-rules.md §3.1 |
| type 集合（8 种） | 03-git-flow-rules.md §3.3 |
| subject ≤ 50 字符 | 03-git-flow-rules.md §3.4 |
| Step 提交须关联 Issue | 03-git-flow-rules.md §2.3 |
| 细小变更可省略 body/footer | 03-git-flow-rules.md §8 |
| docs / worklog 可用中文 subject，代码建议英文 | 03-git-flow-rules.md §3.4 |
| 除非用户明确要求，否则不主动 commit | 03-git-flow-rules.md §3（本 skill §6） |

## 常见模式

```text
# Step 完成
feat(auth): implement credential validation

Closes #42
```

```text
# Worklog 更新
chore: update worklog — version-rules 交叉 Step 状态机规范
```

```text
# 项目初始化
chore: initialize project docs following dev-meta
```

```text
# Bug 修复
fix(storage): fallback to memory when indexeddb is unavailable

Keep playback flow non-blocking when openDB fails.

Closes #42
```

## 产出与完成判据

**产出**：

- 一条符合规范的 commit：`type(scope): subject` + 可选 body / footer

**完成判据**：

- [ ] `type` 在允许集合内，`scope` 存在且非空
- [ ] `subject` ≤ 50 字符且为祈使语气
- [ ] Step 相关含 `Closes #id` 或 `Refs #id` footer
- [ ] 变更内容与本次 commit 范围一致，未夹带无关文件
- [ ] **已获用户确认**后执行（AI 不主动提交）

## 资源映射

| 资源 | 来源 | 用途 |
|------|------|------|
| `~/.codebuddy/skills/dm-commit/SKILL.md` | — | 部署版（由中文源自动生成，勿手改） |
| references/git-flow-rules.md | `docs/03-git-flow-rules.md` | commit 规范详情 |

## 使用示例

```
用户: "commit"

AI:  1. 检查暂存区 (git diff --staged)
     2. 分析变更类型 → 推荐 type: feat
     3. 推荐 scope: auth
     4. 建议 subject: implement credential validation
     5. Step 相关 → 建议 footer: Closes #42
     6. 构建: feat(auth): implement credential validation\n\nCloses #42
     7. 确认后执行 commit
```

```
用户: "S2 完成了，帮我 commit"

AI:  1. 读取 200-spec.md 确认 S2 验收标准
     2. 按 dm-commit 规范构建 commit message
     3. type: feat, scope: <Step 相关模块>
     4. footer: Closes #<版本 Issue>
     5. 执行 commit
```
