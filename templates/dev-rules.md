# 开发规则入口

<!--
  本文件是 dev-meta 规范在本项目的唯一锚点。
  规范正文不复制到项目内，统一从 dev-meta 仓库引用。
-->

## 1. 规范来源

| 项 | 值 |
|---|---|
| 来源仓库 | `dev-meta` |
| 仓库地址 | <!-- 填写 dev-meta 仓库的 git 地址或本地路径 --> |
| 采用版本 | <!-- 填写 tag 或 commit hash，如 v1.0.0 / a1b2c3d --> |

## 2. 核心参考文件

| 规范 | 路径 | 说明 |
|---|---|---|
| 项目开发流程 | `docs/project-dev-flow.md` | 两层文档体系、小版本执行步骤、文档边界规则 |
| 版本文档规范 | `docs/version-rules.md` | spec / general-design / detailed-design / tasks 结构与职责 |
| Git 工作流规范 | `docs/git-flow-rules.md` | 分支命名、commit 规范、PR/Issue 关联规则 |

## 3. 模板目录

按版本从以下模板创建文档，不复制模板正文到项目内（需要离线或审计要求时除外）。

| 模板 | 路径 | 用途 |
|---|---|---|
| 版本四件套 | `templates/versions/vX.Y-<slug>/` | 每个小版本从模板创建 spec / general-design / detailed-design / tasks |
| 项目基线 | `templates/project/` | 项目初始化时按需创建 project-spec / general-design / api-design / schema-design / roadmap |

## 4. 本项目例外

<!-- 如无例外项，写"无"；如有，逐条列出差异及理由 -->

- 无
