# Plan: Real Demo Stabilization - BUG-017 to BUG-021 Repair Program

> Type: repair execution plan / handoff document | Status: both repair changes archived; supplemental live replay incomplete | Updated: 2026-08-02
>
> Implementation order: exactly two sequential repair changes. The later
> policy-gate-injection-layer work is deliberately not a prerequisite.

## Decision

The failed Chinese storage-comparison demo exposed five active bugs, but they are
not five independent implementation projects. They form two causal groups:

| Order | Planned OpenSpec change slug | Bugs | Primary owner | Status | Why this is one change |
| --- | --- | --- | --- | --- | --- |
| 1 | fix-topic-planning-provider-outcomes | BUG-017, BUG-018 | runtime/ | Archived: implementation `0ce8a3b`; archive `023680b` | The shared boundary is RuntimeNodeAgentBridge: it projects a node-agent stop or provider exception into the NodeProblem consumed by topic planning. A correct retry cannot be implemented separately from truthful failure projection. |
| 2 | harden-hitl1-comparison-intake | BUG-019, BUG-020, BUG-021 | domain/profile.py with graph/nodes/hitl1/ as the necessary adjacent contract | Archived: commit `771e8f3`; archive `openspec/changes/archive/2026-08-02-harden-hitl1-comparison-intake/` | All three decide when a user's scope, confirmation, and language preference become typed profile state. Splitting them would repeatedly modify the same persisted profile, completion predicate, HITL request, and downstream prompt inputs. |

This is a two-change stabilization program, not an invitation to repair every
newly discovered imperfection. A new finding is recorded and triaged, but it
does not enter either change unless it changes one of the explicitly named
contracts below.

The deferred governance plan remains useful after these repairs. Its current v1
does not alter runtime behavior, and it still names an active-change migration
that is now archived. It must be refreshed using the two real repair changes as
evidence, rather than delaying this incident response.

## Evidence and Boundaries

The starting evidence is the retained real-demo run
r_pT1B7bsx-CnWHknsW_HcykxMnQA5ddYDX4sRHSb_Dlk and the five active bug cards:

| Bug | Observed failure | Repair destination |
| --- | --- | --- |
| BUG-017 | A zero-tool topic-planning stop is shown as tool.execution_failed. | Change 1 failure projection. |
| BUG-018 | A real httpx.ReadTimeout reaches topic planning as internal.unexpected without a provider observation, so the declared one-shot retry never starts. | Change 1 provider observation and recovery admission. |
| BUG-019 | An unspecified comparison can be accepted and researched as an implicit model-selected pair. | Change 2 typed comparison scope and profile completeness. |
| BUG-020 | A clear natural-language confirmation invokes the model instead of the visible action's deterministic path. | Change 2 contextual deterministic confirmation. |
| BUG-021 | Chinese request text can produce English scope and report intent because language is not profile state. | Change 2 typed language preference and propagation. |

The detailed evidence remains in:

- ../bugs/BUG-017-zero-tool-stops-misclassified-as-tool-failures.md
- ../bugs/BUG-018-topic-planning-provider-timeouts-not-retry-eligible.md
- ../bugs/BUG-019-comparison-subjects-not-required-before-start.md
- ../bugs/BUG-020-natural-hitl-confirmation-remains-model-dependent.md
- ../bugs/BUG-021-research-output-language-not-bound-to-request-language.md

### Program-wide non-goals

- Do not modify backend/ or frontend/.
- Do not create openspec/guardrails/, implement cross-session control, or begin
  the policy-injection change while either repair is active.
- Do not redesign every node's provider retry policy. Change 1 is limited to
  the bridge classification/admission contract and topic planning's already
  specified one-shot recovery.
- Do not make the model the authority for profile completeness, accepted
  confirmation, language choice, state writes, or graph routes.
- Do not add a hidden default pair of storage technologies. An explicit pair
  must be shown and accepted by the user, or the run remains in HITL1.
- Do not turn this into generic multilingual translation. The required behavior
  is a deterministic request-language default plus an explicit typed override.

### Program-wide operating rules

- [ ] Before each change, run openspec list --json; keep only one repair change
  active at a time.
- [ ] Create the formal proposal, delta specs, design, and tasks under
  openspec/changes/<slug>/. This file is a handoff plan, not the behavior
  authority.
- [ ] Put a Change Focus card in every proposal and name only the needed
  adjacent contracts. Do not broaden inspection because a future feature might
  use it.
- [ ] Write the smallest deterministic red test before production code. A
  credentialed real demo is supplemental evidence, not the proof seam.
- [ ] Record any out-of-scope finding as a new bug card, then continue the
  current change unless its named invariant cannot be preserved.
- [ ] Do not start change 2 until change 1 is archived and its focused tests,
  strict OpenSpec validation, and deterministic repository verification pass.

