## Why

A real Wave1 run left 28 `targeted_search` open questions with no way to turn them
into retrieval work (BUG-028), and an invalid Wave1 critic result disappears without
any Journal fact (BUG-029). Both failures live on the same Wave1 review→gate seam:
the gate promises a targeted-search repair path that creates no work, and the critic
dispatch that feeds the gate fails silently. One program change closes both bugs.

## What Changes

- **WS1 (BUG-029):** a failed Wave1 critic dispatch — agent-invocation failure or an
  invalid typed result — SHALL record one bounded, safe, observation-only Journal
  fact (closed critic kind, `post_candidate` stage, canonical code collection,
  work/attempt correlation) instead of a silent `continue`. No route, retry,
  admission, or lifecycle authority changes.
- **WS2 (BUG-028):** the Wave1 gate stops promising a repair it cannot deliver. Every
  `targeted_search` open question SHALL be projected from the validated review into a
  bounded, gate-owned checkpointed field (`wave1_open_questions`); the gate passes when
  source floor and critic presence hold. Wave2 synthesis SHALL receive that projection
  as trusted model-visible assignment and dispose every question deterministically:
  exactly one searchable gap (new bounded `GapRecord.source_questions` refs) or an
  explicit resolution (new bounded `SynthesisResult.resolved_questions`). A coverage
  failure enters the existing one-shot structured repair and then the existing
  blocked/exhausted terminal. Retrieval still flows through the unchanged
  `wave2 gate → evidence_needed → targeted_evidence` loop; topology is unchanged.
- The `targeted_evidence` real node SHALL return the validated `WorkUnitGateView` on
  every visit — including an empty-gap visit — fixing the
  `work_unit_gate_view_inconsistent` red line that blocks any routed gap work.
- The stale red test `test_real_wave1_review_gate_enforces_question_floor_and_review_integrity`
  SHALL be rewritten to the new contract (projection + pass), and the scripted-real
  debug baseline SHALL gain the repair/targeted named case reserved by the closed
  `narrow-scripted-real-workflow-debug-path` plan.
- BUG-028 and BUG-029 backlog cards close with this change; the removed
  `wave1_open_question_disposition` repair rule stays removed (the mitigation becomes
  the specified handoff contract).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `wave1-node`: the Wave1 gate contract replaces the unanswered `targeted_search`
  repair promise with the bounded handoff projection (WON-004 modified, WON-013
  added), and the Wave1 post-candidate Journal coverage extends to the critic review
  dispatch boundary with a closed critic kind (WON-012 modified).
- `wave2-synthesis-node`: synthesis SHALL dispose every projected Wave1 question
  through a searchable gap or an explicit resolution with deterministic coverage
  validation and the existing bounded repair/terminal path (WSN-009 added).
- `run-event-journal`: the current v3 RunEvent contract gains one bounded optional
  `critic_kind` field usable only by Wave1 critic-boundary validation facts (REJ-008
  added).
- `targeted-evidence-loop`: the real targeted_evidence node SHALL conform to the
  work-unit gate-view protocol on every visit, including empty-gap visits (TEL-007
  added).

## Impact

- `deep_research_harness/src/deerflow_deep_research/domain/wave1.py`,
  `domain/synthesis.py`, `domain/state.py`, `domain/run_observation.py`,
  `domain/invocation.py` (recorder protocol keyword)
- `deep_research_harness/src/deerflow_deep_research/graph/nodes/gate_adapter.py`,
  `graph/nodes/wave1/review.py`,
  `graph/nodes/wave1/node.py`, `graph/nodes/wave2_synthesis/node.py` and `prompts.py`,
  `graph/nodes/targeted_evidence/node.py` and `subgraph.py`,
  `runtime/run_observation.py` (recorder accepts `critic_kind`),
  `runtime/work_unit_store.py` (bounded accepted open-question read)
- `deep_research_harness/tests/integration/test_wave1_work_units.py`,
  `tests/unit/test_wave1_review.py`, `tests/graph/test_wave2_synthesis_real.py`,
  `tests/integration/test_scripted_real_workflow_debug.py` plus the scripted-real
  fixture scenario, and `openspec/governance/req-registry.yaml` (pending IDs)
