# dm-init

## 概述

项目初始化 skill，按 `01-project-dev-flow.md` 规范为新项目搭建文档骨架。一次性使用，项目启动时执行。

## 触发

- "初始化新项目"
- "按 dev-meta 规范搭建项目结构"
- "创建项目文档目录"

## 执行流程

### 1. 创建目录结构

```
docs/
├── 02-project-spec.md         (按需)
├── 03-project-design.md       (按需)
├── 04-project-api-design.md   (按需)
├── 05-project-schema-design.md(按需)
├── 06-project-ui-design.md    (按需)
├── 07-project-deployment.md   (按需)
├── 08-project-roadmap.md      (按需)
├── versions/
└── adrs/
docs/reports/
└── worklog.md
```

### 2. 生成 CODEBUDDY.md

- 基于 `assets/CODEBUDDY.md` 模板，在项目根目录创建 `./CODEBUDDY.md`
- 填写 dev-meta 仓库地址与版本（当前为 v0.1.0）
- 作用：项目与 dev-meta 的版本绑定 + 例外项记录。通用规范（DoD、AI 协作、编码约定）由 `~/.codebuddy/CODEBUDDY.md` 全局加载，无需每个项目重复。

### 3. 按需创建项目基线文档

- `02-project-spec.md` — 项目目标、核心功能、非功能需求
- `03-project-design.md` — 系统架构、模块划分、技术决策
- `04-project-api-design.md` — API 设计（若涉及）
- `05-project-schema-design.md` — 数据 Schema（若涉及）
- `06-project-ui-design.md` — UI 设计系统（前端项目建议创建）
- `07-project-deployment.md` — 部署与运维（几乎都需要）
- `08-project-roadmap.md` — 版本路线图

### 4. 初始化 worklog

- 基于 `assets/worklog.md` 创建 `docs/reports/worklog.md`

### 5. 提交

提交所有创建的文件 — 委托 dm-commit skill。示例：
```
chore: initialize project docs following dev-meta
```

## Skill 资源映射

| 资源 | 来源 | 用途 |
|------|------|------|
| SKILL.md | — | 上述流程指令 |
| references/project-dev-flow.md | `docs/01-project-dev-flow.md` | 目录结构与文件职责详情 |
| assets/CODEBUDDY.md | — | 项目入口模板（版本绑定 + 例外项） |
| assets/project-spec.md | `templates/project/project-spec.md` | 项目规格模板 |
| assets/project-design.md | `templates/project/project-design.md` | 设计模板 |
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
    2. 生成 ./CODEBUDDY.md（版本绑定 + 例外项）
    3. 询问是否需要项目基线文档
    4. 创建 docs/reports/worklog.md
    5. 输出初始化报告
```
