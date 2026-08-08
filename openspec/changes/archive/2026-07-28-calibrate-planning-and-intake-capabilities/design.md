## Context

The capability contract already supports validated package-local Markdown policy,
required/legacy request bindings, and catalog projection. Wave0 has migrated local
policies, while topic planning and Wave1 are still explicit legacy branches. Existing
phase contracts already own parsing, materialization, work-unit submission, ledger
admission, route, and recovery. This change must make the research-start behavior
observable without introducing another controller or treating a model candidate as an
authority.

## Goals / Non-Goals

**Goals:**

- Move only topic-planning and Wave1 normal/repair requests into the next closed
  node-agent capability cohort; retain Wave0's existing binding.
- Calibrate six direct branches through the production node/runtime path with
  deterministic fake adapters: planner coverage and zero-tool posture; Wave0 1--3
  retrieval and honest degradation; Wave1 exactly-one new-source search; all repairs
  zero-tool and non-inventive.
- Register per-branch success and highest-risk evidence claims at the lowest stable
  planner or work-unit admission seam.

**Non-Goals:**

- No live-provider quality evaluation, claim truth assessment, source-quality score,
  graph topology, checkpoint schema, controller/retry redesign, or public interface.
- No Wave2 or targeted-evidence migration/calibration. Those remain the next change.

## Decisions

### Treat the research-start chain as one cohort

Topic planning produces the bounded topic registry consumed by Wave0, and Wave1
expands the Wave0 baseline. Their output contracts and artifact/ledger admission are
already separate, but their capability policies must jointly preserve the confirmed
profile-to-evidence handoff. Grouping them permits a focused mixed real-node proof
without pulling in downstream synthesis or critics.

Alternative: migrate all remaining legacy branches at once. Rejected because targeted
critics and Wave2 use a different assigned-evidence, zero-tool authority boundary;
their failure evidence would obscure intake faults.

### Keep candidate admission with existing deterministic owners

Each local policy explains a bounded cognitive job but carries no route, checkpoint,
ledger, parser, or recovery data. Existing `TopicPlan` parsing/materialization and
Wave0/Wave1 validation/controller/ledger paths remain the only authorities that admit
a candidate. Repair policies receive bounded draft/validation evidence and cannot
search or extend the assigned fact set.

Alternative: let capability metadata select a parser or controller. Rejected because
that would make static policy an authority and duplicate existing ownership.

### Evidence follows a branch and its highest risk

The global capability matrix gains exactly four rows, expanding its existing eight
rows to twelve. The four new topic-planning/Wave1 rows each have a normal and
highest-risk `REAL_NODE_FAKE_CAPABILITIES` claim at the production node seam. Wave0
retains its already registered matrix rows. Separately, the existing planner, Wave0,
and Wave1 `SCRIPTED_REAL_WORKFLOW` claims exercise the real bridge/tool path and are
revised only when their exact call-order or admission assertions need strengthening.
No matrix row may substitute for workflow proof, and no workflow claim may substitute
for a branch's matrix proof. Tests do not claim live language quality or source truth.

Alternative: prove the whole cohort with a single mixed-graph test or prompt snapshots.
Rejected because it cannot attribute a bad tool call, fabricated repair field, or
baseline-duplicate source to its producer.

### Keep existing recovery semantics unchanged

The change reuses each phase's existing typed failure and retry/repair ownership. It
adds no new retry or terminal route. A test that exposes a conflict must return the
change to design review rather than silently changing those bounds.

## Risks / Trade-offs

- [A scripted transcript can overstate live quality] -> Claims declare deterministic
  authenticity and assert only tool/order/admission boundaries.
- [Wave0 already has capability evidence] -> New claims distinguish calibration
  behavior from generic binding tests; they do not duplicate aggregate counts.
- [One cohort touches three node packages] -> Exact six-branch table and explicit
  non-scope prevent migration of targeted/Wave2 cases.
- [Tool fixtures leak authority] -> Runtime bridge is real; scripts fail on unexpected
  calls and deterministic validators/controller own all observable admission.

## Migration Plan

1. Add the four local declarations/resources and switch the corresponding builders
   from `legacy` to `required`; extend the closed matrix from eight to twelve rows and
   update catalog cases.
2. Add tests and central evidence metadata before changing behavior assertions, then
   implement the smallest policy/request fixes required by failing real-node cases.
3. Run focused tests and the complete offline deterministic gate; validate OpenSpec and
   evidence governance before archive. Rollback is a normal code revert: no persisted
   state or public API migration is introduced.

## Open Questions

None. Any discovered need to change graph routes, recovery bounds, or runtime tool
interfaces is out of scope and requires proposal/design revision.
