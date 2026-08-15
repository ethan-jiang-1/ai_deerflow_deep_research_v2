## Why

An interrupted standalone all-real demo can leave an available active Run Bundle in
its stable local scope. A later fresh `start` correctly returns the typed
`active_bundle_exists` lifecycle outcome, but `ResearchRunExperience` tries to
present its `active` status as a terminal result and masks it as
`protocol.invalid_result`. The local demo then cannot begin a distinct run despite
explicitly not promising cross-process continuation.

## What Changes

- Project record-bearing active/conflict lifecycle results as a closed
  `research.active` fault with the selected Bundle reference and the legal
  query/cancel guidance, rather than as a terminal or protocol fault.
- Give each all-real standalone demo process a fresh trusted local scope so a
  retained active Bundle from an earlier process cannot block a distinct new demo.
- Render Bundle identity and durability for any fault that carries a selected Bundle.
- Lock the behavior with deterministic, zero-API runtime and demo-composition tests.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/runtime/run_experience.py`
- **Seam classification:** deterministic-guardrail - the runtime owns the typed lifecycle-result to safe presentation projection; no model behavior or human decision changes.
- **Question:** How does the shared presentation module truthfully expose a selected active Bundle when it cannot start a distinct run in that scope?
- **Necessary adjacent/external contracts:** `deep_research_harness/src/deerflow_deep_research/domain/run_experience.py` defines the closed failure vocabulary; `deep_research_harness/scripts/_demo_core.py` owns trusted local demo scope construction; `deep_research_harness/scripts/demo_real.py` consumes safe `Fault` updates without lifecycle authority.
- **Evidence seam:** `tests/contract/test_run_experience_contract.py` for typed active-result projection and `tests/integration/test_demo_real.py` plus `tests/unit/test_demo_core.py` for bounded demo rendering and fresh real scope.
- **Not in scope:** graph topology, checkpoint recovery, model/provider behavior, a generic cross-process demo controller, changes inside `deerflow/`, or deletion of retained Bundles.
- **Triggered review policies:** local-context, authority-and-projections, participant-outcomes, control-and-recovery, workflow-outcome-review, change-admission

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| A selected scope already has an active Bundle | Bundle-local Research State through the lifecycle result | Lifecycle control only; no automatic resume, retry, or cancellation | `research.active` presentation fault; the Bundle remains active and unchanged | Query or explicitly cancel the selected Bundle before any same-scope control | `tests/contract/test_run_experience_contract.py` |
| A later standalone real demo starts after an earlier process left an active Bundle | Trusted demo adapter scope binding | The new process derives one fresh trusted scope; it never reopens, mutates, or deletes the older Bundle | Fresh independent start admission | Start the new demo; inspect the older retained Bundle only through supported operations | `tests/unit/test_demo_core.py` |

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `research-run-experience`: project available active/conflict lifecycle results as a safe non-terminal fault instead of an invalid terminal result.
- `demo-pipeline`: isolate all-real standalone demo launches in fresh trusted local scopes while retaining previous Bundles as independent records.

## Impact

- `deep_research_harness/src/deerflow_deep_research/domain/run_experience.py`
- `deep_research_harness/src/deerflow_deep_research/runtime/run_experience.py`
- `deep_research_harness/scripts/_demo_core.py`
- `deep_research_harness/scripts/demo_real.py`
- Focused runtime, demo-core, and real-CLI tests

Ordinary downstream work remains within `deep_research_harness/`; it neither
modifies nor source-browses the `deerflow/` gitlink.