- `_backlog/bugs/BUG-028-*` and `_backlog/bugs/BUG-029-*` cards close at archive
- No graph topology, route-map, gate-budget, or targeted-gap-router contract changes.
  Ordinary downstream work neither modifies nor source-browses the `deerflow/`
  gitlink; this change owns no DeerFlow interface.

## Program Focus

- **Program outcome:** Every Wave1 `targeted_search` open question reaches a bounded,
  traceable retrieval disposition (a searchable synthesis gap routed through the
  existing targeted-evidence loop, or an explicit resolution), and every failed Wave1
  critic dispatch leaves a bounded, safe, observation-only Journal fact.
- **Candidate / obligation budget:** REJ-008, WON-012, WON-013, WON-004, WSN-009, TEL-007
- **Declared workstream order:** ws1-critic-observability, ws2-question-handoff
- **Program decision authority:** Program authority approves only the frozen scope,
  declared order, and whole-program archive closure. It owns no gate, review,
  synthesis, Journal, state, route, or lifecycle fact.
- **Shared archive invariant:** The Wave2 gate remains the sole route authority for
  gap work; the Wave1 gate keeps its unchanged `{PASS, REPAIR, BLOCKED}` route map
  with repair reserved for source-floor and critic-presence failures; Journal facts
  remain bounded observations with no control effect; deterministic materializers
  remain the only admission owners; topology is unchanged.
- **Program failure / recovery:** A workstream that cannot close its declared evidence
  stays active for approved forward repair, rollback, or plan-level re-scope; neither
  workstream archives independently. The whole change archives only when both bug
  cards close with their red lines green.
- **Split / expansion rule:** No topology change, new Wave1 repair route, change to
  the `targeted-evidence-loop` gap-router input, gate budget/fatigue change, new
  Journal authority, or `deerflow/` change enters scope. Anything beyond the frozen
  budget requires a later change with its own proposal.
- **Not in scope:** Wave1 worker/repair cognition, Wave0 behavior, hitl2/readiness/
  final-delivery semantics, unresolved-gap ownership, live model quality claims,
  credentialed evidence, or the `deerflow/` gitlink.

### Workstream Focus: ws1-critic-observability

- **Primary module / causal owner:** `graph/nodes/wave1/review.py` review dispatch
  (`build_wave1_gate_review` → `_dispatch_missing_reviews`); it owns whether a failed
  critic dispatch emits a bounded observation.
- **Seam classification:** deterministic-guardrail because the critic bridge result
  either validates into an artifact or emits a closed observation; no model-visible
  behavior, route, or lifecycle authority changes.
- **Question:** How can each failed Wave1 critic dispatch (invocation failure or
  invalid typed result) record one bounded, safe, observation-only Journal fact —
  fixed critic kind, validation stage, closed canonical codes, work/attempt
  correlation — without retaining raw output or gaining control authority?
- **Necessary adjacent/external contracts:** `run-event-journal` — which RunEvent v3
  fields may carry a Wave1 critic-boundary fact and how `critic_kind` stays optional
  everywhere else; `RunEventRecorderProtocol` — how the recorder already reaches the
  wave1 node can thread into the review dispatch without a new controller.
- **Evidence seam:** `tests/integration/test_wave1_work_units.py` with scripted
  invalid critic payloads and a recorder spy asserting the exact Journal fact; unit
  coverage for the closed canonical-code mapping in `tests/unit/test_wave1_review.py`.
- **Not in scope:** critic retry policy, repair prompts, admission, routing,
  lifecycle authority, worker initial/repair validation events (already covered by
  WON-012), raw output retention, or participant-facing surfaces.
- **Triggered review policies:** local-context, authority-and-projections, workflow-outcome-review
- **Candidate / obligation IDs:** REJ-008, WON-012
- **Target / retirement:** Target is the correlated `post_candidate` VALIDATION fact
  and the closed MODEL_TOOL invocation-failure fact for the critic boundary. The
  silent `except ValueError: continue` retires: the dispatch still continues, but
  only after a best-effort observation.
