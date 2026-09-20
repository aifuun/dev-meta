---
name: dm-dev-step
description: Step 全生命周期：启动（读版本文档、确认/创建版本 Issue、输出 Step 开发概要）→ 提交（委托 dm-commit，Refs 关联）→ 收尾（验收、勾选 Issue checklist、回写 500-schedule 执行记录）。开发在版本分支上，不建分支。触发于「开始 S2」「S2 完成了」「/dm-dev-step」。
---

# dm-dev-step

## 概述

Step 施工 skill，**拥有 Step 的整个生命周期**：启动（读文档 / 确认·创建版本 Issue / 出开发概要）→ 提交（委托 dm-commit）→ 收尾（验收 / 勾选 Issue checklist / 回写 `500-schedule.md`）。开发直接在现有版本分支上进行，Step 不处理分支创建/删除。是 `dm-plan-ver` 阶段 2 的唯一承接方。

> **Step 是版本内唯一的施工拆分单位**（`S0`–`S7`，定义见 `docs/02-version-rules.md` §6.2）。
> 版本内**不再划分业务流（TF）**；若发现一个 Step 装不下，说明版本过大，须退回 `dm-plan-roadmap` 重切。

## 职责边界

| 职责 | 归属 |
|------|------|
| 读版本文档、提取 Step 上下文 | ✅ 本 skill |
| 确认/创建**版本 Issue**（内容为 Step checklist） | ✅ 本 skill |
| 输出 Step 开发概要 | ✅ 本 skill |
| **Step 收尾**：验收 + 勾选版本 Issue 的 checklist 项 + 回写 `500-schedule.md`（工作包状态 / tracking-matrix / 执行记录） | ✅ 本 skill |
| **关闭版本 Issue** | ❌ 由版本 PR 合并时 merge commit 的 `Closes #id` 关闭（`dm-close-ver`） |
| 分支创建/删除 | 版本级职责（dm-plan-ver），不在本 skill |
| Step 提交 | 委托 dm-commit |
| 版本粒度实证（S4/S5 计数）与重切 | ❌ `dm-plan-ver` / `dm-plan-roadmap` |

## 关系

dm-dev-step 承接 dm-plan-ver 的**阶段 2**（施工），全程负责启动 → 提交 → 收尾：

```
dm-plan-ver (版本规划)
  └── 阶段 2: Step 施工 —— 委托后由本 skill 全程承接
        dm-dev-step（本 skill）
          ├── 启动：读文档 / 确认·创建版本 Issue / 出开发概要
          ├── 提交：委托 dm-commit
          └── 收尾：验收 → 勾选 Issue checklist → 回写 500-schedule
```

## 触发

- "开始 S2" / "做 S4"
- "S2 完成了"（进入收尾：验收 → commit(Refs) → 勾选 Issue checklist → 回写 500-schedule）
- "/dm-dev-step" / "/dm-dev-step S4"

## 核心概念

### Step 上下文来源

Step 开发概要从版本四件套提取，各文档提供不同视角：

| 文档 | 提供内容 |
|------|----------|
| `500-schedule.md` | 该 Step 对应工作包的状态 |
| `200-spec.md` | 核心业务场景、验收标准（本版本唯一的交付物） |
| `300-design.md` | 架构与分层、防腐设计、数据流与状态机、测试策略 |
| `400-build.md` | **Step 清单**（该 Step 的状态 / 环节 / guard）+ 该 Step 的明细（步骤、函数签名、异常边界） |

> 启动阶段从 `500-schedule.md` 只取**该 Step 工作包的状态**；「执行记录」是收尾时的**写入端**，
> 启动时不必读取（避免历史记录占用上下文）。

### 条件步与跳过

- 若目标 Step 在 `400-build` §2 中标记为 `⏭️ SKIPPED` → **不施工、不排工作包、不产生 commit**，
  直接告知用户并给出该步的跳过理由。
- 必做步（`S0` / `S1` / `S6` / `S7`）**不得**跳过；若发现被跳过，须回报 `dm-plan-ver` 修正。

### 开发分支

- 开发直接在**当前版本分支** `feature/v<版本>-<slug>` 上进行，**不创建/删除分支**。
- 分支的创建/删除是版本级职责（dm-plan-ver），Step 级只负责在其上开发。

## 执行流程

### 1. 检测版本

从 `docs/versions/` 查找当前活跃的版本目录。如果存在多个版本，询问用户。如果不存在，提示用户先执行 dm-plan-ver。

### 2. 读取 Step 上下文

从 `docs/versions/<版本>/` 按「核心概念」的文档提取该 Step 相关内容，并确认其在 `400-build` §2 的状态（执行 / `⏭️ SKIPPED`）。

### 3. 确认/创建版本 Issue

- 版本 Issue 是**版本级唯一**的（命名 `[vX.Y] <feature-name>`），由阶段 1 创建
- 若已存在，确认编号与状态；若未创建，输出 Issue 内容（目标、完成标准、依赖、验收方法、**Step 0–7 checklist**）

### 3.5 实现级 grill（仅当文档不完整时）

