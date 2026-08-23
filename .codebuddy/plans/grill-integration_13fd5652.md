---
name: grill-integration
overview: 将 Grill-Me「提问收敛」理念内嵌到 dev-meta 的 Plan 阶段 skill（dm-plan-ver / dm-dev-tf）：在版本级（需求级、架构级）与 TF 级（实现级）文档产出前增加显式「提问→回答→沉淀」步骤，并同步部署版 SKILL.md，符合 skill-doc-principles 双端一致原则。
todos:
  - id: add-grill-principle
    content: 在 skill-doc-principles.md 新增「决策点显式收敛」原则（提问→回答→沉淀三步 + 沉淀规则）
    status: completed
  - id: update-dm-plan-ver
    content: 更新 dm-plan-ver.md 核心概念与阶段 1，插入需求级/架构级 grill 步骤，并同步部署版 SKILL.md
    status: completed
    dependencies:
      - add-grill-principle
  - id: update-dm-dev-tf
    content: 更新 dm-dev-tf.md 执行流程与规则速查，插入实现级 grill，并同步部署版 SKILL.md
    status: completed
    dependencies:
      - update-dm-plan-ver
  - id: update-readme
    content: 更新 skills/README.md 关系图与触发方式，标注 grill 内嵌位置
    status: completed
    dependencies:
      - update-dm-plan-ver
      - update-dm-dev-tf
  - id: verify-sync
    content: 用 [skill:skill-creator] 验收双端一致性与文档结构完整性，确认无漂移
    status: completed
    dependencies:
      - update-readme
---

## 产品概述
将 Grill-Me 理念（AI 扮演挑剔架构师，在编码前提出决定性问题的问答闭环）内嵌到 dev-meta 现有 Plan 阶段 skill 流程中，填补「AI 单方面输出文档、无显式决策收敛」的空白。不新增独立 skill，以显式子步骤形式嵌入 dm-plan-ver 与 dm-dev-tf，问答结果沉淀进文档，从源头拦截隐性假设、防止无效编码。

## 核心功能
- 需求级 grill：dm-plan-ver 创建 200-spec 前触发，围绕范围边界、完成标准、降级策略、排除项提问收敛
- 架构级 grill：dm-plan-ver 创建 300-design 前触发（最关键），围绕数据流、模块边界、异常处理、兼容性、技术选型提问收敛
- 实现级 grill：dm-dev-tf 出开发概要前触发，仅当 300-design 对当前 TF 不完整时启动，针对缺口提问
- 决策沉淀规则：决策性回答写入 200-spec/300-design 对应章节；技术选型类触发 dm-adr 记录；问答不得留在对话流中丢失
- 原则与入口落地：skill-doc-principles 新增「决策点显式收敛」原则；README 标注 grill 内嵌位置（不新增 skill 条目）


## 技术栈
- 纯文档修改：dev-meta 规范仓库（Markdown 设计文档 + 英文部署版 SKILL.md），无代码实现
- 双端一致机制：`skills/*.md`（中文设计文档）↔ `~/.codebuddy/skills/<skill>/SKILL.md`（英文部署版）结构强制对齐，先改中文再同步英文

## 实施方案
### 修改目标与变更内容
1. `skills/skill-doc-principles.md`（[MODIFY]，叠加在未提交新增之上）：新增核心原则「决策点显式收敛」——决策点应有显式「AI 提问→用户回答→沉淀文档」三步，不依赖 AI 自问自答；沉淀规则：决策性回答写入对应文档、技术选型触发 dm-adr
2. `skills/dm-plan-ver.md` + `~/.codebuddy/skills/dm-plan-ver/SKILL.md`（[MODIFY]）：核心概念新增「grill 决策收敛」小节（触发时机：spec 前=需求级、design 前=架构级；问题粒度 3-5 个决定性决策点，不重复文档已有内容；沉淀规则）；执行流程阶段 1 在创建 200-spec、300-design 前各插入一个 grill 步骤
3. `skills/dm-dev-tf.md` + `~/.codebuddy/skills/dm-dev-tf/SKILL.md`（[MODIFY]）：执行流程步骤 3 与 4 之间插入实现级 grill 步骤（触发条件：300-design 对当前 TF 不完整；回答写入开发概要或对应文档）；关键规则速查新增一条规则
4. `skills/README.md`（[MODIFY]，叠加在未提交修改之上）：Skill 关系图与触发方式表标注 grill 内嵌位置，明确「grill 是 dm-plan-ver / dm-dev-tf 流程内步骤，非独立 skill」

### 关键决策
- 不做独立 skill：触发时机无法由用户自觉界定，独立会造成职责边界与 dm-plan-ver/dm-dev-tf 重复
- 实现级 grill 设触发条件：300-design 完整时跳过，避免流程负担过重
- 不触碰 `skills/dm-adr.md` 的未提交重构（与本计划无关）；不修改模板、samples、docs/ 规范文档

## 目录结构
```
skills/
├── skill-doc-principles.md  # [MODIFY] 新增「决策点显式收敛」原则（反模式表与核心原则同步更新）
├── dm-plan-ver.md           # [MODIFY] 核心概念新增 grill 小节；阶段 1 插入需求级/架构级 grill 步骤
├── dm-dev-tf.md             # [MODIFY] 步骤 3/4 间插入实现级 grill；规则速查新增一条
└── README.md                # [MODIFY] 关系图/触发方式标注 grill 内嵌位置

~/.codebuddy/skills/
├── dm-plan-ver/SKILL.md     # [MODIFY] 英文版同步（Core Concepts + Phase 1）
└── dm-dev-tf/SKILL.md       # [MODIFY] 英文版同步（Workflow Step 3.5 + Key Rules）
```


## Agent Extensions
### Skill
- **skill-creator**
  - Purpose: 指导 dm-plan-ver 与 dm-dev-tf 的 skill 文档更新，确保新增的 grill 步骤符合 skill 设计规范（触发词、规则表、可遍历性）
  - Expected outcome: 更新后的两份 skill 文档结构完整、规则单一权威、与 skill-doc-principles 骨架一致
