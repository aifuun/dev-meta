# dm-dev-tf

## 概述

TF 开发引导 skill，读取版本文档上下文、确认/创建 TF Issue、输出开发概要。开发直接在现有版本分支上进行，TF 不处理分支创建/删除。是 dm-plan-ver Phase 2 中 TF 开发的"启动端"。

## 职责边界

| 职责 | 归属 |
|------|------|
| 读版本文档、提取 TF 上下文 | ✅ 本 skill |
| 确认/创建 TF Issue | ✅ 本 skill |
| 输出开发概要 | ✅ 本 skill |
| 分支创建/删除 | 版本级职责（dm-plan-ver），不在本 skill |
| TF 提交 | 委托 dm-commit |

## 关系

dm-dev-tf 嵌入 dm-plan-ver 的 Phase 2（TF 开发）：

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

## 核心概念

### TF 上下文来源

TF 开发概要从版本四件套提取，各文档提供不同视角：

| 文档 | 提供内容 |
|------|----------|
| `500-schedule.md` | 该 TF 对应工作包的状态 |
| `200-spec.md` | TF 业务目标、验收标准、验收锚点 |
| `300-design.md` | TF 数据流、对其它 TF 的依赖、跨 TF 状态机、测试策略 |
| `400-build.md` | TF 步骤、函数签名、Schema、单 TF 状态机/时序图 + 执行顺序矩阵 |

### 开发分支

- 开发直接在**当前版本分支** `feature/vX.Y-<slug>` 上进行，**不创建/删除分支**。
- 分支的创建/删除是版本级职责（dm-plan-ver），TF 级只负责在其上开发。

## 执行流程

### 1. 检测版本

从 `docs/versions/` 查找当前活跃的版本目录。如果存在多个版本，询问用户。如果不存在，提示用户先执行 dm-plan-ver。

### 2. 读取 TF 上下文

从 `docs/versions/vX.Y-<slug>/` 按「核心概念」的文档提取该 TF 相关内容。

### 3. 确认/创建 TF Issue

- 若 Phase 1 已创建该 TF Issue，确认编号与状态
- 若未创建，输出 Issue 内容：标题 `[TFx] <flow-name>`，包含目标、完成标准、依赖、验收方法

### 3.5 实现级 grill（仅当文档不完整时）

对照 `300-design.md` 检查当前 TF 的设计完整性。若存在缺口（数据流、模块边界、异常处理、兼容性等未定义），提出 **3-5 个针对缺口的决定性决策点**（不重复文档已有内容），回答沉淀进开发概要或对应文档章节；技术选型类触发 `dm-adr`。若 `300-design.md` 已完整覆盖该 TF，跳过本步骤。

> 原则见 skill-doc-principles §7「决策点显式收敛」。

### 4. 输出开发概要

结构化输出：

```
## TF<N> 开发概要 — <flow-name>

**目标**：<200-spec.md 的一句话目标>
**分支**：feature/v<X.Y>-<slug>（当前版本分支，不新建）
**Issue**：#<N>

### 关键文件
- <file> — <用途>
- ...

### 依赖
- 前序 TF：<列表或"无">
- 外部依赖：<列表或"无">

### 测试策略
- 级别：<unit / integration / e2e>
- 关键场景：<来自 300-design.md>

### 开发步骤（来自 400-build.md，含部署/联调环节）
1. <步骤>
2. <步骤>
...
```

## 关键规则速查

| 规则 | 来源 |
|------|------|
| 始终从 `docs/versions/` 自动检测版本，不可假定 | — |
| 直接在版本分支 `feature/vX.Y-<slug>` 上开发，**不创建/删除分支** | 03-git-flow-rules.md §4 |
| TF 开发步骤含部署/联调环节（归属 dev，不归 qa） | 02-version-rules.md §2.2 |
| `400-build.md` 不完整时需在概要中标注 | 02-version-rules.md |
| `300-design.md` 对当前 TF 不完整时，出概要前须执行实现级 grill，问答沉淀进文档 | skill-doc-principles.md §7 |
| 提交委托 dm-commit，本 skill 仅负责启动阶段 | dm-commit.md |

## 资源映射

| 资源 | 来源 | 用途 |
|------|------|------|
| SKILL.md | — | 上述启动流程指令 + 规则速查 |
| dm-plan-ver references/version-rules.md | `docs/02-version-rules.md` | TF 文档结构、环节定义 |
| dm-plan-ver references/git-flow-rules.md | `docs/03-git-flow-rules.md` | Issue 规范（分支归版本级，不在本 skill 处理） |

## 使用示例

```
用户: "开始 TF3"

AI:  1. 检测版本: docs/versions/v0.2-auth/ → v0.2（当前分支 feature/v0.2-auth）
     2. 读取四件套，提取 TF3 相关内容
     3. 确认 Issue #15 [TF3] 会话管理 → 已创建，未关闭
     4. 输出开发概要（不新建分支，直接在 feature/v0.2-auth 上开发）:
        ## TF3 开发概要 — 会话管理
        **目标**: 实现 token 签发、校验与刷新
        **分支**: feature/v0.2-auth（当前版本分支，不新建）
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
