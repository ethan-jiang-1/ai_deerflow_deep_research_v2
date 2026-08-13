## Context

The selected product decision is recorded in the Stage 4 A-003 Option A review: a
case-linked Rubric has a narrow deterministic admission role, but it is not an
execution-quality input. See `proposal.md` for the incompatibility that this resolves.

Current `runtime/evaluation/controls.py` parses a source-controlled Rubric, verifies
its case identity/version and criterion-ID set, and rejects malformed or mismatched
cognitive-program declarations before a subject is constructed. This is evidence of
the current mechanism, not authority to make the specification follow code. The
current main CES and EVH requirements describe that mechanism incompatibly.

This change owns only the required-behavior reconciliation in the CES, EVH, and HITL1
deltas. EVH owns the Wave0/Wave1/Wave2 fixture contract, while `hitl1-node` owns the
equivalent HITL1 cognitive-program contract. It does not change the loader, typed
cases, fixtures, subjects, Runner, review service, tests, or the glossary/ADR language
that Stage 6 owns.

## Goals / Non-Goals

**Goals:**

- Give CES and EVH one precise boundary for the five distinct Rubric concepts:
  identity, criterion IDs, criterion content, model-facing execution input, and
  cognitive quality verdict.
- Preserve a single non-bypassable deterministic control: admission may validate the
  declared Rubric identity/version and unique criterion-ID set before constructing an
  execution subject.
- Keep content interpretation and all cognitive dispositions in the separately
  initiated review workflow; a Runner retains only `completed` or `failed`.
- Make later conformance review observe the real admission-to-subject/model handoff,
  rather than inferring the boundary from a parser unit test or a passing Runner test.

**Non-Goals:**

- Do not edit or otherwise ratify the current implementation, typed contracts,
  controls, fixtures, tests, prompts, or model-visible context.
- Do not treat criterion IDs as semantic scoring inputs, an execution result, or a
  replacement for a later review.
- Do not synchronize `CONTEXT.md`, ADRs, guides, or other terminology surfaces; Stage
  6 owns that post-decision work.
- Do not decide A-004, N-002, gitlink protection, or any DeerFlow behavior.

## Decisions

### 1. Use a five-part Rubric boundary

The deltas separate the following facts instead of using the unqualified phrase
"Rubric execution input":

| Rubric fact | Admission use | Execution/model use | Result authority |
| --- | --- | --- | --- |
| Identity and version | May be compared with the selected Case. | No. | Establishes control provenance only. |
| Unique criterion-ID set | May be compared with declared scenario IDs. | Non-model control metadata only; no quality interpretation. | Establishes closed-control integrity only. |
| Criterion prose, weights, thresholds, evaluator guidance | No. | No. | Review-only content. |
| Model-facing execution input | Not supplied by the Rubric. | N/A. | Owned by the declared Case/subject boundary. |
| Cognitive quality verdict | No. | Must not be emitted by the Runner. | Owned by the separate review workflow. |

This realizes the selected Option A without weakening the review-only boundary for
content and judgment. It rejects Option B because it would contradict the approved
need to deterministically reject mismatched cognitive-program controls before subject
construction. It also rejects a broad "metadata may be used during execution" rule,
because that would let criterion IDs become a gradual route for quality semantics.

### 2. Keep one deterministic admission evaluator and no competing quality controller

The declared Case plus source-controlled Rubric are the direct facts. The existing
admission seam is the one deterministic evaluator that may compare identity/version
and IDs before subject construction. The specification does not create a Runner-side
evaluator, a second registry, or a model-visible Rubric channel.

Parsing the source-controlled Rubric solely to derive identity/version and criterion
IDs is allowed admission semantics. Interpreting criterion prose, weights, thresholds,
evaluator guidance, or dispositions is not. This matches the proposal's
`non-bypassable` Control Placement Review posture and prevents an execution result
from competing with the review record.

### 3. Treat code as conformance evidence, with a hard handoff stop condition

