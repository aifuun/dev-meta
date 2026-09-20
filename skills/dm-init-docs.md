---
name: dm-init-docs
description: 初始化新项目文档：引导式意图收集，生成 00~06 文档骨架（04 可选）+ ./CODEBUDDY.md 版本绑定。触发于「初始化新项目」「创建项目文档骨架」。
---

# dm-init-docs

## 概述

交互式项目初始文档脚手架生成器：通过引导式问答收集开发者核心意图，从本地全局资产目录 `~/.dev-meta/` 读取静态模板，渲染并输出带**单向依赖纪律声明**的项目文档骨架（00~06，其中 04 可选），同时生成 `./CODEBUDDY.md` 完成 dev-meta 版本绑定。项目启动时一次性使用。

## 职责边界

| 职责 | 归属 |
|------|------|
| 生成项目文档骨架 00~06（04 条件跳过） | ✅ 本 skill |
| 生成 `./CODEBUDDY.md`（版本绑定 + 例外项） | ✅ 本 skill（原 `dm-init` 职责，现由本 skill 承接；是 dm-plan-ver / dm-log 的前置条件） |
| 模板资产的发布与 skill 触发入口部署 | 委托 `dm-pub-skill`（本 skill 只消费模板生成文档，不负责发布） |
| 代码脚手架（目录 / 依赖 / 配置） | ❌ 各语言 CLI 负责 |
| 运行时代码植入（如 `observe` 包装器） | ❌ 由开发阶段 `dm-dev-step` 落地，本 skill 只生成文档 |
| 版本四件套（200-spec / 300-design / 400-build / 500-schedule） | 委托 `dm-plan-ver` |
| 提交 | 委托 `dm-commit` |

## 触发

- "初始化新项目"
- "按 dev-meta 规范搭建项目文档"
- "创建项目文档骨架"
- "生成 00~06 文档"

## 核心概念

### 00~06 编号体系与单向依赖

| 编号 | 文档 | 核心职责 | 依赖方向 |
|------|------|----------|----------|
| **00** | `00_PRODUCT_REQUIREMENTS.md` | 业务背景、用户痛点、User Story、业务验收标准 | **业务根**，只被下游引用 |
| **01** | `01_TECHNICAL_SPEC.md` | 技术选型、边界约束、测试策略、部署基线 | ← 00 |
| **02** | `02_SYSTEM_DESIGN.md` | 架构图、组件分层、数据流、并发/状态机 | ← 00, 01 |
| **03** | `03_CONTRACTS_AND_API.md` | **契约 SSOT**：Invariants、API、存储 Schema、错误码 | ← 01, 02 |
| **04** | `04_UI_UX_DESIGN.md`（可选） | 交互流程、视图五态、组件规范 | ← 00, 03；**纯后端/CLI 跳过** |
| **05** | `05_ROADMAP_AND_COMPLIANCE.md` | Milestone、版本切分（Epoch）、合规/安全/隐私 | ← 00~04, 06 |
| **06** | `06_OBSERVABILITY.md` | dev-meta 07 的项目实例化 | ← 02, 03 |

- **单向依赖纪律**：每篇文档头部声明流向，**只被下游引用，不反向引用下游**。改上游不动下游，避免「改一次计划就要动契约」。
- **契约位置**：契约（03）在架构（02）之后，方向为自上而下 `00 → 01 → 02 → 03 → 04/05`。
- **不重定义规范**：涉及契约 / 可观测性 / 执行粒度时，模板只**引用** `dev-meta/docs/06`、`07`、`08`，不复制其定义（单一权威）。

### 两层 CODEBUDDY 架构

| 层 | 文件 | 内容 |
|----|------|------|
| 全局层 | `~/.codebuddy/CODEBUDDY.md` | 通用 DoD、AI 协作约定、编码约定、工作日志指引。**每次会话自动加载**，跨项目共享 |
| 项目层 | `./CODEBUDDY.md` | 仅两块：**规范来源表**（来源仓库 + 采用版本）+ **本项目例外**。不复制规范正文，**也不重复仓库地址**（由全局层统一提供） |

- 项目层只回答两个问题：「用哪套 dev-meta、哪个版本」「哪些地方不按通用规范走」。
- **生成 `./CODEBUDDY.md` 是本 skill 的必选步骤**：`skills/README.md` 前置条件表将「项目中已有 `./CODEBUDDY.md`」列为 `dm-plan-ver` / `dm-log` 的前置条件，缺失会导致后续 skill 前置断裂。

### 资产布局

