#!/usr/bin/env python3
"""
pub_local.py - 将 dev-meta 的模板与 skill 文档同步至本地全局资产目录 ~/.dev-meta/

用法:
    python3 pub_local.py                    # 发布资产到 ~/.dev-meta/
    python3 pub_local.py --deploy           # 同时部署 skill 触发入口到 ~/.codebuddy/skills/
    python3 pub_local.py --dry-run          # 预演，不写入
    python3 pub_local.py --deploy --dry-run # 预演（含部署）

两类产物:
- 资产 SSOT  ~/.dev-meta/              模板 + 中文设计文档（默认发布）
- 触发入口    ~/.codebuddy/skills/<name>/  英文 SKILL.md + assets/ + references/（--deploy）

修复的旧版缺陷:
1. 过滤: skills 只同步 `dm-*.md`，排除 README.md / skill-doc-principles.md，防污染
2. 清理: 同步前删除目标目录中源已不存在的文件，防改名后残留（如旧的 project-*.md 平铺模板）
3. 校验: 同步后核对文件数，不一致则非 0 退出
4. dry-run: 支持预演，不实际写入
"""

import argparse
import shutil
import sys
from pathlib import Path

TARGET_DIR = Path.home() / ".dev-meta"
DEPLOY_DIR = Path.home() / ".codebuddy" / "skills"
SKILL_PREFIX = "dm-"
TEMPLATE_REL = Path("templates") / "project" / "docs"
IGNORE_NAMES = {"__pycache__", ".DS_Store"}


def _ignored(rel: Path) -> bool:
    """相对路径中是否含应忽略的目录/文件名。"""
    return any(part in IGNORE_NAMES for part in rel.parts)


def sync_dir(src: Path, dst: Path, pattern: str, dry_run: bool, label: str) -> int:
    """同步单一目录: 过滤 -> 清理 -> 拷贝 -> 校验。返回同步文件数，-1 表示失败。"""
    if not src.exists():
        print(f"  [warn] [{label}] 源目录不存在，跳过: {src}")
        return 0

    src_files = sorted(p for p in src.glob(pattern) if p.is_file())
    if not src_files:
        print(f"  [warn] [{label}] 源目录无匹配文件: {src}/{pattern}")
        return 0

    dst.mkdir(parents=True, exist_ok=True)
    src_names = {p.name for p in src_files}

    removed = 0
    for existing in sorted(p for p in dst.glob(pattern) if p.is_file()):
        if existing.name not in src_names:
            print(f"  - 删除旧文件: {existing.name}")
            if not dry_run:
                existing.unlink()
            removed += 1

    copied = 0
    for f in src_files:
        target = dst / f.name
        action = "更新" if target.exists() else "新增"
        print(f"  {action}: {f.name}")
        if not dry_run:
            shutil.copy2(f, target)
        copied += 1

    if not dry_run:
        actual = len([p for p in dst.glob(pattern) if p.is_file()])
        if actual != len(src_files):
            print(f"  [error] [{label}] 校验失败: 期望 {len(src_files)} 个，实际 {actual} 个")
            return -1

    print(f"  [ok] [{label}] 同步 {copied} 个文件（清理 {removed} 个）")
    return copied


def sync_tree(src: Path, dst: Path, dry_run: bool, label: str) -> int:
    """递归同步目录树（SKILL.md + assets/ + references/）：清理 -> 拷贝 -> 校验。

    返回同步文件数，-1 表示失败。
    """
    if not src.is_dir():
        print(f"  [warn] [{label}] 源目录不存在，跳过: {src}")
        return 0

    src_files = [p for p in sorted(src.rglob("*"))
                 if p.is_file() and not _ignored(p.relative_to(src))]
    if not src_files:
        print(f"  [warn] [{label}] 源目录无文件: {src}")
        return 0

    dst.mkdir(parents=True, exist_ok=True)
    rels = {p.relative_to(src).as_posix() for p in src_files}

    removed = 0
    for existing in sorted(p for p in dst.rglob("*") if p.is_file()):
        rel = existing.relative_to(dst)
        if _ignored(rel):
            continue
        if rel.as_posix() not in rels:
            print(f"  - 删除旧文件: {rel.as_posix()}")
            if not dry_run:
                existing.unlink()
            removed += 1

    copied = 0
    for f in src_files:
        rel = f.relative_to(src)
        target = dst / rel
        action = "更新" if target.exists() else "新增"
        print(f"  {action}: {rel.as_posix()}")
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)
        copied += 1

    if not dry_run:
        actual = len([p for p in dst.rglob("*")
                      if p.is_file() and not _ignored(p.relative_to(dst))])
        if actual != len(src_files):
            print(f"  [error] [{label}] 校验失败: 期望 {len(src_files)} 个，实际 {actual} 个")
            return -1

    print(f"  [ok] [{label}] 同步 {copied} 个文件（清理 {removed} 个）")
    return copied


def main() -> int:
    parser = argparse.ArgumentParser(description="将 dev-meta 模板与 skill 发布到 ~/.dev-meta/")
    parser.add_argument("--dry-run", action="store_true", help="预演，不实际写入")
    parser.add_argument("--deploy", action="store_true",
                        help="同时把 skills/<name>/ 部署到 ~/.codebuddy/skills/<name>/（skill 触发入口）")
    args = parser.parse_args()

    root = Path(__file__).parent.resolve()
    if args.dry_run:
        print("=== [dry-run] 预演模式，不会写入任何文件 ===\n")

    print(f"[templates] -> {TARGET_DIR / TEMPLATE_REL}")
    if sync_dir(root / TEMPLATE_REL, TARGET_DIR / TEMPLATE_REL, "*.md", args.dry_run, "templates") < 0:
        return 1

    print(f"\n[codebuddy] -> {TARGET_DIR / 'templates' / 'CODEBUDDY.md'}")
    if sync_dir(root / "templates", TARGET_DIR / "templates", "CODEBUDDY.md", args.dry_run, "codebuddy") < 0:
        return 1

    print(f"\n[skills] -> {TARGET_DIR / 'skills'}（仅 {SKILL_PREFIX}*.md）")
    if sync_dir(root / "skills", TARGET_DIR / "skills", f"{SKILL_PREFIX}*.md", args.dry_run, "skills") < 0:
        return 1

    if args.deploy:
        print(f"\n[deploy] -> {DEPLOY_DIR}（skill 触发入口）")
        for skill_dir in sorted((root / "skills").glob(f"{SKILL_PREFIX}*")):
            if skill_dir.is_dir():
                if sync_tree(skill_dir, DEPLOY_DIR / skill_dir.name, args.dry_run, skill_dir.name) < 0:
                    return 1
        print(f"\n[done] 资产已发布至 {TARGET_DIR}，触发入口已部署至 {DEPLOY_DIR}")
    else:
        print(f"\n[done] 已发布至本地全局资产目录: {TARGET_DIR}")
        print("       [hint] 加 --deploy 可同时部署 skill 触发入口至 ~/.codebuddy/skills/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
