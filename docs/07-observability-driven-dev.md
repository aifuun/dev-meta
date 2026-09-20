# 面向 AI 协作的可观测性驱动开发（Observability-Driven Dev, ODD）

## 1. 概述

定义 dev-meta 中「运行时暴露足够上下文、让 AI 能靠日志一次定位」的统一规范。AI 能高效生成代码，但在不透明系统里一旦出错，容易陷入「瞎猜 → 改 → 引入新 Bug」的低效循环。**ODD 把调试模式从「盲目试错」转为「日志驱动-精准定位-一次修复」**。

本文档是 ODD 的**唯一权威**；模板与 skill 只引用、不重定义。

**与 06（契约式开发）的关系**：06 定义「契约要测什么 / 不变量是什么」（静态约定）；ODD 定义「运行时如何把这些契约的状态、耗时、错误**结构化暴露**出来，供 AI 精准定位」（动态可观测）。二者互补——06 §4 的 provenance（真值来源）让诊断日志可被交叉引用防漂移；06 §5 的失败面契约（严禁静默危险失败）是 ODD §2.1 的运行时落点。

## 2. 核心原则

### 2.1 契约驱动诊断（Contract-Driven Diagnostics）

诊断契约是行为契约（06 §3 / §5）的运行时延伸：

- **不隐式吞错**：`catch` / 降级分支必须「记录并重抛（Log & Re-throw）」或「记录并回退兜底态」，保持既有 ERROR 契约不被破坏（06 §5）。
- **状态机显式化**：关键状态切换（如 `Idle → Processing → Success/Failed`）必须有日志留痕，防止流程出现无状态响应的「死锁 / 白屏」。

### 2.2 无侵入包装（Non-Intrusive Wrapping）

严禁把打点逻辑大量硬编码进主业务。应利用各语言的装饰器 / 高阶函数 / 切面（AOP）/ 中间件，使业务与诊断解耦。统一经一个 `observe(...)` 包装器出入，不在业务里散落 `print`。

### 2.3 环境快照（Environmental Snapshot）

受限环境（移动端 Extension、边缘、Serverless）中，异常日志除 Error 本身外，**须附带瞬间的物理指标**（内存增量 `ΔMemory`、当前 `Elapsed Time`），便于 AI 区分「逻辑错」vs「资源受限错」。

### 2.4 真值来源可校验（Provenance，关联 06 §4）

诊断日志的 `Input Snapshot` 须含可被交叉引用的特征（如 `imageSize`、`conf`、契约编号 `COORD-001`），使 AI 能把日志与代码 / ADR / 版本文档对上，防漂移（06 §4 四要素）。

> 📌 **判据**：诊断快照的 `Input Snapshot` 无契约编号 → 该日志**不合格**（无法与契约 SSOT 交叉引用，漂移无从发现）。

### 2.5 写逻辑即写观测（可观测性防线，AI 硬约束）

AI 盲目修改的根因是「改完代码看不到运行状态，全靠脑补」。因此可观测性不是事后补丁，而是**写业务逻辑的同时必须落地的防线**：

- **AI 写逻辑 = 同时写观测**：实现任何关键节点（状态机切换、边界条件、错误捕获、映射/查表）时，必须同步注入结构化日志（`observe` 包装器，§4）与出口 Assert。逻辑与观测不可分离提交。
- **出口 Assert 兜底**：映射/查表结果为空、状态非法、坐标越界等「不该发生但会发生」的点，必须 `assertionFailure` / `preconditionFailure`（或等价断言），把隐性错转为显性崩溃日志，而非静默返回空值（呼应 06 §5 失败面契约）。
- **范式（Swift）**：写 `DetectionBoxRenderer` 时，每次函数出口打印结构化 Log（含输入 Tensor 维度、处理时长、类别映射结果）；若 `mapped_name == nil` 必须抛 `assertionFailure("category_id=\(id) mapped_name=nil")`。AI 看到该日志可精确定位字典缺失，而非瞎改渲染视图。
- **AI 生成的单元测试 Assert 同样适用本条**：在 `docs/08-small-batch-iteration.md` §2.2 的 Agentic TDD 范式下，AI 生成的测试必须断言具体边界值（空输入、极值、越界），禁止无断言的假 Green（呼应 06 §5 失败面契约）。

