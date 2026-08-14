> req: REJ-002

## MODIFIED Requirements

### Requirement: Material execution outcomes retain canonical safe evidence

The Event Journal SHALL retain a bounded process fact at the shared lifecycle,
graph-node, work-attempt, model/tool invocation, deterministic validation, retry,
exhaustion, and terminal-result seams. A validation result SHALL identify whether it is
an `initial`, `repair`, or `post_candidate` validation and retain its bounded collection
of exact canonical rule codes, including an empty collection for a successful
initial/repair validation. For a Wave0 or Wave1 `initial` or `repair` candidate boundary,
the validation result SHALL also retain exactly one closed final response shape:
`empty`, `prose`, `fenced`, `embedded_json`, or `json_object`. A `post_candidate`
validation result SHALL carry only the existing canonical codes from the named
deterministic validation boundary and no response-shape value. A known failure SHALL
retain its existing closed category; a repair attempt SHALL retain its own validation
result rather than overwrite or collapse the initial one. An unclassified boundary
failure SHALL retain only a bounded unknown category. The Journal SHALL NOT retain raw
exception text, stack traces, prompts, answers, model/tool bodies, provider payloads,
credentials, full URLs, host paths, checkpoints, or internal wires. (`REJ-002`)

Newly established Journal events and manifests SHALL use schema version 3. The current
Run Summary representation SHALL remain schema version 2. Version-1 Journal data has
no migration route. A version-2 manifest and its complete correlated event set may be
migrated to version 3 only by the separately invoked offline route when it is explicitly
registered in the source-controlled migration inventory and its exact Bundle identity,
sequence, and retained facts validate. The migration SHALL produce current v3 records
without inferring response shape, `post_candidate` stage, watermark, generation, or
validation provenance that was not retained. It SHALL preserve the current Summary v2
representation without upgrading it.

After cutover, the runtime reader SHALL accept only v3 Journal manifest/event records.
An old, unregistered, malformed, partial, stale, replayed, or failed-migration Journal
SHALL be unavailable or unsupported observation before append or participant
projection. The runtime SHALL not append a v3 event to it, rewrite it, derive current
facts from it, or change graph, recovery, terminal, publication, or lifecycle truth.

#### Scenario: A validation repair preserves both observed rule results
- **WHEN** a work attempt fails an initial validation rule and its repair also fails a
  validation rule
- **THEN** the retained journal exposes the canonical rule code or codes and closed
  response shape for each observed initial/repair result, their common
  Run/work/attempt correlation, and no raw validation message or response body

#### Scenario: A parser-accepted candidate preserves its later closed result
- **WHEN** a Wave0 or Wave1 candidate reaches a later deterministic submission or
  artifact validation boundary and that boundary rejects it
- **THEN** the Journal retains one correlated `post_candidate` validation fact with
  only the boundary's canonical codes and never treats the projection as repair or
  lifecycle authority

#### Scenario: A known provider failure remains a process fact
- **WHEN** a node-agent invocation produces a safe classified provider failure
- **THEN** the journal retains its phase, attempt correlation, and safe category while
  the existing phase/controller remains the only owner of recovery and terminal routing

#### Scenario: An unexpected shared-boundary failure remains honest
- **WHEN** a shared execution boundary catches a non-cancellation failure without a
  known safe classification
- **THEN** the journal retains a bounded unknown outcome and never labels it as a
  provider, validation, or tool failure from exception text

#### Scenario: Registered v2 Journal migrates without upgrading provenance
- **WHEN** the offline migration route processes a registered valid v2 manifest and complete matching event set
- **THEN** it writes a v3 Journal whose retained facts and sequence remain valid, preserves Summary v2, and does not infer unavailable v3-only provenance

#### Scenario: Legacy Journal cannot be read or silently upgraded after cutover
- **WHEN** inspection or a producer encounters a v1, v2, partial, or unregistered Journal after cutover
- **THEN** it returns only the bounded unavailable or unsupported observation outcome, appends and rewrites nothing, and leaves the Run outcome unchanged

#### Scenario: Older Journals remain readable and are never silently upgraded
- **WHEN** the approved offline migration decoder receives a registered complete v2 Journal before cutover
- **THEN** it reads only the retained source facts to create its separately validated v3 output, while the post-cutover runtime reader rejects the old source and never silently upgrades it
