# V1.4.1 任务拆分

## 1. 按 Transaction Flow 的任务列表

| 序号 | 流 | 任务 | 涉及文件 | 依赖 | 预估 |
|---|---|---|---|---|---|
| 1 | TF4 | 设计并实现 IndexedDB 可用性探测与静默降级 | `src/storage/audio-store.js`、`src/storage/prefs-store.js` | 无 | 0.5d |
| 2 | TF1 | 实现切歌时先存后读偏好 | `src/engine/playback-controller.js`、`src/storage/prefs-store.js` | TF4 | 1d |
| 3 | TF2 | 在 timing loop 中节流写入 currentTime | `src/engine/playback-controller.js`、`src/storage/prefs-store.js` | TF4 | 1d |
| 4 | TF3 | 删除轨道与清空列表时清理偏好 | `src/engine/playlist-manager.js`、`src/engine/core-engine.js`、`src/storage/prefs-store.js` | TF4 | 0.5d |
| 5 | 全部 | 补单测与回归用例 | tests/ 对应目录 | TF1-TF4 | 1d |
| 6 | 全部 | 本地构建与回归验证 | `package.json`、CI 配置 | 全部 | 0.5d |

## 2. 执行顺序

- 推荐先做哪些流：先做 TF4，再做 TF1 / TF2 / TF3。
- 哪些任务可以并行：TF1 与 TF2 的实现可以并行，但需共享 prefs-store 接口定义。
- 哪些任务必须串行：TF4 必须先完成，否则后续保存/恢复逻辑没有兜底。
