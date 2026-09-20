---
name: dm-plan-ver
description: 新建版本：创建版本文档四件套、分支/PR、版本 Issue，并在产出 200-spec/300-design 前执行需求级/架构级 grill。触发于「新建版本 vX.Y」。
---

# dm-plan-ver

## 概述

版本启动 skill，负责版本级规划与启动：创建版本文档四件套、分支、PR、版本 Issue 生成与追踪。

## 职责边界

| 职责 | 归属 |
|------|------|
| 创建版本文档四件套 + 分支 + PR + 版本 Issue | ✅ 本 skill |
| Step 开发全生命周期（启动 → 提交 → 收尾回写） | 委托 dm-dev-step |
| 提交格式（Step 内由 dm-dev-step 调用） | 委托 dm-commit |
| 版本收尾（merge / 关 Issue / 清理分支） | 委托 dm-close-ver |

## 触发

- "新建版本 v1.2-payment"
- "开始 vX.Y"
- "创建 Step 文档"

## 核心概念

### 四件套结构

版本目录 `docs/versions/vX.Y-<slug>/` 下的四个文档，按依赖顺序创建：

| 文档 | 回答的问题 | 前置依赖 |
|------|-----------|----------|
| `200-spec.md` | 交付什么？怎样算完成？ | — |
| `300-design.md` | 流程如何串联？模块如何分工？ | spec |
| `400-build.md` | 怎么实现？怎么执行？ | design |
| `500-schedule.md` | 什么时候做什么？按什么顺序？ | build（委托 dm-schedule） |

### Step 施工清单（400-build §2）

400-build §2 的 Step 清单承载 **Step 状态、环节、依赖约束与验收约束（guard）**：

| 列 | 内容 |
|----|------|
| Step | `S0`–`S7`，**固定 8 行**，不得增删 |
| 名称 | 固定（见 `docs/02-version-rules.md` §6.2） |
| 状态 | 执行 / `⏭️ SKIPPED`（跳过须写理由，格式固定为「跳过：<理由>」） |
| 环节 | 所属交付环节（开发/部署/联调/测试/发布…），使环节顺序与 schedule 对齐 |
| guard | 该 Step 须通过的防腐契约编号（`GUARD-01,03`…）；每个编号须能在 §1.4 找到对应行 |
| 交付物 / 跳过理由 | 交付物清单；跳过时写理由 |

- **必做步（S0 / S1 / S6 / S7）不得标记 `⏭️ SKIPPED`**。
- **粒度实证（本 skill 的硬职责）**：**S4 / S5 各只出现一次**。多于一次 → 版本过大，
  **退回 `dm-plan-roadmap` 重切**，不得在版本内自行加层级。
- 任务简述、预估工时、状态由 `500-schedule.md` 承载，不在清单重复。
- 环节完整定义见 `dm-schedule`「核心概念」环节↔类别表（唯一权威）。

### 追踪矩阵（tracking-matrix）

**版本 Issue 唯一**（命名 `[vX.Y] <feature-name>`），追踪矩阵的行以 **Step** 为单位：

| Step | Issue | PR | 验收 |
|----|-------|-----|------|
| S0 Scaffold & Clean | #xx | #xx | ⬜ |

### Grill 决策收敛

在产出关键文档前，对影响实现/验收的决策点做显式「提问 → 回答 → 沉淀」三步，**不依赖 AI 自问自答**（原则见 skill-doc-principles §7）：

| 触发点 | Grill 级别 | 提问范围 |
|--------|-----------|----------|
| 创建 `200-spec.md` 前 | 需求级 | 范围边界、完成标准、降级策略、明确排除项、**架构锚点五维**（触及哪些分层 / 模块 / 门面、**受影响契约及是否阻塞编码** / 对外 API 变更形态） |
| 创建 `300-design.md` 前 | 架构级（最关键） | 数据流、模块边界、异常处理、兼容性、技术选型 |

> 📌 **需求级 grill 问架构锚点的边界**：只问「本版本动到架构哪几处」「受影响契约是否阻塞编码」，
> **不问「为什么这样设计」** —— 论证属 `300-design.md`，留到架构级 grill。避免 `200-spec` 膨胀成第二份设计文档。

