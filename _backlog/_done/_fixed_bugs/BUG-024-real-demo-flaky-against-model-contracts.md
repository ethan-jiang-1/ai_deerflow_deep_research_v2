# BUG-024: real demo (`make demo-real-scripted`) flakily fails at different nodes; model attribution is unresolved

> 严重级别: P1 | 发现: 2026-08-10 | 状态: 已修复，已归档

## 症状

`make demo-real-scripted`（默认问题）连续三次真实 run，每次都挂在**不同节点、不同失败类别**。历史诊断没有保留 selected model，因此下表不把这些 run 归因给 flash 或任何其他模型：

| Run | 失败点 | 失败类别 | 现象 |
| --- | --- | --- | --- |
| 1（修复前） | wave1 | `agent_invocation` | 模型单次响应并发请求多个 web 工具，超 `tool_call_limit=1`，被拒 3 次 → `gate_blocked`；该工具窗口缺陷现已修复。 |
| 2（修复后） | topic_planning | `budget.exhausted` | 零工具节点耗尽了某项闭合预算；旧诊断未保留具体 subreason。 |
| 3（修复后） | wave0 | `structured_output` | 1/3 topic 三次尝试全败；旧终态未保留具体 parser/validator rule。 |

诊断引用: `diag_49S1w5uxd8C_1bcU_Fu5ZPgX`（wave1）、`diag_4dfKqbo-2X8Y3F_jgw8Q5Bjt`（topic_planning）、`diag_YIGwIwtleMN6mnybBiwJqDwb`（wave0）。指纹分别为 `754e1a58…`（wave1）、`26c9dcf2…`（topic_planning）。

## 受控校准结果（2026-08-10，诊断 change 之后）

`calibrate-real-demo-model-contracts` 已将显式 profile、闭合 budget subreason 和
canonical validation code 写入 Bundle-local Journal。随后以同一固定 scripted 问题运行了
四个独立 Bundle；未读取或保留模型原始输出、prompt、异常文本或 provider body。

| Profile | Bundle | 终态 | 可归因事实 |
| --- | --- | --- | --- |
| `deepseek-v4-pro` | `b_PPyIVKWK9L4qQFzNMNt7tJ9uOiOwbQbFV_rDAYk64Dk` | `blocked@topic_planning` | `budget.exhausted`，`budget_stop_reason=per_call_output_cap` |
| `deepseek-v4-flash` | `b_oM9xWQawuKU2YZHvlE6wMC472RWxUOqBWMt_AGF-9zM` | `blocked@topic_planning` | `budget.exhausted`，`budget_stop_reason=per_call_output_cap` |
| `deepseek-v4-flash` | `b_UtD8E6jYOc83h31f5D9rZImykt6xuTSzcbgrI98nNeg` | `blocked@topic_planning` | `budget.exhausted`，`budget_stop_reason=per_call_output_cap` |
| `deepseek-v4-pro` | `b_S849xv_SzRf-GHAyzbij5Rv3s9uNbjYa4K4J-1C44bs` | `blocked@wave1` | 两个 Wave1 work item 的 `a00`--`a02` 都记录 `wave1_worker_output_json_invalid`，最终为 `structured_output` |

### Topic-planning envelope calibration (2026-08-10)

| Profile / revision | Bundle | Topic-planning phase | Terminal category | Budget-stop reason | Validation codes |
| --- | --- | --- | --- | --- | --- |
| `deepseek-v4-pro` / `v1` | `b_yl-J4DR0lQDM36qdKrX1RiRbw29TpRA8P21nEBjaBB8` | initial validation succeeded; advanced to Wave0 then Wave1 | `blocked@wave1`, `research.blocked`, worker `structured_output` | none at topic planning | topic planning: `[]`; Wave1: `wave1_worker_output_json_invalid`, `wave1_worker_output_invalid` |
| `deepseek-v4-flash` / `v1` | `b_DNtPmLPzHEqBQGc4GpHhRcUiB_jqRmHu4tEztEeEqzc` | initial validation succeeded; advanced to Wave0 then Wave1 | `blocked@wave1`, `research.blocked` | none at topic planning | topic planning: `[]`; observed Wave0/Wave1 validation facts: `[]` |

