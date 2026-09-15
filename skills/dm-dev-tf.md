---
name: dm-dev-tf
description: TF 全生命周期：启动（读版本文档、确认/创建 Issue、输出开发概要）→ 提交（委托 dm-commit）→ 收尾（验收、关 Issue、回写 500-schedule 执行记录）。开发在版本分支上，不建分支。触发于「开始 TF3」「TF3 完成了」「/dm-dev-tf」。
---

# dm-dev-tf

## 概述

TF 开发 skill，**拥有 TF 的整个生命周期**：启动（读文档 / 确认·创建 Issue / 出开发概要）→ 提交（委托 dm-commit）→ 收尾（验收 / 关 Issue / 回写 `500-schedule.md`）。开发直接在现有版本分支上进行，TF 不处理分支创建/删除。是 `dm-plan-ver` 阶段 2 的唯一承接方。

## 职责边界

| 职责 | 归属 |
|------|------|
| 读版本文档、提取 TF 上下文 | ✅ 本 skill |
| 确认/创建 TF Issue | ✅ 本 skill |
| 输出开发概要 | ✅ 本 skill |
| **TF 收尾**：验收 + 关闭 Issue + 回写 `500-schedule.md`（工作包状态 / tracking-matrix / 执行记录） | ✅ 本 skill |
| 分支创建/删除 | 版本级职责（dm-plan-ver），不在本 skill |
| TF 提交 | 委托 dm-commit |

## 关系

dm-dev-tf 承接 dm-plan-ver 的**阶段 2**（TF 开发），全程负责启动 → 提交 → 收尾：

```
dm-plan-ver (版本规划)
  └── 阶段 2: TF 开发 —— 委托后由本 skill 全程承接
        dm-dev-tf（本 skill）
          ├── 启动：读文档 / 确认·创建 Issue / 出开发概要
          ├── 提交：委托 dm-commit
          └── 收尾：验收 → 关 Issue → 回写 500-schedule
```

## 触发

- "开始 TF3"
- "开发 TF2"
- "/dm-dev-tf 3"
- "/dm-dev-tf 3 auth-session"（带 topic 提示）
- "start TF1"
- "TF1 完成了"（进入收尾：验收 → commit → 关 Issue → 回写 500-schedule）

## 核心概念

### TF 上下文来源

TF 开发概要从版本四件套提取，各文档提供不同视角：

| 文档 | 提供内容 |
|------|----------|
| `500-schedule.md` | 该 TF 对应工作包的状态 |
| `200-spec.md` | TF 业务目标、验收标准、验收锚点 |
| `300-design.md` | TF 数据流、对其它 TF 的依赖、跨 TF 状态机、测试策略 |
| `400-build.md` | TF 步骤、函数签名、Schema、单 TF 状态机/时序图 + 执行顺序矩阵 |

> 启动阶段从 `500-schedule.md` 只取**该 TF 工作包的状态**；「执行记录」是收尾时的**写入端**，
> 启动时不必读取（避免历史记录占用上下文）。

### 开发分支

- 开发直接在**当前版本分支** `feature/vX.Y-<slug>` 上进行，**不创建/删除分支**。
- 分支的创建/删除是版本级职责（dm-plan-ver），TF 级只负责在其上开发。

## 执行流程

### 1. 检测版本

从 `docs/versions/` 查找当前活跃的版本目录。如果存在多个版本，询问用户。如果不存在，提示用户先执行 dm-plan-ver。

### 2. 读取 TF 上下文

从 `docs/versions/vX.Y-<slug>/` 按「核心概念」的文档提取该 TF 相关内容。

### 3. 确认/创建 TF Issue

- 若阶段 1（版本启动）已创建该 TF Issue，确认编号与状态
- 若未创建，输出 Issue 内容：标题 `[TFx] <flow-name>`，包含目标、完成标准、依赖、验收方法

### 3.5 实现级 grill（仅当文档不完整时）

对照 `300-design.md` 检查当前 TF 的设计完整性。若存在缺口（数据流、模块边界、异常处理、兼容性等未定义），提出 **3-5 个针对缺口的决定性决策点**（不重复文档已有内容），回答沉淀进开发概要或对应文档章节；技术选型类触发 `dm-adr`。若 `300-design.md` 已完整覆盖该 TF，跳过本步骤。契约质量缺口按 `docs/06-contract-based-dev.md` §2.5 维度核查（错误契约/幂等/兼容/不变量是否齐全）。

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
> **契约式开发核心（详见 `docs/06-contract-based-dev.md`，即使链接失效也以本句为准）**：
> ① 先契约后实现；② L1 接口契约含错误/幂等/兼容/限流，L2 TF 契约含失败语义/前置后置/依赖方向，L3 行为契约仅算法类必填（given-when-then）；③ 测试三层分工 design=场景 / build=行为契约 / dev-tf=落地，互不重定义；④ 契约质量基线要求错误透明、命名即契约、不可变默认、显式边界校验；⑤ 下层契约不得违背上层。

- 级别：<unit / integration / e2e>（来自 300-design.md §7）
- 关键场景：<来自 300-design.md §7>
- 不变量：<来自 400-build.md 关键行为契约的不变量项；无则写"无">
- 行为预期：<来自 400-build.md 关键行为契约；dm-dev-tf 据此生成真实单测，不重新定义行为>
- 测试职责分层见 `docs/06-contract-based-dev.md` §3

