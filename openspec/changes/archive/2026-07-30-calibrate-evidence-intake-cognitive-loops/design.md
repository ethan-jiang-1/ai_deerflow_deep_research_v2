## Context

See [proposal.md](proposal.md) for motivation. Source audit confirms that Wave0 has
one required-retrieval source-intake worker with a one-to-three request tool window
and a separate zero-tool repair, while Wave1 has one baseline-aware retrieval worker,
one zero-tool repair, and two post-acceptance zero-tool critics. Their typed
candidates are validated and admitted by existing work-unit, review-artifact, and
gate owners. The immediately preceding calibration introduced a twelve-case
intake/planning corpus and typed live-rubric projection whose fixed collection must
remain intact.

Current code does not yet provide the proposed repair-feedback context:
`build_wave0_repair_prompt()` and `build_wave1_repair_prompt()` accept only a draft
and retained tool results, and their subgraph call sites pass only the initial result
summary and untrusted tool results. The original assignment and any validation
category are therefore pending wiring, not a current behavior. The existing
`intake_planning_live.py` runner also hard-codes model-only preflight and supplies no
web adapter, so it cannot serve as the live execution seam for tool-bearing worker
cases. Focused canaries demonstrate a separate real model-and-web bridge seam, but
their canonical collection is not part of this change.

The existing repair seams are intentionally narrower than general deterministic
submission validation. Wave0 invokes its zero-tool repair only when the initial
summary cannot parse into `Wave0WorkerOutput`. Wave1 invokes it only when its initial
summary cannot parse into `Wave1WorkerOutput` or fails
`validate_wave1_worker_output()` before artifact persistence. In contrast, the shared
work-unit submit path catches a post-candidate `SubmissionValidationFailure`, records
the existing `VALIDATION_FAILED` terminal update, and lets its retry allocation and
gate path decide the next outcome. That later failure, its codes, and later artifact
validation are not inputs to either repair prompt and this change does not add a
second repair seam.

The typed evidence-v1 report currently validates a rubric result by looking up only
the intake/planning corpus index. Compatible report reuse therefore also requires a
closed two-corpus case resolver: it must resolve a rubric result only to its owning
known corpus and reject duplicate or cross-corpus identities, while preserving
readability of older evidence-v1 reports that have no rubric result.

## Goals / Non-Goals

**Goals:**

- Make each of the six existing Wave0/Wave1 branch policies expose its bounded source
  or evidence judgment criteria before deterministic admission.
- Add a separate, auditable calibration corpus with deterministic conformance proof
  and selected supplemental live judgment evidence.
- Preserve current candidate contracts, runtime tool enforcement, work-unit/review
  recovery owners, state/artifact writers, gate predicates, and route ownership.

**Non-Goals:**

- No retrieval-provider, runtime-policy, execution-budget, graph-topology, evidence
  schema, checkpoint, ledger, or gate redesign.
- No model-owned source truth, evidence acceptance, review-artifact publication,
  retry, terminal outcome, or route selection.
- No change to the prior intake/planning corpus, canonical live-canary collection,
  default offline verification lane, `backend/`, or `frontend/`.

## Decisions

### 1. Keep the evidence-intake corpus disjoint from the existing calibration corpus

The implementation will add a separately named twelve-case corpus rather than append
to the fixed intake/planning collection. It may factor test-only shared calibration
types, rubric validation, or runner helpers only if both collections retain their
own identities, exact branch denominator, and collection-specific validation. This
keeps the prior `EVH-018` twelve-case contract true and lets `EVH-019` govern the
tool-bearing evidence-intake cases without changing canonical canaries or the
reusable scenario registry. The compatible typed report path will use a closed
test-owned resolver over these two named corpus indexes, not an open registry or a
case-id prefix inference. It will require global case-id uniqueness and resolve the
branch/criterion tuple from the matching corpus; archive reports with no optional
rubric result remain readable.

Alternative considered: extend the existing collection to twenty-four cases.
Rejected because its exact six-branch/twelve-case identity is an approved contract,
and one mixed collection would obscure credential and tool-posture differences.

