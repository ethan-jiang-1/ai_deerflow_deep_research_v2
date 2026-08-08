## Context

The existing full-real selector is a single pytest file in `tests/e2e/`, selected by a
dedicated marker expression, Make target, GitHub workflow, and active evidence claim.
It invokes the test-only release adapter in `tests/scenarios/release.py`. Recent
authorized attempts ended at `first_resume:blocked`; the later one took 510.70 seconds.
The adapter also supplies active deterministic Bundle-authority control-plane tests and
the release preflight, so its ownership cannot be inferred from the E2E selector's
current unsuitability. See `proposal.md` for the motivation and the EVH-024 diagnosis
issue for the recorded observations.

## Goals / Non-Goals

**Goals:**

- Preserve the full-real selector and its scenario definition for future diagnosis.
- Make ordinary collection and every active execution path unable to select it.
- Preserve the deterministic public-entry and Bundle-authority assertions that remain
  reliable and useful.
- Leave one concise, local pointer from the retained file to the diagnostic owner and
  its reactivation condition.

**Non-Goals:**

- Repairing the model, provider, source-set, or graph behavior observed by EVH-024.
- Running the credentialed selector, declaring it successful, or creating a replacement
  release lane.
- Changing runtime lifecycle/state behavior, Bundle semantics, credentials, or any
  upstream `backend/` or `frontend/` surface.

## Decisions

### Move only the selector into a non-default-discoverable retained surface

The full-real pytest selector will move to
`tests/scenarios_suspended/evh_024_release_acceptance.py`. It remains executable only
through a future deliberate reactivation change, while the `evh_` filename stays outside
pytest's default `test_*.py` and `*_test.py` discovery patterns. A concise README in
that directory will point to
`_backlog/plans/evh-024-release-acceptance-diagnosis.md`; the backlog issue remains the
single diagnostic and reactivation authority.

`tests/scenarios/release.py` remains active. It is a support adapter, not the expensive
selector: deterministic control-plane cases and the preflight use it today. Moving the
whole module would make the suspension overbroad and discard valid low-cost evidence.

Alternative considered: leave the file under `tests/e2e/` and rely only on markers.
That would preserve accidental direct collection and communicates that the path is an
active E2E surface. A physical suspended directory makes the retained-but-inactive
status visible and mechanically testable.

### Remove the active release-evidence category as one consistency unit

The Make target, release workflow, release-focused selection constants, focused release
selection enum, release-acceptance evidence class, full-real evidence claim, and the
`EVH-005` requirement-evidence policy entry will be removed or revised together with
the moved selector. The existing asset checker requires a focused collection for every
active selection enum value, so leaving an empty release enum member would retain a
false control plane rather than eliminate an execution surface. Any one remaining
entry point could still spend credentials or imply current acceptance, so a marker-only
change is insufficient.

`AuthenticityLevel.FULL_REAL_PIPELINE` and the registered `release_e2e` marker remain
as provenance for the retained scenario. They are not an active selection or evidence
category; the marker remains a defense-in-depth exclusion if the retained source is
later incorrectly renamed or placed. The deterministic Bundle-authority control-plane
registry entries, tests, and `scripts/release_preflight.py` remain because they do not
select the full-real run. Command-specific tests that presently require the removed
Make target or workflow will instead assert their absence. The versioned release
attestation also remains a deterministic historical-record contract, not active proof
that the suspended selector currently passes.

Alternative considered: retain a manual Make target or workflow as a convenience. This
would contradict suspension and make re-execution easier than the required diagnosis
loop and authorization review.

Alternative considered: retain an empty focused release-lane enum and evidence class.
The checker currently treats every enum value as an active collection obligation, so an
empty member would preserve a misleading release control surface and require special
cases. Removing the inactive category is smaller and makes reactivation an explicit
future change.

### Treat reactivation as a future behavior change, not an ad-hoc command

The retained README states the exact issue and the less-than-ten-second deterministic
diagnostic-loop precondition. It does not describe an execution command. A later
OpenSpec change must decide whether and how an executable release lane returns, update
the corresponding evidence metadata, and separately obtain authorization for any
credentialed run.

## Risks / Trade-offs

- [A retained file becomes invisible and stale] -> The dedicated directory and README
  preserve its provenance, while collection and asset-contract tests make its inactive
  state explicit.
- [Removing the release path is mistaken for removing Bundle evidence] -> Retain and
  exercise `tests/scenarios/release.py` through the existing deterministic
  control-plane tests.
- [A contributor recreates an executable path informally] -> The OpenSpec delta and
  focused contracts remove the active category and require a new approved reactivation
  change plus the diagnostic precondition.
- [A user mistakes historic full-real material for current evidence] -> Remove the
  active evidence claim and replace contributor guidance with the suspended status.

## Migration Plan

1. Add focused red collection and asset-contract coverage for the retained inactive
   surface, including removal of the active release-evidence category and full-real
   `EVH-005` policy requirement.
2. Move the selector, add the local pointer, and remove every active selection and
   evidence entry point in one implementation change.
3. Run focused deterministic tests and the normal deterministic verification gate;
   never run the credentialed selector as part of this migration.

Rollback is a source-control revert that restores the same selector, lane, workflow,
and evidence claim as a consistent set. It does not authorize a real execution.
