# Dev-Meta Skills

本目录为 `dev-meta` 规范体系对应的 CodeBuddy Skills 设计文档。每个 skill 封装一套标准化开发流程，让 AI 在任何项目中自动遵循 dev-meta 规范。

> **所有 skill 设计文档须遵循 [skill-doc-principles.md](skill-doc-principles.md) 的核心原则**（概念驱动结构、单一权威、职责边界、自动部署、面向 AI 可遍历）。新增或重构 skill 文档时先阅读该文档。

## Skill 总览

| Skill | 触发场景 | 职责 | 频率 |
|-------|----------|------|------|
| `dm-init-docs` | 初始化新项目文档 | 引导式意图收集，生成 00~06 文档骨架（04 可选）+ `./CODEBUDDY.md`（版本绑定+例外） | 低频 |
| `dm-plan-roadmap` | 规划路线图 / 切版本 | 划分 Milestone 与 Epoch（版本组）、执行**版本粒度红线**校验（预估 + 实证回环）、分配 `v`/`r` 双轴编号与号段留白 | 低频 |
| `dm-plan-ver` | 新建版本 | 创建版本文档四件套（200-spec/300-design 产出前执行需求级/架构级 grill 收敛决策）、分支/PR、版本 Issue、粒度实证 | 中频 |
| `dm-close-ver` | 关闭版本 | 就绪审计、保留历史 merge、关闭 版本 Issue、清理分支、关闭报告 | 中频 |
| `dm-schedule` | 版本排程 | 生成按优先级排序的扁平工作包列表，附带防沉迷红线 | 中频 |
| `dm-dev-step` | Step 全生命周期 | 启动（读文档、确认/创建版本 Issue、出开发概要）→ 提交（委托 dm-commit）→ 收尾（验收、关 Issue、回写 500-schedule） | 高频 |
| `dm-log` | 每日记录工作 | 追加工作总结、维护待办与里程碑 | 每日 |
| `dm-commit` | 提交变更 | type 向导、格式校验、footer 关联 Issue，确保 commit 一致性 | 频繁 |
| `dm-report` | 生成阶段报告 | 从 worklog 提取数据，按模板输出周报/月报/自定义周期报告 | 每周 |
| `dm-adr` | 记录技术决策 | 按 ADR 格式维护架构/技术选型决策日志 | 按需 |
| `dm-arch-design` | 创建 / 调整产品架构 | 人的架构设计规范 + AI 执行边界（单向分层、Facade 极简暴露、事件总线），落地 06/07/08 三支柱 | 按需 |
| `dm-contract-gate` | 改代码前 / 改完 / 交付前 | 契约断言门禁：改前 diff 契约、改后跑门禁（sha256 + contract_verified）、交付对齐 MANIFEST | 高频 |
| `dm-grillme-plan` | 通用需求 Plan 前逼问决策 | 非版本类需求写代码/出方案前的「提问→回答→沉淀」决策收敛，输出 Final Plan（版本类走 dm-plan-ver/dm-dev-step 内嵌 grill） | 按需 |
| `dm-cleanup` | 技术债清理 + 仓库卫生 | 版本/Step 之外的跨文件清理（正确性/注释/死代码/重复结构/占位常量标注）与仓库卫生（.gitignore + 误提交文件 `git rm --cached`），验证后委托 dm-close-ver | 按需 |
| `dm-pub-skill` | 发布 / 部署 skill 与模板 | 发布资产到 `~/.dev-meta/`、部署 skill 触发入口到 `~/.codebuddy/skills/`，含前置检查与同步后校验（编排 `pub_local.py`） | 按需 |

## Skill 关系

```
dm-init-docs
    │
    └── 项目初始化后，后续版本迭代用 dm-plan-ver
            │
            ├── 版本规划完成后 → dm-schedule（排程：工作包列表 + 红线）
            ├── 每个版本开始 → 创建四件套 + 分支 + PR + Issue
            │                            （200-spec/300-design 产出前执行需求级/架构级 grill，问答沉淀进文档）
            ├── 每个 Step 启动 → dm-dev-step（读文档、确认 Issue、出概要；开发在版本分支上）
            │                            （300-design 不完整时，出概要前执行实现级 grill）
            ├── 每个 Step 完成 → dm-commit + 关 Issue + 更新追踪
            └── 版本收尾 → dm-close-ver（就绪审计 + merge 保留历史 + 关 Issue + 清理分支）
                                    │
dm-log ← 每日穿插，记录所有工作 ──→ dm-commit (统一提交出口)
                                    │
                               dm-report ← 阶段性汇总，生成周报

dm-adr ← 按需穿插，记录技术决策 ──→ dm-commit (统一提交出口)
```

## 使用说明

### 安装与部署

dev-meta 的产物分布在两个根目录，**缺一不可**：

| 目录 | 角色 | 内容 |
|------|------|------|
| `~/.dev-meta/docs/` | **规范文档**（权威副本） | 01~09 + CODEBUDDY-global，**跨项目可读** |
| `~/.dev-meta/templates/` | **模板**（骨架） | `CODEBUDDY.md` + `project/docs/00~06_*.md` |
| `~/.dev-meta/skills/` | **skill 中文源** | `dm-*.md`（唯一权威） |
| `~/.dev-meta/README.md` | **资产总索引**（自动生成） | 全部资产及用途（AI 单一入口） |
| `~/.codebuddy/skills/<name>/` | **触发入口**（CodeBuddy 只从这里加载） | `SKILL.md`（**由中文源自动生成**，含 frontmatter）+ `assets/` + `references/` |

用仓库根目录的 `pub_local.py` 一键发布与部署（详见 `dm-pub-skill`）：

