> req: WON-004, WON-012, WON-013

## Purpose

Replace the Wave1 gate's unanswered `targeted_search` repair promise with a bounded,
gate-owned handoff projection consumed by Wave2 synthesis, and extend Wave1's
post-candidate Journal coverage to the critic review dispatch boundary with a closed
critic kind.

## MODIFIED Requirements

### Requirement: Wave1 gate with provenance, coverage, and critic verdicts

The real Wave1 gate SHALL evaluate the shared `WorkUnitCompletionRule` before its
Wave1-specific review conditions. When structural work completion is satisfied, it
SHALL evaluate a bounded, validated, non-checkpointed review projection for every
accepted topic. The projection SHALL prove: at least two distinct canonical URLs with
`is_new_vs_wave0=true`; presence of both identity-bound SourceDiagnostic and
ClaimVerifier artifacts; and bounded open-question refs — question id and work id —
for every question whose state is `targeted_search`. Question text SHALL NOT enter
the projection: the projection carries ids only, and the owning synthesis node
resolves question text from the accepted Wave1 result documents (WSN-009). The
projection SHALL contain no source body, artifact location, critic reason,
checkpoint field, or route authority, and gate rules SHALL perform no filesystem or
network I/O.

The Wave1-specific rules SHALL make no independent decision while structural
completion is absent. A missing review artifact or an insufficient new-source floor
SHALL produce the existing repairable gate outcome. A `targeted_search` question
SHALL NOT itself produce a repair and SHALL NOT change any worker or critic tool
posture: whenever a validated review projection is present, the gate adapter SHALL
write its targeted-search refs to the gate-owned checkpointed `wave1_open_questions`
control field through the existing `apply_research_update` seam, and that projection
write SHALL NOT change any gate verdict or route. A malformed or unreconciled review
projection SHALL fail before a business-gate pass, repair, or route is emitted.
Critic prose or verdict value SHALL not select a route. The route map SHALL remain
`{PASS: pass, REPAIR: repair, BLOCKED: exhausted}`.

#### Scenario: Missing critic verdict routes repair
- **WHEN** a topic has accepted submissions but lacks one valid bound SourceDiagnostic or ClaimVerifier artifact
- **THEN** the gate routes repair without admitting a pass

#### Scenario: Two distinct new sources satisfy the floor
- **WHEN** an accepted topic has two distinct canonical sources marked new versus Wave0 and both valid review artifacts
- **THEN** the real Wave1 gate may pass after structural completion, and any `targeted_search` question refs from the validated projection are written to `wave1_open_questions` without changing the verdict

#### Scenario: Unresolved question routes repair
- **WHEN** an accepted Wave1 result contains an open question in `targeted_search`
- **THEN** the gate no longer routes repair for that question: it writes the question's bounded ref to the gate-owned `wave1_open_questions` projection, changes no worker or critic tool posture, and leaves the existing repair routes reserved for source-floor and critic-presence failures

#### Scenario: Review projection is bounded and validated before gate evaluation
- **WHEN** a review projection omits an accepted topic, exposes a disallowed field, or cannot reconcile with accepted records and their bound review artifacts
- **THEN** the phase fails at the deterministic validation boundary before a pass, repair, or route is emitted

#### Scenario: Repeated floor failure exhausts to blocked
- **WHEN** repair budget is exhausted and the new-source floor remains unmet
- **THEN** the gate routes exhausted and the lifecycle terminates

### Requirement: Wave1 retains closed response-shape and post-candidate validation evidence

For every Wave1 initial or repair result that reaches the existing parser or local
pre-persistence validation boundary, Wave1 SHALL classify the final response as exactly
one of `empty`, `prose`, `fenced`, `embedded_json`, or `json_object` and retain that
closed classification on its correlated Bundle-local Journal validation fact. `empty`
means no non-whitespace response; `fenced` means a response containing a Markdown code
fence; `json_object` means the complete trimmed response is a JSON object;
`embedded_json` means a non-standalone response contains a JSON object; and `prose`
covers every other non-empty response. The classification SHALL be a structural
observation only and SHALL not cause parsing, semantic validation, admission, repair,
or routing behavior to differ.

When a parser- and locally-valid Wave1 candidate later fails an existing deterministic
post-candidate submission or artifact validation boundary, Wave1 SHALL retain one
correlated `post_candidate` Journal validation fact containing only that boundary's
existing canonical code collection. It SHALL retain no raw response, draft, prompt,
tool observation, URL, artifact path, validation message, or exception text. A
post-candidate fact SHALL not enter the structural repair request or change the existing
controller retry, ledger, critic, gate, route, terminal, or lifecycle owner.

