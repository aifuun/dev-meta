# dev-meta

开发元规范与工程标准，跨项目共享。当前以 Transaction Flow 作为版本文档主轴。

## 元数据

| 项 | 值 |
|---|---|
| 版本 | `v0.1.0` |
| 状态 | 起草中 |
| 许可证 | 待定 |

## 文件

- `docs/project-dev-flow.md` — 项目级开发流程与文档分层骨架
- `docs/version-rules.md` — 版本目录文件规范（spec / general-design / detailed-design / tasks）
- `docs/git-flow-rules.md` — Git 开发流规范（小版本 PR、TF issue、commit 规范）
- `templates/dev-rules.md` — 项目入口模板：新项目在根目录放置 `docs/dev-rules.md`，指向本仓库并声明采用的规范版本
- `templates/versions/vX.Y-<slug>/` — 版本文档模板（与规范文件一一对应）
- `templates/project/` — 项目级文档模板（project-spec / general-design / api-design / schema-design / roadmap）
