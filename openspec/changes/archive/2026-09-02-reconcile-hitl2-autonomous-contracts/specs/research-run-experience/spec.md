> req: RER-001, RER-002, RER-003, RER-004, RER-005, RER-006, RER-007, RER-008, RER-009, RER-010, RER-011, RER-012, RER-013, RER-014

## MODIFIED Requirements

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
not print machine JSON. HITL2 SHALL be projected only as graph-owned autonomous phase
progress from a verified trace/result; the run experience SHALL NOT render an HITL2
decision prompt, route menu, Answer action, or pending-input recovery.

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

#### Scenario: Autonomous HITL2 creates no second prompt
- **WHEN** a verified returned trace records HITL2 after the accepted Wave2 path
- **THEN** the shared run experience projects phase progress without `AwaitingInput`,
  an Answer action, or any advertised internal route

### Requirement: Verification protects the production-shaped first interaction

The change SHALL include deterministic tests at the run-experience Interface and a
`SCRIPTED_REAL_WORKFLOW` using the real bootstrap, real HITL-1, interrupt,
checkpointer, and reflected lifecycle projection with replayed external dependencies.
It SHALL cover first HITL-1 suspension, HITL-1 follow-up, autonomous HITL2 without a
second pending input, status, trace repetition/divergence, malformed wire values,
source failure categories, redaction, diagnostic records, cancellation outcome
distinction, and CLI/TUI shared adapter fixtures.

A stubbed top-level lifecycle result may supplement adapter tests but SHALL NOT be the
only proof of the first real suspension. Credentialed provider/tool acceptance is
supplemental live evidence and SHALL preserve only redacted category/reference data.
(`RER-005`)

#### Scenario: A favorable stub cannot hide the phase-lag regression
- **WHEN** a test suite exercises the standalone first interaction
- **THEN** at least one deterministic collected test reaches the production interrupt projection with checkpoint phase `bootstrap` and pending phase `hitl1`, so a fixture that manually sets phase `hitl1` cannot be the sole regression proof

#### Scenario: A synthetic HITL2 prompt cannot be production-shaped evidence
- **WHEN** CLI, TUI, or run-experience adapter tests need a choice-mode pending input
- **THEN** they use the current typed HITL1 choice contract, while autonomous HITL2
  evidence proves graph continuation without constructing an HITL2 `AwaitingInput`
