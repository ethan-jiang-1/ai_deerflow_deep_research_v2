# Design: Honest Delivery Degradation and Faithful Real-Run Diagnostics

## Context

Three observed defects from the same two real mode-003 runs (BUG-035/036/037 in
`_backlog/bugs/`):

1. The wave2 gate treats budget exhaustion as a hard terminal: an honest searchable
   gap (wave1 open-question projection, or a missing precise figure) that two
   targeted rounds cannot converge kills the whole run at `wave2_synthesis`
   blocked — no report, no degraded artifact. Execution trace observed twice:
   `… wave2_synthesis → targeted_evidence → wave2_synthesis → targeted_evidence →
   wave2_synthesis → BLOCKED`.
2. That blocked terminal renders on the demo terminal as "Bundle 内 Event Journal
   记录不可用" while the same bundle's `diagnostics/` is complete and
   `soft-bundle inspect` reports `Journal health: complete`.
3. Every real run prints langgraph `Deserializing unregistered type …` warnings for
   exactly the three project types research checkpoints persist; a future langgraph
   will turn this into a hard recovery failure.

Relevant owners today: `engine/gate_kernel.py` (verdict derivation, step 8
escalates exhaustion → BLOCKED), `domain/gate.py` (`GateDefinition`),
`engine/real_gates.py` (wave2 gate + minimal-pair budget resolver = 2),
`graph/nodes/gate_adapter.py` (writes `unresolved_gaps`), readiness report plan
(`graph/nodes/readiness/materializer.py` + `contracts.py`), final report rendering
(`graph/nodes/final_delivery/composer.py` — already renders a
`## Uncertainties` section), `runtime/run_experience.py`
(`_failure_for_terminal` resolves journal fields only on the provider-diagnostic
branch), `runtime/checkpoint.py` (`build_deep_research_checkpoint_serde`
registers `ContentRef` + `AttemptStatus`), `runtime/bundle_lifecycle.py`
(`open_graph_checkpoint` opens `AsyncSqliteSaver` with the library default serde),
`runtime/graph_host.py` (already assigns the app serde onto its savers).

## Goals / Non-Goals

Goals:

- A minimal real-auto run with a non-converging honest gap completes and delivers
  a report that discloses the gap.
- Degradation is bounded and cannot loop; every other gate's semantics are
  byte-identical to today.
- Blocked terminals report journal availability from published facts.
- Checkpoint serialization crosses one explicit registered boundary everywhere.

Non-Goals (design-level):

- No provider/bridge hardening, no budget increases, no fatigue-rule changes.
- No new model role: disclosure is a deterministic projection; the readiness
  critic and final composer are untouched.
- No change to route labels or topology edges; a degraded pass reuses `pass`.

## Decisions

### D1 — Exhaustion-degradation policy lives on `GateDefinition`, not on `FailureCode`

`FailureCode.MISSING_EVIDENCE` is shared by wave1's review-presence rule and
others; making its classification `degradable` would change wave1/final semantics.
A boolean `degraded_pass_on_exhaustion` on `GateDefinition` scopes the policy to
exactly the gates that opt in (only the real wave2 gate does). The kernel branch in
`evaluate_gate` replaces the step-8 escalation only when ALL of: budget ≤ 0, no
hard failure among collected failures, policy declared, and the phase's
`exhaustion_degraded` marker absent from `degraded_decisions`. Verdict becomes
`PASS` with `degraded=True`; no `REPAIR_BUDGET_EXHAUSTED` failure is appended
(the run did not terminally fail), `remaining_budget` stays 0, and
`gate_result_to_state_update` appends `f"{phase}:exhaustion_degraded"` to
`degraded_decisions` (GATE-owned writer, `last_write_wins`, field already declared
in `domain/state.py` and currently unwired — this change gives it its first
writer/reader, its named purpose).

Alternative rejected: per-`Failure` "exhaustion-degradable" classification —
requires new classification plumbing and still needs a gate-level opt-out for
final_delivery; strictly more surface for the same behavior.

Alternative rejected: resolving degradation in the wave2 node — the node does not
own budget/verdict authority; the gate kernel does (architecture: nodes → engine).

### D2 — Once-per-seeding bound via `degraded_decisions`, reset by the rerun planner

