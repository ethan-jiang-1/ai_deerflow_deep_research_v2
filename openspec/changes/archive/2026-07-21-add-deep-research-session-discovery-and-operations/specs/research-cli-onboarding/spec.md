> req: REC-003, REC-004

## MODIFIED Requirements

### Requirement: Real CLI exposes bounded standalone diagnostics and durability

The standalone CLI SHALL label the active local profile's durability truth and remain
explicitly non-product. Same-process sessions SHALL not promise recovery after process
exit. A configured operation-enabled file-SQLite profile MAY direct an owner to the
bounded profile-mediated session commands, but SHALL not claim Gateway, Web, multi-user,
or generic product-session recovery. Failures continue to expose only safe opaque
diagnostic references and relative local record locations. (`REC-003`)

#### Scenario: User can retain a safe support reference
- **WHEN** a standalone run fails after its lifecycle begins
- **THEN** the CLI prints an opaque diagnostic reference and bounded local record location that an operator can inspect without revealing raw runtime data

#### Scenario: Durable local operation is not advertised as product recovery
- **WHEN** a record-bearing run uses the configured restart-durable local profile
- **THEN** the CLI may state the bounded local session-operation command while still
  identifying the surface as a standalone local demo rather than a Gateway or workbench

### Requirement: Real CLI exposes a safe run reference and local inspection path

The local session CLI SHALL render broker-projected discovery and operation availability
from an adapter-injected broker, without host paths, raw artifact content, binding
internals, or claims that an unavailable session can resume. For an authorized pending
session it MAY render the broker's validated bounded input view and submit raw answer text
plus an expected opaque request id. It SHALL not construct broker authority or accept
user/thread/path/provider/recipe/phase authority. A restart-capable operation view SHALL
be available only through a configured durable local profile; same-process demo records
remain honestly unavailable after a fresh process. It SHALL preserve the exact legacy
inspection command for inspection, and use only the profile-mediated `discover`, `open`,
`status`, `cancel`, and stdin-answer `resume` command shapes for operations. (`REC-004`)

#### Scenario: First HITL gives a developer an inspectable handle
- **WHEN** real CLI start returns the first bootstrap-plus-HITL-1 suspension
- **THEN** the user sees the semantic scope prompt and a safe run reference with an explicit inspect path, without raw workspace details or a promise of resume

#### Scenario: CLI denial does not leak a foreign session
- **WHEN** a user supplies a foreign or stale session reference
- **THEN** CLI output is bounded and indistinguishable from an unavailable session
