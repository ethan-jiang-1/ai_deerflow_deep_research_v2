# Fast Lane Duration Profile Retro

Date: 2026-08-06

## Snapshot

`cd deep_research_harness && UV_OFFLINE=1 make test-fast` completed with
`2262 passed, 2 deselected` in `146.643s` of pytest time. The repository already
declares a `5.0s` per-selector fast-lane threshold in
`scripts/check_test_durations.py`; the JUnit report identified six unwaived selectors
above it. Their measured time is `64.800s`, about 44% of the complete fast lane.

| Selector | Observed time | What the source currently does | Classification |
| --- | ---: | --- | --- |
| `tests/contract/test_asset_checker_contract.py::test_model_led_smoke_requirement_impacts_use_collected_appropriate_selectors` | 20.857s | Builds the focused fast, integration, and release selector views through `collect_pytest_selectors()`. On a cold process cache that invokes the project catalog subprocess once, then filters it. | Highest-priority catalog/collection profile target |
| `tests/contract/test_configure.py::test_cli_read_only_modes_emit_redacted_json_and_runtime_axis_exit_codes` | 13.910s | Starts the real `configure.py` CLI three times (`--dry-run`, pre-apply `--check`, post-apply `--check`) and performs one in-process apply. | Expected process-boundary cost; profile startup versus configuration work before changing it |
| `tests/contract/test_cognitive_program_board.py::test_board_rejects_incomplete_or_self_consistent_denominators[missing-branch-row]` | 11.328s | Re-enters full board validation and reloads the reader inventory from every node workflow document. | Repeated full-validation candidate |
| `tests/contract/test_cognitive_program_board.py::test_board_rejects_incomplete_or_self_consistent_denominators[duplicate-node]` | 7.576s | Same full board-validation path with a different invalid denominator. | Repeated full-validation candidate |
| `tests/contract/test_live_architecture_contract.py::test_live_repository_satisfies_architecture_contract` | 6.074s | Runs the permanent project architecture checker against the live repository. | Whole-repository governance scan; keep authoritative, profile scan inputs |
| `tests/contract/test_regression_descent.py::test_regression_descent_log_classifies_each_discovery_and_names_live_rationale_or_collected_test` | 5.055s | Calls `collect_deterministic_selectors()`, which uses the same project test catalog path when its process cache is cold. | Catalog/collection profile target |

## What This Means

The test count is not the primary signal here. Most selected tests are short; six
selectors dominate the current elapsed time. The first actionable split is therefore
between test execution and repeated repository/catalog/process work.

Two findings are already supported directly by the source:

- Selector collection has a process-local cache, but the cold path starts a catalog
  subprocess. The asset-contract and regression-descent tests both depend on that
  mechanism. A cold-versus-warm measurement is needed before claiming duplicate work
  or changing its correctness boundary.
- The configure test intentionally exercises three true CLI invocations. Replacing it
  with a unit-only test would weaken the public command contract, so any speed-up must
  preserve at least one real end-to-end command boundary.

The cognitive-board and architecture cases are legitimate full-surface checks. Their
current timings identify where to measure next; they do not prove that their validation
should be skipped or moved out of the fast lane.

## Governance Gap

The duration checker correctly rejects these six selectors when run against
`.reports/test-fast.xml`, but the current `make verify` dependency list does not invoke
`test-duration-policy`. Thus the project has a defined threshold and no waiver, while
the aggregate verification command can still pass without applying that threshold.

This is an observation, not a claim that the current Harness migration is incomplete.
It should be handled as a focused test-performance/governance decision with an explicit
choice about whether the threshold belongs in `verify`, CI only, or an advisory report.

## Selected Release-Lane Observation

The manually selected credentialed release lane is deliberately outside the fast lane.
Its first post-migration execution took `213.562s` and failed at `first_resume:blocked`.
The bounded diagnostic records a model-produced source object with an unexpected
`fetch_status` field, which did not satisfy the Wave0/Wave1 structured-output
contracts. This is a correctness failure, not duration evidence for a fast-feedback
test: the release selector remains a manually selected full-real acceptance proof and
must not be weakened, skipped, or silently retried to make timing look better.

Before treating that lane as a performance target, establish a passing baseline and
separate time spent in model calls, retrieval, and graph work. The immediate work is
to preserve its Bundle-authoritative execution/observation boundary and diagnose why
the real model exhausted the relevant structured-output path.

## Recommended Next Change

Open a small dedicated change only after this Run Bundle migration closes. Its first
step should record a baseline JUnit profile twice (cold and warm cache), then make the
lowest-risk improvement supported by that evidence:

1. Measure catalog creation separately from selector filtering and retain detector
   coverage for stale or empty collection.
2. Measure the three configure subprocesses separately; retain one real CLI contract
   while considering a bounded shared setup fixture for the repeated read-only cases.
3. Cache immutable cognitive-board reader records inside the test process only if each
   invalid-fixture case still exercises the complete validator.
4. Decide explicitly whether `make verify` must run `test-duration-policy`; do not add
   an indefinite waiver merely to make the gate green.

## Next-Time Standard

- Capture the JUnit duration profile after a large migration before assuming that the
  number of tests explains slow feedback.
- Treat a slow selector as a measurable ownership question: catalog collection,
  subprocess boundary, repository scan, or test body.
- Preserve the evidence seam while reducing repeated setup; a faster test that no
  longer proves the intended public or governance contract is not an improvement.