| 目录 | 角色 | 内容 |
|------|------|------|
| `~/.dev-meta/templates/` | **模板**（骨架） | `project/docs/0X_*.md` 全套模板 + `CODEBUDDY.md` |
| `~/.dev-meta/docs/` | **规范文档**（权威副本） | 01~09，供跨项目引用 |
| `~/.dev-meta/skills/` | **skill 中文源** | `dm-*.md`（唯一权威） |
| `~/.codebuddy/skills/dm-init-docs/SKILL.md` | **部署版** | 由本中文源自动生成（`pub_local.py --deploy`），内容即本文全文，**禁止手改** |

### 目标路径三级优先级

1. **显式配置**：目标项目根目录 `.dev-metarc` 的 `docsTargetDir` 字段（可选，不强制创建）
2. **交互指定**：开发者在问答中明确输入的路径
3. **默认保底**：`<project-root>/docs/`（不存在则自动创建）

### 占位符约定

| 形式 | 用途 | 示例 |
|------|------|------|
| `{{FIELD}}` | 结构化命名字段，渲染时用收集到的意图替换 | `{{PROJECT_NAME}}`、`{{API_PATH}}` |
| `<!-- TODO: [dm-init-docs] <说明> -->` | 待补充内容，保留可检索标记 | `<!-- TODO: [dm-init-docs] 响应时间需求 -->` |

## 执行流程

### 1. 意图收集（Prompt Stage）

向开发者抛出结构化提问（支持一次性输入或多轮交互）：

- **项目名称与核心目标**：解决什么问题？核心 User Story 是什么？
- **技术栈与运维约束**：语言/框架？存储选型？如何部署与测试？
- **核心数据实体与 API**：关键接口与绝对不能违反的业务不变量（Invariants）？
- **是否存在前端/客户端 UI**：如无 UI（纯 CLI / Lib / 后端），**跳过 04 号文档**。
- **目标生成路径确认**：默认 `<project-root>/docs/`，是否调整？
- **dev-meta 版本**：采用的 dev-meta tag / commit（用于写入 `./CODEBUDDY.md` 版本绑定）。

### 2. 解析目标路径

按「三级优先级」确定落地目录（见核心概念）。

### 3. 生成 `./CODEBUDDY.md`（版本绑定，必选）

基于模板在项目根目录创建 `./CODEBUDDY.md`，填写来源仓库（`dev-meta`）与采用版本，并留「本项目例外」待填。**不填仓库地址**——它由 `~/.codebuddy/CODEBUDDY.md` 全局提供，项目层再写一份只会漂移。作用：项目与 dev-meta 的版本绑定 + 例外项记录；通用规范由 `~/.codebuddy/CODEBUDDY.md` 全局加载，不重复。

### 4. 读取模板并渲染

1. **确认资产已发布**：检查 `~/.dev-meta/templates/project/docs/` 下是否已有 7 个模板（00~06）。
   - 已存在 → 继续。
   - **不存在 → 暂停并提示**：本 skill 只消费模板、不负责发布（见职责边界）。请先在 dev-meta 仓库执行 `python3 pub_local.py --deploy` 发布资产，然后再回来继续。禁止凭记忆编造模板内容。
2. 依次读取 `~/.dev-meta/templates/project/docs/` 下的 00~06 模板（04 按条件跳过）。
3. 将收集到的意图填入 `{{FIELD}}` 占位符；未知或待定细节统一填入 `<!-- TODO: [dm-init-docs] 说明 -->`。
4. 保留每篇头部的**单向依赖纪律声明**与占位符约定说明。

### 5. 文件落地

在目标目录下写入生成的文档（`mkdir -p` 保证目录存在）。

### 6. 输出校验报告

列出：已生成文档清单、已填充章节、遗留 TODO 事项（含文件与行定位）、跳过的文档及原因（如无 UI 跳过 04）。

### 7. 提交

提交所有创建的文件 — 委托 `dm-commit`。示例：

```
chore: initialize project docs following dev-meta
```

## 关键规则速查（单一权威）

| 规则 | 来源 |
|------|------|
| 文档编号 00~06；04 可选，纯后端/CLI 跳过 | 本文核心概念 |
| 每篇头部须保留单向依赖纪律声明，只被下游引用、不反向引用 | 本文核心概念 |
| 契约（03）依赖 upstream 01、02，作为下游实现与测试的只读 SSOT | 本文核心概念 |
| 模板只引用 `dev-meta/docs/06`、`07`、`08`，不重定义 | skill-doc-principles §2 |
| 必须生成 `./CODEBUDDY.md`（版本绑定 + 例外项），是 dm-plan-ver / dm-log 前置条件 | skills/README.md 前置条件表 |
| 项目层 CODEBUDDY.md 不复制规范正文，只写来源与例外 | docs/05-codebuddy-management.md |
| 资产在 `~/.dev-meta/`（模板 / 规范 / skill 源分开存放）；触发入口为 `~/.codebuddy/skills/dm-init-docs/SKILL.md` | 本文核心概念 |
| 目标路径三级优先级：.dev-metarc → 交互指定 → `<project-root>/docs/` | 本文核心概念 |
| 占位符：`{{FIELD}}` 结构化字段，`<!-- TODO: [dm-init-docs] -->` 待补 | 本文核心概念 |
| 本 skill 不生成代码、不植入运行时代码（observe 包装器由开发阶段落地） | 职责边界 |
| 资产未发布（`~/.dev-meta/` 缺模板）时须暂停并提示先跑 `pub_local.py --deploy`，禁止编造模板 | 执行流程·步骤 4 |
| 提交委托 dm-commit | dm-commit |

