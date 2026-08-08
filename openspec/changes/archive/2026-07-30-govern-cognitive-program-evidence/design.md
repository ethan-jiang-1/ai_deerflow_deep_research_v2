## Context

See `proposal.md` for motivation and the three delta specs for the behavioral
contract. The current test-owned evidence system already has useful closed pieces:

- `LOGICAL_NODES` and `NODE_CONFORMANCE` cover eleven real logical nodes.
- The prompt catalog, `COHORT_EVIDENCE`, and `COGNITIVE_PROGRAM_EVIDENCE` cover
  twenty direct model branches.
- `MODEL_WORKFLOW_COVERAGE` currently discovers eight model-bearing node owners and
  binds each to success/failure workflow claims.
- The four calibration registries contain forty-one unique cases across all twenty
  branches; readiness owns three cases and every other branch owns two.
- `EVIDENCE_CLAIMS` and `REQUIREMENT_IMPACTS` own collected selectors, evidence
  metadata, responsible seams, and named risks.

Those pieces are validated independently. There is no single join that prevents a
node commitment, current reader projection, branch inventory, or selected proof from
contradicting the others. The existing reader checker validates shape but not the
readiness/final-delivery activation facts, and the activation dossier registry still
treats both fulfilled activations as unresolved.

Everything in this design is test-owned or a non-runtime reader projection. Production
state, checkpoints, artifacts, prompts, capabilities, tools, model calls, candidates,
routes, recovery, and lifecycle outcomes keep their existing owners.

## Goals / Non-Goals

**Goals:**

- Expose one reviewable object that closes the exact eleven-node and twenty-branch
  sets independently, joins all selected node proof to collected central claims, and
  joins every branch to its exact calibration cases and central live-claim selectors.
- Make the semantic node decisions explicit while deriving enumerable source facts
  from their current topology/catalog/workflow owners.
- Make future consolidation decisions prove risk preservation mechanically wherever
  possible and require bounded review rationale where evidence types differ.
- Correct current non-runtime readiness/final-delivery projections without changing
  their implementation.

**Non-Goals:**

- Move current production contracts into test assets or make the board importable by
  production code.
- Re-score evidence classes or define a universal ordering across unit, workflow,
  live, and release evidence.
- Consolidate, rename, move, relabel, or delete any test in this change.
- Modify the Agent Charter checker; the board validates evidence records, not OpenSpec
  proposal prose.

## Decisions

### 1. Add one board module that references existing branch rows and evaluations

Add `agent/tests/assets/cognitive_program_board.py` with immutable
`NodeEvidenceRow`, `NodeEvidenceLink`, `BranchEvidenceReview`,
`BranchEvaluationLink`, and `CognitiveProgramEvidenceBoard` records. The exported
board contains eleven node rows, references the existing
`COGNITIVE_PROGRAM_EVIDENCE` tuple for its twenty branch bodies, and adds one
branch-review wrapper per branch. It does not copy the request, feedback, guardrail,
or evaluation-disposition fields already owned by `node_agent_capabilities.py`.

Each node row declares the semantic fields that cannot be inferred from a call graph:
product responsibility, participation mode, commitment state, bounded hypothesis or
controller rationale, deterministic authority, live-evaluation applicability, and
known limitation. It also names exact direct branch IDs and selected central claim
links. Current mechanism and branch presence remain validated against source-owned
discovery/catalog data instead of being inferred from the semantic classification.

Each branch-review wrapper names the exact branch ID, its known limitation, and exact
`(calibration_case_id, central_claim_id)` links. Those links reference the four
existing calibration registries and their central live claims rather than copying
rubrics or selectors. The central calibration claims gain their already-known
`scenario_case_id` metadata so the join does not depend on parsing a pytest selector.
The existing owning validator for each calibration registry runs before the board
join; the board does not become a second owner of rubric, risk, or resource bounds.

Alternative considered: extend the already large
`node_agent_capabilities.py` with eleven more aggregate rows. Rejected because that
module owns branch capability evidence; mixing topology-level commitments into it
would make branch presence look like node identity and make the existing file harder
to review.

