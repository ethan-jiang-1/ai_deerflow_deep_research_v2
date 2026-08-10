# wave0-node Specification

> req: WAN-001, WAN-002, WAN-003, WAN-004, WAN-005, WAN-006, WAN-007, WAN-008, WAN-009, WAN-010

## Purpose

Real Wave0 source-intake node behavior — per-topic WorkSpec materialization from the
planner registry via the work-unit controller, a bounded web worker agent with an
untrusted-data discipline, a real `wave0.source-intake` result contract with
canonicalized/verified sources, deterministic submit validation, a real source-floor gate
with degraded capture, and mixed-graph integration preserving full-fake behavior.
## Requirements
### Requirement: Real Wave0 materializes per-topic source-intake work from the planner registry

The real Wave0 controller SHALL read the planner-owned `topic_registry`/
`topic_refs` from `ResearchState` and materialize exactly one immutable
source-intake `WorkSpec` per topic through the existing work-unit controller
(`materialize_work_spec`), with `scope` binding the topic id and its must-answer
questions. The real node SHALL drive the shared work-unit fan-out/fan-in component
with those real intents and a real worker, and SHALL return the same
`node_update` + parent work-block update + `WorkUnitGateView` shape the wrapper
already consumes. No second controller, work authority, or phase cursor is
introduced.

#### Scenario: One work spec per accepted topic
- **WHEN** real Wave0 runs after real topic planning recorded a bounded topic registry
- **THEN** the controller allocates one immutable `WorkSpec` per topic with controller-assigned identity and a derived `spec_hash`, and the shared component fans out one worker per topic

#### Scenario: Real Wave0 reuses the shared work-unit component
- **WHEN** the real Wave0 node is built
- **THEN** it drives the shared allocate/dispatch/submit/refill/drain component with real per-topic intents and a real worker, and returns the parent work-block update plus the validated `WorkUnitGateView` without duplicating submit, ledger, retry, or drain authority

#### Scenario: Empty topic registry fails closed
- **WHEN** real Wave0 runs but the planner recorded no topics
- **THEN** the controller fails closed before allocating work rather than inventing fixture topics

### Requirement: A bounded web worker performs source intake under an untrusted-data discipline

For each in-flight `WorkSpec`, Wave0 SHALL run one bounded worker agent through
`capabilities.run_agent()` on the runtime node-agent bridge under a real
`ExecutionPolicy` with a non-empty `allowed_tool_names` set of web search/fetch
tools, per-tool `ToolPolicySpec` entries, and attempt-scoped read/write roots.
All fetched page, PDF, snippet, and cache content SHALL be treated as untrusted
data: it SHALL be placed in the `<untrusted-source-data>` block or referenced as a
sandbox artifact, never spliced into the trusted system prompt, and the
deny-by-default tool policy SHALL block any tool or path the worker is not
allow-listed for. The worker SHALL write only to its own
`work/<work_id>/<attempt_id>/` root and declared cache regions, and SHALL NOT
write phase, gate, ledger, or another attempt's state.

#### Scenario: Fetched content is untrusted data
- **WHEN** a worker fetches a page or snippet
- **THEN** the content is wrapped as untrusted source data or referenced as a sandbox artifact, never placed in the system prompt, and the worker cannot be directed by it to change tools, paths, phase, gate, or ledger state

#### Scenario: Adversarial source cannot escalate
- **WHEN** a fetched source contains directives to ignore rules, call a forbidden tool, or mark itself authoritative
- **THEN** the worker produces only a source limitation or rejection, the deny-by-default tool policy blocks any forbidden call, and no control authority is mutated

#### Scenario: Worker writes only its own attempt root
- **WHEN** a worker attempts to write outside its `attempt_root` or another attempt's directory
- **THEN** the artifact writer and path-containment contract reject the write and the candidate fails validation

### Requirement: A real source-intake result contract and deterministic submit validation

