# demo-pipeline Specification

> req: DPL-001, DPL-002, DPL-003, DPL-004, DPL-005, DPL-006, DPL-007, DPL-008, DPL-009, DPL-010, DPL-011, DPL-012

## Purpose

Provide a standalone, bounded Deep Research demo pipeline with truthful lifecycle
progress, fixture-graph and all-real recipes, local real-demo web tools, and separate CLI/TUI
entry points without changing graph topology, `backend/`, or `frontend/`.
## Requirements
### Requirement: Shared demo core provides infrastructure, lifecycle transport, and prerequisite checks

The agent project SHALL provide
`deep_research_harness/scripts/_demo_core.py` with the existing demo adapter, fixed
recipe factories, idempotent cleanup, shared lifecycle transport adapter, and
non-network preflight primitives. For graph-backed demo modes, the core SHALL own one
trusted runtime composition boundary that selects a fixed all-real or fixture recipe,
the required bridge, and its executor before lifecycle dispatch. That boundary SHALL
not accept a recipe, executor, checkpoint, or graph-route selection from a CLI, TUI,
or reflected public-tool caller.

For every accepted graph-backed Bundle, the selected recipe's `implementation_mode` SHALL be
persisted with the Bundle and every later lifecycle projection for that Bundle SHALL
read its mode from that authoritative state. Fixture-graph execution SHALL therefore
project `fixture`, and real execution SHALL project `all_real`. No supported demo path
may default or backfill a mode, and no caller gains a mode input.

The generic control probe host SHALL remain usable only for its explicitly named
infrastructure-probe seam and SHALL NOT be treated as a graph-backed lifecycle
composition or completion source. A missing graph executor or incomplete fixture
catalog SHALL fail closed before Bundle State write, graph dispatch, or a completed
research presentation. Credential-free execution is the fixed fixture-graph route;
no no-graph lifecycle or simulator is supported.

The core SHALL consume only the shared typed Bundle lifecycle result for Deep Research
identity, status, and legal control; it SHALL not derive `research_id`, select a
Bundle path, or make retained demo material a lifecycle recovery source. (`DPL-001`)

#### Scenario: Demo core remains in the canonical root
- **WHEN** any supported demo entry point imports its common transport implementation
- **THEN** it resolves `deep_research_harness/scripts/_demo_core.py` and receives only
  the shared Bundle lifecycle outcome for a Deep Research Run

#### Scenario: Graph-backed demo cannot fall back to a no-graph lifecycle
- **WHEN** a real or fixture-graph entry starts without the graph composition required
  for its fixed mode
- **THEN** it produces a bounded startup failure and does not dispatch a probe-only
  host, select a no-graph fallback, or report a completed research lifecycle

#### Scenario: Fixture graph projects its selected implementation mode durably
- **WHEN** the named fixture-graph route starts a Bundle and its lifecycle is later
  resumed, reprojected, or inspected through the same trusted scope
- **THEN** each graph-backed result identifies `implementation_mode=fixture` from the
  Bundle-local state, without a command or public-tool mode selector

### Requirement: Demo progress display uses shared verified run updates

Demo scripts SHALL render phase progress only from a shared verified returned trace
delta and labels supplied by the run experience. They MAY preserve repeated logical
phase visits. A suspended marker SHALL identify `pending_input.pending_phase`, not
`control.phase`, because `control.phase` is the last committed checkpoint fact. No
demo script shall hardcode a phase sequence, infer current phase from action or
request options, or update a tracker before a valid returned event/result proves it.

The shared display map SHALL cover the complete closed `RunTraceEntry` set, including
the presentation-only trace steps `hitl1_auto_profile` and `hitl2_auto_proceed` with
safe display labels and descriptions. A returned trace that includes a
presentation-only step SHALL render without a crash and SHALL identify that step as an
automatic-policy step rather than a logical phase.