### 2. Validate the board as joins, not as a new authority

`validate_cognitive_program_board` receives the board plus injected current owners:
the logical topology names, parsed reader records, branch ledger and cohort rows,
model-workflow coverage, node conformance rows, central claims, requirement impacts,
the four independently validated calibration-case registries, and collected selectors.
The integrated gate runs each existing registry validator before this join. The board
validator then checks:

1. the node-ID tuple equals `LOGICAL_NODES` in topology order and branch IDs equal both
   catalog/cohort sets, with no missing, duplicate, stale, or grouped row;
2. the union of each node's branch IDs is exactly the branch ledger, and active-loop
   rows correspond to discovered workflow owners while controller/conditional rows do
   not claim branches;
3. node identity fields agree with the current reader projections, including current
   accepted readiness/final-delivery and conditional HITL2;
4. every selected node claim exists, is collected, belongs to the declared node proof
   purpose, and uses a closing classification allowed for that node context;
5. every active branch retains the existing composition, feedback, guardrail, and
   evaluation-disposition obligations, and has one exact review wrapper;
6. the calibration union contains exactly forty-one unique cases spanning all twenty
   branch IDs, and each branch evaluation link resolves to a calibration case whose `branch_id`
   matches, and to the unique collected central live claim whose `scenario_case_id`
   matches that case; the union of links equals the four calibration registries with
   no missing, duplicate, stale, or grouped case; and
7. every node and branch has an explicit live-evaluation applicability or limitation
   disposition at the level where it applies.

The reader loader will expose the existing title and six ordered identity fields as a
small immutable record while retaining `validate_reader_text` as the shape gate. A
mismatch fails review; neither the reader file nor the board supplies runtime facts to
the other.

Collection of a live selector establishes only that the declared evaluation case and
its provenance remain addressable. The board does not read a live report and therefore
cannot assert that the selector ran, passed, or established model quality.

Alternative considered: generate node rows entirely from `workflow.md`. Rejected
because product responsibility and commitment are approved semantic decisions, not
facts that a mutable Markdown title can self-certify.

### 3. Scope proof classes by node and active-branch context

Extend the shared evidence classification vocabulary with `human-decision`, while
making the allowed closing set context-sensitive. Node-board links may use
`cognitive-program`, `human-decision`, `deterministic-guardrail`, or `wiring` according
to the claim being made. Active-branch links continue to close only with
`cognitive-program`, `deterministic-guardrail`, or `wiring`; `human-decision` is rejected
there because a model branch is not a human choice. The existing
`obsolete-duplicate` value remains available only as a non-closing branch annotation
and can never satisfy a required board proof.

Active model owners require branch-local cognitive-program evidence plus their
deterministic admission/guardrail and workflow proof. HITL2 may use human-decision
classification only for collected proof of its conditional admission precondition and
no-current-interaction boundary; it uses deterministic proof for current autonomous
containment and cannot claim an implemented choice. Bootstrap and rerun use
deterministic-guardrail and wiring proof and are rejected if assigned an active
cognitive branch merely for uniformity.

Alternative considered: classify the whole node once. Rejected because one node can
have cognitive, wiring, and guardrail claims simultaneously; classification belongs
to the proof link, not the node identity.

### 4. Reconcile fulfilled activation projections in place

Keep `deferred_activation_dossiers.py` as the non-runtime home for unresolved
activation planning, but reduce its current denominator to the sole unresolved HITL2
record. Preserve the existing contract test selector while changing its assertions
and invalid fixtures to the one-row contract; archived OpenSpec artifacts retain the
fulfilled readiness/final-delivery dossier history.

Replace the dossier's exact `successor_change` reference with a fresh-change admission
boundary. The archived `introduce-hitl2-human-decision-experience` change records the
approved no-change disposition and cannot be an active successor. The remaining
dossier states that a future interaction is inadmissible until a genuine product
trigger is approved and a new separately reviewed behavior change owns the typed
decision and visible outcome; this change does not invent that future change's name.

