#!/usr/bin/env python3
"""
pub_local.py - 将 dev-meta 的模板、全局规范与 skill 同步到本地生效位置

用法:
    python3 pub_local.py                    # 发布资产 + 部署全局规范（默认）
    python3 pub_local.py --deploy           # 再部署 skill 触发入口（冷启动用这条）
    python3 pub_local.py --dry-run          # 预演，不写入
    python3 pub_local.py --deploy --dry-run # 预演（含部署）

四类产物（默认全部执行）:
- 项目模板    ~/.dev-meta/templates/        CODEBUDDY 模板 + 项目文档骨架 00~06 + 版本四件套模板 + worklog 模板 + 站点脚手架
- 规范文档    ~/.dev-meta/docs/             docs/01~09 + CODEBUDDY-global（跨项目可读的权威副本）
- 全局规范    ~/.codebuddy/CODEBUDDY.md     由 docs/CODEBUDDY-global.md 部署（每次会话自动加载）
- 触发入口    ~/.codebuddy/skills/<name>/   SKILL.md（由中文源自动生成）+ assets/ + references/（--deploy）

索引：每次发布自动生成 `~/.dev-meta/README.md`，列出全部资产及用途 —— AI 的单一入口。
skill 源 `~/.dev-meta/skills/dm-*.md` 为中文源，是唯一权威。

冷启动：clone 后执行一次 `python3 pub_local.py --deploy` 即全部就位。

单一权威（Single Source of Truth）:
  skill 只维护中文源 `skills/<name>.md`（含 YAML frontmatter name/description）；
  部署版 `SKILL.md` 由本脚本从中文源生成，禁止手工编辑 —— 因此不存在双端漂移。

修复的旧版缺陷:
1. 过滤: **触发入口**只由 `dm-*.md` 生成（排除 README.md / skill-doc-principles.md，防污染）；
   `skill-doc-principles.md` 作为**被引用文档**单独同步到 `~/.dev-meta/skills/`——
   否则 7 个 skill 正文里「原则见 skill-doc-principles §7」会变成无本地副本的盲引用
2. 清理: 同步前删除目标目录中源已不存在的文件，防改名后残留（如旧的 project-*.md 平铺模板）
3. 校验: 同步后核对文件数，不一致则非 0 退出
4. dry-run: 支持预演，不实际写入
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET_DIR = Path.home() / ".dev-meta"
DEPLOY_DIR = Path.home() / ".codebuddy" / "skills"
SKILL_PREFIX = "dm-"
TEMPLATE_REL = Path("templates") / "project" / "docs"
VERSIONS_REL = Path("templates") / "versions"
SITE_REL = Path("templates") / "site"
DOCS_REL = Path("docs")
IGNORE_NAMES = {"__pycache__", ".DS_Store"}

# 规范文档与模板的一句话用途（这两类极少变动，集中维护；skill 用途自动取自其 frontmatter）
DOCS_DESC = {
    "01-project-dev-flow.md": "项目级开发流程、文档分层与模板使用",
    "02-version-rules.md": "版本四件套结构、版本粒度与 Step 施工流",
    "03-git-flow-rules.md": "分支策略、commit 格式、PR 流程",
    "04-worklog-rules.md": "工作日志格式与维护规则",
    "05-codebuddy-management.md": "CODEBUDDY 两层架构与部署",
    "06-contract-based-dev.md": "契约式开发（**AI 改前只读契约**，唯一权威）",
    "07-observability-driven-dev.md": "可观测性驱动开发（**日志是 AI 的眼睛**）",
    "08-small-batch-iteration.md": "小版本迭代（**AI 执行粒度** = 单文件/单函数，唯一权威）",
    "09-ai-architecture-guide.md": "AI 辅助架构设计（人定边界 / AI 填内部）",
    "CODEBUDDY-global.md": "全局规范原始版本（部署为 `~/.codebuddy/CODEBUDDY.md`）",
}

TEMPLATE_DESC = {
    "CODEBUDDY.md": "项目层 CODEBUDDY 模板（版本绑定 + 例外项）",
    "project/docs/00_PRODUCT_REQUIREMENTS.md": "新项目 PRD 骨架（业务根，只被下游引用）",
    "project/docs/01_TECHNICAL_SPEC.md": "技术选型 / 测试策略 / 部署基线",
    "project/docs/02_SYSTEM_DESIGN.md": "架构、分层、数据流、并发状态机",
    "project/docs/03_CONTRACTS_AND_API.md": "契约 SSOT：不变式 / API / Schema / 错误码",
    "project/docs/04_UI_UX_DESIGN.md": "交互与视图状态（无 UI 时跳过）",
    "project/docs/05_ROADMAP_AND_COMPLIANCE.md": "Milestone、版本切分、合规",
    "project/docs/06_OBSERVABILITY.md": "可观测性实例化（docs/07 的项目落点）",
    "versions/vX.Y-<slug>/200-spec.md": "版本规格模板（背景 + 用户旅程 + 核心业务场景 + 架构锚点 + 验收标准 + DoD）",
    "versions/vX.Y-<slug>/300-design.md": "版本设计模板（架构与分层、数据流与状态机、核心算法、ADR）",
    "versions/vX.Y-<slug>/400-build.md": "实现蓝图 + Step 0–7 施工清单模板",
    "versions/vX.Y-<slug>/500-schedule.md": "工作包排程模板",
    "worklog.md": "工作日志模板（项目初始化时复制到 `docs/reports/worklog.md`）",
    "site/": "站点脚手架模板（Astro；`content/` 为内容源，由 `dm-pub-site` 实例化）",
}


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


def sync_tree(src: Path, dst: Path, dry_run: bool, label: str, preserve: set | None = None) -> int:
    """递归同步目录树（assets/ + references/）：清理 -> 拷贝 -> 校验。

    `preserve` 中的相对路径不会被清理（用于保护由中文源生成的 SKILL.md）。
    返回同步文件数，-1 表示失败。
    """
    preserve = preserve or set()
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
        if _ignored(rel) or rel.as_posix() in preserve:
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
                      if p.is_file()
                      and not _ignored(p.relative_to(dst))
                      and p.relative_to(dst).as_posix() not in preserve])
        if actual != len(src_files):
            print(f"  [error] [{label}] 校验失败: 期望 {len(src_files)} 个，实际 {actual} 个")
            return -1

    print(f"  [ok] [{label}] 同步 {copied} 个文件（清理 {removed} 个）")
    return copied


def sync_file(src: Path, dst: Path, dry_run: bool, label: str) -> int:
    """同步单个文件（源名与目标名可不同）。返回 1 表示已同步，-1 表示失败。"""
    if not src.is_file():
        print(f"  [warn] [{label}] 源文件不存在，跳过: {src}")
        return 0

    action = "更新" if dst.exists() else "新增"
    print(f"  {action}: {dst}")
    if not dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        if not dst.is_file():
            print(f"  [error] [{label}] 写入失败: {dst}")
            return -1
    print(f"  [ok] [{label}] 已同步")
    return 1


def _skill_description(path: Path) -> str:
    """从中文源 frontmatter 提取 description —— 用途的单一权威，不在别处重复维护。"""
    text = path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        end = text.find("\n---\n", 3)
        if end != -1:
            for line in text[3:end].splitlines():
                if line.startswith("description:"):
                    return line[len("description:"):].strip()
    return "—"


def build_index(root: Path, dry_run: bool) -> int:
    """生成 `~/.dev-meta/README.md` 总索引 —— AI 的单一入口。返回 1 成功，-1 失败。"""
    out = TARGET_DIR / "README.md"
    lines = [
        "# dev-meta 本地资产目录",
        "",
        "> 本文件由 `pub_local.py` **自动生成**，禁止手工编辑。",
        f"> 生成时间：{datetime.now():%Y-%m-%d %H:%M}",
        "",
        "## 目录结构",
        "",
        "```text",
        "~/.dev-meta/",
        "├── README.md       本索引（自动生成）",
        "├── docs/           规范文档（唯一权威副本）",
        "├── templates/      模板（项目层 CODEBUDDY + 项目文档骨架）",
        "└── skills/         skill 中文源（唯一权威）",
        "```",
        "",
        "## 规范文档 docs/",
        "",
        "| 文件 | 用途 |",
        "|------|------|",
    ]
    for f in sorted((root / DOCS_REL).glob("*.md")):
        lines.append(f"| `{f.name}` | {DOCS_DESC.get(f.name, '—')} |")

    lines += ["", "## 模板 templates/", "", "| 文件 | 用途 |", "|------|------|"]
    for rel in sorted(TEMPLATE_DESC):
        lines.append(f"| `templates/{rel}` | {TEMPLATE_DESC[rel]} |")

    lines += ["", "## skill 源 skills/", "", "| 文件 | 用途 |", "|------|------|"]
    for f in sorted((root / "skills").glob(f"{SKILL_PREFIX}*.md")):
        lines.append(f"| `{f.name}` | {_skill_description(f)} |")

    lines += [
        "",
        "## 相关位置",
        "",
        "| 位置 | 内容 |",
        "|------|------|",
        "| `~/.codebuddy/CODEBUDDY.md` | 全局规范（每次会话自动加载） |",
        "| `~/.codebuddy/skills/<name>/SKILL.md` | skill 触发入口（由中文源自动生成） |",
        "",
    ]

    print(f"  生成: {out}")
    if not dry_run:
        TARGET_DIR.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(lines), encoding="utf-8")
        if not out.is_file():
            print("  [error] [index] 写入失败")
            return -1
    print("  [ok] [index] 已生成")
    return 1


def check_copies(root: Path) -> int:
    """告警：仓库内的手工副本若落后于源，提示同步。

    覆盖两类极易漏改的副本（只告警不阻断，副本内容仍需人工确认后同步）：
    - `skills/dm-*/references/*.md`      ← `docs/NN-*.md`（规范副本）
    - `skills/dm-plan-ver/assets/*.md`   ← `templates/versions/vX.Y-<slug>/*.md`（模板副本）
    """
    pairs = []

    docs_src = {}
    for p in (root / DOCS_REL).glob("*.md"):
        docs_src[p.name.split("-", 1)[1] if "-" in p.name else p.name] = p
    for ref in sorted((root / "skills").glob("dm-*/references/*.md")):
        if ref.name in docs_src:
            pairs.append((ref, docs_src[ref.name]))

    version_src = {p.name: p for p in (root / VERSIONS_REL).glob("*/*.md")}
    for asset in sorted((root / "skills" / "dm-plan-ver" / "assets").glob("*.md")):
        if asset.name in version_src:
            pairs.append((asset, version_src[asset.name]))

    # 文件名不同但同源：dm-schedule 的排程模板 ← templates/versions/500-schedule.md
    sched_src = next((root / VERSIONS_REL).glob("*/500-schedule.md"), None)
    sched_copy = root / "skills" / "dm-schedule" / "assets" / "500-schedule-template.md"
    if sched_src and sched_copy.is_file():
        pairs.append((sched_copy, sched_src))

    stale = [(c, s) for c, s in pairs
             if c.read_text(encoding="utf-8") != s.read_text(encoding="utf-8")]

    if not stale:
        print("  [ok] [copies] 副本与源一致")
        return 0

    print("  [warn] [copies] 以下副本落后于源，请同步（不阻断发布）：")
    for copy, src in stale:
        print(f"        - {copy.relative_to(root)}  <-  {src.relative_to(root)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="将 dev-meta 模板、全局规范与 skill 发布到本地生效位置")
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

    worklog_dst = TARGET_DIR / "templates" / "worklog.md"
    print(f"\n[worklog] -> {worklog_dst}")
    if sync_file(root / "templates" / "worklog.md", worklog_dst, args.dry_run, "worklog") < 0:
        return 1

    print(f"\n[versions] -> {TARGET_DIR / VERSIONS_REL}（版本四件套模板，dm-plan-ver 运行时读取）")
    if sync_tree(root / VERSIONS_REL, TARGET_DIR / VERSIONS_REL, args.dry_run, "versions") < 0:
        return 1

    print(f"\n[site] -> {TARGET_DIR / SITE_REL}（站点脚手架模板，dm-pub-site 实例化用）")
    if sync_tree(root / SITE_REL, TARGET_DIR / SITE_REL, args.dry_run, "site") < 0:
        return 1

    print(f"\n[docs] -> {TARGET_DIR / DOCS_REL}（规范文档，供跨项目引用；不含 reports/）")
    if sync_dir(root / DOCS_REL, TARGET_DIR / DOCS_REL, "*.md", args.dry_run, "docs") < 0:
        return 1

    check_copies(root)

    global_dst = Path.home() / ".codebuddy" / "CODEBUDDY.md"
    print(f"\n[global] -> {global_dst}")
    if sync_file(root / "docs" / "CODEBUDDY-global.md", global_dst, args.dry_run, "global") < 0:
        return 1

    print(f"\n[skills] -> {TARGET_DIR / 'skills'}（仅 {SKILL_PREFIX}*.md）")
    if sync_dir(root / "skills", TARGET_DIR / "skills", f"{SKILL_PREFIX}*.md", args.dry_run, "skills") < 0:
        return 1

    # 非触发入口，但被 7 个 skill 正文引用（「原则见 skill-doc-principles §7」），必须可加载
    principles_dst = TARGET_DIR / "skills" / "skill-doc-principles.md"
    print(f"\n[principles] -> {principles_dst}")
    if sync_file(root / "skills" / "skill-doc-principles.md", principles_dst,
                 args.dry_run, "principles") < 0:
        return 1

    if args.deploy:
        print(f"\n[deploy] -> {DEPLOY_DIR}（触发入口，由中文源生成）")
        for src in sorted((root / "skills").glob(f"{SKILL_PREFIX}*.md")):
            name = src.stem
            target_dir = DEPLOY_DIR / name
            # 1) 同步该 skill 的资源目录（assets/ references/），保护待生成的 SKILL.md
            extra = root / "skills" / name
            if extra.is_dir():
                if sync_tree(extra, target_dir, args.dry_run,
                             f"{name} resources", preserve={"SKILL.md"}) < 0:
                    return 1
            # 2) 由中文源生成 SKILL.md（唯一权威）
            out = target_dir / "SKILL.md"
            print(f"  生成: {name}/SKILL.md  <-  {src.name}")
            if not args.dry_run:
                target_dir.mkdir(parents=True, exist_ok=True)
                out.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"\n[done] 资产已发布至 {TARGET_DIR}，触发入口已部署至 {DEPLOY_DIR}")
    else:
        print(f"\n[done] 已发布至本地全局资产目录: {TARGET_DIR}")
        print("       [hint] 加 --deploy 可同时部署 skill 触发入口至 ~/.codebuddy/skills/")

    print(f"\n[index] -> {TARGET_DIR / 'README.md'}（资产总索引，AI 单一入口）")
    if build_index(root, args.dry_run) < 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
