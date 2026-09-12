---
name: dm-report
description: This skill should be used when the user wants to generate a periodic report (default: weekly) from the project worklog. Target audience is PM / product manager — the report focuses on feature delivery and milestone progress, not code or commit details.
---

# dm-report — Periodic Report Generator

Generate a structured periodic report from the project worklog. Default reporting period is the current week (Mon–Sun). Supports custom date ranges for other reports (monthly, sprint, etc.).

**Target audience**: PM / product manager. Reports focus on feature delivery, milestone progress, and what was accomplished — not code details, commit hashes, or implementation specifics.

## When to Use

- User says "生成周报"
- User says "本周报告" / "上周报告"
- User says "generate weekly report"
- User says "report this week"
- User says "这个月的报告" (monthly)
- User says "汇报" with a date range

## Workflow

### Step 1: Locate the Worklog

Read `docs/reports/worklog.md` in the current project. If the file does not exist, report that no worklog is available and suggest using dm-log to start recording.

### Step 2: Determine the Reporting Period

Default: **current week** (Monday to Sunday of the current week). If today is Sunday, default to the current week (not next week).

When the user specifies a different period:
- "上周" → previous Monday to Sunday
- "本月" → 1st to today (or last day of month)
- "上个月" → 1st to last day of previous month
- Custom range → "YYYY-MM-DD 到 YYYY-MM-DD"

### Step 3: Extract Relevant Entries

Parse `reports/worklog.md` and extract:

1. **Daily summaries** — rows from the `## 每日工作总结` table whose dates fall within the reporting period; merge into task list without dates
2. **Detailed logs** — the `## YYYY-MM-DD` sections; extract feature-level deliverables and decisions, ignore commit hashes, dates, and implementation details
3. **TODO changes** — items whose status changed during the period (compare with previous state; if that history is unavailable, list current pending/in-progress items)
4. **Milestones** — any milestones dated within the period

### Step 4: Generate the Report

Output a Markdown report following this structure:

```markdown
# <Period> 工作报告

> 生成时间：<now> | 数据来源：worklog.md

## 1. 已完成任务

- task from daily summaries and detailed logs
- describe in user-facing terms (what PM / users can now do)
- do NOT include dates in descriptions

## 2. 功能交付

- bullet list of features / capabilities delivered this period
- describe in user-facing terms (what PM / users can now do)

## 3. 关键决策与讨论

- important decisions made
- design discussions and conclusions
- scope changes or trade-offs

## 4. 待办进展

- list of TODO items that changed or are in progress
(if no changes, write "无变化")

## 5. 里程碑

- milestones achieved this period

(If none, write "本周期无新增里程碑")

## 6. 下阶段计划

- planned features / deliverables for next period
- priority order, from PM / product perspective
```

### Step 5: Save the Report

Save the generated report to `docs/reports/weekly-YYYY-MM-DD.md` (using today's date). For non-weekly reports, use `docs/reports/report-YYYY-MM-DD.md` (also using today's date).

### Step 6: Output to User

Present the report content to the user directly in the conversation. After presenting, ask whether to commit the report file:
- If confirmed, refer to dm-commit skill.

## Key Rules

| Rule | Source |
|------|--------|
| Default period is Mon–Sun of current week | — |
| Report MUST be based on `reports/worklog.md` data | worklog-rules.md |
| Do NOT fabricate work entries not present in the worklog | worklog-rules.md |
| Do NOT include commit hashes, code details, or implementation specifics | — |
| Do NOT include specific dates in report sections — just list completed tasks | — |
| Write in feature / user-facing language — target PM audience | — |
| If worklog is empty or has no entries in period, report that clearly | — |
| Report file named with today's date: `docs/reports/weekly-<today>.md` / `docs/reports/report-<today>.md` | — |

## References

- `references/worklog-rules.md` — Worklog file structure and record format specification.

## Assets

- `assets/report-template.md` — Weekly report template for direct use.