The observed failure mode is a gap that provably does not converge; an unbounded
degrade → readiness-repair → wave2 → degrade cycle would burn cost forever. The
marker makes degradation happen at most once per phase per budget seeding:
- Re-visit with the same gaps → marker present → BLOCKED (today's semantics).
- Re-visit with changed gaps → marker present → BLOCKED as well: after one honest
  degraded delivery, further non-convergence is terminal, which is the bounded
  promise.
- A genuine later repair round (hitl2 → rerun, or a refinement round) goes through
  `reset_gate_state_for_scope`, which already clears `gate_attempts_by_phase` and
  `repair_budget_by_phase`; it gains `"degraded_decisions": ()` so a fresh round
  regains exactly one degradation opportunity. The reset update flows through the
  same GATE-writer path the budget resets already use.

Alternative rejected: fingerprint comparison against `latest_gate_feedback`
(`previous.degraded and same fingerprint`) — `latest_gate_feedback` is a single
slot shared by all phases and is overwritten by interleaved gated phases; the
bound would be order-dependent. The state field is order-independent and testable.

### D3 — Disclosure projection: gap ids from state, gap bodies from the canonical artifact

`unresolved_gaps` (ids only) is already gate-written and checkpointed; the wave2
spec forbids gap bodies in checkpoint state. Readiness therefore joins those ids
against the bundle store's canonical `synthesis/findings.json` via one new bounded
read on `WorkUnitStore` (symmetric with `read_synthesis_evidence`; same canonical
bytes, size-bounded, hash-verified path). Matching `search_required=true` gaps
become `ReportPlanUncertainty` entries (bounded description + gap id); a recorded
id with no body still yields an uncertainty naming the id (no fabrication, no
silent drop). Empty `unresolved_gaps` → zero added uncertainties. The final
composer needs no change — its uncertainties section renders the plan as-is.

### D4 — Journal truth generalizes off the provider-only branch

`_failure_for_terminal` keeps its structure but resolves
`diagnostic_location`/`journal_record_created` for every blocked incident that has
a diagnostic reference, using the existing observation-view verification
(`_provider_diagnostic_location`, renamed `_incident_diagnostic_location`; same
check: session available + bundle match + exact reference match). The
`RunFailure` invariant (`journal_record_created == (diagnostic_location ==
"bundle_journal")`, enforced in `domain/run_experience.py`) is preserved; no
renderer change is needed — demo_real already prints availability from these
fields, so a faithful projection fixes the terminal output with zero
presentation-layer edits.

### D5 — One serde boundary: allowlist completion + saver wiring

Two mechanical fixes: (a) `build_deep_research_checkpoint_serde` registers
`("deerflow_deep_research.domain.wave1", "Wave1OpenQuestionRef")` — the persisted
project types are exactly `ContentRef`, `AttemptStatus` (aliased `WorkStatus`),
and `Wave1OpenQuestionRef`; gate views/reviews are popped from node results before
the checkpoint write, and terminal-failure/attempt dicts are normalized to plain
models by their reducers; (b) `open_graph_checkpoint` assigns
`build_deep_research_checkpoint_serde()` onto the opened `AsyncSqliteSaver`
(`saver.serde = …`, the same pattern `graph_host._saver_context` already uses —
`from_conn_string` takes no serde argument in the pinned langgraph). Strict mode
(`LANGGRAPH_STRICT_MSGPACK=true`) stays failing-closed for everything else; the
strict-checkpoint Make lane gains the graph-execution tests that build real
research states so the registered set is proven complete under strict mode.

## Risks / Trade-offs

- [A degraded wave2 pass reaches readiness whose critic may still route
  `repair_targeted` for an uncovered must-answer question] → that loop re-enters
  wave2, which now BLOCKS on the marker (D2); the cycle is bounded to one extra
  targeted round, identical to today's worst case minus the premature death.
- [Marker write adds a gate state field consumers must tolerate] → the field
  already exists in `ResearchState` with GATE ownership and a `last_write_wins`
  reducer; no schema change, no new writer role.
- [Report gains uncertainties the operator did not see in 002 scripted runs] →
  only when `unresolved_gaps` is non-empty; clean runs render exactly as before.
- [Registering a type too narrowly could miss a future persisted type] → the
  strict-mode lane fails closed the moment an unregistered project type appears,
  which is precisely the alarm BUG-037 asks for.
- [AsyncSqliteSaver serde assignment timing] → assigned immediately after the
  saver context opens and before any graph compile/invocation uses it, mirroring
  the proven graph_host pattern; covered by a wiring test.

## Migration Plan

Pure additive runtime behavior; no data migration. Existing blocked bundles
remain valid records of their time. Rollback = revert the commit; gates without
the policy flag were never affected, and the serde allowlist addition is
backward-compatible with existing checkpoints (msgpack type tags are stable).

## Open Questions

(none)