- 每次提出 **3-5 个决定性决策点**，不重复文档已有内容。
- 沉淀规则：决策性回答写入对应文档章节；技术选型类回答触发 `dm-adr` 记录；问答不得留在对话流中丢失。

## 执行流程

> ⚠️ **前置检查（必做）**：四件套模板来自发布后的资产目录 `~/.dev-meta/templates/versions/`。
> 若该目录不存在（首次安装、或尚未执行过发布），**先提示用户执行**再继续：
>
> ```bash
> cd <dev-meta 仓库> && python3 pub_local.py
> ```
>
> 不要凭印象手写模板 —— 否则结构会与 `docs/02 §4` 漂移。

### 阶段 1：版本启动（核心）

```
用户: "新建版本 v1.3-export"
```

1. **创建版本文档** `docs/versions/v1.3-export/`（四件套，顺序见「核心概念」；`200-spec.md` 与 `300-design.md` 产出前分别执行需求级/架构级 grill，见「核心概念」Grill 决策收敛）
   - **需求级 grill**（创建 `200-spec.md` 前）：围绕范围边界、完成标准、降级策略、排除项提问，回答沉淀进 `200-spec.md`
   - 创建 `200-spec.md`
   - **架构级 grill**（创建 `300-design.md` 前）：围绕数据流、模块边界、异常处理、兼容性、技术选型提问，回答沉淀进 `300-design.md`（技术选型类触发 `dm-adr`）
   - 创建 `300-design.md`、`400-build.md`（`400-build.md` §2 Step 清单按固定 `S0`–`S7` 顺序填写、不得增删；逐行标注环节与 guard，定义见 `docs/02` §6.2）

2. **创建分支**
   ```bash
   git checkout -b feature/v1.3-export
   ```

3. **生成 PR 描述**
   - 标题：`[V1.3.0] Export to PDF`
   - 填写：目标、范围、验收入口、风险与回滚
   - 若用户装有 `gh` CLI，可直接创建 PR

3.5 **开版本 Issue 前的契约门禁自检（Gate）**
   生成 Issue（即把 Step 列为可执行单元）之前，确认 `400-build.md` 已落地 06/07/08 基线，否则退回补写、不开 Issue：
   - **06 契约式开发**：含 L1/L2/L3 行为契约、Step 清单带环节、失败面不静默、契约四要素标注（归属/方向/不变性/真值来源 + 域-序号编号，见 `docs/06-contract-based-dev.md` §2.5/§2.6/§2.7/§3）
   - **07 可观测性**：行为契约含诊断契约（关键路径 observe 包装 + 状态留痕 + 无静默吞错，见 `docs/07-observability-driven-dev.md` §2.1/§3/§7）
   - **08 小步开发**：计划可拆成单文件批次（AI 执行粒度 = 单文件重构/单函数修复，见 `docs/08-small-batch-iteration.md`）
   - **结构零残留**：`200-spec` / `300-design` 的**标题**中不得出现 `Transaction Flow` / `TF` / `Step`（属 `400-build`）；
     检查**只扫标题**，且须**豁免历史版本**（见 `docs/02` §3.7 / §8）
   - 建议对该文档跑 `dm-contract-gate` 做静态合规校验；本 skill 仅**引用**其结论（不实现校验逻辑、不委托其开发），不通过则不开 Issue。

4. **生成版本 Issue**（版本级唯一，不按 Step 拆多个）
   - 标题：`[vX.Y] <feature-name>`
   - 填写：目标、完成标准、依赖、验收方法、**Step 0–7 checklist**（`- [ ] S0 Scaffold & Clean` …）
   - 关联到版本 PR，输出追踪矩阵

### 阶段 2：Step 开发（委托 dm-dev-step，本 skill 不执行）

Step 的**全生命周期**归 `dm-dev-step`，本 skill 只做**一次委托**，不参与其中任何步骤：

- **启动**：读文档、确认/创建 Issue、出开发概要（开发在版本分支上，不建分支）
- **提交**：委托 `dm-commit`（`type(scope): subject` + `Closes #id`）
- **收尾**：验收 → 关 Issue → 回写 `500-schedule.md`（工作包状态 + tracking-matrix + 执行记录一条）

```
用户: "开始 S2"  /  "S2 完成了"
```

两种说法均触发 `dm-dev-step`，由其按上述三阶段推进。
执行记录规则（每条 ≤8 行 / append-only / 日常流水进 worklog）见 `dm-dev-step`。

