# C-003 - Editable Harness Path

> Stage: 1 - `retire-v1-topology-residue`
> 类型: `UNAMBIGUOUS-RETIRE`
> 状态: **REVIEWED - APPROVED FOR STAGE 1 PLANNING ONLY**

## 调整内容到底是什么

将 `deep_research_harness/README.md` 中不存在的 `../backend/packages/harness` 改为当前
checkout 实际使用的 `../deerflow/backend/packages/harness`，同时写清命令运行目录。

## 主要风险

只修路径字符串但忽略运行目录，示例仍可能不可执行；路径里的合法 `backend` 也可能被
后续清理误删。

## 可能副作用

仍使用 V1 外部目录布局的个人环境不再符合文档。这是支持边界收紧，不是运行时代码
回退。

## 控制与停止条件

- 与 `pyproject.toml`、lockfile 和根运行说明交叉核对。
- 不修改 dependency metadata，也不借此新增另一套安装方式。
- 若真实安装命令与三处权威仍不一致，停止并记录新 finding。

## 审阅结论

- [x] 调整内容准确
- [x] 风险与副作用已充分披露
- [x] 批准进入 Stage 1 planning
- [ ] 需要修改或补充，原因：

> 审阅确认: 2026-08-12。README 示例必须同时校对真实路径和运行目录；不修改
> `pyproject.toml`、lockfile、dependency metadata、代码或 target authority。未授权
> 创建/apply OpenSpec change。