### 2. Calibrate policy pairs and critics without adding authority fields

Initial workers will receive their current trusted assignment/baseline and existing
tool posture. Before invoking each existing zero-tool repair at its current
pre-persistence seam, its Wave0 or Wave1 subgraph will construct a bounded repair
context with: (1) the same trusted assignment projection used by the initial request,
(2) the invalid draft and retained tool observations as untrusted data, and (3) one
compact subgraph-generated category. Wave0 selects that category only for an initial
parser/typed-structural-output failure; Wave1 selects it only for an initial parser or
`validate_wave1_worker_output()` local semantic failure. The category is a closed
mapping of that triggering seam, not a raw exception or a submission-validation code.
The assignment is only the same topic/baseline projection rendered by the initial
builder, not a raw `WorkSpec`, attempt identity, checkpoint, ledger, or accepted
record. Assignment and category constrain scope and correction only; they cannot
supply a candidate source, URL, title, fact, fetch observation, claim, reference, or
open question. Prompt composition will keep the trusted assignment/category separate
from the untrusted-data block. It will not expose a raw exception string, artifact
path, checkpoint field, ledger content, review/gate data, or route data. A
post-candidate `SubmissionValidationFailure` and later artifact validation remain
outside the repair path. Critics will continue to receive only accepted bounded
assignments. The policy changes will make
relevance, independence, baseline newness, claim provenance/counterevidence,
uncertainty, and review-only limits explicit; typed source, evidence, review, and
candidate contracts will not gain quality scores, acceptance flags, or lifecycle
fields. Focused deterministic tests will exercise the subgraph call site as well as
the prompt builder so this feedback cannot be specified but left unwired.

Alternative considered: pass the raw parser/validator exception to the repair prompt
or add model-authored quality/authority fields to worker or critic candidates.
Rejected because raw error text can leak unbounded data, and deterministic validators
and materializers must remain the only admission owners.

### 3. Prove branch boundaries deterministically; assess model judgment only in a selected lane

Focused deterministic tests will assert rendered request content, trusted/untrusted
input boundaries, request-level tool posture, bounded repair or critic assignment,
and no admission on an invalid candidate. The request's `minimum_tool_calls` and
`tool_call_limit` define the Wave0 1--3 and Wave1 exact-one windows; bridge middleware
enforces those request windows, while the capability/runtime policy supplies the
allow-list, containment, and broader execution budgets. The selected live cases will
invoke only the declared branch boundary, use one outer attempt, and carry explicit
bounds no wider than the current branch request and focused live policy. A dedicated
test-only evidence-intake runner will reuse typed report/rubric and preflight
primitives, but not the zero-tool-only intake/planning execution harness: selected
workers invoke their generated request through a real model-and-web bridge after
strict model/web preflight, while selected repair and critic cases invoke their
generated zero-tool request through a real model-only bridge after model preflight.
The runner parses each summary through its production branch parser and, for Wave1
workers and repairs, its local pre-persistence semantic validator; the generated
request's declared tool posture and resource bound are also hard invariants. A failed
bridge invocation, tool posture/bound, parser, or local validator is a failed live
run with no rubric result. For critic cases, a deterministic test-owned fixture may
construct only the prompt's accepted-assignment projection; it is neither a
`SubmissionRecord` nor a full-pipeline assertion. The runner neither expands
`LIVE_CANARIES` nor makes a full-pipeline quality claim. Only a structurally valid
candidate that misses a rubric receives `limited` or `inconclusive`, never a hidden
retry or production mutation.

Alternative considered: use fake capabilities to assign quality scores. Rejected
because they prove request composition and deterministic guardrails, not an external
model's source/evidence judgment.

### 4. Retain current recovery and publication owners

