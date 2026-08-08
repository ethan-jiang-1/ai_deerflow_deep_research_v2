## Context

See [proposal.md](proposal.md) for the motivation. The approved runtime contracts are
already present: topic planning declares `REQUEST_BUNDLE`, capability resources are
loaded through the shared renderer, and the test-asset checker collects focused lanes.
The executable `test-fast` target retains its own path list, so the current drift is
isolated to assertions plus the two focused-lane declarations that retained pre-slice
expectations.

The test-evidence policy requires the smallest responsible deterministic seam. This
change therefore repairs the four stale observations in place and does not create new
evidence metadata, alter requirement coverage, or make an archived implementation
slice active again.

## Goals / Non-Goals

**Goals:**

- Make the package registry regression match the approved topic-planning capability
  declaration exactly.
- Ensure both fast-lane declarations observe and execute deterministic tests under
  `tests/assets`, without changing marker semantics or any other lane.
- Bind the Wave0/Wave1 worker and repair calibration assertions plus both HITL1
  renderer regressions to the resource actually loaded by the production renderer, preserving
  bounded request and tool-posture assertions.
- Establish focused red-to-green evidence before using the complete offline gate as
  the closeout signal.

**Non-Goals:**

- Changing node capabilities, prompt objectives, capability Markdown, render logic,
  resource loading, deterministic admission, or test-evidence requirements.
- Adding a generic selector abstraction, recataloging unrelated assets, or updating
  historical evidence counts.
- Claiming credentialed live-model quality or starting Wave2 work.

## Decisions

### 1. Preserve exact registry contracts

The topic-planning package regression will name `NodeCapability.REQUEST_BUNDLE` as
its complete declared set, alongside the existing real-factory assertion. This tests
the public node-spec fact rather than weakening the expectation to merely include an
unknown capability.

An open-ended membership assertion was considered and rejected because it would hide
an accidental later capability expansion.

### 2. Align the two existing fast-lane declarations

The focused selection definition will add `tests/assets` to `FAST_PATHS`, and the
existing `test-fast` target will add the same root to its pytest path list. The marker
expression and all other paths remain unchanged. The lane-partition regression proves
selection completeness, while the direct main-spec-source test proves the executable
target runs the newly selected asset. The existing verification-gate contract will
assert the target includes that path; the asset checker remains the collection seam.

Broadening collection to all `tests`, or introducing a new selector abstraction, was
considered and rejected because either would silently alter the fast lane's boundary
or widen this small contract-restoration change.

### 3. Use loaded capability content as the method source

The Wave0/Wave1 worker and repair calibration cases will load their request capability
references through the existing production loader and assert their authority method
against the loaded policy, including its ledger-retaining authority limit and the
highest-risk Wave1 repair baseline non-promotion boundary, not a generic `objective`
string. Their objectives must not reintroduce that method text.
Wave1 source-diagnostic and claim-verifier objective checks remain because those
bounded critic prompts still directly prohibit a ledger update. All branches retain
their existing tool-posture bounds. Both HITL1 renderer regressions will assert their
exact loaded policy bodies occur in the rendered system policy, while the phase-prompt
test retains its base-policy ordering check. Request data remains asserted in the
user-message projection and tool posture remains asserted from the request/rendered
capability.

Checking legacy marker phrases or Python objectives was considered and rejected:
those projections can change while the runtime-loaded method remains correct, and
cannot prove that the renderer received the resource body. Reading files directly
without the production renderer was also rejected because it misses the injection
boundary.

### 4. Stage verification from local contracts to the shared gate

Implementation will first run the seven focused selectors across the five contracts,
the asset checker, and `make test-fast`, then run `UV_OFFLINE=1 make verify`. The
HITL1 hardening selector is expected to be green against the existing renderer; it is
not a production defect disguised as a red-to-green change. Any unrelated failure
will be reported as such and will not be absorbed into this change. The full gate is a
completion check, not evidence that the change modifies all of its covered production
behavior.

## Risks / Trade-offs

- [Selection says fast but the gate does not execute it] -> Update the existing
  `FAST_PATHS` and `test-fast` declarations together, and prove both partition and
  direct asset execution.
- [A selector becomes too broad] -> Limit the path change to `tests/assets`, preserve
  the marker expression, and keep the collector's known-violation tests green.
- [A renderer test obscures its evidence source with stale marker text] -> Retain the
  exact loaded-policy-to-rendered-system assertion in both renderer regressions and
  remove the marker subset.
- [A registry test masks a future capability increase] -> Assert the exact one-member
  capability set.
- [An unrelated full-gate failure expands scope] -> Record it separately; only the
  four approved stale contracts may be edited by this change.

## Migration Plan

1. Capture the three current failing contracts and update both HITL1 renderer
   regressions to their exact-resource proofs before changing the corresponding
   selection/assertion expectations.
2. Make the narrow registry, twin-selector, documentation, and renderer-observation
   edits until focused tests, `UV_OFFLINE=1 make test-assets`, and
   `UV_OFFLINE=1 make test-fast` pass.
3. Run `UV_OFFLINE=1 make verify`, strict OpenSpec validation, and boundary checks.

No data, configuration, interface, or deployment migration is required. A normal
revert restores the previous test observations without affecting Bundle state or
runtime behavior.
