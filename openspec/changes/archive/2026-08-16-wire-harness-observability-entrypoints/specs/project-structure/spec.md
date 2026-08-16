> req: PRS-005

## MODIFIED Requirements

### Requirement: Run-experience contracts use the canonical domain and runtime ownership layers

The existing run-experience domain and runtime contracts SHALL remain under
`deep_research_harness/src/deerflow_deep_research/` at their registered canonical
paths. The public Gateway observation boundary SHALL live at the registered runtime
path
`deep_research_harness/src/deerflow_deep_research/runtime/gateway_observer.py`, and
its deterministic contract evidence SHALL remain under registered
`deep_research_harness/tests/` paths. Its dependency direction SHALL permit only the
existing domain contracts plus approved public HTTP/SSE libraries and SHALL not import
presentation scripts or private DeerFlow Gateway modules.

The existing run-experience dependency-direction, runtime-binding, and presentation-
adapter boundaries remain unchanged; `deep_research_harness/scripts/` remains only a
permitted presentation/launcher-adapter location, not a lifecycle authority. The
structure registry SHALL admit `httpx_sse` only for the bounded runtime Gateway
observer and SHALL continue to reject upstream source placement, private Gateway
imports, and generic `utils`/`helpers`/`common` modules. (`PRS-005`)

#### Scenario: Run-experience paths follow the Harness root
- **WHEN** structural governance inspects the registered run-experience and Gateway
  observer modules
- **THEN** it finds their domain/runtime/test paths beneath `deep_research_harness/`
  and rejects an old-root duplicate, presentation-owned lifecycle module, or upstream
  placement

#### Scenario: Structured SSE dependency remains bounded
- **WHEN** the architecture checker evaluates runtime imports for the Gateway observer
- **THEN** `httpx_sse` is permitted only through the declared runtime dependency rule,
  while private DeerFlow Gateway modules and reverse imports into scripts remain
  rejected
