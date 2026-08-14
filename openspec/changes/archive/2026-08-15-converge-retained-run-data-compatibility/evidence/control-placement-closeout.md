# Control Placement Closeout

> Apply review for task 4.4, recorded on 2026-08-15 against the implementation
> represented by the current worktree and the retained-data evidence set.

## Review Result

No actionable correction was found. The two frozen workstreams still have one
deterministic admission owner per changed fact, no runtime inventory bypass, no
competing lifecycle authority, and the complete-reader-only recovery boundary.
No new unchecked task is required.

| Changed fact | Direct owner and boundary checked | Evidence checked | Placement result |
| --- | --- | --- | --- |
| Checkpoint `repair_counts` retirement | `validate_research_state` and graph checkpoint admission reject legacy input before graph compilation; gate kernel remains the owner of `gate_attempts_by_phase` and `repair_budget_by_phase`. | `tests/unit/test_retained_checkpoint_cutover.py`; `evidence/repair-lifecycle-cutover-matrix.md`; restart/replay proof. | `non-bypassable`; no repair alias or second gate controller. |
| Bundle `REPAIR_EXHAUSTED` retirement | `BundleLocalState`/Bundle lifecycle status rejects old input before lifecycle projection; Bundle-local State remains the lifecycle authority. | `tests/unit/test_retained_bundle_cutover.py`; `evidence/repair-lifecycle-cutover-matrix.md`; restart/replay proof. | `non-bypassable`; no synthetic terminal or retry route. |
| Journal v1/v2 reader retirement | `RunObservationStore` validates the current v3 manifest/event boundary; the offline runner is not imported by runtime readers and Journal exposes no lifecycle mutation authority. | `tests/unit/test_retained_journal_cutover.py`, `tests/unit/test_run_observation_store.py`; `evidence/observation-terminal-cutover-matrix.md`. | `non-bypassable`; unavailable/unsupported observation is bounded and no-write. |
| Missing terminal `diagnostic_location` | `RunFailure` validation runs before `RunUpdate` participant projection; current writer chooses only explicit `bundle_journal` or factual `unavailable`. | `tests/unit/test_retained_terminal_result_cutover.py`; `evidence/observation-terminal-cutover-matrix.md`; restart/replay proof. | `non-bypassable`; no UI inference, external fallback, resume, or retry. |

## Boundary Checks

- `rg` confirms production runtime modules do not import or consult
  `retained_run_data_inventory.json`; only the offline migration script and its
  deterministic tests reference it.
- The post-cutover report records old runtime readers/writers as zero and counts
  planted rejected inputs separately from the zero supported inventory.
- Recovery is a complete local reader hotfix/revert with paired tests. No task,
  code path, or evidence authorizes a field-level compatibility flag or payload
  rewrite.
- `deerflow/` remains a leveraged gitlink; no source-browse, source edit, or
  pointer update is part of this review.
