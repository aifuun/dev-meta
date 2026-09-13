---
name: dm-log
description: 每日记录工作：追加每日工作总结、详细日志、待办与里程碑。触发于「记录今天的工作」。
---

# dm-log

## 概述

每日工作日志 skill，按 `04-worklog-rules.md` 规范追加工作记录、维护待办与里程碑。

## 职责边界

| 职责 | 归属 |
|------|------|
| 追加每日工作总结表行 | ✅ 本 skill |
| 追加详细日志（按日期章节，含当日 commit） | ✅ 本 skill |
| 维护待办与里程碑 | ✅ 本 skill |
| 新建 worklog 文件（基于 `templates/worklog.md`） | ✅ 本 skill |
| 生成周报 / 月报 / 阶段报告 | ❌ 委托 `dm-report` |
| 提交 worklog | 委托 `dm-commit` |
| 版本规划与版本文档 | ❌ `dm-plan-ver` |

## 触发

- "记录今天的工作"
- "update worklog"
- "今天做了什么"（隐式触发）

## 核心概念

### worklog 四块结构

| 块 | 内容 |
|----|------|
| 每日工作总结 | 顶部加行：**日期 + 一句话总结 + 更新次数** |
| 详细日志 | 按日期章节，记录模块 / 功能级别做了什么 |
| 待办 | 随进度标记完成、新增 |
| 里程碑 | 关键节点与状态 |

### 追加式，不改写历史

每日记录**追加**（总结表在顶部加新行），不修改已有日期的记录——worklog 是不可变工作史，改写会破坏追溯。

### 有 commit 记 commit，无 commit 记「其他工作」

当日有 commit 则在详细日志中列出（`hash` + `subject`）；无 commit 时在「其他工作」中记录，保持每日不空。

### 文件位置与模板

`docs/reports/worklog.md`；不存在时基于 `templates/worklog.md` 创建。格式规范的唯一权威是 `docs/04-worklog-rules.md`。

### 前置条件

`./CODEBUDDY.md` 需存在——本 skill 依赖它确认项目已绑定 dev-meta 规范（见 skills/README 前置条件表）。

## 执行流程

### 1. 定位文件

找到当前项目的 `docs/reports/worklog.md`。若不存在，基于 `templates/worklog.md` 创建。

### 2. 追加每日工作总结

在 `## 每日工作总结` 表格**顶部**新增一行：

```markdown
| **2026-07-21** | 工作总结（一句话概括，含关键交付物与问题）（更新了 n 次） |
```

### 3. 追加详细日志（如当天有新内容）

在 `## 详细日志` 下新增日期章节：

```markdown
### 2026-07-21

- **模块/功能**: 具体做了什么事
- **模块/功能**: 具体做了什么事
  - `abc1234` commit 简述（如有 commit）
```

当日有 commit 则列出 commit hash 与简述；无 commit 则在"其他工作"中记录讨论、决策、操作。

### 4. 维护待办列表

同步增减 `## 待办` 中的条目，状态使用以下标注：

| 标注 | 含义 |
|------|------|
| ⬜ 待开始 | 尚未启动 |
| 🔄 进行中 | 正在执行 |
| ✅ 已完成 | 已达成 |
| ❌ 已取消 | 不再需要 |

### 5. 按需更新里程碑

若当日产生了可标记的里程碑节点，在 `## 里程碑` 表格追加。

### 6. 提交

提交 worklog 更新 — 委托 dm-commit skill。示例：
```
chore: update worklog — <一句话总结>
```

## 关键规则速查

| 规则 | 来源 |
|------|------|
| 每日表行顶部插入，更新次数用 `（更新了 n 次）` | 04-worklog-rules.md |
| commit 用 `` `abc1234` `` 格式，简述用中文 | 04-worklog-rules.md |
| 一个日期章节对应一个 `###`，允许多次编辑 | 04-worklog-rules.md |
| 待办状态用统一标注，勿混用 | 04-worklog-rules.md |
| 禁止：粘贴大段日志、未完成先标记✅、总结与详情矛盾 | 04-worklog-rules.md |

## 产出与完成判据

**产出**：

- `docs/reports/worklog.md` 更新：总结表新增一行 + 详细日志新增日期章节 + 待办 / 里程碑同步

**完成判据**：

- [ ] 「每日工作总结」表**顶部**已加当日行
- [ ] 「详细日志」已加当日日期章节
- [ ] 当日有 commit 则已列出（hash + subject）；无 commit 则在「其他工作」记录
- [ ] 待办已标记完成 / 新增，里程碑已同步
- [ ] **未改写**已有日期的历史记录

## 资源映射

| 资源 | 来源 | 用途 |
|------|------|------|
| `~/.codebuddy/skills/dm-log/SKILL.md` | — | 部署版（由中文源自动生成，勿手改） |
| references/worklog-rules.md | `docs/04-worklog-rules.md` | 日志规范详情 |
| assets/worklog.md | `templates/worklog.md` | 新建项目时复制 |

## 使用示例

```
用户: "记录今天的工作"

AI:  1. 读取 docs/reports/worklog.md
     2. 追加每日表行：| 2026-07-21 | 新增状态机分层规则... |
     3. 追加详细日志章节：
        ### 2026-07-21
        - **version-rules**: design 增加跨 TF 状态机章节
          - `42ee152` feat: design 增加跨 TF 状态机
        - **templates**: 同步更新 version 与 project 模板
     4. 待办: 标记已完成项，新增待办
     5. 输出变更摘要
```
