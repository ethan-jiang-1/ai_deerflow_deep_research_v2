## Why

The shared offline verification gate no longer reaches its intended test suite after
the completed direction-loop, HITL1, and Wave0/Wave1 slices changed runtime-loaded
contracts. The topic-planning registry, deterministic lane partition, and Wave0
calibration assertion currently encode superseded assumptions and fail; that generic
calibration assertion also hides the same worker/repair drift in Wave1. A passing
HITL1 renderer check retains superseded marker text alongside its exact-policy
injection assertion, while the fast lane exposes a second HITL1 renderer check that
still positions its assertion on obsolete capability prose. A full
`UV_OFFLINE=1 make verify` therefore cannot yet serve as current deterministic
evidence for the archived slices.

This change restores the gate's ability to observe existing behavior before any
further cognitive-program scope, including Wave2, is admitted.

## What Changes

- Update the topic-planning package/registry regression to accept the existing
  `REQUEST_BUNDLE` node-input declaration.
- Align both `tests/assets/selection.py::FAST_PATHS` and `Makefile`'s `test-fast`
  target so the focused lane collects and executes the deterministic
  direction-loop asset test it already governs.
- Make the Wave0 and Wave1 worker/repair calibration regression inspect the
  runtime-loaded capability resource instead of an objective string that is no longer
  the method owner, while preserving the critic branches' bounded objective checks.
- Replace superseded marker wording in both HITL1 renderer regressions with the exact
  currently loaded resource-body assertion, retaining the base-policy ordering check
  in the phase-prompt seam.
- Keep the testing reference aligned with the restored fast-lane contents, then run
  the seven focused selectors across the five contracts and `UV_OFFLINE=1 make verify`
  as completion evidence. This change repairs test evidence only; it makes no
  production behavior, main-spec, capability-method, or ownership change.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/tests/assets/selection.py` and `deep_research_harness/Makefile::test-fast`, the existing twin declarations of focused fast-lane discovery and execution. `scripts/check_test_assets.py` validates the collection; it does not replace the Make execution target.
- **Question:** Can the shared deterministic gate again collect, execute, and assert the current approved node-input and runtime-resource contracts without changing those contracts, their owners, or the evidence semantics they prove?
- **Necessary adjacent/external contracts:** `domain/node_spec.py` and `graph/nodes/topic_planning/` answer the existing `REQUEST_BUNDLE` declaration; `tests/contract/test_test_lane_selection.py`, `tests/contract/test_verification_gate_contract.py`, `tests/assets/test_main_spec_requirement_sources.py`, and `scripts/check_test_assets.py` answer focused-lane partition, Make-target composition, execution, and collection; the Wave0/Wave1 worker and repair capability resources plus production loader answer the loaded source of method truth, while Wave1's two critic objectives retain their bounded direct prohibitions; the HITL1 capability resources, production loader, renderer, and graph/unit renderer regressions answer exact rendered content and its base-policy order. Each is inspected only to align its regression with the current contract.
- **Evidence seam:** focused registry, lane-partition, direct asset-execution, Wave0 resource, and two HITL1 renderer regressions, followed by the offline full gate. No provider, browser, external API, or live-quality evidence is involved.
- **Not in scope:** production source behavior, public APIs, capability Markdown content, test-evidence semantics, main specs, requirement registry, evaluation corpus content, test-lane redesign, Wave1 or Wave2 ownership, live credentials, `backend/`, and `frontend/`.
- **Triggered review policies:** none: this change repairs stale deterministic observations and collection only; it does not move a candidate, human judgment, control fact, admission/recovery boundary, node-agent role, or lifecycle output.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. This change uses `skip_specs: true` because it restores test selection and
assertions for already approved behavior without modifying a normative requirement.

## Impact

Affected files are confined to the focused-lane declarations in
`deep_research_harness/`, their direct test/documentation projections, and the five
focused regressions. The release-quality conclusion will be limited to a restored
deterministic gate; the previously noted live cognitive evidence remains separate and
unclaimed.
