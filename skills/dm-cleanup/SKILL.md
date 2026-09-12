---
name: dm-cleanup
description: Skill for tech-debt cleanup and repo hygiene outside any version/TF. Scans code and repo by priority tiers, converges risky decisions explicitly (§7), fixes in place, validates (lint 0 + tests pass), then routes to dm-close-ver. Explicitly triggered via /dm-cleanup.
---

# dm-cleanup

## Overview

A tech-debt cleanup and repo-hygiene skill. It owns **standalone cleanup work outside any version / TF**: scans code and repo by priority tiers, converges risky decisions explicitly, fixes in place, validates, and finally routes to version close. Modeled on the PochiHide `VisionDetector.swift` cleanup.

## Responsibility Boundaries

| Responsibility | Owner |
|----------------|-------|
| Priority-tiered scan + list findings with tiers | ✅ this skill |
| In-place fixes (correctness / comments / dead code / duplicate structure / placeholder-constant labeling) | ✅ this skill |
| Repo hygiene (`.gitignore` rules + `git rm --cached` for wrongly-committed files) | ✅ this skill |
| Validation (lint 0 errors + relevant tests pass) | ✅ this skill |
| Version close (merge / close Issue / clean branch / commit & push) | delegate dm-close-ver |

> **Routing rule**: This skill only handles **standalone cleanup that cannot be attributed to a version TF** (one-off tech debt, cross-file refactor, repo hygiene). If the cleanup clearly belongs to a version TF, point to `dm-dev-tf` — this skill does not take over its dev flow, to avoid overlapping with the TF chain.

## Triggers

- `/dm-cleanup`
- "clean up tech debt"
- "do some repo hygiene"
- "refactor cleanup + gitignore tidy"

> Explicit trigger only; no natural-language auto-match, to avoid conflicting with other skills.

## Core Concepts

### Priority Tiers

Scan and fix by impact/risk, highest first:

| Tier | Focus | Typical action |
|------|-------|----------------|
| 🔴 High | Correctness bugs (tested fn never called, coord out of range, flip regression) | Make the pure function actually called, clamp output, add regression assertions |
| 🟡 Medium | Stale comments, ambiguous placeholder constants, repo hygiene (wrongly committed files / missing .gitignore) | Align comments to ADR, label placeholder-constant status, `git rm --cached` + add ignore |
| 🟢 Low | Test / structure duplication | Extract helper, unify call style, rename misleading test method |

### Decision Convergence §7

Risky decisions must follow skill-doc-principles §7 "AI asks → user answers → persist" — never assume. Two mandatory convergence points in this skill:

- **Wrongly-committed files**: use `git rm --cached` (keep local physical file) to make it ignored, or delete the physical file? Deleting is destructive — must ask the user first.
- **Placeholder-constant enablement**: are placeholder constants (e.g. `appGroupID` / `defaultStickerKey`) currently enabled? If not, label them explicitly so readers don't mistake them as active; whether to trigger `dm-adr` is the user's call — this skill does not auto-record.

### Reuse Existing Pure Functions

When cleaning, prefer reusing pure functions that already exist and are tested (e.g. `flipYToUIKit`, `clampedNormalized`) instead of writing duplicate logic. Test: **tested AND should be used** — if a pure function is covered by tests but never called on the main path, make it actually take effect rather than copying the formula again.

### Two-End Consistency

- Chinese design doc `skills/dm-cleanup.md` ↔ English deploy `~/.codebuddy/skills/dm-cleanup/SKILL.md`, chapters map 1:1, language differs only.
- Any change to core concepts / rules on either end must sync the other.

## Execution Flow

### 1. Receive & Route Check

Read the cleanup request; decide if it is **standalone cleanup outside a version / TF** (yes → this skill; if it belongs to a TF → point to `dm-dev-tf`).

### 2. Priority Scan

Read target files / repo, list findings by "Priority Tiers" (tier + file + problem + expected fix) into a scan checklist. Mark repo-hygiene items separately (current `.gitignore`, whether any wrongly-committed file is tracked).

### 3. Decision Convergence

Explicitly ask on risky items (delete physical file or not; placeholder enablement), collect answers and apply in place — **never assume**.

### 4. Fix by Priority

- 🔴 High: make pure functions actually called, clamp output, add regression assertions.
- 🟡 Medium: align comments to ADR, label placeholder status, `git rm --cached` keep-local + add `.gitignore`.
- 🟢 Low: extract helper, unify style, rename misleading test method.

### 5. Validate

