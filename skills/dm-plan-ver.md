# dm-plan-ver

## 概述

版本启动 skill，负责版本级规划与启动：创建版本文档四件套（500-schedule / 200-spec / 300-design / 400-build）、分支、PR、TF Issue 生成。逐 TF 开发由 dm-dev-tf 负责；提交格式由 dm-commit 负责；版本收尾由 dm-close-ver 负责。

## 触发

- "新建版本 v1.2-payment"
- "开始 vX.Y"
- "创建 TF 文档"

## 执行流程

### 阶段 1：版本启动

```
用户: "新建版本 v1.3-export"
```

1. **创建版本文档** `docs/versions/v1.3-export/`
   - `500-schedule.md` — 工作包列表与执行顺序
   - `200-spec.md` — TF 目标与验收
   - `300-design.md` — TF 划分、数据流、关键决策、跨 TF 状态机
   - `400-build.md` — 流内步骤、函数签名、Schema、状态机/时序图 + **执行顺序矩阵（§末尾）**
     - 按 `300-design.md` §3 的 TF 执行顺序排列矩阵行
     - 每行标注**环节**（开发/部署/联调/测试/发布），使环节顺序与 schedule 对齐
     - 末尾追加固定行："补单测与回归用例" + "本地构建与回归验证"
     - 填写执行顺序说明（先做、可并行、必须串行）
     - dev TF 的矩阵行须含「代码 + 部署 + 联调」环节（部署/联调归 dev，不归 qa）
     - 任务简述、预估工时、状态由 `500-schedule.md` 承载，不在矩阵重复

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

- **dm-dev-tf** — TF 启动：读文档、确认/创建 Issue、出开发概要（开发在版本分支上，不建分支）
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
4. **更新 500-schedule.md** 工作包状态 + tracking-matrix

### 阶段 3：版本收尾（委托 dm-close-ver）

```
用户: "关闭版本 v1.3-export"
```

用户要求关闭版本时，委托 **dm-close-ver**。本 skill 不再处理收尾；dm-close-ver 拥有完整流程（就绪审计 → 收尾执行 → 保留历史的 merge → 关闭 TF Issue → 清理分支 → 关闭后确认）。

## 关键规则速查

| 规则 | 来源 |
|------|------|
| TF 编号需稳定，废弃 TF 保留编号标 `[DEPRECATED]` | 02-version-rules.md §3.1 |
| design 管 TF 级，build 管步骤级 | 02-version-rules.md §3.3 |
| 跨 TF 状态机放 300-design，单 TF 状态机放 400-build | 02-version-rules.md §3.4 |
| 每版本 1 PR，每 TF 1 Issue | 03-git-flow-rules.md §2 |
| commit: `type(scope): subject` + `Closes #id`，详见 dm-commit | 03-git-flow-rules.md §3 |
| 分支: `feature/<version>-<tf>-<topic>` | 03-git-flow-rules.md §4 |
| 收尾: 委托 dm-close-ver（保留历史 merge，不用 squash） | dm-close-ver.md |
| 执行顺序矩阵行含环节；dev TF 含代码+部署+联调（部署/联调归 dev） | 02-version-rules.md §2.2 |

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

AI:  委托 dm-close-ver 处理版本收尾（就绪审计 → merge 保留历史 → 关闭 TF Issue → 清理分支 → 关闭报告）
```