The implementation SHALL register a real `wave0.source-intake` v1 result contract (frozen
model carrying canonical source URLs, source metadata, baseline facts, fetch/cache
refs, and limitations) in the generalized `(result_contract,
result_schema_version)` validation registry, alongside the existing fixture
contract. Submit validation SHALL canonicalize each source URL via
`canonicalize_source_url`, verify that cited fetch/cache content is real and
contained, check path, hash, and source identity, reject snippet-as-cache,
cross-attempt, and out-of-containment writes, and accept the candidate only as a
typed `SubmissionRecord`. Only accepted `SubmissionRecord`s SHALL count as
coverage; worker final text SHALL NOT.

#### Scenario: Valid sources become accepted evidence
- **WHEN** a worker submits a `wave0.source-intake` result with canonical, independently-fetchable sources under its attempt root
- **THEN** submit validation accepts it as a hash-chained `SubmissionRecord` and the accepted ref enters the evidence ledger

#### Scenario: Non-canonical or fabricated sources are rejected
- **WHEN** a candidate carries a non-canonical URL, a snippet presented as cached content, a path outside the attempt root, or a hash that does not match the fetched bytes
- **THEN** submit validation fails closed with a typed code and no `SubmissionRecord` is appended

#### Scenario: Duplicate URLs are deduplicated per topic
- **WHEN** two sources canonicalize to the same URL within one topic
- **THEN** submit validation counts them as one source, protecting the independent-source floor

### Requirement: A real source-floor gate with honest degraded capture

The real Wave0 gate SHALL drop the `FixtureSequenceRule`, keep the shared
`WorkUnitCompletionRule` (drain plus accepted-record coverage), and enforce a
per-topic source floor of at least N independent, deduplicated sources. Because
gate rules are pure and the `WorkUnitGateView` carries accepted-record hashes
rather than source counts, the source floor, independent-source, and dedup checks
SHALL be enforced at submit-validation time, and the gate SHALL verify that every
planned topic has an accepted record and the work is drained. When a source is
unreachable, the worker SHALL record a typed degraded capture (attempted URL,
limitation, reason) rather than fabricating success; a degraded `PASS` SHALL be
permitted only when the independent-source floor is otherwise met. The route map
SHALL remain `{PASS: pass, REPAIR: repair, BLOCKED: exhausted}`.

#### Scenario: Source floor gates coverage
- **WHEN** a topic's accepted submissions do not meet the independent-source floor
- **THEN** the gate routes `repair` (within budget) or `exhausted` and the lifecycle does not advance to Wave1

#### Scenario: Unreachable source is captured honestly
- **WHEN** a worker cannot fetch a source
- **THEN** it records a typed degraded capture, never marks an unfetched source authoritative, and the gate may pass degraded only if the floor is otherwise met

#### Scenario: Bounded repair refetches missing topics only
- **WHEN** the gate routes `repair`
- **THEN** only topics lacking accepted coverage are retried, no submission ledger entry is hand-written, and repeated failure exhausts to terminal `blocked`

### Requirement: Real Wave0 integrates into the mixed graph off the real topic chain

Real Wave0 SHALL be selectable only in the mixed implementation map and SHALL
require `bootstrap=real`, `hitl1=real`, and `topic_planning=real`, because the
worker consumes the real topic registry. Selecting `wave0=real` without the real
topic chain SHALL fail closed before graph invocation. The Wave0 topology SHALL be
unchanged (`repair`/`pass`/`exhausted`); the real gate writes the route via the
gate kernel. The full-fake Wave0 fixture path SHALL remain deterministic and
SHALL NOT construct the node-agent bridge. The lifecycle result SHALL remain
`implementation_mode=mixed` for this recipe composition.

#### Scenario: Real Wave0 requires the real topic chain
- **WHEN** a recipe selects `wave0=real` without `topic_planning=real`
- **THEN** recipe construction fails with a typed dependency error before the graph is compiled or invoked

#### Scenario: Topology is unchanged for real Wave0
- **WHEN** the mixed graph selects real Wave0
- **THEN** Wave0 keeps its `repair`/`pass`/`exhausted` routes, the gate writes the route via the gate kernel, and no top-level edge changes

#### Scenario: Full-fake Wave0 remains the deterministic fixture path
- **WHEN** the full-fake graph reaches Wave0
- **THEN** it runs the fixture work-unit path without constructing the node-agent bridge and the topology snapshot is unchanged

