---
name: dm-close-ver
description: 关闭版本时使用：就绪审计、保留历史的 merge（不用 squash）、关闭 TF Issue、清理分支、打 annotated tag 并推送。触发于「关闭版本」。
---

# dm-close-ver

## 概述

版本收尾 skill，独立承接"关闭版本"的完整流程：就绪性审计 → 收尾执行 → 合并与关闭 → 关闭后确认。与 dm-plan-ver 职责分离：**dm-plan-ver 开版本，dm-close-ver 关版本**。

## 职责边界

| 职责 | 归属 |
|------|------|
| 就绪性审计（Issue / 工作包 / 验收 / 工作区 / ODD DoD） | ✅ 本 skill |
| 收尾执行（矩阵核对、worklog 补全、文档收尾） | ✅ 本 skill |
| 保留历史的 merge（`--no-ff`，不用 squash） | ✅ 本 skill |
| 关闭 TF Issue、清理分支、打 annotated tag 并推送 | ✅ 本 skill |
| worklog 补全 | 委托 `dm-log` |
| 文档提交 | 委托 `dm-commit` |
| 版本规划与启动（四件套 / 分支 / PR / Issue） | 委托 `dm-plan-ver` |
| 新功能开发 | ❌ 收尾阶段禁止 |

## 关系

dm-close-ver 是 dm-plan-ver Phase 3（版本收尾）的独立承接者。dm-plan-ver 负责版本规划与启动（四件套、分支、PR、TF Issue）；版本进入收尾阶段后由本 skill 接管。

```
dm-plan-ver (开版本)
  └── Phase 2: TF 开发
        ├── dm-dev-tf (TF 启动)
        └── dm-commit (TF 提交)

dm-close-ver (关版本) ← 独立 skill，接收 dm-plan-ver 交接
```

- **前置条件**：版本分支 `feature/vX.Y-<slug>` 已存在，TF 开发已完成或明确延期
- **委托**：dm-log（worklog 补全）、dm-commit（文档提交）

## 触发

- "关闭版本 v1.2-payment"
- "准备发版 / merge"
- "结束这个版本"
- "close version v1.2"
- dm-plan-ver 收尾阶段的提示调用

## 核心概念

### 四阶段收尾

```
Phase A 就绪性审计 → Phase B 收尾执行 → Phase C 合并与关闭 → Phase D 关闭后确认
```

任一 Phase 不满足 → 先修复再继续，**不跳过**。

### 保留历史的 merge

用 **merge commit**（`--no-ff`）合并版本分支到 main，**不使用 squash**——保留每个 TF commit 的原始历史，便于追溯与回滚。

### annotated tag 是版本锚点

版本标记用 **annotated tag** `v<X.Y.Z>`，message 含 `version` / `scope` / `merge`（回滚点）/ `issues`，且**必须 `git push origin --tags`**——否则远端没有版本锚点。

### 不静默跳过

未完成的 Issue 必须显式标记 `[DEFERRED]` 并备注原因；未被 `Closes` 自动关闭的须手动关闭。禁止静默略过。

### 完成定义

dev 工作包完成 = **代码 + 部署 + 联调**；部署与联调归 dev，qa 只验收「已部署 + 已联调」的功能（见 `docs/02-version-rules.md`）。

## 执行流程

### Phase A：就绪性审计（Can we close?）

```
用户: "关闭版本 v1.3-export"
```

1. **Issue 全查** — 所有 TF Issue 已关闭或明确标记 `[DEFERRED]`
2. **工作包状态核对** — `500-schedule.md` 全部 ✅ 或明确延期
3. **验收追溯** — 每个 TF 是否有可核对的验收结果（对照 `200-spec.md` 标准）
4. **未提交变更** — 检查工作区/暂存区是否干净（`git status`）
5. **可观测性 DoD** — 无裸露日志（关键路径经 `observe` 包装）、无静默吞错、高开销节点（推理/IO/跨进程）有诊断快照（见 `docs/07-observability-driven-dev.md` §7 DoD）

> 任一不满足 → 先修复再继续，不跳过。

### Phase B：收尾执行（Do the close）

6. **执行顺序矩阵核对** — `400-build.md` 固定收尾行（补单测/回归、构建验证）已完成（测试职责分层见 `docs/06-contract-based-dev.md` §3）
7. **worklog 补全** — 版本周期内所有工作已记录（委托 dm-log）
8. **文档收尾** — 版本文档确认提交（委托 dm-commit）

### Phase C：合并与关闭（Merge & close issues）

9. **Merge PR（保留历史）** — 用 **merge commit** 合并版本分支到 main，**不使用 squash**：
   ```bash
   git checkout main
   git merge --no-ff feature/vX.Y-<slug>
   git push origin main
   ```
   - 保留每个 TF commit 的原始历史
   - 若 TF commit 已含 `Closes #id`，合并时由托管平台自动关闭对应 Issue

10. **关闭剩余 TF Issue** — 逐个确认并关闭本版本所有 TF Issue：
   - 已完成：标注验收结果后关闭
   - `[DEFERRED]`：单独备注延期原因后关闭
   - 未被 commit 自动关闭的：手动关闭
   - 关闭后更新追踪矩阵（tracking-matrix）为 ✅

11. **清理分支** — 删除已合并的版本分支：
    ```bash
    git branch -d feature/vX.Y-<slug>
    ```

