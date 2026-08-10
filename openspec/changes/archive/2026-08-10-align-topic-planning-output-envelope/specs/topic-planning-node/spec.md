> req: TOP-010

## ADDED Requirements

### Requirement: Topic planning has a compact output envelope aligned with its admitted execution budget

The real topic-planning node SHALL present both its initial and one-shot repair
requests as one compact JSON TopicPlan candidate: no prose, markdown, code fences, or
restatement of the assignment; title text at most 80 characters; scope text at most
240 characters; and no more than four search dimensions or four exclusions per topic,
each at most 80 characters. The existing TopicPlan parser and materializer SHALL keep
their current authoritative validity bounds and admission ownership; the compact
envelope is the bounded model-visible target, not a new route, state writer, or
model-authorized control.

The real topic-planning policy SHALL remain zero-tool and one-model-call, with a local
total-token budget of 12288 and its existing wall-time budget of 60 seconds. When a
rendered request's deterministic byte upper bound plus the output ceiling fits that
total budget, it SHALL admit one response of up to 4096 output tokens and retain a
structured candidate of up to 16384 bytes before existing parser/materializer
validation. It SHALL not change the provider-recovery table, one-shot structured-output
repair, checkpoint writer, `next`/`exhausted` routes, blocked terminal disposition, or
legal lifecycle action.

#### Scenario: The fixed scripted-demo planner request is admitted before provider invocation
- **WHEN** the observed fixed scripted-demo profile is projected through the real
  initial topic-planning prompt renderer under the local 4096-output-token and
  12288-total-token policy
- **THEN** its rendered-request upper bound plus the reserved output ceiling is at most
  the total budget, so the existing runtime may invoke the provider rather than stop
  at `token_admission`

#### Scenario: An oversized rendered request retains the existing closed admission stop
- **WHEN** a topic-planning request's rendered byte upper bound plus its 4096-token
  output ceiling exceeds the local 12288-token budget
- **THEN** the runtime stops before provider invocation with the existing
  `token_admission` reason, topic planning publishes no topic state, and it adds no
  repair or provider-recovery attempt before the existing exhausted path

#### Scenario: Compact initial and repair candidates are preserved for validation
- **WHEN** the topic planner receives either the initial assignment or its one allowed
  repair assignment and returns one JSON candidate within the compact envelope and
  within 4096 output tokens and 16384 bytes
- **THEN** the runtime passes the untruncated candidate to the existing parser and
  materializer, and a candidate accepted by the existing subsequent validation follows
  the existing planner-owned `next` path

#### Scenario: Existing parser authority is not narrowed after runtime retention
- **WHEN** the runtime has retained a topic-plan candidate and it remains valid under
  the existing authoritative TopicPlan parser and materializer bounds
- **THEN** the deterministic parser and materializer retain their existing admission
  decision and no prompt or budget setting grants the model a route, identifier,
  checkpoint, or lifecycle authority

#### Scenario: Calibrated policy retains the existing closed stop above its envelope
- **WHEN** the real topic-planning model response exceeds 4096 output tokens or its
  retained structured candidate exceeds 16384 bytes
- **THEN** the existing bounded runtime failure handling applies with no added retry,
  no topic-state publication, and the existing exhausted terminal path