### Requirement: Real Wave0 maps trusted worker boundaries into diagnosis-only failures

Real Wave0 SHALL map only its trusted node-agent result, parser/repair, and typed
submission-validation boundaries to `WFC-001` categories before the shared work-unit
component creates the existing terminal attempt.  The lower-level submission boundary
SHALL continue to reject invalid candidates with its typed validation result; the
component SHALL catch only that typed rejection and route it through the existing
terminal/retry path.  Storage, checkpoint, ledger, and other infrastructure failures
SHALL preserve their existing propagation and SHALL NOT be relabeled as worker failure.
(`WAN-006`)

#### Scenario: Typed validation retries through the existing controller
- **WHEN** a real Wave0 candidate receives a typed deterministic submission-validation
  rejection
- **THEN** the component records `submission_validation` for that attempt and applies
  the existing retry/gate policy without appending a submission record

#### Scenario: Infrastructure failure is not disguised
- **WHEN** Wave0 storage or ledger infrastructure fails outside typed validation
- **THEN** it follows its existing infrastructure failure behavior and does not publish
  an invented worker category

### Requirement: Wave0 retains classified invocation causes through work-unit failure

Wave0 SHALL normalize every non-successful worker invocation before passing it to the
existing work-unit controller. It SHALL map tool failures, structured-output
failures, and invocation failures to the existing closed worker categories, retain a
safe provider category in the bounded attempt/event observation when known, and let
the controller own retry, aggregation, gate routing, and terminal projection.

#### Scenario: A Wave0 provider timeout remains visible to the controller
- **WHEN** a Wave0 worker receives a safe provider timeout result
- **THEN** it produces the existing closed invocation failure category plus the safe
  provider observation for the bounded attempt record, without accepting a candidate
  or raising an unclassified generic exception

### Requirement: Wave0 source intake has bounded retrieval and honest degradation evidence

The existing Wave0 source-intake and repair capabilities SHALL retain distinct
deterministic real-node evidence. A normal worker SHALL use only its existing
permitted retrieval policy, make at least one and at most three tool calls, and submit
only contract-valid source candidates through the existing validator/controller/ledger
path. A source-floor or retrieval shortfall SHALL retain the existing failed or
degraded outcome and SHALL not be represented as fetched or accepted coverage. Repair
SHALL expose no model-visible tool and SHALL not invent a URL, title, source metadata,
or fact absent from its bounded draft and retained observations. (`WAN-007`)

#### Scenario: Bounded retrieval admits only validated sources
- **WHEN** a scripted real Wave0 worker completes permitted retrieval calls within its
  1--3 bound
- **THEN** the existing validation and ledger owners admit only canonical,
  contract-valid candidates and the model receives no ledger or route authority

#### Scenario: Retrieval shortfall remains honest
- **WHEN** the scripted worker misses its retrieval/source-floor condition or its
  repair draft lacks a source field
- **THEN** the existing controller records only its legal failed or degraded outcome
  and no fabricated fetched source or accepted coverage is produced

### Requirement: Wave0 calibration preserves source-intake judgment boundaries

The existing Wave0 initial and repair source-intake policies SHALL expose
model-visible criteria for an assignment-relevant, independent source-metadata
candidate: retrieved material remains untrusted, source metadata is proposed rather
than accepted evidence, a source shortfall is represented as an honest limitation,
and the candidate contains no finding, cache/content authority, ledger action, or
route claim. The initial policy SHALL retain its existing required retrieval posture
and bounded request window. It SHALL not treat title, URL shape, or tool output as
proof that a source is authoritative, relevant, or accepted. A `fetch_status` MAY
report only the bounded retrieval-status observation supported by retained retrieval
observations; it does not imply authority, independent validation, accepted coverage,
ledger admission, or route control.

