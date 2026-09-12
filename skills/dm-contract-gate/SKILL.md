---
name: dm-contract-gate
description: This skill should be used when the AI is about to modify business code, has just finished modifying code, or is about to commit/package a delivery. It enforces the contract assertion gate from docs/06 §2.8 — diff the contract before editing, run the gate (sha256 + contract_verified) after editing, and verify MANIFEST integrity before delivery; never deliver while the gate is red, and throw the raw error back for self-repair.
---

# dm-contract-gate — Contract Assertion Gate

Enforce the contract assertion gate defined in `docs/06-contract-based-dev.md` §2.8. At three key checkpoints — before editing, after editing, and before commit/packaging — verify the contract: diff the contract before changing logic, run the gate after editing, and align MANIFEST fingerprints before delivery. Never deliver while the gate is red; throw the raw error back for self-repair within the contract frame.

## Scope & Boundaries

| Responsibility | Owner |
|----------------|-------|
| Diff contract before edit; judge whether the change breaks the contract | ✅ This skill |
| Run gate script after edit / before delivery (sha256 + contract_verified + compile/type check) | ✅ This skill |
| On gate failure: throw raw error back, self-repair within the contract frame | ✅ This skill |
| Breaking contract change (semantics/signature/coordinate) | Delegate to `dm-adr` (06 §5) |
| Pure-incremental contract append + renumber | Delegate to user PR note (06 §5); skill only reminds |
| Implementing business code | Delegate to `dm-dev-tf` (this skill only guards, does not write) |

## When to Use

- User says "help me change X", "fix bug Y", "implement Z" → **Gate 1 (pre-implementation)**
- AI finished multi-file edits, about to tell user "done" → **Gate 2 (post-implementation)** (automatic, no user trigger)
- User says "commit", "package dist/", "submit", or calls `dm-commit` → **Gate 3 (delivery)**
- User explicitly says "run contract gate", "verify contract", "contract gate"

## Core Concepts

### Contract Read-Only (Schema & Interface First)

The contract file is the single source of truth (SSOT) and must be parseable (`Contract.swift` / `JSON Schema` / `OpenAPI` / `Protobuf` / Swift `Protocol` / `400-build.md` behavior-contract table). Before changing implementation, diff the contract to confirm no invariant breaks. **Never let the AI rewrite the contract itself.**

### Three Checkpoints (Gates)

- **Gate 1 — Pre-Implementation**: Before writing the first line of business code, read and diff the contract; confirm no public contract breaks. If the contract is touched, ask the user for permission first. No contract check, no code change.
- **Gate 2 — Post-Implementation**: Before delivering, silently run the local gate (`xcrun swiftc -parse` / `python3 package_dist.py --verify` / `MANIFEST` hash check / JSON Schema check). **Never claim success while red** — intercept output, throw the raw terminal error back to self, patch within the contract frame until the gate turns green.
- **Gate 3 — Delivery**: On commit/packaging, verify `MANIFEST.json` file list, `sha256` fingerprints, and `contract_verified` status are all aligned; if not, throw the error back and block the merge.

### SHA256 + contract_verified Pattern

Gate artifact `MANIFEST.json` carries per-file `sha256` and a top-level `contract_verified` boolean; `--verify` exits non-zero on failure for CI / git hook / AI throwback. Reference implementation: `samples/contract-gate/verify_contract.py`, aligned with `package_dist.py`.

## Workflow

### Step 1: Locate the Contract SSOT

| Contract type | Typical file |
|---------------|--------------|
| Swift contract facade | `DetectorContract.swift` / `Contract.swift` / public `Protocol` |
| Schema contract | `*.schema.json` / inline JSON Schema in `project-schema-design.md` |
| API contract | `OpenAPI` (`openapi.yaml`) / `project-api-design.md` |
| Version behavior contract | `docs/versions/vX.Y-<slug>/400-build.md` §1.x / §2.3 / §3.3 |

