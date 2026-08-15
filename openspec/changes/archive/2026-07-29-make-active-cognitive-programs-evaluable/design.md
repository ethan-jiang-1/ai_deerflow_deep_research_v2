## Context

Change 1 made eleven node readers navigable; this change makes the six currently
active cognitive programs inspectable branch-by-branch. The following are verified
current facts, not new runtime behavior:

- `graph/prompt_catalog.py::prompt_catalog_cases` emits sixteen sorted synthetic
  direct-branch cases. `tests/graph/test_prompt_catalog.py` independently discovers
  direct `NodeExecutionRequest` builders and requires the catalog to cover them.
- `tests/assets/node_agent_capabilities.py::COHORT_EVIDENCE` has the same sixteen
  case IDs and current capability references. Its validator already rejects missing,
  duplicate, unknown, aggregate-substituted, and uncollected branch claims.
- `agents/phase_prompt.py::render_node_agent_prompt` is the pure final-prompt seam;
  `runtime/node_agent_bridge.py::RuntimeNodeAgentBridge` consumes that result and
  enforces the declared capability posture before model construction or tool dispatch.
- Each active node package owns its candidate parsing, admission, recovery, and
  feedback transition. For example, the existing Wave2 reader and handler record
  that a repair request receives draft/evidence but not detailed validation feedback;
  that limitation must be recorded, not repaired, here.

The progressive plan supplies the approved scope: all sixteen rows need composition,
feedback/loop, authority/guardrail, and evaluation-disposition evidence. It does not
turn a direct-call count into a product classification or a quality result.

The project requirement checker scans active delta headers as well as main specs. The
new CPE/NPC/NAC/NOA/EVH IDs therefore require registry entries before their first
agent-owned verification run. Registry registration establishes only ID ownership; it
does not promote the delta into a main specification or grant runtime behavior. The
unrelated committed `NRI-003` main-spec ownership drift was a full-gate precondition.
Under explicit user authorization, this change carries its minimal traceability
correction: restore the existing header ID and the existing reader inventory test's
`@impl` marker without changing reader behavior.

### External verification dependency

At planning time, `check_project_reqs.py` reported that the accepted
`node-agent-reader-interface` main-spec header omitted its registered `NRI-003` ID.
The explicit authorization above resolved that existing main-spec/registry
inconsistency at its lowest deterministic seam. It remains separate from the
cognitive-program ledger and does not weaken its requirement/evidence checks.

## Goals / Non-Goals

**Goals:** establish a typed test-owned ledger derived from the current catalog and
cohort denominator, deterministic composition and feedback proof, and an explicit
judgment-evaluation disposition for every direct branch.

**Non-Goals:** tune model quality, alter prompt/capability bodies, change bridge/tool
policy, candidate admission, recovery, route, lifecycle, or any deferred node.

## Decisions

### The ledger is a review projection, not an execution registry

`CognitiveProgramEvidenceRow` extends the existing test-owned capability-cohort
asset. Its `case_id` is a join key, not a selector: the exact set of row IDs MUST
equal both `prompt_catalog_cases()` and `COHORT_EVIDENCE`. Production code MUST NOT
import this ledger. The catalog continues to own only synthetic case construction and
the renderer continues to own only final prompt text.

Each row records the bounded question and product responsibility; trusted versus
untrusted input boundary; capability and catalog/render seams; requested tool window
and bridge-enforcement seam; feedback disposition, recipient when present, and source
seam; candidate and deterministic-admission owner; guardrail evidence; classified
evidence links; and evaluation disposition. Symbol references and central claim IDs
are links to their owners, never alternate authority.

The feedback disposition is one of: `delivered` (a bounded feedback datum reaches a
named later model request), `partial` (a named later request receives only the listed
subset, with the omitted datum recorded), or `absent` (no later model request receives
feedback). A repair trigger alone is not `delivered`. An `absent` row identifies its
source seam rather than inventing a recipient. The ledger does not change retry,
repair, terminal, or route behavior.

### Deterministic proof precedes judgment evaluation

Every row closes deterministic facts with separate evidence for composition/tool
posture, source-faithful feedback disposition, and candidate guardrail/admission. A
table-driven node/subgraph test may script the `NodeExecutionCapabilities` boundary
to capture requests, but it MUST exercise the production branch transition and assert
the ordered requests emitted by it; direct builder or parser calls are insufficient
feedback proof. A table-driven bridge test uses the real bridge with fake model/tool
bindings to prove the requested-versus-enforced posture without a provider.

The evaluation disposition is either `deterministic-sufficient`, accompanied by the
statement that this change asserts no model-quality claim, or
`judgment-evaluation-required`, accompanied by a bounded rubric, selected scenario or
live lane, and nondeterministic limit. The latter is introduced only for an actual
judgment claim discovered in the source/evidence audit; no live run is required to
prove a deterministic disposition. A generic parser mock is not agent-loop evidence.

### Evidence classification remains branch-local and non-destructive

Each ledger evidence link names one central claim and exactly one class:
`cognitive-program`, `deterministic-guardrail`, `wiring`, or `obsolete-duplicate`.
The validator rejects a missing case, duplicate case, unknown/uncollected claim,
wrong branch seam, aggregate substitution, missing required proof role, or an
unbounded judgment disposition. An obsolete duplicate remains linked to the existing
test and cannot be used to close a required role or authorize deletion in this change.

## Risks / Trade-offs

- [Ledger duplicates runtime authority] -> store links and evidence classifications only.
- [A branch aggregate hides a repair/diagnostic gap] -> exact equality to catalog and
  cohort IDs plus per-row proof-role validation.
- [A repair trigger is mistaken for feedback] -> assert ordered production requests;
  record `partial` or `absent` where the recipient does not receive the needed datum.
- [Live tests become a default] -> require a rubric and judgment-only rationale.
- [Evidence work becomes behavior tuning] -> reject prompt/tool/admission changes in review.

## Migration Plan

1. Register the new active-delta requirement IDs, then re-run requirement governance
   before introducing their `@impl` markers or evidence claims.
2. Re-discover the exact sixteen catalog/cohort branches and add red inventory and
   row-shape checks.
3. Extend the test-owned ledger and add deterministic composition, bridge, and
   source-faithful feedback proof without changing production authority.
4. Classify each branch evidence link and add only judgment evaluations whose claimed
   outcome cannot be settled deterministically.
5. Run focused gates and re-check requirement governance; run the complete gate and
   sync specs only after every row has a validated closure or explicit evaluation
   disposition.

## Verification Plan

| Proof obligation | Lowest responsible seam | Deterministic evidence | Boundary |
| --- | --- | --- | --- |
| Exact denominator and row shape | `COHORT_EVIDENCE` joined to `prompt_catalog_cases()` | Red invalid-fixture cases for missing, duplicate, stale, grouped, and mismatched rows | No production registry or prompt selection changes |
| Model-visible composition | `render_node_agent_prompt` plus catalog case | Case-by-case renderer/catalog assertions | Does not prove model judgment |
| Requested versus enforced tools | `RuntimeNodeAgentBridge` capability admission | Real bridge with fake model/tool bindings for every ledger case/posture | Does not resolve live configured tools |
| Feedback reachability | Existing node/subgraph branch transition | Ordered captured production requests, or an asserted `partial`/`absent` disposition | Does not alter repair/retry behavior |
| Candidate cannot gain authority | Existing parser/materializer/controller/ledger seam | Per-row linked collected guardrail claim | Does not test prompt quality |
| Judgment outcome, if asserted | Scenario or selected live evaluation asset | Rubric plus explicit nondeterministic boundary | Credentialed execution remains supplemental and is not run during planning |