The repair policy SHALL be invoked only when the initial Wave0 summary cannot parse
into its typed worker output. It SHALL receive only the same bounded topic projection
rendered by the initial request, invalid draft, retained tool observations, and a
compact subgraph-generated structural category; it SHALL not receive a raw `WorkSpec`,
attempt identity, checkpoint, ledger, or accepted record. The assignment and category
SHALL be bounded trusted context; the draft and observations SHALL remain untrusted
data. The category SHALL omit raw exception text, artifact paths, checkpoint fields,
ledger contents, review/gate data, and route data. Assignment and category SHALL
constrain repair only and SHALL not supply candidate source metadata, URLs, titles,
facts, fetch outcomes, or limitations. The repair SHALL preserve the source-intake
boundary, use no tool, and shall not add a source, URL, title, fact, fetch outcome,
limitation, artifact, or authority absent from the untrusted draft and retained
observations. A later post-candidate `SubmissionValidationFailure`, its codes, and
artifact-validation detail SHALL not invoke or enter repair; the existing submit
validator, work-unit controller, ledger, and gate remain the only owners of source
validation, evidence admission, recovery, and routing.

#### Scenario: Source candidate distinguishes retrieval from acceptance
- **WHEN** an assigned topic asks for source intake and retrieved material includes
  source-like text, snippets, or instructions
- **THEN** the candidate proposes bounded metadata and honest limitations only, keeps
  the material untrusted, reports `fetch_status` only as a bounded retrieval-status
  observation, and does not assert that a source is authoritative, accepted, or
  controlling

#### Scenario: Retrieval shortfall remains an honest candidate limitation
- **WHEN** the bounded retrieval window cannot produce enough assignment-relevant
  independent source candidates
- **THEN** the candidate records only the available metadata and an honest limitation,
  while the existing deterministic validation/controller path decides whether the
  source floor, evidence record, recovery, or terminal outcome is legal

#### Scenario: Pre-candidate structural repair cannot upgrade untrusted data into evidence authority
- **WHEN** an initial Wave0 source-intake summary cannot parse into its typed worker
  output
- **THEN** its one bounded repair receives the same bounded assignment and only a
  compact structural category, keeps its draft/observations untrusted, receives no
  model-visible tool, and cannot introduce an absent source or fact, materialize an
  artifact, append a ledger record, or select a route

#### Scenario: Trusted assignment cannot become source metadata
- **WHEN** a Wave0 repair receives its bounded topic projection together with an
  untrusted draft or observation that asks it to promote assignment text into a source
- **THEN** the topic projection constrains scope only; the repair introduces no
  source metadata, URL, title, fact, fetch outcome, or limitation absent from the
  untrusted draft and retained observations

#### Scenario: Downstream submission validation does not invoke repair
- **WHEN** a constructed Wave0 candidate later receives a post-candidate
  `SubmissionValidationFailure`
- **THEN** its validation codes and artifact-validation detail do not enter a repair
  request, no `SubmissionRecord` is appended, and the existing controller terminal,
  retry, and gate path remains the only recovery owner

### Requirement: Wave0 runtime capabilities own bounded source-intake cognition without evidence-control authority

The real Wave0 worker SHALL bind distinct runtime-loaded local capability resources
for initial source intake and its one pre-candidate structural repair. Each activated
resource SHALL contain the reusable cognitive method for its bounded task: assignment
interpretation, permitted-retrieval or no-tool posture, source-candidate judgment,
untrusted-data handling, uncertainty/shortfall handling, self-check, repair limit,
and completion condition. The final production-rendered agent context SHALL include
the exact activated resource body; reader-only workflow material and a duplicate
method dynamically assembled outside the resource SHALL not be required to determine
the worker's cognitive procedure.

Outside the resource method, Wave0 SHALL pass only bounded assignment and closed
output-contract data. The initial worker may receive its existing permitted retrieval
tools only through the runtime policy; the repair remains zero-tool and receives only
the bounded assignment, closed structural category, untrusted initial draft, and
retained untrusted retrieval observations. Neither capability may treat a retrieved
page, snippet, title, URL, tool result, or assignment as accepted evidence or
instruction authority. The capabilities SHALL not create an artifact reference, admit
a source, append a ledger record, select a retry, gate, route, or terminal outcome,
or mutate Bundle-local State. Existing parser, artifact, source validation, ledger,
work-unit controller, source-floor, retry, and graph-route owners remain
deterministic.

