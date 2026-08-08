> req: RUI-008

## ADDED Requirements

### Requirement: Deep Research checkpoint serialization is strict-msgpack compatible

Every project-owned value persisted through a Deep Research LangGraph checkpoint SHALL
be encoded as native safe data or decoded through the smallest explicit allowed msgpack
compatibility registration required by the runtime. The checkpoint path SHALL pass with
`LANGGRAPH_STRICT_MSGPACK=true` and SHALL not emit unregistered-type warnings for
`ContentRef`, `AttemptStatus`, or other project-owned persisted values. The selected
boundary SHALL not widen deserialization permission to arbitrary project modules or
untrusted type names, and existing valid checkpoints SHALL remain readable. (`RUI-008`)

#### Scenario: Strict checkpoint resume succeeds
- **WHEN** a persisted Deep Research run with profile and work-unit state resumes under
  `LANGGRAPH_STRICT_MSGPACK=true`
- **THEN** it reads the checkpoint without unregistered-type warnings or rejection and
  preserves the existing state validation and namespace boundaries

#### Scenario: Unknown project type remains disallowed
- **WHEN** a checkpoint payload names a project-owned type not in the explicit minimal
  serialization boundary
- **THEN** strict decoding rejects it and no arbitrary type is imported or instantiated

> req: RUI-009

## ADDED Requirements

### Requirement: Runtime captures and projects one trusted canonical bundle locator

Before every new lifecycle invokes the graph, runtime SHALL derive an immutable
UTC-minute `bundle_directory` from trusted time and the already-derived opaque
`research_id`, checkpoint it under controller-only ownership, and pass it through every
runtime projection that needs a workspace root. It SHALL validate the locator grammar,
never accept it from caller context, and preserve `research_id` as the only checkpoint
namespace, binding, and lifecycle identity. A restarted legacy checkpoint with no locator
SHALL resolve only to `r_<research_id>` without migration. (`RUI-009`)

#### Scenario: New lifecycle pins its locator before bootstrap or metadata publication
- **WHEN** a new lifecycle starts at `2026-07-22T03:59:53Z` with research id `r_abc`
- **THEN** its first graph state contains `bundle_directory=202607220359_r_abc`, and projection, bootstrap, request, work-unit, and retained-session roots all use that one locator

#### Scenario: Caller cannot select a bundle directory
- **WHEN** caller context supplies a timestamp, path, or locator-like value
- **THEN** runtime ignores it and derives/validates the locator from trusted state only

#### Scenario: Legacy checkpoint remains reopenable
- **WHEN** SQLite reopens a compatible checkpoint without `bundle_directory`
- **THEN** it resolves only `r_<research_id>` and retains existing binding and containment checks
