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
├── project-spec.md           (按需)
├── project-general-design.md (按需)
├── project-api-design.md     (按需)
├── project-schema-design.md  (按需)
├── project-roadmap.md        (按需)
└── versions/
reports/
└── worklog.md
```

### 2. 按需创建项目基线文档

- `project-spec.md` — 项目目标、核心功能、非功能需求
- `project-general-design.md` — 系统架构、模块划分、技术决策
- `project-api-design.md` — API 设计（若涉及）
- `project-schema-design.md` — 数据 Schema（若涉及）
- `project-roadmap.md` — 版本路线图

### 3. 初始化 worklog

- 基于 `templates/worklog.md` 创建 `reports/worklog.md`

## Skill 资源映射

| 资源 | 来源 | 用途 |
|------|------|------|
| SKILL.md | — | 上述流程指令 |
| references/project-dev-flow.md | `docs/project-dev-flow.md` | 目录结构与文件职责详情 |
| assets/project-spec.md | `templates/project/project-spec.md` | 项目规格模板 |
| assets/project-general-design.md | `templates/project/project-general-design.md` | 概要设计模板 |
| assets/project-api-design.md | `templates/project/project-api-design.md` | API 设计模板 |
| assets/project-schema-design.md | `templates/project/project-schema-design.md` | Schema 设计模板 |
| assets/project-roadmap.md | `templates/project/project-roadmap.md` | 路线图模板 |
| assets/worklog.md | `templates/worklog.md` | 工作日志模板 |

## 使用示例

```
用户: "初始化一个新项目 shadow-player-v3"

AI:  1. 创建 docs/ 目录树
     2. 询问是否需要项目基线文档
     3. 创建 reports/worklog.md
     4. 输出初始化报告
```