## Dependency and Exit Shape

~~~text
retained real-demo failure
          |
          v
Change 1: truthful bridge outcome + eligible provider observation
          |
          v
Change 2: explicit scope + deterministic confirmation + typed language
          |
          v
one end-to-end Chinese comparison acceptance replay
          |
          v
refresh and propose policy-gate v1 using observed repair evidence
~~~

The two changes are technically adjacent rather than code-dependent, but the
execution order is intentional. Change 1 restores truthful, recoverable runtime
behavior before another agent uses the real demo to validate Change 2. Change 2
then prevents a successful run from researching a pair the user never chose.

## Change 1: fix-topic-planning-provider-outcomes (archived 2026-08-02)

**Completed in:** implementation commit `0ce8a3b`; archive and main-spec sync commit
`023680b`.

### Focus and contract

| Item | Plan |
| --- | --- |
| Primary module / causal owner | deerflow_research/src/deerflow_deep_research/runtime/node_agent_bridge.py |
| Question | How does a zero-tool node-agent termination or provider exception become a safe NodeProblem with enough truth for the owning topic-planning node to make its already-specified recovery decision? |
| Necessary adjacent contracts | graph/nodes/topic_planning/node.py consumes the result; domain/run_experience.py owns the closed failure and presentation contracts; domain/workflow_outcomes.py owns normalization and safe diagnostic identity. |
| Main specs to read before proposing | node-agent-runtime, topic-planning-node, workflow-failure-outcomes, research-run-experience. |
| Triggered review policies | workflow-outcome-review, node-agent-workflow-integrity, control-and-recovery, authority-and-projections, participant-outcomes. |
| Not in scope | New provider vendors, retry counts beyond topic planning's existing one retry, generic tool-policy rewrites, raw exception display, or a new generic error controller. |

### Decisions that the formal design must make explicitly

1. PhaseAgentStop is a family of stops, not evidence of tool execution. The
   bridge must preserve the stop's safe finish_reason and map each admitted
   category truthfully. tool.execution_failed is allowed only where an actual
   tool execution failed; it must not be the blanket projection for usage,
   budget, or policy stops.
2. The existing closed RunFailureCode registry has no obvious dedicated
   usage_unavailable code. The proposal must choose and document a truthful
   existing projection or add the smallest closed code needed. It must not hide
   the distinction merely by changing prose.
3. Provider observation admission cannot be context.node_name == "hitl1".
   A named execution policy/capability must explicitly authorize the safe model
   binding observation for the zero-tool topic-planning request. Preserve the
   existing HITL1 behavior while extending only the authorized topic-planning
   case.
4. topic-planning-node already owns the one-shot timeout/unavailable retry.
   The bridge supplies the classified problem and safe observation; it does not
   own retry loops, state writes, or terminal routes.
5. The terminal projection must retain the actual closed category and safe
   diagnostic identity. User-visible presentation consumes that typed result;
   no new presentation-side inference is permitted.

### Implementation checklist

- [x] Create openspec/changes/fix-topic-planning-provider-outcomes/ with a
  Change Focus card and one Workflow Outcome Review. Add a Node Agent Review
  only for the bridge's bounded model/tool admission question; do not describe
  topic-planning recovery as an LLM decision.
- [x] Add delta requirements for truthful zero-tool stop projection, explicit
  provider-observation admission, one eligible topic-planning timeout retry,
  and preserved safe terminal diagnostic projection.
- [x] Write red bridge tests in tests/unit/test_node_agent_bridge.py:
  an AgentBudgetError with NodeFinishReason.USAGE_UNAVAILABLE for a zero-tool
  topic-planning request must not yield tool.execution_failed; an
  httpx.ReadTimeout must yield provider.timeout and a valid observation when
  the topic-planning policy authorizes it.
- [x] Extend the bridge mapping/admission implementation with a closed,
  reviewable policy instead of a node-name special case. Preserve cancellation
  propagation and redaction guarantees.
- [x] Add a graph-level red/green case in tests/graph/test_topic_planning_node.py
  or its closest lifecycle seam: the eligible initial timeout invokes the
  planner exactly twice, records attempt/retry/exhaustion facts correctly, and
  never turns structured-output repair into provider recovery.
- [x] Add the bridge-to-graph integration case in
  tests/integration/test_topic_planning_lifecycle.py: drive the actual bridge
  boundary, not a hand-built NodeProblem, so the existing fixture-only gap
  cannot recur.
- [x] Add or update the smallest presentation/contract assertion showing that
  the terminal message follows the truthful closed code and diagnostic record,
  not the old generic tool-failure wording.
- [x] Run focused tests before widening verification:

~~~bash
cd deerflow_research
uv run --extra operations python -m pytest \
  tests/unit/test_node_agent_bridge.py \
  tests/graph/test_topic_planning_node.py \
  tests/integration/test_topic_planning_lifecycle.py \
  tests/contract/test_run_experience_contract.py -q
