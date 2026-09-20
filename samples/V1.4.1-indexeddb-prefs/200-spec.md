# V1.4.1 特性规格

建立 IndexedDB 基础通道，实现 **per-trackId 播放偏好持久化**（进度 / 倍速 / AB 循环），解决切歌丢进度的核心痛点。
版本范围内**不包含**：云同步、跨设备偏好漫游、服务端存储。

## 1. 架构锚点（本版本触及的架构面）

> 只登记「本版本动到架构哪几处」，不写为什么这样设计（论证属 `300-design.md`）。

| 维度 | 本版本触及 | 硬约束 / 红线 |
|---|---|---|
| 分层 | 宿主层：调用偏好读写，IndexedDB 不可用时静默降级；存储层：新增 per-trackId 偏好读写 | 宿主不直接操作 IndexedDB API；存储层不依赖 DOM / Engine 实例 |
| 模块 | `audio-store.js`、`prefs-store.js`（新建）；`switchTrack()` / `startTimingLoop()` / `deleteTrack()` / `clearPlaylist()`（修改） | — |
| 门面 | `prefs-store.js`（新增） | 仅暴露 save / load / delete / deleteAll，不暴露底层 IndexedDB 句柄 |
| 契约 | STORE-001（本样例未建契约 SSOT，仅示范）·新增·阻塞 | — |
| API | `openDB()` / `closeDB()` / `getStorageEstimate()`；`save(trackId,prefs)` / `load(trackId)` / `delete(trackId)` / `deleteAll()` | 新增 |

### 1.1 明确不做（技术 / 范围）

| 项 | 类型 | 理由 / 归属 |
|---|---|---|
| 云同步 / 跨设备偏好漫游 / 服务端存储 | 范围 | 见版本范围声明 |
| 每帧写入 `currentTime` | 技术 | 阻塞播放时钟，须节流至每秒一次 |

## 2. 功能验收标准

| 验收项 | 验证方法 | 通过标准 |
|---|---|---|
| 切歌保持进度 | 播放曲 A 至 30s，切到曲 B，再切回曲 A | 曲 A 从 ~30s 附近续播 |
| 切歌保持倍速 | 曲 A 设为 1.5x，切到曲 B，再切回曲 A | 曲 A 倍速恢复为 1.5x |
| 切歌保持 AB 循环 | 曲 A 设 AB 区间，切到曲 B，再切回曲 A | AB 循环恢复生效 |
| 首次播放默认值 | 从未播放过的曲目切换进来 | 进度=0，倍速=1.0，AB=空 |
| 删除轨道清理偏好 | 删除某曲目后再重新导入同名文件 | 偏好不残留，按默认值起播 |
| 清空列表清理全部偏好 | 清空列表 | prefs-store 中数据全部清除 |
| IndexedDB 不可用降级 | 隐私模式下使用播放器 | 所有功能正常，偏好丢失时静默降级 |
| Web 版回归 | 执行 V1.3 delivery 中 24 项 Web 验收 | 全部通过，无回归 |

## 3. 架构验收标准

| 验收项 | 通过标准 |
|---|---|
| 模块独立 | `prefs-store.js` 不依赖 DOM、不依赖 Engine 实例，可独立单测 |
| 异步非阻塞 | 所有 prefs-store 写操作不阻塞 UI 线程和播放时钟 |
| 向后兼容 | 旧版无 per-trackId 数据的用户升级后，所有曲目按默认值起播，不报错 |
| 构建通过 | `npm run build` 无错误 |

## 4. DoD (Definition of Done)

> **确认类** checklist —— 只写「是否已确认 / 已通过」，实现任务见 `400-build.md`。

- [ ] 核心业务场景已确认（单一场景：per-trackId 偏好持久化）
- [ ] 架构锚点已确认（§1 分层 / 模块 / 门面 / 契约 / API 均已登记）
- [ ] 受影响契约已回写至契约 SSOT
- [ ] 验收标准已确认
- [ ] 相关设计文档已评审通过
- [ ] 测试策略已定义（见 `300-design.md` 测试策略章节）
- [ ] 关键测试场景已通过
- [ ] Web 版 24 项回归全部通过
- [ ] `npm run build` 通过
