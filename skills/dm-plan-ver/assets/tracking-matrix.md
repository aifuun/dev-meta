# 📋 版本追踪矩阵

> 用于追踪版本内各 **Step** 从创建到合并、验收的完整状态。
> **版本 Issue 唯一**（命名 `[vX.Y] <feature-name>`，正文含 Step 0–7 checklist）；
> 矩阵的行以 Step 为单位，Issue / PR 列填该版本唯一的那一个。

## 追踪矩阵

| Step | Issue | PR | 验收结果 |
|------|-------|-----|----------|
| S0 Scaffold & Clean | #xx | #xx | ⬜ |
| S1 Contract & ADR | #xx | #xx | ⬜ |
| S2 Core & Prototype | #xx | #xx | ⬜ |
| S3 Standard Finalization | #xx | #xx | ⬜ |
| S4 Ingress Migration | #xx | #xx | ⬜ |
| S5 Egress Migration | #xx | #xx | ⬜ |
| S6 Guards & Tests | #xx | #xx | ⬜ |
| S7 Verification & Close | #xx | #xx | ⬜ |

> 状态：⬜ 待开始 / 🔄 进行中 / ✅ 已完成 / ⏭️ 已跳过（对应 `400-build` §2 的 `⏭️ SKIPPED`）

## 维护时机

1. **版本创建时**：生成**唯一**版本 Issue（标题 `[vX.X] <feature-name>`，正文含 Step 0–7 checklist），关联到版本 PR，填入矩阵。
2. **Step 完成时**：确认验收标准 → commit（subject 末尾 `(S<n>)` + **`Refs #<版本 Issue>`**，由用户触发）→ 更新矩阵该 Step 为 ✅ → 勾选版本 Issue checklist → 回写 `500-schedule.md` 执行记录。
3. **版本关闭时**：检查全部 Step 已完成或已标记跳过、矩阵全 ✅，再输出 merge 建议。
