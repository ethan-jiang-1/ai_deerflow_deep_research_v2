## Why

Change 2 proves that OpenSpec operation guidance can remind a later session to review
an active change, but that guidance neither owns an archive transition nor supplies a
reliable selected-change diff boundary. Without an explicit, Git-verified range, a
closeout review of a shared worktree would overstate what it covered.

## What Changes

- Add a narrow `openspec/guardrails/` capability that resolves a caller-declared
  canonical active change, validates its committed selected-change boundary, and
  produces a structured, non-authoritative evidence record for that exact
  `base..head` range.
- Define a durable evidence protocol that binds the canonical change name,
  repository identity, base and head commits, diff summary, review disposition, and
  linked ordinary unfinished tasks without judging semantic quality.
- Add deterministic rejection handling for missing fields, wrong repositories,
  non-ancestor commits, HEAD drift, and dirty worktrees. Rejections report
  `missing-boundary`; they do not create tasks, run archive, or claim coverage.
- Extend the Deep Research Agent Charter route so selected control-placement work
  can distinguish advisory operation guidance from the separate guardrail evidence
  contract and its non-authoritative closeout result.
- Register the new governance-owned structure and evidence seam. Do not change
  DeerFlow runtime behavior or native OpenSpec apply/archive behavior.

## Capabilities

### New Capabilities

- `selected-change-closeout-evidence`: validates caller-declared committed Git
  boundaries and records bounded, task-linked closeout-review evidence without
  semantic approval or archive authority.

### Modified Capabilities

- `deep-research-agent-charter`: route the existing control-placement operation
  guidance to the new evidence contract while preserving its advisory and
  non-runtime authority boundaries.

## Change Focus

- **Primary module / causal owner:** `openspec/guardrails/` owns the proposed local
  boundary-verification and closeout-evidence protocol; Git owns commit and diff
  facts.
- **Question:** How can a later session record exactly which committed range it
  reviewed, carry actionable findings through ordinary tasks, and report an honest
  non-authoritative disposition without inferring a shared-worktree boundary or
  controlling native archive?
- **Necessary adjacent/external contracts:** `deep-research-agent-charter` owns the
  `control-placement` authoring route and DRC-010 advisory boundary; OpenSpec 1.7
  `instructions apply/archive --json` remains the guidance-delivery contract; Git
  supplies commit identity, ancestry, `HEAD`, worktree cleanliness, and diff facts;
  native `openspec archive` remains the only archive transition contract; the
  Change 2 [probe evidence](../../../_backlog/plans/policy-gate-injection-layer/05-operation-guidance-probe-evidence.md)
  establishes `missing-boundary` as the required failure posture.
- **Evidence seam:** deterministic isolated Git-repository fixtures exercise a
  valid committed range and every invalid-boundary rejection; structured records
  prove only input binding, Git facts, task-reference shape, and no archive side
  effect.
- **Not in scope:** a semantic evaluator, model-quality score, self-approval,
  fresh-session identity claim, automatic task writer, archive wrapper or blocker,
  full-worktree scan, runtime graph/state/checkpoint behavior, `backend/`, and
  `frontend/`.
- **Triggered review policies:** change-admission, agent-information-map, control-placement

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Selected-change coverage for cross-session closeout evidence | A reviewer may decide what requires further review, but cannot assert semantic clearance through this record | Caller/adapter declares the attestation; Git owns repository, commit, ancestry, HEAD, worktree, and diff facts; the guardrail verifier checks the declared boundary and record shape | advisory | A coverage claim names only a verified committed `base..head`; invalid input yields `missing-boundary` and leaves native archive unchanged | Reuse Git and ordinary `tasks.md` instead of a worktree scanner, archive wrapper, semantic judge, or parallel task ledger | Isolated Git fixtures plus structured-output and no-side-effect assertions |

## Impact

- Adds the `selected-change-closeout-evidence` capability, a bounded
  `openspec/guardrails/` implementation surface, deterministic fixture coverage,
  and governance registrations for those files.
- Modifies the Deep Research Agent Charter route and its requirement evidence so
  `operations.apply/archive.guidance` remains a prompt-delivery layer rather than a
  coordinator or archive gate.
- Adds no provider dependency, user-facing product behavior, runtime route, state
  schema, network service, or change under `backend/` or `frontend/`.
