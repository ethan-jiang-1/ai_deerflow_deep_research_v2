## Context

See proposal.md — Why. The existing rapid gate invokes every deterministic integration test for every Harness pull request. `test_local_entry_environment.py` contains two public-entry process scenarios; each copies the Harness and runs `make install` in the copy. They prove supported-command behavior, but their setup cost is unrelated to most source changes. Only the fast lane currently emits JUnit and has an enforced duration policy.

## Goals / Non-Goals

**Goals:**
- Preserve the two clean-copy scenarios and their DPL-005, DPL-006, and LCP-002 evidence claims.
- Make their maintained, low-frequency execution surface explicit and mechanically selectable.
- Keep the rapid PR gate deterministic and free of complete-environment copy/setup work.
- Make periodic regressions observable, path-routed, manually runnable, and cost-bounded.

**Non-Goals:**
- Suspending, deleting, credentialing, or weakening public-entry scenarios.
- Reclassifying general integration or workflow evidence beyond the two clean-copy scenarios.
- Changing supported Make commands, runtime adapters, profile behavior, or DeerFlow.

## Decisions

### D1. Use `tests/scenarios_periodic/`, not `scenarios_suspended/`

`scenarios_suspended/` means a scenario no longer has an active default support promise and needs a new approved change before reactivation. The clean-copy entry scenarios continue to prove supported commands, so they move to `tests/scenarios_periodic/test_local_entry_environment.py`. The periodic directory has a README naming its maintenance status, deterministic/no-credential boundary, owning target, CI workflow, and the path-routing rule. Its tests carry a registered `periodic` marker and never carry `requires_llm` or `release_e2e`.

Alternative rejected: place them in `scenarios_suspended/`. That would make an active public-entry contract invisible to its ordinary owner and misuse release-only suspension semantics.

### D2. Split rapid and periodic targets without two competing aggregate authorities

`make verify` remains the one rapid deterministic PR aggregate and excludes the `periodic` marker from both its pytest-only aggregate and workflow selection. `make test-entry-environment-regression` is the sole project-owned Make target dedicated to executing `tests/scenarios_periodic/`; it writes `.reports/test-entry-environment.xml` and invokes a reusable duration checker with a periodic budget. The test-asset checker is the sole non-executing consumer: it collects the periodic selection to validate central claims and requirement impacts. This is a maintained supplement, not a second meaning of `verify` or an ad-hoc command list.

Alternative rejected: directory placement alone. `make test` and workflow collection start from `tests/`, so placement cannot prevent accidental default execution; the directory gives contributor-visible ownership and the marker gives executable selection semantics.

### D3. Route CI by causal dependency surface and recurrence

The periodic workflow runs on pull-request changes and `master` pushes affecting `deep_research_harness/Makefile`, `pyproject.toml`, `uv.lock`, `run/**`, `scripts/**`, `src/**`, `src_fake/**`, `tests/scenarios_periodic/**`, or the workflow definition itself. It also runs daily and on manual dispatch. It performs explicit `make install`, then offline periodic execution. The existing rapid workflow retains its job/status identity and runs for all Harness changes. Workflow configuration expresses trigger scope and publishes a distinct job result; it does not claim branch-protection policy.

Alternative rejected: run only nightly. A relevant PR could merge with a broken supported entry and wait a day; path routing captures the causal changes without taxing unrelated work.

### D4. Preserve small static contracts; retain one process truth

Existing quick Makefile/runner contract tests continue to assert shared preflight/no-sync composition. The relocated process scenarios remain the sole clean-copy proof that explicit setup, a missing/incomplete environment, profile validation, launcher credential boundary, state preservation, and concurrent commands interact correctly. No assertion is duplicated solely to recreate a full process test at unit cost.

## Risks / Trade-offs

- [An entry dependency path is omitted from CI routing] → exact workflow-path contract tests list the declared surface; the daily run bounds detection delay and manual dispatch remains available.
- [Periodic cost grows silently] → first record the observed clean-copy duration in the task evidence, then set a documented per-scenario budget with enough normal-run slack; fail later overruns unless an owner/reason/expiry waiver is recorded.
- [A contributor mistakes periodic for suspended] → directory READMEs and collection contracts assert that periodic is maintained/deterministic while suspended is release-only/credentialed.
- [Rapid gate accidentally reabsorbs periodic tests] → an exact collection test asserts the rapid selection excludes the periodic directory and the periodic target selects it.

## Migration Plan

1. Add red collection, asset-governance, and CI-routing contracts, including a planted periodic selector and a suspended-selector exclusion check.
2. Move the test file with `git mv`, add the periodic README and target, then update evidence/requirement registries without changing assertions.
3. Add the path-routed scheduled/manual workflow and periodic duration report/policy, using one observed baseline to select the initial numeric budget.
4. Run rapid and periodic targets independently; rollback moves the file back and restores its former target membership, with no data or runtime migration.

## Open Questions

None.
