---
name: dm-pub-site
description: 把当前项目发布成 GitHub Pages 站点：从 ~/.dev-meta/templates/site 实例化 Astro 脚手架（content/ 为内容源），按目录生成索引树，本地构建后推 dist 到 gh-pages 分支，并用 gh CLI 自动启用 Pages。触发于「发布站点」「发布 gh page」「建站」。
---

# dm-pub-site

## 概述

站点发布 skill。在目标项目内实例化 Astro 脚手架（`site/`），以 `site/content/` 为**内容源**，按目录结构生成可折叠目录树索引；本地构建后把 `dist/` 推到 `gh-pages` 分支，并用 `gh` CLI 自动完成 Pages 配置。

## 职责边界

| 职责 | 归属 |
|---|---|
| 实例化脚手架、填 `base`、构建、推送 | ✅ 本 skill（自动执行，失败才提示） |
| 创建 gh-pages 分支 / 启用 Pages | ✅ 本 skill（自动执行，失败才提示） |
| 内容组织（往 `content/` 放文件） | 用户 |
| 站点视觉定制 | 用户（改 `site/src` 样式） |
| 自定义域名（需 DNS 解析） | ❌ 人工，本 skill 只提示 |
| CI 自动发布（push main 即构建） | ❌ 本版不做，后续扩展项 |

## 触发

- "发布站点"
- "把这个项目发布成 gh page"
- "建站"
- "/dm-pub-site"

## 核心概念

### 内容源：`site/content/` 就是内容的家

- 支持 `.md` / `.mdx` / `.html`
- **不从项目其它目录（`docs/` 等）复制内容** —— 复制会产生同一内容的多份副本，必然漂移
- 目录结构直接映射为目录树索引与 URL

### 索引是派生物

首页目录树与各页面路由全部由构建生成。**禁止手工编辑 `site/dist/`**（每次构建覆盖）。

### `base` 必须设置

项目站点地址是 `https://<user>.github.io/<repo>/`，故 `astro.config.mjs` 的 `base` 必须为 `/<repo>`（从 `git remote` 解析）。漏设则**所有资源 404**。

### `.nojekyll` 必须生成

GitHub Pages 默认跑 Jekyll，**忽略下划线开头的目录**。Astro 产物含 `_astro/`（CSS/JS）时，缺此文件会导致样式与脚本全 404，且**不报错**、极易误判为成功。

> 注：极简站点可能把样式内联而不产出 `_astro/`，此时不触发；但只要有客户端 JS 或较大 CSS 就会触发。成本为零、收益确定，故作为**强制步骤**。

### gh-pages 分支策略

**孤儿分支 + 单次 commit + force push**。构建产物没有保留历史的价值，分支永远只有 1 个 commit。

## 执行流程

> **总原则：先自动、后提示** —— 每个可自动化步骤先执行；失败则打印该步的**确切手工命令**与失败原因，停下来问人。不静默跳过、不猜测继续。

### 1. 前置检查

```bash
gh auth status                    # 失败 → 提示 gh auth login
node --version                    # 需 ≥ 18.20.8 / 20.3+ / 22+
ls ~/.dev-meta/templates/site/    # 缺失 → 提示先在 dev-meta 跑 python3 pub_local.py
```

### 2. 实例化脚手架

```bash
mkdir -p site && cp -r ~/.dev-meta/templates/site/. site/
cd site && npm install
```

从 `git remote get-url origin` 解析 `<repo>`，写入 `astro.config.mjs` 的 `base: '/<repo>'`。

### 3. 本地构建

```bash
npm run build
```

校验：`dist/index.html` 存在、目录树节点数 > 0。

### 4. 生成 `.nojekyll`

```bash
touch dist/.nojekyll
```

### 5. 推送到 gh-pages（孤儿分支 + force push）

```bash
cd dist
git init -q && git checkout -q -b gh-pages
git add -A && git commit -q -m "publish site"
git push -f <remote> gh-pages
```

### 6. 启用 Pages（幂等）

```bash
gh api -X POST repos/<owner>/<repo>/pages \
  -f "source[branch]=gh-pages" -f "source[path]=/"
```

- 返回 **409**（已启用）→ 改用 `PATCH` 更新 source，**不当失败**
- 其它失败 → 提示网页路径 Settings → Pages → Source

### 7. 验证

```bash
gh api repos/<owner>/<repo>/pages                  # 查状态
curl -fsSL https://<user>.github.io/<repo>/        # 失败 → 提示浏览器打开（首次构建约 1-2 分钟）
```

## 关键规则速查

| 规则 | 来源 |
|---|---|
| 内容源唯一：只写 `content/`，不从 `docs/` 等目录复制 | 反多份副本（单一权威） |
| 索引与路由是派生物，禁止手工编辑 `dist/` | 本 skill 核心概念 |
| `base` 必须为 `/<repo>`，否则资源 404 | 本 skill 核心概念 |
| 推送前必须生成 `dist/.nojekyll` | GitHub Pages + Jekyll 行为 |
| gh-pages 用孤儿分支 + 单次 commit + force push | 本 skill 核心概念 |
| Pages API 409 → 改 `PATCH` 更新，不判失败 | 幂等要求 |
| **先自动执行，失败才提示用户手工命令** | 本 skill 总原则 |
| 自定义域名需人工配 DNS；组织级禁用 Pages 无法自动化 | 超出自动化范围 |

## 产出与完成判据

**产出**：项目内 `site/`（脚手架 + content）、`gh-pages` 分支、Pages 站点

**完成判据**：

- [ ] `site/content/` 已放入内容
- [ ] `astro.config.mjs` 的 `base` = `/<repo>`
- [ ] `npm run build` 通过，`dist/index.html` 含目录树
- [ ] `dist/.nojekyll` 已生成
- [ ] `gh-pages` 分支已推送（孤儿单 commit）
- [ ] Pages 已启用且指向 `gh-pages`
- [ ] 站点 URL 可访问，抽查 2 条内链无 404

## 资源映射

| 资源 | 来源 | 用途 |
|---|---|---|
| `~/.dev-meta/templates/site/` | `templates/site/`（dev-meta 经 `pub_local.py` 发布） | Astro 脚手架模板 |
| `gh` CLI | 系统 | 仓库 / Pages API 操作 |

## 使用示例

```
用户: "把这个项目发布成 gh page"

AI:  1. 前置检查：gh auth status ✅ / node v22 / 模板已发布 ✅
     2. 解析 remote → repo = PochiHide，实例化 site/ 并写 base: '/PochiHide'
     3. 提示：把要发布的内容放进 site/content/（.md / .mdx / .html）
     4. npm run build → 校验 dist/index.html 含目录树
     5. touch dist/.nojekyll
     6. 孤儿分支 + force push → gh-pages
     7. gh api 启用 Pages（409 则 PATCH）
     8. curl 验证 https://<user>.github.io/PochiHide/
```