~~~

- [x] Run openspec validate fix-topic-planning-provider-outcomes --strict, then
  UV_OFFLINE=1 make verify and git diff HEAD --check. Record the exact commands
  and worktree state in the change tasks before archive.

### Change 1 acceptance conditions

- [x] A zero-tool USAGE_UNAVAILABLE stop preserves a safe, non-tool failure
  category and does not tell the user to check research tools.
- [x] An eligible topic-planning ReadTimeout carries provider.timeout plus a valid,
  redacted provider observation through the real bridge boundary.
- [x] Topic planning performs exactly one automatic provider retry. A second
  eligible provider failure is terminal with an accurate recovery projection;
  a non-provider failure does not gain an invented retry.
- [x] HITL1's existing admitted provider behavior remains covered by regression
  tests.

## Change 2: harden-hitl1-comparison-intake (archived 2026-08-02)

**Completed in:** commit `771e8f3`; archived at
`openspec/changes/archive/2026-08-02-harden-hitl1-comparison-intake/`.

The deterministic acceptance evidence passed. The supplemental explicit-pair
live replay stopped at HITL1 with `budget.exhausted` before profile publication,
clear-confirmation handling, or topic planning, so it is retained as incomplete
evidence rather than reported as a successful replay.

### Focus and contract

| Item | Plan |
| --- | --- |
| Primary module / causal owner | deerflow_research/src/deerflow_deep_research/domain/profile.py |
| Question | Which comparison scope, confirmation, and language facts must be typed before the graph may accept a research profile, and which bounded interpreter may turn user text into those facts? |
| Necessary adjacent contracts | graph/nodes/hitl1/node.py owns the interaction and admission route; domain/human_interaction.py owns the interaction subject/action semantics; profile consumers such as topic-planning prompt inputs must receive accepted facts without re-inferring them. |
| Main specs to read before proposing | hitl1-node, human-interaction-contract, agent-led-research-decisions, topic-planning-node, and the profile/checkpoint persistence contracts discovered from the Focus Card. |
| Triggered review policies | human-interaction-integrity, authority-and-projections, node-agent-workflow-integrity, workflow-outcome-review, control-and-recovery. |
| Not in scope | A universal natural-language classifier, automatically selecting a supposedly common storage pair, translating arbitrary output after the fact, new upstream UI work, or a second route authority outside HITL1. |

### Required design decisions

The formal design must settle these decisions before implementation. They are
intentionally explicit because putting them in prompt prose was the source of
BUG-019 and BUG-021.

| Decision | Required outcome |
| --- | --- |
| Comparison scope | Define a bounded, canonical typed representation for exactly two nonempty, distinct comparison subjects. It belongs in StructuredBrief, PartialResearchProfile, ResearchProfile, canonical persisted bytes, state projection, and downstream prompt inputs as needed. It must not be encoded only in must_answer, scope_boundaries, or custom_notes. |
| When the pair is required | A supported explicit comparison request must enter a typed comparison-intake path. A brief that identifies comparison but lacks the pair remains incomplete and cannot expose accept_suggestion. Ambiguous requests ask a bounded follow-up rather than silently selecting a pair. The design must state the deterministic supported signal and the fallback, including Chinese and English regression cases. |
| Confirmation | The visible accept_current_proposal control and an exact, bounded set of normalized clear confirmation phrases share one typed accept_suggestion path, but only when the currently displayed proposal is complete and version-correlated. Mixed, modifying, questioning, or ambiguous text continues to the existing bounded semantic intake. A direct confirmation must create no node-agent request. |
| Language | Separate immutable request-language evidence from the accepted interaction/output language preference. Derive the supported request-language default locally; if the request is outside the supported deterministic detection set, request an explicit visible choice. Never let the brief model silently choose English for Chinese input. Persist the accepted language and pass it to every owned profile consumer. |
| Compatibility | Changing a frozen profile schema, canonical hash, and checkpoint projection needs an explicit backward-compatibility decision. Old retained profiles must either remain readable under a documented compatible default or be rejected/migrated deliberately; no silent reinterpretation of an accepted historic profile. |

### Implementation checklist

- [x] Create openspec/changes/harden-hitl1-comparison-intake/ only after
  change 1 archives. Include a Change Focus card, Node Agent Review for the
  residual semantic-intake candidate, Workflow Outcome Review for its bounded
  provider behavior, and a Control Placement Review copied as a voluntary
  design record from the deferred policy plan. The latter guides review only
  and creates no runtime authority.
- [x] Write delta requirements that make comparison-subject completeness, local
  confirmation, language default/override, profile persistence, and downstream
  propagation observable behavior.
