> req: DPL-001, DPL-002, DPL-004, DPL-006

## MODIFIED Requirements

### Requirement: Shared demo core provides infrastructure, lifecycle transport, and prerequisite checks

The agent project SHALL provide agent/scripts/_demo_core.py with a demo adapter,
recipe and host factories, idempotent cleanup, a shared lifecycle transport adapter,
and non-network preflight primitives for all demo scripts. The preflight and
DemoAppConfig SHALL share non-blank validation for one supported model key plus
TAVILY_API_KEY. Real recipes SHALL resolve fresh, policy-filtered Tavily
web_search/web_fetch tool pairs. Fetch requires same-run search provenance; clients
close before return; credentials never enter state, prompts, errors, RunUpdate, or
diagnostic records; global DeerFlow tool configuration is unused; and the direct
demo-real extra declares compatible tavily-python.

The demo core SHALL not become the owner of lifecycle presentation semantics. It
may satisfy the runtime Module's narrow transport seam, but Command parsing,
pending-phase interpretation, trace validation, prompt rendering, and failure
classification belong to ResearchRunExperience. (DPL-001)

#### Scenario: Real demo uses local web tools
- **WHEN** make demo-real or make demo-tui has valid real-demo prerequisites
- **THEN** it constructs the all-real recipe with the demo-local tool path and
  shared preflight without requiring global tool configuration

### Requirement: Demo progress display uses shared verified run updates

Demo scripts SHALL render phase progress only from a shared verified returned trace
delta and labels supplied by the run experience. They MAY preserve repeated
logical-phase visits. A suspended marker SHALL identify pending_input.pending_phase,
not control.phase, because control.phase is the last committed checkpoint fact.
No demo script shall hardcode a phase sequence, infer current phase from action or
request options, or update a tracker before a valid returned event/result proves it.
(DPL-002)

#### Scenario: First HITL phase is not confused with checkpoint phase
- **WHEN** a suspended run has execution_trace bootstrap, checkpoint phase bootstrap,
  and pending_input phase hitl1
- **THEN** a demo marks bootstrap as completed and renders HITL-1 as the current
  requested interaction without treating the result as inconsistent

### Requirement: CLI real demo validates and explains prerequisite readiness

agent/scripts/demo_real.py SHALL invoke shared preflight before collecting a
question or building an all-real recipe. It SHALL validate non-blank values for one
supported model key and TAVILY_API_KEY, report what prerequisite is missing and why,
support --question and --scripted, and pass
non_interactive_policy with auto_profile and auto_proceed only in scripted mode.
DemoAppConfig SHALL select the matching supported model config. (DPL-004)

#### Scenario: Real demo rejects a missing Tavily key clearly
- **WHEN** a model key exists but TAVILY_API_KEY is blank or absent
- **THEN** preflight identifies the web-search prerequisite and its setup action
  before question entry or graph construction

## ADDED Requirements

### Requirement: Command boundary selects a comprehensible project environment

Real demo Make targets SHALL deliberately select the agent project environment or
fail before Python begins with a concise command-environment explanation. A stale
active environment from another project SHALL not produce an unexplained uv
VIRTUAL_ENV mismatch warning as the first user-visible result. The target SHALL not
silently execute dependencies from an unrelated environment. (DPL-006)

#### Scenario: Foreign active environment is handled before onboarding
- **WHEN** a shell has VIRTUAL_ENV set to a different project environment and a
  user runs make demo-real
- **THEN** the command uses the agent project environment deliberately or stops
  with a clear environment setup message, rather than leaving a warning followed
  by an unrelated lifecycle failure
