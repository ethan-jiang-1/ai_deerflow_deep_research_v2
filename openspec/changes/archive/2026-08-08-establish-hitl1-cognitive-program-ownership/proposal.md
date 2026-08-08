## Why

HITL1 已经通过 production renderer 加载四条 package-local capability Markdown，但它们只是短 policy；
brief 和 semantic reply 的方法、分支与 repair 仍主要由 Python prompt builder 拼接。这使修改
认知 UX 仍像修改传统程序，也无法独立证明 runtime-visible Markdown 是行为的唯一认知 owner。

现在可以在不改变 Bundle lifecycle 或 profile admission 的前提下，把这个上游、零工具 cognitive
program 收敛为一条小 change，并为后续 node 提供可复用的准入样板。

## What Changes

- 将现有 HITL1 brief、brief repair、semantic intake、semantic intake repair capability Markdown
  扩展为 versioned、runtime-loaded 的完整认知方法，包含任务步骤、输入解释、分支、uncertainty、
  self-check、repair 与停止条件。
- 将 `prompts.py` 中可复用的认知方法和自然语言分支收缩为有界 assignment data、schema contract
  与 renderer invocation；Python 保留 typed parsing、candidate admission、human correlation、call
  ceiling、Bundle-local persistence、route 和 provider recovery。
- 为四条 production resources 建立 renderer/source-digest 与 method-ownership evidence，并新增
  `hitl1-cognitive-program-v1` corpus（不改写既有 `hitl1-brief-v1` smoke）。其确定性 handoff
  与 credentialed live-quality evidence 使用不同、写入后不可伪装的 evidence layer；未通过严格
  credential preflight 前不得产生 live layer，更不得表述为 release 结论。
