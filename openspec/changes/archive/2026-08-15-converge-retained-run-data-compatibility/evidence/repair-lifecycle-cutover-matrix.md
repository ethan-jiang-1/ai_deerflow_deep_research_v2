# Repair And Lifecycle Cutover Matrix

> Recorded for task 2.6 on 2026-08-15. The source-controlled inventory remains
> zero-record; its offline decoders are evidence tools and are not runtime readers.

| Family | Offline old decoder | Old runtime reader | Old runtime writer | Current runtime reader | Current runtime writer | Evidence |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Graph checkpoint `repair_counts` | 1 registered v2 decoder | 0 | 0 | 1 schema-v3 admission boundary | 1 v3 initial graph-state writer | `test_retained_checkpoint_cutover.py` rejects an old SQLite checkpoint before compile and proves migration write/reload/replay; `test_current_graph_state_has_no_repair_counts_alias` proves the typed state and ownership surfaces contain no old field. |
| Bundle `REPAIR_EXHAUSTED` | 1 registered v4 decoder | 0 | 0 | 1 current `BundleLocalState` decoder | 1 current `BundleStateStore` writer | `test_retained_bundle_cutover.py` rejects unregistered v4 input before status projection and proves identity/blocked-status preservation without a replacement reason. The enum member is absent from the current terminal contract. |

The direct current readers reject every legacy/unregistered record before graph work or
lifecycle projection. A replayed target and an atomic write failure leave the source
unchanged and create no current output. No old reader is restored by the inventory,
and no Journal or terminal projection is involved in either lifecycle decision.

Focused verification:

```text
UV_OFFLINE=1 .venv/bin/python -m pytest \
  tests/unit/test_retained_checkpoint_cutover.py \
  tests/unit/test_retained_bundle_cutover.py \
  tests/unit/test_state_contracts.py \
  tests/unit/test_state_persistence.py \
  tests/unit/test_bundle.py \
  tests/unit/test_bundle_graph_journal.py \
  tests/integration/test_refinement_round_recovery.py \
  tests/integration/test_refinement_round_workflow.py \
  tests/integration/test_research_lifecycle_tool.py -q

117 passed
```