> 以上「写逻辑即写观测」为 **07 §2.5 唯一权威**；模板与 skill 只引用本小节，不重定义。

### 2.6 观测层编号与三层次判据（O1 / O2 / O3）

> **编号约定**：`L1 / L2 / L3` 专属于**契约层级**（接口 / Feature / 行为，见 `docs/06`）；观测层级用 **`O1 / O2 / O3`**，避免同号不同义。

| 层 | 手段 | 回答的问题 | 自动化 |
|---|---|---|---|
| **O1 断言** | 单测 / 契约断言 | 代码是否正确 | ✅ |
| **O2 埋点** | 运行时日志（`observe`） | 运行中走了哪条分支 | ❌ |
| **O3 回读** | 端到端产物验证 | 交付物是否正确 | ❌ |

- **判据 A**：凡「产物离开进程」的操作（落盘 / 跨进程 / 上传 / 分享）→ **O3 回读不可省**（O1/O2 只能证明中间产物正确）。
- **判据 B**：存在平台专属失效模式（CI / 模拟器无法暴露）→ **O2 不可被 O1 替代**。

### 2.7 负向约束（禁止项）

- **热路径禁止无条件打点**：UI `body` / layout 等高频路径只允许 once 语义或经开关包裹，防每帧重绘写日志。
- **Release 不得存在运行期日志旁路**：日志开关不得经 `UserDefaults` / 启动参数 / 远程配置等运行期途径开启；生产隔离一律靠**构建期门控**（如 `#if DEBUG`）。

## 3. 诊断与轨迹规范（唯一权威）

> 本节含两个子节：**§3.1 诊断黑匣子**（异常 / 性能越界时的快照结构）与 **§3.2 工作流轨迹**（成功路径的流程定位）。

### 3.1 诊断黑匣子（Diagnostic Snapshot Spec）

任何被包装函数在异常或性能越界时，输出日志须含以下 **5+ 核心要素**，供 AI 直接解析：

```text
================❌ [AI-DEBUG-CONTEXT] ================
- Trace / TraceID   : [唯一链路ID，如 exec_task_9082]
- Task / Phase      : [模块名 / 函数名 / 阶段，如 VisionDetector.computeDetections]
- Elapsed Time      : [耗时，如 42.15ms]
- Resource Metrics  : [关键资源，如 Memory: 58.5MB (Delta: +0.2MB)]
- Input Snapshot    : [核心入参特征 + **契约编号**，如 { imageSize: "591x1280", conf: 0.1, nmsBefore: 24, contract: "COORD-001" }]
- Error Type        : [错误类型/类名，如 CoreMLError.ModelUnavailable]
- Error Details     : [详细报错 / 堆栈轨迹]
======================================================
```

要素含义：

| 要素 | 用途 |
|------|------|
| TraceID | 串联一次请求的多段日志（加载→检测→渲染） |
| Task / Phase | 定位到具体函数 / 阶段，避免「哪一步慢」的猜测 |
| Elapsed Time | 量化耗时，直接定位 10s 落在哪段（而非假设） |
| Resource Metrics | 区分逻辑错 vs 内存/配额受限 |
| Input Snapshot | 让 AI 复现并对照契约（06 §4 provenance） |
| Error Type / Details | 精准分类，避免泛化修改 |

### 3.2 工作流轨迹（Workflow Trace）

> **定位**：breadcrumb trail（流程面包屑），**不是**分布式 tracing —— 不做 span 树 / 父子结构 / 跨进程传播 / 采样 / 云端后端。
> 回答「**现场表现相同、根因不同时，根因是哪一条**」，而非「哪一步慢」。§3.1 的 `TraceID` 用于错误快照的链路串联，本节用于**成功路径的流程定位**；二者同属黑匣子延伸，**不新建出口**。