For a shared `PromptView` in `choice` mode from a separately specified graph
interaction, standalone demo adapters SHALL distinguish the canonical option ID from
its bounded human-readable consequence and submit only the advertised ID through
`AnswerRun`; they SHALL NOT parse rendered text as graph-control protocol. Current
HITL2 produces no such prompt. When `ResearchRunExperience` re-presents an unchanged
choice prompt with `rejection_category=choice_input_invalid`, adapters SHALL show
fixed safe feedback and the same choices without echoing rejected input, inferring
progress, changing the request ID, or constructing a lifecycle result. (`DPL-002`)

#### Scenario: First HITL phase is not confused with checkpoint phase
- **WHEN** a suspended run has execution trace `bootstrap`, checkpoint phase
  `bootstrap`, and pending-input phase `hitl1`
- **THEN** a demo marks bootstrap as completed and renders HITL-1 as the current
  requested interaction without treating the result as inconsistent

#### Scenario: Presentation-only trace step renders without crashing
- **WHEN** a returned trace delta includes `hitl1_auto_profile` or
  `hitl2_auto_proceed`
- **THEN** each demo adapter renders that step from the shared display map with an
  automatic-policy label and does not raise or invent a logical phase

#### Scenario: Fixture demo shows phases that actually executed
- **WHEN** `make demo --scripted` runs the fixture graph
- **THEN** it renders the actual trace order before, during, and after its HITL1
  interaction without inventing an HITL2 prompt

#### Scenario: Autonomous update is not rendered as a menu
- **WHEN** the shared update represents a policy-led HITL2 continuation
- **THEN** neither adapter renders `proceed`, `repair`, `rerun`, or another internal
  route as an input menu

### Requirement: Recipe factory supports fixture and all-real implementation modes

The graph-backed demo runtime SHALL construct one explicit recipe for each of its two
fixed modes. Fixture-graph mode SHALL load the fixture package's complete catalog and
pass an explicit fixture selection; it SHALL not rely on an omitted implementation map
or a production default. Real mode SHALL pass an explicit all-real selection, the
store factory, and the demo-local bridge factory. The runtime factory SHALL not
construct the recipe dataclass manually, and graph-backed dispatch SHALL use the
executor constructed from that selected recipe.

Fixture-graph mode is the sole credential-free deterministic execution route. It is
not a simulator or an alternate lifecycle contract. (`DPL-003`)

#### Scenario: Fixture recipe has no node-agent bridge requirement
- **WHEN** the named fixture-graph verification route is selected with the fixture
  source root enabled
- **THEN** it resolves the complete fixture catalog, has no node-agent bridge
  requirement, executes through its selected graph executor, and does not load real
  model, web, or publication prerequisites. Its completion evidence is the
  fixture final-delivery gate's checkpointed terminal fact and trace, not a report
  artifact claim.

#### Scenario: Real recipe requires the demo-local bridge
- **WHEN** real mode is selected with a valid store factory
- **THEN** it requires the bridge and bootstrap bundle, resolves policy-filtered local
  tools, and executes through the corresponding all-real graph executor

### Requirement: CLI real demo validates and explains prerequisite readiness

`deep_research_harness/scripts/demo_real.py` SHALL retain the existing shared
preflight, supported-model and `TAVILY_API_KEY` validation, `--question` and
`--scripted` behavior. After successful preflight it SHALL obtain its all-real recipe
and executor only from the shared demo runtime composition boundary, then use the
shared Bundle lifecycle transport. It SHALL not derive a Run/control identity from the
demo process, a checkpoint, or a retained-session record, and it SHALL not accept
recipe, executor, checkpoint, or graph-route selection as a command input.

If the required all-real composition is unavailable, the CLI SHALL present the bounded
startup outcome and SHALL NOT render a synthetic terminal completion as completed
research. Its scripted real question SHALL contain an explicit comparison pair
expressed in a supported language before bounded report-delivery evidence is asserted.
(`DPL-004`)