```bash
python3 pub_local.py                    # 仅发布资产到 ~/.dev-meta/
python3 pub_local.py --deploy           # 同时部署触发入口到 ~/.codebuddy/skills/
python3 pub_local.py --deploy --dry-run # 预演，不写入
```

> **单一权威（Single Source of Truth）**：`skills/<name>.md` 是唯一权威——中文源，含 YAML frontmatter（`name` + `description`）；`skills/<name>/` 目录只存放 `assets/` 与 `references/`。部署版 `SKILL.md` 由 `pub_local.py --deploy` **自动生成**，仓库内不保存、禁止手改，从结构上消除双端漂移（详见 `skill-doc-principles.md` §5）。
>
> ⚠️ 早期文档中的 `cp -r skills/dm-* ~/.codebuddy/skills/` 已废弃——它会把中文 `.md` 复制成文件而非目录，且缺少 frontmatter，不会被 CodeBuddy 识别为 skill。

### 触发方式

在 CodeBuddy 对话中，用自然语言描述需求，AI 自动匹配对应 skill：

| 想做什么 | 对话示例 |
|----------|----------|
| 初始化项目 | "初始化一个新项目 `my-app`" |
| 开始新版本 | "新建版本 v1.2-login" |
| 生成排程 | "排程" / "为 v1.0 排程" |
| 开始开发 Step | "开始 S2" / "/dm-dev-step S2" |
| 完成一个 Step | "S2 完成了，帮我 commit" |
| 关闭版本 | "关闭版本 v1.2，准备 merge" |
| 记录工作 | "记录今天的工作" |
| 提交变更 | "commit" / "帮我 commit" |
| 生成报告 | "生成周报" / "本周报告" |
| 记录决策 | "记录一个技术决策" / "创建 ADR" |
| 设计 / 调整架构 | "设计架构" / "规划模块边界" / "生成 AI 防腐规则" |
| 跑契约门禁 | "跑契约门禁" / "校验契约" / "contract gate" |
| 规划前逼问 | "/grill-me" / "规划前先拷问我" / "先 pressure-test 这个方案" |
| 技术债清理 / 仓库卫生 | "/dm-cleanup" / "清理技术债" / "做一下仓库卫生" |
| 发布 / 部署 skill 与模板 | "发布 skill" / "部署模板" / "同步资产" |

> **grill（决策收敛）双轨制**（原则见 skill-doc-principles §7）：
> - **版本类需求**：grill 内嵌于 `dm-plan-ver` / `dm-dev-step`，无需显式触发——AI 在产出 200-spec、300-design、开发概要前自动执行（需求级/架构级/实现级），问答沉淀进文档，技术选型类触发 `dm-adr`。
> - **非版本类通用需求**：走独立 skill `dm-grillme-plan`（触发词 `/grill-me` 等），在写代码/出方案前显式逼问决策并沉淀 Final Plan 到 `docs/plans/<topic>-grill.md`。两轨不重复 grill 逻辑。

### 典型项目生命周期

```
                          dm-init-docs
                             │
                    项目骨架搭建完成
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         dm-plan-ver     dm-plan-ver     dm-plan-ver
         v1.0-core       v1.1-fix       v1.2-feature
              │              │              │
         dm-log  ←─── 每日穿插记录 ───→  dm-log
              │              │              │
         版本收尾        版本收尾        版本收尾
              └──────────────┼──────────────┘
                             │
                        dm-commit (统一提交出口)
```

### 前置条件

| 条件 | 适用 skill | 说明 |
|------|------------|------|
| Git 仓库已初始化 | dm-init-docs / dm-plan-ver | 版本管理依赖 Git |
| `gh` CLI（可选） | dm-plan-ver / dm-close-ver | dm-plan-ver 创建 PR/Issue；dm-close-ver 合并 PR / 关闭 Issue，未安装则手动执行 |
| 项目中已有 `./CODEBUDDY.md` | dm-plan-ver / dm-log | 确保项目已绑定 dev-meta 规范 |

## 共享资源

当前已定义的 skill 共享 `dev-meta` 仓库中的规范文件与模板，通过 `references/` 和 `assets/` 分发：

| 资源类型 | 文件 | 使用方 |
|----------|------|--------|
| 规范 | `docs/01-project-dev-flow.md` | dm-init-docs |
| 规范 | `docs/02-version-rules.md` | dm-plan-ver, dm-close-ver |
| 规范 | `docs/03-git-flow-rules.md` | dm-plan-ver, dm-commit, dm-close-ver |
| 规范 | `docs/04-worklog-rules.md` | dm-log, dm-report |
| 规范 | `docs/06-contract-based-dev.md` | dm-contract-gate, dm-plan-ver, dm-dev-step, dm-cleanup, dm-grillme-plan, dm-arch-design |
| 规范 | `docs/07-observability-driven-dev.md` | dm-cleanup, dm-grillme-plan, dm-arch-design, dm-dev-step, dm-plan-ver |
| 规范 | `docs/08-small-batch-iteration.md` | dm-dev-step, dm-commit, dm-plan-ver |
| 规范 | `docs/09-ai-architecture-guide.md` | dm-arch-design（规范源；skill 为其执行入口） |
| 模板 | `templates/CODEBUDDY.md` | dm-init-docs（项目层：版本绑定+例外项；通用规范见 `~/.codebuddy/CODEBUDDY.md`） |
| 模板 | `templates/project/docs/*` | dm-init-docs（00~06 项目文档骨架，发布至 `~/.dev-meta/`） |
| 模板 | `templates/versions/vX.Y-<slug>/*` | dm-plan-ver |
| 模板 | `templates/versions/vX.Y-<slug>/500-schedule.md` | dm-schedule（排程**单一权威**；`assets/500-schedule-template.md` 为其副本，由 `check_copies` 校验） |
| 模板 | `templates/worklog.md` | dm-log |
