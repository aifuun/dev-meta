---
name: dm-pub-skill
description: This skill should be used when publishing or deploying dev-meta assets and skills. It publishes template assets and Chinese design docs to ~/.dev-meta/, and deploys skill trigger entries (English SKILL.md plus assets/ and references/) to ~/.codebuddy/skills/. It orchestrates pub_local.py, runs pre-flight checks and post-deploy verification.
---

# dm-pub-skill — Publish & Deploy

Publish template assets to `~/.dev-meta/` and deploy skill trigger entries to `~/.codebuddy/skills/`. `pub_local.py` performs the actual file sync; this skill owns orchestration, pre-flight checks, and verification.

## Responsibility Boundary

| Responsibility | Owner |
|----------------|-------|
| Publish template assets + Chinese design docs to `~/.dev-meta/` | ✅ This skill |
| Deploy skill trigger entries to `~/.codebuddy/skills/` | ✅ This skill |
| Pre-flight checks (templates present, SKILL.md frontmatter, dual-end alignment) | ✅ This skill |
| Actual file sync (clean → copy → verify) | `pub_local.py` (invoked here) |
| Editing template content / authoring skill design docs | Not this skill (dm-init-docs / each skill) |
| Format validation (`package_skill.py`) | External tool (invoked and interpreted here) |
| Commit | Delegate `dm-commit` |

## When to Use

- User says "publish skill", "deploy templates", "sync assets", "publish", "deploy"
- After changing `templates/` or `skills/` and wanting the change to take effect

## Core Concepts

### Two-Directory Split

| Directory | Role | Content | Read by |
|-----------|------|---------|---------|
| `~/.dev-meta/` | **Asset SSOT** (standalone, usable without CodeBuddy) | `templates/project/docs/0X_*.md`, `templates/CODEBUDDY.md`, `skills/dm-*.md` (Chinese design docs) | AI on demand |
| `~/.codebuddy/skills/<name>/` | **Trigger entry** (CodeBuddy only loads skills from here) | `SKILL.md` (English, with frontmatter) + `assets/` + `references/` | CodeBuddy loader |

> Neither replaces the other. Publishing assets alone will not make a skill triggerable; deploying the entry alone leaves templates missing.

### Two File Sets in the Repo

| Path | Role | Destination |
|------|------|-------------|
| `skills/<name>.md` | Chinese design doc (source of truth for maintainers) | `~/.dev-meta/skills/` |
| `skills/<name>/SKILL.md` | English trigger entry source (**version-controlled, prevents loss**) | `~/.codebuddy/skills/<name>/` |
| `skills/<name>/assets/`, `references/`, `scripts/` | Deployed alongside the trigger entry | `~/.codebuddy/skills/<name>/` |

> Having both `skills/dm-adr.md` (file) and `skills/dm-adr/` (directory) is expected: Chinese design doc vs English deploy source.

### Idempotency & Safety

- **Clean before copy**: delete files in the target that no longer exist in the source (prevents stale leftovers).
- **Ignore junk**: `__pycache__` and `.DS_Store` are never synced.
- **Post-sync verification**: file counts are compared; mismatch exits non-zero.
- **Dry run**: `--dry-run` prints the plan without writing.

## Workflow

### 1. Pre-flight Checks

From the repo root:

- Does `templates/project/docs/` contain all 7 templates (00~06)?
- Does `templates/CODEBUDDY.md` exist?
- Does every `skills/<name>/SKILL.md` exist and carry YAML frontmatter (`name` + `description`)?
- Are the Chinese design doc `skills/<name>.md` and the English `SKILL.md` roughly section-aligned (dual-end consistency)?

Report problems and ask before publishing; never force it.

### 2. Dry Run

```bash
python3 pub_local.py --deploy --dry-run
```

### 3. Publish & Deploy

```bash
python3 pub_local.py --deploy
```

Assets only (leave trigger entries untouched):

```bash
python3 pub_local.py
```

### 4. Verify

- Built in: per-directory file count check, non-zero exit on mismatch.
- Spot check: `~/.codebuddy/skills/<name>/SKILL.md` exists with frontmatter.
- Spot check: `~/.dev-meta/templates/project/docs/` holds 7 templates.
- Optional per-skill format validation:

```bash
python3 ~/.vscode/extensions/tencent-cloud.coding-copilot-*/out/extension/builtin/skill-creator/scripts/package_skill.py ~/.codebuddy/skills/<name> /tmp
```

### 5. Report & Commit

Output the report (assets published, entries deployed, cleaned items, verification result). Delegate to `dm-commit` when changes should be committed.

## Key Rules

| Rule | Source |
|------|--------|
| Assets go to `~/.dev-meta/`; trigger entries go to `~/.codebuddy/skills/<name>/` | Core concepts |
| English `SKILL.md` must be version-controlled under `skills/<name>/` | Core concepts (prevents loss) |
| New/changed skills must stay dual-end consistent (Chinese doc ↔ English SKILL.md sections) | skill-doc-principles §5 |
| Always `--dry-run` before publishing | Workflow |
| Sync is clean-then-copy with file count verification, non-zero exit on failure | `pub_local.py` |
| Ignore `__pycache__` / `.DS_Store` | `pub_local.py` |
| Omit `--deploy` for assets-only; `--deploy` is required to make a skill triggerable | Workflow |

## Assets

- `pub_local.py` (repo root) — publish/deploy engine, no third-party dependencies
- `templates/project/docs/0X_*.md` — project doc templates
- `templates/CODEBUDDY.md` — project-level CODEBUDDY template
- `skills/<name>.md` — Chinese design docs
- `skills/<name>/SKILL.md` — English trigger entry sources

## Example

```
User: "publish skill"

AI:  1. Pre-flight: 7 templates ok / CODEBUDDY.md ok / 13 SKILL.md with frontmatter ok
     2. Dry run: python3 pub_local.py --deploy --dry-run
        [templates] 7 · [codebuddy] 1 · [skills] 13 · [deploy] 13 skills
     3. Run: python3 pub_local.py --deploy
     4. Verify: counts match; spot check dm-plan-ver (7 files) and dm-arch-design (2 files)
     5. Report: assets published to ~/.dev-meta/, trigger entries deployed to ~/.codebuddy/skills/
```
