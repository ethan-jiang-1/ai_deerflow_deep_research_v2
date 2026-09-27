# Design

## Context

See proposal.md — Why. The failing stage is the scenario's launcher block:
scrubbed credential env + empty test `.env` + readiness gate requiring a
credential = the ready-assert can never hold. Everything before that stage
passes on credential-free machines (verified on CI: install, preflight,
`demo --help`, `demo-scripted`, `demo-fixture-graph`, `demo-sessions`,
`profile-check`, `session-workbench` all green before the launcher assert
fails).

## Goals / Non-Goals

**Goals:**

- Make the launcher stage assert the journey the product actually offers a
  credential-free machine: readiness honestly NOT ready, the remediation
  guidance printed, non-zero exit, nothing leaked.
- Keep the lane credential-free and offline — no synthetic credential that a
  real endpoint could ever see.

**Non-Goals:**

- No change to the launcher, the readiness gate, or any product semantics —
  the scenario was wrong, not the product.
- No waiver of the readiness gate for scripted mode (that would weaken what
  the real-mode entry honestly reports).

## Decisions

- **Option B (assert the honest not-ready journey), after Option A was
  measured and rejected.** The first implementation attempt injected bounded
  fake credentials to let readiness pass, on the theory that the launcher's
  engineered default question blocks at HITL1 before the first model call.
  The measured reality (2026-09-28 run): in the launcher's result-return
  mode the auto-policy stage auto-confirms, `topic_planning` makes a REAL
  model call with the fake key against `api.deepseek.com`, and the run ends
  `provider.authentication_failed` (HTTP 401). The fake credential reaches
  the network — so that journey cannot belong to a credential-free offline
  periodic lane, and the ready-then-blocked assertions are unsatisfiable
  without a real endpoint interaction. The honest credential-free journey is
  the not-ready one, and that is what the scenario now pins.
- **What the not-ready journey asserts**: non-zero exit; the readiness report
  says the model configuration is not ready (`尚未找到可用的模型配置`) with
  its next-action guidance; the ready summary (`本地前提检查已就绪`) must be
  ABSENT — the entry does not pretend readiness it does not have; and the
  credential variable names never appear in the output.
- **The bounded claim keeps its meaning**: with no credentials to leak, the
  name-absence assertions verify the launcher does not echo its environment;
  the marker-value check from the rejected attempt is dropped with it.

## Risks / Trade-offs

- The ready-then-blocked launcher journey (with real credentials) is now not
  covered by the periodic lane — it cannot be, offline. If that journey
  needs coverage, it belongs to a credentialed manual lane, recorded here as
  the honest boundary rather than a silent hole.
- The scenario stays slow (the full lane runs the copied-project install);
  it remains in the periodic lane outside the rapid gate, as designed.
