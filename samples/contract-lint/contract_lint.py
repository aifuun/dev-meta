#!/usr/bin/env python3
"""Contract structural lint — reference implementation for `docs/06` §8.4.

Lints the **contract documents themselves** (form), not the artifacts they
describe (semantics — that is `samples/contract-gate/`, see `docs/06` §2.8).

Four checks (docs/06 §8.4):

  LINT-01  References `<path>.md#<slug>` resolve — the file is a contract doc
           and the anchor exists in *that* file (zero dead links).
  LINT-02  Exactly one canonical state marker per anchor block — one contract,
           one `- 状态：`[CURRENT]`` (docs/06 §2.9). Prose mentions and the
           title / intro area before the first anchor are exempt.
  LINT-03  Anchor slugs are unique repo-wide and match
           `^[a-z][a-z0-9]*(-[a-z0-9]+)+$` (docs/06 §8.2).
  LINT-04  Contract docs never reference downstream docs
           (versions / plans / upper specs) — references are one-way
           (docs/06 §8.1).

Reference convention: refs are written **root-relative** to the anchor
(`docs/contracts/02-render.md#render-host-dispatch`). A bare basename
(`02-render.md#render-host-dispatch`) is accepted as a shorthand, but pointing
at the wrong file for that slug is a violation.

No third-party dependencies (stdlib only).

Usage:
    # Directory form (docs/06 §7.2)
    python3 contract_lint.py --root . --contracts-dir docs/contracts

    # Single-file form (docs/06 §7.1, small projects)
    python3 contract_lint.py --root . --contract-file docs/03_CONTRACTS_AND_API.md

    # Stricter: anchors are mandatory
    python3 contract_lint.py --root . --contracts-dir docs/contracts --require-anchors

    # Prove the linter itself works (no fixture files needed)
    python3 contract_lint.py --self-test

Exit codes: 0 = green, 1 = violations found, 2 = usage / IO error.
Throwing the error back is the point: never pass silently (docs/06 §2.8).
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

ANCHOR_RE = re.compile(r'^<a id="([^"]+)"></a>\s*$', re.M)
# Canonical record form (docs/06 §2.9): a line reading `- 状态：`[CURRENT]``.
# Only this form counts as *the* state of a contract — prose mentions of
# `[PLANNED]` / `[HISTORY]` (guides, examples, index tables) are ignored.
STATE_CANON_RE = re.compile(r'状态：\s*`\[(CURRENT|PLANNED|HISTORY)\]`')
# Lenient form, used only for files with no anchors yet (migration step 1–2):
# enough to catch "contract without any state", not granularity.
STATE_ANY_RE = re.compile(r'\[(CURRENT|PLANNED|HISTORY)\]')
SLUG_RE = re.compile(r'^[a-z][a-z0-9]*(-[a-z0-9]+)+$')
REF_RE = re.compile(r'([A-Za-z0-9._-]+\.md)#([a-z0-9-]+)')

SKIP_DIR_NAMES = {
    ".git",
    "node_modules",
    ".build",
    "build",
    "DerivedData",
    ".codebuddy",
    ".venv",
    "__pycache__",
}
SOURCE_SUFFIXES = {".md", ".mdx", ".swift", ".py", ".ts", ".js", ".kt", ".java", ".go", ".rs"}
DEFAULT_DOWNSTREAM = (r"(?:docs|templates)/versions/",)


@dataclass
class Config:
    root: Path
    contract_docs: list[Path]
    require_anchors: bool = False
    downstream_patterns: tuple[str, ...] = DEFAULT_DOWNSTREAM
    source_suffixes: set[str] = field(default_factory=lambda: set(SOURCE_SUFFIXES))


def iter_scan_files(cfg: Config):
    """All lintable text files under root (contract docs included — they may
    reference each other)."""
    for p in sorted(cfg.root.rglob("*")):
        if not p.is_file() or p.suffix not in cfg.source_suffixes:
            continue
        if SKIP_DIR_NAMES.intersection(p.relative_to(cfg.root).parts):
            continue
        yield p


def rel_posix(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def lint(cfg: Config) -> tuple[dict, list[str], list[str]]:
    """Returns (stats, violations, warnings). Empty violations == green."""
    violations: list[str] = []
    warnings: list[str] = []

    anchors: dict[str, str] = {}  # slug -> contract doc rel path
    doc_relpaths: dict[str, str] = {}  # rel path -> rel path
    doc_basenames: dict[str, str] = {}  # basename -> rel path (shorthand lookup)
    per_doc_states: dict[str, int] = {}

    # ---- pass 1: collect anchors + state markers (LINT-02 / LINT-03) ----
    for doc in cfg.contract_docs:
        rel = rel_posix(doc, cfg.root)
        text = doc.read_text(encoding="utf-8")
        found = list(ANCHOR_RE.finditer(text))
        canon_states = len(STATE_CANON_RE.findall(text))
        any_states = len(STATE_ANY_RE.findall(text))
        per_doc_states[rel] = canon_states
        doc_relpaths[rel] = rel
        doc_basenames.setdefault(doc.name, rel)

        if not found:
            # Migration step 1–2 (docs/06 §7.6): no anchors yet → granularity is
            # unverifiable, but "contract with no state at all" is still caught.
            if any_states == 0:
                violations.append(f"LINT-02 {rel}: 无状态标记（契约须一条一标，见 docs/06 §2.9）")
            elif cfg.require_anchors:
                violations.append(f"LINT-03 {rel}: 缺少语义锚点 <a id=\"slug\"></a>（docs/06 §8.2）")
            else:
                warnings.append(
                    f"{rel}: {any_states} 处状态提及但无锚点 —— 无法按条校验，"
                    f"建议补 §8.2 语义锚点"
                )
        else:
            # Text before the first anchor (title / intro / index table) is not a
            # contract block — it is exempt on purpose (guides quote `[CURRENT]`).
            for i, m in enumerate(found):
                end = found[i + 1].start() if i + 1 < len(found) else len(text)
                n = len(STATE_CANON_RE.findall(text[m.start():end]))
                if n != 1:
                    violations.append(
                        f"LINT-02 {rel}: 锚点 #{m.group(1)} 有 {n} 个规范状态标记"
                        f"（须恰好 1 个「- 状态：`[X]`」）"
                    )

        for m in found:
            slug = m.group(1)
            if not SLUG_RE.match(slug):
                violations.append(f"LINT-03 {rel}: 锚点 slug 不合规范 `{slug}`（docs/06 §8.2）")
            if slug in anchors:
                violations.append(f"LINT-03 {rel}: 锚点重复 `{slug}`（已见于 {anchors[slug]}）")
            anchors[slug] = rel

    # ---- pass 2: references (LINT-01) and downstream (LINT-04) ----
    downstream_re = re.compile("|".join(cfg.downstream_patterns)) if cfg.downstream_patterns else None
    ref_count = 0
    contract_relpaths = set(doc_relpaths)

    for p in iter_scan_files(cfg):
        text = p.read_text(encoding="utf-8")
        rel = rel_posix(p, cfg.root)

        for ref_path, slug in REF_RE.findall(text):
            target = doc_relpaths.get(ref_path) or doc_basenames.get(ref_path)
            if target is None:
                continue  # reference to a non-contract doc — not ours to judge
            ref_count += 1
            if slug not in anchors:
                violations.append(
                    f"LINT-01 {rel}: 锚点 `#{slug}` 不存在于任何契约文档（引用 {ref_path}）"
                )
            elif anchors[slug] != target:
                violations.append(
                    f"LINT-01 {rel}: 锚点 `#{slug}` 实际位于 `{anchors[slug]}`，不是 `{ref_path}`"
                )

        if rel in contract_relpaths and downstream_re:
            for m in downstream_re.finditer(text):
                line = text[: m.start()].count("\n") + 1
                violations.append(
                    f"LINT-04 {rel}:{line} 契约引用了下游 `{m.group(0)}` —— 引用须单向（docs/06 §8.1）"
                )

    stats = {
        "docs": len(per_doc_states),
        "anchors": len(anchors),
        "refs": ref_count,
        "per_doc_states": per_doc_states,
    }
    return stats, violations, warnings


def report(stats: dict, violations: list[str], warnings: list[str], quiet: bool = False) -> int:
    print(
        f"契约文档：{stats['docs']} 个；锚点：{stats['anchors']} 个；引用：{stats['refs']} 处"
    )
    if not quiet:
        for name, n in stats["per_doc_states"].items():
            print(f"  - {name}: {n} 条状态标记")

    for w in warnings:
        print(f"⚠️  {w}")

    if violations:
        print(f"\n❌ 发现 {len(violations)} 项违规：")
        for v in violations:
            print("  -", v)
        return 1

    print("\n✅ 契约结构 lint 全绿（LINT-01 / 02 / 03 / 04）")
    return 0


def die(msg: str) -> None:
    """Usage / IO error → exit 2 (distinct from 'violations found' = 1)."""
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(2)


def resolve_targets(args: argparse.Namespace) -> tuple[Path, list[Path]]:
    root = Path(args.root).resolve()
    if not root.is_dir():
        die(f"--root 不是目录：{root}")

    docs: list[Path] = []
    if args.contracts_dir:
        cdir = (root / args.contracts_dir).resolve()
        if not cdir.is_dir():
            die(
                f"契约目录不存在：{cdir}\n"
                f"   若项目尚未拆目录，请用单文件形态：--contract-file <path>（docs/06 §7.1）"
            )
        docs += sorted(cdir.glob("*.md"))
    if args.contract_file:
        cfile = (root / args.contract_file).resolve()
        if not cfile.is_file():
            die(f"契约文件不存在：{cfile}")
        docs.append(cfile)

    if not docs:
        die("未指定契约来源：请给 --contracts-dir 或 --contract-file（见 docs/06 §7.1）")
    return root, docs


def build_config(args: argparse.Namespace) -> Config:
    root, docs = resolve_targets(args)
    return Config(
        root=root,
        contract_docs=docs,
        require_anchors=args.require_anchors,
        downstream_patterns=tuple(args.downstream_pattern or DEFAULT_DOWNSTREAM),
    )


def run_self_test() -> int:
    """Build throw-away fixture trees and assert the linter behaves."""
    good_contract = (
        "# Contracts\n\n"
        "- **A-001｜alpha**\n"
        '<a id="alpha-rule"></a>\n'
        "  - 状态：`[CURRENT]`\n"
        "  - 不变性：must hold\n"
    )
    good_index = "# Index\n\n| id | 状态 | 正文 |\n|---|---|---|\n| A-001 | `[CURRENT]` | [01](docs/contracts/01-a.md#alpha-rule) |\n"

    bad_contract = (
        "# Contracts\n\n"
        "- **A-001｜alpha**\n"
        '<a id="alpha-rule"></a>\n'
        "  - 状态：`[CURRENT]`\n"
        "  - 状态：`[PLANNED]`\n"          # LINT-02: two states in one block
        "\n- **A-002｜beta**\n"
        '<a id="Bad_Slug"></a>\n'          # LINT-03: bad slug
        "  - 状态：`[CURRENT]`\n"
        "\n- **A-003｜gamma**\n"           # (no anchor)
        "  - 状态：`[CURRENT]`\n"          # LINT-02: state outside anchor blocks
        "\n> 参见 docs/versions/v1.0-x/400-build.md\n"  # LINT-04: downstream
    )
    bad_index = "# Index\n\n| id | 正文 |\n|---|---|\n| A-001 | [01](docs/contracts/01-a.md#ghost-anchor) |\n"

    def write_tree(base: Path, contract: str, index: str) -> None:
        (base / "docs/contracts").mkdir(parents=True, exist_ok=True)
        (base / "docs/contracts/01-a.md").write_text(contract, encoding="utf-8")
        (base / "docs/00_CONTRACTS.md").write_text(index, encoding="utf-8")

    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        good = base / "good"
        bad = base / "bad"
        write_tree(good, good_contract, good_index)
        write_tree(bad, bad_contract, bad_index)

        cfg_good = Config(root=good, contract_docs=[good / "docs/contracts/01-a.md"])
        _, gv, _ = lint(cfg_good)
        if gv:
            failures.append(f"self-test: 合法样本被误报 → {gv}")

        cfg_bad = Config(root=bad, contract_docs=[bad / "docs/contracts/01-a.md"])
        _, bv, _ = lint(cfg_bad)
        joined = "\n".join(bv)
        for code in ("LINT-01", "LINT-02", "LINT-03", "LINT-04"):
            if code not in joined:
                failures.append(f"self-test: 违规样本未报出 {code}")

    if failures:
        print("❌ self-test 失败：")
        for f in failures:
            print("  -", f)
        return 1
    print("✅ self-test 通过：合法样本全绿，四类违规全部被捕获")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Contract structural lint (docs/06 §8.4).")
    parser.add_argument("--root", default=".", help="仓库根（默认当前目录）")
    parser.add_argument("--contracts-dir", help="契约目录，如 docs/contracts（目录形态）")
    parser.add_argument("--contract-file", help="单文件契约，如 docs/03_CONTRACTS_AND_API.md")
    parser.add_argument(
        "--require-anchors",
        action="store_true",
        help="无锚点即失败（迁移到第 3 步后启用，docs/06 §7.6）",
    )
    parser.add_argument(
        "--downstream-pattern",
        action="append",
        help="下游路径正则（可重复；默认 docs|templates 下的 versions/）",
    )
    parser.add_argument("--quiet", action="store_true", help="不逐文件列出统计")
    parser.add_argument("--self-test", action="store_true", help="用内置样本自证 linter 有效")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if not args.contracts_dir and not args.contract_file:
        parser.error("须给 --contracts-dir 或 --contract-file（见 docs/06 §7.1）")

    cfg = build_config(args)
    stats, violations, warnings = lint(cfg)
    return report(stats, violations, warnings, quiet=args.quiet)


if __name__ == "__main__":
    sys.exit(main())
