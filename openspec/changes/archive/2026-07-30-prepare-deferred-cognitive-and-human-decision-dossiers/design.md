## Context

HITL2's real handler currently returns its deterministic `proceed` recommendation. Readiness
uses `run_readiness_critic` as a deterministic fallback before materializing a report plan and
selecting its own route. Final delivery formats and publishes from that plan deterministically.
Their reader cards accurately name future responsibilities, but no single review artifact records
the minimum facts required before `introduce-hitl2-human-decision-experience`,
`activate-readiness-evidence-critic-loop`, or `activate-final-report-composition-loop` can activate
behavior.

## Goals / Non-Goals

**Goals:**

- Create a closed, three-record dossier collection that makes the next behavior proposal reviewable.
- Preserve the distinct HITL2 conditional decision and readiness/final accepted deferred roles.
- Prove dossier facts against existing deterministic seams without claiming model quality.

**Non-Goals:**

- No runtime implementation, node reader behavior rewrite, public interface, model dependency, or
  lifecycle change.
- No choice of HITL2 trigger, human-visible actions, model support, tool posture, or final candidate
  schema. Those remain later Scope Card decisions.

## Decisions

### 1. Store dossiers as test-owned non-runtime activation records

The implementation adds a closed record collection in
`agent/tests/assets/deferred_activation_dossiers.py` and its validator plus negative fixtures in
`agent/tests/contract/test_deferred_activation_dossiers.py`. The existing reader-card checker
remains limited to reader-card shape. The focused contract test also scans the production source
root for imports of the test-owned dossier module. Records make the current source fact, future
proposal preconditions, and authority boundary mechanically checkable without adding a production
control plane.

Alternative considered: add fields to graph state or reader cards. Rejected because a dossier is
planning evidence, not run state, and extending runtime state would falsely imply activation.

### 2. Preserve three separate activation contracts

HITL2 records a missing user decision trigger and successor
`introduce-hitl2-human-decision-experience`. Readiness records a future read-only per-question
evidence-sufficiency candidate and successor `activate-readiness-evidence-critic-loop`. Final
delivery records a future report-composition candidate bounded by the readiness plan and successor
`activate-final-report-composition-loop`.

Alternative considered: one generic deferred-agent record. Rejected because it would erase the
conditional-vs-accepted distinction and let a readiness/final contract stand in for a user decision.

### 3. Validate absence claims conservatively

The validator checks exact identity, commitment, required fields, successor, source/proof seams,
and prohibited active-program claims. It does not use absent `run_agent` calls as proof that a role
is unnecessary and it does not certify a later implementation.

Alternative considered: derive dossiers automatically from current source. Rejected because product
commitment and HITL2's unresolved trigger are approved planning facts, not source-inferable facts.

## Risks / Trade-offs

- [Dossiers become a second authority] -> keep them test-owned, link to source/spec owners, and
  validate that they cannot define state, route, or runtime policy.
- [HITL2 is prematurely activated] -> require a missing-trigger disposition and a separate later
  Scope Card before any user-facing or model behavior change.
- [Fallback is mistaken for a permanent product decision] -> require current mechanism and future
  bounded question as separate fields and prove each from different evidence.

## Migration Plan

1. Add failing closed-collection, production-import, and negative-fixture tests.
2. Add the three dossiers and deterministic validator; update the established test-evidence
   registries that select and map their focused contract test.
3. Run focused dossier/card tests and the offline verification target.
4. Roll back by removing the test-owned records and their test-evidence registry entries together;
   no stored data or compatibility migration exists.
