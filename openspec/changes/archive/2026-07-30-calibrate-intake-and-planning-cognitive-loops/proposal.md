## Why

HITL1 and topic planning already have bounded, zero-tool model loops with deterministic
admission, but their current evidence establishes composition and failure conformance rather
than whether their candidates faithfully turn a user request into a usable confirmed profile and
non-overlapping research plan. This is the first quality-calibration change in the roadmap, so
it must make the model-visible decision criteria and the evidence boundary explicit without
mistaking a fluent candidate for an accepted profile, topic registry, route, or research result.

## What Changes

- Revise HITL1's four existing capability/prompt policies so a profile brief is a conservative,
  decision-ready proposal and semantic intake faithfully distinguishes confirmation, revision,
  question, and clarification while preserving the human reply as untrusted data.
- Revise topic planning's initial and repair policies so candidates decompose only the confirmed
  profile into a bounded, non-overlapping plan that makes every must-answer binding and material
  scope/exclusion explicit; the deterministic materializer remains the authority for acceptance,
  stable identifiers, coverage checks, checkpoint state, and routing.
- Add a small labeled calibration corpus and branch-specific rubrics for the six existing
  zero-tool branches. Deterministic tests will prove request composition, bounded repair, and
  non-admission; an explicitly selected `requires_llm` lane will evaluate only the stated
  judgment claims and report its result as live evidence rather than as a default CI guarantee.
- Keep all existing tool postures, bridge budgets, failure/recovery owners, human-interrupt
  protocol, profile/topic schemas, deterministic validation, and graph topology unchanged.

## Change Focus

- **Primary module / causal owner:** `agent/src/deerflow_deep_research/graph/nodes/hitl1/` owns
  the first bounded model interpretation of the original question and correlated human reply.
- **Question:** Can the existing HITL1 intake branches and their necessary topic-planning consumer
  produce conservative, decision-ready candidates for a bounded labeled corpus without treating
  untrusted input or model output as profile, topic, or route authority?
- **Necessary adjacent/external contracts:**
  `graph/nodes/topic_planning/` consumes only confirmed HITL1 profile fields and owns the plan
  candidate boundary; its question is whether its two zero-tool request policies preserve those
  constraints while making useful, non-overlapping coverage explicit. `evaluation-hardening`
  and its test-only `tests/scenarios/live.py` report contract own the question of how the labeled
  calibration corpus, deterministic composition proof, optional live judgment evidence, and
  evidence-v1 archive compatibility remain distinct.
- **Evidence seam:** production prompt builders plus the real node with fake capabilities for
  deterministic request/admission assertions; a separate selected `requires_llm` calibration
  case with a typed rubric for judgment quality.
- **Not in scope:** `backend/`, `frontend/`, HITL2 interaction, Wave0/Wave1/Wave2/targeted
  programs, tool/bridge policy, model-provider selection, retry/fallback bounds, profile/topic
  schemas, checkpoint or lifecycle state, route ownership, canonical live-canary count/budget,
  and any claim of research/source quality.
