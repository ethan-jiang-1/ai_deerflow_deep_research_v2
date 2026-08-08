# Progressive Plan: Node-local Reader Interfaces

> 状态: complete - Change 1 and Change 2 archived; six-node reader-interface capability established, 2026-07-29
>
> 最终方法以 [Wave2 v1 example](node-agent-control-flow-readability/wave2-synthesis-compact_v1/README.md) 为准。它是方法示例，
> 不是要求其他 node 复制 Wave2 的章节、问题或控制流。

## 决策

按既定决定，采用 **2 个 OpenSpec changes**。

```text
Change 1: Wave2 pilot
    |
    |-- reader-task gate: 只读 workflow.md 能否正确定位 owner/test？
    v
Change 2: five-node rollout
    |
    v
One established node-local reader-interface capability
```

现有 Wave1、Targeted Evidence 与 Wave2 的 conformance findings 仍由各自的行为 change 处理。
本计划的 `workflow.md` 如实说明已实现行为和限制，但不在文档 change 中修复、放宽或重写它们。

## 不变条件

两次 change 都必须满足：

- `workflow.md` 是 reader projection，不进入 runtime；代码、spec 和测试才是 authority。
- 一份 interface 只保留 node 的认知工作、deterministic authority、症状到 owner/test 的路径，
  以及容易导致错误修改的跨模块因果。
- 不复制 `node.py` 已清楚表达的局部逐行流程；不建立 `workflow_review.py`、JSON/Python
  semantics record、metadata、generated inventory、checker 或远端 documentation index。
- 不修改 `backend/`、`frontend/`、graph route、state schema、capability body、tool posture、
  prompt catalog 或测试行为。
- 不把 v1 的固定标题、表格行或 Wave2 repair case 当成所有 node 的 schema。

## Step 0: Change 前准备

这一步不创建 OpenSpec change，也不修改产品代码。

- [x] 0.1 为 Wave2 建 source worksheet：cognitive job、deterministic admission/route owner、
  最低责任测试，以及最多三条容易误改的跨模块事实。
- [x] 0.2 用当前 source、main spec 和测试核对 Wave2 worksheet；无法命名 owner 的条目不写进
  `workflow.md`，改记为 owning behavior change 的 open finding。
- [x] 0.3 固定 Wave2 pilot reader task：initial candidate 因
  `synthesis_findings_required` 失败，repair 又失败时，读者必须能判断 validation code 当前未
  传给 repair，并定位 `node.py::build_real`、
  `prompts.py::build_synthesis_repair_prompt` 与最低责任测试。

Step 0 的产物只是 change proposal 的 source notes；它不形成第二份长期 authority。

## Change 1: Wave2 Pilot

建议 change 名：`add-wave2-reader-interface`。

### Change Focus

| 项目 | 内容 |
| --- | --- |
| Primary module / causal owner | `agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/` 的 node-local reader projection。 |
| Question | 一份小型 `workflow.md` 能否让陌生 Coding Agent 正确区分 Wave2 的模型 candidate、deterministic admission、gate route 与 repair feedback？ |
| Necessary contracts | `wave2-synthesis-node` 说明 required behavior；`node-agent-capabilities` 说明 capability body/metadata authority；`research-graph-lifecycle` 仅用于确认 wrapper route 的事实。 |
| Evidence seam | Wave2 reader task，加上 workflow 所引用的 existing Wave2 real-node、gate、runtime-capability 和 bridge tests。 |
| Not in scope | 修复 validation-feedback delivery、改变 gate/route、增加自动文档检查、修改 package grammar 或生成 prompt 目录。 |
| Triggered charter policies | `authority-and-projections`。这是一份 explanation/projection；不改变 LLM role、tool posture、admission 或 recovery，因此不触发 `node-agent-workflow-integrity` 或 `workflow-outcome-review`。 |

### Checklist

- [x] 1.1 创建 `add-wave2-reader-interface` 的 OpenSpec proposal、design、spec delta 和 tasks，
  并填入上方 Change Focus。
- [x] 1.2 创建正式 package-local
  `agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/workflow.md`。
- [x] 1.3 以 v1 方法写 Wave2 interface：节点性质、症状到 exact owner/test、模型可见内容与
  capability metadata 的区别、repair feedback 的真实语义、route writer/consumer。
- [x] 1.4 为每条 reader-facing assertion 核对 source、main spec 与最低责任测试；已知 spec/code
  缺口只记录 implemented limitation，不让文档充当修复。
- [x] 1.5 运行 Wave2 reader task：仅提供该 `workflow.md` 和症状，确认陌生 Coding Agent 能指出
  首次修改点、不可先改的 surface 与 proof seam。
- [x] 1.6 运行文档引用的最低责任 tests、`openspec validate add-wave2-reader-interface --strict`、
  `python3 openspec/governance/check_project_architecture.py` 与 `git diff --check`。
- [x] 1.7 归档前运行 `cd agent && UV_OFFLINE=1 make verify`，记录原有失败或 skip，不把它们归因
  给文档 change。
- [x] 1.8 审阅并归档 Change 1；确认不新增文档 parser、Markdown schema、checker、
  `project-structure.toml` 或 `agent/AGENTS.md` 修改。

### 完成关口

- [x] Gate 1: reader-task 到达正确的 `file::symbol` 与测试，并明确 repair trigger 不等于 failure
  feedback 已送达模型。
