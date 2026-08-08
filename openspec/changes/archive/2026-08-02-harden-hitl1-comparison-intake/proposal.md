## Why

The real-demo intake can accept an underspecified comparison, route a clear Chinese or
English confirmation through an unnecessary model classifier, and let an advisory
brief silently select English for a Chinese request. These behaviors make the
accepted research profile less faithful than the user-visible interaction, so the
typed profile contract and its HITL1 admission path must be hardened before another
demo stabilization pass.

## What Changes

- Add typed, canonical comparison-subject and request/output-language facts to the
  research profile. A supported explicit comparison requires exactly two distinct,
  nonempty subjects before a profile may be accepted; it may never be inferred from
  prose or silently defaulted.
- Make HITL1 detect the bounded supported Chinese/English comparison and language
  signals locally, issue a focused incomplete-comparison or language-choice follow-up
  where necessary, and persist only the accepted typed facts through the profile,
  checkpoint, request bundle, and direct profile consumers.
- Recognize an exact bounded set of normalized Chinese and English clear-confirmation
  phrases locally before semantic intake. Correlated complete proposals take the same
  `accept_suggestion` materialization path as the visible control with zero
  node-agent calls; modifying, questioning, and ambiguous replies retain the bounded
  semantic-intake path.
- Preserve safe compatibility for retained legacy profiles and checkpoints without
  inventing a comparison pair or language preference from historical prose.
- Extend deterministic domain, HITL1 lifecycle, persistence, and topic-planning
  prompt evidence for the accepted facts and their legal failure/recovery paths.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `hitl1-node`: require typed comparison/language completion before acceptance and
  add deterministic local confirmation ahead of bounded semantic intake.
- `human-interaction-contract`: project incomplete comparison/language recovery and
  retain visible controls only where their typed action is legally admissible.
- `topic-planning-node`: consume the confirmed comparison and language facts directly
  from checkpoint profile fields without re-inferring them.
- `research-graph-lifecycle`: carry the bounded HITL1 language selection as a
  correlated typed option while preserving existing HITL2 choice compatibility.
- `research-run-experience`: present and submit the typed HITL1 language choice
  without deriving it from context or turning it into an action/control alias.
- `research-session-discovery-and-operations`: preserve the current advertised
  HITL1 language option through the retained-session broker and reject stale options.
- `runtime-operations`: prevent an authorized non-interactive auto-profile policy
  from bypassing required typed comparison or language facts.

## Change Focus

