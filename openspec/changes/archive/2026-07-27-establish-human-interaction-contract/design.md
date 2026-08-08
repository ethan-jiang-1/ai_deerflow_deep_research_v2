## Context

HITL1 currently has two incompatible input models. The graph can safely accept a
correlated typed `accept_suggestion` action, while a person using the real CLI sees a
text prompt. The CLI translates only one magic phrase into that action; all other
text, including a natural confirmation, enters the deterministic profile parser. A
zero-recognition reply increments a rejection counter and the follow-up context drops
the advertised action. This is a deterministic contract failure, not a missing alias.

The graph remains the only authority for lifecycle transition, request correlation,
and advertised actions. The new domain contract owns only the bounded interpretation
of a current proposal and a safe presentation projection. Raw reply text and model
output remain ephemeral and never enter checkpoint, bundle, diagnostics, or adapter
state.

## Goals / Non-Goals

**Goals:**

- Let a person naturally confirm, revise, ask about, or clarify a complete HITL1
  proposal without learning a transport token or JSON schema.
- Keep semantic intake strictly advisory: it yields a closed candidate intent, never
  an action, route, request id, checkpoint update, or provider policy decision.
- Keep the proposal visible and recoverable after ambiguity, a question, malformed
  semantic output, or a semantic-provider failure.
- Give all adapters one safe projection with explicit visible controls and make
  control selection bind to a current advertised graph action only inside trusted
  runtime/broker code.
- Bound semantic invocation to at most three calls per reply: at most two transient
  provider retries and at most one structured-output repair in the shared budget.

**Non-Goals:**

- No generic chat intent router, cross-process continuation, HITL2 redesign, or
  semantic interpretation of the initial research question.
- No provider-global retry setting, tool use by semantic intake, or model authority
  over profile publication.
- No changes to `backend/` or `frontend/`; old checkpoints remain readable through
  defaults and old submitted responses are not reinterpreted.

## Decisions

### 1. Introduce a domain-owned closed interaction contract

`domain/human_interaction.py` will define frozen bounded contracts:

- `InteractionSubject`: proposal version and human-safe current proposal facts.
- `HumanIntent`: closed candidate kinds `accept_current_proposal`,
  `revise_proposal`, `ask_about_proposal`, and `clarify`.
- `SemanticCandidate`: model-shaped candidate with only bounded candidate data.
- `InteractionResolution` and `InteractionFeedback`: graph-consumable outcomes that
  preserve the current proposal unless a complete revision is accepted for display.
- `VisibleControl`: an adapter-safe control id, label, and consequence with no graph
  action id.
- `InteractionProjection`: the one controller-derived prompt projection containing
  subject, feedback, and visible controls.

The contract validates enum values, full revision shape, text limits, and unique
control ids. It has no dependency on runtime, lifecycle, or graph modules. This avoids
turning a prompt string into a second authority and prevents a lifecycle/domain import
cycle.

Alternative considered: use only aliases in the deterministic parser. Rejected: it
cannot answer questions, distinguish ambiguity, explain a recommendation, or make the
available control discoverable. Alternative considered: let the model emit a graph
action. Rejected: a model response cannot own correlation or transition authority.

### 2. Separate candidate intake from graph resolution

On a raw HITL1 text response with a complete current proposal, HITL1 calls a zero-tool
structured semantic-intake prompt. The prompt includes only the original question,
current bounded proposal, raw reply, and the closed result schema. The candidate is
resolved by pure domain validation before the graph writes state:

- `accept_current_proposal` becomes final profile only after normal correlated response
  validation has completed.
- `revise_proposal` must contain a full valid profile. HITL1 checkpoints it as a new
  advisory proposal version, displays all material values, and requires a fresh
  confirmation; it is never auto-accepted.
- `ask_about_proposal` returns one bounded explanation/answer about why the proposed
  setting fits the stated question and reissues the same proposal. The prompt prohibits
  a research finding, external claim, or unbounded general answer.
- `clarify` returns one focused clarification and reissues the same proposal.

