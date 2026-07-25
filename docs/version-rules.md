# Version Rules — 版本目录文件规范

本规范定义了每个版本目录下的标准文件结构、职责分工和基于 Transaction Flow 的写作方式。

---

## 1. 目录结构

```
docs/versions/vX.Y-<slug>/
├── spec.md              # Transaction Flow 目标与验收：交付什么、怎样算完成
├── general-design.md    # Transaction Flow 概要设计：流程如何串联、模块如何分工
├── detailed-design.md   # Transaction Flow 详细设计：每一步怎么做、怎么落代码
└── tasks.md              # Transaction Flow 交付计划：怎么拆分、怎么执行
```

### 创建顺序

> 版本级四文档按以下顺序创建，每步都是下一步的前置条件：

| 顺序 | 文档 | 回答的问题 | 前置依赖 |
|------|------|-----------|----------|
| 1 | `spec.md` | 交付什么？怎样算完成？ | — |
| 2 | `general-design.md` | 流程如何串联？模块如何分工？ | spec |
| 3 | `detailed-design.md` | 每一步怎么实现？ | general-design |
| 4 | `tasks.md` | 怎么拆分？怎么执行？ | detailed-design |

---

## 2. 各文件职责

| 文件 | 受众 | 回答的问题 | 关键内容 |
|------|------|-----------|---------|
| `spec.md` | PM / QA / Dev | 这条 Transaction Flow 要交付什么？怎样算完成？ | 目标、交付范围、功能验收标准、架构验收标准、DoD |
| `general-design.md` | 架构师 / Dev | 各 Transaction Flow 如何衔接？各流负责什么？ | 流程切分、顺序、模块关系图、关键架构决策与原因 |
| `detailed-design.md` | Dev | 每个 Transaction Flow 的每一步怎么实现？ | 流内步骤、函数签名、Schema、API 契约、异常路径策略 |
| `tasks.md` | Dev / PM | 这条 Transaction Flow 怎么交付？先后顺序是什么？ | 任务拆分列表、依赖关系、预估执行顺序 |

---

## 3. 以 Transaction Flow 为主轴的设计原则

### 3.1 基本定义

Transaction Flow 是版本内可独立描述、可独立验证的一段业务流或交付流。例如：

- TF1：初始化与前置准备
- TF2：核心处理与转换
- TF3：结果落库与对外输出

Transaction Flow 不是章节编号，而是业务流单元。编号要稳定，名称要表达业务语义。

补充规则：

- TF 编号在同一版本迭代期间必须保持稳定，不得随意重排或重命名。
- 若某个 TF 后续确认废弃，应保留原编号并标记为 `[DEPRECATED]`，避免文档、任务和实现引用失配。

### 3.2 两层设计如何对齐

```
1. general-design 先定义每个 Transaction Flow 的目标、边界、输入输出和依赖关系
2. detailed-design 再展开同一个 Transaction Flow 内部的具体步骤、接口和异常处理
3. tasks 按 Transaction Flow 的实现顺序拆解任务，便于按业务流推进交付
```

### 3.3 分层收益

| | general-design | detailed-design |
|------|:---:|:---:|
| **关注粒度** | Transaction Flow 级别 | 流内步骤级别 |
| **迭代频率** | 低，更多改业务边界 | 高，更多改实现细节 |
| **审核方式** | 人审业务流是否合理 | 人审实现是否完整可落地 |
| **复用价值** | 适合做版本总览和评审 | 适合直接指导编码 |

### 3.4 内容边界

**general-design.md** 包含：
- Transaction Flow 的名称、目标、范围
- 各流之间的先后顺序与依赖关系
- 每个流的输入、输出、成功条件
- 关键架构决策及理由（为什么这样串联）
- 与上一版本或现有能力的继承/变更关系
- **跨 TF 状态机**：当多个 TF 通过状态跃迁协作时，在此定义状态、跃迁条件及各 TF 在状态机中的角色
- **测试策略**：每个 TF 的测试级别（单元/集成/E2E/手工）、关键测试场景、测试环境依赖