#### Scenario: Real demo entry follows the canonical root
- **WHEN** an operator starts the real CLI demo from the downstream module
- **THEN** the executable path is `deep_research_harness/scripts/demo_real.py` and its
  all-real executor comes from the shared demo runtime, and its lifecycle result
  remains Bundle-authoritative

#### Scenario: Real demo cannot claim synthetic completion
- **WHEN** a real CLI composition lacks its all-real executor or returns no
  graph-backed final-delivery evidence
- **THEN** the command exits nonzero without reporting completed research

### Requirement: Makefile provides targets for all demo variants

The `deep_research_harness/Makefile` SHALL retain its fixed fixture-graph and all-real
CLI/TUI demo targets, `DEMO_ARGS` forwarding, and direct-extra selection. It SHALL
enable fixture source only for the child process of a fixture route. Its `--help` and
README command description SHALL identify every credential-free route as deterministic
fixture-graph composition verification.

`make install` SHALL be the explicit project-environment synchronization owner for
every supported demo CLI, TUI, fixture-graph, retained-observation, and workbench
target, and for the documented prepared all-real launcher. It SHALL synchronize the
reviewed locked environment with the `operations`, `demo-tui`, and `demo-real`
optional dependency sets. A reviewed dependency-metadata or lockfile change occurs
outside ordinary target execution; `make install` SHALL use the locked state and SHALL
fail rather than refresh it implicitly.

Real targets SHALL load `deep_research_harness/.env` when present; fixture-graph
targets remain credential-free. No target SHALL use `deerflow_research/` as a working
directory or fallback, and no `backend/` or `frontend/` file is changed.
(`DPL-005`)

#### Scenario: Demo target loads the renamed local environment
- **WHEN** `make demo-real` runs from the canonical downstream module
- **THEN** it loads `deep_research_harness/.env` when present and does not resolve an
  old-root environment file

#### Scenario: Explicit install prepares every supported demo extra
- **WHEN** a clean checkout runs `make install` followed by a supported real CLI, real
  TUI, fixture-graph TUI, fixture-graph CLI, retained-observation, workbench, or documented
  prepared all-real launcher entry
- **THEN** the entry can use its declared optional dependencies from the prepared
  locked project environment without synchronizing a dependency set itself

#### Scenario: Credential-free commands are fixture-graph routes
- **WHEN** an operator reads the fixture-graph command help or the README entry map
- **THEN** it identifies the route as fixture-graph verification and names no
  full-fake/no-graph lifecycle or command alias

### Requirement: Command boundary selects a comprehensible project environment

Supported demo CLI, TUI, fixture-graph, retained-observation, and workbench Make
targets, plus the documented prepared all-real launcher, SHALL deliberately select the
agent project environment or fail before Python begins with a concise
command-environment explanation. A stale active environment from another project SHALL
not produce an unexplained `uv` `VIRTUAL_ENV` mismatch warning as the first
user-visible result, and the entry SHALL not silently execute dependencies from an
unrelated environment.

Before ordinary execution, each entry SHALL run a deterministic local preflight for
the complete optional dependency set prepared by `make install`. If the project
environment is missing or lacks a required distribution, it SHALL exit nonzero before
the adapter begins and identify only `make install` as the corrective setup command. A
prepared ordinary entry SHALL use the locked project environment with synchronization
disabled. It SHALL neither resolve nor update `uv.lock` nor create, remove, or change
the project `.venv`; declared ignored run-bundle, retained-observation, and diagnostic
artifacts remain permitted target outputs. `make lock-check` SHALL remain the separate
lock-freshness assertion; no ordinary entry's no-sync execution SHALL claim to validate
or refresh lock freshness. (`DPL-006`)

#### Scenario: Foreign active environment is handled before onboarding
- **WHEN** a shell has `VIRTUAL_ENV` set to a different project environment and a user
  runs `make demo-real` or `bash run/real-research.sh`
- **THEN** the entry uses the agent project environment deliberately or stops with a
  clear `make install` setup message, rather than leaving a warning followed by an
  unrelated lifecycle failure