When a Wave1 critic review dispatch — SourceDiagnostic or ClaimVerifier — fails its
agent invocation or its typed result fails the deterministic review-artifact
validation boundary, Wave1 SHALL retain one correlated Journal fact instead of a
silent drop: for an invalid typed result, one `post_candidate` VALIDATION fact with
that boundary's canonical code collection and the closed critic kind; for an
invocation failure, one closed model/tool failure fact with the existing safe
category. Neither fact SHALL retain raw critic output, prompt, tool observation,
URL, artifact path, or exception text, and neither SHALL enter a repair request,
change the critic re-dispatch loop, or change any gate, route, terminal, or
lifecycle owner.

#### Scenario: A final prose response is distinguishable without being retained
- **WHEN** a Wave1 initial or repair result contains final prose after its model turn
- **THEN** the correlated Journal validation fact records `prose` and the existing
  canonical parser code without retaining the response body

#### Scenario: A parser-accepted candidate records a later validation failure safely
- **WHEN** a Wave1 candidate passes parsing and local semantic validation but fails
  deterministic submission or artifact validation
- **THEN** the Journal retains one correlated `post_candidate` fact with the existing
  canonical code collection, no repair request receives that code, and no submission is
  published

#### Scenario: An invalid critic result leaves a safe correlated fact
- **WHEN** a Wave1 critic returns a typed result that fails the review-artifact validation boundary
- **THEN** the Journal retains one `post_candidate` VALIDATION fact for phase wave1 with the boundary's canonical code collection, the closed critic kind, and the work/attempt correlation, and no review artifact is published

#### Scenario: A critic invocation failure leaves a closed process fact
- **WHEN** a Wave1 critic dispatch agent invocation fails with a known safe provider cause
- **THEN** the Journal retains one closed model/tool failure fact with the safe category and the work/attempt correlation, and the existing gate-owned repair loop remains the only recovery owner

#### Scenario: Observation failure never changes critic control flow
- **WHEN** the event recorder is absent or raises while a critic dispatch fails
- **THEN** the dispatch keeps its existing bounded behavior and no gate verdict, route, admission, or terminal disposition changes

## ADDED Requirements

### Requirement: Wave1 targeted-search questions project a bounded synthesis handoff

The gate-owned checkpointed control field `wave1_open_questions` SHALL contain only
validated refs of open questions whose state is `targeted_search`, each ref carrying
exactly a `q:w1_` question id and the accepted work id, all derived from validated
non-checkpointed review projections. Question text SHALL NOT be carried in the
field; the owning synthesis node resolves text from the accepted Wave1 result
documents (WSN-009). The field SHALL be written only by the gate adapter with the
GATE writer role through the existing `apply_research_update` seam. Because a Wave1
repair visit's gate view reconciles only the work planned on that visit, the adapter
SHALL merge the current review's refs with the already-projected refs — deduplicated
by question id, ordered by `(work_id, question_id)` — so an earlier accepted work's
open questions survive later Wave1 visits. The projection SHALL hold at most 64
entries and SHALL contain no source or claim body, artifact path, critic reason,
route, or terminal authority. A merged projection that would exceed the bound SHALL
fail the wave1 gate evaluation with a typed deterministic error and SHALL NOT drop
entries or write a partial projection. The field SHALL be consumed only by Wave2
synthesis as a bounded model-visible assignment, never by a gate rule, worker,
critic, or route.

#### Scenario: Projection carries only bounded validated question refs
- **WHEN** a validated Wave1 review contains targeted-search questions
- **THEN** the gate adapter writes their bounded refs to `wave1_open_questions` with no source body, artifact path, critic reason, or route authority

#### Scenario: A repair visit preserves earlier projected refs
- **WHEN** a validated Wave1 review contains no targeted-search question but the checkpointed projection holds earlier refs
- **THEN** the gate adapter writes the merged projection unchanged rather than replacing it with an empty one

#### Scenario: An over-bound projection fails closed
- **WHEN** the validated review would project more than 64 targeted-search question refs
- **THEN** the wave1 gate evaluation fails with a typed deterministic error and writes no partial projection

#### Scenario: A checkpoint written before the projection defaults empty
- **WHEN** a checkpoint lacks the `wave1_open_questions` field
- **THEN** graph state reads an empty projection and synthesis keeps its existing behavior for that generation

#### Scenario: Only the gate writer updates the projection
- **WHEN** a non-gate writer attempts a `wave1_open_questions` update
- **THEN** the existing state field-ownership machinery rejects the update
