---
name: dm-contract-gate
description: 契约断言门禁：改前 diff 契约、改后跑门禁（sha256 + contract_verified）、交付前对齐 MANIFEST。触发于改代码前后与「跑契约门禁」。
---

# dm-contract-gate

## 概述

契约断言门禁 skill，是 `docs/06-contract-based-dev.md` §8 的执行入口。在「改代码前 / 改代码后 / 提 commit 打包」三道关键卡口强制校验契约——AI 改逻辑前先 diff 契约、改完先跑门禁、交付前对齐 MANIFEST 指纹，门禁没绿不准向用户交付，报错原样抛回自我修复。项目采用文档式契约时，**Gate 2 另跑结构 lint**（`docs/06` §8.4 / `samples/contract-lint/`）。

## 职责边界

| 职责 | 归属 |
|------|------|
| 改前 diff 契约、判定是否破坏契约 | ✅ 本 skill |
| 改后 / 交付前跑门禁脚本（sha256 + contract_verified + 编译/类型校验） | ✅ 本 skill |
| 门禁失败 → 报错原样抛回、契约框架内自我修复 | ✅ 本 skill |
| 契约需破坏性变更（改语义/签名/坐标口径） | 委托 `dm-adr`（06 §9） |
| 契约纯增量追加 + 回写编号 | 委托用户 PR 标注（06 §9），本 skill 仅提示 |
| 落地实现代码 | 委托 `dm-dev-step`（本 skill 只守门禁，不写业务） |

## 触发

- 用户指令「帮我改 X 功能」「修复 Y Bug」「实现 Z」→ **Gate 1 改前卡口**
- AI 完成多文件修改、准备告知「改好了」之前 → **Gate 2 改后卡口**（自动，不待用户触发）
- 用户指令「提交代码」「打包 dist/」「commit」或调用 `dm-commit` → **Gate 3 交付卡口**
- 用户显式说「跑契约门禁」「校验契约」「contract gate」

## 核心概念

### 契约只读（Schema & Interface First）

契约文件是单源真理（SSOT），须为可 parse 形式（`Contract.swift` / `JSON Schema` / `OpenAPI` / `Protobuf` / Swift `Protocol` / `400-build.md` 行为契约表）。AI 改实现前先 diff 契约，确认不破坏既有不变性；**严禁 AI 自行改写契约本身**。

### 三道卡口

- **Gate 1 改前**：写第一行业务代码前，读取并 diff 契约，确认不破坏公开契约；若触及契约，先向用户提出申请、获许可才继续。不看契约，不准动代码。
- **Gate 2 改后**：准备交付前静默跑本地门禁（`xcrun swiftc -parse` / `python3 package_dist.py --verify` / `MANIFEST` 哈希校验 / JSON Schema 校验）。**没绿绝不向用户邀功**——拦截输出，把终端报错原样抛回自身，在契约框架内修复到门禁变绿。
- **Gate 2 双门禁**：**结构 lint**（校验契约**文档**形态：零死链 / 一条一标 / 锚点唯一 / 不引下游，见 `docs/06` §8.4）+ **产物断言门禁**（校验契约对应**产物**语义：编译 / Schema / sha256 / `contract_verified`，见 `docs/06` §8）。二者互补、**不可互替**；文档式契约的项目，lint 未绿同样不得交付。
- **Gate 3 交付**：commit / 打包前校验 `MANIFEST.json` 文件清单、`sha256` 指纹、`contract_verified` 状态全部对齐；未对齐即报错抛回，禁止带病合并。

### SHA256 + contract_verified 范式

门禁产物 `MANIFEST.json` 含每个文件的 `sha256` 与顶层 `contract_verified` 布尔；`--verify` 失败即非 0 退出，供 CI / git hook / AI 抛回。范式实现见 `samples/contract-gate/verify_contract.py`，对齐 `package_dist.py` 实践。

## 执行流程

### 1. 定位契约 SSOT 文件

按项目识别契约载体：