Update readiness and final-delivery `workflow.md` fields and bodies to the accepted
current active critic/composer mechanisms and canonical `current accepted` commitment
state. Rebind readiness's stale `readiness-autonomous-continuation` node-conformance
success reference to the already collected `readiness-all-clear` current critic-path
claim. Retain the displaced claim and test because this change does not authorize
consolidation; final delivery's current `final-delivery-completed` node-conformance
claim remains valid.

Alternative considered: keep all three records and add an `activated` flag. Rejected
because they are explicitly activation dossiers with future preconditions; retaining
fulfilled rows in the current unresolved denominator would preserve the contradiction
the board is meant to detect.

### 5. Model consolidation as requirement-risk replacement, with an empty rollout

Add immutable consolidation decision records beside `RequirementImpact` in
`requirement_evidence.py`. A decision names one displaced central claim and exact
replacement links. Validation derives the displaced selector's requirement/risk pairs
from `REQUIREMENT_IMPACTS` and requires every pair to resolve to a collected retained
claim and impact entry. Self-replacement, unknown claims, uncollected selectors,
missing requirement ownership, or omitted risk pairs fail closed.

There is no numeric strength score. When seam, asset class, or authenticity differs,
the replacement must carry a bounded rationale explaining the metadata difference and
why the exact same requirement/risk pair remains proved at its responsible seam. This
avoids treating any evidence class or authenticity as universally stronger or allowing
deterministic evidence to claim model judgment.

The committed `CONSOLIDATION_DECISIONS` tuple is empty in this change. Its structured
basis admits only risk preservation, so a target count, directory, marker, or coverage
percentage cannot be represented as a valid decision. Invalid fixtures prove those
boundaries without deleting a real test.

Alternative considered: infer duplicates from equal selectors or similar test names.
Rejected because similarity does not establish identical risk, and the current claim
catalog already forbids conflicting selector identities.

### 6. Put the joins on the existing deterministic evidence gate

Extend `check_test_assets.py` to run the existing cognitive-program branch validator,
then the complete board validator and consolidation validator using the already
collected selector catalog. Add focused mutation tests for empty/mis-scoped source
sets, missing/grouped rows, false active-loop and Charter-binary identities,
under-specified programs, wrong-owner/class claims, missing or cross-branch evaluation
links, a self-consistent but mis-scoped calibration source, incomplete risk
replacement, and count-only consolidation.

The checker continues to report review metadata only. It performs no model, network,
runtime, graph, or artifact operation.

## Risks / Trade-offs

- [Static semantic rows can drift from approved specs] -> Compare them with reader
  projections and exact source-owned denominators, require explicit requirement-impact
  mappings, and fail the integrated checker on disagreement.
- [A passing board may be mistaken for model quality] -> Keep live-evaluation
  applicability and known limitations mandatory; validate selector provenance without
  treating collection as execution; branch judgment dispositions remain separate from
  deterministic composition and admission proof.
- [Risk equivalence cannot be fully automated] -> Require exact requirement/risk joins
  and explicit rationale for evidence-metadata changes; semantic approval remains a
  review decision rather than a fabricated score.
- [Retiring fulfilled dossier rows can appear to erase history] -> Keep their archived
  change artifacts as history and remove them only from the current unresolved
  projection; no production or test file is deleted.
- [The integrated checker becomes broader] -> Reuse its existing one-time collected
  selector catalog and pure validators; add known-violation smoke cases so an empty or
  mis-scoped source cannot pass.

## Migration Plan

1. Capture the current selector sets for every canonical deterministic, live, and
   release lane before implementation and require each post-change set to be a
   superset; keep every existing test selector intact without executing paid lanes.
2. Add the board and consolidation schemas with failing focused fixtures, then populate
   the eleven node rows, wire the existing twenty branch rows, and link every branch to
   its calibration cases and central live claims.
3. Reconcile the two reader cards, sole unresolved dossier, selected claim references,
   requirement impacts, and requirement registry.
4. Integrate the validators into the existing test-asset checker and run focused,
   complete offline, strict OpenSpec, and clean-boundary verification.

Rollback removes only test-owned board/consolidation records and restores the prior
reader/dossier projections. No runtime data, state, artifact, API, or migration requires
recovery.