- **Primary module / causal owner:** `deerflow_research/src/deerflow_deep_research/domain/profile.py` owns the typed comparison and language facts, their validation, canonical serialization, and profile completeness.
- **Question:** Which comparison scope, confirmation, and language facts must be typed before the graph may accept a research profile, and which bounded interpreter may only propose a candidate from user text?
- **Necessary adjacent/external contracts:** `graph/nodes/hitl1/node.py` validates correlated interaction input, applies non-interactive admission, owns the persistence call, and routes. `domain/human_interaction.py` defines human-safe subjects, feedback, and visible-control projection without state or route authority. `domain/lifecycle.py` and `domain/run_experience.py` carry an explicit HITL1 language option through the existing correlated response boundary without changing action authority. `runtime/session_operations.py` revalidates the advertised option against the current retained pending request under its namespace lock. `runtime-operations` keeps an authorized non-interactive policy from bypassing the profile's typed admission gate. `graph/nodes/topic_planning/prompts.py` consumes confirmed checkpoint facts in its model input without re-inference.
- **Evidence seam:** Pure profile contract tests for validation/canonical compatibility; HITL1 node and lifecycle tests for interaction correlation, zero-call confirmations, persistence, and legal routing; topic-planning prompt tests for direct typed-fact propagation.
- **Not in scope:** `backend/` or `frontend/` changes; a universal language or intent classifier; implicit/default storage-pair selection; arbitrary post-hoc translation; generic semantic retry redesign; or a second route authority outside HITL1.
- **Triggered charter policies:** human-interaction-integrity, authority-and-projections, node-agent-workflow-integrity, workflow-outcome-review, control-and-recovery, change-admission

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Comparison requirement and supported request-language detection | no-agent | A narrow local Chinese/English signal and typed field validation are deterministic; model judgment must not decide whether a pair or language is required. | Original request is untrusted text; the profile contract owns admitted facts. | No invocation or tools. | Typed parser/profile completeness; HITL1 admits only complete correlated profiles. | HITL1 issues its bounded follow-up; no model fallback for the local detector. | Domain invalid-fixture and HITL1 incomplete-proposal tests. |
| Exact clear confirmation | no-agent | Normalized membership in a fixed Chinese/English phrase set is deterministic and must avoid semantic calls. | Correlated response text and current checkpointed proposal are inputs; neither supplies route authority. | No invocation or tools. | HITL1 maps the recognized reply to the existing `accept_suggestion` action only after completeness/correlation checks. | HITL1 rejects stale/incomplete input and retains the legal follow-up. | HITL1 test asserting zero bridge requests and unchanged correlation rules. |
| Revision, question, or ambiguous natural reply | node-agent | Classify one bounded reply against the current proposal as a candidate confirmation, full revision, question, or clarification when no local confirmation applies. | Original question/current proposal are trusted assignment context; raw reply and model output are untrusted data. | Zero-tool bounded semantic-intake bridge; runtime enforces call budget, cancellation, and provider policy. | Existing semantic candidate resolver and HITL1 remain the sole state, profile-publication, and route owners. | Existing semantic-intake bounded retry/repair/fallback owner remains unchanged. | HITL1 semantic-fallback and provider-failure tests. |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Supported comparison request lacks an explicit valid pair | Partial profile/proposal in HITL1 checkpoint, validated by the profile contract | HITL1 asks a focused correlated follow-up within its existing bounded intake rounds. | No acceptance or `profile.json`; final missing pair blocks rather than degrading into an invented profile. | Supply exactly two distinct subjects or cancel while intake is current; after the terminal result, start an independent run. | HITL1 interaction test verifies no generic accept control and final-round block. |
| Request language is unsupported or ambiguous for the bounded detector | Typed language-choice progress in the profile/HITL1 checkpoint | HITL1 presents one explicit visible bounded language choice through the selected trusted binding. | No accepted profile until a supported choice is supplied; cancellation remains available. | Select a supported language or cancel. | Lifecycle test for visible choice, request correlation, and reload. |
| Exact confirmation for a complete current proposal | Current proposal version and request correlation in HITL1 checkpoint | No recovery: local recognizer enters the existing action materialization path. | Accepted profile and legal `accepted` route. | Continue to topic planning. | HITL1 test asserts zero semantic bridge calls. |
| Semantic intake is unavailable, malformed, or exhausts after a non-local reply | Existing semantic candidate/failure projection owned by HITL1 interaction flow | Existing HITL1 semantic retry/repair bound and non-terminal fallback remain the recovery owner. | Preserve the current confirmable proposal with closed feedback; no profile artifact. | Use visible acceptance control, send a clear confirmation, revise, ask, or cancel. | Existing and extended semantic fallback tests. |
| Non-interactive auto-profile lacks a required pair or a supported output language | Immutable local intake seed and profile contract | The authorized non-interactive policy has no human-recovery channel and cannot supply a default. | Terminal `GATE_BLOCKED`, with no profile artifact or final profile fields. | Start an interactive run with the missing facts, or use a new non-interactive request whose original text contains an explicit valid pair and supported language evidence. | HITL1 auto-profile tests for generic comparison and unsupported language block. |
| Legacy retained profile omits new fields | Profile decode/compatibility contract | Deterministic compatibility normalization only; it may not infer historical pair or language. | Readable legacy record remains explicitly unspecified, never silently upgraded to a modern explicit fact. | Re-enter ordinary intake when a new accepted profile is needed. | Domain serialization/hash and lifecycle reload tests. |

## Impact

Primary implementation is under `deerflow_research/src/deerflow_deep_research/domain/`
with narrow HITL1 graph, lifecycle/runtime binding, state, prompt, and test updates as
required by the accepted contract. It changes persisted profile and checkpoint facts,
their canonical hash bytes, and direct topic-planning prompt inputs. No upstream
DeerFlow service, API, backend, or frontend changes are proposed.
