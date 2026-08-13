# C-001 - Real Upstream Topology

> Stage: 1 - `retire-v1-topology-residue`
> 类型: `UNAMBIGUOUS-RETIRE`
> 状态: **REVIEWED - APPROVED FOR STAGE 1 PLANNING ONLY**

## 调整内容到底是什么

修改 `openspec/config.yaml`、local `AGENTS.md`、Charter 及 approved delta 所拥有的
current authority，把“根 `backend/` / `frontend/` 是 DeerFlow mirrors”改成“根
`deerflow/` 是只 leverage、不修改的 upstream gitlink”。下游产品仍由
`deep_research_harness/` 拥有。

## 主要风险

字符串级批量替换会误伤真实 `deerflow/backend/packages/harness` 依赖路径、
database/persistence backend、host compatibility path，以及仍可能有效的 legacy-root
negative drift guard。

## 可能副作用

- contributor 可能把“gitlink 是边界”误读为可浏览其源码；
- 新措辞可能被误读成已有 gitlink/diff 机械 detector；
- 若只同步部分 authority，会出现新的迁移中间态冲突。

## 控制与停止条件

- 每个 `backend` / `frontend` occurrence 必须人工分类；无法判定则进入 quarantine。
- 在同一个获授权 change 内原子同步受影响 authority。
- 明确“不读取 DeerFlow 源码”与“A-002 仍为 deferred”。
- 若需改 checker、test、manifest/TOML 或读取 `deerflow/` 源码，立即停止。

## 审阅结论

- [x] 调整内容准确
- [x] 风险与副作用已充分披露
- [x] 批准进入 Stage 1 planning
- [ ] 需要修改或补充，原因：

> 审阅确认: 2026-08-12。仅批准逐 occurrence 的 planning；禁止批量替换，继续公开
> A-002 自动防护尚未实现。未授权创建/apply OpenSpec change，也未授权修改 target
> authority。
