## Context

The retained event journal added by the preceding observability change shows that the
captured real Wave0 run exhausted three work attempts.  It intentionally withholds
raw exceptions and provider/tool bodies, but each attempt is currently collapsed to
`worker.failed`.  That is not enough to distinguish an invocation boundary failure,
a structured-output failure, or a deterministic submission-validation failure.

Wave0 already has the right control boundaries: the node-agent bridge returns a safe
`NodeExecutionResult`, the Wave0 adapter parses/repairs it, and the shared work-unit
component turns a raised worker or rejected submission into a terminal attempt and
then the existing retry/gate path.  This change adds diagnosis only; it does not alter
those authorities.

## Goals / Non-Goals

Goals:

- Record a closed, deterministic class for every terminal Wave0 worker attempt.
- Preserve the class through attempt, exhaustion, and terminal diagnostic projections.
- Keep retained files and presentation surfaces free of raw exception text, provider
  payloads, tool bodies, URLs, paths, prompts, answers, and secrets.
- Make the classification independently testable at the bridge, Wave0, and work-unit
  seams.

Non-goals:

- Diagnose the live provider/Tavily failure from the existing redacted run.
- Change model, web-tool, repair, retry, gate, ledger, or lifecycle routing policy.
- Add generic logging, tracing, a pod dependency, or changes under `backend/` or
  `frontend/`.

## Decisions

### Controller-owned closed categories

Introduce a frozen per-attempt worker-failure category owned by controller/runtime
code.  The initial closed vocabulary is `agent_invocation`, `tool_execution`,
`structured_output`, `submission_validation`, and `unknown`.  Node-agent failures
map only from existing safe `RunFailureCode`/finish-reason information; Wave0 parsing
and failed repair map to `structured_output`; a typed deterministic submission rejection
maps to `submission_validation`; an unrecognized exception at the Wave0 adapter maps to
`unknown`.  The generic component does not classify arbitrary worker exceptions for
other phases.

The exact bridge map is fixed: `tool.unavailable` and `tool.execution_failed` map to
`tool_execution`; `output.structured_invalid` maps to `structured_output`; all other
non-cancelled safe node-agent failure codes map to `agent_invocation`. Cancellation is
never classified. The component still propagates storage, ledger, and checkpoint errors
raised by its own trusted dependencies rather than turning them into a worker class.

The category is not read from a model result, tool result, exception string, prompt,
or filesystem artifact.  It is carried in a bounded attempt terminal projection and
uses strict enum validation, so an untrusted worker cannot add a free-form value.

### Preserve per-attempt truth; aggregate honestly

Each terminal attempt exposes exactly one category.  `mixed` is a separate closed
*aggregate* value, never an attempt category.  On exhaustion, the aggregate is the
shared category when all failed attempts for one work id agree, otherwise `mixed`.
The helper reads the checkpointed `AttemptRef` history, rather than just the current
fan-in batch, so retries remain part of the same honest aggregate.  The terminal
incident retains its existing `research.blocked` route code and carries this optional
diagnosis aggregate separately; the ordered event journal remains the source for
individual categories.

### Reuse the existing event envelope

No new raw log file or writer is introduced. Existing `attempt` and `exhaustion`
events receive a distinct versioned `worker_failure_category` field, rather than
overloading `validation_code`, and the existing run-summary
and terminal incident use the closed exhaustion aggregate.  The recorder remains
non-authoritative: failed recording cannot change worker status, retry allocation,
submission, gate result, checkpoint state, or lifecycle result.

### Lowest-seam tests before integration

Test the mapping without credentials or a live provider: bridge failure results,
Wave0 parser/repair failure, and the typed deterministic submit-validation exception.
The public lower-level submission function keeps its existing rejection contract; only
the shared component catches that exact typed rejection and uses its pre-existing
terminal/retry path. Infrastructure/storage failures continue to propagate unchanged.
Add one Wave0 exhaustion fixture that proves ordered redacted events and honest `mixed`
aggregation.

### Typed validation and gate-owned terminal materialization

`submit_candidate_if_active()` SHALL raise a frozen `SubmissionValidationFailure`
containing only the existing ordered closed `SubmissionValidationCode` tuple when
validation rejects a candidate. The shared component catches only this exception,
creates the existing `VALIDATION_FAILED` terminal update with
`submission_validation`, and leaves every other exception unchanged.

The gate remains the only writer of `latest_incident`. When, and only when, the Wave0
gate produces its existing exhausted route, it calls the pure historical aggregate
helper over `AttemptRef` data and writes the optional diagnosis alongside the unchanged
`research.blocked` incident. It writes no diagnosis for another phase, an incomplete
Wave0 history, a non-exhausted Wave0 route, or legacy attempts with no categories.
This is faster and sharper than repeatedly invoking the real demo.

## Risks / Trade-offs

- [A category is mistaken for a root cause] -> names describe the controller boundary
  that failed, and the BUG record explicitly keeps the provider root cause unknown.
- [More observability leaks data] -> only enum values and existing opaque identifiers
  cross persistence/presentation boundaries; adversarial redaction tests cover this.
- [Diagnosis changes control flow] -> all new data is observation-only and existing
  retry/gate assertions remain regression coverage.
- [Mixed failures lose useful detail] -> each attempt remains visible in the bounded
  timeline; only the compact exhaustion/terminal projection is aggregated.

## Migration Plan

New runs write the optional closed classification fields.  Readers accept legacy
attempts/events without them as `unavailable`; there is no bundle rewrite or checkpoint
migration.  Rollback is code rollback: existing retained events remain readable because
the envelope is additive and independently validated.

## Open Questions

None for this scope.  A future change may use a newly observed closed category to fix
the actual provider/tool integration, but only after a classified reproduction.
