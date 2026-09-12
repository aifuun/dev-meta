#!/usr/bin/env python3
"""
pub_local.py - 将 dev-meta 的模板与 skill 文档同步至本地全局资产目录 ~/.dev-meta/

用法:
    python3 pub_local.py              # 执行同步
    python3 pub_local.py --dry-run    # 预演，不写入

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
SKILL_PREFIX = "dm-"
TEMPLATE_REL = Path("templates") / "project" / "docs"


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


def main() -> int:
    parser = argparse.ArgumentParser(description="将 dev-meta 模板与 skill 发布到 ~/.dev-meta/")
    parser.add_argument("--dry-run", action="store_true", help="预演，不实际写入")
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

    print(f"\n[done] 已发布至本地全局资产目录: {TARGET_DIR}")
    print("       触发入口: ~/.codebuddy/skills/dm-init-docs/SKILL.md（薄入口，指向上述资产）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