- [x] Gate 2: 所有 source refs 在 review 时存在，且文档不声称拥有 runtime authority。
- [x] Gate 3: 1.6 与 1.7 的验证记录完整；changed surfaces 全部通过，6 个
  `test_adversarial_worker_path.py` failures 与 4 个 Gateway skips 已在 pre-change
  `7c4ccc1` worktree 复现并单独记录。

只有这个关口通过，才创建 Change 2。若失败，修订 Wave2 的小 interface；不通过添加 checker 或
恢复 v0 全景文档来掩盖定位问题。

## Change 2: Five-node Rollout

建议 change 名：`roll-out-node-reader-interfaces`。

### Change Focus

| 项目 | 内容 |
| --- | --- |
| Primary module / causal owner | Change 1 建立的 node-reader-interface documentation capability；实现分布在五个 node package 的 local `workflow.md`。 |
| Question | 已通过 Wave2 reader-task 的最小方法，能否按每个 node 的真实 seam 覆盖其余 LLM-bearing nodes，而不制造统一控制流 schema？ |
| Necessary contracts | 各 node 的 main spec、`node-agent-capabilities`、`node-prompt-catalog` 和仅在对应 node 需要时的 lifecycle/work-unit/gate contracts。 |
| Evidence seam | 每份 interface 的一个症状驱动 reader task，加上它引用的最低责任 deterministic test。 |
| Not in scope | 新的共享文档模块、checker/index、跨 node 统一 metadata、运行时行为修改，或将 no-agent controller 伪装成 LLM-bearing node。 |
| Triggered charter policies | `authority-and-projections`；与 Change 1 相同，不触发 runtime-role 或 outcome policies。 |

### Rollout Checklist

- [x] 2.1 创建 `roll-out-node-reader-interfaces` 的 OpenSpec proposal、design、spec delta 和 tasks，
  并填入上方 Change Focus。
- [x] 2.2 为 `hitl1` 完成 source worksheet、`graph/nodes/hitl1/workflow.md`、特有 reader task 与
  最低责任 test：human interrupt/response 与 model candidate 的 authority，及 profile brief / semantic
  intake 的分支差异。
- [x] 2.3 为 `topic_planning` 完成 source worksheet、`graph/nodes/topic_planning/workflow.md`、特有
  reader task 与最低责任 test：confirmed profile 到 plan candidate 的边界，以及 repair / blocked
  outcome owner。
- [x] 2.4 为 `wave0` 完成 source worksheet、`graph/nodes/wave0/workflow.md`、特有 reader task 与
  最低责任 test：受限检索工具、structured repair 与 work-unit/gate 的不同 recovery owner。
- [x] 2.5 为 `wave1` 完成 source worksheet、`graph/nodes/wave1/workflow.md`、特有 reader task 与
  最低责任 test：深度 evidence extraction、accepted-submission admission 与下一阶段 gate authority。
- [x] 2.6 为 `targeted_evidence` 完成 source worksheet、`graph/nodes/targeted_evidence/workflow.md`、
  特有 reader task 与最低责任 test：worker/controller/ledger 与 critic path 的不同 admission，及
  handler 写 `next` 但 builder 以 unconditional edge 返回 Wave2。
- [x] 2.7 逐一复核五份 interface：只写 node 特有且会改变维修决策的事实；不复制 Wave2 章节，
  没有清晰 owner 的 critic/recovery 事实标为 implemented limitation 或留给 owning behavior change。
- [x] 2.8 逐一确认 docs 未修改 runtime-rendered capability body，并运行每份文档引用的最低责任
  tests。
- [x] 2.9 运行 `openspec validate roll-out-node-reader-interfaces --strict`、
  `python3 openspec/governance/check_project_architecture.py`、`cd agent && UV_OFFLINE=1 make verify`
  与 `git diff --check`。
- [x] 2.10 审阅并归档 Change 2；确认没有新增共享文档模块、checker/index、跨 node metadata 或
  runtime behavior 修改。

Change 2 归档后，`node-agent-reader-interface` capability 成为唯一的实施规范；本目录的 v1
example 保持为设计解释，不变成运行时或第二份事实 authority。

## Completion Record

- Change 1 archived at `openspec/changes/archive/2026-07-29-add-wave2-reader-interface/`
  in commit `2771162`.
- Change 2 archived at
  `openspec/changes/archive/2026-07-29-roll-out-node-reader-interfaces/`; its delta
  was synced to `openspec/specs/node-agent-reader-interface/spec.md` in commit
  `f210493`.
- Both changes completed their cited deterministic checks and `UV_OFFLINE=1 make
  verify`; no shared documentation mechanism or runtime behavior was introduced.

## Stop Conditions

暂停 rollout 并回到 owning behavior change，而非在文档中猜测，出现下列任一情况：

- source、spec 与测试无法确定某条 feedback、route 或 failure 的 owner；
- reader task 需要修改 runtime behavior 才能给出诚实答案；
- 文档为了导航而必须改变 capability body、prompt catalog 或 graph wiring；
- Wave2 pilot 证明小 interface 无法将读者带到正确 owner，且缺失事实不能以一条局部导航补足。

这使 progressive rollout 始终只向前增加经过验证的 reader interface，而不把未解决的行为问题
藏进文档或放大为跨 node 的基础设施。