#### Scenario: Incomplete prepared environment fails before the entry adapter
- **WHEN** a user runs a supported target or the documented launcher while a
  distribution required by the complete `make install` environment is absent
- **THEN** it exits nonzero before Python adapter execution, does not synchronize or
  mutate dependency state, and names `make install` as the only corrective action

#### Scenario: Ordinary entries preserve dependency state
- **WHEN** a clean prepared copy runs supported help, fixture-graph,
  retained-observation, bounded profile/workbench, and launcher credential-preflight
  commands
- **THEN** the tracked lockfile and project environment state remain unchanged across
  every ordinary command, except for the target's declared ignored run or diagnostic
  artifacts

#### Scenario: Concurrent read-only entries do not contend over setup
- **WHEN** independently started supported help or read-only entry commands overlap in
  a prepared project environment
- **THEN** each uses synchronization-disabled execution and neither command mutates
  `uv.lock` or the project `.venv`

#### Scenario: Lock freshness remains independently checkable
- **WHEN** a user needs to verify whether dependency metadata and the tracked lock
  agree
- **THEN** `make lock-check` performs that assertion independently of ordinary target
  execution and a no-sync target does not report lock freshness by implication

### Requirement: Local demos retain inspectable run bundles under bounded policy

Local demos SHALL retain only their own contained Run Bundles below the project-local
`deep_research_harness/.deep-research-demo-runs/` root, ignored by
`deep_research_harness/.gitignore`, and bounded observation-only diagnostics under the
shared Bundle lifecycle contract. They retain the existing lock, bounded cleanup, and
fixture/demo-composition guarantees. A demo may inspect an available Bundle through its
supported typed result, but SHALL not retain a session broker, `research_id`, checkpoint
namespace, or local path as a resume/control authority. Deleting a demo Bundle SHALL
make only that Run unavailable; a later demo may start a fresh independent Bundle
without recovering the prior one. (`DPL-007`)

#### Scenario: Demo retention does not become a recovery store
- **WHEN** a retained demo diagnostic refers to a deleted Bundle
- **THEN** the demo can show its bounded observation but returns unavailable for control and does not recreate State/content from a session or checkpoint record

### Requirement: Fixture-backed demo and local-session commands activate fixture source only for their child process

The fixture-graph CLI and TUI demo targets, `demo-sessions` operation path, and fixed-profile
`session-workbench` target SHALL add the registered fixture source root only to their selected
child process when they compose a fixture recipe. Real demo targets, ordinary production
packaging, and reflected runtime launch paths SHALL not add that root. `demo-sessions` and
`session-workbench` remain local demo/operator surfaces and SHALL not turn fixture composition
into reflected public authority. Every target SHALL retain `DEMO_ARGS` forwarding and the
existing credential-free or credentialed prerequisite behavior.

#### Scenario: Fixture demo is self-contained
- **WHEN** `make demo` or `make demo-tui-fixture` runs without model or web credentials
- **THEN** its child process can import the fixture package, completes the deterministic
  fixture path, and no production package import resolves to fixture source

#### Scenario: Real demo does not activate fixture source
- **WHEN** `make demo-real` or `make demo-tui` runs with real prerequisites
- **THEN** it constructs the all-real recipe without adding the fixture source root to its
  import path

#### Scenario: Fixture-backed local session tools remain explicitly isolated
- **WHEN** `make demo-sessions` performs a profile-mediated operation or `make session-workbench`
  constructs its fixed local demo profile
- **THEN** only that child process can import the fixture package, the selected recipe remains
  fixture/test-demo-only, and no public reflected runtime path gains fixture source

### Requirement: Configured real-demo web reads have bounded transient recovery

When a standalone real-demo recipe exposes configured `web_search` or `web_fetch`,
each Tavily-backed search or extraction SHALL be treated as an idempotent read with a
60-second maximum duration for each attempt. The direct demo tool boundary SHALL make
at most three total attempts for one read. It SHALL retry only a direct timeout,
transport/protocol failure, Tavily usage-limit error, HTTP 429, or an HTTP status in
the inclusive range 500-599; its cancellable backoff SHALL be one second before
attempt two and two seconds before attempt three. A successful retry SHALL return the
normal bounded tool payload and preserve the existing same-run search-to-fetch
provenance rule.

