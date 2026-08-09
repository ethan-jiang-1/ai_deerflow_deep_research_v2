> req: RER-001

## MODIFIED Requirements

### Requirement: One runtime Module owns lifecycle-to-presentation interpretation

`ResearchRunExperience` SHALL retain one runtime-owned shared presentation interface
with the existing safe `Ready`, `Working`, `AwaitingInput`, `Terminal`, and `Fault`
updates. Its closed input vocabulary SHALL distinguish `Start`, correlated response/
visible-control submission for `resume`, `Cancel`, `Status`, and a separate bounded
`Refine` intent. The module consumes one shared typed Bundle lifecycle result; it does
not derive a `research_id`, keep a durable session or Bundle cache, construct a Bundle
path, or create an alternative graph/state authority.

A scripted `Start` intent SHALL project the explicit trusted
`non_interactive=true` marker and the complete closed non-interactive policy to its
single `start` transport dispatch. It SHALL not synthesize a human response, select a
HITL route, write checkpoint state, or attach policy to later `resume`, `refine`,
`status`, or `cancel` dispatches. The reflected lifecycle boundary remains the sole
admission point and the selected Bundle checkpoint remains the later policy owner.
When the checkpointed graph trace contains the bounded `hitl1_auto_profile` or
`hitl2_auto_proceed` policy observation marker, the module SHALL accept and project it
as an observation only; the marker SHALL NOT become lifecycle, route, profile, or
checkpoint authority.
(`RER-001`)

#### Scenario: Run experience keeps refine distinct from a response
- **WHEN** an available Bundle awaits input and a presentation adapter submits a
  refinement
- **THEN** the module dispatches the separate `refine` intent and leaves the correlated
  pending response available only to its resume path

#### Scenario: Scripted start projects explicit intent only once
- **WHEN** a standalone adapter submits a scripted `Start` intent
- **THEN** its one `start` transport dispatch contains `non_interactive=true` and both
  closed policy values, while the adapter has not created a Bundle, graph route,
  profile, response, or checkpoint mutation

#### Scenario: Subsequent dispatches do not reproject policy
- **WHEN** a scripted start has produced an available Bundle and the adapter later
  dispatches resume, refine, status, or cancel
- **THEN** the later transport context contains only that action's existing bounded
  input and does not supply a non-interactive policy as a new lifecycle authority

#### Scenario: Policy observations remain presentation-only
- **WHEN** a record-bearing lifecycle result includes either bounded policy observation
  marker in its checkpointed execution trace
- **THEN** the module accepts the trace as a safe observation and does not derive a
  lifecycle result, graph route, profile, or checkpoint mutation from the marker
