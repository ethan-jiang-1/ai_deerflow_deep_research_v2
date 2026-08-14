# Observation And Terminal Cutover Matrix

> Recorded for task 3.5 on 2026-08-15. The checked-in retained-data inventory is
> still zero-record. The offline decoder is the only old-data reader and is never
> imported by runtime admission paths.

| Family | Offline old reader | Old runtime reader | Old runtime writer | Current runtime reader | Current runtime writer | Post-cutover count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Journal manifest/event | 1 registered v2 decoder | 0 | 0 | 1 v3-only `RunObservationStore` boundary | 1 v3 manifest/event writer | v1/v2 runtime compatibility readers/writers: 0/0 |
| Run Summary | excluded from this cutover; current v2 decoder unchanged | excluded | excluded | current v2 decoder | current v2 writer | unchanged; not counted as legacy Journal data |
| Persisted/public terminal result | 1 registered reject-only input decoder | 0 | 0 | 1 required `RunFailure.diagnostic_location` boundary | 1 shared current writer (`ResearchRunExperience._failure`) plus explicit demo fixtures | missing-location compatibility readers/writers: 0/0 |

The Journal reader rejects a v1/v2 manifest before append, rewrite, inspection, or
projection and leaves manifest, Summary, and events byte-for-byte unchanged. The
current writer emits v3 manifest/events while retaining Summary v2. The terminal
reader rejects a missing location before a `RunUpdate` can reach CLI, TUI, machine
participant, lifecycle, or Journal projection. Current non-provider writers emit
`unavailable` with no invented reference; verified provider publication emits
`bundle_journal` and `journal_record_created=true`.

## Deterministic Evidence

```text
make test-retained-observation
12 passed

.venv/bin/python -m pytest \
  tests/unit/test_retained_journal_cutover.py \
  tests/unit/test_run_observation_store.py \
  tests/contract/test_run_experience_contract.py \
  tests/contract/test_run_experience_failures.py \
  tests/integration/test_demo_run_update_adapters.py \
  tests/integration/test_demo_real.py \
  tests/integration/test_demo_tui.py \
  tests/unit/test_retained_terminal_result_cutover.py -q
96 passed
```

The retained-data inventory dry-run remains the source-owned zero count for all
four families: registered 0, migrated 0, rejected 0, failed 0, and unaccounted
supported 0. The focused terminal tests additionally prove that a legacy fixture
fails Pydantic `RunFailure` and public `RunUpdate` validation before any adapter
projection, while provider and non-provider current writer cases retain their
explicit location truth.

Ignored `.deep-research-demo-runs/` data is not included in these counts. Its stale
Bundle state is intentionally treated as unsupported local risk evidence; isolated
fixture tests use a fresh temporary Bundle root and do not grant that root runtime
support.
