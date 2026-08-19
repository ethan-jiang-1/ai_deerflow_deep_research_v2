# fix-readiness-fallback-degraded-delivery

## Why

BUG-057（真实 003 run，bundle `b_hxxd16dhKAh…`，诊断引用 `diag_db4086f958d6e993672263ef`）：readiness critic
的单次模型调用越过 `per_call_output_cap` 被截停后，保守回退产物（全部 `blocked_repair_required`）在
wave2 未降级的 run 里路由 `repair_targeted`；而 targeted-evidence 循环在 `unresolved_gaps` 为空时是
确定性 no-op，于是 run 进入 `readiness → targeted_evidence(空转) → wave2 → hitl2 → readiness` 的无界
自旋，直到某次预算/结构性死亡写下 `blocked` terminal——全部真实研究产出（wave0/wave1/wave2）零交付。
这与 runbook-003 §5.1 的运营验收语义（"即便 readiness critic 调用失败也走降级交付"；blocked 只应来自
结构性失败或"降级后再次耗尽"）直接冲突：契约已写明，实现没跟上。readiness 是 BUG-044（wave2）/
BUG-050（wave2 节点预算）/BUG-055（final_delivery 排版）同一"诚实降级交付"家族中唯一没有等价降级通路的
阶段。

诊断过程（确定性探针 + journal 全量核验）同时暴露了观测缺口：非 gated 节点的路由决策、targeted-evidence
的空转 no-op、blocked terminal 的结构性归因都不落 Event Journal，检查器还把已发布诊断引用的 journal 误报
为"不可用"——修复本身需要这些事实作为验收证据，否则下次真实 run 仍要靠猜。

## What Changes

- **保守回退不再伪装成修复需求**：critic 执行失败（含预算截停）或候选不可采纳时的保守投影，从
  `blocked_repair_required` 改为 `ready_insufficient_judgment` + 固定 limitation note——观察失败是
  "无法判断"（披露为强制不确定项），不是"证据不足需要补证"。观察失败从此不路由 repair、不改变
  blocked 计数语义。
- **blocked 判定的空转防护**：admitted `blocked_repair_required` 判定仅在修复循环有申报工作
  （`unresolved_gaps` 非空）且 wave2 未降级时路由 `repair_targeted`；gapless run 中的 blocked 判定降级
  为披露的强制不确定项并继续交付（与 wave2/final_delivery 的降级语义对齐）。
- **pass 投放下 blocked 判定必须披露**：当 readiness 以 `pass` 路由（降级借用、gapless 防护、或保守
  回退）时，每个 blocked 判定都成为 report plan 的强制不确定项（含闭合 limitation 文案），不再从计划中
  消失。
- **readiness 访问决策事实入 journal**：每次 readiness visit 记一条闭合的路由决策事实（route、
  blocked_count、降级借用/防护标志、结构性失败码），遵循 run-event-journal 的闭合码契约。
- **targeted-evidence 空转事实入 journal**：0 gap intents 的 drained no-op visit 记一条闭合事实，循环
  空转从此可从 journal 直接断定。
- **blocked terminal 归因增强**：readiness 写 `exhausted` terminal 时，其结构性失败码进入 terminal
  incident/journal 事实（`research.blocked @ readiness` 不再是归因终点）。
- **journal 可用性行如实呈现（RER-009 合规修复）**：修复"terminal 已发布诊断引用时检查器仍报
  Bundle 内 Event Journal 不可用"的呈现/发布链（BUG-057 卡上登记的观察）。RER-009 已规定该语义，
  这是实现合规缺口而非 spec 缺口——本 change 补实现与单元 seam 回归测试，不改该 spec。
- **不改动**：结构性失败 → `exhausted`/`BLOCKED` 语义、wave2 降级借用分支（BUG-044）、hitl2/前置
  节点行为、图拓扑、hard rules 本身。