| 契约类型 | 典型文件 |
|----------|----------|
| Swift 契约门面 | `DetectorContract.swift` / `Contract.swift` / 公开 `Protocol` |
| Schema 契约 | `*.schema.json` / `docs/03_CONTRACTS_AND_API.md` §3 内联 JSON Schema |
| API 契约 | `OpenAPI`（`openapi.yaml`）/ `docs/03_CONTRACTS_AND_API.md` §2 |
| 版本行为契约 | `docs/versions/vX.Y-<slug>/400-build.md` §1.x（Schema / API / 异常 / 防腐）+ §3 各 Step 明细内的「关键行为契约」小节 |
| 设计令牌（视觉契约） | `*.tokens.json`（W3C DTCG 规范形态）/ `tokens.ts` / `theme.css`（项目可扩展）；三层规范见 `docs/09` §7，项目取值见 `docs/04_UI_UX_DESIGN.md` §3.1 |

### 2. Gate 1 改前卡口（Pre-Implementation）

- 读取契约文件，与本次需求做 diff 判定：改动是否触及契约不变性（签名 / 字段 / 坐标口径 / 失败面行为）。
- 未触及 → 允许继续实现。
- 触及但属纯增量（新增接口 / 新域）→ 提示用户在 PR 标注「纯增量」并回写编号（06 §9）。
- 触及且破坏语义 → **暂停**，走 `dm-adr` 申请破坏性变更，获批准并调用方适配后再继续。

### 3. Gate 2 改后卡口（Post-Implementation）

- AI 完成修改、准备输出前，**静默**运行门禁（见资源映射），**双门禁并行**：

| 门禁 | 校验对象 | 命令（示例） |
|------|----------|--------------|
| **结构 lint** | 契约**文档**形态（`docs/06` §8.4 四查） | `python3 contract_lint.py --contracts-dir docs/contracts` |
| **产物断言** | 契约对应的**产物**语义（`docs/06` §8） | `xcrun swiftc -parse` / `package_dist.py --verify` / `MANIFEST` 校验 |

- 通过 → 将 `contract_verified` 置 `true`，继续向用户交付。
- 失败 → **绝对不邀功**，捕获终端报错，原样抛回自身，定位漏改点，在契约框架内补丁修复；回到本步重跑，直到门禁变绿。
- **不可互替**：lint 绿 ≠ 契约语义正确；产物门禁绿 ≠ 文档无死链 —— 两项都要跑。

### 4. Gate 3 交付卡口（Delivery）

- 用户「提交 / 打包」时，触发最终门禁：校验 `MANIFEST.json` 的文件列表、`sha256`、与 `contract_verified` 是否一致。
- 不一致 → 报错抛回，禁止 `dm-commit` 通过；一致 → 放行交付。

### 5. 结构化诊断（失败时）

门禁失败时按 `docs/07-observability-driven-dev.md` §3.1 输出黑匣子快照：含契约快照（`Input Snapshot` = 当前契约 SSOT 摘录）+ 不一致 diff + 资源/命令上下文，便于 AI 一次定位（呼应 07 §2.1/§2.3）。

## 关键规则速查

| 规则 | 来源 |
|------|------|
| 契约文件只读，AI 严禁自改；破坏须走 dm-adr，纯增量须 PR 标注 | docs/06 §8 / §9 |
| Gate 1：改前先 diff 契约，不看契约不准动代码 | docs/06 §8 |
| Gate 2：改后门禁没绿绝不向用户邀功，报错原样抛回自我修复 | docs/06 §8 |
| Gate 3：交付前对齐 MANIFEST 指纹 + contract_verified，未对齐不合并 | docs/06 §8 |
| 机器可校验优先：关键契约须可 parse（JSON Schema/Contract.swift/OpenAPI） | docs/06 §8 |
| 门禁失败须结构化诊断（07 黑匣子） | docs/07 §6 / §3.1 |
| Gate 2 含可观测性 DoD：改后无 observe 包装 / 无出口 Assert（映射空须 assertionFailure）视为门禁未过 | docs/07 §2.5 |
| Gate 2 含轨迹项（启用时）：观测点无判别量 / 轨迹验证只在单测层完成 → 视为未过 | docs/07 §3.2 |
| 可观测性 DoD 已由 `verify_contract.py --source-dir` 脚本化（扫描裸打点 vs 结构化断言/包装信号） | samples/contract-gate |
| 版本文档结构检查：`200-spec` / `300-design` **标题**含 `Transaction Flow` / `TF` / `Step` 即报告（只扫标题；**豁免历史版本**） | docs/02 §8 / §3.7 |
| Gate 2 结构 lint：文档式契约须过 LINT-01..04（零死链 / 一条一标 / 锚点唯一 / 不引下游） | docs/06 §8.4 / samples/contract-lint |
| 契约状态**一条一标**；S3 由 `[PLANNED]` 翻 `[CURRENT]`，废弃标 `[HISTORY]` 并归档（不删除） | docs/06 §4.2 / §6.5 |
| 落地实现委托 dm-dev-step，本 skill 只守门禁 | 职责边界 |

