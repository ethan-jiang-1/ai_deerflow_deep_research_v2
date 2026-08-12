# C-002 - Proposal And Closeout Boundary

> Stage: 1 - `retire-v1-topology-residue`
> 类型: `UNAMBIGUOUS-RETIRE`; A-002 remains `DEFERRED-CODE-CHANGE`
> 状态: **REVIEW REQUIRED**

## 调整内容到底是什么

将 `openspec/config.yaml` 中“保持旧根 `backend/` / `frontend/` clean”的
proposal/archive 文案，改为普通 change 不拥有 `deerflow/` gitlink，并要求记录当前可
取得的 scope/diff 人工证据。

## 主要风险

只删旧规则会留下保护真空；写成“系统验证 gitlink clean”则会虚构当前 checker 没有的
能力。

## 可能副作用

- archive closeout 增加人工核查成本；
- architecture checker 仍可能对真实 gitlink 风险假绿；
- prose rule 无法阻止本地 submodule worktree 被改动。

## 控制与停止条件

- 不改 checker、tests、manifest 或 TOML。
- 规则和验证报告必须区分人工 evidence 与 mechanical enforcement。
- 若诚实表述必须依赖新 detector，停止并保持 A-002 为 `DEFERRED-CODE-CHANGE`。

## 审阅结论

- [ ] 调整内容准确
- [ ] 风险与副作用已充分披露
- [ ] 批准进入 Stage 1 planning
- [ ] 需要修改或补充，原因：
