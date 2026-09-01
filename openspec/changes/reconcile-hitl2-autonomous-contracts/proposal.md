## Why

现行 `hitl2-node` 契约与实现已经把 HITL2 定义为不产生人工 interrupt 的自主
continuation，但五份已批准 capability spec 仍把旧的 HITL2 路由菜单描述成用户
选择、第二次停点、再次 `resume` 或 rerun 后重新挂起。相互冲突的主规格会继续误导
proposal、TUI debugger 设计、测试 fixture 与验收，因此必须把失败尝试从当前权威面
摘除，而不只在 backlog 中标注为历史材料。

## What Changes

- 将当前人工输入边界收敛为 HITL1；HITL2 只投影为已验证的自主 graph phase，
  不产生 `PendingResearchInterrupt`、第二次 Answer、用户 route menu 或 re-suspend。
- 从 run experience、CLI、TUI 与 lifecycle wire 要求中移除现行 HITL2 prompt、choice、
  response 和 retained HITL2 session 的承诺；保留 typed pending-input adapter、关联校验、
  visible-control/no-local-inference 等仍适用于 HITL1 的约束。
- 将 rerun 规格中的 `hitl2_rerun_payload`、HITL2 route 与 generation 语义明确为内部
  graph/control facts；移除“用户在 HITL2 选择 rerun”与“新 generation 必须再次等待
  HITL2 用户决定”的旧验收场景。
- 保留现行 HITL2 route 集、fixture route coverage、readiness `repair_hitl2` 回边和 graph
  topology；这些是内部控制/测试表面，不是可广告的人机交互。
- 同步 requirement-registry 投影、run lifecycle walkthrough 以及伪造 HITL2 pending prompt
  的 presentation fixtures/tests，使 deterministic evidence 证明“只有 HITL1 待答，HITL2
  自主通过”。
- 这是 accepted-contract reconciliation，不改变 runtime、public API、checkpoint schema、
  topology 或已存在的 decoder。任何未来 HITL2 人工决策仍须由独立 change 定义真实语义
  subject、trusted producer、typed options、response binding、恢复和迁移。

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `research-graph-lifecycle`: 明确 HITL1 是当前唯一 pending human-input producer，删除
  HITL2 choice/response 的现行 wire 承诺，同时保留内部 HITL2 routes 和 topology。
- `research-run-experience`: 删除 HITL2 人工 prompt/choice 呈现与第二次 suspension 的测试
  要求，改为投影自主 HITL2 progress 且不产生 `AwaitingInput`。
- `rerun-node`: 将 rerun 输入和 generation 复验描述为 graph-owned control facts，删除
  用户 HITL2 rerun choice、cached human decision 与 re-suspend 语义。
- `research-demo-tui`: 只从正式 typed pending request 呈现 HITL1 输入，删除 retained
  HITL2 session/choice fixture 的产品含义，并继续禁止本地状态推断。
