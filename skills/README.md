# Dev-Meta Skills

本目录为 `dev-meta` 规范体系对应的 CodeBuddy Skills 设计文档。每个 skill 封装一套标准化开发流程，让 AI 在任何项目中自动遵循 dev-meta 规范。

## Skill 总览

| Skill | 触发场景 | 职责 | 频率 |
|-------|----------|------|------|
| `dm-init` | 初始化新项目 | 创建 docs 目录树、生成 dev-reference.md、初始化项目基线文档与 worklog | 低频 |
| `dm-plan-ver` | 新建版本 / 关闭版本 | 创建版本文档四件套、分支/PR、TF Issue、追踪验收 | 中频 |
| `dm-dev-tf` | 开始开发某个 TF | 读取版本文档、确认 Issue、创建 TF 分支、输出开发概要 | 高频 |
| `dm-log` | 每日记录工作 | 追加工作总结、维护待办与里程碑 | 每日 |
| `dm-commit` | 提交变更 | type 向导、格式校验、footer 关联 Issue，确保 commit 一致性 | 频繁 |

## Skill 关系

```
dm-init
    │
    └── 项目初始化后，后续版本迭代用 dm-plan-ver
            │
            ├── 每个版本开始 → 创建四件套 + 分支 + PR + Issue
            ├── 每个 TF 启动 → dm-dev-tf（读文档、建分支、出概要）
            ├── 每个 TF 完成 → dm-commit + 关 Issue + 更新追踪
            └── 版本收尾 → merge PR + 补齐验收
                                    │
dm-log ← 每日穿插，记录所有工作 ──→ dm-commit (统一提交出口)
```

## 使用说明

### 安装

将本目录下的 skill 复制到 CodeBuddy 的 skills 目录：

```bash
# 用户级（推荐，跨项目可用）
cp -r skills/dm-* ~/.codebuddy/skills/

# 项目级（团队共享）
cp -r skills/dm-* .codebuddy/skills/
```

每个 skill 目录下需包含 `SKILL.md`（核心指令）、`references/`（规范文档）、`assets/`（模板文件），具体文件清单见各 skill 设计文档。

### 触发方式

在 CodeBuddy 对话中，用自然语言描述需求，AI 自动匹配对应 skill：

| 想做什么 | 对话示例 |
|----------|----------|
| 初始化项目 | "初始化一个新项目 `my-app`" |
| 开始新版本 | "新建版本 v1.2-login" |
| 开始开发 TF | "开始 TF3" / "/dm-dev-tf 3 auth" |
| 完成一个 TF | "TF2 完成了，帮我 commit" |
| 关闭版本 | "关闭版本 v1.2，准备 merge" |
| 记录工作 | "记录今天的工作" |
| 提交变更 | "commit" / "帮我 commit" |

### 典型项目生命周期

```
                          dm-init
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
| Git 仓库已初始化 | dm-init / dm-plan-ver | 版本管理依赖 Git |
| `gh` CLI（可选） | dm-plan-ver | 用于自动创建 PR/Issue，未安装则生成文本描述手动粘贴 |
| 项目中已有 `docs/dev-reference.md` | dm-plan-ver / dm-log | 确保项目已绑定 dev-meta 规范 |

## 共享资源

五个 skill 共享 `dev-meta` 仓库中的规范文件与模板，通过 `references/` 和 `assets/` 分发：

| 资源类型 | 文件 | 使用方 |
|----------|------|--------|
| 规范 | `docs/project-dev-flow.md` | dm-init |
| 规范 | `docs/version-rules.md` | dm-plan-ver |
| 规范 | `docs/git-flow-rules.md` | dm-plan-ver |
| 规范 | `docs/worklog-rules.md` | dm-log |
| 模板 | `templates/dev-reference.md` | dm-init |
| 模板 | `templates/project/*` | dm-init |
| 模板 | `templates/versions/vX.Y-<slug>/*` | dm-plan-ver |
| 模板 | `templates/worklog.md` | dm-log |
| 规范 | `docs/git-flow-rules.md` | dm-commit |
