## Context

BUG-006 is reproducible in the credential-free fake CLI and is reachable from any
standalone adapter that renders a HITL2 option as an ID plus a human-readable
consequence. The graph correctly rejects a pasted display line as
`response_invalid`, without mutating the suspended checkpoint. The runtime
presentation module then validates the denial's empty trace against the previously
verified non-empty trace, turns that expected mismatch into
`protocol.invalid_result`, and leaves adapters with no retryable prompt.

The graph remains the sole authority for accepted HITL2 decisions. The run
experience is process-local presentation state. It currently retains the last
validated pending request, prompt, trace, and individual snapshot fields, but it
does not retain the complete `AwaitingInput` snapshot needed to reissue the exact
safe suspension. This change adds that bounded presentation cache only; no backend,
frontend, checkpoint schema, provider, or retained-bundle format needs to change.

## Goals

- Make canonical choice-ID entry explicit in standalone CLI presentation.
- Re-present a verified pending choice after a locally rejected choice without
  rerunning graph nodes, changing the checkpoint, or fabricating trace progress.
- Preserve a closed input-validation category instead of masking it as a protocol
  failure.
- Keep malformed, mismatched, or otherwise untrusted lifecycle results fail-closed.
- Add zero-API deterministic regression proof at the shared runtime and public fake
  CLI seams.

## Non-Goals

- Accepting or parsing rendered `<id>: <description>` text as a graph decision.
- Changing HITL2 option IDs, graph routing, checkpoint schema, retained-session
  authority, durability, Gateway, Web UI, or model/web behavior.
- Persisting raw rejected input, exception text, or a new diagnostics record for a
  locally recoverable invalid choice.

## Decisions

### Keep option IDs canonical and make the entry contract explicit

Every standalone choice renderer will keep the bounded option consequence, but will
state that the user must enter/select the option ID (for example, `proceed`). The
adapter submits that value through `AnswerRun`; only the graph/runtime validation
decides whether it is acceptable.

Accepting a copy of the rendered display line was considered and rejected. It would
make a presentation-local string an alternate control protocol, creates localization
and formatting ambiguity, and bypasses the useful distinction between an advertised
option ID and explanatory text.

### Recover only a narrowly verified invalid choice as the existing pending prompt

After decoding a lifecycle result, `ResearchRunExperience` will recognize a retry
only when all of the following are true: the locally dispatched action was `resume`;
the result is a typed `resume` `response_invalid` denial for the current research
ID; the module still holds a previously validated `AwaitingInput` whose prompt and
pending request are both HITL2 `choice`; and the denial supplies no lifecycle state.
In particular, its trace is empty and it has no bundle directory, status, phase,
generation, request/pending projection, or terminal projection. It will then return
an immutable copy of that cached `AwaitingInput`, preserving the exact validated
snapshot, prompt/request, and trace while adding only a closed choice-validation
feedback category and an empty trace delta.

The denial must be the ordinary decoded mapping form, not a `Command` carrying a
new human-input artifact. The cached snapshot's pending projection, prompt, and
pending request must still agree on request ID and `choice` mode, and its research ID
must agree with the current run and denial. Those checks make the cache a validated
presentation fact rather than an alternate source of lifecycle authority.

The invalid message may remain in the local message sequence; a later valid answer is
the newest eligible response and normal graph validation remains authoritative. The
re-prompt path does not publish a session fact, write diagnostics, or derive state
from denial payload fields beyond the strict recognition predicate. It must not
reconstruct a snapshot from current mutable fields, because that would lose the
validated `pending_input` projection or accidentally adopt denial data.

Returning a retryable `Fault` and teaching every adapter to reconstruct a prompt was
rejected because `Fault` does not carry a prompt, would make adapters own recovery
policy, and could diverge across CLI and TUI. A new `RunUpdate` variant was rejected
because a feedback-bearing `AwaitingInput` already expresses the unchanged graph
state and preserves the closed public interface shape.

### Validate source category before trace continuity only for that denial class

Normal record-bearing results and all unknown/non-matching denials continue through
the existing ordered trace and wire validation, preserving fail-closed behavior. The
retry branch is intentionally before trace mutation because a non-record denial has
no new graph trace to validate. It neither replaces the last known trace nor accepts
an empty trace as a general continuation.

A mismatched expected outbound action, result action, code, research ID, prompt mode,
pending request, empty-trace condition, or any unexpected record-bearing field
remains a `protocol.invalid_result` Fault. `response_mismatch` also remains
non-retryable because correlation failures must not be re-presented as a safe user
correction.

### Use closed feedback, not raw rejected text

`PromptView` already carries the optional closed `rejection_category` channel for
HITL1 feedback. Its frozen literal will be extended with `choice_input_invalid`
rather than adding a parallel field. Adapters render fixed safe feedback from that
category and never echo the rejected value. This keeps one bounded feedback contract
for CLI and TUI while retaining the redaction boundary and compatibility for prompts
whose category is absent.

## Risks / Trade-offs

- [A broad denial branch could hide a malformed protocol result] -> Match only the
  exact locally initiated `resume`, same-run `response_invalid` shape with a cached
  HITL2 choice suspension, no lifecycle-bearing fields, and no new request artifact;
  retain protocol faults for every other case.
- [A reconstructed retry could lose or fabricate pending state] -> Cache the complete
  validated `AwaitingInput` and return an immutable copy with only closed feedback and
  an empty trace delta.
- [A retry could imply graph progress] -> Preserve the previous trace and use an
  empty trace delta; do not invoke a node, publish a fact, or change durability.
- [Adapters could display different wording] -> Expose one closed rejection category
  and add adapter assertions for safe, actionable wording rather than raw input.
- [Invalid local messages accumulate before a valid retry] -> Test that the latest
  eligible valid response is consumed and that the rejected text is absent from
  returned prompt, failure, and diagnostics surfaces.

## Migration Plan

1. Add red tests at the shared run-experience and public fake-CLI seams, including
   wrong outbound action and non-choice-prompt rejection cases.
2. Implement the cached-update feedback/re-prompt branch and canonical choice-ID
   guidance.
3. Update the affected adapter renderers and evidence registrations.
4. Run focused tests, the deterministic agent verification, strict OpenSpec
   validation, and diff checks.

The change is code-only within the downstream `agent/` package and its tests. There
is no data migration, configuration rollout, restart procedure, or compatibility
fallback. Reverting the change restores the prior presentation behavior without
touching checkpoints or retained bundles.

## Open Questions

None. The canonical option IDs and existing graph validation contract are already
defined; the change only makes their presentation and recovery semantics accurate.