- `research-cli-onboarding`: 删除 HITL2 choice prompt 与第二次 resume 假设，保留 HITL1
  多轮输入及 shared `RunUpdate` 投影。

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/graph/nodes/hitl2/` 与其 `hitl2-node` capability 拥有当前 HITL2 predecessor validation 和 autonomous route；本 change 只修复相邻 accepted specs、reader projection 与测试证据，不改该 runtime owner。
- **Seam classification:** deterministic-guardrail 当前边界根据已接受的 Wave2 predecessor 确定性地产生 graph route，不接收人类 decision candidate；本次工作清除与该事实冲突的契约投影。
- **Question:** 如何让所有现行规格和参与者投影一致表达“只有 HITL1 可待答、HITL2 自主继续”，同时不删除仍有效的内部 HITL2 route topology、rerun control data 或 generic typed adapter？
- **Necessary adjacent/external contracts:** `research-graph-lifecycle` 回答唯一 pending-input producer 与内部 route/人类 option 的边界；`rerun-node` 回答 rerun source/payload 是否是 graph-owned control fact；`research-run-experience`、`research-demo-tui`、`research-cli-onboarding` 回答同一 typed lifecycle fact 如何投影且不产生第二 prompt；`domain/lifecycle.py` 的现存宽泛 decoder 只用于确认本 change 不暗中修改 persisted schema 或 API，不把 dormant acceptance 提升为当前 producer contract。
- **Evidence seam:** `tests/unit/test_hitl2_real.py::TestRealHitl2Factory::test_validated_state_routes_proceed_without_a_human_response` 和 malformed-state 场景证明 real HITL2 无 prompt；`tests/graph/test_research_graph.py::test_happy_path_completes_after_scope_with_autonomous_hitl2` 与 `tests/integration/test_demo_cli.py::test_interactive_demo_completes_after_scope_without_a_hitl2_choice` 证明 graph/participant 路径；HITL1 language-choice contract tests继续证明 generic typed option adapter。
- **Not in scope:** HITL2 runtime、route enum、topology、readiness repair、rerun compiler、checkpoint/schema migration、public lifecycle API、真实 retained bundle migration、新 debugger 实现或任何 `deerflow/` gitlink 变更/源码浏览。普通 downstream 工作既不修改也不 source-browse `deerflow/`。
- **Triggered review policies:** local-context, change-admission, authority-and-projections, human-interaction-integrity, participant-outcomes, workflow-outcome-review, control-placement

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| 当前 HITL2 是否等待用户 | 无；当前边界没有被批准的非可推断偏好或不可逆授权 | HITL2 validator/node 校验 Wave2 predecessor 并写合法 route | non-bypassable | 无 `PendingResearchInterrupt`、无 presentation-owned route | 删除第二套人工菜单/Answer 叙事，复用现行 graph route | real HITL2 unit test + autonomous graph completion |
| rerun 是否来自 HITL2 用户选择 | 无；现行 `rerun_source`/payload 是 graph/control fact | HITL2 route owner 与 rerun compiler | non-bypassable | generation、capacity、invalidation 仍由 rerun owner 判定 | 保留一个 compiler，不制造 human response authority | rerun compiler/unit tests + route-source tests |
| CLI/TUI 是否显示输入 | 用户只回答当前正式 typed HITL1 subject | Bundle-local pending interaction 及 `ResearchRunExperience` adapter | human-decision | stale/无 pending 时不得生成 Answer 或 `resume` | generic typed adapter 由 HITL1 language/text tests覆盖 | run-experience contract + CLI/TUI adapter tests |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| 合法 Wave2-pass 到达 HITL2 | HITL2 node 的 validated predecessor/route | 无人工 recovery；graph 按现行 route 继续 | 保持 graph-owned 非终态进展 | 继续到 readiness；不广告 Answer/Resume | autonomous HITL2 unit + graph completion tests |
| HITL2 predecessor malformed/unknown | HITL2 deterministic validator | 现行 graph failure owner；本 change 不新增 fallback | fail closed，不伪造 prompt | 仅现行 typed failure outcome允许的动作 | malformed-state unit tests |
| presentation fixture 构造伪 HITL2 pending | 当前 accepted lifecycle contract 拒绝其 production-shaped 含义 | 测试在 apply 时改用真实 HITL1 typed choice 或 autonomous trace | 不形成产品 lifecycle disposition | 不提交第二 Answer；继续依赖正式 typed pending fact | fixture audit + CLI/TUI/run-experience focused tests |

## Impact

- Apply/sync 将修改五份 main specs、既有 `REN-001`/`REN-006` registry 摘要、
  `deep_research_harness/docs/run-lifecycle-walkthrough.md` 和与伪 HITL2 pending
  presentation 直接相关的 tests/fixtures。
- 不新增 requirement ID，不修改应用 runtime、公开 API、依赖、graph topology、持久化
  schema 或 `deerflow/` gitlink。
- `_backlog/plans/_archive/` 继续只作 provenance；当前 debugger 计划只依赖同步后的 main
  specs、现行 typed contracts 与确定性证据。