Authentication, malformed input, non-429 HTTP 4xx, unknown exceptions, and
cancellation SHALL not receive another attempt. Cancellation SHALL propagate rather
than becoming an unavailable result. A terminally failed read SHALL return only the
existing bounded redacted unavailable payload for its tool name; it SHALL not expose
credentials, provider response data, exception text, or a new lifecycle/graph outcome.
The demo tool boundary SHALL not create a second worker or lifecycle retry controller.
(`DPL-009`)

#### Scenario: A transient search failure recovers within the read bound
- **WHEN** the first direct `web_search` attempt receives a timeout, transport failure,
  Tavily usage-limit error, HTTP 429, or HTTP 500-599 response and its second attempt succeeds
- **THEN** the tool makes exactly two attempts with the one-second cancellable backoff
  and returns the normal bounded search payload

#### Scenario: A transient fetch failure exhausts the read bound
- **WHEN** three direct `web_fetch` attempts each receive a retry-eligible transient
  failure
- **THEN** the tool makes exactly three attempts with only the one- and two-second
  backoffs, returns the bounded `web_fetch_unavailable` payload, and does not alter
  the existing worker or lifecycle outcome itself

#### Scenario: Non-transient failure does not consume retry budget
- **WHEN** a direct search or fetch attempt receives authentication, malformed input, a
  non-429 HTTP 4xx, or an unknown exception
- **THEN** the tool returns its bounded unavailable payload after that one attempt and
  does not schedule a backoff or another provider call

#### Scenario: Cancellation remains an outer control signal
- **WHEN** the standalone run is cancelled during a direct web-read attempt or its
  configured backoff
- **THEN** cancellation propagates, no later attempt starts, and the tool does not
  return an unavailable payload as if the read completed

### Requirement: Demo pipeline carries Bundle identity through the shared lifecycle transport

The demo pipeline SHALL obtain Deep Research lifecycle identity, status, and legal
actions only from the shared typed Bundle lifecycle result. Fixture and all-real composition
roots SHALL not derive `research_id`, session references, or Bundle paths, and demo
retention shall remain an observation of a Bundle rather than an independent resume
store. (`DPL-010`)

#### Scenario: Demo restart cannot revive a deleted Bundle
- **WHEN** a demo process restarts after a prior Bundle was deleted
- **THEN** its shared lifecycle transport reports unavailable for that identity and does not reuse a session/checkpoint record to resume it

### Requirement: All-real demo admission binds one explicit configured model profile

Before an all-real demo composes its graph executor or the Bundle lifecycle admits a
Run, the trusted demo composition boundary SHALL resolve a non-blank
`DEERFLOW_DEMO_MODEL` selector to exactly one credential-backed registered model
profile. The selected profile SHALL be the only model configuration passed to the
all-real demo bridge; model choice SHALL NOT depend on registry order, credential
enumeration order, or a node-agent resolver's first-configured-model behavior.

Each registered profile SHALL carry one bounded version-controlled safe revision. A
material change to the profile's model binding or supported connector configuration
SHALL update that revision without putting the changed configuration value itself in a
Bundle or Journal. The revision is not an endpoint, credential, or deployment-environment
identifier.

An absent selector, unknown selector, or selector with other than one matching
credential-backed profile SHALL use the existing safe model-configuration prerequisite
failure. It SHALL create neither a Bundle nor an Event Journal, and SHALL NOT choose a
replacement model. The selector is a deployment/configuration input only: it SHALL NOT
become a graph route, checkpoint field, public lifecycle control, or model-visible
instruction. (`DPL-011`)

#### Scenario: Explicit selected profile enters one all-real composition
- **WHEN** an all-real demo starts with a supported selector and its corresponding
  credential
