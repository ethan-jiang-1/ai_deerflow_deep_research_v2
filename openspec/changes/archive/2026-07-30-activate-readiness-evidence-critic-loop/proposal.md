## Why

Readiness currently converts every must-answer question into `ready_substantive` through
a deterministic fallback, even when the accepted evidence cannot support an answer.
The approved readiness activation dossier admits a bounded, read-only evidence critic
whose candidate remains subject to the existing hard-rule, materialization, and route
owners.

## What Changes

- Replace the real readiness critic's unconditional fallback with one bounded Node Agent
  invocation that evaluates answerability for each checkpointed must-answer question.
- Add a readiness-local capability/prompt and a closed structured candidate contract;
  the critic receives only the approved question/evidence boundary and has no tools,
  writes, checkpoint access, route authority, or evidence-admission authority.
- Deterministically validate and normalize the candidate before report-plan
  materialization. Verdict questions and backing references must be drawn from the
  supplied projection; the checkpoint retains only the bounded admitted projection.
  Invalid, incomplete, duplicate, out-of-scope, or execution-failure output becomes
  conservative `blocked_repair_required` candidates and follows the existing
  `repair_targeted` route rather than silently returning the all-ready fallback.
- Declare the existing `WORK_UNIT_CONTROLLER` capability for readiness so the graph
  injects the ledger reader it needs, and register a dedicated readiness zero-tool
  bridge/policy in the existing per-node runtime resolver.
- Add deterministic scripted-loop evidence and a bounded, separately classified
  answerability evaluation. Live model quality remains supplemental and is never
  claimed by fixture or scripted proof.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `readiness-node`: Replace the all-ready fallback with a bounded read-only critic
  candidate, deterministic admission, conservative failure projection, and unchanged
  node-owned route/materialization authority.
- `evaluation-hardening`: Require distinct deterministic workflow-conformance and
  bounded answerability-judgment evidence for the newly active readiness critic branch.

## Impact

- Primary code changes are limited to `agent/src/deerflow_deep_research/graph/nodes/readiness/`
  and the existing `runtime/research.py` per-node Node Agent bridge assembly. The
  change may add readiness-local capability resources and focused tests/evaluation
  assets under `agent/`.
- `backend/` and `frontend/` remain out of scope. No API, graph topology, state-schema,
  checkpoint ownership, evidence ledger, or public lifecycle contract is broadened.
- The real readiness recipe gains a model dependency and can conservatively request
  existing targeted repair when the critic cannot produce an admissible verdict;
  full-fake readiness remains fixture-controlled.

## Change Focus

- **Primary module / causal owner:** `agent/src/deerflow_deep_research/graph/nodes/readiness/`
  owns the semantic answerability question, candidate validation boundary, report-plan
  input, and node-owned route selection.
- **Question:** How can a bounded critic distinguish supported answers, stated
  insufficiency, and repair-required gaps from checkpointed questions and accepted
  evidence without becoming a source of evidence, checkpoint writer, or executable
  route authority?
- **Necessary adjacent/external contracts:** `domain/context.py` and the existing
  `NodeExecutionCapabilities` protocol define the typed request/result boundary;
  `domain/node_spec.py` and `graph/builder.py` answer how a declared
  `WORK_UNIT_CONTROLLER` is injected and rejected when absent; `runtime/research.py`
  answers how readiness receives its own trusted zero-tool policy rather than an
  upstream node's bridge; `runtime/node_agent_bridge.py` enforces config, budgets, and
  posture; `agents/phase_prompt.py` and `graph/prompt_catalog.py` enter only if they
  are the existing renderer/catalog integration seam; `evaluation-hardening`
  distinguishes workflow conformance from model-judgment evidence.
- **Evidence seam:** `agent/tests/unit/test_readiness_real.py` covers deterministic
  admission and route projection; a new readiness scripted Node Agent test exercises
  the real bridge/policy/request path; bounded evaluation assets assess answerability
  labels independently of deterministic conformance.
- **Not in scope:** web/search or other tools; evidence or ledger admission; state or
  checkpoint authority; new routes/topology; automatic retry beyond existing repair
  control; report drafting/publication; HITL2 interaction; backend/frontend/API work;
  unrestricted model output; or an assertion that offline fixtures establish live
  judgment quality.
- **Triggered charter policies:** change-admission, node-agent-workflow-integrity, workflow-outcome-review

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Real readiness critic | node-agent | For each supplied must-answer question, is the accepted evidence sufficient, insufficient with an honest limitation, or in need of targeted repair? | Trusted checkpointed questions and accepted submission/provenance references are read through the declared work-unit controller; rendered evidence summaries are untrusted presentation inputs; model output is untrusted. | A readiness-specific zero-tool, read-only, one-request `ExecutionPolicy`; `RuntimeNodeAgentBridge`, the per-node resolver, and capability posture enforce it. | Closed `ReadinessCriticOutput`; the readiness validator permits only supplied questions and accepted evidence refs, then hard rules, materializer, and node admit/project it. | Typed execution or validation failure projects conservative repair-required candidates once; existing targeted-evidence/routing bounds own subsequent recovery. | Readiness scripted bridge and real-node tests, plus invalid-output contract tests. |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Model unavailable, timeout, provider failure, or malformed candidate | Bridge result and readiness validator | Readiness projects one conservative repair-required candidate; existing targeted-evidence and gate budgets bound further work. | No new terminal; existing route may later reach its typed blocked disposition. | `repair_targeted` only; no all-ready fallback or direct publish. | Scripted bridge failure and real-node route tests. |
| Missing declared work-unit capability or readiness bridge binding | Graph wrapper/factory and runtime dependency resolver | Capability/binding admission fails before readiness invocation; no model call, candidate, or route is created. | Existing typed configuration failure; no new lifecycle projection. | Correct the runtime dependency configuration, then start a new invocation. | Factory and runtime resolver tests. |
| Accepted-evidence reader missing, unreadable, or integrity-invalid | Readiness hard-rule boundary and the ledger reader | Readiness records a redacted structural hard-rule failure before model invocation; it does not ask targeted evidence to repair a corrupted accepted ref. | Existing `BLOCKED` / `GATE_BLOCKED`. | `exhausted`; no model retry. | Store-read failure and hard-rule precedence tests. |
| Structural evidence/provenance failure | Existing readiness hard rules | Existing node terminal branch; critic result cannot override it. | Existing `BLOCKED` / `GATE_BLOCKED`. | `exhausted`; no model retry. | Existing hard-rule precedence tests. |
| Valid insufficiency judgment | Validated critic candidate and deterministic materializer | No critic-owned recovery; node uses existing route calculation. | No new terminal. | Report plan records uncertainty and follows existing `pass` unless a repair-required verdict exists. | Candidate/materializer/route tests. |
