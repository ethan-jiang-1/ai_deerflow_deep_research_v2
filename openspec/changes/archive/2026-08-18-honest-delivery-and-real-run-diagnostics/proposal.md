# Honest Delivery Degradation and Faithful Real-Run Diagnostics (BUG-035/036/037)

## Why

Two consecutive real mode-003 runs died at the same place: the wave2 gate spent its
whole evidence budget on honest searchable gaps (a wave1 open-question projection and
a missing precise figure) that no bounded number of targeted searches can force to
converge, then escalated to `research.blocked` with no report and no degraded
artifact (BUG-035). The same blocked terminal then misreported itself on the demo
terminal as "Bundle 内 Event Journal 记录不可用" while the bundle's journal on disk
was complete (BUG-036), and every real run prints langgraph
"Deserializing unregistered type … will be blocked in a future version" warnings for
the exact three project types persisted in checkpoints (BUG-037) — a time bomb for
checkpoint recovery. One change covers all three because they share one causal
theme: the minimal real-auto run must converge to honest delivery with faithful,
future-proof diagnostics.

## What Changes

- **Wave2 honest-delivery degradation (BUG-035, gate side).** `GateDefinition`
  gains an explicit `degraded_pass_on_exhaustion: bool = False` policy. When a
  phase's repair budget is exhausted, no hard failure exists, the gate declares the
  policy, and this phase has not already degraded since its budget was seeded, the
  kernel returns `PASS` with `degraded=True` (same route label as `pass`) instead
  of `BLOCKED`; the run continues to readiness/final delivery. Only the real wave2
  gate declares the policy — wave0/wave1/final_delivery keep today's
  budget-exhaustion blocking semantics. Repeated exhaustion (same or changed gap
  set) still blocks: degradation happens at most once per phase per budget seeding,
  recorded through the existing gate-owned `degraded_decisions` state field, and
  the rerun planner's existing gate-state reset clears it together with the
  budgets it already resets.
- **Honest gap disclosure in the report (BUG-035, delivery side).** The readiness
  report-plan materializer appends the remaining unresolved searchable gaps as
  mandatory uncertainties: gap ids come from the checkpointed `unresolved_gaps`
  control field, gap bodies are read from the bundle store's canonical
  `synthesis/findings.json` artifact through one new bounded read. No gap body
  enters checkpoint state; the final report's existing "Uncertainties" section
  discloses what was not resolved.
- **Faithful journal-availability projection (BUG-036).** A blocked terminal's
  `RunFailure.journal_record_created` / `diagnostic_location` reflect the
  observation-confirmed diagnostic reference for **any** blocked incident, not only
  provider diagnostics. Gate-blocked incidents whose diagnostic reference was
  published to the bundle journal stop rendering as "journal unavailable".
- **Registered checkpoint types (BUG-037).** The explicit msgpack compatibility
  boundary gains `deerflow_deep_research.domain.wave1.Wave1OpenQuestionRef`
  (alongside `ContentRef` and `AttemptStatus` — the only project types persisted in
  research checkpoints), and the bundle-contained graph store
  (`open_graph_checkpoint` → `AsyncSqliteSaver`) opens with that serde instead of
  langgraph's default, matching what `GraphHost` already does. Real-run checkpoint
  recovery stops emitting unregistered-type warnings and survives strict mode.
- **Runbook-003 acceptance sync.** The 003 runbook and its spec acceptance now
  expect: an honest gap that does not converge yields a **completed** run with a
  real report that discloses the gap — not a blocked terminal.

No product default changes: gates that do not declare the policy behave exactly as
today, and runs whose gaps converge within budget never see the degraded path.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `gate-kernel`: exhaustion verdict derivation gains an opt-in degraded-pass
  policy with a once-per-seeding bound; `GateDefinition` and `GateResult`
  semantics extended accordingly.
- `wave2-synthesis-node`: the real wave2 gate declares
  `degraded_pass_on_exhaustion`; a degraded pass leaves `unresolved_gaps` intact
  for downstream disclosure instead of routing `exhausted`.
- `readiness-node`: the report plan gains mandatory uncertainties projected from
  the bundle store's canonical synthesis artifact for the gate-recorded unresolved
  searchable gaps.
- `research-run-experience`: blocked-terminal journal availability and diagnostic
  location derive from the observation-confirmed diagnostic reference for every
  blocked incident, not only provider diagnostics.
- `research-graph-lifecycle`: the bundle-contained graph store uses the explicit
  application msgpack serde boundary, and that boundary covers every project type
  research checkpoints persist.
- `low-scale-real-auto`: 003 acceptance includes the degraded honest-delivery
  outcome (completed run, real report, disclosed gaps).

## Impact

- Code: `domain/gate.py`, `engine/gate_kernel.py`, `engine/real_gates.py`,
  `graph/nodes/gate_adapter.py` (marker write), `graph/nodes/readiness/`
  (materializer + node), `runtime/work_unit_store.py` (one bounded canonical
  read), `runtime/run_experience.py` (journal projection),
  `runtime/checkpoint.py` (allowlist), `runtime/bundle_lifecycle.py` (saver serde),
  `graph/nodes/rerun/planner.py` (degraded marker reset alongside budget reset).
- Docs: `_backlog/_local_demo/runbook-003-medium-real-auto.md` acceptance section;
  bug ledger entries BUG-035/036/037 move to fixed on completion.