- **Surface grade:** Journal events are persisted observation surfaces, never
  lifecycle, route, or admission sources.
- **Decision authority:** Wave1 Review Owner defines the closed canonical codes and
  the critic-kind mapping; Observation Owner owns the RunEvent v3 contract. Program
  authority owns neither.
- **Negative path / recovery:** An absent or failing recorder SHALL NOT crash the
  gate path — observation is best-effort and the dispatch keeps its existing bounded
  control flow. A failure to record never changes admission, gate verdict, route, or
  terminal disposition.

#### Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Critic agent invocation fails with a known safe provider cause | `_dispatch_missing_reviews` records a closed MODEL_TOOL failed fact (failure/provider category only) | Wave1 Review Owner records and continues; no new retry | No terminal; the gate's existing `wave1_review_presence` repair loop re-dispatches on the next visit | Operator reads the Journal fact; no admission or route changes | Scripted invocation failure in `test_wave1_work_units.py` asserting the exact recorded fact |
| Critic typed result fails the review-artifact validation boundary | `_dispatch_missing_reviews` records one `post_candidate` VALIDATION fact with canonical codes and closed critic kind | Wave1 Review Owner records and continues; no repair request receives the code | No terminal; artifact stays absent and the existing gate repair loop owns the outcome | Operator reads the Journal fact; no submission or route is published | Scripted invalid critic payload asserting codes, stage, critic kind, work/attempt correlation |

### Workstream Focus: ws2-question-handoff

- **Primary module / causal owner:** `graph/nodes/wave2_synthesis` materializer and
  node — they own the deterministic disposition of every projected Wave1 question.
- **Seam classification:** cognitive-program because the synthesis prompt/context
  gains the bounded question assignment and the model must disposition each question;
  the deterministic coverage validator owns admission. Cognitive hypothesis: making
  `targeted_search` questions model-visible in the trusted assignment lets synthesis
  either ground an explicit resolution in accepted evidence or project one searchable
  gap per question; observable result: every projected question id appears in the
  materialized disposition or the candidate is rejected deterministically.
- **Question:** How do Wave1 `targeted_search` questions become bounded, traceable
  retrieval gaps with a deterministic coverage guarantee, without changing graph
  topology or the targeted-evidence gap-router contract?
- **Necessary adjacent/external contracts:** `wave1-node` — the gate contract and the
  review projection that must carry bounded question refs; `work-unit-kernel` — the
  `WorkUnitGateView` protocol the targeted_evidence node must satisfy; `targeted-evidence-loop`
  — `unresolved_gaps` consumption stays unchanged.
- **Evidence seam:** rewritten Wave1 gate/review integration tests (projection +
  pass), synthesis coverage unit/integration tests (prompt assignment present;
  missing, duplicated, or foreign coverage rejected; bounded repair then exhausted),
  targeted_evidence gate-view conformance tests (non-empty and empty gap visits), and
  the scripted-real repair/targeted named case reserved by the closed debug-path plan.
- **Not in scope:** graph topology, a new Wave1 repair route, TEL gap-router input,
  gate budgets/fatigue, Wave1 worker/repair behavior, hitl2/readiness/final-delivery
  semantics, or live quality claims.
- **Triggered review policies:** local-context, change-admission, control-placement, control-and-recovery, node-agent-workflow-integrity, workflow-outcome-review, authority-and-projections
- **Candidate / obligation IDs:** WON-013, WON-004, WSN-009, TEL-007
- **Target / retirement:** Target is the gate-owned `wave1_open_questions` projection
  → synthesis question disposition → existing Wave2 searchable-gap routing. The
  removed `wave1_open_question_disposition` repair rule stays retired, and the stale
  red test expectation retires in favor of the projection contract.
- **Surface grade:** `wave1_open_questions` is a checkpointed control field, and
  `GapRecord.source_questions` / `SynthesisResult.resolved_questions` are persisted
  artifact fields — bounded authority surfaces, never route or lifecycle authority.
- **Decision authority:** Wave1 Gate Owner projects questions from the validated
  review; Synthesis Materializer Owner validates disposition coverage; the Wave2 gate
  remains the only route authority. Program authority owns none of those facts.