## 产出与完成判据

**产出**：

- 门禁结果：通过 / 失败（含报错原文）
- `MANIFEST.json` 的 `contract_verified` 状态与指纹对齐
- 结构 lint 结果：`0` 全绿 / `1` 违规逐条列出

**完成判据**：

- [ ] **Gate 1**：写业务代码前已 diff 契约，未破坏不变性
- [ ] **Gate 2a（文档）**：结构 lint 全绿（零死链 / 一条一标 / 锚点唯一 / 不引下游）
- [ ] **Gate 2b（产物）**：门禁脚本通过（编译 / 类型校验 + sha256 + `contract_verified`）
- [ ] **Gate 3**：MANIFEST 文件清单、sha256、状态三者对齐
- [ ] 失败时报错已**原样抛回**并自我修复至变绿；**未绿不向用户交付**
- [ ] 可观测性 DoD 已检查（无裸打点、有出口 Assert）

## 资源映射

| 资源 | 来源 | 用途 |
|------|------|------|
| SKILL.md | — | 上述三阶段门禁流程 + 规则速查 |
| `samples/contract-lint/contract_lint.py` | `samples/contract-lint/` | 结构 lint 参考实现（`docs/06` §8.4 四查 + `--self-test` 自证 + 非 0 退出） |
| `samples/contract-gate/verify_contract.py` | `samples/contract-gate/` | 可复用门禁脚本（sha256 MANIFEST + contract_verified + JSON Schema 校验 + `--verify --source-dir` 可观测性 DoD 静态扫描 + 非 0 退出） |
| `samples/contract-gate/contract.schema.json` | `samples/contract-gate/` | 机器可校验契约样例（JSON Schema） |
| `docs/06-contract-based-dev.md` §8 | `docs/06` | 契约只读 + 三道卡口权威规范 |
| `docs/06-contract-based-dev.md` §8.4 / §4.2 | `docs/06` | 结构 lint 四查（文档层） / 契约状态生命周期 |
| `docs/07-observability-driven-dev.md` §3 | `docs/07` | 门禁失败结构化诊断（黑匣子） |

## 使用示例

```
【场景：让 AI 修复类别映射问题】

用户: 帮我把 VisionDetector 里类别映射逻辑改一下，支持 4 类检测。

AI (Gate 1 自动触发):
  读取 DetectionCategory / DetectorContract 契约...
  - 判定：改动涉及 DetectionCategory.names。
  - 约束：names 为 private static let，禁止外部覆盖，须直接改字典。
  - 确认：未破坏公开 Protocol 契约，允许继续。

[修改 VisionDetector.swift...]

AI (Gate 2 自动触发，后台静默):
  $ python3 contract_lint.py --contracts-dir docs/contracts
    ❌ LINT-01 docs/02_ARCHITECTURE.md: 锚点 `#render-host-dispatch` 不存在（引用 02-render.md）
    → 捕获报错，自我修复：修正引用锚点。
    $ python3 contract_lint.py --contracts-dir docs/contracts → ✅ 全绿
  $ xcrun swiftc -parse PochiHide-CoreML-Spike/*.swift
  ❌ DetectionBoxRenderer.swift:260: 'DetectionCategory' has no member 'names'
  → 捕获报错，自我修复：漏改 DetectionBoxRenderer 调用点。
  $ xcrun swiftc -parse ... → ✅ 0 errors
  $ python3 package_dist.py --verify → ✅ MANIFEST (contract_verified: true)

AI: 修复完成！已通过编译门禁与 MANIFEST 契约断言，3 个调用点已同步。
```

```
【场景：交付前 Gate 3】

用户: 提交代码

AI:
  触发 Gate 3：校验 MANIFEST.json（文件数 / sha256 / contract_verified）...
  ✅ 对齐 → 放行 dm-commit。
```
