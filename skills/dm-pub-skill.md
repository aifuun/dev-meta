---
name: dm-pub-skill
description: 发布/部署 dev-meta 资产与 skill：模板发布到 ~/.dev-meta/，skill 触发入口部署到 ~/.codebuddy/skills/。触发于「发布 skill」「部署模板」「同步资产」。
---

# dm-pub-skill

## 概述

发布与部署 skill：把 `dev-meta` 仓库的**模板资产**发布到 `~/.dev-meta/`，并把 **skill 触发入口**（`SKILL.md` + `assets/` + `references/`）部署到 `~/.codebuddy/skills/`——其中 `SKILL.md` **由中文源自动生成**（单一权威，禁止手改）。实际文件同步由 `pub_local.py` 执行，本 skill 负责**编排、前置检查与校验**，让发布/部署可复现、可校验、新人可照做。

## 职责边界

| 职责 | 归属 |
|------|------|
| 发布模板资产与中文设计文档到 `~/.dev-meta/` | ✅ 本 skill |
| 部署 skill 触发入口到 `~/.codebuddy/skills/` | ✅ 本 skill |
| 前置检查（模板齐全、中文源 frontmatter、资源目录匹配） | ✅ 本 skill |
| 实际文件同步（清理 → 拷贝 → 校验） | `pub_local.py`（本 skill 调用） |
| 修改模板内容 / 编写 skill 设计文档 | ❌ `dm-init-docs` / 各 skill 自身 |
| 格式校验（`package_skill.py`） | 外部工具（本 skill 调用并解读结论） |
| 提交 | 委托 `dm-commit` |

## 触发

- "发布 skill"
- "部署模板"
- "同步资产"
- "publish" / "deploy"
- 改完 `templates/` 或 `skills/` 后需要生效时

## 核心概念

### 资产布局

| 位置 | 角色 | 内容 | 谁读 |
|------|------|------|------|
| `~/.dev-meta/templates/` | **模板**（骨架） | `CODEBUDDY.md` + `project/docs/00~06_*.md` | `dm-init-docs` 渲染新项目文档 |
| `~/.dev-meta/docs/` | **规范文档**（权威副本） | `01~09_*.md` + `CODEBUDDY-global.md` | AI **跨项目**引用（如「见 06 契约只读」） |
| `~/.dev-meta/skills/` | **skill 中文源**（唯一权威） | `dm-*.md` | 生成部署版 + 存档 |
| `~/.dev-meta/README.md` | **资产总索引**（自动生成） | 上述全部文件及一句话用途 | AI 的**单一入口** |
| `~/.codebuddy/CODEBUDDY.md` | **全局规范** | DoD、编码约定、01~09 导航 | 每次会话自动加载 |
| `~/.codebuddy/skills/<name>/` | **触发入口**（CodeBuddy 只从这里加载 skill） | `SKILL.md`（**由中文源自动生成**，含 frontmatter）+ `assets/` + `references/` | CodeBuddy 加载并触发 |

> **不可互相替代**：只发布资产 → skill 不会出现在可触发列表；只部署入口 → AI 找不到模板资产。
> **规范文档为什么也要发布**：业务项目里没有 `docs/06`，若 `~/.dev-meta/docs/` 也缺失，skill 中「见 `docs/06`」的引用就成了**盲引用**。发布后跨项目可读。

### 仓库内的源文件

| 路径 | 角色 | 去向 |
|------|------|------|
| `skills/<name>.md` | **唯一权威**：中文源（含 YAML frontmatter） | → `~/.dev-meta/skills/`，并生成 `~/.codebuddy/skills/<name>/SKILL.md` |
| `skills/<name>/assets/`、`references/` | 随触发入口一同部署 | → `~/.codebuddy/skills/<name>/` |
| `docs/*.md`（顶层，不含 `reports/`） | 规范文档原始版本 | → `~/.dev-meta/docs/` |
| `templates/` | 模板原始版本 | → `~/.dev-meta/templates/` |

> 仓库内**没有** `skills/<name>/SKILL.md` 源文件——它是部署产物，由脚本从中文源生成。同时存在 `skills/dm-adr.md`（中文源）与 `skills/dm-adr/`（`assets/`+`references/`）是正常的。

### 幂等与安全

- **先清理后拷贝**：删除目标中源已不存在的文件，防改名/下线后残留。
- **忽略垃圾文件**：`__pycache__`、`.DS_Store` 不参与同步。
- **同步后校验**：核对文件数，不一致则非 0 退出。
- **预演**：`--dry-run` 先看清单，不写入。

## 执行流程

### 1. 前置检查

在仓库根目录执行：

- `templates/project/docs/` 是否含 7 个模板（00~06）
- `templates/CODEBUDDY.md` 是否存在
- `docs/` 是否含 01~09 与 `CODEBUDDY-global.md`（共 10 个；`reports/` 不发布）
- 每个中文源 `skills/<name>.md` 是否含 YAML frontmatter（`name` + `description`）——缺失会导致部署后无法被 CodeBuddy 触发

发现问题先报告并询问，不强行发布。

### 2. 预演

```bash
python3 pub_local.py --deploy --dry-run
```

确认清单与文件数无误。

