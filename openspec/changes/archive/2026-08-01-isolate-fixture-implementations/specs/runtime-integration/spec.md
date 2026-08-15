> req: RUI-003, RUI-004, RUI-006

## MODIFIED Requirements

### Requirement: GraphHost owns topology but not live SQL resources

GraphHost SHALL cache only request-independent topology recipes explicitly supplied at host
construction and a generic typed action-handler registry. It SHALL not discover fixture
source or select a recipe from a checkpoint. Cached objects SHALL NOT retain runtime
envelopes, reduced dependencies/capabilities, namespace values, checkpointers, or user/thread
data. Each action SHALL bind fresh dependencies and compile inside the lifetime of the
effective selected checkpointer. SQLite/Postgres SHALL use `make_checkpointer(app_config)` per
action and close it on success, failure, or cancellation; the project-owned provider
classifier SHALL follow the official legacy `checkpointer`-over-`database` precedence;
embedded node agents SHALL not receive that checkpointer. The infrastructure probe retains
its own versioned topology and namespace, separate from the public real research graph.

#### Scenario: SQL provider is reopened and closed
- **WHEN** two probe actions run against a fake async SQL provider
- **THEN** each action enters and exits its own provider context and no compiled graph or
  connection escapes that context

#### Scenario: Invocation failure still closes resources
- **WHEN** the probe node raises or its outer task is cancelled
- **THEN** provider cleanup and child-task cleanup complete and the error is not reported as
  success

#### Scenario: Startup provider drift does not split checkpoints
- **WHEN** live AppConfig database/checkpointer values differ from the launcher-captured
  startup fingerprint
- **THEN** GraphHost returns typed `restart_required` before opening a saver or reading or
  writing a nested checkpoint

## ADDED Requirements

### Requirement: Reflected research uses an explicit real recipe and isolated recipe namespace

The default reflected `deep_research` host SHALL construct one explicit all-real recipe. It
SHALL not load fixture source, discover a fixture catalog, or derive a recipe from caller
input, checkpoint content, or a stored compatibility fingerprint. Its research namespace
SHALL use a new fixed public recipe revision distinct from the retired full-fixture public
recipe namespace. The opaque research id remains the only caller-visible identity. Every
current control-result projection SHALL take `implementation_mode` from its selected recipe,
or default directly to `all_real`; it SHALL not default to `full_fake`. A retained
`full_fake` value is legacy inspection metadata only and SHALL not be emitted by a current
public action.

#### Scenario: Public host constructs the all-real recipe
- **WHEN** the reflected tool initializes its default graph host
- **THEN** all lifecycle handlers share one explicit all-real recipe and no fixture package is
  imported

#### Scenario: Retired fixture checkpoint is not reinterpreted
- **WHEN** a public action uses an opaque research id whose old checkpoint exists only in the
  retired fixture namespace
- **THEN** the public real host does not open that checkpoint as a real lifecycle, does not
  select an adapter from it, and returns the documented new-run or inspection-only outcome

#### Scenario: Public result cannot inherit a retired fixture default
- **WHEN** the reflected host projects a current action result without a caller-supplied mode
- **THEN** the result identifies the explicit all-real recipe and never emits `full_fake`
