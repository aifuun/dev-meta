---
name: dm-dev-tf
description: This skill should be used when the user wants to start development on a specific Transaction Flow (TF). It reads the relevant version documents (spec, design, build), confirms or creates the TF Issue, and outputs a development brief with goals, key files, dependencies, and test strategy. Development happens on the existing version branch; branch create/delete is not handled here.
---

# dm-dev-tf — TF Development Bootstrap

Start development on a specific Transaction Flow. Reads all version documents to gather TF context, confirms or creates the TF GitHub Issue, and outputs a development brief. Development proceeds on the current version branch — dm-dev-tf does not create or delete branches.

## Responsibility Boundary

| Responsibility | Owner |
|----------------|-------|
| Read version docs, extract TF context | ✅ This skill |
| Confirm/create TF Issue | ✅ This skill |
| Output development brief | ✅ This skill |
| Branch create/delete | Version-scope (dm-plan-ver), not this skill |
| TF commit | Delegate dm-commit |

## Relationship

dm-dev-tf sits within dm-plan-ver's Phase 2 (TF Development):

```
dm-plan-ver (version plan)
  └── Phase 2: TF Development
        ├── dm-dev-tf — TF start (this skill)
        └── dm-commit — TF commit
```

## When to Use

- User says "start TF3"
- User says "develop TF2"
- User says "/dm-dev-tf 3"
- User says "/dm-dev-tf 3 auth-session" (with topic hint)
- User says "开始开发 TF1"

## Core Concepts

### TF Context Sources

The four version docs each offer a different perspective for the TF brief:

| Document | Provides |
|----------|----------|
| `500-schedule.md` | Work package status for this TF |
| `200-spec.md` | This TF's business goal, acceptance criteria, acceptance anchors |
| `300-design.md` | TF data flow, dependencies on other TFs, cross-TF state machine sections, test strategy for this TF |
| `400-build.md` | TF steps, function signatures, schemas, single-TF state machines / sequence diagrams, execution order matrix |

### Development Branch

- Develop directly on the **current version branch** `feature/vX.Y-<slug>`, **do not create/delete branches**.
- Branch create/delete is version-scope (dm-plan-ver); TF level only develops on it.

## Workflow

### Step 1: Detect Version

Look under `docs/versions/` to find the current active version directory. If multiple versions exist, ask the user which one. If none exist, instruct the user to run dm-plan-ver first.

### Step 2: Read TF Context

From `docs/versions/vX.Y-<slug>/`, extract TF-specific content per Core Concepts.

### Step 3: Confirm/Create TF Issue

- If the TF Issue already exists (from dm-plan-ver Phase 1), confirm its number and state
- If not yet created, output the Issue body: title `[TFx] <flow-name>`, with goal, completion criteria, dependencies, verification method

### Step 3.5: Implementation Grill (only when docs are incomplete)

Check `300-design.md` for the completeness of this TF's design. If gaps exist (data flow, module boundaries, error handling, compatibility, etc. undefined), ask **3-5 decisive decision points targeting the gaps** (do not repeat content already in the docs); persist answers into the brief or the corresponding doc section; route tech-choice answers to `dm-adr`. If `300-design.md` already fully covers this TF, skip this step.

> Principle: skill-doc-principles §7 "Explicit Decision Convergence".

### Step 4: Output Development Brief

Summarize in a structured brief:

```
## TF<N> Development Brief — <flow-name>

**Goal**: <one-line goal from 200-spec.md>
**Branch**: feature/v<X.Y>-<slug> (current version branch, do not create a new one)
**Issue**: #<N>

### Key Files
- <file> — <purpose>
- ...

### Dependencies
- Previous TFs: <list or "none">
- External: <list or "none">

### Test Strategy
- Level: <unit / integration / e2e>
- Key scenarios: <from 300-design.md>
- Invariants: <from 400-build.md Key Behavior Contract invariants; "none" if none>

### Steps (from 400-build.md, includes deploy/integrate stages)
1. <step>
2. <step>
...
```

## Key Rules

| Rule | Source |
|------|--------|
| Never assume the version — always detect from `docs/versions/` | — |
| Develop directly on the current version branch; **do not create/delete branches** | 03-git-flow-rules §4 |
| TF dev steps include deploy/integrate stages (belong to dev, not qa) | 02-version-rules §2.2 |
| If `400-build.md` is incomplete, flag it in the brief | 02-version-rules |
| If `300-design.md` is incomplete for this TF, run the implementation grill before the brief; persist Q&A into docs | skill-doc-principles §7 |
| Delegate commits to dm-commit; this skill only handles the bootstrap phase | dm-commit |
| Every contract must record four elements (owner/direction/invariant/provenance) + domain-seq id; quality dimensions land as invariant items | docs/06-contract-based-dev.md §2.6 |
| Failure-face contract: pure-function failures return empty/original, not nil; never silently swallow dangerous failures — intercept before call and expose explicitly (implicit-contract-debt check §2.7) | docs/06-contract-based-dev.md §2.7 |
| Contract evolution governance: breaking changes go through dm-adr; label pure-incremental PRs; new interfaces written back to the master catalog (orphan-doc guard) | docs/06-contract-based-dev.md §5 |
| Diagnostic contract: behavior expectations come from 400-build; error/degradation paths need structured diagnosis (07 §2.1/§3), high-cost nodes (inference/IO/cross-process) must include Elapsed Time + resource metrics (07 §2.3); reuse observe wrapper (07 §4), no silent swallow | docs/07-observability-driven-dev.md |
| Micro-Batching: within a TF, advance in three batches (contract/data model → Core single file → UI/call site); AI execution granularity = single-file refactor / single-function fix; each green batch is committed only when the user triggers it; on chaos the user runs `git reset --hard` to the last green commit (AI never自发), then New Session | docs/08-small-batch-iteration.md |

## References

- `../dm-plan-ver/references/version-rules.md` — Version document structure, TF content boundaries, stage definitions
- `../dm-plan-ver/references/git-flow-rules.md` — Issue/PR conventions (branch lifecycle is version-scope)
- `../dm-commit/references/git-flow-rules.md` — Commit format rules

## Example

```
User: "start TF3"

AI:  1. Detect version: docs/versions/v0.2-auth/ → v0.2 (current branch feature/v0.2-auth)
     2. Read the four docs, extract TF3 content
     3. Confirm Issue #15 [TF3] Session management → created, open
     4. Output development brief (no new branch; develop directly on feature/v0.2-auth):
        ## TF3 Development Brief — Session Management
        **Goal**: implement token issuance, validation, and refresh
        **Branch**: feature/v0.2-auth (current version branch, do not create a new one)
        **Issue**: #15
        ### Key Files
        - src/auth/session.ts — session management core logic
        - src/auth/token.ts — JWT issuance and validation
        ### Dependencies
        - Previous TFs: TF2 validation flow
        - External: none
        ### Test Strategy
        - Level: unit
        - Key scenarios: token expiry refresh, concurrent request dedup
        ### Steps
        1. Implement token issuance
        2. Implement token validation middleware
        3. Implement refresh concurrent dedup
```
