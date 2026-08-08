## Why

The completed control-placement policy can make an author disclose a control
boundary, but its review posture is not reliably returned when an existing change is
applied or archived in a later session. Change 2 makes that posture durable and
event-timed without pretending that prompt guidance executes a review or controls a
native OpenSpec transition.

## What Changes

- Add concise `rules.tasks` language for a proposal that selects `control-placement`:
  it keeps plan-review and archive-closeout-review work in its durable task ledger.
- Add distinct `operations.apply.guidance` and `operations.archive.guidance` entries
  to `openspec/config.yaml`; they route the current agent to the selected change,
  its actual boundary, and actionable findings without executing commands or
  blocking an operation.
- Add deterministic local evidence for the six required OpenSpec integration probes:
  guidance delivery, absence, and fresh config-read behavior, supported archive path,
  observable archive side effects, selected-change diff boundary, historical replay,
  and named observed facts that a later closeout coordinator may evaluate in its own
  proposal.
- Extend the Deep Research Agent Charter requirement and authoring route so the
  guidance's `control-placement`-only trigger, advisory authority boundary, and
  evidence limits remain discoverable.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `deep-research-agent-charter`: add operation-timed, advisory authoring guidance
  and its bounded durable task obligation for selected control-placement reviews.

## Change Focus

- **Primary module / causal owner:** `openspec/config.yaml` owns OpenSpec authoring
  configuration; the existing OpenSpec apply/archive workflows own operation state
  and native transitions.
- **Question:** How can a selected control-placement review return at apply and
  archive time, and retain actionable work across sessions, without granting
  guidance task-writing, command-running, or archive-blocking authority?
- **Necessary adjacent/external contracts:** `deep-research-agent-charter` owns the
  authoring/admission contract; `openspec/policies/control-placement.md` owns the
  selected review trigger; OpenSpec 1.7 `instructions apply/archive --json` defines
  guidance delivery; the existing archive workflow remains the supported transition
  contract; `_backlog/plans/policy-gate-injection-layer/03-openspec-1.7-operation-guidance.md`
  records the local probe basis.
- **Evidence seam:** disposable OpenSpec fixture changes and deterministic
  `instructions`/archive observations prove the configured guidance, its advisory
  failure boundary, selected-change scope, and recorded probe outcomes without a
  provider, runtime graph, or semantic-quality claim.
- **Not in scope:** `openspec/guardrails/`, a runner, dossier persistence,
  fresh-session identity, an impact-packet schema, a semantic evaluator, an archive
  wrapper, a new blocking checker, runtime graph/state behavior, `backend/`, and
  `frontend/`.
- **Triggered review policies:** change-admission, agent-information-map, control-placement

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Apply/archive review posture for a selected control-placement change | Current agent reviews the selected change and records an actionable finding | OpenSpec configuration parser delivers guidance; native apply/archive workflows own operation state and transitions | advisory | Guidance cannot write tasks, run commands, or bypass native archive behavior | Reuse OpenSpec operation guidance and the ordinary task ledger instead of a session banner or archive wrapper | Disposable instruction and archive-side-effect probe |

## Impact

- Affects OpenSpec authoring configuration, the Deep Research Agent Charter,
  deterministic governance/contract evidence, and the policy-gate long-term plan.
- Adds no runtime dependency, provider call, model role, graph route, persistence
  schema, user-facing product behavior, or new `openspec/guardrails/` directory.
