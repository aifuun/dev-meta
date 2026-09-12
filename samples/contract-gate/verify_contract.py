#!/usr/bin/env python3
"""Contract assertion gate — reference implementation.

Mirrors the SHA256 + `contract_verified` pattern used in
`PochiHide-CoreML-Spike/src/scripts/package_dist.py`, generalized so any
project can drop it in as a pre-commit / pre-delivery gate.

Three responsibilities (mapped to docs/06 §2.8 three gates):

  1. Generate / verify MANIFEST.json — per-file sha256 + top-level
     `contract_verified` boolean. `--verify` exits non-zero on mismatch so
     CI / git hook / the AI loop can throw the error back for self-repair.
  2. Verify a contract file against a JSON Schema (`contract.schema.json`),
     proving the contract is machine-checkable (Gate 1 / Gate 2 input).
  3. Emit a structured diagnosis snapshot on failure (echoes ODD black box,
     docs/07 §3) so the AI can localize in one shot.
  4. Gate 2 observability DoD (docs/07 §2.5): scan source for bare logging
     calls without a structured `observe` wrapper or exit asserts; findings are
     surfaced in the same failure diagnosis.

No third-party dependencies: stdlib only (hashlib / json / argparse /
pathlib / datetime).

Usage:
    # Build MANIFEST (no gate, just record fingerprints)
    python3 verify_contract.py build --contract-dir .

    # Run the gate (non-zero exit on any failure)
    python3 verify_contract.py verify --contract-dir . \
        --schema contract.schema.json --manifest MANIFEST.json

Exit codes: 0 = green, 1 = gate failed, 2 = usage / IO error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path


# Files excluded from the manifest fingerprint (the manifest describes itself).
EXCLUDE_NAMES = {"MANIFEST.json"}


def sha256_file(path: Path) -> str:
    """Compute SHA-256 of a file, streaming in 1 MiB chunks."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_manifest(contract_dir: Path, contract_verified: bool) -> dict:
    """Collect every file under contract_dir (excluding the manifest itself)
    into a fingerprint manifest. Returns the manifest dict (not yet written)."""
    files = []
    for p in sorted(contract_dir.rglob("*")):
        if not p.is_file():
            continue
        if p.name in EXCLUDE_NAMES:
            continue
        files.append(
            {
                "path": p.relative_to(contract_dir).as_posix(),
                "bytes": p.stat().st_size,
                "sha256": sha256_file(p),
            }
        )
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "generator": "samples/contract-gate/verify_contract.py",
        "contract_verified": contract_verified,
        "file_count": len(files),
        "total_bytes": sum(f["bytes"] for f in files),
        "files": files,
    }


def verify_manifest(contract_dir: Path, manifest: dict) -> list[str]:
    """Recompute sha256 for every manifest entry and return a list of
    mismatch descriptions (empty == green)."""
    bad: list[str] = []
    for entry in manifest.get("files", []):
        rel = entry["path"]
        fp = contract_dir / rel
        if not fp.exists():
            bad.append(f"missing: {rel}")
            continue
        if sha256_file(fp) != entry["sha256"]:
            bad.append(f"sha256 mismatch: {rel}")
    return bad


