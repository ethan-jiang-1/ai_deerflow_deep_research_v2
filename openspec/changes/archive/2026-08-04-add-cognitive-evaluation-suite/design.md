## Context

The proposal's motivation and observable contract are in `proposal.md` and the two delta
specs. The relevant current constraints are:

- Deep Research production Python is governed by the `deerflow_research/src/deerflow_deep_research/`
  source root and its `runtime` ownership layer. `backend/` and `frontend/` are upstream and
  are not part of this change.
- `tests/eval/` is already a deterministic pytest selection. `tests/scenarios/live.py` and
  the branch-specific live helpers contain useful bridge, preflight, and reporting seams,
  but they currently combine execution plumbing with calibration/rubric concerns.
- Production node handlers, parsers, validators, work-unit controllers, ledgers, gates,
  checkpoint state, and lifecycle routes remain the authorities for production behavior.
- The product decisions recorded in `deerflow_research/CONTEXT.md` require two independent
  evaluation layers: a Python Runner that collects objective evidence and an upper,
  review-only Agent workflow that a person explicitly starts.

The new suite therefore adds an observation and review boundary around existing production
branches. It does not create a second graph, a production recovery controller, or a second
candidate-admission authority.

## Goals / Non-Goals

**Goals:**

- Give every selected execution a fresh local identity, isolated workspace, immutable Bundle,
  and objective execution status.
- Make Case, control-version, observation, output, artifact, resource, and failure provenance
  sufficient for a later review without rerunning the execution.
- Keep execution, cognitive judgment, and production admission in separate ownership layers.
- Make human initiation of review and explicit fresh reruns visible in the operator contract.
- Establish a directory layout that keeps versioned control content separate from generated
  run data and keeps Python implementation in the governed source root.
- Start with two node-level Cases that exercise real production seams and expose the highest
  value of the protocol without claiming whole-flow quality.

**Non-Goals:**

- Making `evals/` part of normal pytest collection or deterministic CI.
- Implementing a new evaluator graph node, general Python LLM judge, auto-fixer, or scheduler.
- Capturing hidden chain-of-thought; the observation trace is limited to objective runtime
  events, logs, tool/model call metadata, outputs, artifacts, resources, and diagnostics.
- Adding portable redaction, multi-user storage, cloud execution, or user-facing Support
  Handoff in Local-First V1.
- Changing production retry, provider fallback, checkpoint, lifecycle, graph route, or
  candidate admission behavior.

## Decisions

### 1. Use three physically separate surfaces

The suite uses three distinct locations below `deerflow_research/`:

```text
evals/
  control/                         # tracked, slow-changing declarations
    cases/
    rubrics/
    review_protocol.md
    schemas/
  runs/                            # ignored, fast-changing local records
    <execution-id>/
      bundle/                      # immutable evidence only
      reviews/<review-id>/         # immutable review records only
src/deerflow_deep_research/runtime/evaluation/
                                  # governed Runner/recording implementation
src/deerflow_deep_research/domain/evaluation.py
                                  # pure typed Case/Bundle/Review contracts
```

`evals/control/` is the authority for registered Case and Rubric versions and the review
protocol. `evals/runs/` is never an authority; it is the local materialization area for one
execution and its separately stored reviews. Pure typed contracts live in the `domain` layer;
the `runtime` package owns loading, workspace I/O, invocation, and record publication. Neither
is a script or resource hidden in either content subtree.

**Alternative rejected:** put Cases, runner code, and generated Bundles in one `evals/`
package. That makes a frequently changing run tree look like source authority, encourages
imports from generated data, and violates the requested control/run separation.

### 2. Treat a Case as a closed execution declaration

A Case registry entry is versioned and names only a finite subject, fixture/input builder,
service requirements, resource bounds, and control identity. A runner invocation accepts a
Case id/version and an explicitly selected local environment binding; it does not accept an
arbitrary prompt, path, model override, or resume token. A Rubric is selected by the Case
version for the later review, but the runner process does not read or interpret it.

**Alternative rejected:** accept a free-form prompt plus optional node name. This bypasses
the production branch's bounded input contract, makes results incomparable, and lets an
operator accidentally run an unbounded or resumed graph.

### 3. Keep the Runner one-shot and externally orchestrated

The Runner owns preflight, Case admission, workspace creation, production invocation,
observation capture, Bundle finalization, and the two-state execution status. It performs
one outer execution and contains no retry, resume, review dispatch, or quality judgment. A
provider timeout or malformed result is recorded as a failed execution with observations;
an operator may correct the owner and explicitly invoke the Case again under a new identity.

