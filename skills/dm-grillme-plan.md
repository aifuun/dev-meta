# dm-grillme-plan

## 概述

通用（非版本类）需求的 Plan 阶段决策逼问 skill。在写代码 / 出方案前，通过「AI 提问 → 用户回答 → 沉淀文档」三步收敛关键决策，输出可复用的 Final Plan；技术选型类回答转交 `dm-adr`。

## 职责边界

| 职责 | 归属 |
|------|------|
| 逼问决策点 + 收敛输出 Final Plan | ✅ 本 skill |
| 沉淀 Final Plan 到 `docs/plans/<topic>-grill.md` | ✅ 本 skill |
| 技术选型类回答记录 ADR | 委托 dm-adr |
| 编码 / 实现 | 委托对应实现 skill |
| 提交 | 委托 dm-commit |

> **双轨分工**：本 skill 只管**非版本类通用需求**（一次性脚本、独立重构、跨项目方案评审等）。**版本类**规划走 `dm-plan-ver`（需求级 / 架构级 grill）与 `dm-dev-tf`（实现级 grill）的**内嵌** grill，不在此链路，避免 grill 逻辑三处维护。

## 触发

- `/grill-me`
- "规划前先拷问我"
- "先 pressure-test 这个方案"
- "这个新需求先逼问一下关键决策"
- 收到新需求 / 初始方案，想先收敛再动手

## 核心概念

### 三阶段闭环

本 skill 是 skill-doc-principles §7「决策点显式收敛」的**通用落地实例**。每个决策点走：

```
AI 提问 → 用户回答 → 沉淀文档
```

不依赖 AI 自问自答；问答不得只留在对话流中。

### 问题三级

按需求成熟度逐层聚焦，每轮只取 **3-5 个最影响实现的决策点**（不重复用户已明说）：

| 级别 | 关注点 | 典型提问 |
|------|--------|---------|
| 目标边界级 | 范围 / 完成标准 / 排除项 / 降级 | 交付边界在哪？什么算 done？哪些明确不做？信息不全怎么降级？ |
| 架构技术级 | 数据流 / 模块边界 / 异常 / 兼容 / 选型 | 数据怎么流转？模块边界？异常处理？向下兼容？技术选型？ |
| 实现降级级 | 并发边界 / 依赖集成 / 测试策略 | 高并发边界？外部依赖如何集成？测试怎么覆盖？ |

### Final Plan 结构

唯一权威定义在 `assets/grill-plan-template.md`（部署版）。字段含：目标、范围、完成标准、降级策略、关键决策点 Q&A、后续动作（含 ADR 链接）。

### 与 §7 的关系

- §7 规定「决策点须显式提问→回答→沉淀」，本 skill 是其**通用 / 非版本类**的具体执行形态。
- 版本类的同款执行已内嵌于 `dm-plan-ver` / `dm-dev-tf`，本 skill 不重复定义也不重复触发。

## 执行流程

### 1. 接收需求

读取用户的新需求或初始 Plan；判断是否属于**非版本类通用需求**（是 → 本 skill；否 → 提示走 `dm-plan-ver` / `dm-dev-tf` 内嵌 grill）。

### 2. Grill 提问

扮演挑剔架构师，提出 **3-5 个决定性决策问题**（按「问题三级」聚焦，不重复用户已明说），**不直接写代码或最终方案**。

### 3. 用户回答

收集回答；若某决策点影响重大且未收敛，可追加一轮（至多 2 轮，避免流程负担）。

### 4. 收敛输出 Final Plan

按 `assets/grill-plan-template.md` 结构输出 Final Plan（目标 / 范围 / 完成标准 / 降级策略 / 关键决策点 Q&A）。

### 5. 沉淀文档

创建 `docs/plans/<topic>-grill.md`（目录若不存在则按需创建），写入 Final Plan。

### 6. 后续路由

- 技术选型类回答 → 委托 `dm-adr` 记录 ADR，并在 Final Plan 关联链接。
- 编码类需求 → 交对应实现 skill。
- 提交 → 委托 `dm-commit`。

## 关键规则速查

| 规则 | 来源 |
|------|------|
| 本 skill 只管非版本类；版本类走 dm-plan-ver / dm-dev-tf 内嵌 grill | skill-doc-principles §7 |
| 每轮 3-5 个决定性决策点，不重复用户已明说 | skill-doc-principles §7 |
| grill 阶段不产出实现代码 / 最终方案 | skill-doc-principles §7 |
| 问答须沉淀进 Final Plan 文档，不留在对话流 | skill-doc-principles §7 |
| 技术选型类回答触发 dm-adr | skill-doc-principles §7 |
| Final Plan 结构唯一权威在 assets/grill-plan-template.md | — |

## 资源映射

| 资源 | 来源 | 用途 |
|------|------|------|
| SKILL.md | — | 流程指令 + 规则速查 |
| assets/grill-plan-template.md | — | Final Plan 空白模板（部署版路径 `~/.codebuddy/skills/dm-grillme-plan/assets/`） |

## 使用示例

```
用户: "/grill-me 我想写个脚本，把 Notion 里的每周任务自动同步到日历"

AI:  1. 判断：非版本类通用需求 → 本 skill
     2. Grill 提问（架构技术级 + 目标边界级）：
        Q1 同步方向是单向（Notion→日历）还是双向？双向冲突怎么解？
        Q2 "每周任务" 怎么界定？按数据库/标签/某个视图过滤？
        Q3 日历用哪个？Google / Apple / 飞书？授权方式（OAuth 本地 token？）
        Q4 失败降级：API 限流 / 网络抖动手工怎么兜底？
        Q5 触发时机：cron 本地跑 / 云函数 / 手动？
     3. 用户回答：单向、按"每周"标签视图、Google Calendar OAuth、限流就跳过并通知、本地 cron 每日 7 点
     4. 收敛输出 Final Plan
     5. 沉淀 docs/plans/notion-calendar-sync-grill.md
     6. 路由：技术选型（Google Calendar API）→ 提示可走 dm-adr；编码 → 对应实现 skill
```
