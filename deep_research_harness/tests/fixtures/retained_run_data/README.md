# Retained Run Data Evidence

`initial_zero_inventory_dry_run.json` is the deterministic output of:

```bash
cd deep_research_harness
uv run --extra operations python scripts/retained_run_data_migration.py
```

It records the approved initial support decision: zero registered records, zero
migrations, zero failed records, and zero unaccounted supported records. The test
suite compares the runner output to this file so changes to the admission matrix or
counts require explicit evidence review.

The ignored local `.deep-research-demo-runs/` and `.reports/` roots are not inputs to
this runner and are not an inventory. The 2026-08-13 snapshot in
`_backlog/_done/_closed_plans/deep-research-post-migration-convergence/02-audit-findings/75-persisted-compatibility-findings.md`
is risk evidence only: it observed 28 opaque graph checkpoint stores, 326 Bundle
states, 56 v2 plus 113 v3 Journal manifests, 616 v2 plus 426 v3 Journal events, and
169 current Summary v2 records. Those values neither authorize migration nor imply
anything about external retained data.