12. **版本标记**（必做）— 用 **annotated tag** 打版本号，message 须含「版本 + 必要信息」：
    - tag 命名：`v<X.Y.Z>`（与版本目录 `vX.Y-<slug>`、PR `[Vx.y.z]` 一致；`<X.Y>` 取自版本目录，`<Z>` 为补丁号，首个版本为 `.0`）
    - message 必要字段：`version`（含 slug）、`scope`（本次交付范围摘要）、`merge`（merge commit 哈希，作回滚点）、`issues`（关闭的 TF Issue 清单）
    ```bash
    git tag -a v<X.Y.Z> -m "$(cat <<'EOF'
    version: vX.Y.Z (slug: <slug>)
    scope: <交付范围一句话摘要>
    merge: <merge commit 哈希>
    issues: #<id1> #<id2> ...
    EOF
    )"
    git push origin --tags
    ```
    - 若版本目录未提供 `<Z>`（补丁号），默认 `.0`；若用户要求其他补丁号，沿用其指定
    - tag 必须推送（`--tags`），否则远端无版本锚点

13. **追踪矩阵归档** — 更新/归档 tracking-matrix

### Phase D：关闭后确认（Post-close verify）

14. **依赖本版本的上游** — 确认 main 上无残留分支引用
15. **roadmap 更新** — 标记该版本已交付，推进下一步
16. **回滚预案确认** — 记录已知回滚点（merge commit 哈希）

## 常见失误排查（Troubleshooting）

版本收尾中常见失败场景与处理：

| 场景 | 识别信号 | 处理 |
|------|----------|------|
| **Issue 漏关** | 版本合并后仍有 open TF Issue | 逐个核对 → 关闭或标记 `[DEFERRED]` |
| **分支未删** | `git branch` 显示已合并分支残留 | `git branch -d <branch>` 清理 |
| **merge 冲突** | merge 时 conflict 报错 | 手动解决冲突 → `git add` → `git merge --continue`；保留双方历史 |
| **验收不可追溯** | `200-spec.md` 验收项无对应结果 | 补验收记录或明确标记遗留 |
| **worklog 缺失** | 版本周期无记录 | 委托 dm-log 补全后再归档 |
| **commit 未关联 Issue** | 历史 commit 无 `Refs`/`Closes` footer | 记录到关闭报告中，人工补关联（不改写历史） |
| **误用 squash** | 合并后 TF 历史被压平 | 确认分支已推送后，用 merge commit 方式重建或记录回滚点 |
| **遗留引用** | main 上仍有指向版本分支的引用 | 修正文档/配置，更新 roadmap |
| **ODD DoD 未达标** | 关键路径有裸露 print / 静默吞错 / 高开销节点无诊断快照 | 补 `observe` 结构化诊断（07 §2.1/§3/§4），`#if DEBUG` 隔离 |
| **tag 未推送** | `git tag` 本地有但 `git ls-remote --tags` 无 | `git push origin --tags` 补推；tag 是版本锚点，不可遗漏 |

## 关键规则速查

| 规则 | 来源 |
|------|------|
| 合并使用 merge commit（`--no-ff`），**保留历史，不使用 squash** | 03-git-flow-rules §4.2（本 skill 覆盖默认 squash） |
| 每个 TF commit 带 `Closes #id`，合并时自动关 Issue | 03-git-flow-rules §2.3 |
| 未关闭 Issue 必须明确 `[DEFERRED]`，不可静默跳过 | 03-git-flow-rules §2.3 |
| 验收结果需可追溯 | 02-version-rules |
| 收尾阶段禁止新功能 commit | — |
| 合并后删除已合并分支 | 03-git-flow-rules §9 |
| 关闭版本后更新 roadmap | 01-project-dev-flow |
| 版本标记用 annotated tag `v<X.Y.Z>`，message 含 version/scope/merge/issues，必推送 `--tags` | 本 skill §11 |
| 合并前须过 ODD DoD：无裸露日志 / 无静默吞错 / 高开销节点有诊断快照（07 §7） | docs/07-observability-driven-dev.md §7 |

## 输出

- **关闭报告**：版本 → 交付范围 → 验收摘要 → 关闭的 Issue 清单 → 遗留项（deferred）→ 回滚点（merge commit 哈希）

## Skill 资源映射

| 资源 | 来源 | 用途 |
|------|------|------|
| SKILL.md | — | 上述收尾流程指令 + 规则速查 |
| references/version-rules.md | `docs/02-version-rules.md` | 四件套验收结构 |
| references/git-flow-rules.md | `docs/03-git-flow-rules.md` | Issue/PR/merge 规则详情 |
| dm-plan-ver references/git-flow-rules.md | `docs/03-git-flow-rules.md` | 追踪矩阵、分支清理 |

## 使用示例

```
用户: "关闭版本 v1.5-login"

AI:  1. 就绪性审计:
        - Issue #21 [TF1] 登录表单 → closed ✅
        - Issue #22 [TF2] 验证流程 → closed ✅
        - 500-schedule.md 全部 ✅
        - git status 干净
     2. 收尾执行: 400-build 收尾行已完成, worklog 已补全
     3. 合并(保留历史):
        git checkout main
        git merge --no-ff feature/v1.5-login
        git push origin main
     4. 关闭 TF Issue: 确认 #21/#22 已自动关闭(Closes footer)
     5. 清理分支: git branch -d feature/v1.5-login
     6. 打版本 tag:
        git tag -a v1.5.0 -m "version: v1.5.0 (slug: login)
        scope: 登录表单 + 验证流程
        merge: <merge commit 哈希>
        issues: #21 #22"
        git push origin --tags
     7. 输出关闭报告
```
