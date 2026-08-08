> req: RUS-004

## ADDED Requirements

### Requirement: Retained session diagnosis is summarized, correlated, and redacted

For a validated retained lifecycle observation, the session store SHALL maintain a bounded versioned `run-summary.json` and `diagnostics/events.jsonl` in addition to the existing manifest/trace. Summary fields SHALL be derived facts only: research id, timestamps, status/terminal outcome, committed phase, generation, durability, last trace sequence, closed failure category/reference, event-journal availability/completeness and latest observed sequence, and fixed artifact references. Event fields SHALL be closed safe categories plus bounded timestamp, sequence, component, event type, severity, phase, opaque work/attempt/tool/model-call ids, duration, validation/retry/exhaustion facts, and non-reversible correlation fingerprint.

The diagnostic event journal SHALL record the runtime dispatch, graph node, worker attempt, model/tool boundary, validation, submit, retry/exhaustion, and terminal lifecycle facts that the runtime actually observes. A future sandbox or pod worker SHALL emit the same closed event shape and correlation fields, allowing the runtime to join cross-process facts into the same run timeline. One deterministic runtime-owned diagnostic reference SHALL be carried unchanged from a terminal incident through lifecycle trace, summary, and correlated events; no session publisher or presentation adapter may create a competing reference. The store SHALL not write user input, prompt/model/tool body, URL, absolute path, credential, exception text, traceback, or arbitrary payload. Each additional file SHALL be atomically written and independently validated; its absence/corruption SHALL be an unavailable observation, not a lifecycle inference. Instrumentation failure SHALL never alter worker, ledger, gate, checkpoint, or graph route authority. If event recording fails after valid observation begins, the summary SHALL report `incomplete`; missing/corrupt journal data is `unavailable`, not silent completion. (`RUS-004`)

For every new run, the retained session store SHALL publish to the same checkpointed canonical
bundle locator used by graph/bootstrap/work-unit artifacts, named
`YYYYMMDDHHMM_r_<research-id>` from the trusted lifecycle-start UTC minute. The
`research_id` suffix SHALL remain the sole graph, checkpoint, lifecycle-binding, and
inspect identity; the locator is only a human-sortable physical-root selector. Lookup by
research id SHALL validate contained non-symlink candidate roots, strict locator grammar,
and marker/manifest identity; it SHALL support old checkpoints with absent locator through
legacy `r_<research-id>` roots without migration and fail closed if more than one valid
candidate represents the same research id. Inspection/list projection SHALL expose the
manifest created time and safe relative locator label without accepting a caller-supplied
path or treating the directory timestamp as authority. (`RUS-004`)

The manifest SHALL record the selected relative locator label and validate it against the
containing directory and checkpoint/session fact before publication or inspection. A
full-fake retained session may use the locator for metadata only; absent real marker or
content artifacts remain an explicit `session_metadata_only` layout rather than a corrupt
or implicitly materialized graph bundle. (`RUS-004`)

#### Scenario: Wave worker exhaustion is inspectable
- **WHEN** all Wave0 attempts terminally fail and the returned lifecycle is blocked at `wave0`
- **THEN** inspection can show the terminal summary, a correlated diagnostic reference, and bounded runtime/node/attempt categories without any raw worker exception

#### Scenario: Execution timeline orders observed components
- **WHEN** a real run enters a node, starts a worker attempt, receives model/tool/validation results, retries, and becomes terminal
- **THEN** its event journal orders those safe events by monotonic sequence and UTC timestamp with one run correlation identity

#### Scenario: Terminal reference is one correlated value
- **WHEN** HITL1 terminally rejects a third unrecognized response or a Wave0 attempt exhausts
- **THEN** the returned terminal incident, lifecycle trace, summary, event timeline, CLI receipt, and inspect view expose the same opaque diagnostic reference when available

#### Scenario: Journal failure remains visible but non-authoritative
- **WHEN** an event write fails after at least one validated run observation
- **THEN** graph/checkpoint/ledger decisions are unchanged and a later valid summary marks the journal `incomplete` rather than implying a complete timeline

#### Scenario: New retained directory sorts by creation time
- **WHEN** a validated run first publishes at `2026-07-22T03:59:53Z` with research id `r_abc`
- **THEN** its physical bundle directory begins `202607220359_r_abc`, while its manifest, inspect argument, binding, and checkpoint identity remain exactly `r_abc`

#### Scenario: Legacy bundle remains inspectable
- **WHEN** an existing contained bundle is named only `r_<research-id>` and its manifest validates
- **THEN** inspect, cleanup, and authorized workbench observation continue to resolve it without directory migration or a changed lifecycle identity

#### Scenario: Duplicate directory identities fail closed
- **WHEN** both a legacy or timestamp-prefixed directory and another valid candidate claim the same manifest research id
- **THEN** lookup marks the session unavailable and does not choose one by timestamp or filename ordering

#### Scenario: Legacy inspection remains honest
- **WHEN** a retained bundle predates summary/events files
- **THEN** inspect shows validated existing facts and marks diagnosis observations unavailable without fabricating a status or modifying the bundle

#### Scenario: Redaction rejects unsafe event content
- **WHEN** an event recorder is offered a secret, host path, raw answer, or traceback
- **THEN** validation rejects or redacts it before persistence and no inspection view emits it
