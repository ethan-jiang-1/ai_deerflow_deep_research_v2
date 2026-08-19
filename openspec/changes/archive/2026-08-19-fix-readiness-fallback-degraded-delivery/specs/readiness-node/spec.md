# readiness-node Delta

> req: REA-002, REA-003, REA-004, REA-006, REA-008

## MODIFIED Requirements

### Requirement: Node determines its own route based on hard-rule results and critic verdicts

The readiness node SHALL write its own `route` field. Route determination SHALL retain
this priority: structural hard-rule failures, including accepted-evidence reader
failures, route to `exhausted` with `BLOCKED`; admitted `blocked_repair_required`
verdicts route to `repair_targeted` only when the targeted-repair loop has declared
work — the gate-recorded `unresolved_gaps` control field is non-empty — **and the wave2
gate has not already exhausted and degraded**; a conservatively projected verdict after
a critic execution failure or inadmissible candidate SHALL NOT route `repair_targeted`
at all (observation failure is not a repair demand); in every other case the node routes
`pass`. A critic candidate SHALL NOT select, write, or bypass a route.

The wave2-degraded condition is read-only from checkpoint state: it holds exactly when
the gate-owned `degraded_decisions` field contains the
`wave2_synthesis:exhaustion_degraded` marker, meaning the wave2 repair budget is spent
and any further `repair_targeted` route would be re-evaluated by the wave2 gate at
exhausted budget with the degradation marker present and therefore terminate the run
`blocked` without a report. The gap-work condition is likewise read-only: targeted
evidence can dispatch workers only for recorded unresolved searchable gaps, so a
`repair_targeted` route with empty `unresolved_gaps` is a deterministic no-op loop and
SHALL NOT be written. In either blocked-but-delivering state — wave2 degraded, or no
declared gap work — the only non-terminal route is `pass`, and every blocked verdict
SHALL be disclosed as a mandatory uncertainty by the report-plan materializer rather
than dropped from the plan. A run with declared gap work and a non-degraded wave2 gate
SHALL keep the existing repair loop exactly as before.

#### Scenario: Admitted critic result routes through deterministic owner
- **WHEN** hard rules pass, the admitted candidate contains a `blocked_repair_required`
  verdict, `unresolved_gaps` is non-empty, and the wave2 gate has not degraded
- **THEN** the readiness node writes `repair_targeted` and the critic writes no route

#### Scenario: A gapless blocked verdict delivers with disclosure instead of spinning
- **WHEN** hard rules pass, the admitted candidate contains a `blocked_repair_required`
  verdict, and `unresolved_gaps` is empty
- **THEN** the node writes `pass`, `readiness_blocked_count` still counts the blocked
  questions, and the report plan discloses each blocked question as a mandatory
  uncertainty instead of routing a no-op repair loop

#### Scenario: A conservative fallback never demands repair
- **WHEN** hard rules pass and the bounded critic execution fails or its candidate is
  inadmissible, in a run whose wave2 gate has not degraded
- **THEN** the node writes `pass` with the fallback limitation disclosed as mandatory
  uncertainties and never writes `repair_targeted`, so an observation failure cannot
  spin or kill the run

#### Scenario: Insufficient judgment remains an honest pass projection
- **WHEN** hard rules pass and all admitted verdicts are `ready_substantive` or
  `ready_insufficient_judgment`
- **THEN** the node writes `pass` and the report plan records each insufficiency as a
  mandatory uncertainty

#### Scenario: Structural failures still take priority
- **WHEN** a structural hard-rule failure and any critic verdict are present
- **THEN** the node writes `exhausted` with the existing blocked terminal facts,
  even when the wave2 gate has degraded

#### Scenario: Wave2-degraded run never re-opens the spent repair loop
- **WHEN** `degraded_decisions` contains `wave2_synthesis:exhaustion_degraded` and
  hard rules pass but the admitted candidate reports `blocked_repair_required` for
  one or more questions
- **THEN** the node writes `pass`, `readiness_blocked_count` still counts the
  blocked questions, and the report plan discloses every blocked verdict and every
  unresolved searchable gap as mandatory uncertainties instead of routing
  `repair_targeted`

#### Scenario: Wave2-degraded run with a failed critic still delivers
- **WHEN** `degraded_decisions` contains `wave2_synthesis:exhaustion_degraded` and
  the bounded critic execution fails (timeout, configuration, provider, or policy)
