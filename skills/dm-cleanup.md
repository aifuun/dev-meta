---
name: dm-cleanup
description: 版本/TF 之外的跨文件技术债清理与仓库卫生（死代码、注释、.gitignore、误提交文件）。触发于「清理技术债」「做仓库卫生」。
---

# dm-cleanup

## 概述

技术债清理与仓库卫生 skill。收口**版本 / TF 之外**的跨文件清理工作：按优先级分层扫描代码与仓库，显式收敛关键决策，逐处修复并验证，最终路由至版本收尾。以 PochiHide `VisionDetector.swift` 清理为范式。

## 职责边界

| 职责 | 归属 |
|------|------|
| 优先级分层扫描 + 列出发现项与优先级 | ✅ 本 skill |
| 逐处修复（正确性 / 注释 / 死代码 / 重复结构 / 占位常量标注） | ✅ 本 skill |
| 仓库卫生（`.gitignore` 补规则 + 误提交文件 `git rm --cached`） | ✅ 本 skill |
| 验证（lint 0 错误 + 相关测试通过） | ✅ 本 skill |
| 版本收尾（merge / 关 Issue / 清理分支 / 提交推送） | 委托 dm-close-ver |

> **分流规则**：本 skill 只管**无法归到某版本 TF** 的 standalone 清理（一次性技术债、跨文件重构、仓库卫生）。若清理内容能明确归到某版本 TF，则提示走 `dm-dev-tf`，本 skill 不接管其开发流程，避免与 TF 链路重叠。

## 触发

- `/dm-cleanup`
- "清理技术债"
- "做一下仓库卫生"
- "重构清理 + gitignore 整理"

> 显式触发为主，不走自然语言自动匹配，避免与其他 skill 抢触发。

## 核心概念

### 优先级分层

扫描时按影响面与风险分级，先高后低逐处处理：

| 级别 | 关注点 | 典型动作 |
|------|--------|---------|
| 🔴 高 | 正确性 bug（被测函数未被调用、坐标越界、翻转回归） | 让纯函数真正被调用、输出套夹取、补回归断言 |
| 🟡 中 | 过时注释、占位常量语义模糊、仓库卫生（误提交文件 / .gitignore 缺失） | 注释对齐 ADR、标注占位常量启用状态、`git rm --cached` + 补 ignore |
| 🟢 低 | 测试 / 结构重复 | 抽辅助函数、统一调用风格、重命名误导性方法名 |

### 决策收敛 §7

高风险决策点须走 skill-doc-principles §7「AI 提问 → 用户回答 → 沉淀」三步，不依赖 AI 自答。本 skill 必收敛的两类：

- **误提交文件**：用 `git rm --cached`（保留本地物理文件）使其被忽略，还是直接删除物理文件？删物理文件有损，必须先问用户。
- **占位常量启用与否**：占位常量（如 `appGroupID` / `defaultStickerKey`）当前是否启用？未启用的须在代码中显式标注，避免读者误判为已生效；是否触发 `dm-adr` 由用户决定，本 skill 不自动记录。

### 复用已有纯函数

清理时优先复用代码中已存在、且已有测试的纯函数（如 `flipYToUIKit`、`clampedNormalized`），不另写重复逻辑。判断标准：**被测且应被用**——若某纯函数已被测试覆盖却未在主干路径调用，应让其真正生效，而非再抄一份公式。

### 单一权威 + 自动部署

- 本中文源 `skills/dm-cleanup.md` 是**唯一权威**（含 YAML frontmatter）。
- 部署版 `~/.codebuddy/skills/dm-cleanup/SKILL.md` **由本源自动生成**，禁止手工编辑；修改后执行 `python3 pub_local.py --deploy` 生效（见 `skill-doc-principles.md` §5）。

## 执行流程

### 1. 接收与分流判定

读取用户的清理诉求；判断是否属于**版本 / TF 之外**的 standalone 清理（是 → 本 skill；若可归某 TF → 提示走 `dm-dev-tf`）。

### 2. 优先级扫描

通读目标文件 / 仓库，按「优先级分层」列出发现项（级别 + 文件 + 问题 + 预期修复），形成扫描清单。仓库卫生项单独标注（`.gitignore` 现状、是否已有误提交文件被跟踪）。测试相关发现项的「期望行为」判定，参考 `docs/06-contract-based-dev.md` §3（测试职责分层）中 build 层的行为契约口径。

### 3. 决策收敛

对高风险项（误提交文件删不删物理文件、占位常量启用与否）显式提问，收集回答并就地应用，**不自行假设**。

### 4. 按优先级逐处修复

- 🔴 高：让纯函数真正被调用、输出套夹取、补回归断言。
- 🟡 中：注释对齐 ADR、标注占位常量状态、`git rm --cached` 保留本地 + 补 `.gitignore`。
- 🟢 低：抽辅助函数、统一风格、重命名误导性方法名。

### 5. 验证

> **契约式开发核心（详见 `docs/06-contract-based-dev.md`，即使链接失效也以本句为准）**：
> ① 先契约后实现；② L1 接口契约含错误/幂等/兼容/限流，L2 TF 契约含失败语义/前置后置/依赖方向，L3 行为契约仅算法类必填（given-when-then）；③ 测试三层分工 design=场景 / build=行为契约 / dev-tf=落地，互不重定义；④ 契约质量基线要求错误透明、命名即契约、不可变默认、显式边界校验；⑤ 下层契约不得违背上层。