### 3. 执行发布与部署

```bash
python3 pub_local.py --deploy
```

仅发布资产（不碰触发入口）时用：

```bash
python3 pub_local.py
```

### 4. 校验

- 脚本内建：每个目录同步后核对文件数，失败非 0 退出。
- 抽查：`~/.codebuddy/skills/<name>/SKILL.md` 存在且含 frontmatter。
- 抽查：`~/.dev-meta/templates/project/docs/` 含 7 个模板。
- 可选：对单个 skill 跑格式校验：

```bash
python3 ~/.vscode/extensions/tencent-cloud.coding-copilot-*/out/extension/builtin/skill-creator/scripts/package_skill.py ~/.codebuddy/skills/<name> /tmp
```

### 5. 报告与提交

输出发布报告（资产清单、部署清单、清理项、校验结果）。改动需入库时委托 `dm-commit`。

## 关键规则速查

| 规则 | 来源 |
|------|------|
| 资产走 `~/.dev-meta/`，触发入口走 `~/.codebuddy/skills/<name>/` | 本文核心概念 |
| skill 只维护中文源 `skills/<name>.md`（含 frontmatter），部署版 `SKILL.md` 由脚本生成、禁止手改 | skill-doc-principles §5 |
| 新增/修改 skill 只改中文源，随后 `python3 pub_local.py --deploy` 生效 | skill-doc-principles §5 |
| 发布/部署须先 `--dry-run` 预演 | 本文执行流程 |
| 同步为「先清理后拷贝 + 文件数校验」，失败非 0 退出 | `pub_local.py` |
| 忽略 `__pycache__` / `.DS_Store` | `pub_local.py` |
| 只发布资产不加 `--deploy`；需 skill 可触发必须加 `--deploy` | 本文执行流程 |
| 提交委托 `dm-commit` | dm-commit |

## 产出与完成判据

**产出**：

- `~/.dev-meta/docs/` 规范文档已发布（01~09 + CODEBUDDY-global，跨项目可读）
- `~/.dev-meta/templates/` 模板已发布（CODEBUDDY 模板 + 00~06 骨架）
- `~/.dev-meta/skills/` 14 篇中文源已发布
- `~/.dev-meta/README.md` **资产总索引**已生成（AI 单一入口）
- `~/.codebuddy/CODEBUDDY.md` 全局规范已部署（默认执行）
- `~/.codebuddy/skills/<name>/` 触发入口已部署（`--deploy`）
- 发布报告：资产清单 / 部署清单 / 清理项 / 校验结果

**完成判据**：

- [ ] 模板 7 个齐全、`templates/CODEBUDDY.md` 存在
- [ ] `docs/` 10 个规范文档已同步（不含 `reports/`）
- [ ] 16 个中文源均含 YAML frontmatter
- [ ] 同步后**文件数校验通过**（无 `[error]`，退出码 0）
- [ ] 抽查 `~/.codebuddy/skills/<name>/SKILL.md` 存在且含 frontmatter
- [ ] `~/.dev-meta/README.md` 已生成，且 skill 用途与其 frontmatter 描述一致
- [ ] 发布报告已输出

## 资源映射

| 资源 | 来源 | 用途 |
|------|------|------|
| `pub_local.py` | 仓库根目录 | 发布与部署执行引擎（零第三方依赖） |
| `templates/project/docs/0X_*.md` | `templates/project/docs/` | 项目文档模板（发布至 `~/.dev-meta/`） |
| `templates/CODEBUDDY.md` | `templates/` | 项目层 CODEBUDDY 模板 |
| `skills/<name>.md` | `skills/` | 中文设计文档（发布至 `~/.dev-meta/skills/`） |
| `skills/<name>/assets/`、`references/` | `skills/<name>/` | 随触发入口部署（`SKILL.md` 为生成物，不在仓库保存） |
| `docs/*.md`（顶层） | `docs/` | 规范文档（发布至 `~/.dev-meta/docs/`，**不含 `reports/`**） |
| `~/.dev-meta/README.md` | 脚本生成 | 资产总索引（AI 单一入口；skill 用途取自其 frontmatter） |
| `package_skill.py` | skill-creator 扩展 | skill 格式校验（frontmatter / 结构） |

## 使用示例

```
用户: "发布 skill"

AI:  1. 前置检查：模板 7 个齐全 ✅ / CODEBUDDY.md ✅ / 16 个中文源含 frontmatter ✅
     2. 预演：python3 pub_local.py --deploy --dry-run
        [templates] 7 个文件 · [codebuddy] 1 · [skills] 16 · [deploy] 16 个 skill
     3. 执行：python3 pub_local.py --deploy
     4. 校验：文件数一致，抽查 dm-plan-ver（6 文件）与 dm-arch-design（1 文件）
     5. 报告：资产已发布至 ~/.dev-meta/，触发入口已部署至 ~/.codebuddy/skills/
```

```
用户: "我只改了 00 模板，帮我发布"

AI:  1. 仅模板变更 → 不需要 --deploy
     2. python3 pub_local.py --dry-run → 确认
     3. python3 pub_local.py
     4. 报告：7 个模板已更新至 ~/.dev-meta/templates/project/docs/
```
