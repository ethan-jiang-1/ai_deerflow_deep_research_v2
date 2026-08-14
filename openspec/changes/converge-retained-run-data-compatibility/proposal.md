## Why

The runtime still carries four retained-data compatibility surfaces whose old readers
can outlive their policy: graph checkpoint `repair_counts`, Bundle terminal
`REPAIR_EXHAUSTED`, Journal v1/v2 records, and terminal results that omit a diagnostic
location. The Data Owners have approved a clean retained-data cutover: only data
explicitly registered by the source-controlled implementation migration inventory is supported;
ignored local demo/report roots and every unregistered external or retained record
receive no support promise and must be rejected without rewriting or provenance
upgrade.

## What Changes

- **BREAKING (checkpoint data):** retire the frozen `repair_counts` checkpoint field
  after a decoder-based inventory and zero-write migration/rejection proof. The gate
  kernel remains the sole repair authority; an unregistered old checkpoint fails before
  graph mutation and is not reconstructed or rewritten.
- **BREAKING (Bundle terminal data):** retire `REPAIR_EXHAUSTED`. An explicitly
  registered old Bundle may be migrated only through the approved terminal-data route;
  an unregistered old reason fails closed and is never mapped to completed, a generic
  failure, or another current terminal fact.
- **BREAKING (Run Observation data):** migrate registered Journal v2 manifests/events
  to v3, then retire old Journal readers. The current Run Summary v2 representation
  remains current. Unregistered v1/v2 Journal data is rejected as an unavailable or
  unsupported observation and cannot affect graph, lifecycle, retry, terminal, or
  publication truth.
- **BREAKING (persisted/public terminal results):** retire reading a terminal result
  that lacks the required diagnostic-location fact. It is rejected before participant
  projection; it cannot be inferred as `bundle_journal`, resume a Run, or create an
  external diagnostic fallback. Registration records rejection only for this family;
  it never permits a missing location to be migrated or defaulted.
- Record source-owned dry-run counts, old/new reader-writer matrices, restart/replay
  proof, post-cutover counts, and the only legal recovery: a separately approved
  complete local reader hotfix/revert. No partial reader restore or payload rewrite is
  a legal rollback.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `gate-kernel`: make the gate-owned repair state the sole repair budget/attempt
  authority after the frozen checkpoint field is removed.
- `research-graph-lifecycle`: require an explicit migration/rejection boundary before
  an old graph checkpoint can reach graph execution.
- `deep-research-harness-run-bundles`: retire the persisted legacy terminal reason
  without granting an old Bundle another lifecycle or recovery route.
- `run-event-journal`: move supported v2 Journal records to the v3 contract, retire
  old Journal readers, and preserve current Summary v2 plus incomplete-observation
  truth.
- `research-run-experience`: reject legacy terminal results with an absent diagnostic
  location without changing the typed lifecycle or publication authority.

## Impact

- Expected implementation is confined to `deep_research_harness/` persisted-state,
  Bundle, Journal, and terminal-result readers/writers plus focused deterministic
  migration and negative-path tests.
- The Data Owner decision treats the ignored `.deep-research-demo-runs/` and
  `.reports/` roots as unregistered evidence, not a production support inventory. It
  records their observed counts only as a risk floor; it does not infer any external,
  host, deployment, or retained-data inventory from their contents.
- Ordinary downstream work neither modifies nor source-browses the `deerflow/`
  gitlink. This change owns no DeerFlow parser, external provider data, deployment
  migration, support service, retained-data discovery, or external Python consumer
  contract.

## Program Focus

- **Program outcome:** Every admitted retained runtime record has one explicit
  disposition: it is registered and migrated to the current contract, or it is
  rejected at its local reader without mutation, lifecycle recovery, or provenance
  upgrade.
- **Candidate / obligation budget:** PC-C03, PC-C04, PC-C06, RC-C06, EV-C05, RS-C05
- **Declared workstream order:** repair-lifecycle-data, observation-result-data
- **Program decision authority:** Data Owners approve the registered-data inventory,
  terminal rejection/migration decision, retention closure, and whole-program archive.
  The program authority approves only frozen scope, order, and archive closure; it
  owns no checkpoint, Bundle, Journal, terminal result, writer, or lifecycle fact.
- **Shared archive invariant:** Gate-owned repair data remains the only repair
  authority; Bundle-local State remains the sole lifecycle authority; Journal and
  terminal results remain bounded projections. A rejected record never mutates,
  restarts, resumes, publishes, or strengthens a Run.
