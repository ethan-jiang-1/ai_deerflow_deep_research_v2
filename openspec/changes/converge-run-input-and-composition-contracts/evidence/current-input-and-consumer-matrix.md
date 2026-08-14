# Current Input And Consumer Matrix

This is the supported source-controlled input inventory for
`converge-run-input-and-composition-contracts`. It is an apply-time evidence record,
not a retained-data inventory. Inputs outside these rows are rejected. Emergency
rollback may restore the previous reader as a code change; it never rewrites a payload.

## Plan-Review Result

- The frozen obligation union is exactly `FM-C01`, `FM-C02`, `FM-C04`, `EC-C06`,
  `PC-C01`, `PC-C02`, `RC-C03`, `EV-C06`, `FM-C03`, `PC-C05`, and `RC-C05`.
- `composition-mode` remains owned by `runtime/bundle_control.py` admission and its
  executor-supplied State fact. `profile-proposal` remains owned by
  `domain/profile.py` candidate parsing and HITL1 acceptance. Neither workstream
  introduces a runtime fact authority, reader-support promise, mode selector, data
  migration, or DeerFlow boundary.
- The scoped current specs, deltas, source seams, and focused evidence seams agree:
  no no-graph/full-fake completion, missing-mode default, profile v1/absent-schema
  reader, or convenience Python alias remains a target contract after the cutover.
- The only source-controlled writers/readers and tracked consumers are represented
  below. No additional in-scope source-controlled reader, writer, documentation
  surface, root facade, or consumer was found; no corrective task is needed.

## Supported Input Rows

| Family | Current schema / exact fields | Writer → reader | Acceptance owner / tracked consumers | Rejection and no-write assertion | Rollback boundary / consumer count |
| --- | --- | --- | --- | --- | --- |
| Bundle-local State | `schema_version=4`; explicit `implementation_mode` is written by the trusted graph executor, and the complete `BundleLocalState.to_mapping()` field set is current | `BundleLifecycle.start()` receives the trusted `BundleGraphExecutor.implementation_mode`; `BundleStateStore` / `BundleLocalState.from_mapping()` read it | `BundleLocalState` codec is the target admission owner before lifecycle, review, or graph projection; consumers are `BundleLifecycle`, `RequestBundleStore`, and `BundleGraphExecutor` | Missing / old schema / `full_fake` / unknown mode raises `bundle_state_invalid`; decode then causes no write, backfill, graph dispatch, completion, or provenance upgrade | Restore only the prior State reader in an emergency; current writer is never rewritten. 3 source consumers |
| Profile content | `schema_version=2`; `depth`, `audience`, `format`, `cost_tolerance`, `time_budget`, `must_answer`, `scope_boundaries`, `custom_notes`, `comparison_required`, `comparison_subjects`, `request_language`, `output_language`, `degraded_profile` | HITL1 `finalize_profile()` → `RequestBundleStore.write_profile()` → `RequestBundleStore.read_profile()` | `ResearchProfile` validates current content before `ContentRef`; consumers are HITL1 and topic-planning assignment | Absent/v1/alias/extra/malformed shape raises `profile_schema_invalid` before `ContentRef`, State projection, proposal/control, or continuation; content bytes remain untouched | Restore only the prior profile reader. 2 source consumers |
| HITL1 pending / proposed profile | `schema_version=2`; `depth`, `audience`, `format`, `cost_tolerance`, `time_budget`, `must_answer`, `scope_boundaries`, `custom_notes`, `comparison_required`, `comparison_subjects`, `request_language`, `output_language` | HITL1 `_proposal_payload()` / `_profile_progress_payload()` → Bundle State field → HITL1 `_pending_progress()` / `_proposed_profile()` | HITL1 is sole acceptance owner before visible interaction, State reducer, profile content, or graph continuation; consumers are the pending/proposal read helpers | Absent schema, v1, legacy alias, unknown field, malformed map, or external shape is invalid before proposal/control/State/continuation write; retained mapping is unchanged | Restore only the prior HITL1 reader. 2 source consumers |
| Raw semantic reply | unpersisted text accepted by `parse_profile_input()`; its `ProfileParseResult` has `partial` and `recognized_fields` | Human reply → `parse_profile_input()` → HITL1 semantic admission | Domain parser produces a candidate only; HITL1 decides whether it becomes a proposal, control, profile, or continuation fact | Empty, invalid JSON, extra JSON field, unrecognized, or incomplete reply preserves existing bounded candidate/visible-recovery behavior and creates no persisted fact by parser action | No persisted-reader rollback applies. 1 source acceptance consumer |

`current_refinement` and `refinement_replay_receipts` remain the existing optional
reader/recovery exception. This change neither reclassifies them nor uses their
optional semantics to admit a missing composition or profile/proposal schema.

## Clean-Cutover Python Surfaces

| Retired surface | Tracked consumers / supported-surface evidence | Denial form and migration target | Emergency rollback / later-support trigger |
| --- | --- | --- | --- |
| `ResearchGraphRecipe.create()` | One internal test consumer in `tests/graph/test_topology_and_implementation.py`; no root-package re-export, application runtime consumer, README/local-operations entry, or supported Python facade | Attribute lookup/call fails after removal. Internal callers use `ResearchGraphRecipe.all_real()`; explicit fixture/mixed assembly remains `from_adapters()` | Restore only the former alias if an emergency rollback is approved. Any third-party support requires a later change with consumer inventory, notice, compatibility decision, and removal trigger |
| `parse_profile_response()` | `tests/domain/test_profile.py` and `tests/unit/test_live_evaluation.py`; no production runtime consumer, root-package re-export, README/local-operations entry, or supported Python facade | Import/attribute lookup fails after removal. Consumers use `parse_profile_input(...).partial` or intentionally inspect `ProfileParseResult` | Restore only the former wrapper if an emergency rollback is approved. Any third-party support requires a later change with consumer inventory, notice, compatibility decision, and removal trigger |

## Evidence Boundaries

Focused tests prove only source-controlled current writers/readers and repository
consumers. They do not claim a retained-data inventory, live credentialed execution,
or external Python consumer closure. Those lanes remain intentionally unrun and do not
expand this supported-input scope.