- **THEN** the preflight and composition resolve exactly that one registered profile,
  construct the all-real executor with it, and make its safe identity and declared
  revision available only to the Bundle-local Journal boundary

#### Scenario: Ambiguous or absent profile fails before Bundle admission
- **WHEN** an all-real demo has no selector, an unknown selector, or a test registry
  whose selector resolves zero or more than one credential-backed profile
- **THEN** it returns the existing safe model-configuration prerequisite result before
  graph construction, Bundle admission, or Journal creation and does not infer a model
  from configuration order

#### Scenario: Existing launcher policy remains explicit at the composition boundary
- **WHEN** a documented all-real launcher supplies its existing profile policy through
  `DEERFLOW_DEMO_MODEL`
- **THEN** the demo composition treats that exported value as the one explicit selector
  and does not add a second defaulting path

### Requirement: Profile calibration is bounded, explicit, and observational

Operator documentation SHALL provide a bounded calibration procedure that starts a
fresh all-real Bundle for one explicitly selected registered profile, uses the existing
scripted real-demo question and read-only Bundle inspection command, and records only
the resulting Journal evidence for later comparison. The procedure SHALL require the
operator to select each candidate profile explicitly and SHALL NOT automatically run a
model matrix, designate a qualified profile from one run, alter the configured default,
change a prompt or budget, or relax a graph contract. (`DPL-012`)

#### Scenario: An operator calibrates one selected profile
- **WHEN** an operator follows the documented calibration procedure with
  `DEERFLOW_DEMO_MODEL` set to one supported profile
- **THEN** the resulting fresh Bundle can be inspected through the existing read-only
  command for its redacted profile provenance and bounded execution facts

#### Scenario: Calibration evidence cannot select a model or control a Run
- **WHEN** a retained calibration Journal contains a success, failure, or repeated
  failure pattern
- **THEN** it supplies no lifecycle action beyond the existing typed outcome and no
  command or automation changes a default model, reruns a Bundle, or changes a budget

### Requirement: Credential-free demo execution is explicitly fixture-graph backed

Every supported credential-free demo CLI or TUI route SHALL construct the complete
fixture catalog, its fixed fixture recipe, and its graph executor before lifecycle
dispatch. The selected executor's `fixture` composition SHALL be persisted in the
Bundle-local State and every later lifecycle projection SHALL read that State fact.
No credential-free route SHALL bind or dispatch a lifecycle without a graph executor,
default its composition to `all_real`, use a probe-only host as execution, or claim
completed research without fixture-graph final-delivery evidence. (`DPL-001`,
`DPL-003`, `DPL-010`)

#### Scenario: Credential-free CLI persists fixture composition
- **WHEN** a supported credential-free CLI starts a Run in a prepared checkout with
  fixture source enabled only for its child process
- **THEN** it runs the complete fixture graph, persists `implementation_mode=fixture`,
  and projects lifecycle facts only from that Bundle-local State and graph result

#### Scenario: Missing graph composition fails before a lifecycle claim
- **WHEN** a credential-free demo route lacks its fixed executor or complete fixture
  catalog
- **THEN** it returns a bounded startup failure before a Bundle State write, graph
  dispatch, or completed-research presentation

### Requirement: Full-fake demo compatibility is retired rather than reclassified

The supported demo command map and documentation SHALL identify credential-free
execution as fixture-graph proof and SHALL not retain a full-fake/no-graph lifecycle,
simulator, command alias, or a distinct completed-presentation contract. The fixed
all-real route and explicit fixture/mixed test composition remain separate and no
caller receives recipe, executor, checkpoint, graph-route, or mode selection
authority. (`DPL-003`, `DPL-005`, `DPL-008`)

#### Scenario: A credential-free route is not a no-graph alias
- **WHEN** an operator inspects supported demo help, Make targets, or README command
  guidance
- **THEN** every zero-credential execution route is described as fixture-graph proof
  and no route names or invokes a full-fake/no-graph lifecycle
