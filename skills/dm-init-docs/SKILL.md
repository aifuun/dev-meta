---
name: dm-init-docs
description: This skill should be used when initializing a new project's documentation. It interactively collects the developer's core intent, reads static templates from the local asset SSOT at ~/.dev-meta/templates/project/docs/, and generates a project doc skeleton (00~06, with 04 optional) that carries unidirectional dependency discipline, plus ./CODEBUDDY.md for dev-meta version binding.
---

# dm-init-docs — Project Docs Scaffold

Generate a project's initial documentation skeleton interactively: collect intent via guided questions, render the 00~06 templates from the local asset SSOT, and emit `./CODEBUDDY.md` for dev-meta version binding.

> **Thin entry point.** This file only carries the trigger contract and a workflow summary. The full design doc and all templates live in the **asset SSOT**: `~/.dev-meta/` (published by `pub_local.py`). Read assets from there; do not duplicate template content here.

## Asset SSOT Paths

| # | Doc | Template path |
|---|-----|---------------|
| 00 | Product Requirements | `~/.dev-meta/templates/project/docs/00_PRODUCT_REQUIREMENTS.md` |
| 01 | Technical Spec | `~/.dev-meta/templates/project/docs/01_TECHNICAL_SPEC.md` |
| 02 | System Design | `~/.dev-meta/templates/project/docs/02_SYSTEM_DESIGN.md` |
| 03 | Contracts & API (SSOT) | `~/.dev-meta/templates/project/docs/03_CONTRACTS_AND_API.md` |
| 04 | UI/UX Design (optional) | `~/.dev-meta/templates/project/docs/04_UI_UX_DESIGN.md` |
| 05 | Roadmap & Compliance | `~/.dev-meta/templates/project/docs/05_ROADMAP_AND_COMPLIANCE.md` |
| 06 | Observability | `~/.dev-meta/templates/project/docs/06_OBSERVABILITY.md` |

Full design doc: `~/.dev-meta/skills/dm-init-docs.md`

## Dependency Direction (unidirectional)

`00 → 01 → 02 → 03 → 04/05`, and `02/03 → 06`. Each doc declares its flow in the header: **referenced by downstream only, never referencing downstream**.

## Workflow

### 1. Collect intent (prompt stage)

Ask: project name & goal / core User Stories; tech stack, storage, deploy & test approach; core entities & APIs; business invariants that must never break; **is there a frontend/client UI?** (if none, skip 04); target path; dev-meta version adopted.

### 2. Resolve target path (3-level priority)

1. `.dev-metarc` → `docsTargetDir` (optional, not required to exist)
2. Path explicitly given by the developer
3. Default fallback: `<project-root>/docs/` (create with `mkdir -p`)

### 3. Generate `./CODEBUDDY.md` (required)

Create it at the project root with the dev-meta repo URL + adopted version, and an "exceptions" section. It is the **version binding** record and a **prerequisite for `dm-plan-ver` / `dm-log`**. It must NOT duplicate the global spec body — the global layer `~/.codebuddy/CODEBUDDY.md` (DoD, AI collaboration, coding conventions, worklog guide) is auto-loaded every session.

### 4. Read templates and render

Read 00~06 from the asset SSOT (skip 04 when there is no UI). Fill `{{FIELD}}` placeholders with collected intent; leave unknowns as `<!-- TODO: [dm-init-docs] <description> -->`. Preserve each doc's unidirectional-dependency header.

### 5. Write files

Write into the resolved target directory.

### 6. Output a verification report

List: generated docs, filled sections, remaining TODOs (with file/line), skipped docs and why.

### 7. Commit

Delegate to `dm-commit`, e.g. `chore: initialize project docs following dev-meta`.

## Key Rules

| Rule | Source |
|------|--------|
| Docs numbered 00~06; 04 optional, skipped for backend/CLI | Design doc |
| Each doc header keeps the unidirectional dependency declaration | Design doc |
| Contracts (03) depend on upstream 01/02 and are the read-only SSOT for downstream impl & tests | Design doc |
| Templates only reference `dev-meta/docs/06`, `07`, `08` — never redefine them | skill-doc-principles §2 |
| `./CODEBUDDY.md` generation is mandatory (prerequisite of dm-plan-ver / dm-log) | skills/README.md |
| Project-level CODEBUDDY.md holds only source + version + exceptions, not the spec body | docs/05-codebuddy-management.md |
| Assets live in `~/.dev-meta/`; this file is only the trigger entry | Design doc |
| No code scaffolding, no runtime code injection (observe wrapper lands during development) | Responsibility boundary |

## Assets

- `~/.dev-meta/templates/project/docs/0X_*.md` — the seven doc templates (SSOT)
- `~/.dev-meta/templates/CODEBUDDY.md` — project-level CODEBUDDY template (version binding + exceptions)
- `~/.dev-meta/skills/dm-init-docs.md` — full Chinese design doc
- `pub_local.py` (in the dev-meta repo) — publishes templates & skills to `~/.dev-meta/`

## Example

```
User: "initialize a new project shadow-player-v3"

AI:  1. Ask the intent questions (goal / stack / entities+invariants / has UI? / path / dev-meta version)
     2. Resolve path: no .dev-metarc, not specified -> <root>/docs/
     3. Generate ./CODEBUDDY.md (source repo + adopted version + exceptions placeholder)
     4. Render 00/01/02/03/05/06 (and 04 if it has a UI)
     5. Write to <root>/docs/
     6. Report: 7 docs generated, 0 skipped, 23 TODOs remaining (per-doc breakdown)
     7. Offer to commit via dm-commit
```