- **Negative path / recovery:** Coverage failure enters the existing one-shot
  structured repair with a closed category, then the existing blocked/exhausted
  terminal. An absent or empty projection keeps synthesis behavior unchanged
  (compatibility). A projection exceeding the frozen bound fails closed at the gate
  adapter rather than silently dropping questions. A targeted_evidence visit with no
  gaps returns a drained valid gate view instead of crashing the wrapper.

#### Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| `wave1_open_questions` checkpointed projection | No cognitive candidate; the projection is derived only from validated review rows and merged with the existing projection | Wave1 gate adapter writes with the GATE writer role through the existing `apply_research_update` seam, merging (dedupe by question id) so repair visits cannot drop earlier works' questions | non-bypassable | Only bounded validated question refs enter state; an over-bound merged projection fails closed; old checkpoints default empty | Reuses the gate-owned projection seam instead of a new writer or controller | Gate-adapter projection tests including merge, overflow, and empty cases |
| Synthesis question disposition (gap vs resolution) | The synthesis model proposes the disposition per question | The materializer coverage validator admits only complete, disjoint, non-foreign coverage; the Wave2 gate routes only searchable gaps | bounded-repair | Every projected question id is disposed exactly once or the candidate is rejected; no silent loss | Reuses the existing synthesis repair loop and Wave2 gate instead of a new route or gate rule | Synthesis coverage unit/integration tests (valid, missing, duplicate, foreign) |
| targeted_evidence gate-view conformance | No cognitive candidate; gap visits return the component-built reconciled view and gap-less visits return the canonical empty drained view | Wrapper validator admits the `WorkUnitGateView`; the node owns no route decision | non-bypassable | Gap and gap-less visits both satisfy the wrapper; the reserved key is never checkpointed | Reuses the shared work-unit component for gap visits instead of a targeted-only reconciled-view builder | Conformance tests for gap and empty-gap visits |

#### Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Synthesis output leaves a projected question undisposed or mis-attributed | Materializer coverage validator (`synthesis_question_coverage_invalid`) | One existing structured synthesis repair with a closed category; no new retry owner | Exhausted to the existing typed blocked terminal when repair fails | Operator inspects the Journal/terminal; no partial gap work is inferred | Coverage validator negative tests plus bounded repair/exhausted integration case |
| Synthesis still projects searchable gaps after targeted evidence | Wave2 gate searchable-gap rule and existing gate budget/fatigue | Existing Wave2 gate budget (`default_budget=1`) bounds the evidence loop | Exhausted to the existing typed blocked terminal | Operator reviews the run; retrieval stays bounded to one targeted round | Scripted-real repair/targeted named case asserting the bounded loop and terminal |
| targeted_evidence visit returns no gate view | Wrapper `work_unit_gate_view_inconsistent` (existing WOU contract) | Node returns the component-built view on every visit | Bounded node failure before gate evaluation (current red line becomes green) | Node re-run produces the drained/valid view | Empty-gap and gap-visit conformance tests |

#### Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Synthesis initial prompt gains the resolved Wave1 question assignment | node-agent | Which projected question is explicitly resolved by accepted evidence, and which becomes one searchable gap with scoped search dimensions | Trusted assignment = bounded `wave1_open_questions` id refs, verbatim question text resolved from accepted Wave1 result documents, topic registry, accepted submission refs | Zero-tool synthesis posture unchanged; the existing runtime bridge enforces it | `SynthesisResult` with per-question gap refs or resolutions; the materializer coverage validator is the only admission owner | Coverage failure = one closed-category repair then the existing exhausted terminal | Prompt-assignment unit test plus coverage validator and repair/exhausted integration cases |
| Synthesis repair receives the coverage failure | node-agent | The same bounded cognitive job corrects the draft to complete question coverage | Closed repair category only; no raw validator text or question body re-enters | Zero-tool repair posture unchanged | Repaired `SynthesisResult` re-validated by the same materializer | One repair attempt; failure exhausts to blocked | Repair integration case with a scripted corrected draft |
