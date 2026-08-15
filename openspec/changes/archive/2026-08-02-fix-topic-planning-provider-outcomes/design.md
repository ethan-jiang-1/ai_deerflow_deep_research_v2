## Context

See [proposal.md](proposal.md) for the observed demo failures. The current
`RuntimeNodeAgentBridge` is the causal boundary for both failures: it turns every
`NodeAgentStop` into `tool.execution_failed`, and it decides whether a direct provider
exception can carry a safe `ProviderObservation` with a hard-coded `hitl1` node-name
check. `ExecutionPolicy` is already frozen and owns each phase's tool posture and
budget, but it has no provider-observation admission value.

Topic planning already has the intended recovery table. It retries exactly once only
when it receives `provider.timeout` or `provider.unavailable` with a safe observation;
the bridge currently prevents a real topic-planning `httpx.ReadTimeout` from reaching
that table. `NodeProblem`, terminal incidents, and `ResearchRunExperience` already
carry closed categories, but `RunFailureCode` and the shared safe-copy map do not yet
represent the three distinct node-agent stop outcomes.

## Goals / Non-Goals

**Goals:**

- Preserve the typed reason of an eligible node-agent stop through the bridge, direct
  phase terminal incident, and shared run presentation. When that incident has no
  diagnostic reference, retain the existing shared diagnostic-publication behavior,
  which derives an opaque reference only from typed terminal facts.
- Make safe configured-model-service observations an explicit, default-deny execution
  policy capability for both existing HITL1 and topic-planning zero-tool invocations.
- Restore topic planning's existing one-retry provider recovery through the actual
  bridge boundary while preserving cancellation and structured-output repair behavior.
- Establish deterministic, redacted evidence at bridge, node, lifecycle, and shared
  presentation seams.

**Non-Goals:**

- This does not change provider SDK retry policy, tool policy, graph topology, retry
  counts, provider vendors, checkpoint schema version, or any `backend/` or
  `frontend/` module.
- This does not grant provider recovery to another phase, add retries to the bridge,
  or treat provider observation as a route or state-write authority.
- This does not expose raw exception detail, provider content, credentials, paths,
  endpoint URLs, or model-object metadata.

## Decisions

### 1. Project trusted node-agent stops with a closed mapping table

The bridge will add three additive `RunFailureCode` values:

| `NodeFinishReason` from `NodeAgentStop` | Resulting `RunFailureCode` |
| --- | --- |
| `USAGE_UNAVAILABLE` | `provider.usage_unavailable` |
| `BUDGET_EXHAUSTED` | `budget.exhausted` |
| `POLICY_DENIED` | `policy.denied` |

The bridge will preserve the non-success `finish_reason` in `NodeExecutionResult` and
use the table only for the typed `NodeProblem`. An unsupported `NodeAgentStop` reason
will fail closed as `internal.unexpected`. Neither stop detail nor exception text will
be copied into `NodeProblem`, terminal state, diagnostic input, or presentation.
No `NodeAgentStop` will be a fallback to `tool.execution_failed`. Existing non-stop
tools-enabled mappings, including the required-tool-count validation, remain outside
this change.

Using the existing tool category was rejected because it changes the user's action and
corrupts diagnostic attribution. Folding all three outcomes into
`internal.unexpected` was rejected because it keeps the system safe but still loses the
known causal distinction needed for operations and future recovery decisions.

### 2. Make provider-observation admission a closed execution-policy value

`ExecutionPolicy` will gain a frozen, default-deny
`ProviderObservationAdmission(StrEnum)` value with
`DENIED = "denied"` and
`CONFIGURED_MODEL_SERVICE = "configured_model_service"` members. The policy field
will default to `DENIED`. Its `__post_init__` will reject a value that is not an
instance of that enum, including a raw string that happens to equal a member value.

Only `_hitl1_node_agent_policy()` and `_topic_planning_node_agent_policy()` will set
`CONFIGURED_MODEL_SERVICE`. The bridge's admission predicate will require both that
policy value and `request.tools_enabled is False`; it will not inspect
`context.node_name` or match a policy-name string. The existing model-binding
redaction, public exception-class boundary, status validation, timeout-origin handling,
and one-invocation limit remain unchanged. A denied policy, including another zero-tool
policy, and every tools-enabled request receive no configured-model-service observation
and no new retry eligibility.

A node-name allowlist was rejected because it duplicates policy capability outside the
immutable policy value and already caused the topic-planning omission. A loose boolean
without a closed semantic type was rejected because the admission is security- and
recovery-relevant; a named value leaves a reviewable path for a future approved class
without silently broadening the meaning of `true`.

### 3. Keep classification, recovery, and lifecycle authority separate

