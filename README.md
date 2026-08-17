# dev-meta

开发元规范与工程标准，跨项目共享。当前以 Transaction Flow 作为版本文档主轴。

## 元数据

| 项 | 值 |
|---|---|
| 版本 | `v0.1.0` |
| 状态 | 起草中 |
| 许可证 | 待定 |

## 工作流

### 项目全生命周期

```
dm-init     →  架构基线  →  契约基线  →  路线规划  →  小版本迭代  →  归档
(project-spec)  (design)   (api/schema)  (roadmap)    (plan-ver)     (回收)
```

### 版本迭代（每个小版本）

```
200-spec    →  300-design    →  400-build    →  500-schedule
(验收标准)      (架构决策)       (实现蓝图)       (排程)
```

### Git 开发流

```
版本 PR  →  TF Issue  →  TF 分支  →  commit  →  review  →  merge  →  关 Issue
```

### 工作日志

```
每日总结表  +  详细日志  +  待办  +  里程碑  （每日穿插）
```

### Skill 工作流

```
dm-init  ──→  dm-plan-ver  ──→  dm-schedule（排程）
                   │
                   ├── dm-dev-tf（TF 开发）
                   ├── dm-commit（统一提交出口）
                   └── 版本收尾

dm-log  ←── 每日穿插  ←──→  dm-commit
dm-report  ←── 阶段周报
dm-adr  ←── 按需穿插  ←──→  dm-commit
```

| Skill | 职责 | 频率 |
|-------|------|------|
| `dm-init` | 初始化项目骨架，生成 CODEBUDDY.md + docs 目录树 | 低频 |
| `dm-plan-ver` | 开/关版本，创建四件套 + 分支/PR/Issue | 中频 |
| `dm-schedule` | 版本排程，工作包列表 + 防沉迷红线 | 中频 |
| `dm-dev-tf` | 启动 TF，读文档 + 确认 Issue + 出开发概要（开发在版本分支上） | 高频 |
| `dm-commit` | type 向导 + 格式校验 + Issue 关联 | 频繁 |
| `dm-log` | 每日总结 + 详细日志 + 待办 + 里程碑 | 每日 |
| `dm-report` | 从 worklog 提取生成周报/阶段报告 | 每周 |
| `dm-adr` | 维护架构/技术决策记录 | 按需 |

### CODEBUDDY 管理层

```
编辑 CODEBUDDY-global.md  →  commit  →  部署到 ~/.codebuddy/  →  全局生效
```

```
~/.codebuddy/CODEBUDDY.md  ← 全局：DoD、AI 协作、编码约定
        +（CodeBuddy 自动合并加载）
./CODEBUDDY.md              ← 项目：dev-meta 版本绑定 + 例外项
```

## 文件

- [docs/01-project-dev-flow.md](https://github.com/aifuun/dev-meta/blob/main/docs/01-project-dev-flow.md) — 项目级开发流程与文档分层骨架
- [docs/02-version-rules.md](https://github.com/aifuun/dev-meta/blob/main/docs/02-version-rules.md) — 版本目录文件规范（schedule / spec / design / build）
- [docs/03-git-flow-rules.md](https://github.com/aifuun/dev-meta/blob/main/docs/03-git-flow-rules.md) — Git 开发流规范（小版本 PR、TF issue、commit 规范）
- [docs/04-worklog-rules.md](https://github.com/aifuun/dev-meta/blob/main/docs/04-worklog-rules.md) — 工作日志规范（每日工作总结 + 详细日志 + 待办 + 里程碑）
- [docs/05-codebuddy-management.md](https://github.com/aifuun/dev-meta/blob/main/docs/05-codebuddy-management.md) — CODEBUDDY.md 管理规范：两层架构（全局层 vs 项目层）、加载机制、迁移说明
- [docs/CODEBUDDY-global.md](https://github.com/aifuun/dev-meta/blob/main/docs/CODEBUDDY-global.md) — 全局规范原始版本：`~/.codebuddy/CODEBUDDY.md` 的 source of truth，在此修改后部署生效
- [templates/worklog.md](https://github.com/aifuun/dev-meta/blob/main/templates/worklog.md) — 工作日志模板
- [templates/versions/](https://github.com/aifuun/dev-meta/tree/main/templates/versions) — 版本文档模板（与规范文件一一对应）
- [templates/project/](https://github.com/aifuun/dev-meta/tree/main/templates/project) — 项目级文档模板（project-spec / design / api-design / schema-design / roadmap）
- [skills/](https://github.com/aifuun/dev-meta/tree/main/skills) — Skill 设计文档（dm-init / dm-plan-ver / dm-schedule / dm-dev-tf / dm-log / dm-commit / dm-report / dm-adr）
- [samples/](https://github.com/aifuun/dev-meta/tree/main/samples) — 版本文档样例（V1.4.1-indexeddb-prefs）