- Tests: kernel unit tests (degraded pass, once-bound, hard-failure precedence),
  readiness projection tests, run-experience projection tests, msgpack
  round-trip/strict-mode tests including `Wave1OpenQuestionRef`, and a graph-level
  test that a non-converging honest gap reaches `final_delivery` with disclosed
  uncertainties. All new evidence is deterministic and offline (fixture providers,
  no network, no API keys); `make verify` stays offline-green and nothing moves
  behind the `requires_llm` mark. The real 003 run remains an operator runbook
  step requiring `DEEPSEEK_API_KEY`/`TAVILY_API_KEY`, never a CI gate.

## Change Focus

- **Primary module / causal owner**:
  `deep_research_harness/src/deerflow_deep_research/engine/` — the deterministic
  gate kernel owns the budget-exhaustion verdict semantics that currently kill
  real runs at wave2; the other two bugs are bounded fixes in their owning
  adapters (`runtime/`).
- **Seam classification**: `deterministic-guardrail` — all three fixes are
  deterministic policy/projection changes (gate verdict policy, report-plan
  projection, journal-field projection, serde registration); no new model role,
  prompt, tool, or capability is added.
- **Question**: When bounded evidence cannot force an honest gap to converge, how
  does the run deliver honestly (report with disclosed gaps) instead of dying
  blocked — while blocked terminals report journal facts faithfully and the
  checkpoint boundary stays explicitly registered for future langgraph strict
  mode?
- **Necessary adjacent/external contracts**:
  - `domain/state.py` + `graph/nodes/gate_adapter.py`: the gate-owned
    `degraded_decisions` field as the once-per-seeding marker (control-placement
    question).
  - `graph/nodes/readiness/` + `runtime/work_unit_store.py`: canonical
    `synthesis/findings.json` as the gap-body content authority for disclosure
    (fact-owner question).
  - `runtime/run_experience.py` + `domain/run_experience.py`: the
    `journal_record_created`/`diagnostic_location` invariant (projection-faithfulness
    question).
  - langgraph `JsonPlusSerializer.allowed_msgpack_modules` /
    `LANGGRAPH_STRICT_MSGPACK`: upstream serialization compatibility contract
    (upstream-compatibility question).
- **Evidence seam**: `tests/engine/test_gate_kernel.py`,
  `tests/unit/test_checkpoint_msgpack.py` (+ strict-mode lane), readiness/run
  -experience unit seams, and the fixture graph tests in `tests/graph/`; operator
  runbook 003 for the real-model confirmation.
- **Not in scope**: no bridge/provider hardening, no budget increases, no
  wave0/wave1/final gate semantic changes, no HITL flow changes, no Gateway
  observer-path claims, no langgraph/deerflow source changes (registration only).
- **Triggered review policies**: workflow-outcome-review, control-placement,
  deerflow-downstream.

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Honest searchable gap not converging within wave2 evidence budget | wave2 gate preview + `unresolved_gaps` (gate-owned control field) | targeted-evidence loop, bounded by gate budget (minimal pair: 2 rounds) | degraded `PASS` at first exhaustion (once per seeding) → completed run with disclosed gap uncertainties; repeated exhaustion → `BLOCKED` as today | read disclosed uncertainties in the final report; rerun/refine resets budgets and the degradation marker | `tests/engine/test_gate_kernel.py`, fixture graph run to `final_delivery` |
| Blocked terminal (any incident class) with a journal-confirmed diagnostic reference | bundle event journal via observation view | none needed (presentation fact, not a run failure) | unchanged (`research.blocked` terminal) | operator inspects bundle diagnostics with correct availability rendering | run-experience unit tests over `_failure_for_terminal` |
| Checkpoint contains an unregistered project type under strict msgpack | explicit serde allowlist in `runtime/checkpoint.py` | register every persisted project type at the boundary; strict mode fails closed | n/a (prevents a future recovery failure class) | keep allowlist equal to the persisted type set; strict-mode lane proves it | `tests/unit/test_checkpoint_msgpack.py` under `LANGGRAPH_STRICT_MSGPACK=true` |

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Budget exhaustion verdict for a gate declaring `degraded_pass_on_exhaustion` | none — the model already produced the honest gap; convergence is not model-decidable | `engine/gate_kernel.py` derives the verdict from budget, failure classifications, and the `degraded_decisions` marker | smallest policy extension at the existing verdict seam; route labels unchanged | gates without the policy block exactly as today; degradation bounded once per seeding | reuses `degraded` flag, route map, and the reserved `degraded_decisions` gate field instead of new state machinery | `tests/engine/test_gate_kernel.py` |
| Which unresolved gaps the report discloses | none — disclosure is a projection of admitted facts | readiness materializer: `unresolved_gaps` ids (gate-owned) joined against canonical `synthesis/findings.json` (store-owned) | fact owner stays the artifact; no gap body in checkpoint | report can only disclose gaps the gate recorded and the artifact contains | no new prompt/critic round-trip; final report layout unchanged | readiness materializer unit tests + fixture graph run |
| Journal availability for a blocked terminal | none | `runtime/run_experience.py` resolves the observation-confirmed diagnostic reference | same check generalized off the provider-only branch | `journal_record_created` ⇔ `diagnostic_location == "bundle_journal"` invariant preserved | no new field, no renderer change downstream | run-experience unit tests |
| Checkpoint serialization boundary | none | explicit `allowed_msgpack_modules` set in `runtime/checkpoint.py`, wired into the bundle graph saver | registration only; no deerflow/langgraph source change | strict msgpack mode keeps failing closed for anything unlisted | one serde constructor reused by GraphHost and the bundle store | strict-mode msgpack tests |