- **THEN** readiness projects the disclosed-fallback verdicts and routes `pass`
  (not `repair_targeted`), so the run continues to `final_delivery` and the report
  carries the disclosed gaps

### Requirement: Semantic critic assesses answerability per must-answer question

The real readiness node SHALL declare `NodeCapability.WORK_UNIT_CONTROLLER` and invoke
one bounded zero-tool critic for each readiness visit. Before invocation, trusted code
SHALL derive a bounded read-only evidence projection solely from the checkpointed
must-answer questions, accepted submission references, and ledger-validated synthesis
evidence read through that declared controller. The critic SHALL return exactly one
typed verdict for every supplied question: `ready_substantive`,
`ready_insufficient_judgment`, or `blocked_repair_required`. It SHALL receive no raw
checkpoint, runtime authority, writable path, tool, or route instruction. Full-fake
readiness SHALL remain fixture-controlled. (`REA-002`)

#### Scenario: Complete candidate is admitted
- **WHEN** the zero-tool critic returns one valid verdict for every supplied question
- **THEN** the deterministic readiness boundary accepts the typed candidate for
  report-plan materialization without granting the critic evidence or route authority

#### Scenario: Candidate references cannot exceed the projection
- **WHEN** a candidate names an unknown or duplicate question, or a backing reference
  absent from the accepted evidence projection
- **THEN** readiness rejects that candidate and projects the disclosed conservative
  insufficiency verdicts without admitting the unknown identifier

#### Scenario: Evidence projection is bounded and ledger-derived
- **WHEN** real readiness prepares the critic request
- **THEN** it includes only the approved questions and bounded evidence derived from
  accepted ledger references, and does not expose arbitrary sandbox content

#### Scenario: Full-fake readiness remains fixture-controlled
- **WHEN** the full-fake graph reaches readiness
- **THEN** it does not invoke the critic and retains its declared fixture route

### Requirement: Report plan materializer produces immutable projection

A deterministic materializer SHALL produce a `ReadinessReportPlan` from the critic's verdicts, the canonical synthesis artifact's admitted findings, and hard-rule results. The plan SHALL contain writable conclusions (from `ready_substantive`), mandatory uncertainties (from `ready_insufficient_judgment`), and prohibited upgrades. It SHALL additionally append one mandatory uncertainty for every gate-recorded unresolved searchable gap: the gap id set comes from the checkpointed `unresolved_gaps` control field, and each gap's description is read from the bundle store's canonical `synthesis/findings.json` artifact through a bounded contained read; a recorded id whose gap body is absent from the artifact SHALL still produce an uncertainty naming the gap id without fabricating a description, and no gap body SHALL enter checkpoint state.

When the node routes `pass` while any `blocked_repair_required` verdict is present — because the conservative fallback replaced the critic result, the run has no declared gap work, or the wave2 gate already degraded — the materializer SHALL convert each such blocked verdict into one mandatory uncertainty carrying that verdict's bounded limitation note (the closed fallback note for conservative substitutions, or the critic's own bounded limitation note for admitted verdicts), so no blocked judgment silently disappears from the delivered plan. When the node routes `repair_targeted`, blocked verdicts SHALL contribute only the existing repair-route counting and SHALL NOT become conclusions or uncertainties, exactly as before.