- **可判别性（硬要求）**：每个观测点**必须给出判别量**（标量 / 计数 / 布尔）；仅输出「已到达某步」**不合格**——布尔值只能说明「没命中」，无法区分「差一点点」与「整体偏掉」。
- **先写判读表，再写埋点**：① 列根因假设 H1…Hn → ② 对每个假设写「若它是根因，此处应观测到什么**反常值**」→ ③ 只保留能区分假设的观测点，其余不埋 → ④ 每条 flow 须能「**一次命中**」。
- **判读表合格线**：须覆盖该 flow 的**全部候选根因**；**两行无法区分 → 该表不合格**（补 step 或换判别量）。
- **粒度判据**：一个 flow = **一次用户可感知操作的完整链路**（入口 → 产物落地）。**反例（禁止）**：每个按钮 / 每个函数各开一个 flow（会膨胀至数十个标识）。
- **单一出口**：轨迹**必须**经既有 `observe` 出口产出；**禁止**新建 logger / 文件 / 环形缓冲（承接 §2.2）。
- **内容与职责边界**：只记操作遥测（计数 / 时长 / 标量 / 布尔 / 契约编号）；**禁止**几何明细或图像 / 大对象派生数据；时长只作**判别量**（判别根因），**不作为性能定位目标**（那属 §3.1 的 `Elapsed Time`）；轨迹**不得**替代失败计数与抛错（承接 §2.1）。
- **测试层级**：原语正确性（调用顺序 / 判别量非空 / 门控）→ **单元测试**；**轨迹有效性（能否一次判别根因）→ 集成 / E2E（完整逻辑链路）**。
  📌 **判据**：单测全绿**不等于**轨迹可用；**不得以单元测试代替完整逻辑链路上的验证**——轨迹的价值只有跑通完整链路才成立。

## 4. 各语言落地模版（无侵入包装器）

### 4.1 Swift / iOS（高阶闭包 + 泛型，DEBUG 隔离）

```swift
import Foundation

enum Observability {
    /// 包装任意同步/异步可能抛错的逻辑；DEBUG 下输出耗时/上下文
    static func observe<T>(
        _ stageName: String,
        metadata: [String: Any] = [:],
        block: () throws -> T
    ) rethrows -> T {
        let startTime = CFAbsoluteTimeGetCurrent()
        do {
            let result = try block()
            let elapsed = (CFAbsoluteTimeGetCurrent() - startTime) * 1000
            #if DEBUG
            print("==> [SUCCESS] \(stageName) | Elapsed: \(String(format: "%.2f", elapsed))ms")
            #endif
            return result
        } catch {
            let elapsed = (CFAbsoluteTimeGetCurrent() - startTime) * 1000
            #if DEBUG
            print("""
            ================❌ [AI-DEBUG-CONTEXT] ================
            - Task / Phase      : \(stageName)
            - Elapsed Time      : \(String(format: "%.2f", elapsed))ms
            - Input Snapshot    : \(metadata)
            - Error Type        : \(type(of: error))
            - Error Details     : \(error.localizedDescription)
            ======================================================
            """)
            #endif
            throw error
        }
    }
}
```

iOS 受限环境（Share Extension 等）建议 `Resource Metrics` 接入 `MemorySampler`（见 PochiHide `Shared/MemorySampler.swift`），在 `metadata` 中补 `memoryMB` / `deltaMB`。

**出口 Assert + 出口日志范式（呼应 §2.5 写逻辑即写观测）**：在映射/查表/边界函数出口同步打印结构化结果并兜底空值，把隐性错转为显性崩溃日志：

```swift
func mapCategoryName(_ id: Int) -> String {
    let mapped = categoryDict[id]            // 查表
    // 出口日志：含输入 id + 映射结果，供 AI 一次定位
    #if DEBUG
    print("==> [MAP] DetectionBoxRenderer.mapCategoryName | id: \(id) | mapped: \(mapped ?? "nil")")
    #endif
    // 出口 Assert：映射为空 = 不该发生但会发生，转显性崩溃而非静默返回
    assert(mapped != nil, "category_id=\(id) mapped_name=nil — 字典缺失，检查 DetectionCategory 契约")
    return mapped ?? "unknown"
}
```