- lint 0 错误。
- 相关测试通过（如 iOS：`xcodebuild test`，确认重构未破坏行为，尤其坐标范围断言）。
- 隐性契约债扫描：清理时若发现空 `catch` 吞错误、魔术数字冒充契约、未标注幂等 / 不变量、或「静默危险失败 / 依赖返回值兜底」等，标注为「隐性契约债」并记入扫描清单（契约质量基线见 `docs/06-contract-based-dev.md` §2.5；失败面契约见 §2.7）。特别地，「静默吞错 / 空 catch / 裸露 print / 依赖返回值兜底」属可观测性债（ODD），清理时须按 `docs/07-observability-driven-dev.md` §2.1 / §3 补 `observe` 结构化诊断（含 Input Snapshot / Resource Metrics，`#if DEBUG` 隔离），使 AI 能一次定位。

### 6. 仓库卫生收尾

- `.gitignore` 追加规则（如 `generated-images/`、`*.xcsettings` 误提交项）。
- 对已误提交文件：`git rm --cached <path>`（保留物理文件），使其后续被忽略；未跟踪项加 ignore 后即不再污染 status，无需删除。

### 7. 路由

清理完成并验证通过后，委托 `dm-close-ver` 进行版本收尾（merge / 关 Issue / 清理分支 / 提交推送）；若本次清理本身不挂版本，由 `dm-close-ver` 决定如何落盘。

## 关键规则速查

| 规则 | 来源 |
|------|------|
| 只管版本 / TF 之外的 standalone 清理；可归 TF 的走 dm-dev-tf | 职责边界 |
| 显式触发 `/dm-cleanup`，不自动匹配 | 触发 |
| 优先级 高→中→低 逐处处理 | 核心概念·优先级分层 |
| 误提交文件删物理文件前必须显式提问 | skill-doc-principles §7 |
| 占位常量启用状态须显式标注，不自动记 ADR | skill-doc-principles §7 |
| 优先复用已有纯函数，不另写重复逻辑 | 核心概念·复用纯函数 |
| 验证门槛：lint 0 + 相关测试通过 才路由收尾 | 执行流程·验证 |
| 部署版 SKILL.md 由中文源自动生成，禁止手改 | 核心概念·单一权威 + 自动部署 |
| 契约须标注四要素（归属/方向/不变性/真值来源）+ 域-序号编号；质量维度作为不变性项落地 | docs/06-contract-based-dev.md §2.6 |
| 失败面契约：纯函数式失败返回空/原值而非 nil；严禁静默危险失败，须调用前拦截显式暴露 | docs/06-contract-based-dev.md §2.7 |
| 契约演进治理：破坏性变更走 dm-adr；纯增量 PR 标注；新接口回写总目录（无主防护） | docs/06-contract-based-dev.md §5 |
| 可观测性债：静默吞错 / 空 catch / 裸露 print / 依赖返回值兜底 = 隐性契约债，清理时须按 07 §2.1/§3 补 observe 结构化诊断 | docs/07-observability-driven-dev.md |

## 产出与完成判据

**产出**：

- 清理后的代码 / 文档（无功能变更）
- 清理报告：改了什么、为什么、遗留项

**完成判据**：

- [ ] **lint 0 且相关测试通过**（未通过不路由收尾）
- [ ] 死代码 / 过期注释 / 重复结构已删，且**未改变既有行为**
- [ ] 误提交文件已 `git rm --cached`（需先显式提问确认）
- [ ] 占位常量是否启用已显式标注
- [ ] 隐性契约债（静默吞错 / 裸露 print）已按 `docs/07` 补 `observe` 结构化诊断
- [ ] 若清理涉及版本收尾，已委托 `dm-close-ver`

## 资源映射

| 资源 | 来源 | 用途 |
|------|------|------|
| `skills/dm-cleanup.md` | — | 中文源（唯一权威，含 frontmatter） |
| `~/.codebuddy/skills/dm-cleanup/SKILL.md` | — | 部署版（由中文源自动生成，勿手改） |

> 本 skill 无需额外 assets 模板，保持轻量（与 `dm-grillme-plan` 形态一致）。

## 使用示例

```
用户: "/dm-cleanup 把 VisionDetector.swift 和仓库卫生一起清理了"

AI:  1. 分流判定：standalone 清理（非某 TF）→ 本 skill
     2. 优先级扫描清单：
        🔴 [VisionDetector.swift] detect 手写翻转未复用 flipYToUIKit → 改调纯函数
        🔴 [VisionDetector.swift] clampedNormalized 被测却未用 → detect 输出套夹取 [0,1]
        🟡 [3 处注释] <15MB / .fast 默认 与代码矛盾 → 对齐 ADR-001 / ADR-004
        🟡 [SharedConfig] 占位常量语义模糊 → 标注 appGroupID/defaultStickerKey 未启用、downsampleMaxDimension 已启用
        🟡 [仓库卫生] WorkspaceSettings.xcsettings 误提交 + generated-images/ 未 ignore
        🟢 [测试] warm-up 重复 → 抽 detectSteadyState；testPeakMemoryUnder15MB 实为 30MB 稳态 → 重命名 testSteadyStateMemoryUnderLimit
     3. 决策收敛：
        Q 误提交的 WorkspaceSettings.xcsettings 要保留本地文件还是删物理文件？
        → 用户：保留本地，只从 git 移除
        Q 占位常量当前是否启用？
        → 用户：appGroupID/defaultStickerKey 未启用（标注），downsampleMaxDimension 已启用
     4. 按优先级逐处修复
     5. 验证：lint 0 错误；xcodebuild test 6 用例 5 passed + 1 skipped + 0 failures
     6. 仓库卫生：.gitignore 加 generated-images/ + *.xcsettings；git rm --cached WorkspaceSettings.xcsettings（本地保留）
     7. 路由：委托 dm-close-ver 收尾
```