非目标：BUG-056（conformance 测试在 HEAD 上 route=exhausted）已由 94c8087 修复（根因：dd4c39d 为
BUG-054 给 readiness 增加结构性 store 读取后，测试 fake store 缺 `read_synthesis_gaps/findings` 方法，
AttributeError 被宽 except 吞成结构性失败；HEAD 已验证 31 测试全绿）。本 change 只归档其卡片并记录根因，
不做产品改动。critic 同 visit 重试（模型方差重跑）不在本次范围。

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/graph/nodes/readiness/` owns the deterministic admission, report-plan projection, and route selected from the bounded readiness critic result.
- **Seam classification:** deterministic-guardrail — the critic remains the existing bounded cognitive program, while this change corrects deterministic fallback projection, route admission, disclosure, and observation facts after cognition fails or is admitted.
- **Question:** How can readiness preserve honest degraded delivery when its critic cannot produce an admissible answer or requests repair for a run with no declared gap work, without allowing a model candidate or diagnostic projection to choose lifecycle control?
- **Necessary adjacent/external contracts:** `targeted-evidence-loop` answers whether declared gap work exists and records its zero-intent no-op; `run-event-journal` answers which closed route and attribution facts may be retained; `research-run-experience` answers whether an already-published Bundle-local diagnostic reference is presented as available. The public DeerFlow API is consumed unchanged, and ordinary downstream work neither modifies nor source-browses the `deerflow/` gitlink.
- **Evidence seam:** focused readiness materializer/node tests prove fallback and gapless routing; the scripted-real conformance scenario proves the bounded bridge-to-final-report handoff; targeted-evidence, Journal-store, and run-experience tests prove closed observation and presentation behavior; `UV_OFFLINE=1 make verify` remains the aggregate application gate.
- **Not in scope:** critic same-visit retries, prompt or capability changes, hard-rule semantics, graph topology, wave2 degradation ownership, human decisions, host-side tracing, DeerFlow internals, and product changes for BUG-056 beyond recording its already-landed conformance fix.
- **Triggered review policies:** local-context, change-admission, authority-and-projections, participant-outcomes, node-agent-workflow-integrity, control-and-recovery, workflow-outcome-review, control-placement

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Readiness evidence critic | node-agent | For each supplied must-answer question, is admitted evidence substantive, honestly insufficient, or repairably blocked? | Trusted readiness code supplies only approved questions and bounded ledger-derived evidence; no raw checkpoint or runtime authority | Zero-tool invocation through the existing Node Agent policy and runtime bridge | Typed per-question verdict candidate; readiness parser/evaluator admits it and the node owns route/materialization | Existing single bounded invocation; execution or admission failure projects closed insufficient-judgment limitations with no retry | Focused readiness critic/node tests and scripted-real cap-trip conformance |
| Gapless route and disclosure guard | no-agent | No new model role: the guard compares admitted blocked verdicts with gate-owned `unresolved_gaps` and degradation facts | Checkpointed control facts and admitted candidate only | No tools or model call | Readiness node owns the route; report-plan materializer owns mandatory uncertainties | Observation failure cannot demand repair; structural failures retain existing exhausted terminal behavior | Focused route/materializer tests cover gapless, declared-gap, fallback, and structural paths |

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Whether a readiness visit repairs, delivers, or exhausts | Critic proposes bounded per-question verdicts but cannot choose a route | Readiness node evaluates hard-rule failures, gate-owned gap/degradation facts, and admitted verdicts | non-bypassable | Structural failure still exhausts; repair is legal only with declared work and remaining wave2 capacity; every other non-terminal path delivers with disclosure | Reuse the existing route field and gate-owned control facts; avoid retry counters or a second controller | Readiness node tests and scripted-real cap-trip conformance |
| Which blocked or unverified judgments enter the report plan | Critic supplies bounded limitation notes; fallback supplies one closed note | Report-plan materializer deterministically projects conclusions and mandatory uncertainties | non-bypassable | A delivering route cannot silently drop a blocked or unverified must-answer judgment | Reuse the canonical immutable report plan; avoid node-side duplicate disclosure state | Materializer tests plus final report publication assertions |
| Readiness and targeted-evidence decision observations | No candidate or reader may authorize behavior from an observation | Node owners emit closed facts; RunObservationStore validates and retains them without lifecycle authority | advisory | Observation failure cannot change route, retry, terminal state, or Bundle selection | Reuse the existing node event channel and closed Journal schema | Node event-recorder tests and Journal serialization/redaction tests |
| Journal availability presentation for blocked readiness | No diagnostic consumer decides availability or recovery | Published Bundle-local observation facts and run-experience projection determine the truthful location line | advisory | Presentation cannot fabricate a reference, recover a Bundle, or alter terminal state; the existing typed outcome remains authority | Reuse RER-009 publication truth instead of incident-class inference | Run-experience blocked-readiness regression test |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Critic execution fails or candidate is inadmissible | Runtime bridge/admission boundary supplies a closed failure reason; readiness owns fallback projection | No same-visit retry; readiness performs one deterministic disclosed fallback | `pass` to final delivery when hard rules pass | Inspect the delivered report limitations or start a separately authorized run/refinement | Readiness unit tests and scripted-real cap-trip conformance |
| Admitted blocked verdict has no declared gap work | Readiness owns the comparison against gate-recorded `unresolved_gaps` | No repair visit because targeted evidence has zero legal work | `pass` with blocked verdicts as mandatory uncertainties | Inspect disclosed limitations; provide new direction only through existing legal lifecycle controls | Gapless and declared-gap readiness route tests |
| Structural readiness hard rule fails | Existing hard-rule evaluator and readiness terminal writer | No fallback or repair added by this change | Existing `BLOCKED` / `exhausted` terminal with closed structural attribution | Use the existing typed diagnostic/legal action; no automatic resume | Structural-failure readiness and Journal tests |
| Targeted-evidence receives zero gap intents | Targeted-evidence node owns the drained view and no-op fact | No worker dispatch and no retry | Existing `next` projection; readiness guard prevents this from becoming a repair spin | Continue the existing graph route | Empty-gap targeted-evidence test and Journal fact assertion |
| A published diagnostic reference is presented for blocked readiness | Observation publisher/store owns publication truth; run-experience owns presentation | No recovery behavior is added | Existing blocked result with truthful Bundle-local Journal availability | Inspect the referenced retained diagnostic while the Bundle exists | RER-009 run-experience regression test |

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `readiness-node`: REA-004 路由优先级修改（保守回退与 gapless blocked 不再路由 `repair_targeted`；
  pass 投向下 blocked 判定成为披露的强制不确定项）；REA-006 保守投影语义修改（观察失败投影为
  `ready_insufficient_judgment` 披露而非 `blocked_repair_required`）；新增 readiness visit 路由决策
  journal 事实要求。
- `targeted-evidence-loop`: 新增 drained no-op visit 的闭合 journal 事实要求。
- `run-event-journal`: 闭合事实集合扩展（readiness 路由决策事实、targeted-evidence no-op 事实、
  readiness 结构性失败码归因）。
- `research-run-experience`: 无 spec 变更——journal 可用性行的真实呈现已由 RER-009 规定，本 change
  只修复实现合规缺口并补回归测试。

## Impact

- `deep_research_harness/src/deerflow_deep_research/graph/nodes/readiness/`（critic.py 保守投影、
  node.py 路由与事实、materializer.py pass 投影下的 blocked→uncertainty）
- `deep_research_harness/src/deerflow_deep_research/graph/nodes/targeted_evidence/node.py`（no-op 事实）
- `deep_research_harness/src/deerflow_deep_research/runtime/run_experience.py`（journal 可用性呈现链）
- 事件记录契约（`run_observation`/journal 事件字段）与对应测试
- 测试：`tests/unit/test_readiness_real.py`（回退/路由语义改写）、`tests/unit/test_targeted_evidence*.py`、
  journal 契约测试、scripted-real conformance 新增降级场景（真实桥 + cap 截停 → 降级交付 PASS）
- `_backlog/bugs/`：BUG-056/057 卡片归档与根因记录