The project SHALL retain a versioned Wave0 cognitive-program control corpus beside the
existing worker smoke. The corpus SHALL cover normal bounded retrieval handoff,
adversarial retrieved instructions, retrieval shortfall, malformed initial candidate
with one repair, and post-candidate validation rejection. Its runtime controls SHALL
bind the two Wave0 capability resources and the worker schema sources by
project-relative path and sha256 digest. Every case SHALL declare expected capability
ids, bounded assignment fragments, forbidden control effects, and rubric criteria.
Deterministic cases SHALL establish exact resource loading, tool/candidate handoff,
legal repair, and non-admission only; cognitive source-quality or release claims
require separately credentialed live evidence.

#### Scenario: Production rendering supplies one exact source-intake method
- **WHEN** real Wave0 prepares an initial source-intake or structural-repair invocation
- **THEN** the final rendered context contains the exact corresponding runtime-loaded
  capability method and its declared tool posture, while assignment, output contract,
  structural category, draft, and retrieval observations remain separate bounded data

#### Scenario: Adversarial retrieved content remains untrusted
- **WHEN** a permitted retrieval observation asks the worker to alter its tools, paths,
  evidence status, ledger, or lifecycle control
- **THEN** the worker may produce only a bounded source candidate or limitation, and
  deterministic runtime and source-admission owners retain tool, artifact, ledger,
  retry, gate, route, and State authority

#### Scenario: Repair is bounded before candidate admission
- **WHEN** an initial source-intake candidate is structurally malformed
- **THEN** Wave0 invokes at most its existing one zero-tool repair with the same bounded
  assignment and untrusted draft/observations, and a repaired candidate still requires
  the existing parser and source-admission path before it can affect evidence coverage

#### Scenario: Post-candidate validation does not re-enter cognitive repair
- **WHEN** a parsed source candidate later fails deterministic source or artifact
  validation
- **THEN** Wave0 follows only its existing validation/controller recovery path and does
  not send validation detail back through the structural-repair capability

#### Scenario: Deterministic evidence does not overclaim source quality
- **WHEN** the Wave0 cognitive corpus runs without approved live model and web evidence
- **THEN** it records only its declared deterministic handoff evidence and creates no
  fabricated source-quality, live-review, or release result

### Requirement: Wave0 records canonical structural validation evidence before candidate admission

When a Wave0 worker's initial result or its existing one zero-tool structural repair
reaches the typed source-intake parser, Wave0 SHALL publish one Journal validation fact
for that stage with its existing work and attempt correlation. A successful parse SHALL
publish an empty code collection. A failed parse SHALL publish only one code from the
closed set `wave0_worker_output_empty`, `wave0_worker_output_json_invalid`, or
`wave0_worker_output_invalid`; it SHALL NOT retain raw JSON, validation messages,
source URLs, tool observations, or exception text.

The initial validation fact SHALL be emitted before the existing repair is invoked. If
the repair result reaches parsing, its validation fact SHALL be retained independently
before the existing structured-output failure path, or as an empty collection on
success. An invocation failure before parser entry retains its existing invocation fact
and does not fabricate a validation result. These facts SHALL not add a repair, change
the one-repair bound, admit a candidate, append a ledger record, alter the
controller/gate route, or change a terminal or lifecycle result. (`WAN-010`)

#### Scenario: Wave0 repair failure retains both parser stages
- **WHEN** an initial Wave0 source-intake result fails parsing and its existing repair
  result also fails parsing
- **THEN** the correlated Journal contains distinct `initial` and `repair` validation
  facts with closed codes before the existing structured-output/controller path runs

#### Scenario: Valid initial Wave0 result retains a successful parser fact
- **WHEN** an initial Wave0 source-intake result parses successfully
- **THEN** the correlated Journal contains one `initial` validation fact with an empty
  code collection, no repair is invoked, and existing candidate admission remains the
  next deterministic boundary

#### Scenario: Pre-parser invocation failure is not relabeled as validation
- **WHEN** the Wave0 bridge invocation fails before it returns a candidate result
- **THEN** Wave0 retains the existing invocation failure behavior and creates no
  fabricated parser validation fact
