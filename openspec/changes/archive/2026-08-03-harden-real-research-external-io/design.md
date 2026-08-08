## Context

See [proposal.md](proposal.md) for motivation and review records. The current runtime
already maps admitted zero-tool model-service failures into a closed `NodeProblem`,
and HITL1 already owns its two-invocation visit budget, one transient-provider retry,
structural repair, blocked route, and terminal incident. The standalone demo creates
run-local Tavily search/fetch tools outside that bridge; the recent tactical patch
adds a 60-second read deadline and a three-attempt transient retry there. The same
patch removed an expected `brief_summary_language` output field that the strict
`StructuredBrief` parser forbids.

The retained live result `r_I1j6YtWqBkeMHRWiuDqUD7jz4a2YNPMXqU7uwSp28cc` is verified
only as `blocked@hitl1` with the safe projected category `research.blocked`. Its
opaque diagnostic reference is evidence that a terminal was retained, not proof of a
specific provider, parser, or graph cause. The implementation must preserve this
uncertainty until a deterministic seam or safe typed terminal fact identifies it.

No new checkpoint, persisted retry counter, provider credential, or lifecycle action
is required. Existing `NodeProblem`, HITL1 `ProviderRecoveryProjection` /
`latest_incident`, `RunFailure`, and `Terminal` remain their current respective
owners.

## Goals / Non-Goals

**Goals:**

- Make configured idempotent demo web reads bounded, cancellation-safe, and retry only
  direct transient conditions.
- Make a future prompt/schema drift fail in a deterministic test before it becomes a
  real HITL1 lifecycle failure.
- Prove that existing typed terminal facts remain distinguishable when rendered by the
  standalone CLI.
- Use one bounded credentialed run only after deterministic evidence passes.

**Non-Goals:**

- A generic provider retry framework, provider failover, or changes to SDK retry
  settings.
- A new graph route, worker retry policy, state schema, checkpoint field, diagnostic
  allocator, CLI command, or recovery action.
- Inferring the unresolved live-run cause from `research.blocked`, or treating a
  successful canary as an availability guarantee.
- Changes under `backend/` or `frontend/`.

## Decisions

### 1. Keep model and web-read recovery at their direct, existing boundaries

The runtime bridge remains the direct classifier for admitted zero-tool model calls;
HITL1 remains the sole graph owner of its existing one-retry/two-invocation brief
budget. It will not gain a general provider retry wrapper. The demo web-tool adapter
owns only its direct Tavily search/extract calls because they are independently
idempotent reads and have no authority over graph state or phase routing.

For a web read, execute one fresh client call in an async deadline scope. Accept only
direct public timeout, transport/protocol, Tavily usage-limit, HTTP 429, and HTTP
500-599 evidence as retry-eligible. Run at most two cancellable sleeps, then return
the existing redacted unavailable tool payload on exhaustion. Let cancellation escape
from both the call and the backoff. Authentication, malformed input, non-429 4xx, and
unknown errors remain one-attempt outcomes.

This prevents a broad `except` from turning a deterministic misconfiguration into
network flakiness while retaining the worker's current freedom to use other permitted
tools or finish normally. It also ensures the web adapter never creates a lifecycle
terminal or a duplicate provider diagnostic.

**Alternatives considered:**

- A runtime-wide retry manager was rejected: it cannot observe whether every arbitrary
  tool is idempotent, would compete with graph-owned provider recovery, and would
  blur per-tool versus per-node budgets.
- Retrying every caught exception was rejected: it hides credentials/input faults and
  makes cancellation or programming errors look recoverable.
- Returning raw exception/status text to the worker was rejected: tool output crosses
  a model boundary and must remain bounded and redacted.

### 2. Treat expected JSON as an admission-contract projection, not an independent schema

