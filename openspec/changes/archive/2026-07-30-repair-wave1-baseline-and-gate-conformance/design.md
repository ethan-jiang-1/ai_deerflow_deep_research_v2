## Context

### Verified current behavior

- `wave1/node.py::build_real` creates `wave0_urls = set()` and leaves both record
  loops as `pass`, so the real worker never receives the available Wave0 baseline.
- `SubmissionRecord` carries `phase`, `generation`, `source_refs`, and canonical
  source URLs. `WorkUnitStoreProtocol.load_records()` is asynchronous and is the
  authoritative record read.
- The current Wave1 worker writes a validated `Wave1SourceIntakeResult` plus source
  cache entries. Its accepted result exposes source id, canonical URL, title,
  `is_new_vs_wave0`, claims, and open-question states. It does not retain a source
  body or a reliable source-id mapping for `NodeExecutionResult.untrusted_tool_results`.
- Real Wave1 currently has only `worker` and `repair` `run_agent` calls. Its real
  gate contains only `WorkUnitCompletionRule`.
- `targeted_evidence` has SourceDiagnostic/ClaimVerifier helpers, but they are
  phase-specific and materialize under a targeted node attempt. They cannot become a
  Wave1 producer or route authority by reuse.
- The graph already carries Wave2's specialized non-checkpointed gate preview. The
  shared `WorkUnitGateView` is deliberately bounded and contains no artifact paths
  or candidate bodies.

### Approved decision

Wave1 adds two bounded, local, zero-tool critic branches:

```
accepted Wave1 record
        |
        +-- validated compact source observations --> SourceDiagnostic
        |
        +-- validated claims + new source ids ----> ClaimVerifier
                                                     |
                                       bound immutable review artifacts
                                                     |
WorkUnitGateView + Wave1GateReview --------------> pure Wave1 gate
                                                     |
                                         pass | repair | exhausted
```

This implements the accepted Wave1 contract that calls both critics after acceptance
and has the gate consume their artifacts. It raises the active direct-branch
denominator from sixteen to eighteen. The existing generic runtime admission rule
already covers a required capability whose posture forbids tools; this change does
not change generic runtime behavior.

## Goals / Non-Goals

**Goals:**

- Read the canonical same-generation Wave0 baseline from accepted records before
  real Wave1 worker dispatch.
- Dispatch exactly the missing Wave1 review branches for every accepted Wave1
  work/attempt, materialize only identity-bound valid artifacts, and preserve
  independent branch evidence.
- Give the real gate a frozen Wave1 review projection sufficient to enforce the
  source floor, critic presence, and open-question disposition after structural
  completion.
- Keep model, tool, artifact admission, ledger, checkpoint, gate, route, and
  retry authorities separated and deterministically testable without a provider.

**Non-Goals:**

- Capture, scrape, or infer source bodies; evaluate source or critic quality; or
  promote the critic result to factual truth. This change reviews accepted source
  observations only, and Change 5 remains the quality-calibration owner.
- Reuse `targeted_evidence` as a Wave1 route, change its artifacts, or add a generic
  critic scheduler.
- Expand `WorkUnitGateView`, persist a Wave1 review field in `ResearchState`, alter
  the gate kernel/routing/budget, or modify backend/frontend.

## Decisions

### Read the baseline from authoritative accepted Wave0 records

Before the real worker is dispatched, `build_real` SHALL await the work-unit store,
select only accepted records matching the active `research_id`, `generation`, and
`phase=wave0`, canonicalize their `source_refs` URLs, and pass the resulting immutable
set to the existing Wave1 worker request. A record required by checkpointed accepted
refs that is unavailable, invalid, cross-generation, or not Wave0 is an authority
failure: the node fails before dispatch and never substitutes `frozenset()`.

The node will not infer URLs from record hashes, checkpoint projection, source text,
or prompts. Copying baseline URLs into `ResearchState` remains rejected because it
would create a second source of record.

### Validate provenance and the source floor at both admission boundaries

After parsing either the initial or structured-repair draft and before any
`write_source()` or `write_result()` call, a Wave1-local semantic validator SHALL
canonicalize every URL, require each declared canonical URL exactly once, derive
`is_new_vs_wave0` from the assigned baseline, require every claim support/counter
reference to be in that output's declared source ids, and require at least two
distinct new canonical URLs. Any provenance, canonical-uniqueness, or floor violation
enters the existing bounded structured repair without emitting a source/result
artifact or candidate. An inadequate repaired draft follows the existing worker
failure/retry path; it is not made valid by a partial artifact write.

