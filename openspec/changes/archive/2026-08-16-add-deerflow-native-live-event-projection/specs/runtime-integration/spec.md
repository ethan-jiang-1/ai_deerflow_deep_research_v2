# runtime-integration Specification

> req: RUI-002

## MODIFIED Requirements

### Requirement: Runtime authority comes only from trusted context

A runtime-owned Bundle lifecycle resolver SHALL require a trusted runtime envelope
created from current authenticated runtime context or a fixed local-profile adapter. It
SHALL derive only a containment scope from that trusted context, validate a supplied
Current Bundle Handle against scoped Bundle-local State, or inspect that scope's actual
Bundle directories and State when the Handle is absent. It SHALL not synthesize a
historical `ToolRuntime` or `thread_data`, reopen a historical session/binding/provider,
or accept caller-supplied scope, path, provider, recipe, or identity fields. It SHALL
reject missing, mismatched, unavailable, foreign, or ambiguous authority before opening
a provider, resolving content paths, or acquiring a sandbox. Startup-fingerprint drift
SHALL still return `restart_required` before sandbox initialization or Bundle access.

The trusted runtime boundary MAY capture the current public injected
`ToolRuntime.stream_writer` solely to reduce it immediately to a project-owned opaque
custom-event sink. Only that sink MAY invoke the writer, and it SHALL accept payloads
only from the validated runtime observation projection. The raw writer SHALL not enter
the trusted envelope, graph/domain owners, State, checkpoints, Bundle storage, tool
arguments, or caller-provided context. A missing or non-callable writer SHALL disable
only the live-event attempt and preserve the existing standard log and typed Run
behavior.

After Bundle admission, the runtime composition root MAY bind the opaque sink and
trusted correlation into the non-checkpointed observation projection. That projection
SHALL remain a no-control capability: it cannot select a Bundle, write State, append the
Bundle Journal, choose a route, authorize a retry, recover a Run, or alter lifecycle
outcomes.

The trusted envelope MAY carry the current bounded outer thread id and outer run id
solely as safe standard-log or independently bounded live-event correlation after a
Bundle is admitted or resolved. DeerFlow logging configuration and its current trace
filter own available request trace correlation; application runtime code SHALL not
configure root logging, install a competing trace filter, invent a missing trace, or
persist a trace correlation. The association SHALL not be caller-supplied, persisted as
graph State, used as a Bundle locator/checkpoint identity/recovery source, or obtained
from a private Gateway journal/store; it SHALL exclude user identity, credentials,
request content, model or tool data, full URLs, and host paths. (`RUI-002`)

#### Scenario: Trusted runtime is adapted without inventing research scope
- **WHEN** runtime context and state contain one consistent effective user, thread,
  sandbox, and thread-data mapping
- **THEN** RuntimeAdapter emits only a runtime-owned envelope and no Bundle root or
  node-agent projection

#### Scenario: Forged cross-user fields are denied
- **WHEN** tool arguments include user, thread, host path, sandbox, checkpoint,
  legacy research identity, or any unknown field
- **THEN** schema validation rejects the invocation before RuntimeAdapter, scoped
  discovery, or filesystem access

#### Scenario: Missing explicit runtime identity fails closed
- **WHEN** a hand-built runtime has no non-empty `runtime.context["user_id"]` even
  though DeerFlow's generic helper could fall back to `default`
- **THEN** RuntimeAdapter rejects it before sandbox initialization, scope derivation,
  or Bundle access

#### Scenario: Startup sandbox drift fails before initialization
- **WHEN** live AppConfig sandbox values do not match the launcher-captured startup
  fingerprint
- **THEN** RuntimeAdapter returns typed `restart_required` before calling the sandbox
  initializer

#### Scenario: Current public writer is reduced to a non-controlling sink
- **WHEN** an authenticated current-pin `ToolRuntime` supplies a callable public
  `stream_writer`
- **THEN** trusted adaptation reduces it to one opaque sink, only that sink can invoke
  the writer, and graph/domain owners receive only the non-checkpointed observation
  projection

#### Scenario: Missing writer preserves the log-only path
- **WHEN** a trusted embedded or test invocation has no callable public writer
- **THEN** its existing safe standard logs and typed execution behavior remain active,
  while no custom event, writer lookup, retry, or private Gateway access is attempted

#### Scenario: Trusted correlation remains a non-controlling log projection
- **WHEN** an authenticated runtime supplies current outer thread/run correlation for
  an admitted Bundle and DeerFlow has a current trace when it configures the log record
- **THEN** the runtime may project only those safe correlations with the opaque Bundle
  id through a standard log or independently bounded live event, without accepting
  caller correlation, reading a private Gateway store, or changing Bundle selection,
  State, checkpoint, recovery, or lifecycle behavior

#### Scenario: Lifecycle logging does not become lifecycle ownership
- **WHEN** `BundleControl` receives a typed admitted or resolved lifecycle result with
  its trusted envelope
- **THEN** `BundleLifecycle` remains the source of exactly one standard-log record for
  both Gateway and Local Session Workbench callers, and no caller-controlled value
  enters that projection
