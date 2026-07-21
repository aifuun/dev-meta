# Dev-Meta Skills

本目录为 `dev-meta` 规范体系对应的 CodeBuddy Skills 设计文档。每个 skill 封装一套标准化开发流程，让 AI 在任何项目中自动遵循 dev-meta 规范。

## Skill 总览

| Skill | 触发场景 | 职责 | 频率 |
|-------|----------|------|------|
| `dev-meta-init` | 初始化新项目 | 创建 docs 目录树、生成 dev-rules.md、初始化项目基线文档 | 低频 |
| `dev-meta-version` | 新建版本 / 推进 TF | 创建版本文档四件套、分支/PR、TF Issue、追踪交付 | 高频 |
| `dev-meta-worklog` | 每日记录工作 | 追加工作总结、维护待办与里程碑 | 每日 |

## Skill 关系

```
dev-meta-init
    │
    └── 项目初始化后，后续版本迭代用 dev-meta-version
            │
            ├── 每个版本开始 → 创建四件套 + 分支 + PR + Issue
            ├── 每个 TF 完成 → commit + 关 Issue + 更新追踪
            └── 版本收尾 → merge PR + 补齐验收
                                    │
dev-meta-worklog ← 每日穿插，记录所有工作
```

## 共享资源

三个 skill 共享 `dev-meta` 仓库中的规范文件与模板，通过 `references/` 和 `assets/` 分发：

| 资源类型 | 文件 | 使用方 |
|----------|------|--------|
| 规范 | `docs/project-dev-flow.md` | init |
| 规范 | `docs/version-rules.md` | version |
| 规范 | `docs/git-flow-rules.md` | version |
| 规范 | `docs/worklog-rules.md` | worklog |
| 模板 | `templates/dev-rules.md` | init |
| 模板 | `templates/project/*` | init |
| 模板 | `templates/versions/vX.Y-<slug>/*` | version |
| 模板 | `templates/worklog.md` | worklog |
