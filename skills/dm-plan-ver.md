# dm-plan-ver

## 概述

版本规划与生命周期 skill，负责版本级规划：创建版本文档四件套（100-schedule / 200-spec / 300-design / 400-build）、分支、PR、TF Issue 生成、追踪验收。逐 TF 开发由 dm-dev-tf 负责；提交格式由 dm-commit 负责。

## 触发

- "新建版本 v1.2-payment"
- "开始 vX.Y"
- "创建 TF 文档"
- "关闭版本 v1.2"

## 执行流程

### 阶段 1：版本启动

```
用户: "新建版本 v1.3-export"
```

1. **创建版本文档** `docs/versions/v1.3-export/`
   - `100-schedule.md` — 工作包列表与执行顺序
   - `200-spec.md` — TF 目标与验收
   - `300-design.md` — TF 划分、数据流、关键决策、跨 TF 状态机
   - `400-build.md` — 流内步骤、函数签名、Schema、状态机/时序图 + **任务执行计划（§末尾）**
     - 按 `300-design.md` §3 的 TF 执行顺序排列任务行
     - 末尾追加固定行："补单测与回归用例" + "本地构建与回归验证"
     - 填写执行顺序说明（先做、可并行、必须串行）

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

### 阶段 2：TF 开发

TF 开发通过两个子 skill 串联：

- **dm-dev-tf** — TF 启动：读文档、确认 Issue、建分支、出开发概要
- **dm-commit** — TF 提交：`type(scope): subject` + `Closes #id`

```
用户: "TF1 完成了"
```

1. **确认验收**：对照 `200-spec.md` 中该 TF 的验收标准
2. **执行 commit** — 委托 dm-commit skill，格式：
   ```text
   feat(export): collect and preprocess data for PDF export
   
   Closes #42
   ```
3. **关闭 TF Issue**（标记验收结果）
4. **更新 400-build.md** 执行计划

### 阶段 3：版本收尾

```
用户: "关闭版本 v1.3-export"
```

1. 确认所有 TF Issue 已关闭或明确延期
2. 补齐 `400-build.md` 执行计划验收结果
3. 提交 worklog 记录
4. Merge PR (squash merge)
5. 提交版本文档（如尚未提交） — 委托 dm-commit

## 关键规则速查

| 规则 | 来源 |
|------|------|
| TF 编号需稳定，废弃 TF 保留编号标 `[DEPRECATED]` | 02-version-rules.md §3.1 |
| design 管 TF 级，build 管步骤级 | 02-version-rules.md §3.3 |
| 跨 TF 状态机放 300-design，单 TF 状态机放 400-build | 02-version-rules.md §3.4 |
| 每版本 1 PR，每 TF 1 Issue | 03-git-flow-rules.md §2 |
| commit: `type(scope): subject` + `Closes #id`，详见 dm-commit | 03-git-flow-rules.md §3 |
| 分支: `feature/<version>-<tf>-<topic>` | 03-git-flow-rules.md §4 |
| 合并: 默认 squash merge | 03-git-flow-rules.md §4.2 |

## Skill 资源映射

| 资源 | 来源 | 用途 |
|------|------|------|
| SKILL.md | — | 上述全流程指令 + 关键规则速查 |
| references/version-rules.md | `docs/02-version-rules.md` | 四件套规则详情 |
| references/git-flow-rules.md | `docs/03-git-flow-rules.md` | PR/Issue/commit 规则详情 |
| assets/200-spec.md | `templates/versions/vX.Y-<slug>/200-spec.md` | 规格模板 |
| assets/300-design.md | `templates/versions/vX.Y-<slug>/300-design.md` | 设计模板 |
| assets/400-build.md | `templates/versions/vX.Y-<slug>/400-build.md` | 实现蓝图 + 执行计划模板 |
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