def verify_schema(contract_file: Path, schema_file: Path) -> list[str]:
    """Lightweight JSON Schema check (type / required / enum / properties).

    Intentionally minimal — avoids a jsonschema dependency for the sample.
    For production, swap in the `jsonschema` package; the contract surface
    (file + field names) stays identical.
    """
    errors: list[str] = []
    try:
        data = json.loads(contract_file.read_text(encoding="utf-8"))
        schema = json.loads(schema_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return [f"cannot parse: {e}"]

    required = schema.get("required", [])
    for key in required:
        if key not in data:
            errors.append(f"contract missing required field: {key}")

    props = schema.get("properties", {})
    for key, spec in props.items():
        if key not in data:
            continue
        expected = spec.get("type")
        actual = type(data[key]).__name__
        if expected == "string" and not isinstance(data[key], str):
            errors.append(f"{key}: expected string, got {actual}")
        elif expected == "array" and not isinstance(data[key], list):
            errors.append(f"{key}: expected array, got {actual}")
        elif expected == "object" and not isinstance(data[key], dict):
            errors.append(f"{key}: expected object, got {actual}")
        enum = spec.get("enum")
        if enum is not None and data[key] not in enum:
            errors.append(f"{key}: {data[key]!r} not in {enum}")

    # Optional: nested $defs/items element type check for arrays
    for key, spec in props.items():
        if key in data and spec.get("type") == "array":
            item_type = (spec.get("items") or {}).get("type")
            if item_type:
                for i, item in enumerate(data[key]):
                    if item_type == "string" and not isinstance(item, str):
                        errors.append(f"{key}[{i}]: expected string, got {type(item).__name__}")
    return errors


# Source files scanned by the observability DoD (Gate 2 extension, docs/07 §2.5).
SOURCE_SUFFIXES = {".swift", ".py", ".ts", ".js", ".kt", ".java", ".go", ".rs"}

# Bare logging calls that ODD §2.2 forbids scattering into business logic
# (must go through a single `observe(...)` wrapper instead).
BARE_LOG_PATTERNS = ("print(", "NSLog(", "console.log(", "Log.d(", "println(")

# Structured assertion / wrapper signals that satisfy the observability DoD
# (ODD §2.5: exit asserts + non-intrusive observe wrapper).
ASSERT_PATTERNS = (
    "assert(",
    "assertionFailure(",
    "preconditionFailure(",
    "precondition(",
    "fatalError(",
    "observe(",
)


def check_observability_dod(source_dir: Path) -> list[str]:
    """Gate 2 observability DoD (docs/07 §2.5): business logic must not scatter
    bare print/NSLog calls; it must route through a structured `observe` wrapper
    and carry exit asserts. Returns a list of findings (empty == green).

    Heuristic: if any source file mixes bare logging with zero structured
    assertion/wrapper signals, the DoD is considered unmet. Conservative on
    purpose — false positives are surfaced as warnings the AI can self-review.
    """
    findings: list[str] = []
    if not source_dir.is_dir():
        return findings  # no source to scan; not a failure of this gate

    scanned = 0
    for p in sorted(source_dir.rglob("*")):
        if not p.is_file() or p.suffix not in SOURCE_SUFFIXES:
            continue
        scanned += 1
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        bare = sum(text.count(pat) for pat in BARE_LOG_PATTERNS)
        structured = sum(text.count(pat) for pat in ASSERT_PATTERNS)
        if bare > 0 and structured == 0:
            findings.append(
                f"observability DoD unmet: {p.relative_to(source_dir).as_posix()} "
                f"has {bare} bare log call(s) but 0 assertion/wrapper signal "
                f"(route through observe(), add exit asserts per docs/07 §2.5)"
            )
    if scanned == 0:
        findings.append(
            "observability DoD skipped: no scannable source files under "
            f"{source_dir} (passing through)"
        )
    return findings


def emit_diagnosis(contract_dir: Path, manifest: dict, bad: list[str]) -> None:
    """Structured black-box snapshot on failure (ODD docs/07 §3)."""
    print("\n[AI-DEBUG-CONTEXT] contract gate failed")
    print(f"  contract_dir: {contract_dir}")
    print(f"  contract_verified: {manifest.get('contract_verified')}")
    print(f"  file_count: {manifest.get('file_count')}")
    print("  mismatches:")
    for line in bad:
        print(f"    - {line}")


def cmd_build(args: argparse.Namespace) -> int:
    contract_dir = Path(args.contract_dir)
    if not contract_dir.is_dir():
        print(f"❌ not a directory: {contract_dir}", file=sys.stderr)
        return 2
    manifest = build_manifest(contract_dir, contract_verified=False)
    out = contract_dir / "MANIFEST.json"
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"📦 MANIFEST.json written: {manifest['file_count']} files, "
          f"{manifest['total_bytes']} bytes (contract_verified=false)")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    contract_dir = Path(args.contract_dir)
    manifest_path = contract_dir / args.manifest
    if not manifest_path.exists():
        print(f"❌ manifest not found: {manifest_path} (run `build` first)", file=sys.stderr)
        return 2

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    bad: list[str] = []

    # Gate 2/3: fingerprint integrity
    bad += verify_manifest(contract_dir, manifest)

    # Gate 1/2: contract is machine-checkable against schema
    if args.schema and Path(args.schema).exists():
        contract_file = contract_dir / args.contract
        bad += verify_schema(contract_file, Path(args.schema))

    # Gate 2: observability DoD — business logic must not scatter bare logging
    # without a structured observe wrapper or exit asserts (docs/07 §2.5).
    bad += check_observability_dod(Path(args.source_dir))

    if bad:
        emit_diagnosis(contract_dir, manifest, bad)
        print(f"\n❌ contract gate FAILED: {len(bad)} issue(s) — throw back for self-repair")
        return 1

    # Mark verified and persist (idempotent green)
    manifest["contract_verified"] = True
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("✅ contract gate passed (sha256 aligned, schema valid, contract_verified=true)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Contract assertion gate (reference).")
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build", help="generate MANIFEST.json fingerprints")
    p_build.add_argument("--contract-dir", default=".", help="directory of contract files")
    p_build.set_defaults(func=cmd_build)

    p_verify = sub.add_parser("verify", help="run the gate (non-zero on failure)")
    p_verify.add_argument("--contract-dir", default=".", help="directory of contract files")
    p_verify.add_argument("--manifest", default="MANIFEST.json", help="manifest filename")
    p_verify.add_argument("--contract", default="contract.json", help="contract data file")
    p_verify.add_argument("--schema", default="contract.schema.json", help="JSON Schema to check")
    p_verify.add_argument("--source-dir", default=".", help="source dir scanned for observability DoD (docs/07 §2.5)")
    p_verify.set_defaults(func=cmd_verify)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
