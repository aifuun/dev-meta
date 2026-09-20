# Project Dev Flow

## 1. 目标与适用范围

- 目标：定义项目级开发流程与长期文档基线，指导每个小版本的迭代交付。
- 适用范围：项目全生命周期（规划、设计、开发、验收、复盘）。

## 2. 两层文档体系

### 2.1 项目级文档（长期稳定，低频更新）

- `00_PRODUCT_REQUIREMENTS.md`：业务背景、用户痛点、User Story、业务验收标准（**业务根**，只被下游引用）。
- `01_TECHNICAL_SPEC.md`：技术选型、边界约束、测试策略、部署基线。
- `02_SYSTEM_DESIGN.md`：系统架构、组件分层、数据流、并发/状态机模型。
- `03_CONTRACTS_AND_API.md`：**契约 SSOT**：不可变式、API 契约、存储 Schema、错误码。
- `04_UI_UX_DESIGN.md`（可选）：交互流程、视图五态、组件规范（纯后端/CLI 跳过）。
- `05_ROADMAP_AND_COMPLIANCE.md`：Milestone、版本切分（Epoch）、合规/安全/隐私。
- `06_OBSERVABILITY.md`：`docs/07-observability-driven-dev.md` 规范的项目实例化。

> **依赖方向**：`00 → 01 → 02 → 03 → 04/05`，`02/03 → 06`。每篇头部声明流向，只被下游引用、不反向引用下游。由 `dm-init-docs` 生成。

### 2.2 版本级文档（高频更新，按版本推进）

- `200-spec.md` — 交付与验收
- `300-design.md` — 流串接与分工
- `400-build.md` — 实现细节与执行计划
- `500-schedule.md` — 工作包排程与执行顺序

版本级文档只描述"本版本增量"，不重复项目级稳定内容。

## 3. 项目级开发主流程

### 文档创建顺序

| 顺序 | 文档 | 何时创建 | 前置依赖 |
|------|------|----------|----------|
| 1 | `00_PRODUCT_REQUIREMENTS.md` | 项目初始化 | — |
| 2 | `01_TECHNICAL_SPEC.md` | 技术基线建立 | 00 |
| 3 | `02_SYSTEM_DESIGN.md` | 架构基线建立 | 00, 01 |
| 4 | `03_CONTRACTS_AND_API.md` | 契约基线建立 | 01, 02 |
| 5 | `06_OBSERVABILITY.md` | 可观测性实例化 | 02, 03 |
| 6 | `05_ROADMAP_AND_COMPLIANCE.md` | 版本路线规划 | 以上全部 |
| * | `04_UI_UX_DESIGN.md` | 按需（有 UI 时） | 00, 03 |

### 3.1 项目初始化

输入：业务目标、约束、团队能力、时间边界。
输出：`00_PRODUCT_REQUIREMENTS.md` 初稿。

检查点：

- 目标可验证。
- 边界与非目标清晰。
- 成功指标可量化。

### 3.2 架构基线建立

输入：`00_PRODUCT_REQUIREMENTS.md`。
输出：`01_TECHNICAL_SPEC.md`、`02_SYSTEM_DESIGN.md`。

检查点：

- 模块边界清晰。
- 关键依赖可解释。
- 主要风险有缓解方向。

### 3.3 契约与数据基线建立

输入：架构基线（`01_TECHNICAL_SPEC.md` / `02_SYSTEM_DESIGN.md`）。
输出：`03_CONTRACTS_AND_API.md`、`06_OBSERVABILITY.md`。

检查点：

- API 输入输出、错误码、兼容策略明确。
- Schema 主键、索引、迁移策略明确。
- 不可变式（Invariants）标注四要素（归属 / 方向 / 不变性 / 真值来源），见 `docs/06-contract-based-dev.md` §4。

### 3.4 版本路线规划

输入：项目级基线文档。
输出：`05_ROADMAP_AND_COMPLIANCE.md`。

检查点：

- **版本粒度合规**：一个版本只承载单一核心业务场景（判据见 `docs/02-version-rules.md` §3.2）。
- **Epoch 划分明确**：若干版本组成一个 Epoch，共同交付一个完整 feature；编号遵 `v` / `r` 双轴与号段留白规则（见 `docs/02` §3.3）。
- 版本间依赖顺序合理。
- 里程碑与风险节点明确。

> 规划动作由 `dm-plan-roadmap` 执行；本文只定义检查点，不重定义规则。

### 3.5 小版本执行（复用版本流程）

每个版本遵循以下步骤：

1. 开始一个小版本（目标与范围）
2. 建文档（spec/design/build）
3. 建跟踪项（1 个版本 PR + 1 个版本 Issue；Step 0–7 作为该 Issue 内的 checklist）
4. 开发（**按 docs/08-small-batch-iteration.md 三 Batch 推进，对 AI 执行粒度须缩到单文件重构 / 单函数修复**）：
   - **Batch 1** 契约接口与数据模型 → 编译 / Schema 校验通过
   - **Batch 2** Core 逻辑单文件 → 单元测试通过（核心算法层采用 docs/08 §2.2 Agentic TDD 轻量范式：仅核心逻辑、独立进程跑、Assert 受 docs/07 §2.5 约束；UI/视图不写 TDD）
   - **Batch 3** 接入 UI / 调用点 → 集成校验通过
   - 每完成一个绿灯 Batch 由用户触发 commit（均 `Refs #同一 Issue`，见 docs/03 §2.3）；下个 Batch 混乱时由用户 `git reset --hard` 退回（AI 不自发，见 docs/08 §2.1）
