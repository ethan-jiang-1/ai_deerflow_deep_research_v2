# demo-pipeline Specification

> req: DPL-001, DPL-002, DPL-003, DPL-004, DPL-005, DPL-006, DPL-007, DPL-008, DPL-009, DPL-010

## Purpose

Provide a standalone, bounded Deep Research demo pipeline with truthful lifecycle
progress, fake and real recipes, local real-demo web tools, and separate CLI/TUI
entry points without changing graph topology, `backend/`, or `frontend/`.
## Requirements

### Requirement: Shared demo core provides infrastructure, lifecycle transport, and prerequisite checks

The agent project SHALL provide
`deep_research_harness/scripts/_demo_core.py` with the existing demo adapter, recipe
and host factories, idempotent cleanup, shared lifecycle transport adapter, and
non-network preflight primitives. Its real/fake composition, credential handling,
tool-provenance, and zero-API default-demo guarantees remain unchanged. The core SHALL
consume only the shared typed Bundle lifecycle result for Deep Research identity,
status, and legal control; it SHALL not derive `research_id`, select a Bundle path, or
make retained demo material a lifecycle recovery source. (`DPL-001`)

#### Scenario: Demo core remains in the canonical root
- **WHEN** any supported demo entry point imports its common transport implementation
- **THEN** it resolves `deep_research_harness/scripts/_demo_core.py` and receives only
  the shared Bundle lifecycle outcome for a Deep Research Run

### Requirement: Demo progress display uses shared verified run updates

Demo scripts SHALL render phase progress only from a shared verified returned trace
delta and labels supplied by the run experience. They MAY preserve repeated logical
phase visits. A suspended marker SHALL identify `pending_input.pending_phase`, not
`control.phase`, because `control.phase` is the last committed checkpoint fact. No
demo script shall hardcode a phase sequence, infer current phase from action or
request options, or update a tracker before a valid returned event/result proves it.

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

#### Scenario: Fake demo shows phases that actually executed
- **WHEN** `make demo --scripted` runs the fake lifecycle
- **THEN** it renders the actual trace order before, during, and after its HITL1
  interaction without inventing an HITL2 prompt

#### Scenario: Autonomous update is not rendered as a menu
- **WHEN** the shared update represents a policy-led HITL2 continuation
- **THEN** neither adapter renders `proceed`, `repair`, `rerun`, or another internal
  route as an input menu

### Requirement: Recipe factory supports fake and real implementation modes

`build_demo_recipe(*, mode, work_unit_store_factory)` SHALL construct one explicit recipe.
Fixture mode SHALL load the fixture package's complete catalog and pass an explicit fixture
selection; it SHALL not rely on an omitted implementation map or a production default.
Real mode SHALL pass an explicit all-real selection, the store factory, and the demo-local
bridge factory. The demo factory SHALL not construct the recipe dataclass manually.

#### Scenario: Fixture recipe has no node-agent bridge requirement
- **WHEN** fixture mode is selected with the fixture source root enabled
- **THEN** it resolves the complete fixture catalog, has `requires_node_agent_bridge=False`,
  and does not load real model or web prerequisites

#### Scenario: Real recipe requires the demo-local bridge
- **WHEN** real mode is selected with a valid store factory
- **THEN** it requires the bridge and bootstrap bundle and resolves policy-filtered local tools

### Requirement: CLI real demo validates and explains prerequisite readiness

`deep_research_harness/scripts/demo_real.py` SHALL retain the existing shared
preflight, supported-model and `TAVILY_API_KEY` validation, `--question` and
`--scripted` behavior, and explicit all-real recipe construction. It SHALL use the
shared Bundle lifecycle transport and shall not derive a Run/control identity from the
demo process, a checkpoint, or a retained-session record. (`DPL-004`)

#### Scenario: Real demo entry follows the canonical root
- **WHEN** an operator starts the real CLI demo from the downstream module
- **THEN** the executable path is `deep_research_harness/scripts/demo_real.py` and its
  lifecycle result remains Bundle-authoritative

### Requirement: Makefile provides targets for all demo variants

The `deep_research_harness/Makefile` SHALL retain the existing fake and real CLI/TUI
demo targets, `DEMO_ARGS` forwarding, and direct-extra selection. Its real targets
SHALL load `deep_research_harness/.env` when present; fake targets retain their
credential-free behavior. No target SHALL use `deerflow_research/` as a working
directory or fallback, and no `backend/` or `frontend/` file is changed. (`DPL-005`)

#### Scenario: Demo target loads the renamed local environment
- **WHEN** `make demo-real` runs from the canonical downstream module
- **THEN** it loads `deep_research_harness/.env` when present and does not resolve an
  old-root environment file

### Requirement: Command boundary selects a comprehensible project environment

Real demo Make targets SHALL deliberately select the agent project environment or
fail before Python begins with a concise command-environment explanation. A stale
active environment from another project SHALL not produce an unexplained `uv`
`VIRTUAL_ENV` mismatch warning as the first user-visible result. The target SHALL
not silently execute dependencies from an unrelated environment. (`DPL-006`)

#### Scenario: Foreign active environment is handled before onboarding
- **WHEN** a shell has `VIRTUAL_ENV` set to a different project environment and a user runs `make demo-real`
- **THEN** the command uses the agent project environment deliberately or stops with a clear environment setup message, rather than leaving a warning followed by an unrelated lifecycle failure

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

The fake CLI and TUI demo targets, `demo-sessions` operation path, and fixed-profile
`session-workbench` target SHALL add the registered fixture source root only to their selected
child process when they compose a fixture recipe. Real demo targets, ordinary production
packaging, and reflected runtime launch paths SHALL not add that root. `demo-sessions` and
`session-workbench` remain local demo/operator surfaces and SHALL not turn fixture composition
into reflected public authority. Every target SHALL retain `DEMO_ARGS` forwarding and the
existing credential-free or credentialed prerequisite behavior.

#### Scenario: Fixture demo is self-contained
- **WHEN** `make demo` or `make demo-tui-fake` runs without model or web credentials
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
actions only from the shared typed Bundle lifecycle result. Fake and real composition
roots SHALL not derive `research_id`, session references, or Bundle paths, and demo
retention shall remain an observation of a Bundle rather than an independent resume
store. (`DPL-010`)

#### Scenario: Demo restart cannot revive a deleted Bundle
- **WHEN** a demo process restarts after a prior Bundle was deleted
- **THEN** its shared lifecycle transport reports unavailable for that identity and does not reuse a session/checkpoint record to resume it
