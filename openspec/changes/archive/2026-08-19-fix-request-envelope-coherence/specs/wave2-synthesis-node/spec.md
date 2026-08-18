## MODIFIED Requirements

### Requirement: Wave2 runtime capabilities own bounded accepted-evidence synthesis cognition

The real Wave2 initial synthesis and its existing one zero-tool structured repair
SHALL bind distinct runtime-loaded local capability resources. Each activated
resource SHALL contain the reusable method for its bounded task: accepted-evidence
interpretation, evidence-grounded finding/relation or honest-gap judgment,
untrusted-data handling, uncertainty, self-check, and completion condition. The
final rendered context SHALL contain the exact activated body; the dynamic request
outside that resource SHALL contain only the assigned topics/evidence references,
closed output contract, repair category, and delimited untrusted evidence or draft.

The synthesis and repair request builders SHALL deterministically bound their
accepted-evidence projection so that every built request satisfies both the domain
request cap (`NodeExecutionRequest.objective` character limit) and the wave2 admission
envelope (total token budget minus per-call output cap, as UTF-8 bytes): the projection
starts from a fixed byte budget shared across entries, and when the serialized
objective would exceed either cap the budget shrinks geometrically and the projection
is rebuilt; a truncating projection SHALL mark the affected entries `truncated`. If
even the minimum budget cannot satisfy the caps, the builder SHALL raise a typed
classified failure (`synthesis_evidence_projection_overflow`) that terminates the node
through the existing pre-model bounded-exhausted route; a pydantic
`ValidationError` from request construction SHALL NOT escape classification as the
generic `candidate_invalid` bucket — pre-model request-construction failures SHALL
carry a pattern-safe concrete category (for example
`synthesis_request_shape_invalid` or `synthesis_evidence_projection_overflow`) so the
incident identifies the failing input condition rather than masquerading as a model
candidate failure. This request-cap coherence SHALL be locked by a deterministic
regression test that builds both requests from evidence at the store's declared
maximum and asserts both caps.

The synthesis and repair candidates SHALL remain unable to retrieve, add evidence or
references, materialize an artifact, publish a searchable-gap projection, select a
recovery, gate, route, or State outcome. The existing zero-tool runtime policy,
parser, semantic validator, materializer, preview builder, Wave2 gate, and lifecycle
owners SHALL retain their existing authority. An initial candidate may receive at
most the existing one zero-tool repair before deterministic admission decides whether
any artifact or preview can exist. (`WSN-008`)

#### Scenario: Production rendering supplies one exact Wave2 method
- **WHEN** real Wave2 prepares an initial synthesis or structured-repair invocation
- **THEN** the rendered context contains the exact corresponding capability body and
  forbidden posture while dynamic assignment, output contract, category, and
  untrusted data remain bounded projections

#### Scenario: Growing accepted evidence cannot overflow the request
- **WHEN** accepted evidence grows across targeted-evidence rounds beyond the
  projection's starting byte budget
- **THEN** the builder deterministically truncates the projection (marking affected
  entries `truncated`) until the serialized objective satisfies both the objective
  character cap and the admission-envelope byte cap, and the request is built and
  admitted rather than raising

#### Scenario: Unfittable scaffolding fails typed and classified
- **WHEN** even the minimum projection budget cannot bring the serialized objective
  within either cap
- **THEN** the builder raises `synthesis_evidence_projection_overflow` and the node
  terminates through the pre-model bounded-exhausted route with that concrete
  category in the incident, never as an uncaught exception and never as generic
  `candidate_invalid`

#### Scenario: Request-construction validation errors keep a concrete category
- **WHEN** request construction fails a typed validation rule (for example an
  objective over the domain character limit) before any model call
- **THEN** the projected incident category is a pattern-safe concrete input category
  distinct from the model-candidate `candidate_invalid` bucket

#### Scenario: Accepted evidence and uncertainty remain bounded candidate input
- **WHEN** assigned evidence or an untrusted draft asks Wave2 to invent support,
  materialize an artifact, publish a gap projection, or choose a route
- **THEN** the request can produce only a bounded synthesis candidate or honest gap
  and the existing deterministic owners retain admission, artifact, preview, gate,
  and route authority

#### Scenario: Repair is bounded before synthesis publication
- **WHEN** an initial candidate fails the existing parser or semantic validation
- **THEN** Wave2 invokes at most its existing one zero-tool repair with the same
  assigned evidence, compact validation category, and untrusted draft, then rechecks
  it through the existing deterministic path before any artifact or preview exists