### 阶段 3：版本收尾（委托 dm-close-ver）

```
用户: "关闭版本 v1.3-export"
```

用户要求关闭版本时，委托 **dm-close-ver**。本 skill 不再处理收尾；dm-close-ver 拥有完整流程（就绪审计 → 收尾执行 → 保留历史的 merge → 关闭 版本 Issue → 清理分支 → 关闭后确认）。

## 关键规则速查

| 规则 | 来源 |
|------|------|
| **版本粒度红线**：一个版本只承载单一核心业务场景；写完后须**实证** S4/S5 各只出现一次 | 02-version-rules.md §3.2 |
| 实证失败 → **退回 dm-plan-roadmap 重切**，不得在版本内加层级 | 02-version-rules.md §3.2 |
| 编号遵 `v` / `r` 双轴与 Epoch 号段留白（本 skill 执行，规则见 `dm-plan-roadmap`） | 02-version-rules.md §3.3 |
| `200-spec` / `300-design` **不得出现** `Transaction Flow` / `TF` / `Step` 章节（标题级零残留） | 02-version-rules.md §8 |
| `200-spec` 含 §1 架构锚点（分层 / 模块 / 门面 / 契约 / API），只做范围声明不做设计论证 | 02-version-rules.md §3.4 / §4 |
| `200-spec` DoD 为**确认类** checklist，不得写成实现任务清单 | 02-version-rules.md §4 / §8 |
| 防腐编号 `GUARD-0x` 落 `400-build` §1.4 + Step 清单 `guard` 列；**与契约层级 L1/L2/L3 无关** | 02-version-rules.md §3.5 / §6 |
| Step 全生命周期（启动 → 提交 → 收尾回写）委托 dm-dev-step，本 skill 不执行 | 本 skill 职责边界 |
| 每版本 1 PR，每版本 1 Issue | 03-git-flow-rules.md §2 |
| commit: `type(scope): subject` + `Closes #id`，详见 dm-commit | 03-git-flow-rules.md §3 |
| 分支: `feature/v<version>-<slug>`（版本级；Step 不建分支，开发在版本分支上进行） | 03-git-flow-rules.md §4 |
| 收尾: 委托 dm-close-ver（保留历史 merge，不用 squash） | dm-close-ver.md |
| Step 清单固定 8 行，含状态 / 环节 / guard / 交付物；必做步不得 SKIPPED | 02-version-rules.md §6.1 |
| dev 工作包含代码+部署+联调（部署/联调归 dev） | 02-version-rules.md §2.2 |
| `200-spec.md`/`300-design.md` 产出前须执行需求级/架构级 grill，问答沉淀进文档，不留在对话流 | skill-doc-principles.md §7 |
> **契约式开发核心（详见 `docs/06-contract-based-dev.md`，即使链接失效也以本句为准）**：
> ① 先契约后实现；② L1 接口契约含错误/幂等/兼容/限流，L2 Feature 契约含失败语义/前置后置/依赖方向，L3 行为契约仅算法类必填（given-when-then）；③ 测试三层分工 design=场景 / build=行为契约 / dev-step=落地，互不重定义；④ 契约质量基线要求错误透明、命名即契约、不可变默认、显式边界校验；⑤ 下层契约不得违背上层。

| `400-build.md` 对算法/隐性契约类函数须含「关键行为契约（关键测试用例）」，薄胶水/CRUD 可省略；测试职责分层见 docs/06-contract-based-dev.md §3 | templates/versions/vX.Y-<slug>/400-build.md + docs/06-contract-based-dev.md §3 |
| `400-build.md` 须覆盖契约质量基线维度（错误/幂等/兼容/不变量等，见 docs/06-contract-based-dev.md §2.5）；缺维度须在 grill/设计阶段补齐 | docs/06-contract-based-dev.md §2.5 |
| 契约须标注四要素（归属/方向/不变性/真值来源）+ 域-序号编号；质量维度作为不变性项落地 | docs/06-contract-based-dev.md §2.6 |
| 失败面契约：纯函数式失败返回空/原值而非 nil；严禁静默危险失败，须调用前拦截显式暴露 | docs/06-contract-based-dev.md §2.7 |
| 契约演进治理：破坏性变更走 dm-adr；纯增量 PR 标注；新接口回写总目录（无主防护） | docs/06-contract-based-dev.md §5 |
| 可观测性诊断契约：400-build 行为契约须含诊断契约（关键路径 observe 包装 + 状态留痕 + 无静默吞错），见 docs/07-observability-driven-dev.md §2.1/§3/§7 | docs/07-observability-driven-dev.md |
| 版本计划须可拆成单文件批次（AI 执行粒度 = 单文件重构/单函数修复），供逐 Batch 推进，见 docs/08-small-batch-iteration.md | docs/08-small-batch-iteration.md |