### 4.2 Python（装饰器模式）

```python
import functools, time, traceback, logging

def observe_stage(stage_name: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed = (time.perf_counter() - start) * 1000
                logging.info(f"==> [SUCCESS] {stage_name} | Elapsed: {elapsed:.2f}ms")
                return result
            except Exception as e:
                elapsed = (time.perf_counter() - start) * 1000
                logging.error(f"\n===❌ [AI-DEBUG-CONTEXT]===\n"
                              f"- Task/Phase: {stage_name}\n- Elapsed: {elapsed:.2f}ms\n"
                              f"- Error: {type(e).__name__}\n- Details: {e}\n"
                              f"- Stack:\n{traceback.format_exc()}================")
                raise
        return wrapper
    return decorator
```

### 4.3 TypeScript / Node.js（异步包装器）

```typescript
export async function observeStage<T>(stageName: string, metadata: Record<string, any>, fn: () => Promise<T>): Promise<T> {
  const start = performance.now();
  try {
    const result = await fn();
    console.log(`==> [SUCCESS] ${stageName} | Elapsed: ${(performance.now() - start).toFixed(2)}ms`);
    return result;
  } catch (error: any) {
    console.error(`\n===❌ [AI-DEBUG-CONTEXT]===\n- Task/Phase: ${stageName}\n- Elapsed: ${(performance.now() - start).toFixed(2)}ms\n- Input: ${JSON.stringify(metadata)}\n- Error: ${error?.name}\n- Details: ${error?.message}\n- Stack:\n${error?.stack}================`);
    throw error;
  }
}
```

## 5. AI 协作调试闭环（3 步）

```
[系统触发异常 / 断言失败 / 性能越界]
          ▼
[控制台自动输出 ❌ AI-DEBUG-CONTEXT]
          ▼
[复制上下文 + 结合契约文件（00_CONTRACTS / 06 / §4 provenance）]
          ▼
[投喂 AI] ──► "根据这份诊断日志和契约，精准修复 X 文件"
```

### 5.1 Log-Driven 排查纪律（禁止自然语言描述现象）

系统报错或结果不符预期时，**绝对不要向 AI 描述现象**（如「图片上标签没显示出来」）。自然语言现象描述迫使 AI 猜想根因，容易瞎改无关模块。

**正确做法：贴出可观测性产物**——终端结构化 Log（`[AI-DEBUG-CONTEXT]`）、Crash 堆栈、Tracing ID、Assert 消息。AI 对结构化日志的解析力远超对现象描述的猜测；当看到 `[ERROR] category_id=3 mapped_name=nil` 时，能直接定位字典缺失，而不会跑去改渲染视图。

- 用户侧：提交排查时优先粘贴日志原文，现象描述仅作辅助上下文。
- AI 侧：收到自然语言现象而无日志时，应先要求对方贴 `[AI-DEBUG-CONTEXT]`，不得基于现象直接改码（呼应 §2.5 写逻辑即写观测——日志是 AI 的眼睛）。

**推荐提问 Prompt 模版**（提交 AI 时直接套用）：

```text
【问题排查指令】
我在运行 [模块/函数名] 时遇到异常，以下是可观测性黑匣子导出的结构化日志：

[直接粘贴控制台 ❌ AI-DEBUG-CONTEXT 全量内容]

约束：
1. 根据日志 Input Snapshot 与 Error Details 分析根因；
2. 遵守既有契约（API 签名、内存/耗时限制、06 §3/§5），只改引发 Bug 的核心几行；
3. 严禁无意义重构；先给诊断原因，再给改动方案。
```

## 6. 与 dev-meta 体系衔接

