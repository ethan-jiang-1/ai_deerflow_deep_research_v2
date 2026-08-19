> req: REG-022

## MODIFIED Requirements

### Requirement: Bundle graph checkpoints cross one explicit registered serialization boundary

Every code path that opens the Bundle-contained graph store — including the
recoverable graph checkpoint opened for graph execution and resume — SHALL use the
application's explicit msgpack serialization boundary (the same registered-type
serializer the generic host uses), never the serialization library's silent
default. That boundary SHALL register exactly the project value types research
checkpoints persist — `deerflow_deep_research.domain.state.ContentRef`,
`deerflow_deep_research.domain.work_units.AttemptStatus`, and
`deerflow_deep_research.domain.wave1.Wave1OpenQuestionRef` — and strict msgpack
mode SHALL keep failing closed for every other project type. Reading or resuming a
research checkpoint SHALL produce no unregistered-project-type deserialization
warnings, and the set of registered types SHALL stay equal to the set of project
types actually persisted in research checkpoints. (`REG-022`)

#### Scenario: The bundle graph store opens with the registered serializer
- **WHEN** a run opens its Bundle-contained graph checkpoint store
- **THEN** the store's serializer is the application's explicit registered-type
  boundary, and a checkpoint written and read through it round-trips
  `ContentRef`, `AttemptStatus`, and `Wave1OpenQuestionRef` values faithfully

#### Scenario: Wave1 open-question projections round-trip under strict mode
- **WHEN** a checkpoint containing `wave1_open_questions` entries is deserialized
  with strict msgpack mode enabled
- **THEN** the projection entries decode as the registered project type without a
  blocked or warned unregistered-type deserialization

#### Scenario: Strict mode still blocks unlisted project types
- **WHEN** strict msgpack mode deserializes a payload carrying a project type
  outside the registered boundary
- **THEN** the deserialization is blocked and the registered types remain usable