### Step 2: Gate 1 — Pre-Implementation

- Read the contract file and diff against the request: does the change touch a contract invariant (signature / field / coordinate / failure behavior)?
- Not touched → proceed with implementation.
- Touched but pure-incremental (new interface / new domain) → remind user to label PR "pure-incremental" and renumber (06 §5).
- Touched with breaking semantics → **pause**, delegate to `dm-adr` for a breaking-change ADR; proceed only after approval and caller adaptation.

### Step 3: Gate 2 — Post-Implementation

- After edits, before output, **silently** run the gate script (see Resources).
- Pass → set `contract_verified` to `true`, deliver to user.
- Fail → **never claim success**; capture the terminal error, throw it back to self, locate the missed call site, patch within the contract frame; rerun this step until green.

### Step 4: Gate 3 — Delivery

- On user "commit / package", run the final gate: verify `MANIFEST.json` file list, `sha256`, and `contract_verified` consistency.
- Inconsistent → throw error back, block `dm-commit`; consistent → allow delivery.

### Step 5: Structured Diagnosis (on failure)

On gate failure, emit a black-box snapshot per `docs/07-observability-driven-dev.md` §3: contract snapshot (`Input Snapshot` = excerpt of current contract SSOT) + mismatch diff + command/resource context, for one-shot AI localization (echoes 07 §2.1/§2.3).

## Key Rules

| Rule | Source |
|------|--------|
| Contract read-only; AI never rewrites it; breaking → dm-adr, incremental → PR label | docs/06 §2.8 / §5 |
| Gate 1: diff contract before edit; no check, no code | docs/06 §2.8 |
| Gate 2: never claim success while red; throw raw error back for self-repair | docs/06 §2.8 |
| Gate 3: align MANIFEST fingerprints + contract_verified before merge | docs/06 §2.8 |
| Machine-verifiable first: key contracts must be parseable | docs/06 §2.8 |
| Gate failure needs structured diagnosis (07 black box) | docs/07 §6 / §3 |
| Gate 2 includes observability DoD: post-edit without observe wrapper / without exit Assert (empty map → assertionFailure) counts as gate failed | docs/07 §2.5 |
| Implementation delegated to dm-dev-tf; this skill only guards | Scope |

## Resources

| Resource | Source | Use |
|----------|--------|-----|
| SKILL.md | — | Three-gate workflow + rules |
| `samples/contract-gate/verify_contract.py` | `samples/contract-gate/` | Reusable gate (sha256 MANIFEST + contract_verified + JSON Schema check + `--verify` non-zero exit) |
| `samples/contract-gate/contract.schema.json` | `samples/contract-gate/` | Machine-verifiable contract sample (JSON Schema) |
| `docs/06-contract-based-dev.md` §2.8 | `docs/06` | Contract read-only + three-gate authority |
| `docs/07-observability-driven-dev.md` §3 | `docs/07` | Structured diagnosis on gate failure |

## Examples

```
User: Change the category mapping in VisionDetector to support 4-class detection.

AI (Gate 1 auto):
  Read DetectionCategory / DetectorContract...
  - touches DetectionCategory.names (private static let, no external override).
  - no public Protocol break → proceed.

[Edit VisionDetector.swift...]

AI (Gate 2 auto, silent):
  $ xcrun swiftc -parse PochiHide-CoreML-Spike/*.swift
  ❌ DetectionBoxRenderer.swift:260: 'DetectionCategory' has no member 'names'
  → capture, self-repair missed call site.
  $ xcrun swiftc -parse ... → ✅ 0 errors
  $ python3 package_dist.py --verify → ✅ MANIFEST (contract_verified: true)

AI: Fixed! Compile gate + MANIFEST assertion passed; 3 call sites synced.
```

```
User: commit

AI:
  Gate 3: verify MANIFEST.json (count / sha256 / contract_verified)...
  ✅ aligned → allow dm-commit.
```
