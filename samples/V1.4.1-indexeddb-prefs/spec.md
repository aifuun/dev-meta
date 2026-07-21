# V1.4.1 特性规格

## 1. 业务流总览

- 该版本的业务目标：建立 IndexedDB 基础通道，实现 per-trackId 播放偏好持久化（进度、倍速、AB 循环），解决切歌数据丢失的核心痛点。
- 本版本包含哪些 Transaction Flow：
  - TF1：切歌时先保存当前曲偏好，再恢复目标曲偏好
  - TF2：播放时定时刷写 currentTime 到 per-trackId 偏好键
  - TF3：删除轨道与清空列表时清理偏好数据
  - TF4：IndexedDB 不可用时静默降级，播放器仍可正常工作
- 版本范围内不包含什么：
  - 不包含云同步
  - 不包含跨设备偏好漫游
  - 不包含服务端存储

## 2. Transaction Flow 清单

| 流编号 | 流名称 | 业务目标 | 验收锚点 |
|---|---|---|---|
| TF1 | 切歌时保存并恢复偏好 | 保证曲目切换前后的偏好连续性 | 切回同一曲目时，进度/倍速/AB 可恢复 |
| TF2 | 定时刷写播放进度 | 保持进度在切歌和重启后可恢复 | 切歌与重启后可从最近保存点恢复 |
| TF3 | 删除/清空时清理偏好 | 避免残留数据污染后续导入 | 删除或清空后，偏好数据不残留 |
| TF4 | IndexedDB 降级 | 在隐私模式或不可用场景中保持可用 | 不可用场景下播放不中断并静默降级 |

## 3. 功能验收标准

| 验收项 | 对应流 | 验证方法 | 通过标准 |
|---|---|---|---|
| 切歌保持进度 | TF1 | 播放曲 A 至 30s，切到曲 B，再切回曲 A | 曲 A 从 ~30s 附近续播 |
| 切歌保持倍速 | TF1 | 曲 A 设为 1.5x，切到曲 B，再切回曲 A | 曲 A 倍速恢复为 1.5x |
| 切歌保持 AB 循环 | TF1 | 曲 A 设 AB 区间，切到曲 B，再切回曲 A | AB 循环恢复生效 |
| 首次播放默认值 | TF1 / TF4 | 从未播放过的曲目切换进来 | 进度=0，倍速=1.0，AB=空 |
| 删除轨道清理偏好 | TF3 | 删除某曲目后再重新导入同名文件 | 偏好不残留，按默认值起播 |
| 清空列表清理全部偏好 | TF3 | 清空列表 | prefs-store 中数据全部清除 |
| IndexedDB 不可用降级 | TF4 | 隐私模式下使用播放器 | 所有功能正常，偏好丢失时静默降级 |
| Web 版回归 | TF1 / TF2 / TF3 / TF4 | 执行 V1.3 delivery 中 24 项 Web 验收 | 全部通过，无回归 |

## 4. 架构验收标准

| 验收项 | 对应流 | 通过标准 |
|---|---|---|
| 模块独立 | TF1 / TF2 / TF3 / TF4 | `prefs-store.js` 不依赖 DOM、不依赖 Engine 实例，可独立单测 |
| 异步非阻塞 | TF1 / TF2 / TF3 | 所有 prefs-store 写操作不阻塞 UI 线程和播放时钟 |
| 向后兼容 | TF4 | 旧版无 per-trackId 数据的用户升级后，所有曲目按默认值起播，不报错 |
| 构建通过 | 全部 | `npm run build` 无错误 |

## 5. DoD (Definition of Done)

- [ ] `src/storage/audio-store.js` — IndexedDB 基础封装（openDB / closeDB / getStorageEstimate）
- [ ] `src/storage/prefs-store.js` — per-trackId 偏好读写（save / load / delete / deleteAll）
- [ ] `switchTrack()` 切歌时先存后读偏好
- [ ] `startTimingLoop()` 中每秒写入一次 `currentTime`（节流，非每帧写入）
- [ ] `deleteTrack()` 和 `clearPlaylist()` 同步清理偏好
- [ ] IndexedDB 不可用时静默降级
- [ ] Web 版 24 项回归全部通过
- [ ] `npm run build` 通过
