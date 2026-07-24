# dm-commit

## 概述

Commit 规范 skill，确保每次提交遵循 dev-meta commit 约定。是 commit 格式的单一事实来源 — dm-plan-ver、dm-log、dm-init 的 commit 步骤均委托至此。

## 触发

- "commit"
- "提交代码"
- "帮我 commit"
- dm-plan-ver 阶段 2 步骤 3（TF 交付提交）
- dm-log 步骤 6（worklog 提交）
- dm-init 步骤 5（初始化提交）

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

- 使用**祈使语气**（"add" 而非 "added"）
- ≤ 50 字符
- 简洁描述做了什么
- docs/worklog 可用中文，代码建议用英文

### 4. 编写 body（按需）

说明为什么改、影响与迁移信息。细小变更可省略。

### 5. 编写 footer（按需）

TF 相关提交：

| Footer | 含义 |
|--------|------|
| `Closes #N` | 本次提交**完成**该 TF |
| `Refs #N` | 本次提交是 TF 的一部分，但未完成 |

非 TF 提交（worklog、项目初始化、独立修复）可省略 footer。

### 6. 构建并执行

构建完整的 commit message，执行 `git commit`。**除非用户明确要求，否则不主动 commit。**

### 7. 校验

提交后验证：

- `type` 在允许集合中
- `scope` 存在且非空
- `subject` ≤ 50 字符
- 如有 `Closes`/`Refs`，格式正确

## 关键规则速查

| 规则 | 来源 |
|------|------|
| 强制格式 `type(scope): subject` | git-flow-rules.md §3.1 |
| type 集合（8 种） | git-flow-rules.md §3.3 |
| subject ≤ 50 字符 | git-flow-rules.md §3.4 |
| TF 提交须关联 Issue | git-flow-rules.md §2.3 |
| 细小变更可省略 body/footer | git-flow-rules.md §8 |

## 常见模式

```text
# TF 完成
feat(auth): implement credential validation

Closes #42
```

```text
# Worklog 更新
chore: update worklog — version-rules 交叉 TF 状态机规范
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

## Skill 资源映射

| 资源 | 来源 | 用途 |
|------|------|------|
| SKILL.md | — | 上述流程指令 + 规则速查 |
| references/git-flow-rules.md | `docs/git-flow-rules.md` | commit 规范详情 |

## 使用示例

```
用户: "commit"

AI:  1. 检查暂存区 (git diff --staged)
     2. 分析变更类型 → 推荐 type: feat
     3. 推荐 scope: auth
     4. 建议 subject: implement credential validation
     5. TF 相关 → 建议 footer: Closes #42
     6. 构建: feat(auth): implement credential validation\n\nCloses #42
     7. 确认后执行 commit
```

```
用户: "TF2 完成了，帮我 commit"

AI:  1. 读取 spec.md 确认 TF2 验收标准
     2. 按 dm-commit 规范构建 commit message
     3. type: feat, scope: <TF 相关模块>
     4. footer: Closes #<TF2 issue>
     5. 执行 commit
```
