# dev-meta

开发元规范与工程标准，跨项目共享。当前以 Transaction Flow 作为版本文档主轴。

## 元数据

| 项 | 值 |
|---|---|
| 版本 | `v0.1.0` |
| 状态 | 起草中 |
| 许可证 | 待定 |

## 文件

- `docs/01-project-dev-flow.md` — 项目级开发流程与文档分层骨架
- `docs/02-version-rules.md` — 版本目录文件规范（schedule / spec / design / build）
- `docs/03-git-flow-rules.md` — Git 开发流规范（小版本 PR、TF issue、commit 规范）
- `docs/04-worklog-rules.md` — 工作日志规范（每日工作总结 + 详细日志 + 待办 + 里程碑）
- `docs/05-codebuddy-management.md` — CODEBUDDY.md 管理规范：两层架构（全局层 vs 项目层）、加载机制、迁移说明
- `docs/CODEBUDDY-global.md` — 全局规范原始版本：`~/.codebuddy/CODEBUDDY.md` 的 source of truth，在此修改后部署生效
- `templates/worklog.md` — 工作日志模板：`docs/reports/worklog.md`
- `templates/versions/vX.Y-<slug>/` — 版本文档模板（与规范文件一一对应）
- `templates/project/` — 项目级文档模板（project-spec / design / api-design / schema-design / roadmap）
