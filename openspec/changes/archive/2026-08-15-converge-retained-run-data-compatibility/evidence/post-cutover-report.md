# Retained Run Data Post-Cutover Report

> Source-owned closeout evidence for task 4.3, recorded on 2026-08-15. This
> report covers only the source-controlled retained-data inventory and the
> deterministic planted records below. It is not an inventory or support promise
> for ignored, local, host, deployment, or external data.

## Supported Inventory

`deep_research_harness/scripts/retained_run_data_inventory.json` is version 1
with an explicit empty `records` list. Running:

```bash
cd deep_research_harness
UV_OFFLINE=1 .venv/bin/python scripts/retained_run_data_migration.py \
  > /tmp/retained-run-data-report.json
diff -u tests/fixtures/retained_run_data/initial_zero_inventory_dry_run.json \
  /tmp/retained-run-data-report.json
```

produces the checked-in dry-run report without a difference. Its totals are:

| Registered | Migrated | Rejected | Failed | Unaccounted supported |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 0 | 0 | 0 |

Every family (`graph_checkpoint`, `bundle_state`, `journal`, and
`terminal_result`) likewise reports zero registered, migrated, rejected, and
failed records. The report and its fixed reader/writer descriptions are retained
at `deep_research_harness/tests/fixtures/retained_run_data/initial_zero_inventory_dry_run.json`.

## Runtime Reader And Writer Counts

| Family | Offline old decoder | Old runtime reader | Old runtime writer | Current runtime reader | Current runtime writer |
| --- | ---: | ---: | ---: | ---: | ---: |
| Graph checkpoint `repair_counts` | 1 registered v2 decoder | 0 | 0 | 1 schema-v3 admission boundary | 1 schema-v3 writer |
| Bundle `REPAIR_EXHAUSTED` | 1 registered v4 decoder | 0 | 0 | 1 current Bundle State decoder | 1 current Bundle State writer |
| Journal manifest/event v1/v2 | 1 registered v2 decoder | 0 | 0 | 1 v3-only Journal boundary | 1 v3 manifest/event writer |
| Persisted/public terminal without location | 1 registered reject-only decoder | 0 | 0 | 1 required `RunFailure.diagnostic_location` boundary | 1 explicit `bundle_journal` or `unavailable` writer |

`RunSummary` v2 remains a current, unchanged Summary contract. It is not a legacy
Journal manifest/event reader or writer, is absent from the inventory, and is
excluded from all legacy-Journal counts in this report.

## Separately Counted Planted Rejections

These are deterministic test inputs, not supported inventory records and not a
discovery scan. They prove that runtime admission fails before mutation,
projection, resume, retry, or provenance strengthening.

| Family | Rejected planted input | Count | Evidence |
| --- | --- | ---: | --- |
| Graph checkpoint | Unregistered v2 checkpoint carrying `repair_counts` | 1 | `test_unregistered_repair_counts_checkpoint_rejects_before_graph_compile_or_execution` |
| Bundle State | Unregistered v4 `REPAIR_EXHAUSTED` terminal | 1 | `test_unregistered_repair_exhausted_bundle_is_unavailable_before_status_projection` |
| Journal manifest/event | Unregistered or partial v1/v2 Journal | 1 | `test_partial_or_unregistered_old_journal_is_unavailable_before_append_or_projection` and `test_bundle_journal_rejects_legacy_manifest_before_append_or_projection` |
| Terminal result | Persisted/public terminal without `diagnostic_location` | 1 | `test_persisted_terminal_without_location_rejects_before_any_projection` |
| **Total** | **Non-inventory planted rejected inputs** | **4** | **No output is written for any rejection.** |

The terminal case is separately a registered *reject-only* migration fixture in
its decoder test; it is not counted as a supported migrated record. This preserves
the distinction between an approved rejection disposition and a current runtime
compatibility reader.

## Attached Deterministic Evidence

- Dry run and fixed matrix: `tests/fixtures/retained_run_data/initial_zero_inventory_dry_run.json` and `scripts/retained_run_data_migration.py`.
- Checkpoint and Bundle old/new matrix: `evidence/repair-lifecycle-cutover-matrix.md`.
- Journal and terminal old/new matrix: `evidence/observation-terminal-cutover-matrix.md`.
- Current write, reload, replay, and non-authority proof: `evidence/restart-replay-cutover.md`.
- Four-family direct cutover suite: `17 passed`.
- Journal, terminal, CLI/TUI, lifecycle, and participant projection suite: `96 passed`.
- Direct Journal store suite after the final legacy-manifest fix: `26 passed`.
- Current Summary/session focused suite: `make test-retained-observation`, `12 passed`.

Ignored `.deep-research-demo-runs/` and `.reports/` remain non-authoritative risk
evidence only. The 2026-08-13 audit snapshot is recorded in
`_backlog/plans/deep-research-post-migration-convergence/02-audit-findings/75-persisted-compatibility-findings.md`;
none of its observed files is registered, migrated, or treated as supported here.

## Recovery Boundary

For a post-cutover discovery, the current reader stops at its local bounded
rejection boundary. The only legal recovery is a Data Owner-approved complete
local reader hotfix or revert with its paired deterministic tests. A field-level
compatibility switch, source payload rewrite, synthetic terminal mapping, or
projection-led lifecycle recovery is not part of this cutover.
