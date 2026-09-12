# {{PROJECT_NAME}} - 契约与 API (Contracts SSOT)

> **文档流向纪律**：本文档严格依赖 upstream `01_TECHNICAL_SPEC.md` 与 `02_SYSTEM_DESIGN.md`。
> 本文档定义系统**不可变式、数据类型、存储 Schema 及 API 契约**，作为下游实现与测试的**只读 SSOT**；下游（`04`、`05`、`06`）引用本文，**本文不反向引用下游**。
> **占位符约定**：`{{FIELD}}` = 结构化命名字段；`<!-- TODO: [dm-init-docs] <说明> -->` = 待补充内容。
> **权威引用**：契约记录规范（四要素 + 域-序号编号）与失败面契约见 `dev-meta/docs/06-contract-based-dev.md` §2.6 / §2.7（唯一权威）；契约只读纪律见 §2.8。本文只落地，不重定义。

---

## 1. 不可变式规则 (Invariants)

> **违反以下任何一条即表示系统处于损坏状态**（写实现与测试的第一判据）。

| 编号 | 不变式 | 归属 | 方向 | 真值来源 |
|------|--------|------|------|----------|
| INV-01 | <!-- TODO: [dm-init-docs] 核心业务不变式，如：账户余额不得为负数 --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |
| INV-02 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |

> 每条契约须标注**四要素**（归属 / 方向 / 不变性 / 真值来源）+ 域-序号编号，详见 `dev-meta/docs/06` §2.6。

---

## 2. API 接口定义

### 2.1 {{API_NAME}}

- **Path**：`{{API_PATH}}`
- **Method**：`{{API_METHOD}}`
- **归属 / 调用方**：<!-- TODO -->
- **幂等性**：<!-- TODO: [dm-init-docs] 是否幂等，重复调用的语义 -->
- **兼容性**：<!-- TODO: [dm-init-docs] 版本兼容策略 -->

**Request**

```json
/* TODO: [dm-init-docs] Request Schema */
```

**Response**

```json
/* TODO: [dm-init-docs] Response Schema */
```

**失败面（Failure Face）**

| 错误码 | 场景 | 返回约定 | 是否静默 |
|--------|------|----------|----------|
| <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | 否 |

> **严禁静默吞错**：纯函数式失败返回空 / 原值而非 nil；危险失败不得静默，须调用前拦截并显式暴露（`dev-meta/docs/06` §2.7）。

---

## 3. 存储 Schema

| 实体 | 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|------|
| <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |

- **迁移策略**：<!-- TODO: [dm-init-docs] Schema 演进与兼容 -->

---

## 4. 错误码总表

| 错误码 | 含义 | 级别 | 处理建议 |
|--------|------|------|----------|
| <!-- TODO --> | <!-- TODO --> | ERROR / WARN | <!-- TODO --> |

---

## 5. 契约演进治理

- **破坏性变更**（改语义 / 签名 / 坐标口径）：须走 `dm-adr` 记录并同步调用方，**不得静默修改**。
- **纯增量追加**：标注「纯增量」并回写编号至本表。
- **只读纪律**：AI 严禁自行改写契约本身；改实现前先 diff 契约（见 `dev-meta/docs/06` §2.8 与 `dm-contract-gate`）。

---

## 6. 引用声明

| 引用对象 | 方向 | 用途 |
|----------|------|------|
| `01_TECHNICAL_SPEC.md` | upstream | 技术选型与约束 |
| `02_SYSTEM_DESIGN.md` | upstream | 架构与数据流 |
| `dev-meta/docs/06-contract-based-dev.md` | 外部权威 | 契约规范（只引用） |
| `04_UI_UX_DESIGN.md` | downstream | 视图状态与交互 |
| `06_OBSERVABILITY.md` | downstream | 失败面可观测性 |