**general-design.md 不包含**：
- 函数签名
- 具体 API 参数列表
- 伪代码
- 具体异常回退细节
- 单 TF 内部的状态机（应放在 detailed-design.md）
- 具体测试用例（策略层级即可，用例细节在 detailed-design 中展开）

**spec.md** 不包含：
- 输入、输出、依赖关系的详细设计
- 伪代码
- 具体异常回退细节

**spec.md** 仅保留业务级别信息：
- 本版本业务目标
- Transaction Flow 的清单与业务目标
- 功能验收标准
- 架构验收标准（面向业务可见结果）
- DoD

**detailed-design.md** 包含：
- 每个 Transaction Flow 内部的步骤拆解
- 每一步对应的函数签名、入参、返回值、调用时机
- 数据结构 / Schema 定义
- API 调用顺序与前置条件
- 边界情况与异常路径策略
- 若 Transaction Flow 内部涉及复杂异步状态或交互流程，必须补充文本状态机或时序图（Sequence Diagram）

---

## 4. spec.md 内容结构

```
# VX.Y 特性规格

## 1. 业务流总览
（自然语言段落，先描述本版本的业务目标，再说明包含哪些 Transaction Flow）

## 2. Transaction Flow 清单
（表格：流编号 | 流名称 | 业务目标 | 验收锚点）

## 3. 功能验收标准
（表格：验收项 | 对应流 | 验证方法 | 通过标准）

## 4. 架构验收标准
（表格：验收项 | 对应流 | 通过标准）

## 5. DoD (Definition of Done)
（勾选框清单，需包含测试相关条目）
```

---

## 5. general-design.md 内容结构

```
# VX.Y 概要设计

## 1. 架构背景与目标
（本版本的架构目标、上一版本基线、影响范围）

## 2. Transaction Flow 划分
（每个流的一句话职责、输入、输出、依赖、边界）

## 3. 流之间的数据流
（流的执行顺序、依赖关系、串行/并行关系）

## 4. 关键决策
（影响业务流和架构的选择及理由）

## 5. 与现有版本的继承关系
（表格：现有能力 / 模块 / 流 → 本版本变更）

## 6. 跨 TF 状态机
（当多个 TF 通过状态跃迁协作时，在此定义。
每个状态机包含：名称与作用范围、状态列表、跃迁条件、涉及哪些 TF、各 TF 在哪些跃迁中起作用）

## 7. 测试策略
（每个 TF 的测试级别、关键测试场景、测试环境依赖。
general-design 仅定义策略层级（单元/集成/E2E/手工）和关键场景，不写具体测试用例）
```

---

## 6. detailed-design.md 内容结构

```
# VX.Y 详细设计

## 1. 通用约束
（本版本所有 Transaction Flow 共用的数据 Schema、API 契约、异常处理原则）

### 1.1 数据 Schema
（存储结构、key 命名规则、索引设计）

### 1.2 API 契约
（模块间调用顺序、前置条件、返回值约定）

### 1.3 异常与边界
（失败重试、并发冲突、配额不足、大数据量等共用处理策略）

## 2. TF1 详细设计

每个 TF 拆解为以下子章节：
- 目标：该流要完成什么、成功条件
- 步骤拆解：每一步的序号与描述
- 函数签名与伪代码：关键函数的签名（函数名、入参类型、返回值类型、调用时机）与流程伪代码
- 输入输出与前置条件：输入、输出、前置条件、后置条件
- 异常与边界：异常场景、回退策略、重试策略

## 3. TF2 详细设计
（结构同上 TF1）

## 4. 风险与缓解
（表格：风险 | 影响 | 缓解措施）

## 5. 状态机 / 时序图
（当 Transaction Flow 涉及复杂异步状态或跨端交互时，补充文本状态机或时序图）
```

---

## 7. tasks.md 内容结构