### 开发步骤（来自 400-build.md，含部署/联调环节）
1. <步骤>
2. <步骤>
...
```

### 5. TF 收尾（用户说「TFn 完成了」时执行）

1. **确认验收**：对照 `200-spec.md` 中该 TF 的验收标准
2. **执行 commit** — 委托 dm-commit：`type(scope): subject` + `Closes #id`
3. **关闭本 TF 的 Issue**（`Closes` footer 自动关闭；未自动关闭的手动关闭，标记验收结果）
4. **回写 `500-schedule.md`**：工作包状态 + tracking-matrix + **追加执行记录一条**
   （五段：概要 / 偏差 / 发现 / 失误 / 遗留；每条 ≤8 行，append-only；
   被推翻的判断用 ~~删除线~~ 保留；日常流水进 worklog，不重复记；状态只改工作包列表一处）

## 关键规则速查

| 规则 | 来源 |
|------|------|
| 始终从 `docs/versions/` 自动检测版本，不可假定 | — |
| 直接在版本分支 `feature/vX.Y-<slug>` 上开发，**不创建/删除分支** | 03-git-flow-rules.md §4 |
| TF 开发步骤含部署/联调环节（归属 dev，不归 qa） | 02-version-rules.md §2.2 |
| `400-build.md` 不完整时需在概要中标注 | 02-version-rules.md |
| `300-design.md` 对当前 TF 不完整时，出概要前须执行实现级 grill，问答沉淀进文档 | skill-doc-principles.md §7 |
| TF 全生命周期归本 skill（启动 → 提交 → 收尾回写）；提交环节委托 dm-commit | 本 skill 职责边界 |
| TF 收尾回写 `500-schedule.md`：工作包状态 + tracking-matrix + 执行记录一条（≤8 行，append-only） | 02-version-rules.md §6.1 |
| 契约须标注四要素（归属/方向/不变性/真值来源）+ 域-序号编号；质量维度作为不变性项落地 | docs/06-contract-based-dev.md §2.6 |
| 失败面契约：纯函数式失败返回空/原值而非 nil；严禁静默危险失败，须调用前拦截显式暴露（隐性契约债核查见 §2.7） | docs/06-contract-based-dev.md §2.7 |
| Micro-Batching：TF 内按三 Batch 推进（契约/数据模型→Core 单文件→UI/调用点），AI 执行粒度=单文件重构/单函数修复；每绿灯 Batch 由用户触发 commit，混乱时用户 `git reset --hard` 退回（AI 不自发），随后 New Session | docs/08-small-batch-iteration.md |
| 契约演进治理：破坏性变更走 dm-adr；纯增量 PR 标注；新接口回写总目录（无主防护） | docs/06-contract-based-dev.md §5 |
| 诊断契约：行为预期来自 400-build；错误/降级路径须结构化诊断（07 §2.1/§3），高开销节点（推理/IO/跨进程）须含 Elapsed Time + 资源指标（07 §2.3）；复用 observe 包装器（07 §4），无静默吞错 | docs/07-observability-driven-dev.md |

## 产出与完成判据

**产出**：

- 开发概要：目标、关键文件、依赖、测试策略
- TF Issue（确认或创建）并关联版本 PR

**完成判据**：

- [ ] 已读取版本文档（`200-spec` / `300-design` / `400-build`）
- [ ] Issue 已确认或创建，并关联到版本 PR
- [ ] 开发概要含**目标 / 关键文件 / 依赖 / 测试策略**四要素
- [ ] 执行粒度收敛到**单文件重构 / 单函数修复**（见 `docs/08`）
- [ ] 在**现有版本分支**上开发（本 skill 不建分支）
- [ ] TF 收尾已回写 `500-schedule.md`（工作包状态 + tracking-matrix + 执行记录一条）

## 资源映射

| 资源 | 来源 | 用途 |
|------|------|------|
| SKILL.md | — | 上述启动流程指令 + 规则速查 |
| dm-plan-ver references/version-rules.md | `docs/02-version-rules.md` | TF 文档结构、环节定义 |
| dm-plan-ver references/git-flow-rules.md | `docs/03-git-flow-rules.md` | Issue 规范（分支归版本级，不在本 skill 处理） |
| dm-commit references/git-flow-rules.md | `docs/03-git-flow-rules.md` | commit 格式规则 |
| dm-plan-ver assets/tracking-matrix.md | — | 收尾时更新 TF→Issue→PR→验收 追踪矩阵 |

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

用户: "TF3 完成了"

AI:  1. 对照 200-spec 验收标准确认
     2. commit: feat(auth): implement session issue/verify/refresh
        Closes #15
     3. 关闭 Issue #15
     4. 回写 500-schedule：工作包状态 ✅ + tracking-matrix + 执行记录一条
        #### TF3 — 会话管理（a1b2c3d）
        - 概要：基于 v0.1 会话基线，实现签发 / 校验 / 刷新
        - 偏差：无
        - 发现：并发刷新须去重，否则双 token 同时失效
        - 失误：无
        - 遗留：→ 无
```
