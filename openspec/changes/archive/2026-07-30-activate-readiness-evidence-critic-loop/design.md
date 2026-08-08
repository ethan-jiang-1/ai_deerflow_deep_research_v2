## Context

See `proposal.md` for motivation. The current real node calls a synchronous fallback
that marks every question ready. `WorkUnitStore.read_synthesis_evidence` is the
existing trusted, bounded reader for the accepted ledger references; the existing Node
Agent bridge is the only raw model/tool binding owner.

## Goals / Non-Goals

**Goals:**

- Replace the all-ready fallback with one zero-tool, bounded critic candidate per
  readiness visit.
- Build a deterministic evidence projection before model invocation and preserve the
  existing hard-rule, materializer, state writer, and route owners.
- Make invalid or failed critic execution conservative and observable through the
  existing repair path.

**Non-Goals:**

- No direct sandbox/model access from the critic, evidence admission, new state field,
  graph edge, report prose, generic retry loop, or new terminal state.

## Decisions

### 1. Trusted projection precedes the Node Agent

Readiness will load only ledger-validated accepted evidence through the existing store,
then form a size-bounded projection paired with the current must-answer questions.
The critic sees that projection as untrusted presentation data, not checkpoint or
filesystem authority. Hash refs alone are insufficient semantic input.

Alternative considered: give the critic sandbox-read tools. Rejected because it would
widen the tool boundary and let unbounded artifact selection shape the judgment.

### 2. The ledger-reader and Node Agent capabilities are explicit

`readiness.NODE_SPEC` will declare `NodeCapability.WORK_UNIT_CONTROLLER`. The graph
wrapper therefore injects `WorkUnitControllerDependencies` from its invocation context
and rejects an absent controller with `work_unit_capability_missing` before the factory
or model can run. The real factory repeats the same fail-closed check for direct factory
tests, then uses `dependencies.work_units.store.read_synthesis_evidence` as the sole
reader for the accepted refs. Full-fake execution remains its existing no-op fixture
node; the recipe already requires work units for every runnable graph.

The runtime currently selects dedicated bridges for some individual Node Agent callers.
This change adds the same explicit per-node selection for readiness: a readiness-only
zero-tool policy and bridge are constructed when `readiness=real` and placed in the
base resolver's per-node map. It must not inherit the default HITL1 or topic-planning
bridge merely because real-readiness compatibility requires the upstream real chain.

Alternative considered: read the store through an undeclared optional dependency or
reuse an upstream bridge. Rejected because both make the critic's I/O or policy depend
on incidental recipe ordering rather than an auditable node contract.

### 3. Candidate cardinality and retention are deterministic admission

The request names the exact question set. The parser requires schema version, one
verdict per supplied question, no duplicate/unknown question, bounded claim references,
and no route/checkpoint fields. Hard rules run independently and the materializer/node
remain the only writers.

Each admitted backing reference must be one of the ledger-validated submission refs
present in the projection. The checkpoint receives only the admitted typed summary;
raw provider output, rejected JSON, prompt content, and provider diagnostics stay out
of `readiness_critic_summary`.

The bridge's existing structured-result byte budget bounds raw success output. The
readiness contract will additionally bound retained field cardinality and values, and
the writer will build a fresh projection from only the admitted `per_question` fields
consumed by the materializer. It will not checkpoint unused critic fields such as
`overall_limitations`, `synthesis_flaws`, or `contradiction_ids`, even when they were
present in otherwise parseable model output. This prevents a general model summary from
becoming durable control-state content.

Alternative considered: accept partial output and fill missing answers ready. Rejected
because it recreates the false all-ready fallback.

### 4. Model failure projects to existing repair; ledger failure remains structural

Bridge failures and invalid candidates are normalized by readiness into
`blocked_repair_required` for the affected question set. The existing node route logic
then selects `repair_targeted`; structural failures retain their existing `exhausted`
precedence. Existing targeted-evidence/gate budgets bound subsequent work.

An absent accepted record, unreadable result, or integrity mismatch from
`read_synthesis_evidence` is not critic uncertainty and cannot be repaired by adding
new targeted evidence while the invalid accepted ref remains. Readiness therefore maps
that bounded reader failure to a redacted structural hard-rule fact and the existing
`exhausted`/`BLOCKED` branch before any request is built. The raw store exception,
artifact path, and content stay out of checkpoint state.

Alternative considered: retry the model locally. Rejected because it creates a second
recovery controller and duplicates existing graph-owned repair bounds.

### 5. Evidence claims stay split by proof class

Scripted zero-API tests prove the real request/policy/bridge/node composition and all
failure projections. Labeled evaluation assesses answerability candidate quality only;
credentialed runs are supplemental and may report `inconclusive` rather than creating a
fallback or test retry.

## Risks / Trade-offs

- [Bounded projection omits material context] -> conservative insufficiency/repair is
  legal; evaluate projection coverage with labeled cases before claiming quality.
- [Provider failure adds repair work] -> use the existing bounded repair controller;
  do not silently mark the run ready.
- [An incidental upstream bridge governs readiness] -> bind a readiness-specific policy
  by logical node and prove resolver selection; do not rely on full-chain ordering.
- [A store reader is absent or accidentally available] -> declare the controller
  capability, fail before invocation when unavailable, and test both factory and graph
  wrapper admission.
- [Accepted evidence cannot be read or fails its integrity check] -> record only a
  closed structural failure and take the existing exhausted branch, rather than loop
  targeted repair over an immutable bad reference.
- [Model mistakes evidence text for authority] -> capability/prompt delimit the
  projection and deterministic candidate admission rejects authority fields, unknown
  questions, and backing refs absent from the projection.
- [Rejected output leaks into checkpoint state] -> store only the bounded admitted or
  conservative projection and prove raw rejection data is absent.

## Migration Plan

1. Add the declared work-unit capability, readiness-specific bridge/policy selection,
   capability, prompt/request builder, projection, and candidate parser through existing
   Node Agent seams.
2. Replace the fallback only for real readiness; retain full-fake fixtures unchanged.
3. Add deterministic conformance/failure tests and the bounded judgment evaluation
   assets, then run the canonical offline verifier. Rollback restores the previous
   deterministic critic function without state or topology migration.
