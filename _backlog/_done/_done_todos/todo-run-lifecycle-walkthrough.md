# TODO: run-lifecycle-walkthrough

> 状态: 待设计 | 优先级: 中 | 更新: 2026-08-31
> 上游: [`../plans/doc-gate-docs-layer-and-fresh-agent-narrative.md`](../plans/doc-gate-docs-layer-and-fresh-agent-narrative.md)（缺口 B）| 下游: 无

## Why

`CONTEXT.md` 约 60 个术语做到「一词一 owner」，但都是**定义态**：fresh agent 要建立
生命周期心智模型（`Run Refinement` vs `Refinement Continuation` vs `Correlated Research
Response` vs `Accepted Profile Note`），只能反复回读定义互相比较。缺的是一条**时间线
叙事**——借鉴源 FAQ 语料自己的范式是 *follow-a-fresh-agent*：跟随一个参与者走完第一个任务。

## 现状对齐

- CLS-056 体检已判「术语 owner = CONTEXT.md ✅」，本 todo **不重写词汇表、不造新词**。
- 节点包已有 per-node `workflow.md` reader projection（局部视角）；本 todo 补的是**全局
  生命周期视角**（一个 bundle 的一生），两者互补不重叠。
- 路线事实已在 `docs/deep-research-topology.md`（生成的边表）与 `docs/runtime-architecture.md`
  （controls 语义）——walkthrough 只做投影，不复制事实。

## Current Direction

在 `deep_research_harness/docs/` 新建 `run-lifecycle-walkthrough.md`：

1. 主线是一个 bundle 的一生：`start` → HITL1（Research Confirmation）→ topic planning →
   wave0/wave1/wave2（+ targeted_evidence 回环）→ HITL2 → readiness → final_delivery →
   终态；然后演示 `refine`（文本方向进入 pending）与 textless `refine` continuation 的差别，
   以及 `Bundle Loss` 时各界面如何表现。
2. 每个 `CONTEXT.md` 术语在**它登场的那一步**首次加粗并链接 CONTEXT.md 锚点——叙事在走，
   定义不搬家。
3. 文件头声明 reader projection / 非权威（沿用节点 `workflow.md` 的措辞纪律）。
4. `deep_research_harness/AGENTS.md` Information Map 挂一行：「生命周期怎么走 → 此文」。

## Design Questions

- 篇幅预算：一篇 walkthrough 控制在多少行以内合适（建议先给个上限并写入文件头，防膨胀成第二文档层）？
- 是否用一个真实 demo 跑法（如 001/002 ladder）作为叙事骨架，让读者可以边跑边读？（倾向是，但需与 `_backlog/_local_demo/` 的阶梯语义对齐。）
- HITL2 `rerun` 分支要不要入主线？（倾向：一笔带过 + 链接 `rerun` 节点 workflow.md，不展开。）

## Non-Goals

- 不改 `CONTEXT.md` 任何定义；不发明新术语。
- 不复制 runtime-architecture / topology 的事实（只 link）。
- 不 link OpenSpec 内容（path-free，PRS-009）。
- 不给 walkthrough 造机器门禁（本 todo 就是 prose 纪律，如实承认靠 review）。

## Next Step

按 Current Direction 起草 `run-lifecycle-walkthrough.md`，先跑一遍
`make soft-bundle … --mode 001`（或 002）对齐叙事与真实输出，再挂 Information Map 链接。