- [x] Write red domain tests in tests/domain/test_profile.py for canonical pair
  validation, profile incompleteness without a required pair, stable
  canonical/hash behavior, parsing/merge behavior, and the chosen old-profile
  compatibility rule.
- [x] Extend profile/state contracts and the request-bundle persistence seam.
  Add fields only where they are authoritative; do not create a duplicate
  profile fact in an interaction projection or prompt catalog.
- [x] Change HITL1 proposal construction so a missing required pair produces a
  focused comparison-subject request and never an actionable generic
  "Start with the current proposal" control.
- [x] Add deterministic text-confirmation recognition before
  _classify_proposal_reply(). Assert an exact clear Chinese and English
  confirmation takes the action path with zero node-agent calls; assert a
  modification or ambiguous reply still uses the semantic path.
- [x] Make request/profile language visible in the proposal and all direct
  profile consumers. Update only the prompt builders that own this behavior;
  add a consumer inventory test or focused prompt assertions so a later node
  cannot silently fall back to its model default.
- [x] Add HITL1 graph tests in tests/graph/test_hitl1_node.py for all four
  branches: incomplete comparison scope; explicit pair accepted; local clear
  confirmation; semantic fallback. Keep proposal-version and request-id
  correlation assertions intact.
- [x] Add lifecycle coverage in tests/integration/test_hitl1_lifecycle.py that
  persists and reloads the accepted pair and language from request/profile.json,
  then proves only the legal route enters topic planning.
- [x] Run focused tests before widening verification:

~~~bash
cd deerflow_research
make test-intake
uv run --extra operations python -m pytest \
  tests/graph/test_topic_planning_prompts.py \
  tests/graph/test_topic_planning_node.py \
  tests/integration/test_topic_planning_lifecycle.py -q
~~~

- [x] Run openspec validate harden-hitl1-comparison-intake --strict, then
  UV_OFFLINE=1 make verify and git diff HEAD --check. Record actual output,
  focused selectors, and git status --porcelain=v1 --untracked-files=all in
  the authoritative tasks before archive.

### Change 2 acceptance replay

Use this exact stateful scenario in deterministic tests and, after credentials
are available, as a supplemental real-demo replay:

1. Start with 比较两种储能路线的成本、风险与适用场景.
2. The first HITL1 presentation is in Chinese, states that the comparison pair
   is required, and offers no generic accept/start action.
3. Supply or visibly select two explicit routes, for example lithium-ion
   batteries and vanadium redox flow batteries. The accepted profile persists
   the exact pair and language preference.
4. Receive the revised complete proposal in the same language. Reply
   可以，我觉得你说的挺好; it advances through the local typed action path
   without invoking the semantic model classifier.
5. Topic planning receives the accepted profile. If the provider succeeds, it
   produces the normal next state. If it has the transient timeout represented
   in change 1, it retries once and projects the correct final outcome if that
   retry also fails.

**Supplemental replay status:** the generic Chinese request reached the required
HITL1 suspension with no generic accept/start control. The explicit-pair run
then stopped with `budget.exhausted` before profile publication, so steps 3-5
remain unobserved in a credentialed live run. The archived task evidence records
the run and diagnostic identifiers; deterministic tests cover the full scenario.

## Final Program Gate and Handoff Checklist

- [x] Both formal changes have been archived separately with no overlapping
  active change left behind.
- [ ] Each bug card has a link or commit reference to its owning repair change:
  BUG-017/018 to change 1; BUG-019/020/021 to change 2.
- [x] The full deterministic gate passes for each change:

~~~bash
cd deerflow_research
UV_OFFLINE=1 make verify
~~~

- [x] Root governance checks, strict OpenSpec validation, and git diff HEAD
  --check are recorded by each change; backend/ and frontend/ remain untouched.
- [ ] Run the real demo twice when credentials are healthy: first to verify the
  incomplete comparison suspension, then with an explicit pair and clear
  confirmation. Treat a provider outage as a valid supplemental result only
  when the new truthful retry/diagnostic behavior is observed. The first stage
  passed; the explicit-pair replay stopped at HITL1 with `budget.exhausted`
  before profile/topic-planning observations.
- [ ] Inspect the retained run bundle and its diagnostic record. The evidence
  must distinguish a provider failure from a tool failure and must show the
  selected pair/language rather than inferred prose alone. The incomplete
  explicit-pair run cannot yet provide that accepted-profile evidence.
- [ ] Triage any newly found defect against this plan's named contracts. Do not
  append it casually to a completed change.

## After the Two Repairs

Only after the final gate should a separate agent refresh
policy-gate-injection-layer.md. Its first task is to remove the stale assumption
that harden-research-run-diagnostics-and-hitl-intake is active, then use these
two changes as real replay/migration evidence. The policy change remains a
separate governance investment; it is not a condition for restoring the demo.