## 产出与完成判据

**产出**：

- 版本四件套（`200-spec` / `300-design` / `400-build` / `500-schedule`）
- 分支 `feature/v<version>-<slug>` + 版本 PR + **1 个版本 Issue**（内容含 Step 0–7 checklist）
- 追踪矩阵（Step → Issue → PR → 验收）

**完成判据**：

- [ ] 四件套按依赖顺序创建（spec → design → build → schedule）
- [ ] `200-spec` / `300-design` 产出前已执行**需求级 / 架构级 grill** 并沉淀
- [ ] `200-spec` §1 **架构锚点已填写**（分层 / 模块 / 门面 / 契约 / API 五维齐全，只做范围声明）
- [ ] `200-spec` §1 **受影响契约已登记**，且标记「阻塞编码」者已定案 / 回写至契约 SSOT
- [ ] **粒度实证通过**：`400-build` §2 中 S4 / S5 **各只出现一次**（否则退回 `dm-plan-roadmap` 重切）
- [ ] **结构零残留**：`200-spec` / `300-design` 标题中无 `Transaction Flow` / `TF` / `Step`
- [ ] 分支、PR、版本 Issue 已创建且互相关联
- [ ] `400-build` 含 Step 0–7 清单，状态 / 环节 / guard / 交付物齐全
- [ ] 契约门禁基线（06 / 07 / 08）已满足
- [ ] 追踪矩阵已输出

## 资源映射

| 资源 | 来源 | 用途 |
|------|------|------|
| SKILL.md | — | 上述全流程指令 + 关键规则速查 |
| references/version-rules.md | `docs/02-version-rules.md` | 四件套规则详情 |
| references/git-flow-rules.md | `docs/03-git-flow-rules.md` | PR/Issue/commit 规则详情 |
| `~/.dev-meta/templates/versions/vX.Y-<slug>/200-spec.md` | `templates/versions/vX.Y-<slug>/200-spec.md`（发布后） | 规格模板（核心业务场景 + 架构锚点 + 验收 + DoD） |
| `~/.dev-meta/templates/versions/vX.Y-<slug>/300-design.md` | 同上（发布后） | 设计模板 |
| `~/.dev-meta/templates/versions/vX.Y-<slug>/400-build.md` | 同上（发布后） | 实现蓝图 + Step 0–7 施工清单模板 |
| assets/tracking-matrix.md | 新增 | Step→Issue→PR 追踪模板 |

## 使用示例

```
用户: "新建版本 v1.5-login"

AI:  1. 创建 docs/versions/v1.5-login/ 四件套
     2. 创建分支 feature/v1.5-login
     3. 输出 PR 描述模板（标题 + 目标/范围/验收/风险）
     4. 生成版本 Issue 描述模板（标题 `[v1.5] 登录表单`，正文含 Step 0–7 checklist）
     5. 打印追踪矩阵（行以 Step 为单位，Issue / PR 为版本唯一的那一个）：
        | Step | Issue | PR | 验收 |
        | S0 Scaffold & Clean | #xx | #xx | ⬜ |
        | S1 Contract & ADR | #xx | #xx | ⬜ |
        | S2 Core & Prototype | #xx | #xx | ⬜ |
        | … | … | … | … |

用户: "S2 完成了"

AI:  委托 dm-dev-step（本 skill 不执行）：
     验收 → commit(Closes #xx) → 关 Issue → 回写 500-schedule
     （工作包状态 + 追踪矩阵 + 执行记录一条）

用户: "关闭版本 v1.5-login"

AI:  委托 dm-close-ver 处理版本收尾（就绪审计 → merge 保留历史 → 关闭 版本 Issue → 清理分支 → 关闭报告）
```
