---
name: dm-plan-ver
description: This skill should be used when starting a new version. It manages version planning: creating the four version documents (spec, design, build, schedule), branch/PR creation, and TF issue generation. For per-TF development, delegate to dm-dev-tf. For closing a version, delegate to dm-close-ver.
---

# dm-plan-ver — Version Planning & Start

Plan and start the lifecycle of a version: version document creation, branch/PR creation, TF issue generation. Per-TF development is handled by dm-dev-tf; commit formatting by dm-commit; version close-out by dm-close-ver.

## Responsibility Boundary

| Responsibility | Owner |
|----------------|-------|
| Create four version docs + branch + PR + TF issues | ✅ This skill |
| Per-TF development bootstrap | Delegate dm-dev-tf |
| Commit formatting | Delegate dm-commit |
| Version close-out (merge / close issues / branch cleanup) | Delegate dm-close-ver |

## When to Use

- User says "create version v1.2-payment"
- User says "start vX.Y"
- User says "create TF documents"

## Core Concepts

### The Four Version Documents

Version directory `docs/versions/vX.Y-<slug>/` holds four docs, created in dependency order:

| Doc | Question it answers | Prerequisite |
|-----|---------------------|--------------|
| `200-spec.md` | What is delivered? What is done? | — |
| `300-design.md` | How are flows sequenced? How are modules split? | spec |
| `400-build.md` | How to implement? How to execute? | design |
| `500-schedule.md` | When and in what order? | build (delegate dm-schedule) |

### Execution Order Matrix (400-build §last)

The matrix at the end of 400-build carries **order, stage, and dependency constraints**:

| Column | Content |
|--------|---------|
| Seq | Recommended execution order, from 1 |
| Stage (环节) | Delivery stage (开发/部署/联调/测试/发布…), aligned with the schedule |
| TF | TF number (TF1/TF2…); wrap-up rows use "—" |
| Notes | Prerequisites, parallel hints, risk markers |

- **A dev TF's matrix rows must include code + deploy + integrate stages** (deploy/integrate are dev's, not qa's).
- Append fixed rows: "unit tests & regression" + "local build & regression verification".
- Task descriptions, effort estimates, and status live in `500-schedule.md` (not duplicated).
- Full stage definitions live in `dm-schedule`'s Core Concepts stage↔category table (single source of truth).

### Tracking Matrix

After generating an Issue for each TF, track TF→Issue→PR→acceptance state:

| TF | Issue | PR | Acceptance |
|----|-------|-----|-----------|
| TF1 | #xx | #xx | ⬜ |

### Grill Decision Convergence

Before producing key documents, run an explicit "question → answer → persist" loop on decisions that affect implementation/acceptance — **never rely on the AI answering its own questions** (principle: skill-doc-principles §7):

| Trigger point | Grill level | Scope of questions |
|---------------|-------------|--------------------|
| Before creating `200-spec.md` | Requirements | Scope boundaries, done criteria, degradation strategy, explicit exclusions |
| Before creating `300-design.md` | Architecture (most critical) | Data flow, module boundaries, error handling, compatibility, tech choices |

- Ask **3-5 decisive decision points** each time; do not repeat content already in the docs.
- Persistence: write decision answers into the corresponding doc section; route tech-choice answers to `dm-adr`; never leave Q&A only in the chat stream.

## Workflow

### Phase 1: Version Start (core)

```
User: "新建版本 v1.3-export"
```

1. **Create version docs** in `docs/versions/v1.3-export/` (the four docs, order per Core Concepts; run the requirements-level and architecture-level grills before producing `200-spec.md` and `300-design.md` respectively, see Core Concepts "Grill Decision Convergence")
   - **Requirements grill** (before `200-spec.md`): ask about scope boundaries, done criteria, degradation strategy, exclusions; persist answers into `200-spec.md`
   - Create `200-spec.md`
   - **Architecture grill** (before `300-design.md`): ask about data flow, module boundaries, error handling, compatibility, tech choices; persist answers into `300-design.md` (route tech-choice answers to `dm-adr`)
   - Create `300-design.md` and `400-build.md` (`400-build.md` execution order matrix arranged per `300-design.md` §3, each row labeled with its stage)

2. **Create branch**
   ```bash
   git checkout -b feature/v1.3-export
   ```

3. **Generate PR description**
   - Title: `[V1.3.0] Export to PDF`
   - Fill: goal, scope, acceptance entry point, risks & rollback
   - If user has `gh` CLI, create the PR directly

3.5 **Contract-gate self-check before opening TF Issues (Gate)**
   Before generating Issues (i.e. decomposing TFs into executable units), confirm `400-build.md` has satisfied the 06/07/08 baselines; otherwise go back and补 write, do NOT open Issues:
   - **06 Contract-Based Dev**: contains L1/L2/L3 behavior contracts, execution-order matrix with stages, no silent failure face, contract four-elements labeled (ownership/direction/invariant/provenance + domain-seq id, see `docs/06-contract-based-dev.md` §2.5/§2.6/§2.7/§3)
   - **07 Observability**: behavior contracts include diagnostic contract (key-path observe wrapper + state trace + no silent swallow, see `docs/07-observability-driven-dev.md` §2.1/§3/§7)
   - **08 Small-Batch**: plan decomposable into single-file batches (AI execution granularity = single-file refactor / single-function fix, see `docs/08-small-batch-iteration.md`)
   - Suggest running `dm-contract-gate` for static compliance check; this skill only **references** its conclusion (does not implement validation logic, does not delegate dev). If it fails, do not open Issues.