- 保持现有 zero-tool posture、三个 semantic calls 上限、bounded repair、current proposal 的
  non-terminal fallback，以及 profile-to-topic-planning 的 canonical `profile_ref` consumer chain。

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/graph/nodes/hitl1/`; it owns the four HITL1 cognitive-program resource bindings and the deterministic graph handler that decides whether their candidates may matter.
- **Question:** How can the existing runtime-loaded HITL1 capability Markdown become the sole reusable method owner for brief and semantic-reply interpretation/repair while the node retains typed candidate admission, human correlation, bounded recovery, Bundle-local profile publication, and routing?
- **Necessary adjacent/external contracts:** `domain/profile.py` answers closed profile schema and publication facts; `domain/human_interaction.py` answers the closed semantic candidate and confirmation facts; `agents/phase_prompt.py` answers whether production rendering loads the exact resource; `runtime/node_agent_bridge.py` answers whether zero-tool posture, budget, cancellation, and safe failure are enforced; `domain/evaluation.py` and `runtime/evaluation/` answer immutable corpus-control identity and evidence-layer recording. None becomes a cognitive, lifecycle, or release owner.
- **Evidence seam:** Production renderer/resource tests for all four bindings; focused prompt tests that distinguish bounded assignment data from reusable method; scripted HITL1 node/integration transcripts proving parser/materializer admission and legal fallback; `hitl1-cognitive-program-v1` control assets plus immutable evaluation manifest/review records whose deterministic and credentialed-live layers are separately labeled.
- **Not in scope:** New `ResearchProfile` or `SemanticCandidate` fields; pending-response correlation; Bundle lifecycle or State writer changes; profile-to-topic-planning canonical projection; tool posture or call-ceiling changes; public controller; `wave0`, `wave1`, synthesis, targeted evidence, readiness, or final delivery; `backend/`, `frontend/`, or a UI route.
- **Triggered review policies:** human-interaction-integrity, node-agent-workflow-integrity, workflow-outcome-review, control-placement

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Brief-method interpretation | Node Agent proposes one `StructuredBrief` from the bounded original question. | `StructuredBrief` parser and HITL1 handler validate the candidate before any interaction state is written. | advisory | An invalid candidate may receive only the existing bounded repair; it never becomes profile authority. | Reuses existing capability ids and parser instead of creating a second prompt or admission path. | Exact production renderer test plus parser/brief failure transcript. |
| Proposal-reply interpretation | Node Agent proposes one closed `SemanticCandidate` from current proposal and reply. | `SemanticCandidate` parser and Research Confirmation/HITL1 handler admit only the current correlated proposal. | advisory | Ambiguity/question preserves the proposal; revision is visible but requires a later confirmation. | Removes duplicated natural-language decision instructions from Python without adding a controller. | Renderer, scripted semantic branch, and correlated confirmation tests. |
| User confirmation | Person selects an advertised confirmation or supplies a reply to the current subject. | HITL1 owns request correlation, visible control, candidate materialization, and profile publication. | human-decision | Stale/mixed/ambiguous input cannot publish a profile; the legal next action remains a fresh correlated request or bounded feedback. | Reuses the existing typed human-interaction contract rather than interpreting free text as an action id. | Existing and extended HITL1 interaction transcript tests. |
| Profile publication and route | No cognitive or human candidate decides persistence or route. | `domain/profile.py` and HITL1 materializer publish `profile.json`/State only after accepted research facts. | non-bypassable | No Markdown, candidate, evaluation record, or renderer may write State, publish content, or select `accepted`. | Keeps one Bundle-local profile authority and the existing downstream `profile_ref` consumer chain. | Parser/materializer integration test with write/reload and downstream consumer assertion. |

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Brief and brief repair | node-agent | What conservative, decision-ready profile candidate follows from this bounded research question, and how can one malformed candidate be repaired without invented requirements? | Original question and validation category are untrusted task data; method Markdown cannot receive State authority. | forbidden; capability loader and `RuntimeNodeAgentBridge` enforce zero tools. | `StructuredBrief`; parser and HITL1 handler. | HITL1 retains existing retry/failure route and one structural repair. | Renderer/source test and scripted invalid-brief transcript. |
| Semantic intake and semantic repair | node-agent | Which closed candidate intent best describes this reply to the displayed proposal, or should uncertainty remain clarification? | Original question, checkpointed proposal, human reply, and invalid draft are bounded data; correlation, route, and request id stay outside the prompt. | forbidden; capability loader and `RuntimeNodeAgentBridge` enforce zero tools. | `SemanticCandidate`; parser and Research Confirmation/HITL1 handler. | HITL1 retains the existing three-call shared ceiling, at most one repair, non-terminal feedback, and cancellation propagation. | Renderer/source test and scripted normal/ambiguity/adversarial/repair transcript. |
| Profile schema, acceptance, and publication | no-agent | Closed schema/correlation/persistence facts require deterministic validation and a Bundle-local writer. | Typed candidate and current Bundle State only. | No agent invocation. | `ResearchProfile`/accepted facts; domain parser and HITL1 materializer. | Existing typed failure/recovery behavior. | Profile parser and write/reload integration tests. |
| Graph route and lifecycle result | no-agent | Route and lifecycle are deterministic effects, not a language judgment. | Admitted confirmation outcome and Bundle-local State only. | No agent invocation. | Typed node update; HITL1 graph handler. | Existing typed fallback/terminal route only. | Mixed-graph route contract and HITL1 lifecycle tests. |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Capability resource missing, malformed, or mismatched | capability loader / runtime bridge safe failure | No method fallback or alternate prompt source; existing bridge/HITL1 safe failure path only. | Existing blocked/failure projection as applicable. | Follow the existing typed retry or inspect/restart action; do not infer a profile. | Resource-admission and bridge configuration tests. |
| Malformed brief or semantic candidate | Parser owns validation category. | HITL1 allows only its existing bounded repair; semantic intake shares its three-call ceiling. | Existing blocked brief route or non-terminal semantic feedback, respectively. | Reissue the current typed interaction where existing behavior permits it. | Scripted malformed-output and repair-exhaustion tests. |
| Retry-eligible provider failure | Runtime bridge owns safe provider observation. | HITL1 owns current bounded retry/backoff and records no model-derived lifecycle fact. | Existing exhaustion projection; semantic path preserves the proposal. | Existing fallback control or typed lifecycle recovery. | Scripted provider-failure transcript and call-count test. |
| Cancellation during invocation | Runtime bridge/node invocation owns cancellation propagation. | No repair/retry after cancellation. | Existing cancellation path. | Caller follows the typed cancelled result. | Cancellation propagation test. |

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `hitl1-node`: HITL1's runtime-loaded capability method becomes the canonical cognitive owner for its bounded brief and semantic-intake programs, with observable runtime-resource, candidate-admission, and evaluation behavior.

## Impact

- Affected code is confined to `deep_research_harness/` HITL1 capability resources, prompt construction, focused evaluation assets, the minimum evaluation manifest/review evidence-layer contract, and their lowest-responsible tests.
- The existing `agents` renderer, runtime bridge, and evaluation runner/reviewer are read as enforcement/evidence contracts and may receive only directly necessary compatibility edits; they do not gain cognitive, lifecycle, or release authority.
- No public API, Run Bundle lifecycle contract, external provider, upstream DeerFlow module, `backend/`, or `frontend/` behavior changes.
