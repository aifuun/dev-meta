# V1.4.1 设计

## 1. 架构背景与目标

- 架构目标：把偏好持久化能力从播放器主流程中拆出来，形成可独立复用的 IndexedDB 基础通道。
- 上一版本基线：V1.3（已发布）。
- 影响范围：切歌恢复、定时写入、删除清理、异常降级。

## 2. 架构与分层

**全局架构**：

```
宿主层（播放器）
  playback-controller.js   编排切歌：先保存当前曲，再恢复目标曲
  core-engine.js           清空列表时触发偏好清理
  playlist-manager.js      删除轨道时触发偏好清理
        │ 只经门面调用，不直连 IndexedDB
        ▼
存储层
  prefs-store.js           per-trackId 偏好读写（唯一门面）
  audio-store.js           IndexedDB 打开 / 关闭 / 容量探测
        ▼
  IndexedDB
```

**分层落位**：

| 层 | 模块 | 职责 |
|---|---|---|
| 宿主层 | `playback-controller.js` / `core-engine.js` / `playlist-manager.js` | 在既有业务流程中插入偏好读写调用；IndexedDB 不可用时静默降级 |
| 存储层 | `prefs-store.js`（门面）、`audio-store.js`（底层） | 偏好持久化与 IndexedDB 能力封装 |

### 2.1 防腐设计

| 关注点 | 设计约束 |
|---|---|
| 类型边界 | 偏好以 `{ trackId, currentTime, rate, abLoop }` 纯数据对象传递；宿主不接触 IndexedDB 句柄 |
| 错误域边界 | 存储层失败只返回 `null` / 空结果，**不抛**；由宿主决定降级表现，禁止字符串匹配错误类型 |
| 模块物理路径 | 新增文件统一放 `src/storage/`；主 App / 测试经同步组自动纳入，**无构建项需显式登记** |

- 新增公共文件（`src/storage/` 下）的工程登记规则：无（当前工程自动纳入）

## 3. 数据流与状态机

**关键数据流**：

1. 播放中：`startTimingLoop()` 每秒（节流）调用 `prefsStore.save(trackId, state)`
2. 切歌时：`switchTrack()` **先** `save(旧 trackId)` → **再** `load(新 trackId)` → 应用到播放器
3. 删除 / 清空：`deleteTrack()` / `clearPlaylist()` 调用 `prefsStore.delete` / `deleteAll`
4. 降级贯穿：`audio-store` 打开失败时，`prefs-store` 所有接口转为无操作并返回空结果

- 串行 / 并行：切歌的「保存 → 恢复」必须**串行**；定时写入与播放主线程**并行**（异步 + 节流）
- 状态跃迁：本版本无多模块状态跃迁，各调用点独立经 `prefs-store` 门面交互，**无需状态机**

## 4. 核心算法方案

本版本不涉及核心算法与数据量化（纯存储能力接入）。

## 5. 关键决策（ADR）

| 决策 | 备选方案 | 选择理由 | 影响 |
|---|---|---|---|
| 以 trackId 作为偏好主键 | 以文件名或索引作为主键 | trackId 更稳定，能避免同名文件与重排问题 | 删除/重导入时可精确清理 |
| 偏好与播放时钟异步写入 | 每帧写入 currentTime | 异步节流可以避免 UI 和播放时钟被阻塞 | 需要容忍最终一致性 |
| 保存与恢复拆为独立操作 | 切歌时一次性覆盖 | 独立操作更容易复用与单测，也更容易失败降级 | 需要保证 switchTrack 顺序正确 |
| IDB 不可用时静默降级 | 直接报错阻断播放 | 播放是主路径，偏好可丢失但功能不能中断 | 需要明确默认值策略 |

## 6. 与现有版本的继承关系

| 现有能力 / 模块 | 本版本变更 |
|---|---|
| `playback-controller.js` 切歌逻辑 | 在 `switchTrack()` 中增加先保存后恢复偏好的编排 |
| `startTimingLoop()` | 增加周期性写入 `currentTime` 的持久化动作 |
| `core-engine.js` 清空列表 | 增加 `prefsStore.deleteAll()` 清理动作 |
| `playlist-manager.js` 删除轨道 | 增加 `prefsStore.delete(trackId)` 清理动作 |
| 播放器默认行为 | 在无历史偏好时继续使用默认值起播 |

## 7. 测试策略

> design 仅定义策略层级和关键场景；具体测试用例与行为契约在 `400-build.md` 展开。

| 关注点 | 测试级别 | 关键场景 | 环境依赖 |
|--------|---------|---------|---------|
| 切歌恢复 | 单元 + 手工 | 切回同一曲目恢复进度/倍速/AB；首次播放用默认值 | 浏览器 IndexedDB |
| 定时写入 | 单元 + 集成 | 节流写入不阻塞播放时钟；重启后从最近保存点恢复 | 浏览器 IndexedDB |
| 删除清理 | 单元 | 删除轨道 / 清空列表后偏好不残留 | 浏览器 IndexedDB |
| 异常降级 | 单元 + 手工 | 隐私模式或配额异常时静默降级、播放不中断 | 隐私模式浏览器 |
