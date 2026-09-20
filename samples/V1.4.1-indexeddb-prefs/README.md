# V1.4.1-indexeddb-prefs Sample

这组 samples 按 `docs/02-version-rules.md` 的结构生成，用于展示如何把一个版本的四件套（spec / design / build / schedule）写成可执行文档。

## 文件

- `200-spec.md` — 核心业务场景、架构锚点与验收标准（**不含任何 Step / TF 章节**）
- `300-design.md` — 全局架构与分层、防腐设计、数据流与状态机、关键决策（**不含任何 Step / TF 章节**）
- `400-build.md` — **唯一**承载 `Step 0–7` 施工清单与明细的文档，含 `GUARD-0x` 防腐契约与自检
- `500-schedule.md` — 工作包排程（dev 工作包以 **Step** 为原子单位，含环节与执行记录）

## 结构要点

- 版本只承载**单一核心业务场景**（per-trackId 偏好持久化），故不再划分 Transaction Flow。
- `Step 0–7` 为固定工序：条件步（本例 `S3`）以 `⏭️ SKIPPED` + 理由标注，且**不排工作包**。
- `S4`（Ingress）/ `S5`（Egress）**各只出现一次** —— 版本粒度红线的硬判据（`docs/02` §3.2）。
