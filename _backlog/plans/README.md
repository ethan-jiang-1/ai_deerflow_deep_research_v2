# Plans — plan/分析文档索引

> 最后更新: 2026-09-01 | `_backlog/plans/` — 活跃 plan 在此（顶层），冻结未关闭的历史在
> [`archive/`](archive/)，完成的普通 plan 移入 [`../_done/_closed_plans/`](../_done/_closed_plans/)。
>
> **plan 没有编号，文件名即标识。完成后文件名不变，位置即状态。**

## 完成一个 plan 的步骤

1. `git mv plans/<name>.md _done/_closed_plans/<name>.md`
2. 更新 `_done/_closed_plans/README.md`（加一行 + 更新 Next available plan ID）
3. 更新本文件（删掉该 plan）
4. 更新 `../_done/README.md`（计数 +1 closed）

**plan 是"分析/设计/复盘"文档，不是活跃 change 本身。** 真正的实施走 `openspec/changes/`；plan 记录的是思考、取舍、复盘（postmortem），一旦其结论已落地或被 change 吸收即可关闭。

---

## 活跃列表

| Plan | 类型 | 下一步 |
|------|------|--------|
| [tui_step_progressive_plan.md](tui_step_progressive_plan.md) | 递进执行计划 | Local workflow debugger（当前唯一活跃 plan）：历史 C1/C2 已归档；下一步只可 propose C0 observation truth，之后 C3 trace/context/workspace observation -> C4a headless driving -> C4b TUI adapter -> real validation；并行线含 B1 第 3 跑收尾 |

**Next available plan ID: CLS-058**（移入 `_closed_plans/` 时分配）

## 冻结存档（`archive/`，只读，未关闭）

> 位置即状态：`archive/` = 冻结的历史稿（不再更新，旧相对链接随层级失效属预期）。
> 未关闭 ≠ 完成；战役收口后按上面步骤整组迁入 `_done/_closed_plans/`。

| Plan | 是什么 | 冻结日期 |
|------|--------|----------|
| [archive/tui-interactive-campaign-digested.md](archive/tui-interactive-campaign-digested.md) | 020 战役计划 v5——**已消化（DIGESTED）**，历史 provenance；§10 已被当前 progressive plan 取代 | 2026-08-31 |
| [archive/tui-interactive-campaign-progress-digested.md](archive/tui-interactive-campaign-progress-digested.md) | 战役进度账本（Phase 0–8 全记录）——**已消化（DIGESTED）**，已退役快照 | 2026-08-31 |
| [archive/tui-interactive-campaign-review-digested.md](archive/tui-interactive-campaign-review-digested.md) | 独立审阅——**已消化（DIGESTED）**，被 campaign v4 消化 | 2026-08-31 |
| [archive/tui_feedback_56.md](archive/tui_feedback_56.md) | 计划一致性审阅反馈——**已消化（DIGESTED）**，结论全部回填当前 plan 与 supporting 文档，仅作 provenance | 2026-09-01 |
| [archive/tui-step-debugger-grounding-review.md](archive/tui-step-debugger-grounding-review.md) | 当前 debugger plan 的冻结证据底稿、纠错、E4 结果与被拒方案；不是执行权威 | 2026-08-31 |
| [archive/tui-workflow-debugger-target-ux.md](archive/tui-workflow-debugger-target-ux.md) | C0-C4b 落地后的完整 operator UX：Run Bundle、captured node-agent context、bounded inner activity、runtime MD/mounted workspace、负路径与 plan traceability；不是当前能力声明 | 2026-09-01 |

## 已归档（移至 `_done/_closed_plans/`）

| Plan | Change | 归档日期 |
|------|--------|----------|
| deep-research-00-runtime-infrastructure.md | 00 | 2026-07-12 |
| deep-research-01-fake-graph-skeleton.md | 01 | 2026-07-12 |
| deep-research-02-state-persistence-contracts.md | 02 | 2026-07-13 |
| deep-research-03-gate-kernel.md | 03 | 2026-07-13 |
| deep-research-04-work-unit-kernel.md | 04 | 2026-07-14 |
| deep-research-05-bootstrap-node.md | 05 | 2026-07-15 |
| deep-research-06-hitl1-node.md | 06 | 2026-07-15 |
| deep-research-07-topic-planning-node.md | 07 | 2026-07-15 |
| deep-research-08-wave0-node.md | 08 | 2026-07-16 |
| deep-research-09-evidence-critic-nodes.md | 09 | 2026-07-16 |
| deep-research-10-wave1-node.md | 10 | 2026-07-16 |
| deep-research-11-wave2-synthesis-node.md | 11 | 2026-07-16 |
| deep-research-12-targeted-evidence-loop.md | 12 | 2026-07-16 |
| deep-research-13-hitl2-node.md | 13 | 2026-07-16 |
| deep-research-14-rerun-node.md | 14 | 2026-07-16 |
| deep-research-15-readiness-node.md | 15 | 2026-07-16 |
| deep-research-tui-hitl-terminal-workbench.md | CLS-001 | 2026-07-13 |
| test-assets-postmortem-real-mode-integration.md | CLS-003 | 2026-07-17 |
| test-assets-bug-to-test-mapping.md | CLS-004 | 2026-07-17 |
| test-assets-demo-design-coverage.md | CLS-005 | 2026-07-17 |
| test-assets-layered-strategy.md | CLS-006 | 2026-07-17 |
| deep-research-test-assets-master-strategy.md | CLS-007 | 2026-07-17 |
| deep-research-demo-full-pipeline.md | CLS-008 | 2026-07-19 |
| deerflow-native-deep-research-graph.md | CLS-009 | 2026-07-19 |
| deep-research-spec-gates-and-coverage.md | CLS-010 | 2026-07-19 |
| runtime-operator-logs-and-live-trace.md | CLS-041 | 2026-08-16 |
| soft-bundle-session-cli.md | CLS-045 | 2026-08-18 |
| low-scale-real-auto-runs.md | CLS-046 | 2026-08-18 |
| test-regression-speedup.md | CLS-053 | 2026-08-22 |
| doc-gate-docs-layer-and-fresh-agent-narrative.md | CLS-057 | 2026-08-31 |
| openspec-product-boundary-portability.md | CLS-054 | 2026-08-17 |

---

## 卡片模板

新建 plan 文件 `<name>.md`（kebab-case slug 即标识）：

```markdown
# Plan: <标题>

> 类型: 设计 / 分析 / 复盘（postmortem） | 更新: 2026-MM-DD

## 背景 / 现状
触发这份 plan 的问题、当前状态、约束。

## 决策 / 方案
关键技术选择与理由（为什么 X 不是 Y），含考虑过的备选。

## 风险 / 取舍
已知限制、可能出问题的点。格式：[风险] → 缓解。

## 落地关联
计划如何变成 `openspec/changes/` 里的 change（或已被哪个 change 吸收）。
```