This is deliberately different from production recovery: production node/controller retry
remains inside the production path and is observed as part of the Case execution. The Runner
does not reimplement or override it.

**Alternative rejected:** put a small retry loop in the Runner to improve smoke-test success.
That would hide provider instability, make Bundle attempt counts ambiguous, and risk replaying
state or human decisions outside the production owner.

### 4. Finalize an immutable Bundle before returning

The execution workspace writes observations to temporary files while the subject runs. At
finalization, it writes a manifest containing execution id, Case/control identities, status,
timestamps, and content digests, then publishes the Bundle atomically. The Bundle contains
declared inputs, actual outputs/artifact references, an append-only Observation Trace, resource
observations, and typed diagnostics. A failure path finalizes the material collected so far
with `failed` status when possible; a publication failure cannot be presented as a reviewable
success.

The Bundle is logically immutable after finalization. Review data lives in a sibling
`reviews/<review-id>/` record and references the Bundle manifest/digest; it never edits the
Bundle directory. This permits multiple review passes over one costly run and makes evidence
hashes stable.

Before an external evaluator receives a Bundle or the review adapter accepts a Review Record,
the review boundary reloads the finalized manifest, verifies every declared content digest and
required record, then resolves the exact Case, Node Cognitive Control Contract, Rubric, and
Review Protocol identities recorded by the Bundle. A missing, changed, incomplete, or
stale-control record is rejected as non-reviewable; it does not alter the Bundle's historical
execution status or create a Review Record. This is the deterministic meaning of immutability
in a private local store: the protocol detects post-publication mutation rather than claiming
that a local user cannot modify a file.

**Alternative rejected:** append evaluator conclusions to `manifest.json` or mutate a run
summary in place. That would conflate observation and judgment and make the same execution
produce different evidence depending on review order.

### 5. Capture an objective trace, not hidden reasoning

The Runner records event and log timestamps, phase/branch labels, request and result metadata,
tool names and call counts, model/provider identifiers permitted by local policy, resource
usage, artifacts, and sanitized typed diagnostics. It may retain the model/tool output needed
to inspect the branch's actual candidate, but it does not attempt to reconstruct private
chain-of-thought or infer a quality verdict from prose.

The upper review receives the Bundle plus the Node Cognitive Control Contract, Case-linked
Rubric, and Review Protocol. It interprets objective observations and candidate outputs; it
does not turn the trace into a lifecycle fact or candidate admission.

**Alternative rejected:** retain only the final text. That leaves the MD-controlled process
uninspectable and cannot distinguish a missing tool call, wrong branch, timeout, or malformed
candidate from a cognitive failure.

### 6. Make review a separate human-controlled operation

The runner-facing operator command returns the Bundle reference and execution status. A
separate explicit review command/adapter accepts a Bundle reference and loads the versioned
Contract, Rubric, and Review Protocol. A Coding Agent or approved evaluator interface may
perform the multi-turn inspection, but the review operation is read-only and cannot call the
Runner. Its output is validated into a Review Record with four cognitive result states.

The same Bundle can be submitted to multiple reviews. A person may defer review, choose a
different evaluator, or start another review without spending another model/web execution.

**Alternative rejected:** automatically run the evaluator as the final Runner step. It would
remove human control, couple expensive execution to one review policy, prevent independent
review, and make a failed review look like a failed run.

### 7. Keep the authority chain explicit for node Cases

The HITL1 Case invokes the existing HITL1 production branch and its no-tool bridge. The Wave0
Case invokes the existing Wave0 worker branch and its bounded model/web bridge. In both cases:

1. the Case supplies trusted assignment and fixed fixtures;
2. the production bridge enforces actual model/tool/budget/cancellation behavior;
3. the node parser/validator/controller/ledger admits or rejects any candidate;
4. the Runner observes the result and writes a Bundle; and
5. the upper review assesses the Bundle against the Case Rubric without writing production state.

The initial Cases are node runs, not graph copies. Flow support remains a later lane using the
same Bundle protocol only after node baselines are useful.

**Alternative rejected:** construct a minimal copied model call inside `evals/`. That would
test a different prompt/bridge and falsely claim the production node was evaluated.

### 8. Reuse existing live seams through narrow adapters

Existing preflight, identity, model/web adapter, usage tracking, and branch request builders
may be extracted behind narrow interfaces. The new Runner owns the Bundle protocol, while
existing `evaluation-hardening` tests retain their own report/rubric contracts and selectors.
No new shared `utils`, `helpers`, or `common` module is introduced; any reusable contract
belongs to the owning `domain` or `runtime` layer.