- **Triggered charter policies:** change-admission, node-agent-workflow-integrity, workflow-outcome-review

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| HITL1 profile brief | node-agent | What conservative profile dimensions and must-answer questions should be proposed from the bounded original question? | Original question is task data; closed enums and output schema are graph-owned. | Forbidden; existing HITL1 bridge permits no tools and enforces its existing call bound. | `StructuredBrief`; HITL1/domain and the human confirmation path alone admit a profile. | Existing HITL1 structured repair and provider recovery bounds. | `build_brief_prompt` plus real HITL1 node fake-capability tests. |
| HITL1 profile-brief repair | node-agent | Can one invalid brief be repaired without changing the bounded assignment or inventing requirements? | Original question and compact validation category only; invalid candidate remains untrusted. | Forbidden; existing HITL1 bridge. | `StructuredBrief`; existing parser and HITL1 flow admit or block it. | Existing one repair within the current visit ceiling. | Repair request composition and exhausted-path tests. |
| HITL1 semantic intake | node-agent | Which single intent does a correlated human reply express about the current proposal? | Current proposal is trusted context; reply is untrusted data. | Forbidden; existing HITL1 bridge. | `SemanticCandidate`; existing HITL1/domain resolver alone controls proposal/profile changes. | Existing semantic repair and non-terminal feedback bounds. | `build_semantic_intake_prompt` and correlated lifecycle tests. |
| HITL1 semantic-intake repair | node-agent | Can one malformed semantic candidate be repaired while preserving ambiguity and the current proposal? | Same proposal/reply and validation fact; no action, route, or checkpoint fields. | Forbidden; existing HITL1 bridge. | `SemanticCandidate`; existing resolver accepts only legal candidate values. | Existing one-repair/call ceiling and fallback. | Repair prompt and semantic exhaustion tests. |
| Topic planning | node-agent | How should the confirmed profile be decomposed into bounded, distinct topics that visibly cover its must-answer questions? | Checkpointed confirmed profile is trusted; model output is an advisory plan candidate. | Forbidden; existing topic-planning bridge permits no tools and enforces its existing call bound. | `TopicPlan`; deterministic materializer alone derives IDs, validates coverage, writes registry, and selects the route. | Existing one structured repair and exhausted path. | `build_planner_prompt` and materializer/node tests. |
| Topic-plan repair | node-agent | Can one invalid plan be repaired using only its confirmed profile and validation facts? | Confirmed profile and compact validation facts only; draft remains untrusted. | Forbidden; existing topic-planning bridge. | `TopicPlan`; existing materializer admits or rejects it. | Existing one repair and terminal exhaustion bound. | Repair request composition and repeated-invalid plan tests. |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Selected calibration has no required model credential | `preflight_live_environment` | Operator configuration; no invocation or automatic retry | Selected test fails before execution and produces no quality evidence | Configure a supported model credential or do not select the live case | `tests/unit/test_live_evaluation.py` preflight tests |
| Canonical canary collection changes count, identity, or budget | `LIVE_CANARIES` plus `validate_live_canary_deadlines` | Implementer corrects the separate collection; canonical collection has no recovery path | Deterministic governance test fails; no calibration case is admitted to canonical canaries | Keep calibration in its separate collection and repair the test asset | `tests/live/test_canaries.py` and canary-deadline contract tests |
| A selected calibration violates a hard invariant or exhausts its declared execution attempt | Existing `LiveScenarioRunner` and branch executor | Existing scenario attempt bound only; this change adds no retry | Existing `LiveScenarioFailure` report records the failed invariants | Investigate the deterministic branch seam or rerun an explicitly selected live case after correction | Live-runner failure-report tests and branch fake-capability tests |
| A live candidate is structurally valid but does not meet all rubric criteria | Test-only calibration rubric evaluator | No automatic recovery or production retry | Typed `limited` or `inconclusive` rubric result is supplemental evidence only | Review the local policy/corpus; do not alter profile acceptance, topic publication, or routing | Typed rubric/report contract tests plus branch request-composition tests |
| An evidence-v1 archived live report predates the optional rubric result | `scan_live_report_archive` compatibility projection | No migration; absent optional result is represented as absent | Archive remains readable without a quality-rubric claim | Use the archived deterministic evidence as recorded; run a new selected calibration only when current live evidence is needed | Archive-scan compatibility tests with a pre-rubric evidence-v1 fixture |

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `hitl1-node`: define calibrated, conservative profile-brief and semantic-intake candidate
  behavior without changing human or deterministic authority.
- `topic-planning-node`: define calibrated profile-faithful, bounded topic-decomposition behavior
  without changing materialization or route authority.
- `evaluation-hardening`: define branch-specific deterministic and optional live calibration
  evidence for the intake-and-planning judgment claims.

## Impact

- Affected code is limited to `agent/src/deerflow_deep_research/graph/nodes/hitl1/` and
  `agent/src/deerflow_deep_research/graph/nodes/topic_planning/`, their package-local capability
  Markdown, generated prompt-catalog projection, and focused `agent/tests/` evidence/evaluation
  assets, including the test-only live-report contract and a separate calibration collection.
- The implementation also registers `HIN-012`, `TOP-007`, and `EVH-018` in
  `openspec/governance/req-registry.yaml`; that registry entry is project governance metadata,
  not runtime behavior.
- No public API, DeerFlow host interface, database schema, provider configuration, tool inventory,
  or `backend/` / `frontend/` change is introduced.
- Default deterministic verification remains network-free; the calibration quality lane is
  separately selected and credential-gated.
