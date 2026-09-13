---
name: dm-log
description: This skill should be used when the user wants to record daily work, update the worklog, or is asked about what they did today. It maintains the daily summary table, detailed log entries, TODO list, and milestones in the project's worklog file.
---

# dm-log — Daily Worklog

Maintain the project worklog: append daily summaries, detailed log entries, update TODOs, and track milestones following the dev-meta worklog specification.

## When to Use

- User says "record today's work"
- User says "update worklog"
- User implicitly references daily activities (e.g. "what did I do today")

## Workflow

### Step 1: Locate File

Find `docs/reports/worklog.md` in the current project. If it does not exist, create it from `assets/worklog.md`.

### Step 2: Append Daily Summary

Add a new row at the **top** of the `## 每日工作总结` table:

```markdown
| **YYYY-MM-DD** | One-line summary (key deliverables & issues) (更新了 n 次) |
```

If updating the same day, increment the `n` count.

### Step 3: Append Detailed Log (if new content)

Add a new section under `## 详细日志`:

```markdown
### YYYY-MM-DD

- **module/feature**: description of work done
- **module/feature**: description of work done
  - `abc1234` brief commit description (if commits exist)
```

List commits when applicable; otherwise record discussions, decisions, and operations under "其他工作".

### Step 4: Maintain TODO List

Update the `## 待办` table, adding/removing items and updating status with these markers:

| Marker | Meaning |
|--------|---------|
| ⬜ 待开始 | Not started |
| 🔄 进行中 | In progress |
| ✅ 已完成 | Done |
| ❌ 已取消 | Cancelled |

### Step 5: Update Milestones (On Demand)

If a notable milestone was reached, append to the `## 里程碑` table.

### Step 6: Commit

Commit the worklog update — refer to dm-commit skill. Example:
```
chore: update worklog — <one-line summary>
```

## Key Rules

- Daily summary rows are inserted at the top of the table.
- Commit references use `` `hash` `` format with Chinese descriptions.
- Each date gets one `###` section; multiple edits to the same day are allowed.
- Use consistent TODO status markers; do not mix styles.
- Never paste large raw logs, mark incomplete work as ✅, or contradict the summary with the details.

## References

- `references/worklog-rules.md` — Full worklog spec: file structure, commit format, anti-patterns.

## Assets

- `assets/worklog.md` — Worklog template for new projects.

## Example

```
User: "log today's work"

AI:  1. Read docs/reports/worklog.md
     2. Append a row to the daily summary table: | 2026-07-21 | add state machine layering rules... |
     3. Append the detailed log section:
        ### 2026-07-21
        - **version-rules**: design adds cross-TF state machine section
          - `42ee152` feat: design adds cross-TF state machine
        - **templates**: sync version and project templates
     4. Update todos: mark completed items, add new ones
     5. Output the change summary
```
