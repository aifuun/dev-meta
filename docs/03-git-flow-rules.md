# Git Flow Rules

## 1. 目标与适用范围

- 目标：统一单人开发下的版本交付、追踪与变更管理。
- 适用范围：本仓库全部版本迭代（基于 Transaction Flow）。

## 2. 核心工作流（必须）

### 2.1 每个小版本开 1 个 PR

- PR 命名：`[Vx.y.z] <short-title>`
- PR 必填：目标、范围、验收入口、风险与回滚。

### 2.2 每个 TF 开 1 个 Issue

- Issue 命名：`[TFx] <flow-name>`
- Issue 必填：目标、完成标准、依赖、验收方法。

### 2.3 关联规则

- 每个 commit 必须关联对应 TF issue（`Refs #id` / `Closes #id`）。
- 每个 TF issue 必须关联版本 PR。
- 版本 PR 合并前必须确认所有 TF issue 已关闭或明确延期。

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
- `body` 用于说明原因、影响与迁移信息。
- `footer` 用于 issue 关联与破坏性变更说明。

## 4. 分支与合并规则

### 4.1 分支命名

- 分支为**版本级**：每个版本 1 个长期分支，**TF 不单独建分支**（开发直接在版本分支上进行）。
- `feature/v<version>-<slug>`：功能版本（slug 取自版本目录名 `v<version>-<slug>`）
- `fix/v<version>-<slug>`：修复版本
- `docs/v<version>-<slug>`：纯文档版本

### 4.2 合并策略

- 默认使用 **merge commit（`git merge --no-ff`）保留历史 commit**，不使用 squash。
- 合并后相关 TF issue 由 `Closes #id` footer 自动关闭，其余手动关闭。
- 合并前执行最小自检：范围正确、链接完整、验收可追溯。
- 版本收尾的完整流程由 `dm-close-ver` 执行。

## 5. PR 模板（最小字段）

- 改了什么
- 为什么改
- 如何验证
- 风险与回滚

## 6. Issue 模板（TF 专用）

- TF 编号与名称
- 目标与完成标准
- 依赖关系
- 验收记录

## 7. 追踪矩阵（版本级）

| TF | Issue | PR | 验收结果 |
|---|---|---|---|
| TF1 | # | # |  |
| TF2 | # | # |  |

## 8. 例外与豁免

- 极小文档修正可不单独建 TF issue（需在版本 PR 记录）。
- 无行为变化的小改动可省略 commit body/footer。
- 紧急修复可先修复后补齐 issue/PR 记录。

## 9. 周期性维护

- 每周巡检：未关闭 issue、未关联 PR、长期分支、漂移文档。
- 版本收尾：补齐验收结果，关闭或延期未完成 TF。

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

### 10.2 TF Issue 示例（标题）

```text
[TF2] 定时刷写播放进度
```

### 10.3 版本 PR 示例（标题）

```text
[V1.4.1] IndexedDB prefs delivery
```
