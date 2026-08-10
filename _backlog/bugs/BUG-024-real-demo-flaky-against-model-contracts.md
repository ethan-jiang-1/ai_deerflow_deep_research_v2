# BUG-024: real demo (`make demo-real-scripted`) flakily fails at different nodes; model attribution is unresolved

> 严重级别: P1 | 发现: 2026-08-10 | 状态: 活跃

## 症状

`make demo-real-scripted`（默认问题）连续三次真实 run，每次都挂在**不同节点、不同失败类别**。历史诊断没有保留 selected model，因此下表不把这些 run 归因给 flash 或任何其他模型：

| Run | 失败点 | 失败类别 | 现象 |
| --- | --- | --- | --- |
| 1（修复前） | wave1 | `agent_invocation` | 模型单次响应并发请求多个 web 工具，超 `tool_call_limit=1`，被拒 3 次 → `gate_blocked`；该工具窗口缺陷现已修复。 |
| 2（修复后） | topic_planning | `budget.exhausted` | 零工具节点耗尽了某项闭合预算；旧诊断未保留具体 subreason。 |
| 3（修复后） | wave0 | `structured_output` | 1/3 topic 三次尝试全败；旧终态未保留具体 parser/validator rule。 |

诊断引用: `diag_49S1w5uxd8C_1bcU_Fu5ZPgX`（wave1）、`diag_4dfKqbo-2X8Y3F_jgw8Q5Bjt`（topic_planning）、`diag_YIGwIwtleMN6mnybBiwJqDwb`（wave0）。指纹分别为 `754e1a58…`（wave1）、`26c9dcf2…`（topic_planning）。

## 当前诊断

已确认的是：真实 demo 在不同节点有重复的失败终态，且 Wave1 的 eager-parallel-tool 根因已修。尚未确认的是：剩余失败是否来自某个模型、某项预算、某条结构化输出规则，或这些因素的组合。不能据此直接选择默认模型或放宽节点契约。

具体到 Wave1：请求 `tool_call_limit=1`（spec 要求「exactly one web search call」），旧 middleware 会拒绝单次响应中的 2+ 工具调用。`tool-window-truncates-eager-parallel-calls` 已把窗口改为执行上限，超额调用只截断、不再使 run 失败。

## 复现

```bash
cd deep_research_harness && make demo-real-scripted
```
无 `--question`，用默认问题。每次 run 约 4 分钟，适合确认整体症状，但不是模型特定根因的紧反馈回路；当前命令也没有显式选择模型。

## 修复关联

- 已归档: `openspec/changes/archive/2026-08-10-tool-window-truncates-eager-parallel-calls/` —— 修 wave1 工具窗口（模型超额调用 → 截断而非 fail run）。
- 未解决（本 bug 的范围）: topic_planning `budget.exhausted`、Wave0 `structured_output`，以及它们是否与 selected model/profile 有关。下一步不是在“换模型”和“放宽预算”之间二选一，而是先补齐证据归因；研究结论见下文。

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

### 原条目中仍是推测的部分

- `make demo-real-scripted` 自己不设置 `DEERFLOW_DEMO_MODEL`（`deep_research_harness/Makefile:62-69`）。未设 selector 时，demo 会收集所有有凭据的模型配置（`deep_research_harness/scripts/_demo_core.py:192-213`），registry 中 `deepseek-v4-pro` 排在 flash 前（`deep_research_harness/scripts/_demo_core.py:69-96`），bridge 再取 `models[0]`（`deep_research_harness/src/deerflow_deep_research/runtime/node_agent_bridge.py:116-129`）。只有 `deep_research_harness/run/real-research.sh:6-12` 显式默认 flash。因此三条历史诊断没有足够证据证明实际模型都是 flash；若仅有 DeepSeek 凭据且 selector 缺失，当前代码反而会首先选择 pro。
- `budget.exhausted` 不能反推是 output cap、wall time、token admission、总 token、模型调用或并行工具上限中的哪一个；它们在 middleware 中共享同一闭合类别（`deep_research_harness/src/deerflow_deep_research/agents/middleware.py:90-119`）。Wave0 的旧记录也不能证明是 `sources`、`baseline_facts` 或 `limitations` 中的哪项不合规。
- 当前 credentialed canary 的 DeepSeek 配置固定为 `deepseek-v4-pro`（`deep_research_harness/tests/scenarios/canaries.py:83-91`），所以已有 live lane 不能验证实际 demo 所选的 flash 或未指定模型。

### 当前 Event Journal 的诊断粒度

新 Journal 已比旧 terminal 强：`RunEvent` 能保存 `generation`、work/attempt correlation、validation stage 和 canonical validation codes（`deep_research_harness/src/deerflow_deep_research/domain/run_observation.py:116-160`）；Wave1 明确把初始与 repair 的 canonical code 写入 Journal（`deep_research_harness/src/deerflow_deep_research/graph/nodes/wave1/subgraph.py:76-105,175-239`），共享 work-unit 层也记录 submission validation codes（`deep_research_harness/src/deerflow_deep_research/graph/components/work_units.py:617-641`）。

但本 bug 的两个关键归因仍有缺口：`RunEvent`/`RunSummary` 没有 selected-model 或 budget-subreason 字段（`deep_research_harness/src/deerflow_deep_research/domain/run_observation.py:116-144,223-243`），bridge 只记录闭合 `failure_category` / `worker_failure_category`（`deep_research_harness/src/deerflow_deep_research/runtime/node_agent_bridge.py:594-648`）；Wave0 的 parser 初始/repair 失败目前直接收敛为 `structured_output`（`deep_research_harness/src/deerflow_deep_research/graph/nodes/wave0/subgraph.py:143-165`），没有在该分支写具体 canonical code。Topic-planning 的 parse/materialize repair 分支同样没有验证事件写入（`deep_research_harness/src/deerflow_deep_research/graph/nodes/topic_planning/node.py:263-306`）。

### 建议的下一步与 Change 边界

可以提出一个**先收集正确证据、暂不放宽行为契约**的 OpenSpec change：

1. 让 real-demo 选择恰好一个显式、可测试的 model profile；把安全的 selected-model/profile revision 写入 Bundle-local Journal 的 admission/summary，而非依赖环境顺序或外部日志。
2. 为 `budget.exhausted` 增加闭合、脱敏的 subreason，并把 Wave0 与 topic-planning 的已知 parser/materialization 违例规范化为 canonical validation codes；不保存 prompt、响应、异常文本或 provider body。
3. 让受控 live canary 复用同一个显式 profile，先逐节点跑 topic planning、单-topic Wave0、单-topic Wave1，再对每个候选模型以固定问题运行多个独立 Bundle。结果只据 Journal 的 model/profile、阶段、闭合类别和 canonical codes 决定后续是选默认模型、调某一节点预算，还是改善该节点 repair。

这也是最低成本的证据循环：先用确定性测试锁定 selector、Journal payload 与归因，再做有限的真实调用；不要在没有模型身份和失败子原因的情况下进行全链路 trial-and-error。另有一个独立规格清理项：`openspec/specs/node-agent-runtime/spec.md:22-38` 仍写“超窗口即拒绝”，但同一文件 `:54-75` 与现有 middleware 都是“截断超额调用”，应单独统一，不应当作 Wave1 回归。