On a separately authorized apply, inspect the concrete path from registered Case and
fixture through subject construction to every model-facing input. The check must show
that the only Rubric-derived facts read at admission are identity/version and criterion
IDs, and that prohibited content or cognitive semantics do not cross into a subject,
model context, output, or Runner status. Criterion IDs may remain non-model
control-integrity metadata, but a subject must not interpret them as a score, quality
instruction, or verdict.

Existing tests that prove rejection of a malformed control or that a Runner returns
`completed`/`failed` are necessary but insufficient on their own: they may not observe
the complete handoff. If the actual path violates the selected boundary, stop
implementation-conformance work, record `DEFERRED-CODE-CHANGE` with evidence, and do
not edit code under this change. The accepted required behavior may still be synced
through the normal OpenSpec workflow only when the current/required gap is explicit;
the sync must not hide it.

### 4. Delay terminology propagation until the behavior authority is settled

CES and EVH own observable required behavior. `CONTEXT.md` and ADR applicability
wording are not parallel authorities, so this change leaves them untouched. Stage 6
can apply the accepted terms after both A-003 and A-004 are settled, while explicitly
disclosing any deferred implementation gap.

### 5. Keep unrelated conflicts isolated

The Bundle-loss diagnostic conflict (A-004) and policy-cardinality residual (N-002)
have different owning specs and decisions. Adding either to this change would make the
five-part Rubric boundary less reviewable and violate the admitted Focus Card scope.

## Risks / Trade-offs

- **"Metadata" becomes a broad execution exception** -> The deltas enumerate the only
  allowed facts and prohibit every form of criterion content, model-facing input, and
  cognitive disposition. Apply evidence must inspect the real handoff.
- **A requirement says content is absent while the current subject carries it** -> Do
  not edit code to force conformance. Stop, record `DEFERRED-CODE-CHANGE`, distinguish
  required from current behavior, and leave affected follow-up to a separately
  authorized implementation change.
- **Criterion IDs are mistaken for scoring or result data** -> The Runner requirement
  explicitly retains only `completed`/`failed`; the delta names review as the sole
  cognitive-result authority.
- **The four cognitive-program families drift apart** -> HITL1 and EVH apply the same
  criterion-ID wording and malformed-control boundary to their respective family
  requirements, while preserving each family's existing corpus constraints.
- **Early glossary/ADR edits create a third answer** -> Stage 6 remains the sole
  terminology synchronization owner. This change deliberately leaves those files out
  of scope.
- **A passing structural check is overstated as semantic proof** -> Record validation
  and tests with their limited proof scope; require manual handoff inspection and
  per-adjustment observed-side-effect evidence before archive.

## Migration Plan

1. Obtain separate apply authorization and re-establish the repository, active-change,
   and DeerFlow-gitlink baseline without opening DeerFlow source.
2. Create a Stage 4 apply-time Adjustment Record that restates the exact before/after
   wording, risk, possible side effects, control, and evidence boundary.
3. Inspect the local registry-admission-to-subject/model handoff. Stop and defer a
   code gap if prohibited Rubric content or quality semantics cross the boundary; do
   not add a test or implementation change under this alignment-only authorization.
4. Apply and validate only the CES/EVH/HITL1 delta requirements, then use the normal
   OpenSpec sync/closeout workflow if the authorization and conformance evidence permit
   it. Do not directly edit main specs.
5. Run focused deterministic evidence and the existing full verification gate. Record
   outcomes and proof limits in the Stage 4 record.
6. Obtain separate archive authorization. Before archive, re-review this change's
   Control Placement Review, unresolved tasks, and the handoff evidence; add any
   actionable finding as an unchecked task.

Rollback of the planning artifacts is not an implementation recovery mechanism. Before
spec synchronization, the active delta can be revised or abandoned. After a normal
sync, a corrective OpenSpec change is required; historical change artifacts are not
rewritten.

## Open Questions

- At apply time, as complete fixtures and scenarios pass through the subject adapter,
  does any subject or model-facing consumer interpret `review_criteria` as quality
  semantics, or carry Rubric-derived prose or other quality semantics across the
  concrete handoff? This is a conformance question, not a new product decision:
  conformance permits the no-code sync path, while a violation triggers the
  predetermined `DEFERRED-CODE-CHANGE` stop condition.