### 已确诊：topic-planning 的输出 envelope 与单次 cap 不相容

前 3 个独立 Bundle、2 个显式 profile 都在同一零工具 planning invocation 以
`per_call_output_cap` 终止。因此这不是 profile 选择、provider 瞬时异常或旧 Wave1
工具窗口的问题。直接 deterministic owner 是
`runtime/research.py::_topic_planning_node_agent_policy()` 的 `2048` output-token cap；
但 TopicPlan 允许最多 8 个含 scope、bindings、dimensions 和 exclusions 的 topic，且当前
planner cognitive program 只要求遵守 schema/bounds，没有规定一个与该 cap 相容的紧凑输出
envelope。

下一 change 应只解决这一已证实的 blocker：定义紧凑 TopicPlan 输出 envelope，并把该节点的
per-call output cap 校准到与合法 envelope 相容的有界值；保持一次 invocation、零工具、总
token、wall-time、repair、route 和 terminal authority 不变。先以 focused deterministic
evidence 锁定此契约，再以同一 Bundle Journal loop 验证两个 explicit profile 都能越过
topic planning。

### 已确诊：Wave1 structured output（后续复查前的初始证据）

第二个 `deepseek-v4-pro` Bundle 成功越过 topic planning 后，Wave1 两个 work item 在各自三轮
有界 attempt 中均产生 `wave1_worker_output_json_invalid` 并最终 `structured_output`。这是一条
真实且已经有 canonical code 的独立故障线，但目前只有一个 Bundle。不得以 topic-planning
cap 修改顺手放宽 Wave1 的 schema、retry、tool window、budget 或默认 profile。待上游 blocker
解除后，以同一显式 profile 和 Journal 重新复现、最小化并单独提出 change。

## 当前诊断

已确认的是：真实 demo 在不同节点有重复的失败终态，且 Wave1 的 eager-parallel-tool 根因已修。尚未确认的是：剩余失败是否来自某个模型、某项预算、某条结构化输出规则，或这些因素的组合。不能据此直接选择默认模型或放宽节点契约。

具体到 Wave1：请求 `tool_call_limit=1`（spec 要求「exactly one web search call」），旧 middleware 会拒绝单次响应中的 2+ 工具调用。`tool-window-truncates-eager-parallel-calls` 已把窗口改为执行上限，超额调用只截断、不再使 run 失败。

## 复现

```bash
cd deep_research_harness && DEERFLOW_DEMO_MODEL=<profile> make demo-real-scripted
```
无 `--question`，用默认问题。当前 demo 要求一个显式支持的 profile；每次 full run 约 4 分钟，适合确认整体症状，但不是模型特定根因的紧反馈回路。

## 修复关联

- 已归档: `openspec/changes/archive/2026-08-10-tool-window-truncates-eager-parallel-calls/` —— 修 wave1 工具窗口（模型超额调用 → 截断而非 fail run）。
- 未解决（本 bug 的范围）: Wave0/Wave1 的工具后结构化输出，以及它们与 selected model/profile 的差异。topic-planning `budget.exhausted` 已由归档的 `align-topic-planning-output-envelope` change 修复；下一步不是在“换模型”和“放宽预算”之间二选一，而是针对真实候选输出的认知 envelope 做受控验证。

## 研究补充（2026-08-10，本地一手证据）

### 结论

这是一个已确认的真实 demo 跨节点失败问题，但目前**不能**严谨地归因为
“`deepseek-v4-flash` 与所有紧契约不匹配”，也不足以支持直接换默认模型或
放大预算。应先修复一次运行的执行配置归因与失败粒度，再以受控模型矩阵决定
具体节点的配置或恢复策略。

### 已证实的事实

