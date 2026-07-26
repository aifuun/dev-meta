# dm-dev-tf

## 概述

TF 开发引导 skill，负责读取版本文档上下文、确认/创建 TF Issue、创建 TF 分支、输出开发概要。是 dm-plan-ver Phase 2 中 TF 开发的"启动端"。

## 关系

dm-dev-tf 嵌入 dm-plan-ver 的 Phase 2（TF 开发）。dm-plan-ver 负责版本级规划（文档、分支、Issue、PR）；dm-dev-tf 负责逐 TF 的开发引导（读上下文、建分支、出概要）。开发完成后由 dm-commit 负责提交。

```
dm-plan-ver (版本规划)
  └── Phase 2: TF 开发
        ├── dm-dev-tf — TF 启动（本 skill）
        └── dm-commit — TF 提交
```

## 触发

- "开始 TF3"
- "开发 TF2"
- "/dm-dev-tf 3"
- "/dm-dev-tf 3 auth-session"（带 topic 提示）
- "start TF1"

## 执行流程

### 1. 检测版本

从 `docs/versions/` 查找当前活跃的版本目录。如果存在多个版本，询问用户。如果不存在，提示用户先执行 dm-plan-ver。

### 2. 读取 TF 上下文

从 `docs/versions/vX.Y-<slug>/` 提取该 TF 相关内容：

| 文档 | 提取内容 |
|------|----------|
| `spec.md` | TF 业务目标、验收标准、验收锚点 |
| `general-design.md` | TF 数据流、对其它 TF 的依赖、跨 TF 状态机、测试策略 |
| `detailed-design.md` | TF 步骤、函数签名、Schema、单 TF 状态机/时序图 + 任务执行计划 |

### 3. 确认/创建 TF Issue

- 若 Phase 1 已创建该 TF Issue，确认编号与状态
- 若未创建，输出 Issue 内容：标题 `[TFx] <flow-name>`，包含目标、完成标准、依赖、验收方法

### 4. 创建 TF 分支

从版本分支切出：

```bash
git checkout -b feature/v<X.Y>-TF<N>-<topic>
```

- `<X.Y>`：从版本目录名提取
- `<N>`：TF 编号
- `<topic>`：用户传入则直接用；否则从 `general-design.md` 中该 TF 的一句话职责推导（如 `credential-validation`、`data-preprocessing`）

### 5. 输出开发概要

结构化输出：

```
## TF<N> 开发概要 — <flow-name>

**目标**：<spec.md 的一句话目标>
**分支**：feature/v<X.Y>-TF<N>-<topic>
**Issue**：#<N>

### 关键文件
- <file> — <用途>
- ...

### 依赖
- 前序 TF：<列表或"无">
- 外部依赖：<列表或"无">

### 测试策略
- 级别：<unit / integration / e2e>
- 关键场景：<来自 general-design.md>

### 开发步骤（来自 detailed-design.md）
1. <步骤>
2. <步骤>
...
```

## 关键规则速查

| 规则 | 来源 |
|------|------|
| 始终从 `docs/versions/` 自动检测版本，不可假定 | — |
| 分支从版本分支切出，不从 main | git-flow-rules.md §4 |
| topic 小写、连字符分隔，从 TF 名称推导 | git-flow-rules.md §4.1 |
| `detailed-design.md` 不完整时需在概要中标注 | version-rules.md |
| 提交委托 dm-commit，本 skill 仅负责启动阶段 | dm-commit.md |

## Skill 资源映射

| 资源 | 来源 | 用途 |
|------|------|------|
| SKILL.md | — | 上述启动流程指令 + 规则速查 |
| dm-plan-ver SKILL.md | — | 版本规划上下文、分支命名规范 |
| dm-plan-ver references/version-rules.md | `docs/version-rules.md` | TF 文档结构 |
| dm-plan-ver references/git-flow-rules.md | `docs/git-flow-rules.md` | 分支/Issue 规范 |

## 使用示例

```
用户: "开始 TF3"

AI:  1. 检测版本: docs/versions/v0.2-auth/ → v0.2
     2. 读取四件套，提取 TF3 相关内容
     3. 确认 Issue #15 [TF3] 会话管理 → 已创建，未关闭
     4. 创建分支: feature/v0.2-TF3-session-management
     5. 输出开发概要:
        ## TF3 开发概要 — 会话管理
        **目标**: 实现 token 签发、校验与刷新
        **分支**: feature/v0.2-TF3-session-management
        **Issue**: #15
        ### 关键文件
        - src/auth/session.ts — session 管理主逻辑
        - src/auth/token.ts — JWT 签发与校验
        ### 依赖
        - 前序 TF: TF2 验证流程
        - 外部依赖: 无
        ### 测试策略
        - 级别: unit
        - 关键场景: token 过期刷新、并发请求去重
        ### 开发步骤
        1. 实现 token 签发
        2. 实现 token 校验中间件
        3. 实现 refresh 并发去重
```