5. 测试与验证（Batch 2 逻辑断言走 Agentic TDD 挂入门禁；Batch 3 集成校验走人工 Preview + 静态检查；记录结果）
6. 验收与收尾（验收记录、关闭 issue、合并 PR）
7. 复盘与归档（变更总结、遗留项）

### 3.6 项目级回收与迭代

输入：各版本复盘结果。
输出：项目级文档增量更新。

检查点：

- 将稳定结论上收至项目级文档。
- 将短期策略保留在版本级文档。
- roadmap 按真实节奏校准。

## 4. 文档边界规则（防重复）

- 项目级文档回答"长期怎么设计"。
- 版本级文档回答"这次具体交付什么、怎么验收"。
- API/Schema 稳定部分写在项目级，版本仅写变更点。
- 同一条规则只保留一个权威来源。

### 4.1 跨项目规范引用策略

- `02-version-rules.md`、`03-git-flow-rules.md` 与 `04-worklog-rules.md` 以 `dev-meta` 项目中的对应文件为统一权威来源。
- 业务项目默认不复制规范正文，通过项目级 `./CODEBUDDY.md` 记录 dev-meta 版本绑定与项目例外项。通用规范（DoD、AI 协作、编码约定、工作日志指引）由 `~/.codebuddy/CODEBUDDY.md` 全局加载。
- 推荐通过 `dm-init-docs` skill 自动生成；若手动创建，模板见 `docs/05-codebuddy-management.md` 与 `templates/CODEBUDDY.md`。
- 项目级 `CODEBUDDY.md` 填写两项必填内容：
    - 规范来源仓库与版本（tag 或 commit）
    - 本项目例外项（如无则写"无"）
- 仅在以下场景复制规范正文到项目内：
    - 离线环境或合规审计要求仓库自包含
    - 团队明确要求项目仓库独立维护完整规范
- 若复制规范正文，必须在文档头部标注来源版本，并建立定期同步机制。

### 4.2 templates 跨项目使用策略

- `templates/versions/` 与 `templates/project/docs/` 以 `dev-meta` 为默认模板源。
- 新项目默认采用"引用优先"策略：
    - 在项目内声明模板来源与版本（tag 或 commit）
    - 按版本从模板创建 `spec/design/build`
- 以下场景建议复制模板到项目内：
    - 项目需要长期离线开发或受审计约束
    - 项目对模板字段有稳定扩展，且扩展不适合回写到公共模板
- 若复制模板，建议在项目中保留 `templates-source.md`，至少记录：
    - 来源仓库与路径
    - 来源版本（tag/commit）
    - 本地扩展项与差异说明
- 模板同步建议：
    - 每个小版本开始前检查一次模板差异
    - 只同步"结构变更"和"字段边界变更"，避免无效格式漂移

## 5. 最小治理规则

版本级治理的权威来源为 `03-git-flow-rules.md`。项目级硬性底线：

- 版本结束：必须有验收记录与复盘结论。

## 6. 模板目录建议

```text
project-root/
├── CODEBUDDY.md                      # dev-meta 版本绑定 + 项目例外（两层架构的项目层）
├── docs/
│   ├── 00_PRODUCT_REQUIREMENTS.md
│   ├── 01_TECHNICAL_SPEC.md
│   ├── 02_SYSTEM_DESIGN.md
│   ├── 03_CONTRACTS_AND_API.md
│   ├── 04_UI_UX_DESIGN.md            # 可选（无 UI 跳过）
│   ├── 05_ROADMAP_AND_COMPLIANCE.md
│   ├── 06_OBSERVABILITY.md
│   ├── versions/
│   │   └── vX.Y-<slug>/
│   │       ├── 200-spec.md
│   │       ├── 300-design.md
│   │       ├── 400-build.md
│   │       └── 500-schedule.md
│   ├── reports/
│   │   └── worklog.md
│   └── adrs/
│       └── adr-001.md
└── templates/                        # 可选：项目自维护模板副本（引用优先，见 §4.2）
    ├── CODEBUDDY.md
    ├── project/
    │   └── docs/
    │       ├── 00_PRODUCT_REQUIREMENTS.md
    │       └── ...（01~06）
    ├── versions/
    │   └── vX.Y-<slug>/
    │       ├── 200-spec.md
    │       ├── 300-design.md
    │       ├── 400-build.md
    │       └── 500-schedule.md
    └── worklog.md
```

## 7. 使用建议（单人开发）

- 保持项目级文档简洁，优先更新 roadmap 与边界变化。
- 小版本文档优先完整，项目级文档按稳定结论回填。
- 每周至少一次"版本状态 -> roadmap"同步。
