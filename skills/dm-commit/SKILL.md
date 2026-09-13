---
name: dm-commit
description: This skill should be used when the user wants to commit changes or asks about commit message formatting. It enforces the dev-meta commit convention: type(scope): subject format, type selection guidance, footer linking rules (Closes/Refs), and pre-commit validation.
---

# dm-commit — Commit Message Convention

Ensure every commit follows the dev-meta commit convention. This skill is the single source of truth for commit formatting — dm-plan-ver, dm-log, dm-init-docs, dm-report, and dm-adr all delegate their commit steps here.

## When to Use

- User says "commit"
- User says "commit my changes"
- User asks about commit message format
- dm-plan-ver Phase 2 step 3 (TF delivery commit)
- dm-log Step 6 (worklog commit)
- dm-init-docs Step 7 (initialization commit)
- dm-report Step 6 (report commit)
- dm-adr Step 7 (ADR commit)

## Workflow

### Step 1: Determine the Type

Analyze the staged changes and recommend a type:

| Type | When to Use |
|------|-------------|
| `feat` | New feature or functionality |
| `fix` | Bug fix |
| `docs` | Documentation changes only |
| `refactor` | Code restructuring without external behavior change |
| `test` | Adding or modifying tests |
| `chore` | Build, dependencies, tooling, worklog, project init |
| `perf` | Performance optimization |
| `ci` | CI/CD changes |

### Step 2: Determine the Scope

Pick a short, lowercase identifier for the module or area affected.

Examples: `auth`, `storage`, `ui`, `api`, `worklog`, `git-flow`, `version-rules`

No default — must be explicit and meaningful.

### Step 3: Write the Subject

- Use **imperative mood** ("add" not "added", "fix" not "fixed")
- ≤ 50 characters
- Describe **what** was done concisely
- Chinese subject is acceptable for docs/worklog; English preferred for code

### Step 4: Add Body (if needed)

Explain **why** the change was made and any migration notes. Skip for trivial changes.

### Step 5: Add Footer (if needed)

For TF-related commits:

| Footer | When |
|--------|------|
| `Closes #N` | This commit **completes** the TF |
| `Refs #N` | This commit is **part of** the TF but doesn't complete it |

For non-TF commits (worklog, project init, standalone fixes), omit the footer.

### Step 6: Construct and Execute

Build the commit message and execute. Never commit unless the user explicitly asks.

> Under the Micro-Batching rhythm of `docs/08-small-batch-iteration.md`, a TF splits into three batches; each **green batch** yields one commit (all `Refs #same TF`). This step still triggers only when the user says commit / calls dm-commit — AI never commits on its own. If the next batch descends into chaos, the **user** runs `git reset --hard` to the last green commit (AI never does so spontaneously, per git safety protocol).

### Step 7: Validate

After commit, verify:
- `type` is from the allowed set
- `scope` is present and non-empty
- `subject` ≤ 50 characters
- `Closes`/`Refs` footer is correct if present

## Key Rules

| Rule | Source |
|------|--------|
| Commit must use `type(scope): subject` format | 03-git-flow-rules §3.1 |
| `type` comes from the allowed set of 8 | 03-git-flow-rules §3.3 |
| `subject` ≤ 50 characters | 03-git-flow-rules §3.4 |
| TF commits must link an Issue (`Closes #id` / `Refs #id`) | 03-git-flow-rules §2.3 |
| Body and footer optional for trivial, non-TF changes | 03-git-flow-rules §8 |
| Chinese `subject` acceptable for docs/worklog, English for code | 03-git-flow-rules §3.4 |
| Never commit unless the user explicitly asks | 03-git-flow-rules §3 (this skill §6) |

## Common Patterns

```text
# TF completion
feat(auth): implement credential validation

Closes #42
```

```text
# Worklog update
chore: update worklog — version-rules cross-TF state machine spec
```

```text
# Project initialization
chore: initialize project docs following dev-meta
```

```text
# Bug fix
fix(storage): fallback to memory when indexeddb is unavailable

Keep playback flow non-blocking when openDB fails.

Closes #42
```

## References

- `references/git-flow-rules.md` — Full commit message specification, type set, branch naming, merge strategy.

## Example

```
User: "commit"

AI:  1. Inspect the staging area (git diff --staged)
     2. Analyze the change type -> recommend type: feat
     3. Recommend scope: auth
     4. Suggest subject: implement credential validation
     5. TF-related -> suggest footer: Closes #42
     6. Build: feat(auth): implement credential validation\n\nCloses #42
     7. Commit after confirmation
```

```
User: "TF2 is done, commit it"

AI:  1. Read 200-spec.md to confirm TF2 acceptance criteria
     2. Build the commit message per dm-commit convention
     3. Suggest: feat(login): implement credential validation\n\nCloses #43
```