Wave0 and Wave1 subgraphs remain the owners of their distinct, pre-persistence
zero-tool repair seams. The shared work-unit submit validator/controller owns every
post-candidate `SubmissionValidationFailure`: it records the existing
`VALIDATION_FAILED` terminal update, then applies the existing retry allocation and
gate bound. It neither invokes a zero-tool repair nor passes validation codes or
artifact-validation details to one. `build_wave1_gate_review()` dispatches missing
critics while constructing its review; a failed invocation or malformed newly
dispatched result is suppressed and leaves no valid artifact. This is not a new or
guaranteed critic-retry mechanism. Existing stored-artifact integrity failures retain
their existing fail-closed behavior rather than being converted into dispatch
suppression. The existing review materializer retains identity binding and
review-artifact admission, and the existing gate retains its repair or blocked
outcome. Gates continue to consume their existing deterministic projection only. New
diagnostics and live rubric reports are test-owned evidence projections, not
checkpoint, ledger, artifact, gate, or route inputs.

Alternative considered: feed critic quality labels into the gate. Rejected because a
calibration rubric is non-deterministic supplemental evidence and cannot become a
new lifecycle predicate.

### 5. Update evidence metadata only where the new proof changes it

The implementation will register `WAN-008`, `WON-008`, and `EVH-019` before running
requirement governance. It will add only the affected prompt catalog, central
requirement-evidence, and cognitive-program evaluation-disposition metadata for
`wave0/worker`, `wave0/repair`, `wave1/worker`, `wave1/repair`,
`wave1/source-diagnostic`, and `wave1/claim-verifier`, with focused checker tests.
The two worker-to-repair feedback rows will describe the bounded assignment/category
delivery and omit raw parser and post-candidate validation details. The ledger will
describe the escalation boundary but will not gain a model result or live-claim
authority field.

## Risks / Trade-offs

- [Tool-bearing live evaluation has credential and external-result variability] → use
  a dedicated real model-and-web branch runner, strict model/web preflight, one outer
  attempt, explicit bounds, bounded redaction, and a supplemental typed disposition.
- [A new corpus accidentally alters prior calibration governance] → validate both
  collection denominators/identities and the unchanged canonical canary count/budget
  in focused deterministic tests.
- [Richer source policy is mistaken for evidence acceptance] → retain explicit
  candidate-versus-admission language and real-node non-admission proof at the
  validator/controller/materializer seams.
- [Repair feedback leaks untrusted instructions or expands scope] → carry only
  bounded draft/observations through the untrusted-data boundary; keep the assignment
  and closed validation category outside it; exclude raw errors and authority-bearing
  state; constrain Wave0 to parser/typed-structural and Wave1 to parser/local-semantic
  triggers; and prove subgraph wiring, no-tool, no-invention, and downstream
  submission-validation non-entry behavior.
- [A trusted assignment or Wave0 baseline leaks into candidate evidence] → reuse only
  the initial request's bounded projection, never the raw work/record identity; let
  assignment/category constrain repair but not supply candidate entities; include a
  Wave1 baseline-injection highest-risk case.
- [A live rubric masks a failed branch contract] → require the real bridge's declared
  tool posture/bounds and the production parser/local semantic seam before rubric
  evaluation; a hard-invariant failure remains a failed live run with no disposition.
- [Critic prose is mistaken for a gate decision] → preserve identity-bound review
  artifact validation and test that malformed or out-of-assignment critics publish
  neither an artifact nor a route; do not describe missing-review dispatch as a
  guaranteed retry.

## Migration Plan

1. Register the three requirement IDs, add the separate corpus and live-selection
   contracts, then write failing deterministic request, repair-feedback, and boundary
   tests.
2. Revise only the six package-local capability Markdown files, prompt composition,
   and the existing pre-persistence Wave0/Wave1 repair-invocation wiring needed to
   render the accepted criteria; regenerate the prompt catalog.
3. Add focused real-node fake-capability and governance tests, then run the
   network-free verification target.
4. Run a selected live calibration only when branch-appropriate credentials are
   configured; record its bounded disposition as supplemental evidence without
   changing production state or canonical canaries.
5. Roll back by reverting policy and calibration/evidence assets together. No stored
   data migration or compatibility bridge is required.