HITL1 will continue to build its human-readable instruction plus a compact JSON
expected-output descriptor. A deterministic prompt test will parse the descriptors
from both initial and structural-repair requests, assert that each contains every field
the strict `StructuredBrief` parser requires and only fields the parser accepts, then
validate a canonical candidate formed from its advertised values and bounds through the
existing parser. Parser-defaulted fields are not required to appear in `required_keys`;
advertised fields may be stricter only when their values remain parser-valid. The test
will also exercise a forbidden extra field. The prompt may constrain how
`brief_summary` is written, but language remains a system instruction plus parser-side
semantic check and does not advertise unsupported `brief_summary_language` output.

The parser remains the admission owner. It receives raw model candidate text, performs
strict validation, and uses the existing one structural repair or typed blocked result.
No runtime schema registry, model-native structured output feature, or checkpointed
candidate is introduced.

**Alternatives considered:**

- Automatically generating every sentence of the prompt from Pydantic JSON Schema was
  rejected: the model needs concise task-specific instructions and this would expose a
  broad schema surface without improving authority.
- A separate hand-maintained admission schema was rejected: BUG-023 is the concrete
  counterexample; parser-compatibility fixtures keep the existing admission contract
  single-sourced while preserving concise task-specific prompt guidance.

### 3. Diagnose projection drift at the shared terminal seam

The CLI receives only `ResearchRunExperience` updates. That module already preserves
the terminal incident code in `RunFailure`, but the current generic CLI failure branch
does not render a non-provider category. Add deterministic terminal fixtures for at
least a provider category and `output.structured_invalid` after the HITL1 blocked
route, then repair that existing CLI projection. The test asserts that the rendered
terminal identifies the final safe category, phase, opaque diagnostic reference,
durability truth, and its legal next action without raw input/provider content. It
must distinguish those typed incidents from an actually generic `research.blocked`
result.

Do not add a second CLI classification branch, inspect retained files to infer a
category, or claim resume from a same-process run. The terminal incident remains the
only writer of its causal summary and diagnostic correlation.

### 4. Make live execution a bounded integration canary, not the regression oracle

The deterministic sequence is: direct adapter fakes, prompt/parser tests, HITL1 node
and lifecycle tests, then terminal projection tests. Only after it is green, run the
existing `run/real-research.sh` once with an explicit question and the script's normal
preflight. The test operator records only the run reference, phase/result, safe
category, diagnostic reference, and whether the run reached the first HITL1
suspension or progressed beyond it.

The canary has one run, existing provider and web read budgets, and no manual rerun
loop. A failing external dependency remains a recorded typed operational result; a
new deterministic regression discovered from its safe category becomes a follow-up
bug/change rather than silently expanding this one.

## Risks / Trade-offs

| Risk | Mitigation |
| --- | --- |
| Three 60-second web attempts can consume up to three minutes for one read | The cap is explicit, occurs only for direct transient classifications, has short backoff, and remains inside existing worker wall-time/tool-count budgets. |
| SDK exception types vary across releases | Classify only the named direct public boundary; unrecognized errors fail once and remain redacted. Focused fakes cover the permitted classifications. |
| Schema fixture passes while semantic language quality is poor | The fixture verifies structural compatibility only; existing parser-side language validation and bounded repair remain in force. No live-language quality claim is introduced. |
| A CLI fixture creates a false impression that real providers work | The fixture proves projection only; the one live canary is explicitly supplemental and may legitimately end in a typed failure. |
| Current tactical code already implements parts of DPL-009 | Apply begins by reconciling code, constants, tests, bug records, and the approved delta; only missing or nonconforming behavior is changed. |

## Migration Plan

1. Register `DPL-009` and `HIN-013` in the requirement registry before implementation
   evidence runs.
2. Reconcile the current tactical patch with these deltas, correcting any disagreement
   (including documents that still describe a different deadline) before declaring a
   task complete.
3. Add the missing deterministic evidence, reconcile any exposed contract disagreement
   with the smallest necessary change, then run the focused suite and normal downstream
   verification.
4. Run the one bounded real CLI canary and record only its safe retained facts in the
   backlog plan/bugs. Close or continue the bugs based on evidence.

No retained data migration is needed. A rollback reverts only the downstream adapter,
prompt/parser, or projection change; existing terminal records remain readable because
no checkpoint or diagnostic schema changes.