## 产出与完成判据

**产出**：

- 项目文档骨架 `docs/00~06`（04 可选）
- `./CODEBUDDY.md`（版本绑定 + 例外项）
- 校验报告：已生成文档 + 遗留 TODO 清单 + 跳过说明

**完成判据**：

- [ ] 目标路径已按三级优先级解析并创建
- [ ] 00~06 已生成；无 UI 时已**跳过 04** 并在报告中说明
- [ ] 每篇头部保留**单向依赖纪律声明**与占位符约定
- [ ] `./CODEBUDDY.md` 已生成（来源仓库 + 版本 + 例外项）
- [ ] 未知项已统一标记为 `<!-- TODO: [dm-init-docs] <说明> -->`
- [ ] 校验报告已输出（含各文档 TODO 数量）

## 资源映射

| 资源 | 来源 | 用途 |
|------|------|------|
| `~/.codebuddy/skills/dm-init-docs/SKILL.md` | — | 部署版（由中文源自动生成） |
| `~/.dev-meta/templates/project/docs/00_PRODUCT_REQUIREMENTS.md` | `templates/project/docs/` | PRD 模板 |
| `~/.dev-meta/templates/project/docs/01_TECHNICAL_SPEC.md` | 同上 | 技术规格模板 |
| `~/.dev-meta/templates/project/docs/02_SYSTEM_DESIGN.md` | 同上 | 系统设计模板 |
| `~/.dev-meta/templates/project/docs/03_CONTRACTS_AND_API.md` | 同上 | 契约 SSOT 模板 |
| `~/.dev-meta/templates/project/docs/04_UI_UX_DESIGN.md` | 同上 | UI/UX 模板（可选） |
| `~/.dev-meta/templates/project/docs/05_ROADMAP_AND_COMPLIANCE.md` | 同上 | 路线图与合规模板 |
| `~/.dev-meta/templates/project/docs/06_OBSERVABILITY.md` | 同上 | 可观测性实例化模板 |
| `~/.dev-meta/templates/CODEBUDDY.md` | `templates/CODEBUDDY.md` | 项目层 CODEBUDDY 模板（版本绑定 + 例外项） |
| `pub_local.py` | `dev-meta/pub_local.py` | 发布模板与 skill 至 `~/.dev-meta/` |
| `docs/06-contract-based-dev.md` | docs/ | 契约规范（只引用） |
| `docs/07-observability-driven-dev.md` | docs/ | ODD 规范（只引用） |
| `docs/05-codebuddy-management.md` | docs/ | 两层 CODEBUDDY 架构（只引用） |

## 使用示例

```
用户: "初始化一个新项目 shadow-player-v3"

AI:  1. 意图收集（提问）：
        - 项目名称与核心目标？核心 User Story？
        - 技术栈 / 存储 / 部署与测试方式？
        - 核心实体与 API？绝对不能违反的业务不变量？
        - 是否有前端/客户端 UI？
        - 生成路径（默认 <root>/docs/）？dev-meta 采用版本？
     2. 解析目标路径：无 .dev-metarc → 用户未指定 → 用 <root>/docs/
     3. 生成 ./CODEBUDDY.md（来源仓库 + 采用版本 + 例外项占位）
     4. 读取 ~/.dev-meta/templates/project/docs/ 模板并渲染
        → 00/01/02/03/05/06（用户答"有 UI"故含 04）
     5. 写入 <root>/docs/
     6. 输出校验报告：
        ✅ 已生成 7 篇（00~06）
        ⏭️ 无跳过
        📝 遗留 TODO 23 处（00:4 / 01:5 / 02:4 / 03:6 / 04:2 / 05:1 / 06:1）
     7. 提示可委托 dm-commit 提交
```

```
用户: "给纯后端 CLI 工具初始化文档，生成到 docs/specs"

AI:  1. 意图收集（同上）
     2. 解析目标路径：用户显式指定 → docs/specs
     3. 生成 ./CODEBUDDY.md
     4. 渲染 00/01/02/03/05/06 → **跳过 04_UI_UX_DESIGN（无 UI）**
     5. 写入 docs/specs/
     6. 校验报告：⏭️ 已跳过 04（原因：纯后端 CLI，无前端界面）
```