| 衔接点 | 关系 |
|--------|------|
| `docs/06-contract-based-dev.md` §3 / §5 | ODD 是行为契约的运行时暴露；06 §3 的「失败透明」与 §5 的「失败面契约（禁止静默吞错）」是 ODD §2.1 的硬约束来源；06 已在其 §4.1 / §5 / §11.2 引用本规范 §2.1 / §3 / §6 |
| `docs/06-contract-based-dev.md` §4 | 诊断日志 `Input Snapshot` 须可被 provenance 交叉引用，防漂移 |
| `skills/dm-plan-ver.md` | 400-build 行为契约须含「诊断契约（关键路径 observe 包装 + 状态留痕 + 无静默吞错）」 |
| `skills/dm-dev-step.md` | Step 实现期须把诊断契约写入 400-build 行为契约；错误/降级路径结构化诊断、高开销节点含 Elapsed+资源指标 |
| `skills/dm-cleanup.md` | 「静默吞错 / 空 catch / 裸露 print / 依赖返回值兜底」列为隐性契约债（06 §5），清理时须补 observability 包装 |
| `skills/dm-grillme-plan.md` | 实现降级级 grill 须 probe 可观测性盲区（无诊断契约 / 静默吞错 / 裸露日志），写码前消灭盲点 |
| `skills/dm-close-ver.md` | Phase A 就绪性审计须加 ODD DoD 检查（无裸露日志 / 无静默吞错 / 高开销节点有诊断快照），合并前闸门 |
| `skills/dm-init-docs.md` | 脚手架阶段植入 `observe` 包装器（§4）+ ODD 基线（无裸 print、错误须结构化诊断），预防式防盲 |
| `skills/dm-adr.md` | 可观测性架构级取舍（如 computeUnits / 采样粒度 / 预编译模型 / 诊断分级）走 ADR 记录 |
| `skills/dm-contract-gate.md` | 断言门禁的「报错原样抛回」是 ODD 闭环在契约层的延伸——门禁失败时须输出结构化诊断（含契约快照 + 不一致 diff），便于 AI 一次定位（呼应 07 §2.1/§3）；门禁须含可观测性 DoD（改后无 observe 包装 / 无出口 Assert 视为未过，呼应 07 §2.5）；门禁脚本见 samples/contract-gate/ |
| `docs/05-codebuddy-management.md` | `observe` 包装器可沉淀为 project snippet / 模板，新模块直接复用 |

## 7. DoD / 行动清单（合并前核对）

- [ ] **无裸露日志**：关键路径全部经 `observe(...)` 包装器，不散落原始 `print` / `console.log`。
- [ ] **写逻辑即写观测**：关键节点（状态切换/边界/映射/错误捕获）实现时同步注入结构化日志 + 出口 Assert（07 §2.5），逻辑与观测不可分离提交。
- [ ] **无静默吞错**：所有 `try-catch` / 降级分支均有诊断快照留痕（06 §5）。
- [ ] **高开销节点覆盖**：文件 I/O、网络、模型推理、跨进程调用均含 `Elapsed Time` + 关键资源指标。
- [ ] **Log-Driven 排查**：报错时只贴结构化日志/Crash/Trace，不向 AI 描述自然语言现象（07 §5.1）。
- [ ] **验证闭环**：故意构造坏数据测试时，控制台能准确输出 `[AI-DEBUG-CONTEXT]`，复制给 AI 后能一次性定位并给出修复。
- [ ] **轨迹可判别**：每个观测点均有判别量，无「只报到达某步」的观测点；判读表无模糊行（07 §3.2）。
- [ ] **轨迹验证在完整逻辑层**：经集成 / E2E 构造已知根因场景并断言「一次命中」，未以单测代替（07 §3.2）。
- [ ] **无旁路 + 计数同处**：Release 无运行期日志开关（靠构建期门控）、热路径无非 once 打点；`recordFailure` 与抛错点同处（07 §2.7 / §2.1）。

> 以上 ODD 规范为**唯一权威**；模板与 skill 只引用本小节，不重定义。
