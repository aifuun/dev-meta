---
name: dm-grillme-plan
overview: 新建独立 skill `dm-grillme-plan`，将 Grill-Me「Plan 阶段显式逼问决策」固化为通用（非版本类）需求的按需工作流，产出可沉淀的 Final Plan，与既有的版本内嵌 grill（dm-plan-ver/dm-dev-tf）形成「通用 vs 版本」分工，并同步英文部署版与 README。
todos:
  - id: write-design-doc
    content: 编写 skills/dm-grillme-plan.md 中文设计文档（按标准骨架，含双轨分工与 §7 引用）
    status: completed
  - id: write-deploy-assets
    content: 创建 ~/.codebuddy/skills/dm-grillme-plan/SKILL.md 英文部署版与 assets/grill-plan-template.md
    status: completed
    dependencies:
      - write-design-doc
  - id: update-readme
    content: 更新 skills/README.md 总览表、触发方式表与 grill 双轨注释
    status: completed
  - id: verify-with-creator
    content: 使用 [skill:skill-creator] 验收双端结构一致性与 §7 合规，确认无漂移
    status: completed
    dependencies:
      - write-design-doc
      - write-deploy-assets
      - update-readme
---


## 用户需求

创建一个独立的 CodeBuddy Skill `dm-grillme-plan`，将 Grill-Me「Plan 阶段显式逼问决策」固化为**通用（非版本类）需求**的按需工作流。当用户提出新需求或初始方案（尤其涉及编码/架构）时，AI 先扮演挑剔架构师逼出隐性假设，再进入实现。

## 产品概述

一个决策收敛前置器：面向版本流水线之外的通用需求（一次性脚本、独立重构、跨项目方案评审等），在写代码/出方案前，通过「AI 提问 → 用户回答 → 沉淀文档」三步收敛关键决策，输出可复用的 Final Plan，技术选型类回答自动转交 `dm-adr`。

## 核心功能

- **触发决策逼问**：通过 `/grill-me`、`规划前先拷问我`、`先 pressure-test 这个方案` 等自然语言触发，不直接写代码或最终方案。
- **三阶段闭环**：单轮提问 3-5 个决定性决策问题（不重复用户已明说），用户回答后收敛输出 Final Plan。
- **Final Plan 沉淀**：生成 `docs/plans/<topic>-grill.md` 决策记录，避免问答仅停留在对话流中丢失。
- **分工清晰**：本 skill 仅管「通用/非版本类」需求；版本类规划仍走 `dm-plan-ver`（需求级/架构级）与 `dm-dev-tf`（实现级）的内嵌 grill，互不重复。
- **后续路由**：技术选型类回答触发 `dm-adr`；编码类需求交对应实现 skill；提交委托 `dm-commit`。



## Tech Stack Selection

- 纯 Markdown 定义：遵循 `skill-doc-principles.md` 标准章节骨架（概述/职责边界/触发/核心概念/执行流程/关键规则速查/资源映射/使用示例）。
- 双端交付：`skills/dm-grillme-plan.md`（中文设计文档） + `~/.codebuddy/skills/dm-grillme-plan/SKILL.md`（英文部署版，frontmatter `name`/`description` + 8 章节）。
- 资产模板：`~/.codebuddy/skills/dm-grillme-plan/assets/grill-plan-template.md`（Final Plan 空白模板）。

## Implementation Approach

以 `dm-adr` 的「按需穿插」模式为参考形态（README 关系图已存在 `dm-adr ← 按需穿插`），新建一个**按需、非内嵌**的通用 grill skill。核心决策：

1. **定位为「通用 vs 版本」双轨中的通用轨**：明确在职责边界声明「版本类走 dm-plan-ver/dm-dev-tf 内嵌 grill，本 skill 只管非版本类」，避免 grill 逻辑三处维护（plan-ver / dev-tf / grillme-plan）。这是与既有提交 203f4ca 内嵌 grill 并存而非冲突的关键。
2. **产出必须有持久载体**：Final Plan 沉淀到 `docs/plans/<topic>-grill.md`，满足 §7「决策须沉淀」并解决独立 skill「无持久产物」的固有弱点。
3. **问题分三级，聚焦决定性点**：目标边界级（范围/完成标准/排除项/降级）→ 架构技术级（数据流/模块边界/异常/兼容/选型）→ 实现降级级（并发边界/依赖集成/测试策略），每轮只取 3-5 个最影响实现的决策点。
4. **不自动编码**：grill 阶段严守「只逼问、不产出实现」，收敛后才允许路由到编码 skill，契合用户「Plan 阶段先触发」的诉求。

## Implementation Notes

- **复用而非新建概念**：三阶段闭环、3-5 点标准、选型走 `dm-adr` 均直接引用 §7「决策点显式收敛」，本 skill 视为 §7 的通用落地实例，正文不重复定义。
- **单一权威**：Final Plan 结构仅在 `assets/grill-plan-template.md` 定义，设计文档资源映射指向它，避免模板散落两处。
- **双端一致**：中文版与英文部署版章节严格一一对应；修改任一端须同步另一端（§5 双端一致）。
- **目录惰性创建**：`docs/plans/` 若不存在，skill 执行时按需在 Final Plan 沉淀步骤创建，不预建空目录。

## Architecture Design

```
用户新需求 / 初始 Plan
        │  (/grill-me / 规划前先拷问我)
        ▼
[ dm-grillme-plan ]  ── 通用/非版本类 决策逼问
   1. 接收需求
   2. grill 提 3-5 决定性问题（不重复已明说）
   3. 用户回答
   4. 收敛输出 Final Plan
   5. 沉淀 docs/plans/<topic>-grill.md
        │
        ├── 技术选型类回答 ──► [dm-adr]  记录 ADR
        ├── 编码类需求     ──► 对应实现 skill
        └── 提交           ──► [dm-commit]

（版本类需求另走：dm-plan-ver / dm-dev-tf 内嵌 grill，不在此链路）
```

## Directory Structure

```
skills/
└── dm-grillme-plan.md                       # [NEW] 中文设计文档，按 skill-doc-principles 标准骨架
~/.codebuddy/skills/dm-grillme-plan/
├── SKILL.md                                 # [NEW] 英文部署版，结构与中文版 8 章节一一对应
└── assets/
    └── grill-plan-template.md               # [NEW] Final Plan 决策记录空白模板
skills/
└── README.md                               # [MODIFY] 总览表/触发方式表加 dm-grillme-plan；将「grill 非独立 skill」注释改为双轨说明
```

## Key Code Structures

Final Plan 模板（`assets/grill-plan-template.md`）关键字段：

```markdown
# Grill Plan: <topic>

- 目标：<一句话目标>
- 范围：<纳入/明确排除项>
- 完成标准：<可验证的 done 定义>
- 降级策略：<信息不全/资源受限时的取舍>

## 关键决策点 Q&A
| # | 决策问题 | 用户回答 | 影响 |
|---|---------|---------|------|
| 1 | ...     | ...     | ...  |

## 后续动作
- 编码：<对应 skill / 入口>
- 技术选型 ADR：<dm-adr 链接，若有>
- 提交：委托 dm-commit
```


## Agent Extensions

### Skill
- **skill-creator**
  - Purpose: 按 CodeBuddy 规范创建/校验 `dm-grillme-plan` 的 SKILL.md 与 assets 结构，确保 frontmatter、章节骨架、双端一致性符合标准。
  - Expected outcome: 生成结构合规的中文设计文档与英文部署版，并通过自检确认与 `skill-doc-principles.md` 一致、无漂移。
