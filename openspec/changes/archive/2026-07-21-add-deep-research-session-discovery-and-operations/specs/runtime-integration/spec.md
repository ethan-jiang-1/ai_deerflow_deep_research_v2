> req: RUI-002, RUI-006

## MODIFIED Requirements

### Requirement: Runtime authority comes only from trusted context

A runtime-owned historical-session resolver SHALL require a `SessionOperationAccess`
created from current authenticated runtime context or a fixed local profile adapter. It
SHALL validate a private owner-index binding before using its historical thread lookup key
with trusted access-owned factories. Runtime-originated access SHALL use public DeerFlow
path and sandbox-provider APIs; a local-profile adapter MAY use only its fixed
contained-root/local-sandbox factories. It SHALL not synthesize a historical `ToolRuntime`
or historical `thread_data`, and SHALL reject missing, mismatched, or unavailable authority
without fallback identity or caller-supplied scope/path/provider/recipe fields. It SHALL
compare the operation access's fixed recipe compatibility fingerprint before opening a
provider, resolving historical paths, or acquiring a sandbox. (`RUI-002`)

#### Scenario: Trusted runtime is adapted without inventing research scope
- **WHEN** runtime context and state contain one consistent effective user, thread, sandbox, and thread-data mapping
- **THEN** RuntimeAdapter emits only a runtime-owned envelope and no research root or node-agent projection

#### Scenario: Registered handler scope is authority-reduced
- **WHEN** a registered research handler supplies a validated opaque scope id with a trusted envelope
- **THEN** runtime projection emits frozen pure graph and node-agent contracts with canonical virtual roots and no model-controlled authority fields, AppConfig, or host paths

#### Scenario: Fresh thread initializes its parent sandbox
- **WHEN** trusted thread data exists but lazy parent sandbox state has not yet been created
- **THEN** RuntimeAdapter uses the public async sandbox initializer once, validates the resulting parent sandbox, and does not create a second sandbox/thread lifecycle

#### Scenario: Forged cross-user fields are denied
- **WHEN** tool arguments include user, thread, host path, sandbox, checkpoint, or any unknown field
- **THEN** schema validation rejects the invocation before RuntimeAdapter, namespace derivation, or filesystem access

#### Scenario: Gateway identity overrides client context spoofing
- **WHEN** an authenticated or explicit auth-disabled Gateway request supplies a conflicting user id through body context or body config context
- **THEN** the runtime user is the server-injected authenticated id or synthetic `default`, never the client value

#### Scenario: Missing explicit runtime identity fails closed
- **WHEN** a hand-built runtime has no non-empty `runtime.context["user_id"]` even though DeerFlow's generic helper could fall back to `default`
- **THEN** RuntimeAdapter rejects it before sandbox initialization, namespace derivation, or checkpoint access

#### Scenario: Startup sandbox drift fails before initialization
- **WHEN** live AppConfig sandbox values do not match the launcher-captured startup fingerprint
- **THEN** RuntimeAdapter returns typed `restart_required` before calling the sandbox initializer

#### Scenario: Missing trusted historical context fails closed
- **WHEN** current DeerFlow facilities cannot resolve the bound historical scope after
  trusted access and binding validation
- **THEN** the resolver returns bounded unavailability without constructing an envelope

### Requirement: Research lifecycle dispatch preserves runtime and resource boundaries

The reflected lifecycle SHALL expose no new Gateway command in this change. Local broker
operations SHALL call existing handlers only after resolver and checkpoint verification;
reopened resume SHALL use a brokered response that the handler revalidates under its
namespace lock. Local-profile mutations SHALL additionally use the shared retained-root
dispatch lease, and read-only operations SHALL not initialize a sandbox. (`RUI-006`)

#### Scenario: Same-process memory lifecycle reuses one host
- **WHEN** start and a later status/resume action use the default reflected tool with the memory provider in one process
- **THEN** both actions reach the same process-local saver and recipe cache without retaining either request's trusted envelope

#### Scenario: Lifecycle actions share one graph recipe
- **WHEN** start, resume, status, and cancel bind the same research namespace
- **THEN** every handler compiles or inspects the identical versioned topology recipe and no action-specific node/edge drift can reinterpret the checkpoint

#### Scenario: SQL provider closes at suspension
- **WHEN** a file-SQLite start or resume action reaches HITL and returns an outer human-input message
- **THEN** the nested checkpoint is durable and the action's provider context is closed before the reflected tool returns

#### Scenario: Request authority is not cached or checkpointed
- **WHEN** two users or outer threads invoke research actions through the retained host
- **THEN** each action constructs fresh reduced invocation context, derives a different trusted namespace, and neither checkpoint nor cache contains the other request's envelope, host paths, sandbox object, or AppConfig

#### Scenario: Looped node receives fresh attempt dependencies
- **WHEN** a node executes again after repair or rerun within the same lifecycle action
- **THEN** the invocation-context resolver creates NodeBuildDependencies with the new deterministic attempt id and does not reuse a cached dependency object from the prior attempt

#### Scenario: Suspended and terminal results share one wire contract
- **WHEN** start or resume suspends, or any lifecycle action returns a non-suspended result
- **THEN** the tool exposes the same bounded versioned control fields, with the suspended form additionally carrying `artifact.human_input`, and neither form leaks internal scope or checkpoint data

#### Scenario: Non-interactive lifecycle fails before suspension
- **WHEN** runtime context marks the run non-interactive or clarification-disabled and start or resume is requested without a later explicit auto-decision policy
- **THEN** the tool returns typed `interactive_required` before graph/checkpoint mutation and does not fabricate a fixture answer, while status and cancel remain dispatchable

#### Scenario: Known IM transport fails closed
- **WHEN** runtime context contains an IM channel-user or channel-name marker for a checked-in bridge that does not consume generic deep-research human-input ToolMessages
- **THEN** start/resume returns `human_input_transport_unavailable` before graph/checkpoint mutation, status/cancel remain dispatchable, and no synthetic AI message is appended

#### Scenario: Lifecycle call with a sibling is refused
- **WHEN** the latest AIMessage has a missing or mismatched active tool-call id, two deep-research calls, or deep research beside any other tool call
- **THEN** the lifecycle action returns `exclusive_control_call_required` before RuntimeAdapter or nested mutation and makes no claim to cancel the sibling call

#### Scenario: Unsupported worker topology remains not ready
- **WHEN** the Gateway worker count is not exactly one
- **THEN** existing readiness continues to fail rather than claiming the combined host locks coordinate lifecycle actions across processes

#### Scenario: Unauthenticated fallback identity cannot open a bound session
- **WHEN** lifecycle binding resolution lacks an injected authenticated runtime user
- **THEN** it rejects the request without falling back to `default`, opening a provider,
  or revealing whether a research id exists

#### Scenario: Broker does not widen the public tool schema
- **WHEN** a local broker operation is requested
- **THEN** it uses runtime-owned entry points and the reflected tool accepts no new
  operation action or caller authority field
