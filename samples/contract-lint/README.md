# contract-lint — 契约结构 lint（参考实现）

`docs/06-contract-based-dev.md` **§8.4** 的可执行落地：对**契约文档本身**做形态校验。

> **与 `samples/contract-gate/` 的分工**（`docs/06` §8）：
> | 门禁 | 校验对象 | 手段 |
> |---|---|---|
> | **本目录 contract-lint** | 契约**文档**（形态：链接 / 状态 / 锚点 / 引用方向） | 纯文本静态检查，零依赖 |
> | `samples/contract-gate/` | 契约对应的**产物**（语义：编译 / Schema / sha256 / `contract_verified`） | 编译、Schema、哈希指纹 |
>
> 二者互补、**不可互替**：lint 过了不等于契约语义正确；产物门禁过了不等于文档无死链。

## 四查（LINT-01 … 04）

| 编号 | 校验项 | 违例即失败 |
|------|--------|------------|
| LINT-01 | 引用**零死链** | `path.md#slug` 指向的不是契约文档，或该锚点不在那个文件 |
| LINT-02 | **一条一标** | 某锚点块内**规范状态标记**（`- 状态：`[X]``）数 ≠ 1（缺失 / 重复）。说明性文字与首个锚点之前的区域**不计** |
| LINT-03 | 锚点**唯一且格式合法** | slug 重复，或不匹配 `^[a-z][a-z0-9]*(-[a-z0-9]+)+$` |
| LINT-04 | 契约**不引下游** | 契约文档内出现版本文档 / 计划 / 上层规格的路径 |

引用约定：**root-relative** 书写，如 `docs/contracts/02-render.md#render-host-dispatch`；接受裸文件名简写，但「slug 实际在另一个文件」仍判违规（`docs/06` §7.2）。

## 用法

```bash
# 目录形态（docs/06 §6.2）
python3 contract_lint.py --root . --contracts-dir docs/contracts

# 单文件形态（docs/06 §6.1，小项目起点）
python3 contract_lint.py --root . --contract-file docs/03_CONTRACTS_AND_API.md

# 迁移到第 3 步后：锚点成为硬要求
python3 contract_lint.py --root . --contracts-dir docs/contracts --require-anchors

# 自证 linter 有效（内置样本，无需任何 fixture 文件）
python3 contract_lint.py --self-test
```

**退出码**：`0` 全绿 ｜ `1` 有违规（逐条列出，绝不静默通过）｜ `2` 用法 / IO 错误。

**参数**

| 参数 | 说明 |
|------|------|
| `--root` | 仓库根（默认当前目录） |
| `--contracts-dir` | 契约目录（目录形态） |
| `--contract-file` | 单文件契约（单文件形态）；与 `--contracts-dir` 可并存 |
| `--require-anchors` | 无锚点即失败。**建议在 `docs/06` §6.7 迁移第 3 步之后再启用**，否则早期项目会误报 |
| `--downstream-pattern` | 下游路径正则，可重复；默认 `(?:docs\|templates)/versions/` |
| `--quiet` | 不逐文件列出统计 |

## 接入（`docs/06` §8.4）

- **关版本前必跑** —— 对齐 `docs/02-version-rules.md` §6.2 S7；
- **Gate 2 改后卡口一并执行** —— 见 `skills/dm-contract-gate.md`（与 `samples/contract-gate/` 双门禁）。

## 自检

```bash
$ python3 contract_lint.py --self-test
✅ self-test 通过：合法样本全绿，四类违规全部被捕获
```

self-test 用临时目录构造「合法样本 + 违规样本」，断言四类违规全部被捕获 —— **脚本自身可被验证**，不必依赖仓库内 fixture 漂移。
