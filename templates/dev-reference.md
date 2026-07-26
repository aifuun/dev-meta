# 开发参考入口

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
| 版本文档规范 | `docs/version-rules.md` | spec / design / build 结构与职责 |
| Git 工作流规范 | `docs/git-flow-rules.md` | 分支命名、commit 规范、PR/Issue 关联规则 |
| 工作日志规范 | `docs/worklog-rules.md` | 每日工作总结 + 详细日志 + 待办 + 里程碑结构与记录规则 |

## 3. 模板目录

版本级和项目级模板**不复制正文**到项目内，按需从模板创建并填写（离线/审计要求时除外）。工作日志模板例外，需复制到项目内。

| 模板 | 路径 | 用途 |
|---|---|---|
| 版本三件套 | `templates/versions/vX.Y-<slug>/` | 每个小版本从模板创建 spec / design / build |
| 项目基线 | `templates/project/` | 项目初始化时按需创建 project-spec / design / api-design / schema-design / ui-design / deployment / roadmap |
| 工作日志 | `templates/worklog.md` | **复制**到 `reports/worklog.md`，每天更新 |

## 4. 工作日志使用指引

1. 项目初始化时，将 `templates/worklog.md` 复制到 `reports/worklog.md`
2. 修改文件头部的项目名，开始记录
3. **每天结束时更新**：在「每日工作总结」表顶部加一行，在下方新增日期章节
4. 当日有 commit 则列出；无 commit 则在「其他工作」中记录讨论、决策、操作
5. 待办与里程碑随进度同步维护

## 5. 通用 DoD (Definition of Done)

每个 PR / commit / TF 交付前应满足：

- [ ] 本地构建通过 / 可运行
- [ ] 手动冒烟验证（核心路径不走查）
- [ ] commit 遵循 dm-commit 规范
- [ ] 涉及文档已同步更新
- [ ] worklog 已记录

## 6. 编码约定

- 禁止魔术数字（用命名常量）
- 单文件 ≤ 300 行
- 公共函数有注释说明意图

## 7. 本项目例外

<!-- 如无例外项，写"无"；如有，逐条列出差异及理由 -->

- 无