```
# VX.Y 任务拆分

## 1. 按 Transaction Flow 的任务列表
（表格：序号 | 流 | 任务 | 涉及文件 | 依赖 | 预估）

## 2. 执行顺序
（按 Transaction Flow 的推荐交付顺序说明）
```

### 7.1 任务填充规则

`tasks.md` 是前序三文档（spec、general-design、detailed-design）的**执行视图**。创建时必须以 `detailed-design.md` 为主要来源逐 TF 提取任务，以 `general-design.md` 补充依赖与顺序。

#### 各列来源

| 列 | 来源 | 提取方式 |
|----|------|----------|
| **序号** | — | 按推荐执行顺序从 1 递增编号 |
| **流** | `general-design.md` §2 | 取该 task 所属的 TF 编号（TF1 / TF2 / …）。一个 TF 可对应多行 task |
| **任务** | `detailed-design.md` 各 TF 的 §步骤拆解 | 将每个步骤提炼为一句可执行的任务描述 |
| **涉及文件** | `detailed-design.md` 各 TF 的 §函数签名 | 提取函数签名所在的文件路径 |
| **依赖** | `general-design.md` §3 + `detailed-design.md` 各 TF 的 §输入输出与前置条件 | 标注前置 TF 编号，或"无" |
| **预估** | — | 基于步骤复杂度的人工评估（0.5d / 1d / 2d ...） |

#### 填充步骤

1. **读取 `general-design.md`**：
   - 从 §2 获取所有 TF 的编号、名称与依赖关系
   - 从 §3 确认 TF 执行顺序与串并行关系
   - 从 §7 提取每个 TF 的测试策略（在任务末尾补充测试任务）

2. **读取 `detailed-design.md`**：
   - 按 TF 顺序，逐个 TF 从中提取：
     - §步骤拆解 → 每步变为一个 task 行
     - §函数签名与伪代码 → 提取涉及文件
     - §输入输出与前置条件 → 确认依赖（映射到其他 TF）
     - §异常与边界 → 如涉及独立的边界处理逻辑，可拆为单独 task

3. **补全最后一轮任务**（每个版本都应包含）：
   - "补单测与回归用例"（流列填"全部"，依赖填所有 TF）
   - "本地构建与回归验证"（流列填"全部"，依赖填全部）

4. **填写 §2 执行顺序**：
   - 推荐先做哪些流
   - 哪些任务可以并行
   - 哪些任务必须串行（含原因）

#### 验收标准

- tasks.md 中的每行非模板 task 都必须能从 detailed-design.md 中找到对应步骤
- 依赖列必须与 general-design.md §3 的 TF 依赖关系一致
- 不允许 tasks.md 留有空白模板行（Phase 1 结束时必须完全填充）

---

## 8. 模板目录

为了让规范可直接落地，建议为每个版本目录维护对应模板：

```
templates/versions/vX.Y-<slug>/
├── spec.md
├── general-design.md
├── detailed-design.md
└── tasks.md
```

模板用途：

- `spec.md` 模板用于快速起草版本交付范围和验收标准。
- `general-design.md` 模板用于快速起草 Transaction Flow 划分与流转关系。
- `detailed-design.md` 模板用于快速起草伪代码、状态机、Schema 和边界处理。
- `tasks.md` 模板用于快速起草按流拆解的任务列表与执行顺序。

模板与正式文档必须保持字段和章节结构一致，避免出现“规范更新了、模板没跟上”的漂移。

---

## 9. 反模式

以下内容不应出现在对应文件中：

| 不要放在… | 内容 | 应放在 |
|-----------|------|--------|
| spec.md | 具体代码实现细节 | detailed-design.md |
| general-design.md | 函数签名 | detailed-design.md |
| detailed-design.md | 流的一句话职责总览 | general-design.md |
| tasks.md | 功能验收标准 | spec.md |
| spec.md | 数据 Schema | detailed-design.md |
| general-design.md | 单 TF 内部的状态机 | detailed-design.md |
| detailed-design.md | 跨 TF 状态机 | general-design.md |
| general-design.md | 具体测试用例 | detailed-design.md |
