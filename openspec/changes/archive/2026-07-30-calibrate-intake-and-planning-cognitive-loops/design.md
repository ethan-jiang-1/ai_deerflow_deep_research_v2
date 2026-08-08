## Context

The current HITL1 and topic-planning branches are bounded zero-tool Node Agents with
validated typed candidates and deterministic admission. Their existing evidence
proves those boundaries, but it intentionally does not claim candidate judgment
quality. See [proposal.md](proposal.md) for the product motivation and review scope.

## Goals / Non-Goals

**Goals:**

- Make the six branch-local policies express the candidate-quality criteria that the
  product needs without widening their assignment or authority.
- Add a small, typed, labeled calibration corpus and an explicit live-evaluation
  rubric for the judgment claims that deterministic fixtures cannot establish, including one
  normal and one highest-risk case for each of the six branches.
- Preserve deterministic proof of rendering, zero-tool posture, bounded repair, and
  non-admission at the existing node and materializer seams.

**Non-Goals:**

- No new model branch, provider, tool, tool-call budget, retry/fallback policy,
  profile/topic schema, checkpoint field, route, or human-interrupt behavior.
- No source/research-quality claim, automatic production acceptance threshold, or
  default CI dependency on credentials or a model API.
- No Wave0, Wave1, Wave2, targeted-evidence, HITL2, backend, or frontend work.

## Decisions

### 1. Calibrate policy pairs, retain typed candidates and controllers

The initial and repair policies for each owner will share one core decision rubric.
Initial branches receive their trusted assignment; repair branches receive that same
assignment, the untrusted invalid draft, and compact validation facts. The existing
`StructuredBrief`, `SemanticCandidate`, and `TopicPlan` contracts remain unchanged.
This makes quality policy the first adjustment seam while retaining the existing
parser, semantic resolver, materializer, and graph handler as authority.

Alternative considered: add quality fields or scores to candidates. Rejected because
those fields would become new model assertions and tempt admission logic to treat a
score as lifecycle authority.

### 2. Use typed labels and rubric dispositions, not golden model text

The calibration corpus will provide exactly one normal and one highest-risk case for
each of the six branches (twelve cases total), with branch-local assignments,
adversarial/ambiguous inputs where applicable, expected constraints, and a short
rubric. A normal case exercises the branch's ordinary bounded assignment; its
highest-risk counterpart exercises the existing boundary named by the delta: advisory
brief versus research output, repair non-broadening, ambiguous reply, semantic-repair
ambiguity, degraded-profile planning, or invalid-plan non-publication. Live evaluation
will record a typed `pass`, `limited`, or `inconclusive` disposition with bounded
diagnostics. `pass` means every declared criterion was assessable and satisfied;
`limited` means the candidate was assessable but one or more declared criteria were
not satisfied; `inconclusive` means that the successful live run did not yield enough
admissible candidate evidence to assess a declared criterion. A hard-invariant or
execution failure remains the existing `LiveScenarioFailure`, not a fabricated rubric
disposition. The rubric will not compare arbitrary model prose to a golden output or
infer quality from JSON validity alone.

Alternative considered: make fake-capability fixtures assert a quality score. Rejected
because fixtures can establish the request and deterministic guardrails, not model
judgment.

### 3. Keep live quality evidence supplemental in a separate collection

The twelve live calibration cases are a dedicated test-only collection rather than
members of `LIVE_CANARIES` or the lane-neutral `ScenarioCase` registry. Each selected
test is marked `requires_llm`, retains a stable case id and branch identity, runs
through strict model-credential preflight, and reports its own rubric result. This
preserves the canonical six-canary count and deadline budget, and the existing
scenario registry's requirement that every family has deterministic closure. The
collection is excluded from `make verify` and normal deterministic selections; an
operator may select one case or the collection explicitly. A result cannot alter
profile acceptance, registry publication, or route behavior.

Alternative considered: add these cases to `LIVE_CANARIES` or the reusable scenario
registry. Rejected because the canary contract fixes six cases and a bounded job
budget, while the scenario registry requires deterministic family closure that a
live-only judgment corpus cannot supply.

### 4. Extend the test-only live report compatibly

`LiveScenarioReport` will gain an optional typed rubric-result projection for this
dedicated collection. A present result contains the stable case/branch identity,
the complete declared criterion identifiers, one `pass`/`limited`/`inconclusive`
disposition, and bounded redacted rationale. The result's case identity must equal
the report's scenario identity and its branch identity must resolve to the selected
corpus case. Each live case also declares an outer attempt, model-call, tool-call,
token, and timeout bound no wider than its existing zero-tool branch policy. The
evidence-v1 schema marker remains unchanged: an existing evidence-v1 archive without
this optional result reads as an absent result, while a new report validates it when
present. The report remains a diagnostic/evidence projection; it is not a candidate,
lifecycle fact, or admission input.

Alternative considered: store the judgment in `LiveOutcome.values` or a free-text
report field. Rejected because those values are not a typed rubric contract and a
free-text field could make bounded, redacted, branch-specific evidence unverifiable.

### 5. Update the evidence ledger only as a review projection

The six existing cognitive-program evidence rows will receive their judgment-evaluation
disposition, rationale, rubric, and nondeterministic boundary. The rows will not
gain a live-claim link because `CognitiveProgramEvidenceRow` has no such field and
the ledger only classifies its deterministic branch evidence. Central requirement
evidence separately records the live-evaluation escalation. Both registries remain
test-owned review metadata; neither selects a prompt, model, tool, candidate, or
lifecycle outcome.

### 6. Register new requirement identifiers before verification

The three added delta requirement IDs are registered in the project requirement
registry as the first implementation action, then verified by the registry checker.
This is a governance lifecycle update required by the new requirements, not an
alternative source of behavioral authority.

## Risks / Trade-offs

- [Live outputs vary across models and time] → bind each run to an explicit rubric,
  case identity, criterion ids, existing branch call limits plus declared outer
  bounds, model/runtime metadata already permitted by the live reporting contract,
  and a bounded inconclusive disposition.
- [Optional report field breaks existing archives] → keep the evidence-v1 marker,
  make the rubric result optional, and prove archive scans of pre-rubric reports.
- [Calibration silently expands release-canary cost] → retain the exact canonical
  canary collection/count/budget checks and keep the new cases in their separate
  `requires_llm` collection.
- [A richer policy broadens the model assignment] → retain the existing trusted-input
  lists, zero-tool binding, repair inputs, and deterministic parsers in focused tests.
- [Labeled corpus becomes an implicit product taxonomy] → keep labels local to the
  branch quality question and do not add them to checkpoint, profile, topic, or route
  state.
- [Quality wording is mistaken for an acceptance guarantee] → every rubric and
  evidence link names the nondeterministic boundary and keeps the deterministic
  admission owner explicit.

## Migration Plan

1. Register the three new requirement IDs, then add corpus types, labels, rubrics,
   report compatibility, and collected deterministic/live evidence claims.
2. Revise only the six package-local capability Markdown files and prompt composition
   needed to surface the accepted criteria.
3. Add focused deterministic rendering/repair/non-admission tests, then run the
   network-free verification target.
4. Run selected live calibration cases only with configured credentials; record their
   bounded dispositions without changing production state, canonical canaries, or
   rollout configuration.
5. Roll back by reverting the policy and corpus/evidence changes together. No stored
   data migration or compatibility bridge is required.