| 观察 | 一手证据 | 能证明什么 |
| --- | --- | --- |
| Wave1 | `deep_research_harness/.reports/deep-research-diagnostics/observations/825c0a2577f9c7f19784bdf24c0f5c4baa242fbe3aac2e9e6dc402e95431ba38/run-summary.json:1` | `research.blocked@wave1`，类别 `agent_invocation`，trace 有三次 Wave1。 |
| Topic planning | `deep_research_harness/.reports/deep-research-diagnostics/observations/1066234f9bbc3e3009f4762096b769c1a9fa9f6e6661b6f50faeabf4ca379685/run-summary.json:1` | `budget.exhausted@topic_planning`。 |
| Wave0 | `deep_research_harness/.reports/deep-research-diagnostics/observations/750a36428bea2cd590addb46ee70e5b8f0331b3ab38ebf577fb82eb71dcac8c0/run-summary.json:1` | `research.blocked@wave0`，trace 有三次 Wave0；旧终态没有保存具体 worker 类别。 |

- 汇总 journal 在 `deep_research_harness/.reports/deep-research-diagnostics/records.jsonl:99` 与 `deep_research_harness/.reports/deep-research-diagnostics/records.jsonl:146-167` 中出现相同 Wave1 指纹 8 次、相同 topic-planning 指纹 4 次；这不是只发生过一次的偶发 terminal。
- Wave1 的并发工具窗口已由提交 `bcc7bf8` 修复：现在保留能放进窗口的前 N 个调用而不使 run 失败，锁定测试在 `deep_research_harness/tests/unit/test_tool_policy.py:138-154`；归档任务也明确修后两次 real run 分别止于 topic planning 和 Wave0，而非把全链路宣称为稳定（`openspec/changes/archive/2026-08-10-tool-window-truncates-eager-parallel-calls/tasks.md:37-45`）。它是已修的独立根因，不应再混入剩余问题。
- 各节点并非同一套“小预算”：topic planning 的确是零工具、每次 invocation 一次模型调用、`2048` output cap / `8192` total / `60s`（`deep_research_harness/src/deerflow_deep_research/runtime/research.py:274-295`）；Wave0/Wave1 的外层 policy 则是 `50` calls、`64000` output cap、`900s`（`deep_research_harness/src/deerflow_deep_research/runtime/research.py:418-485`），请求窗口另行限制 Wave0 为 3、Wave1 为 1（`deep_research_harness/src/deerflow_deep_research/graph/nodes/wave0/prompts.py:86-126`；`deep_research_harness/src/deerflow_deep_research/graph/nodes/wave1/prompts.py:85-118`）。

### 历史记录中曾是推测的部分（校准前）

- 早期 `make demo-real-scripted` 自己不设置 `DEERFLOW_DEMO_MODEL`（`deep_research_harness/Makefile:62-69`）。当时未设 selector 会收集有凭据的模型配置并由 bridge 取 `models[0]`，因此三条历史诊断没有足够证据证明实际模型。现在 `_demo_core.py` 已拒绝缺少或不唯一的 selector；新的 Bundle 一律保留显式 profile/revision。
- 旧的 `budget.exhausted` 记录仍不能反推是 output cap、wall time、token admission、总 token、模型调用或并行工具上限中的哪一个。校准后的 Bundle 已保留闭合 budget subreason；Wave0 的旧记录仍不能证明是 `sources`、`baseline_facts` 或 `limitations` 中的哪项不合规。
- 当前 credentialed canary 的 DeepSeek 配置固定为 `deepseek-v4-pro`（`deep_research_harness/tests/scenarios/canaries.py:83-91`），所以已有 live lane 不能验证实际 demo 所选的 flash 或未指定模型。

### 当前 Event Journal 的诊断粒度

新 Journal 已比旧 terminal 强：`RunEvent` 能保存 `generation`、work/attempt correlation、validation stage 和 canonical validation codes（`deep_research_harness/src/deerflow_deep_research/domain/run_observation.py:116-160`）；Wave1 明确把初始与 repair 的 canonical code 写入 Journal（`deep_research_harness/src/deerflow_deep_research/graph/nodes/wave1/subgraph.py:76-105,175-239`），共享 work-unit 层也记录 submission validation codes（`deep_research_harness/src/deerflow_deep_research/graph/components/work_units.py:617-641`）。

