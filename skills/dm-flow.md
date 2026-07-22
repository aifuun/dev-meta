# dm-flow

## 概述

版本开发生命周期 skill，覆盖从版本创建到收尾的全流程：文档、分支、PR、TF Issue、提交规范、追踪验收。

## 触发

- "新建版本 v1.2-payment"
- "开始 vX.Y"
- "创建 TF 文档"
- "TF1 完成了"
- "关闭版本 v1.2"

## 执行流程

### 阶段 1：版本启动

```
用户: "新建版本 v1.3-export"
```

1. **创建版本文档** `docs/versions/v1.3-export/`
   - `spec.md` — TF 目标与验收
   - `general-design.md` — TF 划分、数据流、关键决策、跨 TF 状态机
   - `detailed-design.md` — 流内步骤、函数签名、Schema、状态机/时序图
   - `tasks.md` — 任务拆解与执行顺序

2. **创建分支**
   ```bash
   git checkout -b feature/v1.3-export
   ```

3. **生成 PR 描述**
   - 标题：`[V1.3.0] Export to PDF`
   - 填写：目标、范围、验收入口、风险与回滚
   - 若用户装有 `gh` CLI，可直接创建 PR

4. **为每个 TF 生成 Issue**
   - 标题：`[TF1] 数据收集与预处理`
   - 填写：目标、完成标准、依赖、验收方法
   - 关联到版本 PR
   - 输出追踪矩阵

### 阶段 2：TF 推进

```
用户: "TF1 完成了"
```

1. **确认验收**：对照 `spec.md` 中该 TF 的验收标准
2. **执行 commit**
   ```text
   feat(export): collect and preprocess data for PDF export
   
   Closes #42
   ```
3. **关闭 TF Issue**（标记验收结果）
4. **更新 tasks.md** 与追踪矩阵

### 阶段 3：版本收尾

```
用户: "关闭版本 v1.3-export"
```

1. 确认所有 TF Issue 已关闭或明确延期
2. 补齐 `tasks.md` 验收结果
3. 提交 worklog 记录
4. Merge PR (squash merge)
5. 提交版本文档（如尚未提交）

## 关键规则速查

| 规则 | 来源 |
|------|------|
| TF 编号需稳定，废弃 TF 保留编号标 `[DEPRECATED]` | version-rules.md §3.1 |
| general-design 管 TF 级，detailed-design 管步骤级 | version-rules.md §3.3 |
| 跨 TF 状态机放 general-design，单 TF 状态机放 detailed-design | version-rules.md §3.4 |
| 每版本 1 PR，每 TF 1 Issue | git-flow-rules.md §2 |
| commit: `type(scope): subject` + `Closes #id` | git-flow-rules.md §3 |
| 分支: `feature/<version>-<tf>-<topic>` | git-flow-rules.md §4 |
| 合并: 默认 squash merge | git-flow-rules.md §4.2 |

## Skill 资源映射

| 资源 | 来源 | 用途 |
|------|------|------|
| SKILL.md | — | 上述全流程指令 + 关键规则速查 |
| references/version-rules.md | `docs/version-rules.md` | 四件套规则详情 |
| references/git-flow-rules.md | `docs/git-flow-rules.md` | PR/Issue/commit 规则详情 |
| assets/spec.md | `templates/versions/vX.Y-<slug>/spec.md` | 规格模板 |
| assets/general-design.md | `templates/versions/vX.Y-<slug>/general-design.md` | 概要设计模板 |
| assets/detailed-design.md | `templates/versions/vX.Y-<slug>/detailed-design.md` | 详细设计模板 |
| assets/tasks.md | `templates/versions/vX.Y-<slug>/tasks.md` | 任务拆分模板 |
| assets/tracking-matrix.md | 新增 | TF→Issue→PR 追踪模板 |

## 使用示例

```
用户: "新建版本 v1.5-login"

AI:  1. 创建 docs/versions/v1.5-login/ 四件套
     2. 创建分支 feature/v1.5-login
     3. 输出 PR 描述模板（标题 + 目标/范围/验收/风险）
     4. 输出 TF1-TF3 的 Issue 描述模板
     5. 打印追踪矩阵：
        | TF | Issue | PR | 验收 |
        | TF1 登录表单 | #xx | #xx | ⬜ |
        | TF2 验证流程 | #xx | #xx | ⬜ |
        | TF3 会话管理 | #xx | #xx | ⬜ |

用户: "TF2 完成了"

AI:  1. 确认验收标准
     2. 建议 commit: feat(login): implement credential validation
     3. 更新追踪矩阵 TF2→✅
     4. 建议关闭 Issue #xx

用户: "关闭版本 v1.5-login"

AI:  1. 检查全部 TF 已关闭
     2. 输出 merge 建议
     3. 提醒更新 worklog
```