Deterministic contract tests use fake model/tool boundaries only where the evidence claim is
structural. The two selected smoke Cases use real production node branches and explicit live
preflight; a single provider failure is a failed Bundle, not a skipped quality claim.

**Alternative rejected:** move all existing live calibration code into the new suite in one
flag-day migration. That would widen scope, change established evidence semantics, and make
it difficult to prove that old deterministic/live lanes remain unchanged.

### 9. Enforce Local-First data and privacy boundaries

V1 uses a fresh private local run directory for every execution and keeps full local inputs,
outputs, logs, traces, and artifacts available for review. `evals/runs/` is ignored by Git and
is not a shared checkpoint namespace. Portable redaction is not required for this private
evaluation lane; any user-facing support summary remains a separate product contract.

The Runner still avoids secrets and hidden reasoning in its structured diagnostics and honors
existing provider/runtime policies. A future export/redaction layer must not mutate the V1
Bundle in place.

### 10. Synchronize structural governance with implementation

Because the new paths are structural, apply tasks must update the project-structure delta,
`project-structure.toml`, architecture checker fixtures, generated `deerflow_research/AGENTS.md`
locator where applicable, and `.gitignore` together. A clean checkout must not require or
create `evals/runs/`; explicit Runner execution creates it. Existing `tests/eval/` remains in
the deterministic selection and is not a compatibility alias for `evals/`.

## Risks / Trade-offs

- **A provider outage produces a failed Bundle and no automatic retry** → Preserve detailed
  typed preflight/phase diagnostics and make a fresh explicit invocation cheap to start;
  never relabel the outage as a cognitive result.
- **A large local Bundle consumes disk space** → Keep the run store ignored and provide
  explicit operator inspection/cleanup later; do not silently delete evidence before review.
- **Reviewers disagree on one execution** → Keep each Review Record immutable and retain the
  exact Rubric/Protocol versions so disagreement is visible rather than overwritten.
- **A control artifact is edited after a run** → Record content/version identity in the Bundle,
  resolve those exact identities at review admission, and require the Review Record to reference
  them; a stale or substituted reference is invalid.
- **A retained Bundle is changed or incomplete after publication** → Reload its manifest and
  verify every declared digest before review; reject the review input without converting that
  integrity failure into a cognitive result or a Runner retry.
- **The new Runner duplicates existing live adapters** → Extract only narrow interfaces and
  leave existing tests/scenario ownership intact; architecture and import checks reject a
  generic shared helper layer.
- **Operators mistake a node smoke for a full research proof** → Make Case subject and
  authenticity explicit in the manifest and Review Protocol; V1 has no Flow Case or outcome
  acceptance claim.

## Migration Plan

1. Add the new `cognitive-evaluation-suite` and `project-structure` delta specs, then register
   their requirement ids through the normal governance path.
2. Add the governed runtime evaluation package and typed Case/Bundle/Review Record contracts;
   first make deterministic schema, isolation, immutability, and no-auto-trigger tests fail.
3. Add `evals/control/` with the review protocol, registry, and exactly two initial node Cases;
   add the ignored `evals/runs/` root without materializing a run in a clean checkout.
4. Implement the one-shot Runner and explicit review adapter using narrow production branch
   seams. Keep the existing test/live calibration runners and selectors unchanged.
5. Add deterministic tests for Case rejection, fresh identities, timeout/cancel/failure
   observation capture, Bundle finalization, Review Record references, and control/run path
   separation. Add bounded selected-live smoke entrypoints for HITL1 and Wave0 with strict
   model/web preflight.
6. Run the required deterministic verification, architecture checker, focused Runner tests,
   and strict OpenSpec validation. Execute a real smoke Case only when its credentials and
   bounded budget are explicitly available; record its Bundle reference, not raw provider
   text, as operational evidence.

Rollback is deletion or archival of the new suite paths and control registrations; it does
not touch production checkpoints, node routes, or existing test reports. A failed or partial
Runner implementation is not repaired by replaying an old Bundle: correct the implementation
and start a new isolated invocation.

## Open Questions

- Which additional node branches should become V1 smoke Cases after the HITL1 and Wave0
  baselines are stable? This does not change the Runner or Bundle contract.
- When should a bounded Flow Evaluation Run be admitted, and what flow-level Rubric is
  necessary to avoid overclaiming Research Outcome quality? This is a later capability delta.
- What portable redaction/export format is appropriate for a future Support Handoff? It is
  intentionally outside the private Local-First evaluation record.
