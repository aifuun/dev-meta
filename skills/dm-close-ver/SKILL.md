---
name: dm-close-ver
description: This skill should be used when closing a version or preparing to merge/release. It runs the full version close-out: readiness audit, wrap-up execution, merge (preserving history, not squash), closing all TF issues, branch cleanup, and post-close verification. Version start is handled by dm-plan-ver.
---

# dm-close-ver — Version Close-out

Sole owner of the "close version" workflow. It is the independent successor to dm-plan-ver's Phase 3 (close-out). dm-plan-ver opens versions; dm-close-ver closes them.

## Relationship

```
dm-plan-ver (version start)
  └── Phase 2: TF Development
        ├── dm-dev-tf (TF start)
        └── dm-commit (TF commit)

dm-close-ver (version close) ← independent skill, takes over from dm-plan-ver
```

- **Prerequisite**: version branch `feature/vX.Y-<slug>` exists; TF development done or explicitly deferred
- **Delegates**: dm-log (worklog completion), dm-commit (document commit)

## When to Use

- User says "close version v1.2-payment"
- User says "prepare for release / merge"
- User says "finish this version"
- User says "close version v1.2"
- dm-plan-ver hands off at close-out

## Workflow

### Phase A: Readiness Audit (Can we close?)

1. **Issue sweep** — all TF issues closed or explicitly `[DEFERRED]`
2. **Work package check** — `500-schedule.md` all ✅ or explicitly deferred
3. **Acceptance traceability** — each TF has a verifiable acceptance result (against `200-spec.md`)
4. **Uncommitted changes** — working tree / staging clean (`git status`)
5. **Observability DoD** — no bare logs (critical paths via `observe`), no silent swallow, high-cost nodes (inference/IO/cross-process) have diagnostic snapshots (see `docs/07-observability-driven-dev.md` §7 DoD)

> If any fails → fix first, do not skip.

### Phase B: Wrap-up Execution (Do the close)

5. **Execution order matrix check** — `400-build.md` fixed tail rows (unit tests & regression, build & regression verification) done
6. **worklog completion** — all work in the version period recorded (delegate dm-log)
7. **Document wrap-up** — version documents committed (delegate dm-commit)

### Phase C: Merge & Close Issues

8. **Merge PR (preserve history)** — merge with a **merge commit**, **not squash**:
   ```bash
   git checkout main
   git merge --no-ff feature/vX.Y-<slug>
   git push origin main
   ```
   - Preserve the original history of every TF commit
   - If a TF commit already carries `Closes #id`, the host platform auto-closes the issue on merge

9. **Close remaining TF issues** — close every TF issue for this version:
   - Done: annotate acceptance result, then close
   - `[DEFERRED]`: annotate reason, then close
   - Not auto-closed by commit: close manually
   - Update tracking-matrix to ✅ after closing

10. **Clean up branch** — delete the merged version branch:
    ```bash
    git branch -d feature/vX.Y-<slug>
    ```

11. **Version tag** (required) — use an **annotated tag** with version + required info:
    - Name: `v<X.Y.Z>` (matches version dir `vX.Y-<slug>` and PR `[Vx.y.z]`; `<Z>` patch starts at `.0`)
    - Message must include: `version` (with slug), `scope` (one-line delivery summary), `merge` (merge commit hash = rollback point), `issues` (closed TF Issue list)
    ```bash
    git tag -a v<X.Y.Z> -m "$(cat <<'EOF'
    version: vX.Y.Z (slug: <slug>)
    scope: <one-line delivery summary>
    merge: <merge commit hash>
    issues: #<id1> #<id2> ...
    EOF
    )"
    git push origin --tags
    ```
    - Tag must be pushed (`--tags`); it is the version anchor, not optional.

12. **Archive tracking matrix** — update/archive tracking-matrix

### Phase D: Post-close Verify

13. **Upstream check** — confirm no residual references to the version branch on main
14. **roadmap update** — mark the version delivered, advance next step
15. **Rollback plan** — record known rollback point (merge commit hash)

## Troubleshooting: Common Close-out Mistakes

| Scenario | Signal | Handling |
|----------|--------|----------|
| **Unclosed issue** | open TF issues remain after merge | sweep → close or mark `[DEFERRED]` |
| **Stale branch** | merged branch still shown in `git branch` | `git branch -d <branch>` |
| **Merge conflict** | conflict error during merge | resolve manually → `git add` → `git merge --continue`; keep both histories |
| **Untraceable acceptance** | `200-spec.md` acceptance item has no result | backfill result or mark explicitly deferred |
| **Missing worklog** | no records for the version period | delegate dm-log before archiving |
| **Unlinked commits** | commits lack `Refs`/`Closes` footer | record in close report; backfill association (do not rewrite history) |
| **Accidental squash** | TF history flattened after merge | confirm branch pushed, rebuild via merge commit or record rollback point |
| **Residual reference** | main still points to version branch | fix docs/config, update roadmap |
| **ODD DoD not met** | critical paths have bare print / silent swallow / high-cost nodes lack diagnostic snapshot | add `observe` structured diagnosis (07 §2.1/§3/§4), `#if DEBUG` isolated |

## Key Rules

| Rule | Source |
|------|--------|
| Merge with a merge commit (`--no-ff`), **preserve history, do NOT squash** | 03-git-flow-rules §4.2 (this skill overrides the default squash) |
| Each TF commit carries `Closes #id`, auto-closes on merge | 03-git-flow-rules §2.3 |
| Unclosed issues must be explicitly `[DEFERRED]`, never silently skipped | 03-git-flow-rules §2.3 |
| Acceptance results must be traceable | 02-version-rules |
| No new feature commits during close-out | — |
| Delete merged branches | 03-git-flow-rules §9 |
| Update roadmap after closing version | 01-project-dev-flow |
| Must pass ODD DoD before merge: no bare logs / no silent swallow / high-cost nodes have diagnostic snapshots (07 §7) | docs/07-observability-driven-dev.md §7 |

## Output

- **Close report**: version → delivered scope → acceptance summary → closed issue list → deferred items → rollback point (merge commit hash)

## References

- `references/version-rules.md` — Four-document acceptance structure
- `references/git-flow-rules.md` — Issue/PR/merge rules
- `../dm-plan-ver/references/git-flow-rules.md` — Tracking matrix, branch cleanup