Contract-specific submit validation SHALL independently parse the persisted
`Wave1SourceIntakeResult`, reconstruct the same-generation accepted Wave0 URL set from
the supplied accepted records, verify every persisted `is_new_vs_wave0` marker against
that set, and recompute canonical-URL uniqueness, provenance, and the two-new-URL
floor before a `SubmissionRecord` is appended. Any failure uses the existing closed
typed validation outcome and appends no record. The real gate repeats only the
two-URL floor over accepted records as a defense against later artifact or projection
divergence; it does not relax either earlier boundary.

### Add local post-acceptance critic branches

After the work-unit component has reconciled its accepted records, Wave1 SHALL select
the current-generation accepted Wave1 record for each completed logical work. For each
record it SHALL read and canonically validate the referenced `Wave1SourceIntakeResult`
against the record identity, result hash/byte count, source ids, and source refs.
Only then may it create a critic assignment.

Before dispatch, Wave1 SHALL read the two fixed review records for that accepted work
attempt. A valid record whose envelope identity and input hash match the reconstructed
assignment suppresses only its own critic call. An absent record dispatches that one
critic; a malformed, mismatched, or conflicting record fails closed before either
dispatch or gate evaluation. Thus a repair visit re-runs only a missing critic and
never creates a second valid result for an already reviewed accepted attempt.

The SourceDiagnostic assignment contains, in a delimited untrusted-data block, only
the ordered accepted new-source observations:
`source_id`, canonical URL, title, and `is_new_vs_wave0`. The ClaimVerifier assignment
contains only the ordered accepted claims and the assigned new-source ids. Neither
assignment includes a candidate body, result/cache path, raw tool result, checkpoint
field, prior gate feedback, or route. A persisted source observation is deliberately
not represented as a fetched source body; the prompt and evidence ledger shall not
claim source-quality proof from it.

Each assignment is one `capabilities.run_agent()` call using a Wave1-local required
capability with `forbidden` tool posture. SourceDiagnostic returns
`SourceDiagnosticResult`; ClaimVerifier returns `ClaimVerifierResult`. The existing
runtime bridge remains the sole tool/window/budget/cancellation enforcer. The call uses
the current Wave1 phase dependency context; its agent receives no artifact-write
capability, while the deterministic materializer later binds a result to the accepted
work attempt. Each invocation is normalized before materialization; a
provider/model/parse failure has no artifact side effect.

### Bind and materialize critic artifacts to the accepted work attempt

Wave1 SHALL use a new frozen, extra-forbid envelope for each critic artifact. The
envelope includes: schema version, critic kind, `research_id`, generation, phase,
`work_id`, accepted `attempt_id`, accepted record hash, deterministic input hash, and
the typed critic result. The input hash covers the exact ordered assignment facts, not
paths or raw tool/model data.

The materializer SHALL derive the artifact location solely from that accepted
work/attempt and write each canonical envelope through the existing constrained
attempt cache writer under fixed `review/` names. The artifact is not a candidate
output, source ref, submission record, checkpoint field, or route authority. A
pre-existing byte-identical envelope is idempotent; a different existing value is an
integrity failure.

Before materializing SourceDiagnostic, the deterministic materializer SHALL require
its unique source-id set to equal exactly the accepted new-source ids and reject any
foreign source id. Before materializing ClaimVerifier, it SHALL require exactly the
accepted claim-id set (or the empty set for no claims), reject duplicate/foreign claim
ids, and reject every support/counter reference outside the accepted new-source ids.
The materializer then orders valid results by the accepted assignment order before
canonical writing; it does not use model order as authority. A malformed,
unbound, or conflicting stored artifact fails closed during later review construction;
it is not converted into a retryable model result.

Existing targeted-evidence critic materializers are not reused: their node-attempt
identity and direct workspace path are not a valid Wave1 work-attempt contract.

### Use a Wave1-only ephemeral review projection

