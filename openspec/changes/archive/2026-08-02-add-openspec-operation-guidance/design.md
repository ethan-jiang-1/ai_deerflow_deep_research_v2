## Context

Change 1 established `control-placement` as a selected, structural proposal review
but intentionally does not time that review to an apply or archive operation. The
current OpenSpec configuration has artifact rules but no `operations` block. The
installed OpenSpec 1.7 workflow can return optional `operationGuidance` for apply
and archive; the existing agent skills treat it as additive advice and continue when
it is absent or unreadable.

Change 2 is the middle delivery layer in the agreed three-change program. It leaves
the native apply/archive workflow and its state ownership intact. Change 3 may later
consume observed integration facts, but this change does not create its directory,
runner, dossier, or coordinator.

## Goals / Non-Goals

**Goals:**

- Add a concise, durable authoring obligation for an active proposal that declares
  `control-placement`.
- Distinguish apply plan review from archive actual-boundary closeout in OpenSpec
  operation guidance.
- Establish reproducible local evidence for the six integration questions that
  determine whether Change 3 can be proposed safely.
- Preserve every unknown or failed probe as evidence, rather than turning it into a
  claim that guidance blocked an operation.

**Non-Goals:**

- Do not introduce a `guardrails/` directory, executable runner, task writer,
  archive wrapper, semantic evaluator, or automatic archive denial.
- Do not decide whether a proposal should select `control-placement`, judge a review
  answer, or add a full-worktree scanner.
- Do not change a Deep Research runtime route, model role, state/checkpoint schema,
  provider behavior, `backend/`, or `frontend/`.

## Decisions

### 1. Use one narrow declarative trigger

`rules.tasks` will specify that an active proposal selecting `control-placement`
keeps two ordinary task records: a plan review and an archive closeout review. Each
record names the owner, minimum action, and deterministic or bounded-evidence done
condition. The rule does not apply merely because another charter policy was selected.

The config and guidance are intentionally declarative. They are not a new checker and
cannot inspect a Focus Card or create the tasks themselves. This matches their actual
OpenSpec authority while preserving a durable work ledger for a later session.

Rejected alternative: require these tasks for every selected policy. That would make
ordinary documentation or information-map changes pay the cost of a cross-session
control review, and would weaken the meaning of the `control-placement` trigger.

### 2. Keep apply and archive guidance separate and advisory

`operations.apply.guidance` will tell an agent to re-read the selected change's Focus
Card, review, policy, current tasks, and relevant historical counterexample before a
target edit or resumed apply. It will tell the agent to turn a new actionable finding
into an unchecked task.

`operations.archive.guidance` will tell an agent to bind closeout review to the
selected change's actual boundary, unresolved tasks, and existing deterministic
evidence before describing archive readiness. It will explicitly say that the native
archive operation remains authoritative.

Both entries will say they apply when `control-placement` is selected. OpenSpec emits
the configured strings to every operation lookup; the strings do not claim that the
configuration conditionally inspected the proposal.

The task rule and guidance text therefore carry two separate statements: current
operation guidance is general advisory text, while the plan-review and
archive-closeout-review obligations apply only after the current agent confirms that
the selected proposal declares `control-placement`. A non-selected change receives
no new obligation merely because it received the shared string.

Rejected alternative: add `blocking`, `command`, or `runner` configuration. OpenSpec
does not support those operation contracts, and accepting an advisory prompt as an
enforcer would create false archive authority.

### 3. Treat probes as observed integration evidence

Implementation will use disposable, isolated local roots and record commands, OpenSpec
version, SHA-256 digest of the exact fixture configuration, selected change,
stdout/stderr summary, exit status, observed side effect, and unknowns in
`_backlog/plans/policy-gate-injection-layer/05-operation-guidance-probe-evidence.md`.
That record is durable design evidence, not a coordinator dossier or source of truth.
Each fixture is removed after its observations are recorded; an unavoidable mutation
to a repository-local fixture must instead name every restored path in the evidence.

The six probes are:

| Probe | Question | Required observed result |
|---|---|---|
| Delivery, absence, and fresh read | Do valid, missing, or malformed operation entries appear or disappear through `instructions apply/archive --json`, and does a second lookup read a changed fixture config? | Exact guidance presence/absence, fresh-read result, and parser/consumer limitation |
| Supported archive path | Which local archive command/skill path is actually supported? | Selected path, inputs, warnings, and unsupported alternatives |
| Archive side effects | What do sync, incomplete-task warning, collision, move, and failure leave behind? | Observable filesystem/spec/task/worktree result for each exercised case |
| Selected-change boundary | Can a selected change be separated from unrelated worktree edits? | Reliable boundary or explicit `missing-boundary` limitation |
| Replay and resume | Can a historical boundary case become a task and be reconsidered on resumed apply? | Guidance, task ledger, and honest unclosed/closed result |
| Change 3 handoff facts | Which direct facts could a later coordinator consume without guessing? | Named inputs and explicit unknowns, not a dossier schema |

Rejected alternative: make a successful prose review the probe result. The probe
evidence is about delivery and observable integration boundaries, not semantic-review
quality.

### 4. Reuse existing governance ownership

The existing Agent Charter spec owns `DRC-010`; the existing project requirement,
structure, and evidence registries remain their own authorities. The charter checker
may verify stable authoring anchors and focused fixture shape, but Change 2 will not
add a checker that accepts/rejects an archive based on review tasks. The normal native
archive flow remains unchanged.

The later coordinator may consume named facts from the probes and existing governance
verdicts. It must define its own interface and failure behavior in Change 3; this
change records no new typed coordinator schema.

## Risks / Trade-offs

- [Guidance is ignored or unavailable] -> Preserve the ordinary task obligation and
  record the delivery limitation; do not call it a hard gate.
- [The config becomes an instruction manual] -> Limit each operation to concise
  routing statements and link to the policy/plan for detail; enforce existing line
  budgets.
- [Probe fixtures mutate real planning history] -> Use disposable isolated roots;
  remove them after recording observations or name every restored local fixture path.
- [Archive behavior varies by CLI version] -> Record the exact version and command;
  retain incompatible results as a Change 3 constraint.
- [A broad worktree scan masks scope ambiguity] -> Return and record
  `missing-boundary`; do not claim a selected-change review is complete.

## Migration Plan

1. Add red deterministic fixtures for the task-rule route, distinct apply/archive
   guidance, advisory boundaries, and each local probe's known limitation.
2. Add the concise config rule/guidance, Charter route wording, requirement and
   registry entries, structural/evidence registrations, and the durable probe record.
3. Run the disposable probes, recording both successful observations and limitations.
4. Re-check every active proposal selecting `control-placement`; add the two ordinary
   review tasks only where the declared trigger requires them. Never rewrite archives.
5. Run focused tests and repository governance gates; archive only with exact probe
   evidence and no claim that guidance itself enforced closeout.

Rollback removes the operation entries, task-rule wording, stable route, and Change 2
evidence registrations together. It does not require runtime data migration because
guidance creates no state and any historical tasks remain ordinary change records.