对照 `300-design.md` 检查当前 Step 的设计完整性。若存在缺口（数据流、模块边界、异常处理、兼容性等未定义），提出 **3-5 个针对缺口的决定性决策点**（不重复文档已有内容），回答沉淀进开发概要或对应文档章节；技术选型类触发 `dm-adr`。若 `300-design.md` 已完整覆盖该 Step，跳过本步骤。契约质量缺口按 `docs/06-contract-based-dev.md` §3 维度核查（错误契约/幂等/兼容/不变量是否齐全）。

> 原则见 skill-doc-principles §7「决策点显式收敛」。

### 4. 输出 Step 开发概要

结构化输出：

```
## S<N> 开发概要 — <Step 名称>

**目标**：<200-spec.md 的核心业务场景中，本 Step 承担的部分>
**分支**：feature/v<版本>-<slug>（当前版本分支，不新建）
**Issue**：#<N>
**guard**：<该 Step 须通过的 GUARD 编号，来自 400-build §2>

### 关键文件
- <file> — <用途>

### 依赖
- 前序 Step：<列表或"无">
- 外部依赖：<列表或"无">

### 测试策略
> **契约式开发核心（详见 `docs/06-contract-based-dev.md`，即使链接失效也以本句为准）**：
> ① 先契约后实现；② L1 接口契约含错误/幂等/兼容/限流，L2 Feature 契约含失败语义/前置后置/依赖方向，L3 行为契约仅算法类必填（given-when-then）；③ 测试三层分工 design=场景 / build=行为契约 / dev-step=落地，互不重定义；④ 契约质量基线要求错误透明、命名即契约、不可变默认、显式边界校验；⑤ 下层契约不得违背上层。

- 级别：<unit / integration / e2e>（来自 300-design.md §7）
- 关键场景：<来自 300-design.md §7>
- 不变量：<来自 400-build.md 关键行为契约的不变量项；无则写"无">
- 行为预期：<来自 400-build.md 关键行为契约；dm-dev-step 据此生成真实单测，不重新定义行为>
- 测试职责分层见 `docs/06-contract-based-dev.md` §10

### 自底向上顺序（强制）
1. Pure Model / Domain
2. Use Case / Application
3. ViewModel / State
4. UI / Presentation

### 开发步骤（来自 400-build.md，含部署/联调环节）
1. <步骤>
2. <步骤>
...
```

> **自底向上顺序**见 `docs/09-ai-architecture-guide.md` §3.4，禁止逆向。

### 5. Step 收尾（用户说「S<n> 完成了」时执行）

1. **确认验收**：对照 `200-spec.md` 中相关验收标准与 `400-build` §2 该 Step 的交付物
2. **执行 commit** — 委托 dm-commit：`type(scope): subject (S<n>)` + **`Refs #id`**
   （subject 末尾的 `(S<n>)` 为 Step 关联标记，合法形式 `\(S[0-7]\)$`；
   **Step 级一律 `Refs`** —— Issue 是版本级的，Step 完成 ≠ 版本完成）
3. **勾选版本 Issue 中本 Step 的 checklist 项** —— **不关闭 Issue**；
   版本 Issue 由版本 PR 合并时 merge commit 的 `Closes #id` 关闭（`dm-close-ver` 执行）
4. **回写 `500-schedule.md`**：工作包状态 + tracking-matrix + **追加执行记录一条**
   （五段：概要 / 偏差 / 发现 / 失误 / 遗留；每条 ≤8 行，append-only；
   被推翻的判断用 ~~删除线~~ 保留；日常流水进 worklog，不重复记；状态只改工作包列表一处）

   > **概要段的写法**：用**一句话**说清两件事 ——
   > ① 本 Step 的**主要工作与完成内容**；② 它在**整个版本**中承担的作用。
   > 偏差与发现不写在这里，归后两段。

## 关键规则速查

