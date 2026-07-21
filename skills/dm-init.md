# dm-init

## 概述

项目初始化 skill，按 `project-dev-flow.md` 规范为新项目搭建文档骨架。一次性使用，项目启动时执行。

## 触发

- "初始化新项目"
- "按 dev-meta 规范搭建项目结构"
- "创建项目文档目录"

## 执行流程

### 1. 创建目录结构

```
docs/
├── dev-rules.md              (必创建)
├── project-spec.md           (按需)
├── project-general-design.md (按需)
├── project-api-design.md     (按需)
├── project-schema-design.md  (按需)
├── project-ui-design.md      (按需)
├── project-deployment.md     (按需)
├── project-roadmap.md        (按需)
└── versions/
reports/
└── worklog.md
```

### 2. 生成 dev-rules.md

- 基于 `assets/dev-rules.md` 模板
- 填写项目名、GitHub 仓库地址
- 声明引用的 dev-meta 版本（当前为 v0.1.0）
- 作用：人类与 AI 共读的项目清单，描述项目结构与规范来源，而非规范正文副本

### 3. 按需创建项目基线文档

- `project-spec.md` — 项目目标、核心功能、非功能需求
- `project-general-design.md` — 系统架构、模块划分、技术决策
- `project-api-design.md` — API 设计（若涉及）
- `project-schema-design.md` — 数据 Schema（若涉及）
- `project-ui-design.md` — UI 设计系统（前端项目建议创建）
- `project-deployment.md` — 部署与运维（几乎都需要）
- `project-roadmap.md` — 版本路线图

### 4. 初始化 worklog

- 基于 `assets/worklog.md` 创建 `reports/worklog.md`

## Skill 资源映射

| 资源 | 来源 | 用途 |
|------|------|------|
| SKILL.md | — | 上述流程指令 |
| references/project-dev-flow.md | `docs/project-dev-flow.md` | 目录结构与文件职责详情 |
| assets/dev-rules.md | `templates/dev-rules.md` | 项目入口模板 |
| assets/project-spec.md | `templates/project/project-spec.md` | 项目规格模板 |
| assets/project-general-design.md | `templates/project/project-general-design.md` | 概要设计模板 |
| assets/project-api-design.md | `templates/project/project-api-design.md` | API 设计模板 |
| assets/project-schema-design.md | `templates/project/project-schema-design.md` | Schema 设计模板 |
| assets/project-ui-design.md | `templates/project/project-ui-design.md` | UI 设计模板 |
| assets/project-deployment.md | `templates/project/project-deployment.md` | 部署运维模板 |
| assets/project-roadmap.md | `templates/project/project-roadmap.md` | 路线图模板 |
| assets/worklog.md | `templates/worklog.md` | 工作日志模板 |

## 使用示例

```
用户: "初始化一个新项目 shadow-player-v3"

AI:  1. 创建 docs/ 目录树
     2. 生成 docs/dev-rules.md（项目名: shadow-player-v3）
     3. 询问是否需要项目基线文档
     4. 创建 reports/worklog.md
     5. 输出初始化报告
```