After critic materialization/reconciliation, Wave1 shall build a frozen
`Wave1GateReview` keyed by the accepted logical work ids. Each bounded row contains the
work id, accepted record hash, count/disposition of distinct canonical new URLs,
presence of each valid bound critic artifact, and normalized open-question disposition.
It contains no artifact path, source/candidate body, raw critic reason, tool result,
or route. Its validator requires its sorted work/record identity to equal the
`WorkUnitGateView` accepted mapping exactly.

Wave1 returns this projection under a dedicated private reserved key. The graph wrapper
shall accept, type-check, and inject it only for real Wave1 after validating the
existing `WorkUnitGateView`; it then removes the key before state reduction or
checkpoint serialization. This follows the existing Wave2 preview pattern, leaves
`WorkUnitGateView` unchanged, and introduces no generic work-unit API.

### Gate sequence and outcome ownership

`WorkUnitCompletionRule` remains first. Because the gate kernel evaluates every rule,
each Wave1-specific rule shall no-op until the work-unit view is structurally complete
and contains one accepted record for every planned work. Thereafter, in stable order,
the gate checks:

1. each accepted topic has at least two distinct canonical URLs with
   `is_new_vs_wave0=true`;
2. each accepted topic has both valid bound review artifacts; and
3. every open question is `resolved`, `deferred`, or `requires_internal_data`.

Floor, absent-review, and `targeted_search` failures are repairable existing gate
failures. The existing gate kernel alone applies budget/fatigue behavior and maps
`PASS`, `REPAIR`, and `BLOCKED` to `pass`, `repair`, and `exhausted`. Critic verdict
values and prose are not route selectors; this conformance change establishes
availability/binding, not an uncalibrated model-quality threshold.

### Preserve evidence and prompt governance

Wave1 declares `wave1-source-diagnostic` and `wave1-claim-verifier` local capability
resources and catalog cases `wave1/source-diagnostic` and `wave1/claim-verifier`.
The test-owned capability/cognitive-program assets add one row per case, each with
separate normal and highest-risk collected deterministic claims. The generated prompt
catalog is refreshed from the production prompt builders. All evidence calls these
branches bounded cognition and deterministic admission behavior, not source truth,
critic accuracy, or research quality.

## Failure Handling

- Baseline record absence or mismatch: fail before worker dispatch, with no empty
  fallback and no new route.
- Critic non-success, malformed output, or bound-materialization rejection: write no
  artifact. A later Wave1 repair visit can re-run only the missing critic, subject to
  the existing gate budget and fatigue bound.
- Existing review artifact malformed, mismatched, or conflicting: fail closed before
  gate evaluation; do not overwrite or silently repair durable evidence.
- No new-source floor, missing valid review artifact, or `targeted_search` question:
  return the existing repairable gate failure. Exhaustion remains the existing terminal
  blocked path.
- Cancellation propagates through the existing bridge/controller boundaries and writes
  neither a success artifact nor a review projection.

## Risks / Trade-offs

- [Critics see compact observations, not source bodies] -> make that boundary explicit
  in prompts, design, and evidence; do not claim quality calibration.
- [Critic work adds two model calls per accepted topic] -> each is single-call,
  forbidden-tool, post-acceptance, and no-ops when an immutable valid artifact already
  exists.
- [Artifact reuse could cross a work or attempt] -> bind identity and deterministic
  input hash in the artifact envelope and validate it against the accepted record.
- [A Wave1-specific view leaks into state] -> use one private, frozen, non-checkpointed
  key that the wrapper extracts before reducer preview.
- [Review failure can loop] -> preserve the existing repair budget and fatigue
  escalation; critics never select a retry or route.

## Migration Plan

1. Add focused red tests for baseline reconstruction, critic capability/prompt
   admission, identity-bound artifact materialization, review projection validation,
   and real-gate outcomes.
2. Implement the Wave1-local capabilities/prompts, baseline reader, post-acceptance
   critic dispatch/materializer, review projection, wrapper handoff, and pure gate
   rules until those tests are green.
3. Update generated prompt outputs and test-owned evidence/requirement inventories;
   run focused tests followed by `cd agent && UV_OFFLINE=1 make verify`.
4. On regression, revert the phase-local baseline/review implementation together.
   No stored-data migration, public API migration, or backend/frontend rollback is
   required; existing review artifacts are non-authoritative cache records.