Questions and clarification never advance accepted answer rounds or the legacy
`profile_rejection_round`. A semantic failure likewise creates non-terminal feedback
and retains the proposal. The existing deterministic partial-profile flow remains for
old/incomplete checkpoints and accepted field answers; new complete-proposal natural
text takes semantic intake first.

### 3. Keep semantic recovery local and bounded

HITL1 owns semantic call sequencing. Each human reply gets a fresh budget of three
bridge/model calls. A valid retry-eligible provider observation can consume at most two
automatic retry slots; one malformed structured result can request at most one repair;
both consume the same three-call cap. Cancellation propagates. Authentication,
configuration, policy, unknown failures, repeated malformed output, and exhausted
transients do not block the research lifecycle: they become a closed feedback category
with the current proposal and a visible fallback control.

The runtime bridge remains a one-call-per-request, zero-tool executor. It does not
retry or decide semantic recovery. This preserves its existing phase/budget boundary.

### 4. Project controls rather than expose action tokens

`HumanInputRequest` gains an optional typed `interaction` projection alongside the
legacy bounded context string. New HITL1 prompts fill it from controller-owned state;
`ResearchRunExperience` reads it directly instead of deriving visible controls or
material constraints from JSON context. Legacy requests continue through the existing
safe context decoder.

`PromptView` and broker/session projections expose `VisibleControl`, not action ids;
the legacy transport action collection stays only on `HumanInputRequest` and in the
generic verifier.
`SelectControlRun(control_id)` is a generic run intent. Only trusted runtime resolves
the current displayed control against the pending typed request and maps it to an
advertised `accept_suggestion` action. The broker repeats that binding while its
existing namespace lock is held. Direct typed actions remain supported for existing
transport compatibility, but adapters no longer translate magic text or machine action
ids.

### 5. Checkpoint compatibility and state ownership

The checkpoint stores only a bounded proposal version and feedback projection needed to
reissue the next prompt. It does not store raw replies, semantic prompts, candidates,
or provider bodies. New `ResearchCheckpoint` fields default safely for schema-v2
checkpoints. The controller is their sole writer and they clear on accepted profile,
cancel, or terminal result. Existing proposal state without interaction fields is
projected as the compatible current proposal; previously submitted replies retain their
normal consumed-response behavior.

### 6. Establish a recurring human-interaction integrity review rule

The charter receives a focused policy for changes that add a human decision or input
surface. It asks reviewers to identify the semantic subject, raw-input interpretation
authority, visible legal controls, adapter binding boundary, recovery behavior, and
lowest deterministic transcript. The policy guides design only; exact behavior remains
in capability specs.

## Risks / Trade-offs

- [Semantic provider unavailable during a confirmation] -> preserve the proposal,
  show closed feedback, and render a numbered current-proposal control rather than
  terminating or consuming a human-answer budget.
- [A model attempts to smuggle an action or partial revision] -> schema admits only
  candidate data; domain validation rejects it and graph authority remains unchanged.
- [A stale UI control is clicked] -> runtime/broker binds it only against the current
  pending request and advertised typed action; generic verifier still fails closed.
- [A new projection diverges from graph state] -> projection derives from the pending
  typed request plus controller checkpoint facts; deterministic adapter and broker
  tests prove current/stale behavior.
- [Adding semantic calls makes the first prompt unexpectedly expensive] -> invocation
  occurs only after a raw reply, uses zero tools and a three-call ceiling, and has a
  focused test seam rather than a live-provider claim.

## Migration Plan

1. Add the domain contract, typed request/projection fields, defaults, and structure
   registry entries.
2. Add semantic prompt/result handling and HITL1 state transitions behind the existing
   request-correlation path.
3. Add runtime and broker control binding, then migrate CLI/TUI/workbench rendering.
4. Run focused deterministic tests and the complete `UV_OFFLINE=1 make verify` gate.

Rollback is a code rollback: absent interaction fields make old checkpoints readable;
the graph continues to use existing typed action validation. No data migration or
provider configuration migration is required.

## Open Questions

None. The accepted decisions are a bounded explanation for proposal questions, a
numbered CLI fallback control, and two automatic transient retries within three total
semantic calls.
