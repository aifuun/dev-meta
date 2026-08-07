# CODEBUDDY.md Management

## 1. 概述

CodeBuddy 每次会话自动加载 `CODEBUDDY.md` 文件作为 AI 上下文。dev-meta 利用这一机制实现两层规范分发，替代此前的 `dev-reference.md` 入口文档。

## 2. 两层架构

### 2.1 全局层 — `~/.codebuddy/CODEBUDDY.md`

跨项目通用规范，用户维护一次，所有项目自动加载：

- **通用 DoD**：每个 PR/commit/TF 交付前的验收 checklist
- **AI 协作约定**：多文件变更脚本优先原则
- **编码约定**：命名规范、文件行数限制、注释要求
- **工作日志指引**：复制模板、每日更新、格式规范

### 2.2 项目层 — `./CODEBUDDY.md`

每个业务项目独有的配置，随 Git 仓库版本管理：

- **dev-meta 版本绑定**：引用的 dev-meta 仓库地址与 tag/commit
- **本项目例外项**：与通用规范的差异及理由

### 2.3 加载机制

CodeBuddy 启动时递归加载所有 `CODEBUDDY.md`：

```
~/.codebuddy/CODEBUDDY.md          ← 全局通用规范
    ↓ （自动合并）
./CODEBUDDY.md                      ← 项目版本绑定 + 例外项
```

两条内容同时注入上下文，项目级规则可覆盖全局规则。

## 3. 项目初始化流程

`dm-init` 在项目初始化时：

1. 从 `assets/CODEBUDDY.md` 模板创建 `./CODEBUDDY.md`
2. 填写 dev-meta 仓库地址与版本号
3. 填写项目例外项（无则留"无"）

通用规范不在项目内重复，由 `~/.codebuddy/CODEBUDDY.md` 统一提供。

## 4. 全局规范维护

### 4.1 原始版本与部署副本

全局规范采用"原始版本 → 部署副本"模式：

```
dev-meta/docs/CODEBUDDY-global.md     ← 原始版本（Git 跟踪，在此修改）
        │  复制覆盖
        ▼
~/.codebuddy/CODEBUDDY.md             ← 部署副本（CodeBuddy 实际加载）
```

**原则**：所有规范修改在 `docs/CODEBUDDY-global.md` 中进行，commit 后手动复制到 `~/.codebuddy/CODEBUDDY.md` 生效。

### 4.2 修改流程

1. 编辑 `docs/CODEBUDDY-global.md`（如新增 DoD 条目、调整编码约定）
2. commit 变更
3. 部署到生效位置：对 AI 说「部署全局规范」或「update global CODEBUDDY」，AI 执行 `cp docs/CODEBUDDY-global.md ~/.codebuddy/CODEBUDDY.md`
4. 所有业务项目下次会话自动应用新规范

### 4.3 为什么要这样做

- **版本控制**：每次规范变更都有 Git 历史可追溯
- **团队同步**：其他开发者 clone dev-meta 后可直接部署相同的全局规范
- **安全回滚**：改坏了可以 `git revert` 再重新部署

## 5. 迁移说明

### 旧方案（dev-reference.md）

```
docs/01-dev-reference.md  ← 项目级入口（含部分通用规则）
~/.codebuddy/CODEBUDDY.md ← 无或无关
```

### 新方案（两层 CODEBUDDY.md）

```
~/.codebuddy/CODEBUDDY.md ← 全局通用规范
./CODEBUDDY.md            ← 项目版本绑定 + 例外项
```

### 迁移步骤

1. 将 `docs/01-dev-reference.md` 的内容拆分为全局和项目两部分
2. 通用内容移到 `~/.codebuddy/CODEBUDDY.md`
3. 项目特定内容（版本绑定 + 例外）移到 `./CODEBUDDY.md`
4. 删除 `docs/01-dev-reference.md`
