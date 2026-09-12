---
name: dm-adr
description: This skill should be used when the user wants to record, update, or discuss architecture/technology decisions. It enforces the ADR (Architecture Decision Record) format: title, status, context, decision, consequences. Use it for tracking tech choices like cloud providers, TTS services, domains, frameworks, or any infrastructure-level decision.
---

# dm-adr — Architecture Decision Records

Maintain a structured log of technical decisions under `docs/adrs/`. Each ADR is a **single file** named `adr-NNN.md`, with `README.md` serving as the directory index.

## Responsibility Boundary

| Responsibility | Owner |
|----------------|-------|
| Generate/maintain ADRs | ✅ This skill |
| ADR index (`docs/adrs/README.md`) | ✅ This skill |
| ADR commit | Delegate dm-commit |

## When to Use

- User says "record a tech decision"
- User says "create an ADR"
- User says "add a decision"
- User announces a new technical choice (e.g., "we'll use X for Y")
- User asks to review or update an existing decision
- User asks "why did we choose X?" — reference existing ADRs

## Core Concepts

### ADR Five-Section Format

Each ADR follows a fixed five-section structure; one ADR records one decision:

| Section | Content |
|---------|---------|
| 背景 Context | Why this decision is needed |
| 决策 Decision | What we chose |
| 原因 Rationale | Why this option (key trade-offs) |
| 后果 Consequences | ✅ positives / ⚠️ costs / 🔧 follow-ups |
| 替代方案 Alternatives | rejected options (optional) |

```markdown
# ADR-NNN: 标题（简短名词短语）

- **状态**: 提议中 (Proposed) / 已接受 (Accepted) / 已废弃 (Deprecated) / 已替代 (Superseded by ADR-NNN)
- **日期**: YYYY-MM-DD

## 背景     — 为什么需要做这个决策
## 决策     — 明确陈述选择了什么方案
## 原因（可选）— 为什么选它而非其他方案
## 后果     — ✅ 正面 / ⚠️ 代价 / 🔧 跟进
## 替代方案（可选）— 被否掉的方案表
## 相关     — 相关文档 / ADRs / Issues
```

### Status Transitions

ADR has a lifecycle; an accepted ADR's original text is immutable:

```
Proposed ──→ Accepted ──→ Deprecated
                    │
                    └──→ Superseded (by ADR-NNN)
```

- **Proposed**: 提议中，正在讨论，尚未实施
- **Accepted**: 已接受，已开始实施
- **Deprecated**: 已废弃，不再适用
- **Superseded by ADR-NNN**: 被新的 ADR 替代，在记录中注明替代者

## File Structure

```
docs/adrs/
├── README.md        # 导航索引（表格 + 按领域分类）
├── adr-001.md       # 独立决策文件
├── adr-002.md
└── ...
```

## Workflow

### Step 1: Determine the Next ADR Number

List files in `docs/adrs/` matching `adr-*.md`. The next number is highest existing + 1.

If the directory doesn't exist, create it with `README.md` and start from ADR-001.

### Step 2: Assess the Decision

Ask clarifying questions if needed:

- What is the decision about? (domain)
- What alternatives were considered?
- What are the key trade-offs?
- What documents/decisions does this relate to?

### Step 3: Draft the ADR

Write the ADR following the five-section format above. Keep it concise — an ADR is a decision log, not a design doc.

### Step 4: Create the File

Create `docs/adrs/adr-NNN.md` with the ADR content.

### Step 5: Update README.md

Add the new ADR to the table in `docs/adrs/README.md`, and update the "按领域浏览" section if it fits an existing or new category.

### Step 6: Update Affected Documents

If this decision supersedes an earlier one, update the old ADR's status to `已废弃 (Deprecated, superseded by ADR-NNN)` and cross-reference.

### Step 7: Commit

Delegate to `dm-commit` skill. Use format:
```
docs(adr): add ADR-NNN — <decision title>
```

## Key Rules

| Rule | Source |
|------|--------|
| Every significant technical decision gets an ADR | — |
| One decision per ADR | — |
| ADRs are immutable once accepted; update status (Deprecated/Superseded), never rewrite | — |
| Cross-reference superseding decisions bidirectionally | — |
| File location is always `docs/adrs/adr-NNN.md` | — |
| Observability architecture trade-offs (sampling granularity / computeUnits / precompiled model / diagnostic tiering) must go through ADR | docs/07-observability-driven-dev.md §6 |
| Commit delegate dm-commit: `docs(adr): ...` | dm-commit |

## References

- `references/adr-format.md` — 完整的 ADR 格式规范与字段说明，当需要确认字段定义或格式细节时加载。
- `assets/adr-template.md` — 新建 ADR 的空白模板，可直接复制使用。