校准 change 已补上 selected profile、budget subreason，以及 Wave0/Wave1 的初始/repair parser code。剩余缺口是 parser 通过后的 Wave0 post-candidate validation code，及不暴露原文的最终 response shape；它们在本次 flash/pro 复查中变成了实际阻碍，而非历史推测。

### 建议的下一步与 Change 边界

可以提出一个**先收集正确证据、暂不放宽行为契约**的 OpenSpec change：

1. 让 real-demo 选择恰好一个显式、可测试的 model profile；把安全的 selected-model/profile revision 写入 Bundle-local Journal 的 admission/summary，而非依赖环境顺序或外部日志。
2. 为 `budget.exhausted` 增加闭合、脱敏的 subreason，并把 Wave0 与 topic-planning 的已知 parser/materialization 违例规范化为 canonical validation codes；不保存 prompt、响应、异常文本或 provider body。
3. 让受控 live canary 复用同一个显式 profile，先逐节点跑 topic planning、单-topic Wave0、单-topic Wave1，再对每个候选模型以固定问题运行多个独立 Bundle。结果只据 Journal 的 model/profile、阶段、闭合类别和 canonical codes 决定后续是选默认模型、调某一节点预算，还是改善该节点 repair。

这也是最低成本的证据循环：先用确定性测试锁定 selector、Journal payload 与归因，再做有限的真实调用；不要在没有模型身份和失败子原因的情况下进行全链路 trial-and-error。另有一个独立规格清理项：`openspec/specs/node-agent-runtime/spec.md:22-38` 仍写“超窗口即拒绝”，但同一文件 `:54-75` 与现有 middleware 都是“截断超额调用”，应单独统一，不应当作 Wave1 回归。

## 复查（2026-08-10，topic-planning 修复后）

### 当前结论

BUG-024 **仍然存在**，但已经不再是 topic-planning budget blocker：两个显式
profile 都通过 topic planning，随后在证据 worker 的结构化候选边界出现不同终态。
不能通过换默认模型、增加 Wave0/Wave1 budget、放宽 parser/schema、或撤销工具窗口截断来
解决它。直接因果 owner 是 Wave0/Wave1 initial 与 repair cognitive program 的
model-visible output envelope；它没有可靠地把一次检索后的最终模型回答收束为现有的
严格 JSON candidate。

### 新的 Bundle 证据

所有以下检查只读取 Bundle-local Journal 的安全投影；没有读取或保存模型正文、prompt、
工具结果、异常文本或 provider body。

| Profile / revision | Fresh Bundle | Result | Safe Journal facts |
| --- | --- | --- | --- |
| `deepseek-v4-pro` / `v1` | `b_xZRfvHtFAOxUkeMBSeW0eb9Q04wacTUa7ZC8pFDwWUk` | `blocked@wave1` | Topic planning completed. Wave0 initial responses sometimes emitted `wave0_worker_output_json_invalid`, but its bounded repairs recovered. One Wave1 work item emitted `wave1_worker_output_json_invalid` on `a00`--`a02`; the final repair emitted `wave1_worker_output_invalid`; the existing controller then exhausted. |
| `deepseek-v4-flash` / `v1` | `b_RP3lS3ygD4NQwQXIX89Z6e-jo4X-vu-YapfHkU8_bCg` | `blocked@wave0` | Topic planning completed. One Wave0 work item emitted `wave0_worker_output_json_invalid` on `a00` and `a01`; `a02` had no parser code but still failed before submission, so the exact post-parser rule is not yet present in the Journal. |

The pro Bundle independently repeats the former Wave1 pattern after the topic-planning
change. The flash Bundle reaches a different phase, so it does **not** prove that the
profiles are equivalent; it does prove that neither explicit profile currently makes the
whole real demo reliable.

