# dm-log

## 概述

每日工作日志 skill，按 `worklog-rules.md` 规范追加工作记录、维护待办与里程碑。

## 触发

- "记录今天的工作"
- "update worklog"
- "今天做了什么"（隐式触发）

## 执行流程

### 1. 定位文件

找到当前项目的 `reports/worklog.md`。若不存在，基于 `templates/worklog.md` 创建。

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

## 关键规则速查

| 规则 | 来源 |
|------|------|
| 每日表行顶部插入，更新次数用 `（更新了 n 次）` | worklog-rules.md |
| commit 用 `` `abc1234` `` 格式，简述用中文 | worklog-rules.md |
| 一个日期章节对应一个 `###`，允许多次编辑 | worklog-rules.md |
| 待办状态用统一标注，勿混用 | worklog-rules.md |
| 禁止：粘贴大段日志、未完成先标记✅、总结与详情矛盾 | worklog-rules.md |

## Skill 资源映射

| 资源 | 来源 | 用途 |
|------|------|------|
| SKILL.md | — | 上述流程指令 + 规则速查 |
| references/worklog-rules.md | `docs/worklog-rules.md` | 日志规范详情 |
| assets/worklog.md | `templates/worklog.md` | 新建项目时复制 |

## 使用示例

```
用户: "记录今天的工作"

AI:  1. 读取 reports/worklog.md
     2. 追加每日表行：| 2026-07-21 | 新增状态机分层规则... |
     3. 追加详细日志章节：
        ### 2026-07-21
        - **version-rules**: general-design 增加跨 TF 状态机章节
          - `42ee152` feat: general-design 增加跨 TF 状态机
        - **templates**: 同步更新 version 与 project 模板
     4. 待办: 标记已完成项，新增待办
     5. 输出变更摘要
```