- **Program failure / recovery:** A stale, malformed, unregistered, partially
  migrated, or replayed record reaches its named deterministic rejection boundary.
  Emergency rollback is a separately approved hotfix/revert of the complete affected
  reader plus paired tests; it never revives one legacy field, rewrites a payload, or
  turns an observation into lifecycle authority. A failed workstream remains active
  for approved repair, rollback, or plan-level re-scope; neither workstream archives
  independently.
- **Split / expansion rule:** No external or host data discovery, DeerFlow change,
  support service, provider migration, broad retained-data scan, public API, model,
  graph topology, new terminal reason, or new Journal authority enters scope. Any
  request for retained support outside the approved inventory requires a later change
  with its own inventory, retention, migration, and recovery decision.
- **Not in scope:** Repair policy semantics, gate budgets, lifecycle routes, user
  actions, Bundle identity, Journal capacity, Summary v2 schema, provider retry,
  terminal category selection, credentialed/live evidence, or the `deerflow/` gitlink.

### Workstream Focus: repair-lifecycle-data

- **Primary module / causal owner:** Domain persisted-lifecycle contract:
  `ResearchGraphState` checkpoint validation and `TerminalReason` decoding own the
  retired data admission; the gate kernel remains the independent current repair
  authority.
- **Seam classification:** deterministic-guardrail because checkpoint and Bundle
  decoding either admits a versioned record or rejects it before a graph/lifecycle
  transition.
- **Question:** How can registered checkpoint and Bundle terminal data retire
  `repair_counts` and `REPAIR_EXHAUSTED` while retaining deterministic gate ownership,
  exact terminal truth, restart/replay safety, and whole-reader recovery?
- **Necessary adjacent/external contracts:** `gate-kernel` answers current repair
  budget/attempt ownership; `research-graph-lifecycle` answers graph admission before
  execution; `deep-research-harness-run-bundles` answers Bundle-local lifecycle
  authority. Data Owners answer only the approved inventory and old terminal
  migration/rejection disposition; no external storage is implied.
- **Evidence seam:** Decoder-based dry run of every registered checkpoint/Bundle,
  followed by write-reload-replay tests, planted legacy records, and post-cutover zero
  counts at the local reader boundary.
- **Not in scope:** Changing gate verdicts or budgets, mapping an old terminal to a
  new one without an approved record, generic checkpoint recovery, payload surgery,
  external Bundle discovery, or new terminal semantics.
- **Triggered review policies:** change-admission, authority-and-projections, control-and-recovery, workflow-outcome-review, control-placement, participant-outcomes
- **Candidate / obligation IDs:** PC-C03, PC-C04, RS-C05
- **Target / retirement:** `gate_attempts_by_phase` and
  `repair_budget_by_phase` remain the target repair facts; `repair_counts` retires.
  Current typed blocked outcomes remain the target terminal facts;
  `REPAIR_EXHAUSTED` retires without a synthetic replacement.
- **Surface grade:** Checkpoint and Bundle terminal fields are persisted,
  cross-process compatibility surfaces; their readers require an explicit data
  disposition, not an implementation-only deletion.
- **Decision authority:** Data Owners approve the registered record inventory and
  terminal disposition. Domain Lifecycle Owner owns decoding semantics; Gate Owner
  owns current repair facts. Program authority owns none of those facts.
- **Negative path / recovery:** An unregistered, stale, malformed, or replayed old
  checkpoint/terminal record returns its existing bounded unsupported-state outcome
  before graph or lifecycle mutation. A complete local reader hotfix/revert is the only
  recovery and preserves gate and Bundle authority.

#### Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Checkpoint `repair_counts` retirement | Data Owners approve registered inventory; no decoder guesses a schema | Research-state decoder admits only current/migrated input; gate kernel owns repair facts | non-bypassable | Old input cannot execute, reset repair budget, or mutate graph; recovery restores the complete reader | Reuses typed state validation; avoids a second repair counter or compatibility switch | Decoder dry run plus write/reload/replay and planted legacy checkpoint tests |
| Bundle `REPAIR_EXHAUSTED` retirement | Data Owners approve migration or rejection; no projection invents a replacement reason | Bundle-state decoder validates terminal reason; lifecycle State remains fact authority | non-bypassable | Old failure cannot become success or a new terminal fact; complete-reader revert only | Reuses closed terminal validation; avoids a terminal alias mapper | Legacy Bundle record read/projection negative and terminal identity tests |

#### Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Unregistered or stale checkpoint with `repair_counts` | Research-state decoder | Data Owner may register/migrate it or approve a complete reader revert | Bounded unsupported-state denial before graph invocation | Use a registered current checkpoint or start a distinct current Run | Decoder and graph-admission negative tests |
| Old `REPAIR_EXHAUSTED` Bundle terminal | Bundle-local State decoder | Data Owner may migrate a registered record or approve a complete reader revert | Bounded unsupported terminal without lifecycle rewrite | Inspect only through an approved migration workflow; no resume/retry is inferred | Bundle reload and terminal-projection negative tests |

### Workstream Focus: observation-result-data

- **Primary module / causal owner:** `runtime/run_observation.py` retained Journal
  reader/writer; it owns bounded observation persistence while
  `domain/run_experience.py` remains the adjacent typed terminal-result contract.
- **Seam classification:** deterministic-guardrail because Journal and terminal-result
  readers must classify a record before any observation or participant projection can
  be emitted.
- **Question:** How can registered Journal v2 records migrate and retained terminal
  results reject when their diagnostic location is absent, while retaining Summary v2,
  incomplete-observation truth, exact diagnostic publication facts, and no lifecycle
  authority in any projection?
- **Necessary adjacent/external contracts:** `run-event-journal` answers Journal
  schema/health and observation limits; `research-run-experience` answers typed
  terminal projection and legal next action. Data Owners answer registered Journal and
  result inventory plus retention closure; external Journal, Support Handoff, and
  diagnostic services are explicitly outside the contract.
- **Evidence seam:** Manifest/event and terminal-result decoder dry runs, v2-to-v3
  migration/reload checks, planted incomplete/stale/missing-location inputs, and
  post-cutover reader/writer count evidence.
- **Not in scope:** Changing summary v2, Journal capacity/retention policy, terminal
  categories, provider retries, Support Handoff, external diagnostic fallback, CLI/TUI
  commands, or lifecycle recovery.
- **Triggered review policies:** change-admission, authority-and-projections, control-and-recovery, workflow-outcome-review, control-placement, participant-outcomes
- **Candidate / obligation IDs:** PC-C06, RC-C06, EV-C05
- **Target / retirement:** Journal v3 is the only current manifest/event contract;
  Summary v2 remains current. Legacy Journal v1/v2 readers and a terminal result that
  omits `diagnostic_location` retire after registered data closes.
- **Surface grade:** Journal manifests/events and persisted/public terminal results are
  persisted observation and participant-contract surfaces, never lifecycle sources.
- **Decision authority:** Data Owners approve the inventory/retention decision;
  Observation Owner owns Journal decoding and health; Run Experience Owner owns typed
  terminal projection. Program authority owns none of those facts.
- **Negative path / recovery:** An unregistered or partial Journal is unavailable or
  unsupported observation only; a missing-location terminal is rejected before
  participant projection. Neither can publish, resume, retry, or create an external
  diagnostic. Recovery is a complete local reader hotfix/revert with its paired tests.

#### Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Journal v1/v2 reader retirement | Data Owners approve registered v2 migration/closure; no inspector infers data | RunObservationStore validates manifest/event version and Journal health | non-bypassable | Old/partial data cannot gain v3 facts or alter lifecycle; recovery restores the complete reader | Reuses bounded Journal validator; avoids parallel external migration reader | v2-to-v3 dry run/reload plus stale/incomplete negative tests |
| Missing terminal diagnostic location retirement | Data Owners approve registered-result migration/rejection; no UI guesses publication | Typed terminal-result decoder validates location before projection | non-bypassable | Missing location cannot become `bundle_journal`, support fallback, retry, or resume | Reuses `RunFailure` validation; avoids a presentation-only compatibility branch | Terminal decode and CLI/TUI projection contract negatives |

#### Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Unregistered, stale, or partial Journal v1/v2 record | Journal manifest/event decoder | Data Owner may register/migrate the record or approve a complete reader revert | Unavailable or unsupported observation without graph/lifecycle mutation | Use a current registered Journal; no inspection-based recovery | Journal decoder, no-write, and incomplete-health tests |
| Persisted/public terminal missing diagnostic location | Typed terminal-result contract | Data Owner may migrate a registered result or approve a complete reader revert | Bounded unsupported terminal projection before participant output | Start a distinct current Run; no inferred diagnostic or resume | RunFailure decoder and participant projection negative tests |
