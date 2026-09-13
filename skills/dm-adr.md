---
name: dm-adr
description: 记录架构/技术决策时使用，按 ADR 五段式（背景/决策/原因/后果/替代方案）维护决策日志。触发于「记录一个技术决策」「创建 ADR」「补充/更新已有决策」。
---

# dm-adr

## 概述

架构决策记录 skill，按 ADR 格式维护技术决策日志。每项重大技术选型（云服务、基础设施、框架、协议、数据存储等）对应一篇独立 ADR，存放于 `docs/adrs/`。

## 职责边界

| 职责 | 归属 |
|------|------|
| 生成/维护 ADR | ✅ 本 skill |
| ADR 索引（`docs/adrs/README.md`） | ✅ 本 skill |
| ADR 提交 | 委托 dm-commit |

## 触发

- "记录一个技术决策"
- "创建 ADR"
- "我们决定用 X 做 Y"
- "为什么选择了 X？"（查询已有 ADR）
- "补一个决策记录"
- "评审 / 更新已有 ADR"

## 核心概念

### ADR 五段式格式

每篇 ADR 按固定五段式组织，一篇只记录一个决策：

| 段落 | 内容 |
|------|------|
| 背景 Context | 为什么需要这个决策 |
| 决策 Decision | 我们选择了什么 |
| 原因 Rationale | 为什么选它（关键取舍） |
| 后果 Consequences | ✅ 正面影响 / ⚠️ 代价 / 🔧 后续动作 |
| 替代方案 Alternatives | 被否掉的可选方案（可选） |

完整骨架（可直接套用）：

```markdown
# ADR-NNN: 标题（简短名词短语）

- **状态**: 提议中 (Proposed) / 已接受 (Accepted) / 已废弃 (Deprecated) / 已替代 (Superseded by ADR-NNN)
- **日期**: YYYY-MM-DD

## 背景     — 为什么需要做这个决策
## 决策     — 明确陈述选择了什么方案
## 原因（可选）— 为什么选它而非其他方案
## 后果     — ✅ 正面 / ⚠️ 代价 / 🔧 跟进
## 替代方案（可选）— 被否掉的方案表
## 相关     — 相关文档 / ADRs / Issues
```

### 文件结构

```text
docs/adrs/
├── README.md        # 导航索引（表格 + 按领域分类）
├── adr-001.md       # 独立决策文件
├── adr-002.md
└── ...
```

### 状态转换

ADR 有生命周期，不可修改已接受原文，只能转换状态：

```
Proposed → Accepted → Deprecated
                 → Superseded (by ADR-NNN)
```

- **Proposed（提议中）**：正在讨论，尚未实施
- **Accepted（已接受）**：已采纳并实施；**不可改原文**，需变化时更新旧 ADR 状态并创建新 ADR
- **Deprecated（已废弃）**：不再适用
- **Superseded（已替代）**：被新 ADR 替代，注明替代者（Superseded by ADR-NNN），需双向交叉引用

## 执行流程

### 1. 确定编号

扫描 `docs/adrs/adr-*.md`，编号 = 最大值 + 1。若目录不存在则创建 `README.md` 并从 ADR-001 开始。

### 2. 评估决策

引导用户明确：决策领域、候选方案、关键取舍、关联文档。

### 3. 撰写 ADR

按「核心概念」的五段式格式撰写。一篇 ADR 只记录一个决策。

> **篇幅纪律**：ADR 是**决策日志，不是设计文档**——保持精简，只写「为什么这么选」，不展开实现细节。

### 4. 创建文件

创建 `docs/adrs/adr-NNN.md`。

### 5. 更新索引

在 `docs/adrs/README.md` 表格与分类导航中追加新记录。

### 6. 处理替代关系

若新决策替代旧 ADR，更新旧 ADR 状态为 `已废弃 (Deprecated, superseded by ADR-NNN)`。

### 7. 提交

委托 dm-commit，格式：`docs(adr): add ADR-NNN — <decision title>`

## 关键规则速查

| 规则 | 来源 |
|------|------|
| 重大技术决策必须有 ADR | — |
| 一篇 ADR 一个决策 | — |
| 已接受的 ADR 不可修改原文，需更新状态并创建新 ADR | — |
| 替代关系需双向交叉引用 | — |
| 文件路径固定 `docs/adrs/adr-NNN.md` | — |
| 可观测性架构级取舍（采样粒度 / computeUnits / 预编译模型 / 诊断分级）须走 ADR | docs/07-observability-driven-dev.md §6 |
| 提交委托 dm-commit | dm-commit |

## 产出与完成判据

**产出**：

- ADR 文件 `docs/adrs/adr-NNN.md`（五段式完整）
- 索引更新 `docs/adrs/README.md`

**完成判据**：

- [ ] 五段式齐全（背景 / 决策 / 原因 / 后果 / 替代方案）
- [ ] 状态明确（Proposed 或 Accepted），日期已填
- [ ] 编号为最大值 + 1，无冲突
- [ ] 一篇只记录一个决策，篇幅精简（决策日志，非设计文档）
- [ ] 若替代旧 ADR：旧 ADR 状态已更新且**双向交叉引用**已建立
- [ ] 索引已追加，且可观测性取舍类已按规则记录

## 资源映射

| 资源 | 来源 | 用途 |
|------|------|------|
| SKILL.md | — | 流程指令 + 规则速查（**由中文源自动部署，勿手改**） |
| references/adr-format.md | — | ADR 完整格式规范与字段说明，**需确认字段定义或格式细节时加载** |
| assets/adr-template.md | — | 新建 ADR 的空白模板，**可直接复制使用** |

## 使用示例

```
用户: "我们决定用 Terraform 管理云资源，记录这个决策"

AI:  1. 扫描 docs/adrs/ → 已有 4 篇，编号 ADR-005
     2. 确认候选方案：手动配置 / Pulumi / Terraform
     3. 生成 ADR-005：
        # ADR-005: 使用 Terraform 管理云资源
        - 状态: Accepted
        - 背景: 需要 IaC 工具统一管理多云资源
        - 决策: 使用 Terraform
        - 原因: 多云支持好、社区生态成熟
        - 后果: ✅ 声明式管理 / ⚠️ 需学习 HCL / 🔧 需搭建 CI 集成
     4. 创建 docs/adrs/adr-005.md
     5. 更新 docs/adrs/README.md 索引
     6. 询问是否提交
```
