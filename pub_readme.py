#!/usr/bin/env python3
"""
pub_readme.py - 从 README.md（唯一权威）生成衍生版本：README.mdx 与 README.html

用法:
    python3 pub_readme.py            # 生成 README.mdx + README.html
    python3 pub_readme.py --dry-run  # 预演，只打印将要生成的内容

设计原则（与 dev-meta 自身一致）:
    README.md 是**唯一权威**；`.mdx` / `.html` 均为**生成产物，禁止手工编辑**。
    凡是靠人记得同步的环节都会漂移 —— 因此衍生版本一律由脚本生成。

两种产物的用途:
    README.mdx   供现代文档站（Docusaurus / Next.js MDX / VitePress）直接引用
    README.html  自包含单文件，直接用浏览器打开或部署到 GitHub Pages

依赖:
    - MDX 生成：纯文本处理，无依赖
    - HTML 生成：使用系统工具 pandoc（未安装时跳过 HTML 并提示，不影响 MDX）
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
SRC = ROOT / "README.md"
MDX = ROOT / "README.mdx"
HTML = ROOT / "README.html"

# MDX frontmatter：文档站用它生成页面标题与摘要
MDX_FRONTMATTER = """---
title: dev-meta
description: 开发元规范与工程标准，跨项目共享。以 Transaction Flow 为主轴，用「契约只读 / 可观测性 / 小批迭代」三支柱约束 AI 协作。
---

"""

# 自包含 HTML 样式（GitHub 风格，保证表格与代码块可读）
HTML_STYLE = """
<style>
  :root { color-scheme: light dark; }
  body {
    max-width: 900px; margin: 0 auto; padding: 2rem 1.5rem 4rem;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    line-height: 1.7; font-size: 16px;
  }
  h1, h2, h3 { line-height: 1.3; margin-top: 2rem; }
  h1 { border-bottom: 2px solid #d0d7de; padding-bottom: .3em; }
  h2 { border-bottom: 1px solid #d0d7de; padding-bottom: .3em; }
  code {
    background: rgba(175,184,193,.2); padding: .2em .4em;
    border-radius: 6px; font-size: 85%;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  }
  pre { background: rgba(175,184,193,.2); padding: 1rem; border-radius: 8px; overflow-x: auto; }
  pre code { background: none; padding: 0; }
  table { border-collapse: collapse; width: 100%; margin: 1rem 0; display: block; overflow-x: auto; }
  th, td { border: 1px solid #d0d7de; padding: .5rem .75rem; text-align: left; }
  th { background: rgba(175,184,193,.2); }
  tr:nth-child(2n) { background: rgba(175,184,193,.05); }
  blockquote { margin: 1rem 0; padding: 0 1rem; color: #57606a; border-left: .25em solid #d0d7de; }
  hr { border: 0; border-top: 1px solid #d0d7de; margin: 2rem 0; }
  a { color: #0969da; text-decoration: none; }
  a:hover { text-decoration: underline; }
</style>
"""


def build_mdx(text: str) -> str:
    """生成 MDX：加 frontmatter；正文与 Markdown 一致（README 无裸花括号，无需转义）。"""
    body = text
    # 若源文件已有 frontmatter 则不再叠加
    if body.startswith("---\n"):
        return body
    return MDX_FRONTMATTER + body


def build_html() -> int:
    """用 pandoc 生成自包含 HTML。返回 0 成功，1 失败/跳过。"""
    pandoc = shutil.which("pandoc")
    if not pandoc:
        print("  [warn] 未找到 pandoc，跳过 HTML 生成（MDX 不受影响）")
        print("         安装：brew install pandoc")
        return 1

    result = subprocess.run(
        [pandoc, str(SRC), "-f", "gfm", "-t", "html5", "-s",
         "--metadata", "title=dev-meta", "-o", str(HTML)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  [error] pandoc 失败: {result.stderr.strip()}")
        return 1

    # 注入样式，保证单文件自包含
    html = HTML.read_text(encoding="utf-8")
    if HTML_STYLE not in html:
        html = html.replace("</head>", f"{HTML_STYLE}\n</head>", 1)
        HTML.write_text(html, encoding="utf-8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="从 README.md 生成 .mdx 与 .html 衍生版本")
    parser.add_argument("--dry-run", action="store_true", help="预演，不写入")
    args = parser.parse_args()

    if not SRC.is_file():
        print(f"[error] 源文件不存在: {SRC}")
        return 1

    text = SRC.read_text(encoding="utf-8")

    if args.dry_run:
        print("=== [dry-run] 预演模式 ===\n")
        print(f"[mdx]  -> {MDX}")
        print(f"       frontmatter: {len(MDX_FRONTMATTER.splitlines())} 行 + 正文 {len(text.splitlines())} 行")
        print(f"[html] -> {HTML}")
        print(f"       pandoc: {'可用' if shutil.which('pandoc') else '未安装（将跳过）'}")
        return 0

    MDX.write_text(build_mdx(text), encoding="utf-8")
    print(f"[ok] 已生成 {MDX.name}（{len(MDX.read_text(encoding='utf-8').splitlines())} 行）")

    if build_html() == 0:
        print(f"[ok] 已生成 {HTML.name}（{len(HTML.read_text(encoding='utf-8').splitlines())} 行）")

    print("\n[done] 衍生版本已生成；README.md 仍是唯一权威，请勿手工编辑 .mdx / .html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
