## 1. Reconcile The Approved Log-Only Contract

- [x] 1.1 Reconcile the partial custom-event implementation, focused tests, and requirement-evidence metadata to this approved log-only design; preserve unrelated worktree changes.
- [x] 1.2 Retire `RTO-002` in `openspec/governance/req-registry.yaml` during apply, preserving its no-reuse history and removing it from all active requirement evidence; do not repurpose the id.
- [x] 1.3 Replace old event-schema, custom-helper, raw-writer, and `ProgressEmitter` red tests with focused log-only schema, level, redaction, duplicate, logger-failure, and cancellation tests.
- [x] 1.4 Update trusted-runtime and lifecycle tests for trusted outer thread/run log extras, DeerFlow-filter-owned trace injection, absent-trace honesty, exactly one `BundleLifecycle` log for Gateway and Local Session Workbench callers, and caller-correlation rejection.

## 2. Retire Unsupported Transport And Establish The Facade

- [x] 2.1 Remove the partial `deep_research.progress.v1` facade, `ProgressEmitter`, event-only projection, injectable event sink, custom-event helper assumptions, and all raw progress emission; leave no compatibility route for an uninstalled DeerFlow custom-event API.
- [x] 2.2 Implement the typed safe standard-log facade in `runtime/events.py`: validate a closed safe observation, select the required level, invoke an owner module logger best-effort, preserve cancellation, and never configure root logging or provide a trace field.
- [x] 2.3 Extend the trusted runtime envelope only with safe outer thread/run values that the trusted boundary already owns; bind them after admission/resolution and pass the Bundle-bound projection through `GraphInvocationContext`, `NodeBuildDependencies`, and work-unit/validation configuration as a non-checkpointed protocol.
- [x] 2.4 Add focused source/behavior guards forbidding raw writer use, custom-event imports/helpers, `ProgressEmitter`, private Gateway journal access, and unsafe data in ordinary log projection paths.

## 3. Instrument Fact Owners

- [x] 3.1 Add `logging.getLogger(__name__)` and one facade call at RuntimeAdapter's trusted adaptation/denial boundary and BundleLifecycle's approved admission, cancellation, and terminal fact boundaries; keep existing typed lifecycle ownership unchanged and emit no duplicate from BundleControl.
- [x] 3.2 Instrument graph builder/node-wrapper phase entry/completion, gate verdict, and boundary-failure owners through the non-checkpointed protocol, with focused tests proving no downstream duplicate, domain-to-runtime import, or route/checkpoint mutation.
- [x] 3.3 Instrument work-unit submission, attempt start/end, retry, and exhaustion owners through the same protocol, with focused tests proving closed counts/codes and no `INFO`-or-higher loop/state-write noise.
- [x] 3.4 Instrument node-agent bridge and topic-planning/Wave0/Wave1 validation owners for model/provider/tool and structured-output facts, preserving existing Journal recorder calls, bounded recovery, and typed results.
- [x] 3.5 Instrument safe Journal persistence/retention degradation only at its storage owner, with no transport replacement or log-derived recovery.

## 4. Verify And Record Boundary Evidence

- [x] 4.1 Run facade, runtime-adapter, Bundle-lifecycle, graph-wrapper, work-unit, node-agent, validation, Journal, observation-separation, cancellation, trusted-correlation, and source-guard suites; record deterministic evidence for every owner-inventory row.
- [x] 4.2 Run `python3 openspec/governance/check_project_reqs.py .`, `cd deep_research_harness && UV_OFFLINE=1 make verify`, `openspec validate instrument-deep-research-runtime-observability --strict`, and `git diff HEAD --check`.
- [x] 4.3 Record scope evidence with `git status --porcelain=v1 --untracked-files=all`, `git ls-files --stage deerflow`, `git submodule status -- deerflow`, `git -C deerflow status --porcelain=v1 --untracked-files=all`, and `git diff --submodule=short`; confirm no `deerflow/` source, gitlink-pointer, or dependency upgrade change is part of this change.
