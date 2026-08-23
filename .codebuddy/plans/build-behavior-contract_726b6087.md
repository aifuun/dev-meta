---
name: build-behavior-contract
overview: 在 400-build 模板新增可选「关键行为契约（关键测试用例）」节，将 300-design 授权的测试 case 落地为函数级 given-when-then 行为约定，锁死算法/隐性契约类函数的具体行为；与既有「design 给场景、build 给签名、dev-tf 落地真实测试」分层不冲突。同步部署版与 dm-plan-ver 速查。
todos:
  - id: write-build-template-cn
    content: 在 templates/versions/vX.Y-<slug>/400-build.md 的 §2.3 与 §3.3 末尾各追加可选「关键行为契约（关键测试用例）」子项（表格：函数/场景/预期）
    status: completed
  - id: write-build-template-en
    content: 同步 ~/.codebuddy/skills/dm-plan-ver/assets/400-build.md 的 §2.3/§3.3 行为契约子项（英文 Behavior Contract）
    status: completed
    dependencies:
      - write-build-template-cn
  - id: update-dm-plan-ver-cn
    content: 在 skills/dm-plan-ver.md 关键规则速查表新增规则：400-build 对算法/隐性契约类函数须含关键行为契约，薄胶水可省略
    status: completed
  - id: update-dm-plan-ver-en
    content: 在 ~/.codebuddy/skills/dm-plan-ver/SKILL.md Key Rules 同步上述规则（双端一致）
    status: completed
    dependencies:
      - update-dm-plan-ver-cn
  - id: verify-with-creator
    content: 使用 [skill:skill-creator] 验收双端模板与规则一致，grep 确认中/英 400-build 均含「关键行为契约」子项
    status: completed
    dependencies:
      - write-build-template-cn
      - write-build-template-en
      - update-dm-plan-ver-cn
      - update-dm-plan-ver-en
---

## 用户需求

在 `dm-plan-ver` 创建 `400-build.md`（实现蓝图）时，当前只给出关键函数签名（函数名、入参类型、返回值类型、调用时机）与伪代码。但签名无法约束「函数具体行为」——边界处理、异常分支、幂等、并发去重、降级取舍等隐性契约仍会在开发时被自由发挥。需在 build 层补充关键 unit test case 形态的行为规定，以锁死函数预期行为。

## 产品概述

在不改变既有测试分层的前提下，于 `400-build` 模板的「函数签名与伪代码」节追加一个**可选**的「关键行为契约（关键测试用例）」子项。用表格列出 函数 / 场景 / 预期（given-when-then 一句话），作为「行为规定」而非「测试实现」；`dm-dev-tf` 落地时据此生成真实单测。

## 核心功能

- **分场景强制**：仅对算法类 / 有隐性契约（幂等、并发去重、异常分支、降级取舍）的函数填写行为契约；薄胶水 / CRUD 函数可省略，避免流程负担。
- **表格化行为规定**：函数名 / 场景 / 预期（given-when-then 一句话），明确「输入→行为→输出」，防止开发时偏离。
- **与既有分层对齐**：`300-design` §7 测试策略给「测什么」（场景列表），`400-build` 行为契约给「期望是什么」（预期），`dm-dev-tf` 转真实测试代码；三层不重复、不冲突。
- **双端一致**：中文模板 ↔ 英文部署版模板，中文设计文档 ↔ 英文部署版 SKILL.md，同步新增并保持章节对齐。

## Agent Extensions
### Skill
- **skill-creator**
  - Purpose: 校验新增的 400-build 模板与 dm-plan-ver 部署版结构合规、双端一致，确认均含行为契约子项
  - Expected outcome: 通过校验，确认中/英 400-build 模板 §2.3/§3.3 均含「关键行为契约」子项且章节对齐，dm-plan-ver 速查含新规则，无漂移