The bridge will classify one invocation and return `NodeExecutionResult` plus an
optional bounded observation. It will never sleep, retry, write graph state, or create
a terminal incident. Topic planning will continue to own its exact recovery table:

1. Initial eligible transient provider result: record attempt/retry, wait the existing
   bounded backoff, and invoke the identical initial planner request once.
2. Second eligible transient provider result: record exhaustion and retain the existing
   `exhausted` projection.
3. Second non-provider result: retain the exact final category with the existing
   `retry_followed_by_terminal_failure` projection.
4. Successful but invalid planner output: use the separate one-shot structured-output
   repair path; it never triggers a provider retry.

The new stop categories do not include a provider observation and therefore do not
enter this table. Cancellation continues to escape both bridge invocation and the
backoff without a later retry record or terminal incident.

Moving the retry into the bridge was rejected because the bridge has no graph-state or
terminal-incident authority and would create a second retry owner. Treating all
non-success results as retryable was rejected because it would turn usage, budget, and
policy controls into unsafe provider recovery.

### 4. Preserve the closed category through terminal projection and safe copy

The direct topic-planning outcome seam will retain the bridge-supplied `NodeProblem`
code, phase, certainty, optional observation, and any supplied safe diagnostic
reference when it writes `TerminalIncidentProjection`. It will not derive a provider
diagnostic reference for a stop that has neither a provider observation nor recovery.
For a blocked terminal incident with no reference, the existing
`ResearchRunExperience` pre-publication seam will derive a generic opaque reference
only from typed terminal facts. It will not hash or display stop detail.
`ResearchRunExperience` will add category-specific `_FAILURE_COPY` entries for the
three new closed codes and project them verbatim into `RunFailure` rather than infer a
tool failure or generic blocked state. These categories carry no provider recovery
facts when they are an initial stop, and no resume action. When one follows a genuine
initial provider recovery, the existing recovery projection remains historical context
for the final closed category; it does not attach a final provider observation or grant
a fresh-start or resume action.

Adding presentation-side inference was rejected because it would create another causal
authority after the bridge and terminal incident. Reusing the existing tool-failure
copy was rejected because it gives the wrong operational next action.

### 5. Verify the real handoff rather than only fixtures

Tests will first make the broken assertions red, then implement the smallest changes.
The evidence layers are deliberately distinct:

| Seam | Evidence |
| --- | --- |
| Bridge unit | Direct `AgentBudgetError`/`AgentPolicyError` stop mapping, admitted topic `httpx.ReadTimeout`, denied-policy and tools-enabled regression cases, and no raw detail. |
| Topic node | Exact two-call recovery, recovery events, no provider retry for the new non-provider categories, and separation from structured-output repair. |
| Lifecycle integration | A recipe `node_agent_bridge_factory` wrapper composes a real `RuntimeNodeAgentBridge` with scripted direct exceptions, proving the bridge-produced timeout reaches the node and terminal/session projection. |
| Shared contract | A typed terminal incident yields the exact new `RunFailureCode`, an opaque diagnostic reference derived or preserved only from typed terminal facts, and non-tool copy for machine, CLI, and TUI consumers. |

Credentialed replay of the retained demo is supplemental release evidence only. It does
not substitute for the deterministic exception and lifecycle seams.

## Risks / Trade-offs

- [A future policy accidentally opts in] -> The field defaults to the closed denied
  value, policy construction tests enumerate the only two intended opt-ins, and
  tools-enabled requests remain denied even under an opted-in policy.
- [A generic exception is mistaken for provider failure] -> Retain direct public class
  checks, no exception-chain walking, and existing unsupported-status/inner-timeout
  negative tests.
- [A retry is duplicated or a repair becomes a retry] -> Keep the bridge one-shot and
  assert both exact bridge-call count and recovery event sequence in node and lifecycle
  tests.
- [Raw stop/provider detail leaks through a new diagnostic path] -> Use sentinel values
  in bridge, terminal, and shared-experience tests; all projections use closed typed
  fields only.
- [An older binary reads a record containing a newly added enum value] -> Treat the
  values as additive only for newly written records. Do not downgrade a process that
  must resume or inspect a record carrying one of these values; finish or cancel that
  run before rollback.

## Migration Plan

1. Add the closed `RunFailureCode` values, safe presentation copy, execution-policy
   admission type/default, and explicit HITL1/topic-planning opt-ins in one compatible
   code change.
2. Add the bridge classification/admission logic and topic-planning terminal/recovery
   preservation, following the red tests in `tasks.md`.
3. Run the focused deterministic suite, strict OpenSpec validation, and the repository
   verification gate. Use a credentialed retained-demo replay only as supplemental
   evidence.
4. Roll back only before a run with a newly written failure code needs to be resumed or
   inspected by an older binary. Existing retained records remain readable by the new
   version; no data rewrite or schema migration is required.
