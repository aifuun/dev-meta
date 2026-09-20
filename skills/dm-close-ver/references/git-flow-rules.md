# Git Flow Rules

## 1. 目标与适用范围

- 目标：统一单人开发下的版本交付、追踪与变更管理。
- 适用范围：本仓库全部版本迭代（版本 + **Step 0–7** 施工流，见 `docs/02-version-rules.md`）。

## 2. 核心工作流（必须）

### 2.1 每个小版本开 1 个 PR

- PR 命名：`[Vx.y.z] <short-title>`
- PR 必填：目标、范围、验收入口、风险与回滚。

### 2.2 每个版本开 1 个 Issue

- Issue 命名：`[vX.Y] <feature-name>`
- Issue 必填：目标、完成标准、依赖、验收方法。
- **Step 0–7 作为该 Issue 内的 checklist**（`- [ ] S0 Scaffold & Clean` …），
  **不单独为每个 Step 开 Issue** —— 版本已收敛为单一业务场景，Issue 表达交付物而非工序。

### 2.3 关联规则

- 每个 commit 必须关联对应版本 Issue（`Refs #id` / `Closes #id`）。
- 版本 Issue 必须关联版本 PR。
- 版本 PR 合并前必须确认版本 Issue 已关闭或明确延期。

> **Micro-Batching（AI 执行粒度）**：一个 Step 内的改动按 `docs/08-small-batch-iteration.md` 拆为三 Batch（契约/数据模型 → Core 单文件 → UI/调用点），每个绿灯 Batch 各生成一个 commit，**多个小 commit 均可 `Refs #同一 Issue`**。若下个 Batch 陷入混乱，由**用户显式**执行 `git reset --hard <上一个绿灯 commit>` 退回（破坏性操作，AI 不自发，遵守 git 安全协议与「AI 不主动 commit」护栏），随后 New Session 携带最新契约 SSOT 继续。

## 3. Commit Message 规范

### 3.1 最小强制格式

```text
type(scope): subject
```

### 3.2 推荐完整格式

```text
<type>(<scope>): <subject>

<body>

<footer>
```

### 3.3 type 集合

- `feat`：新功能
- `fix`：缺陷修复
- `docs`：文档变更
- `refactor`：重构（不改变外部行为）
- `test`：测试相关
- `chore`：构建、依赖、工具链维护
- `perf`：性能优化（可选）
- `ci`：CI/CD 变更（可选）

### 3.4 编写规则

- `subject` 描述“做了什么”，避免空泛表述。
- `subject` 建议不超过 50 个字符。
- **Step 关联**：commit 属于某个 Step 时，`subject` 末尾加 `(S<n>)` —— 如
  `feat(render): extract union path logic (S2)`。合法形式正则：`/\(S[0-7]\)$/`。
  **跳过（`⏭️ SKIPPED`）的 Step 不产生 commit**。
- `body` 用于说明原因、影响与迁移信息。
- `footer` 用于 issue 关联与破坏性变更说明。

## 4. 分支与合并规则

### 4.1 分支命名

- 分支为**版本级**：每个版本 1 个长期分支，**Step 不单独建分支**（开发直接在版本分支上进行）。
- `feature/v<version>-<slug>`：功能版本（slug 取自版本目录名 `v<version>-<slug>`）
- `fix/v<version>-<slug>`：修复版本
- `docs/v<version>-<slug>`：纯文档版本

### 4.2 合并策略

- 默认使用 **merge commit（`git merge --no-ff`）保留历史 commit**，不使用 squash。
- 合并后版本 Issue 由 `Closes #id` footer 自动关闭，其余手动关闭。
- 合并前执行最小自检：范围正确、链接完整、验收可追溯。
- 版本收尾的完整流程由 `dm-close-ver` 执行。

## 5. PR 模板（最小字段）

- 改了什么
- 为什么改
- 如何验证
- 风险与回滚

## 6. Issue 模板（版本级）

- 版本号与名称
- 目标与完成标准
- 依赖关系
- **Step 0–7 checklist**（`- [ ] S0 Scaffold & Clean` … `- [ ] S7 Verification & Close`）
- 验收记录

## 7. 追踪矩阵（版本级）

行以 **Step** 为单位（Issue / PR 列填该版本唯一的那一个）：

| Step | Issue | PR | 验收结果 |
|---|---|---|---|
| S0 Scaffold & Clean | # | # |  |
| S1 Contract & ADR | # | # |  |

## 8. 例外与豁免

- 极小文档修正可不单独建版本 Issue（需在版本 PR 记录）。
- 无行为变化的小改动可省略 commit body/footer。
- 紧急修复可先修复后补齐 issue/PR 记录。

## 9. 周期性维护

- 每周巡检：未关闭 issue、未关联 PR、长期分支、漂移文档。
- 版本收尾：补齐验收结果，关闭或延期未完成的 Step。

## 10. 附录

### 10.1 commit 示例

```text
docs(git-flow): add minimal workflow rules
```

```text
fix(storage): fallback to memory when indexeddb is unavailable

Keep playback flow non-blocking when openDB fails.

Closes #42
```

### 10.2 版本 Issue 示例（标题）

```text
[v30] 主 App 闭环（MainView + MainViewModel）
```

### 10.3 版本 PR 示例（标题）

```text
[V1.4.1] IndexedDB prefs delivery
```
