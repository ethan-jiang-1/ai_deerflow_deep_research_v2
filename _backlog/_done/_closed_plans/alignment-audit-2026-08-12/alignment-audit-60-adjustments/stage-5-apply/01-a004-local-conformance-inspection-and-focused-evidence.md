# Stage 5 Apply - A-004 Local Conformance Inspection and Focused Evidence

> Change: `reconcile-post-loss-diagnostic-authority`
> Date: 2026-08-13
> Tasks: 1.5, 2.1-2.6
> Status: **BOUNDED LOCAL CONFORMANCE OBSERVED; ONE DEFERRED TOOLING RESIDUE**

## Inspection Boundary

This is a finite inspection of the downstream `deep_research_harness/` source and
local CLI/TUI scripts. It did not source-browse `deerflow/`. It covers the typed
terminal projection, terminal publication adapter, Bundle-local Journal writer,
inspection adapter, and located presentation consumers of `diagnostic_location` and
`terminal_diagnostic_ref`. It is not a claim about physical erasure, every runtime
integration, every uninspected source path, or future code.

## Source-to-Consumer Results

| Boundary | Inspected current path | Result | External crossing or stale consumer |
| --- | --- | --- | --- |
| Typed terminal facts | `domain/run_experience.py` `RunFailure` permits only `bundle_journal` or `unavailable` for a provider diagnostic. It requires a reference and sets `journal_record_created` exactly for `bundle_journal`. | Safe category, opaque reference, recovery facts, and legal action are fields of the returned typed terminal result, not retained-artifact reads. | None found. No `support_journal` or `session_bundle` typed literal exists. |
| Terminal publication decision | `runtime/run_experience.py` creates the terminal reference, publishes a `RecordBearingLifecycleFact`, then builds one shared `Terminal`/`RunFailure`. `_provider_diagnostic_location` requires available observation, same `bundle_id`, and same exact terminal reference for `bundle_journal`; otherwise it returns `unavailable`. | Matches the A-004 verified-contained-publication condition. | No support fallback branch, write, read, or presentation found. |
| Retained terminal write | `runtime/run_observation.py` `BundleRunObservationPublisher.publish` resolves the selected Bundle by scope and ID before creating `RunObservationStore` at `lifecycle.private_root(bundle)`. It writes records, event, summary, and manifest only in that Bundle's `diagnostics/` subtree; resolution/persistence failure returns unavailable. `runtime/bundle_graph.py` establishes its Journal through the same private root. | Bundle-local only. | No external diagnostic/Journal destination or Support Handoff implementation found. |
| Retained read / post-loss inspection | `runtime/session_workbench.py` `BundleWorkbench.diagnosis` obtains a current available lifecycle result, resolves the same Bundle, and rechecks state immediately before contained I/O. Lost, missing, invalid, or unavailable Journal returns `WorkbenchAvailability.UNAVAILABLE`. Domain validators forbid facts in an unavailable diagnosis/timeline result. | Supported readers return unavailable with no external fallback. | None found. This does not prove secure erasure or absence of residual bytes. |
| Terminal participant presentation | `scripts/_terminal_failure_presentation.py`, `demo_real.py`, and `demo_tui.py` use only safe fields from shared `RunFailure`. They offer an inspection command only when `bundle_journal` and snapshot availability, Bundle ID, and exact reference all match. `unavailable` supplies no inspection target. `demo.py` and `demo_fixture_graph.py` render shared updates only. | Returned typed facts can be displayed at terminal time; they do not trigger a later retained-artifact read. | No external post-loss presentation found. |
| Workbench presentation | `scripts/session_workbench.py` renders only `WorkbenchDiagnosisView`; unavailable lifecycle/Journal results render unavailable and carry no facts. | Available-Bundle-only presentation. | None found. |

The finite source scan found no runtime/presentation implementation use of
`support_journal`, `support_handoff`, `external_diagnostic`, `external_journal`, or
`session_bundle`. The only `support_journal` occurrence in the inspected Python tree
is an assertion that it is absent from a rendered view. Search is triage evidence, not
proof against an uninspected or future path.

## Deleted and Unavailable Bundle Disposition

The supported inspection path requires a lifecycle-available selected Bundle and
rechecks state immediately before I/O. `RunObservationStore.inspect` returns bounded
unavailable for missing/corrupt Journal and mismatched Bundle ID. `LocalBundleWorkbench`
returns unavailable diagnosis, timeline, catalog, and artifact views when lifecycle
availability is lost. No inspected reader converts a previous reference into a path,
Bundle selector, recovery action, or external lookup.

This does not assert deletion securely erases disk blocks, backups, caches, or other
physical residual bytes. Those forensic claims lie outside the supported-reader
contract.