4. **Generate one Issue per TF**
   - Title: `[TF1] Data collection & preprocessing`
   - Fill: goal, done criteria, dependencies, acceptance method
   - Link to version PR, output tracking matrix

### Phase 2: TF Development (delegated)

TF development is chained through two sub-skills; this skill does not run it directly:

- **dm-dev-tf** — TF start: read docs, create/confirm issue, output dev brief (develops on the version branch, no branch create)
- **dm-commit** — TF commit: `type(scope): subject` + `Closes #id`

```
User: "TF1 完成了"
```

1. **Confirm acceptance**: against the TF's acceptance criteria in `200-spec.md`
2. **Run commit** — delegate to dm-commit, format:
   ```text
   feat(export): collect and preprocess data for PDF export
   
   Closes #42
   ```
3. **Close the TF issue** (annotate acceptance result)
4. **Update `500-schedule.md`** work package status + tracking-matrix

### Phase 3: Version Close-out (delegated)

```
User: "关闭版本 v1.3-export"
```

When the user wants to close a version, delegate to **dm-close-ver**. This skill no longer handles close-out; dm-close-ver owns the full flow (readiness audit → wrap-up → merge preserving history → close TF issues → branch cleanup → post-close verify).

## Key Rules

| Rule | Source |
|------|--------|
| TF numbers must remain stable; deprecate with `[DEPRECATED]` tag, never renumber | 02-version-rules §3.1 |
| design governs TF-level; build governs step-level | 02-version-rules §3.3 |
| Cross-TF state machines in design; single-TF in build | 02-version-rules §3.4 |
| One PR per version, one Issue per TF | 03-git-flow-rules §2 |
| Commit: `type(scope): subject` + `Closes #id` — see dm-commit | 03-git-flow-rules §3 |
| Branch: `feature/v<version>-<slug>` (version-level; TF does not create a branch; develop on the version branch) | 03-git-flow-rules §4 |
| Close-out: delegate dm-close-ver (merge preserves history, no squash) | dm-close-ver |
| Execution order matrix rows carry stages; dev TF includes code+deploy+integrate | 02-version-rules §2.2 |
| Run requirements/architecture grills before producing `200-spec.md`/`300-design.md`; persist Q&A into docs, never in chat only | skill-doc-principles §7 |
| `400-build.md` must include "Key Behavior Contract (key test cases)" for algorithm/implicit-contract functions (idempotency, concurrency dedup, error branches, degradation); thin glue/CRUD may omit. Test-responsibility split: docs/06-contract-based-dev.md §3 | templates/versions/vX.Y-<slug>/400-build.md + docs/06-contract-based-dev.md §3 |
| `400-build.md` must cover contract-quality-baseline dimensions (error/idempotency/compat/invariant etc., see docs/06-contract-based-dev.md §2.5); missing dimensions must be filled in grill/design phase | docs/06-contract-based-dev.md §2.5 |
| Every contract must record four elements (owner/direction/invariant/provenance) + domain-seq id; quality dimensions land as invariant items | docs/06-contract-based-dev.md §2.6 |
| Failure-face contract: pure-function failures return empty/original, not nil; never silently swallow dangerous failures — intercept before call and expose explicitly | docs/06-contract-based-dev.md §2.7 |
| Contract evolution governance: breaking changes go through dm-adr; label pure-incremental PRs; new interfaces written back to the master catalog (orphan-doc guard) | docs/06-contract-based-dev.md §5 |
| Observability diagnostic contract: 400-build behavior contract must include a diagnostic contract (observe wrapper on critical paths + state logging + no silent swallow), see docs/07-observability-driven-dev.md §2.1/§3/§7 | docs/07-observability-driven-dev.md |
| Version plan must be decomposable into single-file batches (AI execution granularity = single-file refactor / single-function fix) for per-batch advancement, see docs/08-small-batch-iteration.md | docs/08-small-batch-iteration.md |

## Assets

- `references/version-rules.md` — Four-document structure, TF content boundaries
- `references/git-flow-rules.md` — PR/Issue/commit rules
- `assets/200-spec.md` — Spec template
- `assets/300-design.md` — Design template
- `assets/400-build.md` — Build template (includes execution order matrix section)
- `assets/tracking-matrix.md` — TF→Issue→PR tracking template

## Example

```
User: "新建版本 v1.5-login"

AI:  1. Create docs/versions/v1.5-login/ four docs
     2. Create branch feature/v1.5-login
     3. Output PR description template (title + goal/scope/acceptance/risk)
     4. Output TF1-TF3 issue description templates
     5. Print tracking matrix:
        | TF | Issue | PR | Acceptance |
        | TF1 登录表单 | #xx | #xx | ⬜ |
        | TF2 验证流程 | #xx | #xx | ⬜ |
        | TF3 会话管理 | #xx | #xx | ⬜ |

User: "TF2 完成了"

AI:  1. Confirm acceptance criteria
     2. Suggest commit: feat(login): implement credential validation
     3. Update tracking matrix TF2→✅
     4. Suggest closing Issue #xx

User: "关闭版本 v1.5-login"

AI:  Delegate dm-close-ver (readiness audit → merge preserving history → close TF issues → branch cleanup → close report)
```