| 规则 | 来源 |
|------|------|
| Step 是版本内唯一的施工拆分单位（`S0`–`S7`）；发现装不下 → 退回 `dm-plan-roadmap` 重切，**不得加 TF** | `docs/02` §3.2 / §6.2 |
| `⏭️ SKIPPED` 的 Step 不施工、不排工作包、不产生 commit | `docs/02` §6.1 |
| 始终从 `docs/versions/` 自动检测版本，不可假定 | — |
| 直接在版本分支 `feature/v<版本>-<slug>` 上开发，**不创建/删除分支** | 03-git-flow-rules.md §4.1 |
| 自底向上顺序：Pure Model → Use Case → ViewModel → UI，**禁止逆向** | `docs/09` §3.4 |
| Step 开发步骤含部署/联调环节（归属 dev，不归 qa） | 02-version-rules.md §2.2 |
| `400-build.md` 不完整时需在概要中标注 | 02-version-rules.md |
| `300-design.md` 对当前 Step 不完整时，出概要前须执行实现级 grill，问答沉淀进文档 | skill-doc-principles.md §7 |
| Step 全生命周期归本 skill（启动 → 提交 → 收尾回写）；提交环节委托 dm-commit | 本 skill 职责边界 |
| Step 级 commit 一律 `Refs #id`；版本 Issue 由 merge 的 `Closes` 关闭，**Step 不关 Issue** | 03-git-flow-rules.md §3.4 / §4.2 |
| commit 以 `(S<n>)` 结尾标记 Step；跳过步不产生 commit | 03-git-flow-rules.md §3.4 |
| Step 收尾回写 `500-schedule.md`：工作包状态 + tracking-matrix + 执行记录一条（≤8 行，append-only） | 02-version-rules.md §2 / §6 |
| 契约须标注四要素（归属/方向/不变性/真值来源）+ 域-序号编号 | docs/06-contract-based-dev.md §4 |
| 失败面契约：纯函数式失败返回空/原值而非 nil；严禁静默危险失败 | docs/06-contract-based-dev.md §5 |
| Micro-Batching：Step 内按三 Batch 推进（契约/数据模型→Core 单文件→UI/调用点）；每绿灯 Batch 由用户触发 commit | docs/08-small-batch-iteration.md |
| 诊断契约：错误/降级路径须结构化诊断，高开销节点含 Elapsed + 资源指标 | docs/07-observability-driven-dev.md |
| 轨迹（启用时）：每观测点须给**判别量**（禁「已到达某步」）；验证落**集成 / E2E 完整链路**，不以单测代替 | docs/07-observability-driven-dev.md §3.2 |

## 产出与完成判据

**产出**：

- Step 开发概要：目标、关键文件、依赖、测试策略、自底向上顺序
- 版本 Issue（确认或创建）并关联版本 PR
- Step 收尾回写：工作包状态 + tracking-matrix + 执行记录一条

**完成判据**：

- [ ] 已读取版本文档（`200-spec` / `300-design` / `400-build` / `500-schedule`）
- [ ] 已确认目标 Step 在 `400-build` §2 的状态；`⏭️ SKIPPED` 的直接终止
- [ ] Issue 已确认或创建，并关联到版本 PR
- [ ] 开发概要含**目标 / 关键文件 / 依赖 / 测试策略**四要素，且含自底向上顺序
- [ ] 执行粒度收敛到**单文件重构 / 单函数修复**（见 `docs/08`）
- [ ] 在**现有版本分支**上开发（本 skill 不建分支）
- [ ] Step 收尾已回写 `500-schedule.md`（工作包状态 + tracking-matrix + 执行记录一条）

## 资源映射

| 资源 | 来源 | 用途 |
|------|------|------|
| SKILL.md | — | 上述启动流程指令 + 规则速查 |
| dm-plan-ver references/version-rules.md | `docs/02-version-rules.md` | Step 定义、四件套结构、环节定义 |
| dm-plan-ver references/git-flow-rules.md | `docs/03-git-flow-rules.md` | Issue 规范（分支归版本级，不在本 skill 处理） |
| dm-commit references/git-flow-rules.md | `docs/03-git-flow-rules.md` | commit 格式规则（含 `(S<n>)` 标记） |
| dm-plan-ver assets/tracking-matrix.md | — | 收尾时更新 Step→Issue→PR→验收结果 追踪矩阵 |

## 使用示例

```
用户: "开始 S2"

AI:  1. 检测版本: docs/versions/v1.4.1-indexeddb-prefs/ → 当前分支 feature/v1.4.1-indexeddb-prefs
     2. 读取四件套，提取 S2 相关内容；确认 400-build §2 中 S2 状态 = 执行
     3. 确认 Issue #15 [v1.4.1] per-trackId 偏好持久化 → 已创建，未关闭
     4. 输出 S2 开发概要（不新建分支，直接在版本分支上开发）:
        ## S2 开发概要 — Core & Prototype
        **目标**: 建成可独立单测的存储引擎（audio-store + prefs-store）
        **分支**: feature/v1.4.1-indexeddb-prefs（当前版本分支，不新建）
        **Issue**: #15
        **guard**: GUARD-01
        ### 关键文件
        - src/storage/audio-store.js — IndexedDB 打开与能力探测
        - src/storage/prefs-store.js — per-trackId 偏好读写
        ### 测试策略
        - 级别: unit
        - 关键场景: IDB 不可用时 save 不抛错、load 无记录返回空
        ### 自底向上顺序
        1. Pure Model（偏好数据结构）  2. Use Case（prefs-store 门面）

用户: "S2 完成了"

AI:  1. 对照 200-spec 验收标准确认
     2. commit: feat(storage): add audio-store and prefs-store (S2)
        Refs #15
     3. 勾选 Issue #15 的 S2 项（Issue 保持 open —— 由版本 merge 时 Closes 关闭）
     4. 回写 500-schedule：工作包状态 ✅ + tracking-matrix + 执行记录一条
        #### S2 Core & Prototype（7c1e4a2）
        - 概要：建成 prefs-store 门面与 audio-store 能力探测，为版本提供存储底座
        - 偏差：无
        - 发现：节流间隔 1s 时写入耗时稳定 < 5ms，无需 S3 量化定案
        - 失误：无
        - 遗留：→ S4 接入播放链路
```
