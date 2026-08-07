# Dev-Meta 规范（全局原始版本）

<!--
  本文件是 ~/.codebuddy/CODEBUDDY.md 的 source of truth。
  所有规范修改在此处进行（受 Git 版本控制），修改后复制到 ~/.codebuddy/CODEBUDDY.md 生效。
-->

本文件由 dev-meta 维护，CodeBuddy 每次会话自动加载。
业务项目通过 `./CODEBUDDY.md` 绑定 dev-meta 版本及例外项，无需复制规范正文。

## 通用 DoD (Definition of Done)

每个 PR / commit / TF 交付前应满足：

- [ ] 本地构建通过 / 可运行
- [ ] 手动冒烟验证（核心路径不走查）
- [ ] commit 遵循 dm-commit 规范
- [ ] 涉及文档已同步更新
- [ ] worklog 已记录

## AI 协作约定

### 多文件变更优先脚本化

对跨度大的同类变更：

1. **先评估**：变更涉及 ≥ 3 个文件，且逻辑为简单文本替换/匹配
2. **可脚本则脚本**：用 `sed`、`awk`、`bash` 或 Python 脚本批量执行，一次到位
3. **不可脚本再编辑**：涉及结构调序、上下文判断、条件性替换时，逐文件编辑

目的：减少 token 消耗、保证多文件一致性、避免遗漏。

## 编码约定

- 禁止魔术数字（用命名常量）
- 单文件 ≤ 300 行
- 公共函数有注释说明意图

## 工作日志指引

1. 项目初始化时从 `templates/worklog.md` 复制到 `docs/reports/worklog.md`
2. **每天结束时更新**：在「每日工作总结」表顶部加一行，在下方新增日期章节
3. 当日有 commit 则列出；无 commit 则在「其他工作」中记录
4. 待办与里程碑随进度同步维护