## Exact `bundle_journal` Condition and Consumers

| Required condition | Current evidence |
| --- | --- |
| Available selected Bundle | `_provider_diagnostic_location` requires `ObservationInspectability.AVAILABLE`; publisher resolves the selected Bundle and returns unavailable on failure. |
| Matching `bundle_id` | Terminal decision compares `session.bundle_id == control.bundle_id`; publisher/store bind fact and selected Bundle ID. |
| Matching terminal reference | Terminal decision compares `session.terminal_diagnostic_ref == diagnostic_ref`; terminal rendering repeats the check before offering inspection. |
| Located consumers | `runtime/run_experience.py` constructs the literal; `_terminal_failure_presentation.py`, `demo_real.py`, and `demo_tui.py` accept only `bundle_journal`/`unavailable`; fixtures use the same pair. No `session_bundle` expectation was found. |

No behavioral or consumer mismatch was observed. Task 2.4's
`DEFERRED-CODE-CHANGE` stop condition was not triggered.

## Existing Focused Deterministic Evidence

Command from `deep_research_harness/`:

```bash
UV_OFFLINE=1 .venv/bin/python -m pytest \
  tests/contract/test_run_experience_failures.py::test_admitted_terminal_diagnostic_has_no_external_support_fallback \
  tests/contract/test_run_experience_contract.py::test_unavailable_result_clears_the_local_handle_and_offers_only_a_fresh_start \
  tests/integration/test_session_operations_lifecycle.py::test_deleted_bundle_is_unavailable_and_fresh_start_is_independent \
  tests/unit/test_run_observation_store.py::test_lifecycle_resolved_publisher_writes_only_the_selected_bundle_journal
```

Result: **4 passed in 1.91s**.

| Existing test | Fixture / exercised result | Establishes |
| --- | --- | --- |
| `test_admitted_terminal_diagnostic_has_no_external_support_fallback` | Starts and blocks a Bundle, publishes through the real publisher, then inspects its Journal. | No synthetic `support-records.jsonl`; exact reference is in the selected Bundle Journal. |
| `test_unavailable_result_clears_the_local_handle_and_offers_only_a_fresh_start` | Replays available suspension then unavailable lifecycle result. | Local Bundle handle clears; action is a distinct fresh start. |
| `test_deleted_bundle_is_unavailable_and_fresh_start_is_independent` | Removes a Bundle root, requests status, then starts another Bundle. | Deleted status is unavailable; the fresh Run has another ID. |
| `test_lifecycle_resolved_publisher_writes_only_the_selected_bundle_journal` | Publishes one fact through the real publisher. | Selected Bundle Journal is readable; no `.reports` external destination appears. |

The tests add no code or fixtures. They do not prove secure erasure, absence of
residual bytes, every live/credentialed route, every third-party integration, every
future path, or universal semantic conformance.

## A-004 Scenario-Title Residue

An attempt to correct two stale RER delta scenario titles to `Bundle-journal` and
`Unverified publication` wording was rejected by `openspec validate --strict`: a
`## MODIFIED Requirements` block must retain every current scenario title. OpenSpec
supports requirement rename syntax, not scenario rename. The legacy labels therefore
remain validation-compatible identifiers only; their scenario bodies require
`bundle_journal` after verification and `unavailable` with no external fallback when
verification fails.

**DEFERRED-TOOLING-CHANGE A-004-T01** (not `DEFERRED-CODE-CHANGE`):

| Field | Record |
| --- | --- |
| Path / issue | The RER delta and, after sync, main spec retain `session-bundle` / `support-journal fallback` scenario titles because strict validation rejects their removal/rename. |
| Affected clause | Bodies are accurate; titles are misleading historical labels. |
| Risk | A reader could mistake an identifier-like heading for permitted external behavior. |
| Control | Keep operative text explicit: `bundle_journal` or `unavailable`; no external write/read/presentation. Record the residue rather than directly editing a main spec or weakening validation. |
| Owner / red-before-green candidate | A separately authorized OpenSpec tooling change owns scenario-rename support and a red validator test. A later RER spec-maintenance change may then retire the labels. Stage 6 `CONTEXT.md`/ADR work does not own validator or main-spec scenario shape. |
| Stop condition | If a later change uses the labels to restore external behavior in operative text, create a new A-004 change and re-evaluate conformance. |

## Bounded Required/Current Disposition

For inspected downstream terminal-publication, retained-Journal, workbench, CLI, and
TUI paths, current local behavior matches the A-004 Bundle-local-only contract. No
prohibited external write/read/presentation or stale typed consumer was observed. This
is bounded local conformance only; it does not close A-004-T01 or prove physical,
live, uninspected, future, or external behavior.
