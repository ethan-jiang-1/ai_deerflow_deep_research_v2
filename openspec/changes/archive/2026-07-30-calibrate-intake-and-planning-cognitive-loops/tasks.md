## 1. Calibration Fixtures And Contracts

- [x] 1.1 Register `HIN-012`, `TOP-007`, and `EVH-018` in `openspec/governance/req-registry.yaml` before running requirement-ID governance; retain their capability ownership and never reuse an existing identifier.
- [x] 1.2 Add failing focused deterministic tests for the six branch-local calibration constraints: conservative profile proposal, ambiguous semantic reply, bounded repair, profile-faithful planning, degraded planning, and invalid-plan repair.
- [x] 1.3 Define the dedicated typed calibration corpus with one normal and one highest-risk case for each of the four HITL1 and two topic-planning branches (twelve cases total), including stable case/branch identities, expected candidate constraints, criterion ids, rubrics, permitted degradation, and nondeterministic boundaries. Keep it outside `LIVE_CANARIES` and the `ScenarioCase` registry.
- [x] 1.4 Add failing test-only live-report compatibility tests for a typed rubric result and for reading an evidence-v1 archive report that lacks it; retain bounded redaction and do not change the evidence-v1 marker.
- [x] 1.5 Extend the existing cognitive-program rows with `JUDGMENT_EVALUATION_REQUIRED`, rationale, rubric, and nondeterministic boundary only; update central requirement-evidence escalation separately, without inventing a live-claim field on `CognitiveProgramEvidenceRow`.

## 2. HITL1 Policy Calibration

- [x] 2.1 Revise the profile-brief initial and repair capability/prompt composition to make conservative, decision-ready profile criteria explicit while retaining the existing closed schema, zero-tool posture, and repair bound.
- [x] 2.2 Revise the semantic-intake initial and repair capability/prompt composition to distinguish confirmation, full constrained revision, proposal question, and clarification while keeping replies untrusted and preserving the existing resolver authority.
- [x] 2.3 Make the HITL1 focused deterministic tests pass and verify that neither initial nor repair candidates can publish a profile, action, checkpoint field, or route without the existing deterministic/human path.

## 3. Topic-Planning Policy Calibration

- [x] 3.1 Revise the initial and repair topic-planning capability/prompt composition to make confirmed-profile fidelity, explicit must-answer coverage, distinct scope, bounded single-topic behavior, and degraded-profile conservatism explicit.
- [x] 3.2 Keep repair inputs limited to the same confirmed profile, invalid draft, and compact validation facts; prove that policy changes cannot introduce retrieval, sources, requirements, identifiers, topic state, or route authority.
- [x] 3.3 Make the planner/materializer-focused deterministic tests pass, including profile constraints, coverage/overlap rejection, one-repair exhaustion, and non-publication on an invalid candidate.

## 4. Live Calibration And Evidence Governance

- [x] 4.1 Extend the test-only live-report contract so new calibration reports carry the typed rubric result and pre-rubric evidence-v1 archive reports parse with no result. Prove malformed, sensitive, mismatched case/branch, incomplete criterion set, unsupported disposition, or unbounded rubric fields fail closed in focused contract tests.
- [x] 4.2 Implement the separate `requires_llm` collection with its twelve calibration cases. Each case must retain stable case/branch identity, strict model-credential preflight, the stated typed rubric disposition semantics and complete criterion ids, hard invariants, existing branch call limits plus declared outer attempt/model/tool/token/timeout bounds, bounded diagnostics, and available run-cost/latency observations; it must not alter `LIVE_CANARIES`.
- [x] 4.3 Add focused governance tests proving default deterministic selections exclude the calibration collection, selected calibration runs retain strict credential preflight, the canonical six-canary count/identities/deadline budget remain unchanged, the reusable scenario registry remains unchanged, and deterministic fixtures cannot close a branch judgment-quality claim.
- [x] 4.4 Regenerate the prompt catalog and update only the affected evidence assertions, requirement impacts, and test-asset governance metadata.

## 5. Verification And Change Evidence

- [x] 5.1 Run the narrow HITL1, topic-planning, prompt-catalog, evidence-registry, live-report compatibility, calibration-collection, canonical-canary, and live-selection tests; record any live execution as supplemental evidence rather than a prerequisite for offline verification.
- [x] 5.2 Run `cd agent && UV_OFFLINE=1 make verify`, `openspec validate calibrate-intake-and-planning-cognitive-loops --strict`, `python3 openspec/governance/check_project_reqs.py .`, and `git diff HEAD --check`.
- [x] 5.3 Record `git status --porcelain=v1 --untracked-files=all`, confirm `backend/` and `frontend/` are clean, and reconcile the proposal, design, specs, tasks, and 18-branch plan ledger before requesting archive authority.
