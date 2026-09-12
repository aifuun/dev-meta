---
name: dm-grillme-plan
description: Skill for general (non-version) requirements. Before writing code or a solution, run an explicit "question → answer → persist" grill loop as a picky architect to surface hidden assumptions, then output a reusable Final Plan. Tech-choice answers route to dm-adr.
---

# dm-grillme-plan

## Overview

A Plan-phase decision-grill skill for **general (non-version) requirements**. Before writing code or a solution, it converges key decisions through an explicit "AI asks → user answers → persist to doc" loop and outputs a reusable Final Plan. Tech-choice answers are handed off to `dm-adr`.

## Responsibility Boundaries

| Responsibility | Owner |
|----------------|-------|
| Grill decision points + converge into Final Plan | ✅ this skill |
| Persist Final Plan to `docs/plans/<topic>-grill.md` | ✅ this skill |
| Record tech-choice answers as ADR | delegate dm-adr |
| Coding / implementation | delegate to the relevant implementation skill |
| Commit | delegate dm-commit |

> **Two-track split**: This skill handles only **non-version general requirements** (one-off scripts, standalone refactors, cross-project design reviews). **Version-level** planning uses the **embedded** grill in `dm-plan-ver` (requirements/architectural level) and `dm-dev-tf` (implementation level) — not this track — to avoid maintaining grill logic in three places.

## Triggers

- `/grill-me`
- "grill me before planning"
- "pressure-test this plan first"
- "challenge the key decisions on this new requirement"
- receiving a new requirement / initial plan and wanting to converge before acting

## Core Concepts

### Three-Stage Loop

This skill is the **general (non-version) instance** of skill-doc-principles §7 "Explicit Decision Convergence". Every decision point follows:

```
AI asks → user answers → persist to doc
```

Never rely on the AI answering its own questions; Q&A must not live only in the chat stream.

### Three Question Levels

Focus by requirement maturity; each round takes only **3-5 decisive decision points** (do not repeat what the user already stated):

| Level | Focus | Example questions |
|-------|-------|------------------|
| Goal/boundary | scope / done criteria / exclusions / degradation | Where are the delivery boundaries? What counts as done? What is explicitly out of scope? How to degrade when info is incomplete? |
| Architecture/tech | data flow / module boundary / error handling / compatibility / tech choice | How does data flow? Module boundaries? Error handling? Backward compatibility? Tech choice? |
| Implementation/degradation | concurrency limits / dependency integration / test strategy / **observability blind spots** | Concurrency boundaries? How to integrate external deps? How is testing covered? **Observability blind spots: do error/degradation paths have structured diagnosis (07 §2.1/§3)? any silent swallow / bare log? do high-cost nodes include elapsed + resource metrics (07 §2.3)?** |

### Final Plan Structure

The single source of truth is `assets/grill-plan-template.md`. Fields: goal, scope, done criteria, degradation strategy, key decision Q&A, follow-up actions (with ADR links).

### Relation to §7

- §7 mandates "decision points need explicit ask→answer→persist"; this skill is its **general / non-version** execution form.
- The version-level equivalent is already embedded in `dm-plan-ver` / `dm-dev-tf`; this skill does not redefine or re-trigger it.

## Execution Flow

### 1. Receive Requirement

Read the new requirement or initial Plan; decide if it is a **non-version general requirement** (yes → this skill; no → point to the embedded grill in `dm-plan-ver` / `dm-dev-tf`).

### 2. Grill Questions

Act as a picky architect; raise **3-5 decisive decision questions** (focused per "Three Question Levels", not repeating what the user already stated); **do not write code or the final solution**.

### 3. User Answers

Collect answers; if a major decision is unconverged, allow at most one more round (≤2 rounds total) to avoid process burden.

### 4. Converge into Final Plan

Output the Final Plan per `assets/grill-plan-template.md` (goal / scope / done criteria / degradation strategy / key decision Q&A).

### 5. Persist Document

Create `docs/plans/<topic>-grill.md` (create the directory on demand if missing) and write the Final Plan.

### 6. Route Forward

- Tech-choice answers → delegate `dm-adr` to record an ADR; link it in the Final Plan.
- Coding requirements → hand to the relevant implementation skill.
- Commit → delegate `dm-commit`.

## Key Rules

| Rule | Source |
|------|--------|
| This skill handles only non-version; version-level uses dm-plan-ver / dm-dev-tf embedded grill | skill-doc-principles §7 |
| 3-5 decisive points per round, no repetition of stated facts | skill-doc-principles §7 |
| Grill stage produces no implementation code / final solution | skill-doc-principles §7 |
| Q&A must be persisted into the Final Plan doc, not left in chat | skill-doc-principles §7 |
| Tech-choice answers trigger dm-adr | skill-doc-principles §7 |
| Grill must surface observability blind spots: silent swallow / no structured diagnosis / bare logs must be flagged in the Final Plan, referencing docs/07-observability-driven-dev.md | docs/07-observability-driven-dev.md |
| Final Plan structure's single source of truth is assets/grill-plan-template.md | — |

## Resource Mapping

| Resource | Source | Purpose |
|----------|--------|---------|
| SKILL.md | — | flow instructions + rule reference |
| assets/grill-plan-template.md | — | blank Final Plan template |

## Example

```
User: "/grill-me I want a script to sync my weekly Notion tasks into my calendar"

AI:  1. Classify: non-version general requirement → this skill
     2. Grill questions (architecture/tech + goal/boundary):
        Q1 Sync direction: one-way (Notion→calendar) or two-way? How to resolve two-way conflicts?
        Q2 How are "weekly tasks" defined? filter by database / tag / a specific view?
        Q3 Which calendar? Google / Apple / Feishu? Auth method (local OAuth token?)?
        Q4 Failure degradation: API rate limit / network blip — manual fallback?
        Q5 Trigger: local cron / cloud function / manual?
     3. User: one-way, filter by "weekly" tag view, Google Calendar OAuth, skip+notify on rate limit, local cron daily 7am
     4. Converge into Final Plan
     5. Persist docs/plans/notion-calendar-sync-grill.md
     6. Route: tech choice (Google Calendar API) → suggest dm-adr; coding → relevant implementation skill
```