### Minimal causal reproduction

A temporary one-worker invocation used the production Wave1 bridge, the production
normal evidence-intake request, a real web tool, and a freshly created selected Bundle.
It completed without a provider or budget error. Its redacted in-memory response-shape
projection recorded two requested `web_search` calls in the first model response (the
existing window correctly executed only one), followed by a 247-character final
`prose` response with no JSON keys. The Wave1 parser therefore rejected the final
candidate as `wave1_worker_output_json_invalid`.

This removes the graph, topic planning, Wave0 ledger, terminal routing, and raw tool
result content from the minimal cause. It also confirms that the old eager-parallel
tool-window defect is not the active failure: truncation behaved as designed, but the
model still did not provide the required JSON after the retained retrieval.

### Evidence gaps discovered during the review

- `tests/scenarios/evidence_intake_live.py` constructs a direct Wave0/Wave1
  calibration without a `SelectedBundleContext`. The real bridge correctly stops it
  at `selected_bundle_context_missing` before a provider call. Its current
  `requires_llm` test is therefore not a live output-contract signal and cannot be
  used as BUG-024's regression loop until the calibration binds a real selected Bundle.
- Wave0 now records initial and repair parser codes, but a later work failure after a
  parser-accepted `a02` has no safe canonical post-candidate validation code in the
  Bundle Journal. The flash terminal is consequently classified but not yet explained.
- The current `59` focused deterministic Wave0/Wave1 tests pass. They validate the
  parser, repair routing, provenance and controller boundaries, but their scripted
  candidate seams cannot detect a real model returning prose after a valid tool turn.

### Next Change Boundary

The next OpenSpec change should own the Wave0/Wave1 evidence-worker output program,
with the Wave1 initial/repair capability and prompt builders as the primary causal
seam. It should:

1. Define compact, model-visible initial **and repair** JSON envelopes for Wave0 and
   Wave1 that state the required tool-then-final sequence, exact allowed keys,
   minimum candidate shape, and a final no-prose/no-fence self-check.
2. Preserve all deterministic authority: existing schemas and semantic validators,
   source/newness/provenance floors, tool windows, one-shot repair, work-unit retry,
   budgets, ledger, gate, route, and selected-model policy remain unchanged.
3. Repair the direct evidence-intake live calibration by creating and threading a
   real `SelectedBundleContext`, then make it assert the production parser/semantic
   verdict for a single Wave0 or Wave1 worker under each explicit profile.
4. Extend Bundle-local validation evidence only where needed: retain a closed,
   redacted final-response shape (`empty`, `prose`, `fenced`, `embedded_json`, or
   `json_object`) and canonical post-candidate validation codes. Do not retain any
   raw response, prompt, tool result, exception text, or provider body.

The change should first prove the compact envelope deterministically, then run the
repaired one-worker live loop and a small explicit-profile Bundle matrix. A full
real demo must advance through both Wave0 and Wave1 before it can be called stable.

## 关闭证据（2026-08-11）

`stabilize-evidence-worker-output-envelopes` 已作为 OpenSpec change 归档，并由提交
`17d0975` 实施。它在不放宽 parser、local semantic validation、source/newness floors、
tool window、预算、repair/controller bound、ledger、gate、route 或 lifecycle 的前提下，
为 Wave0/Wave1 initial 与 repair 程序补齐了模型可见的闭合 JSON completion envelope。
同时，Bundle-local Journal 现在能以脱敏的 closed response shape 与
`post_candidate` canonical code 区分这些失败，而不保留原始模型输出。

确定性回归已在 `UV_OFFLINE=1 make verify` 中通过。归档任务还完成了所有可用显式
profile 的初始 worker 定点校准，并运行一条新的真实
`DEERFLOW_DEMO_MODEL=<profile> make demo-real-scripted` Bundle，确认它穿过 Wave0 和
Wave1；这正覆盖了本 bug 最后的阻断范围。该结论不宣称后续阶段、最终交付质量或外部依赖
永远不会失败。