- lint 0 errors.
- Relevant tests pass (e.g. iOS: `xcodebuild test`, confirming refactor didn't break behavior, especially coord-range assertions).
- Implicit contract-debt scan: during cleanup, if you find empty `catch` swallowing errors, magic numbers masquerading as contracts, unlabeled idempotency/invariants, or "silently swallowed dangerous failures / relying on return-value fallback", flag them as "implicit contract debt" and record in the scan list (contract-quality baseline: `docs/06-contract-based-dev.md` §2.5; failure-face contract: §2.7). In particular, "silent swallow / empty catch / bare print / relying on return-value fallback" are observability debts (ODD); during cleanup, add `observe` structured diagnosis per `docs/07-observability-driven-dev.md` §2.1/§3 (with Input Snapshot / Resource Metrics, `#if DEBUG` isolated) so AI can locate in one pass.

### 6. Repo Hygiene Wrap-up

- Append `.gitignore` rules (e.g. `generated-images/`, `*.xcsettings` wrongly-committed items).
- For wrongly-committed files: `git rm --cached <path>` (keep physical file) so it becomes ignored; untracked items just need an ignore rule and won't pollute status — no deletion needed.

### 7. Route

After cleanup passes validation, delegate `dm-close-ver` for version close (merge / close Issue / clean branch / commit & push); if this cleanup isn't tied to a version, `dm-close-ver` decides how to land it.

## Key Rules

| Rule | Source |
|------|--------|
| Only standalone cleanup outside version/TF; TF-attributable goes to dm-dev-tf | Responsibility Boundaries |
| Explicit trigger `/dm-cleanup`, no auto-match | Triggers |
| Fix by priority High→Medium→Low | Core Concepts·Priority Tiers |
| Must ask before deleting a wrongly-committed physical file | skill-doc-principles §7 |
| Placeholder enablement must be labeled explicitly, no auto ADR | skill-doc-principles §7 |
| Prefer reusing existing pure functions, no duplicate logic | Core Concepts·Reuse Pure Functions |
| Gate: lint 0 + relevant tests pass before routing close | Execution Flow·Validate |
| Chinese doc and English SKILL.md stay structurally consistent | Core Concepts·Two-End Consistency |
| Every contract must record four elements (owner/direction/invariant/provenance) + domain-seq id; quality dimensions land as invariant items | docs/06-contract-based-dev.md §2.6 |
| Failure-face contract: pure-function failures return empty/original, not nil; never silently swallow dangerous failures — intercept before call and expose explicitly | docs/06-contract-based-dev.md §2.7 |
| Observability debt: silent swallow / empty catch / bare print / relying on return-value fallback = implicit contract debt; during cleanup, add observe structured diagnosis per 07 §2.1/§3 | docs/07-observability-driven-dev.md |
| Contract evolution governance: breaking changes go through dm-adr; label pure-incremental PRs; new interfaces written back to the master catalog (orphan-doc guard) | docs/06-contract-based-dev.md §5 |

## Resource Mapping

| Resource | Source | Purpose |
|----------|--------|---------|
| `skills/dm-cleanup.md` | — | Chinese design doc (8-chapter skeleton) |
| `~/.codebuddy/skills/dm-cleanup/SKILL.md` | — | English deploy version (two-end aligned) |

> This skill needs no extra assets templates — kept lightweight (same shape as `dm-grillme-plan`).

## Example

```
User: "/dm-cleanup clean up VisionDetector.swift and repo hygiene together"

AI:  1. Route check: standalone cleanup (not a TF) → this skill
     2. Priority scan checklist:
        🔴 [VisionDetector.swift] detect hand-rolls flip, never reuses flipYToUIKit → call the pure fn
        🔴 [VisionDetector.swift] clampedNormalized tested but unused → clamp detect output to [0,1]
        🟡 [3 comments] <15MB / .fast default contradict code → align to ADR-001 / ADR-004
        🟡 [SharedConfig] ambiguous placeholder constants → label appGroupID/defaultStickerKey disabled, downsampleMaxDimension enabled
        🟡 [repo hygiene] WorkspaceSettings.xcsettings wrongly committed + generated-images/ not ignored
        🟢 [tests] warm-up duplicated → extract detectSteadyState; testPeakMemoryUnder15MB is actually 30MB steady → rename testSteadyStateMemoryUnderLimit
     3. Decision convergence:
        Q WorkspaceSettings.xcsettings wrongly committed — keep local file or delete physical?
        → User: keep local, only remove from git
        Q Are placeholder constants enabled now?
        → User: appGroupID/defaultStickerKey disabled (label them), downsampleMaxDimension enabled
     4. Fix by priority
     5. Validate: lint 0 errors; xcodebuild test 6 cases 5 passed + 1 skipped + 0 failures
     6. Repo hygiene: .gitignore adds generated-images/ + *.xcsettings; git rm --cached WorkspaceSettings.xcsettings (local kept)
     7. Route: delegate dm-close-ver to close
```