Writable conclusions SHALL have a deterministic second source that the critic cannot veto away: every admitted synthesis finding with `confidence=high`, a non-empty `backing_refs` tuple fully contained in the accepted submission-reference ledger, and `search_required=false` SHALL become one writable conclusion whose `conclusion_text` is the finding's verbatim `statement` and whose `backing_claim_ids` are the finding's `backing_refs` (bounded to the plan contract's cardinality). The finding projection is read from the same canonical synthesis artifact through a bounded contained read and no finding body enters checkpoint state. Critic verdicts SHALL NOT remove, demote, or block finding-derived conclusions — a partially answered research question SHALL be delivered as finding-derived conclusions alongside disclosed uncertainties rather than zero delivery. The readiness controller SHALL serialize the admitted plan to the canonical `readiness_report_plan` artifact before checkpointing its `ContentRef`; the reference SHALL name the contained path and exact content hash of those immutable bytes. A later reader may consume only a contained, hash-matched plan and no rejected critic output becomes part of it.

#### Scenario: ready_substantive verdicts become writable conclusions
- **WHEN** the critic produces `ready_substantive` for Q1 and Q3
- **THEN** the report plan lists Q1 and Q3 as writable conclusions with backing claim IDs

#### Scenario: ready_insufficient_judgment verdicts become mandatory uncertainties
- **WHEN** the critic produces `ready_insufficient_judgment` for Q2 with limitation "data is contradictory"
- **THEN** the report plan lists Q2 under mandatory uncertainties with that limitation

#### Scenario: blocked_repair_required verdicts produce neither conclusions nor uncertainties
- **WHEN** the critic produces `blocked_repair_required` for Q4 and the node routes
  `repair_targeted`
- **THEN** Q4 is absent from both conclusions and uncertainties; `readiness_blocked_count` is incremented

#### Scenario: blocked_repair_required verdicts under a pass route are disclosed
- **WHEN** the node routes `pass` while a `blocked_repair_required` verdict is present
  because the run has no declared gap work or the wave2 gate already degraded
- **THEN** the report plan lists that question under mandatory uncertainties carrying the
  verdict's bounded limitation note, and `readiness_blocked_count` still counts it

#### Scenario: A conservative fallback discloses answerability as unverified
- **WHEN** the critic execution fails or its candidate is inadmissible and the node
  routes `pass`
- **THEN** every supplied question appears under mandatory uncertainties with the closed
  fallback limitation note rather than vanishing from the delivered plan

#### Scenario: High-confidence findings become conclusions despite an insufficient critic verdict
- **WHEN** the canonical synthesis artifact carries a `confidence=high` finding with
  non-empty backing refs contained in the accepted ledger and `search_required=false`,
  and the critic judges the corresponding question not substantive
- **THEN** the plan still carries that finding's statement as a writable conclusion
  with its backing refs, and the critic's judgment appears as a disclosed mandatory
  uncertainty — the run delivers partial conclusions instead of zero

#### Scenario: Findings without complete backing stay out of conclusions
- **WHEN** a finding lacks backing refs, cites a reference outside the accepted
  ledger, is not high-confidence, or asks for more search
- **THEN** it produces no writable conclusion from the finding-derived source

#### Scenario: Unresolved searchable gaps become disclosed uncertainties
- **WHEN** readiness runs with `unresolved_gaps` naming gap `g:x` whose
  `search_required=true` body exists in the canonical synthesis artifact
- **THEN** the report plan lists a mandatory uncertainty carrying that gap's
  description (bounded) and identifying the gap id, and the final report's
  uncertainties section discloses it

#### Scenario: A recorded gap id without a body still discloses honestly
- **WHEN** `unresolved_gaps` names an id whose body is absent from the canonical
  synthesis artifact
- **THEN** the plan still carries a mandatory uncertainty naming that id with an
  explicit no-description limitation rather than dropping or inventing the gap

#### Scenario: No unresolved gaps adds no uncertainties
- **WHEN** readiness runs with empty `unresolved_gaps`
- **THEN** the plan's uncertainties come only from critic verdicts and provenance
  hard-rule failures, exactly as before

#### Scenario: Report plan is persisted and checkpointed
- **WHEN** the materializer produces an admitted report plan
- **THEN** exact serialized bytes are written to the contained canonical plan path and a `ContentRef` with its matching content hash is written to `readiness_report_plan`

#### Scenario: Failed plan persistence cannot mint a reference
- **WHEN** the report-plan artifact cannot be written or verified
- **THEN** readiness does not checkpoint a fabricated plan reference or allow final composition to consume it

### Requirement: Critic runs under bounded read-only policy

The real readiness critic SHALL run through the existing bounded Node Agent path with
one invocation, zero allowed tools, no writable roots, a finite model/token/wall-time
budget, and a closed `ReadinessCriticOutput` candidate. Missing, malformed, duplicate,
out-of-scope, incomplete, or failed execution output SHALL be deterministically
projected to conservative `ready_insufficient_judgment` verdicts for the affected
supplied questions carrying one closed limitation note that states the critic did not
produce an admissible answerability verdict; it SHALL NOT silently use the all-ready
fallback and SHALL NOT project any `ready_substantive` or `blocked_repair_required`
verdict from an observation failure — an execution or admission failure asserts
neither answerability nor a repair need. (`REA-006`)

Whenever the conservative projection substitutes for a critic result — execution
failure or an inadmissible candidate — the node SHALL emit one node-level
`readiness_critic_fallback` observation carrying a closed reason
(`execution_failed` or `candidate_invalid`). The event SHALL be absent when the
critic candidate is admitted, SHALL NOT carry the rejected raw output, prompt text,
or provider payload, and SHALL NOT alter the existing conservative projection or
its disclosed-uncertainty materialization.

The checkpointed critic summary SHALL contain only the admitted, bounded typed
per-question projection consumed by the materializer. Raw provider output, prompt
text, sandbox paths, rejected candidate content, and unused critic-only fields SHALL
NOT be checkpointed. The critic contract SHALL bound retained field/cardinality values;
the existing policy's structured-result byte budget remains a separate hard cap on raw
bridge success output.

#### Scenario: Invalid output fails closed to existing repair
- **WHEN** the critic result is malformed or does not provide one valid verdict for
  every supplied question
- **THEN** readiness fails closed: it projects `ready_insufficient_judgment` verdicts
  with the closed fallback limitation note, claims no answerability, demands no repair
  route, and the run continues through the existing deterministic owner with those
  disclosures

#### Scenario: Execution failure cannot claim readiness
- **WHEN** the bounded Node Agent reports timeout, configuration, provider, or policy
  failure, including a budget stop such as the per-call output cap
- **THEN** no question is projected as `ready_substantive` or `blocked_repair_required`
  solely from that failure; the run delivers its finding-derived conclusions with the
  unverified answerability disclosed as mandatory uncertainties

#### Scenario: A fallback is visible as a first-class event
- **WHEN** the conservative projection substitutes for the critic result because the
  invocation failed or the candidate was inadmissible
- **THEN** one `readiness_critic_fallback` node event with the closed reason is
  recorded in the run journal, without raw output or prompt text, and the projection
  is unchanged

#### Scenario: Tool posture is enforced
- **WHEN** the readiness critic request and effective runtime policy are inspected
- **THEN** they permit no web, sandbox, or other tool calls and no writable root

#### Scenario: Builder-maximal evidence stays admissible
- **WHEN** the critic request is built with evidence filling the builder's full
  evidence-projection budget and the assembled node policy is inspected
- **THEN** the projected request bytes plus the trusted system prompt plus the
  per-call output cap do not exceed the policy's total token budget, so the call
  reaches the provider instead of being refused by admission control

#### Scenario: Rejected output is not retained as checkpoint authority
- **WHEN** critic output fails admission
- **THEN** checkpoint state records only the conservative projected verdicts and no
  raw rejected output, provider diagnostic, or prompt text

#### Scenario: Unused parseable critic fields are not retained
- **WHEN** an otherwise admitted candidate includes critic-only limitations, synthesis
  flaws, or contradiction identifiers that the report-plan materializer does not read
- **THEN** `readiness_critic_summary` contains only the bounded admitted per-question
  projection and none of those extra fields

## ADDED Requirements

### Requirement: Readiness visit decisions are first-class journal facts

The readiness node SHALL record one node-level visit-decision fact in the run journal
for every readiness visit, carrying only closed, deterministic decision fields: the
written `route` (`pass`, `repair_targeted`, or `exhausted`), the blocked-verdict count,
a closed flag naming the active pass-guard when the node routes `pass` despite blocked
verdicts (`wave2_degraded`, `no_declared_gap_work`, or `fallback_projection`), and the
closed structural failure codes collected that visit when the route is `exhausted`. The
fact SHALL NOT carry critic raw output, prompt text, evidence content, or any
non-closed value, and SHALL be recorded even when the visit ends in a terminal route so
a blocked-at-readiness terminal retains its structural attribution in the journal.

#### Scenario: A degraded-delivery visit records its guard
- **WHEN** readiness routes `pass` while blocked verdicts are present because the wave2
  gate already degraded
- **THEN** the journal's readiness visit fact carries `route=pass`, the blocked count,
  and the `wave2_degraded` guard flag

#### Scenario: A blocked terminal keeps its structural attribution
- **WHEN** readiness routes `exhausted` after a structural hard-rule failure
- **THEN** the journal's readiness visit fact carries `route=exhausted` and that
  visit's closed structural failure codes, so the terminal's blocking cause is
  retrievable from the journal alone

#### Scenario: An ordinary pass visit stays minimal
- **WHEN** readiness routes `pass` with no blocked verdicts and no fallback
- **THEN** the journal's readiness visit fact carries `route=pass`, a zero blocked
  count, and no guard flag
