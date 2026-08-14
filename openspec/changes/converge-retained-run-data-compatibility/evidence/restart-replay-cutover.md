# Restart And Replay Cutover Proof

> Recorded for task 4.2 on 2026-08-15. Each family is exercised at its named
> local reader; observations and terminal results never become lifecycle authority.

| Family | Current write/reload/replay proof | Rejected-old proof | Authority boundary |
| --- | --- | --- | --- |
| Graph checkpoint | Registered v2 decoder writes schema-v3 output; `validate_research_state` reloads it; a fresh gate evaluation replays the existing `gate_attempts_by_phase` and `repair_budget_by_phase` facts. | An unregistered checkpoint containing `repair_counts` fails before graph compilation/execution and leaves Bundle State and graph SQLite bytes unchanged. | Gate facts remain the only repair authority. |
| Bundle State | Registered v4 terminal migration writes current State; `BundleLocalState.from_mapping` reloads it twice, preserving identity and blocked status with no terminal reason. | An unregistered `REPAIR_EXHAUSTED` State returns unavailable before status projection and leaves its source bytes unchanged. | Bundle-local State remains the lifecycle authority; no replacement reason or route is created. |
| Journal manifest/event | Registered complete v2 data writes v3 manifest/events; a new `RunObservationStore` instance inspects the output and confirms complete v3 events after reload. Summary v2 remains unchanged. | v1/v2 or partial data becomes unavailable before append/inspection projection; manifest/events remain byte-for-byte unchanged. | Journal is observation-only and exposes no lifecycle control method or mutation authority. |
| Terminal result | Current writer tests preserve explicit `unavailable` or verified `bundle_journal` location truth. | A missing-location persisted/public result fails `RunFailure` and `RunUpdate` validation before any participant projection; inventory records rejection only and produces no output. | Terminal result is a bounded participant projection; it cannot resume, retry, publish, or strengthen a Run. |

## Focused Run

```text
.venv/bin/python -m pytest \
  tests/unit/test_retained_checkpoint_cutover.py \
  tests/unit/test_retained_bundle_cutover.py \
  tests/unit/test_retained_journal_cutover.py \
  tests/unit/test_retained_terminal_result_cutover.py -q
17 passed
```

The broader task 3.5 suite also passed (96 tests), including direct observation
store, lifecycle-to-experience, CLI/TUI, and participant adapter coverage. Its
authority checks show that Journal publication failure cannot alter the typed
lifecycle projection and that Bundle loss offers only the typed unavailable result.
