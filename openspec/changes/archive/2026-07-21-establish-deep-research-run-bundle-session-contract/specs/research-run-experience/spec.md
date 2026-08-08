> req: RER-003, RER-004, RER-006

## MODIFIED Requirements

### Requirement: Failures are safe, categorized, and diagnosable

The runtime SHALL classify failures at their source into the existing closed
run-failure registry. A user-visible `Fault` or terminal outcome SHALL identify the
safe category, known phase when available, certainty, a concrete next action,
retryability, and an opaque diagnostic reference when a record exists; it SHALL never
print only "retry". Unknown exceptions remain `internal-unexpected`, and a terminal
checkpoint retains only the existing compact safe incident projection.

Before a record-bearing bind exists, a warranted standalone-demo diagnostic record
SHALL remain in the documented project-relative support journal. A bind requires a
validated returned result with non-null research id, status, phase, and generation; an
id alone is insufficient. After bind, including a later local transport fault while the
session remains bound, a warranted diagnostic record SHALL be bounded and redacted at
`diagnostics/records.jsonl` beneath that retained bundle. Each record contains only
opaque reference, time, action/phase, closed category, certainty, and a fingerprint
derived exclusively from those closed safe fields plus run mode. It SHALL not
incorporate raw exception/message text, prompt or answer text, provider content, URLs,
paths, credentials, or a hash of any such value. (`RER-003`)

#### Scenario: A post-bind diagnostic is discoverable with its retained run
- **WHEN** a record-bearing validated lifecycle result binds a research id and then a
  classified terminal or local failure is projected
- **THEN** its opaque diagnostic reference is retained under that bundle's
  `diagnostics/records.jsonl`, while preflight/no-record failures remain only in the
  global support journal

#### Scenario: Changing a raw source cannot change the persisted fingerprint
- **WHEN** two otherwise identical classified failures carry distinct sentinel
  exception messages, prompts, answers, paths, or provider bodies
- **THEN** their diagnostic fingerprint is identical and neither sentinel nor a
  source-dependent digest appears in the record

#### Scenario: Model configuration failure is actionable without leaking configuration
- **WHEN** the real brief cannot start because no usable model configuration is available
- **THEN** the user sees that model configuration is missing, why it is required, the next configuration action, and a diagnostic reference; no key name value, path, exception body, provider request, or raw stack is displayed

#### Scenario: Unknown implementation failure is not falsified
- **WHEN** an unrecognized exception escapes a lifecycle source
- **THEN** the outcome category is `internal-unexpected` with unknown certainty and a safe support action, not checkpoint-inconsistent or a false provider diagnosis

### Requirement: First-run prompts and waiting states explain user intent truthfully

The shared run experience SHALL perform non-network preflight before an interactive
question is collected or graph construction begins. It SHALL report the selected
real/fake mode, model and web-tool readiness, local environment problems, and that a
standalone demo retains an inspectable local bundle only after a record-bearing result
but does not promise cross-process execution recovery. Preflight failure creates no run
reference or retained bundle.

HITL-1 presentation SHALL decode only the recognized versioned research-brief context
into goal, proposed scope, missing information, supported values, and a concise answer
example. Malformed or unknown context SHALL use a safe generic scope request and SHALL
not print machine JSON. HITL-2 presentation SHALL render the graph-owned advertised
decisions with a bounded explanation of each consequence while leaving all decision
validation to the graph.

Working state SHALL show the dispatch action, elapsed local time, and actual observed
activity only. With no stream writer it SHALL identify delivery as `returned_only` and
say it is waiting for the lifecycle result. It SHALL not emit a percentage, infer a
node phase, or claim model/web progress before a valid returned event or result proves
it. (`RER-004`)

#### Scenario: Preflight does not promise a session before one exists
- **WHEN** a real standalone demo has passed preflight but has not received a
  record-bearing lifecycle result
- **THEN** it explains that a local bundle becomes inspectable only after a run is
  identified and does not display an inspect command or promise restart recovery

#### Scenario: Missing prerequisite stops before the user supplies a question
- **WHEN** a real standalone demo lacks a required model or web-search prerequisite
- **THEN** preflight identifies the missing prerequisite, its purpose, and the next action before the question prompt, model request, or graph construction

#### Scenario: HITL-1 is not a truncated machine object
- **WHEN** a valid versioned HITL-1 brief is returned
- **THEN** the user sees a semantic research-scope prompt with the known proposed values and missing fields rather than a truncated JSON line or an internal lifecycle/gate label

#### Scenario: Waiting makes no false progress claim
- **WHEN** a lifecycle dispatch has begun but no graph event or result has been observed
- **THEN** the entry point shows only elapsed local waiting and does not advance its pipeline tracker or claim that any graph node completed

## ADDED Requirements

### Requirement: Shared run updates expose safe session inspection facts

`ResearchRunExperience` SHALL project a bounded session-inspection view into shared
run updates only after a record-bearing validated lifecycle result supplies non-null
research id, status, phase, and generation. The view SHALL contain the opaque
reference, inspectability state, retention truth, honest durability classification,
and at most one closed observation-failure category, but no host path, raw artifact
body, checkpoint payload, or lifecycle authority. It SHALL remain a presentation and
discovery projection and shall not be used to construct start/resume/cancel/status
intent.

CLI and TUI adapters SHALL consume the same session view. Session publication or
inspection failures SHALL set `inspectability=unavailable` with a closed safe
observation category without exposing raw I/O detail; they SHALL NOT replace a valid
`AwaitingInput`, `Terminal`, or source `Fault`, hide its prompt, retry the lifecycle,
or mutate checkpoint state. Publication and post-run diagnostic filesystem work SHALL
be awaited through runtime-owned off-event-loop I/O before `handle()` returns; adapters
pass only a session publisher protocol and do not construct paths or read records.
Textual unmount SHALL not perform required async publication or cleanup. EOF or
interrupt at a CLI-owned paused prompt is a local presentation message only: it SHALL
NOT write a fake interrupted lifecycle record, and the last verified returned record
remains authoritative. (`RER-006`)

#### Scenario: Shared adapters receive one safe retained-run view
- **WHEN** a record-bearing validated start result first identifies a retained research
  run
- **THEN** CLI and TUI receive the same opaque reference and inspectability state
  through `RunUpdate`, with no adapter filesystem access

#### Scenario: Observability failure preserves a valid pending prompt
- **WHEN** a validated start result suspends at HITL-1 but manifest or trace
  publication fails
- **THEN** both adapters still receive the same `AwaitingInput` prompt and opaque
  reference with unavailable inspectability, and no lifecycle response is retried

#### Scenario: Local interruption does not invent a graph transition
- **WHEN** EOF or `KeyboardInterrupt` occurs at a CLI-owned prompt after a bound
  session's last verified `AwaitingInput` result
- **THEN** CLI may render local interruption and the inspect command, but session trace
  and later inspect retain only that last verified result and claim no resume
