# rerun — Apply a validated rerun scope to research control

> Reader interface only. This file is not a runtime resource or configuration.
> Code, typed contracts, approved specifications, and tests remain the authority.
> Participation mode: deterministic control
> Commitment state: intentional controller exclusion
> Current operating mechanism: source-audited rerun-scope controller
> Primary cognitive/control program surface: validated scope and deterministic reset decision
> Deterministic authority boundary: rerun handler validates scope, writes control state, and returns route
> Current model-branch evidence: audit only; no direct branch observed

## Node Identity

Rerun is a safety controller. It interprets validated scope, not model text or a new
human interaction, before returning to an allowed research phase.

## From Symptoms

Open `node.py` and the typed rerun contract for illegal scope, reset, or route
symptoms; use `tests/unit/test_rerun_real.py` first.

## Three Cross-Module Facts

1. Scope is trusted only after deterministic validation.
2. The controller owns state reset/recovery, not a prompt or capability body.
3. Graph topology consumes the controller's typed route.

## Route Facts

Legal rerun routes return to topic planning or a selected evidence phase; invalid
scope exhausts through the existing deterministic path.

## Evaluation and Verification Order

Run rerun-focused tests before topology tests; do not introduce a model branch to
explain a controller-safety symptom.
