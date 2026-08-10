# Diagnostics Event Journal -- Current-State Research

> Date: 2026-08-10 | Scope: current application code, tests, OpenSpec, and backlog only.
>
> This is a source-backed finding, not an implementation authorization. The active
> plan remains [`../diagnostics-event-journal.md`](../diagnostics-event-journal.md).

## Conclusion

The application already has the right primary seam: the bounded, redacted
`RunObservationStore` event journal. The problem is its **first-write timing**, not
the absence of a journal. A new Bundle's graph executes before an observation manifest
exists, so its first graph-internal events are intentionally ignored. Reusing that
store is preferable to a second general-purpose log, but the change must establish the
observation before graph execution and must preserve its observation-only contract.

## Evidence

| Finding | Primary-source evidence |
| --- | --- |
| The event model already supports lifecycle, node, attempt, model/tool, validation, retry, exhaustion, and terminal categories with bounded scalar fields. | `deep_research_harness/src/deerflow_deep_research/domain/run_observation.py:68-128` |
| The model has `phase`, `work_id`, and `attempt_id`, but **no `generation`**; `validation_code` is singular. `MAX_EVENT_RECORDS` is 256. | `deep_research_harness/src/deerflow_deep_research/domain/run_observation.py:24-34,105-128` |
| A recorder refuses to write until an observation manifest exists, returning silently; observation failures cannot perturb execution. | `deep_research_harness/src/deerflow_deep_research/runtime/run_observation.py:114-157,287-330` |
| Demo composition supplies both `RunObservationRecorder` and an observation publisher, so this is not an unwired factory. It deliberately sets `progress=None`. | `deep_research_harness/scripts/_demo_core.py:302-350` |
| The graph creates a recorder from that factory, but `BundleGraphExecutor.start()` invokes the graph before it projects/returns a lifecycle result. `ResearchRunExperience` publishes only after dispatch returns. | `deep_research_harness/src/deerflow_deep_research/runtime/bundle_graph.py:298-352,846-860`; `deep_research_harness/src/deerflow_deep_research/runtime/run_experience.py:453-464,607-666` |
| Work-unit producers already emit attempt, validation, submit, retry, and exhaustion observations without authority. | `deep_research_harness/src/deerflow_deep_research/graph/components/work_units.py:488-510,529-539,569-628,737-744` |
| The current Wave1 worker retains the exact parse/semantic error only locally, sends a broad repair category, and collapses a failed repair to `structured_output`. | `deep_research_harness/src/deerflow_deep_research/graph/nodes/wave1/subgraph.py:136-170` |
| Submission validation owns a tuple of closed codes, but the emitted event hard-codes `submission.failed`; the terminal update keeps the exact tuple. | `deep_research_harness/src/deerflow_deep_research/graph/components/work_units.py:62-67,610-624`; `deep_research_harness/src/deerflow_deep_research/domain/work_units.py:1163-1215` |
| `ProgressEmitter` is not durable: the demo disables it and the default emitter has a no-op sink when no stream writer is present. | `deep_research_harness/src/deerflow_deep_research/runtime/node_agent_bridge.py:729-740`; `deep_research_harness/src/deerflow_deep_research/runtime/events.py:53-66` |
| `DemoDiagnosticJournal` is a compact fallback support record, not the lifecycle/event journal; its call sites are terminal/fault paths. | `deep_research_harness/src/deerflow_deep_research/runtime/run_diagnostics.py:30-104`; `deep_research_harness/src/deerflow_deep_research/runtime/run_experience.py:592-605,966-989,1043-1051` |
| The supported inspection CLI currently renders only the last eight `category@phase` entries, so it cannot expose a validation code or attempt identity. | `deep_research_harness/scripts/demo_sessions.py:31-63` |

## Corrections To The Active Plan

- Publication is not terminal-only in implementation: `ResearchRunExperience` publishes
  every record-bearing lifecycle result after dispatch. It is nevertheless too late for
  events emitted during that dispatch, especially a scripted start that runs through
  the graph before its first returned result.
- The correlation spine is incomplete in persisted event rows: bundle identity is
  implicit in the observation directory, while `generation` is absent from `RunEvent`.
- The current storage is a **bounded atomic snapshot journal**, not strict physical
  append-only JSONL: publication trims/resequences entries; `record_event()` drops
  events at capacity; writes replace the file atomically.
  `deep_research_harness/src/deerflow_deep_research/runtime/run_observation.py:184-198,310-330,438-454`

## Implementation Direction

1. Keep `RunObservationStore` as the sole durable event route. Establish its
   non-authoritative observation record after lifecycle admission identifies a valid
   `bundle_id`, but before `BundleGraphExecutor.start()` (or its equivalent execution
   path) invokes graph producers. Keep post-dispatch publishing for the authoritative
   lifecycle projection.
2. Extend the event contract deliberately: record `generation`, define how a bounded
   set of closed validation codes is represented, and add explicit Wave1 initial- and
   repair-validation capture points. Persist canonical safe codes, never `str(error)`;
   repair input must remain unchanged.
3. Make supported read-only inspection render the safe correlation and validation
   facts needed for diagnosis. Preserve the 256-event/size bound and report any
   retention truncation honestly rather than calling it a complete append-only history.
4. Do not route durable diagnosis through `ProgressEmitter` or expand
   `DemoDiagnosticJournal` into a competing event authority.

## Constraints From Current Specs

The active `research-run-session` specification requires the trace to be a bounded,
redacted, atomically published observation of a shared typed Bundle result and forbids
it from becoming lifecycle authority: `openspec/specs/research-run-session/spec.md:33-41,61-75`.
It additionally forbids raw exceptions, model/tool data, URLs, paths, prompts, answers,
and credentials in retained events: `openspec/specs/research-run-session/spec.md:77-111`.
The Wave1 spec permits compact repair categories but forbids raw validator errors from
entering repair: `openspec/specs/wave1-node/spec.md:228-242`.

## Note Location

There is no separate active-plan research-note convention in
`_backlog/plans/README.md:14,60-79`. The closest repository precedent is a plan-local
`research.md` with a companion inventory in
`_backlog/_done/_closed_plans/agent-directory-name-and-module-seam/research.md:1-6`.
This note therefore follows that pattern under the active plan's matching directory.
