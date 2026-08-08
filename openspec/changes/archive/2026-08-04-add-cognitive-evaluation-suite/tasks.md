## 1. Contracts And Governance

- [x] 1.1 Before implementation evidence refers to the new requirements, register CES-001 through CES-007 and PRS-015 in `openspec/governance/req-registry.yaml`, confirm the active deltas remain their pending owners, and run `python3 openspec/governance/check_project_reqs.py .`. @impl PRS-015
- [x] 1.2 Add red deterministic tests for registered Case admission, closed execution inputs, two-state execution status, Case/control identity, and rejection of free-form prompt/path/model/resume overrides. @impl CES-001
- [x] 1.3 Add the governed `deerflow_deep_research.runtime.evaluation` package and typed contracts for Case identity, execution status, Observation Trace, Bundle manifest, and Review Record; keep the package inside the existing source-layer import rules. @impl CES-001, CES-003, CES-005, PRS-015
- [x] 1.4 Add source-controlled `deerflow_research/evals/control/` declarations for the Case registry, Case-linked Rubrics, review protocol, schemas, and V1 HITL1/Wave0 identities; do not create a generated run workspace in the change. @impl CES-001, CES-007
- [x] 1.5 Update the project-structure delta's exact path inventory and preserve `backend/` and `frontend/` as protected clean boundaries. @impl PRS-015
- [x] 1.6 Add `deerflow_research/evals/runs/` to the module ignore contract and update `openspec/governance/project-structure.toml`, architecture-checker fixtures, and the generated `deerflow_research/AGENTS.md` locator; prove a clean checkout neither requires nor creates run output. @impl PRS-015

## 2. One-Shot Runner And Bundle

- [x] 2.1 Add failing isolation tests for fresh execution identities, concurrent/repeated Case invocations, no checkpoint/artifact namespace reuse, and explicit rejection of resume state. @impl CES-002
- [x] 2.2 Implement the Runner workspace allocator and one-shot lifecycle: validate Case, preflight required services, invoke one declared production subject, return only `completed` or `failed`, and never invoke review, retry, or resume. @impl CES-001, CES-002, CES-006
- [x] 2.3 Add observation capture for declared inputs, branch/phase events, logs, tool/model metadata, outputs, artifacts, resource use, cancellation, timeout, and typed diagnostics without capturing hidden chain-of-thought or inventing a quality result. @impl CES-003
- [x] 2.4 Implement atomic Bundle finalization with manifest/control identity, content references/digests, failure-phase reason, and immutable evidence; preserve partial observations on failure and reject incomplete publication as reviewable success. Expose one read-only Bundle-integrity verifier that reloads the manifest, checks every required record/digest, and returns the exact retained Case/Contract/Rubric/Protocol identities for review admission. @impl CES-003
- [x] 2.5 Add focused tests for provider/tool/bridge failure, malformed output, timeout, cancellation, partial observation retention, atomic publication, immutable Bundle references, altered/missing evidence and stale-control rejection before review, and the absence of hidden Runner retries. @impl CES-002, CES-003, CES-006
- [x] 2.6 Extract or wrap only the narrow existing preflight, identity, model/web adapter, and production branch interfaces needed by the Runner; leave existing `tests/scenarios` and `evaluation-hardening` selectors semantically unchanged. @impl CES-002, CES-007

## 3. Human-Initiated Review

- [x] 3.1 Add the versioned Evaluation Review Protocol and explicit review-operation input contract; require a person or approved human-controlled interface to select a retained Bundle and never let the Runner auto-start review. @impl CES-004
- [x] 3.2 Add red tests proving review input is read-only, verifies the retained Bundle manifest/content digests and exact control identities, cannot rerun execution or mutate production/Bundle state, and can be deferred without creating a Review Record. @impl CES-004
- [x] 3.3 Implement separate immutable Review Record storage beside (not inside) the Bundle, including Bundle digest, Case/control/Contract/Rubric/Protocol versions that exactly match the retained manifest, evaluator identity/time, four-state result, evidence, confidence, unknowns, owning seam, and follow-up. @impl CES-005
- [x] 3.4 Add validation tests for multiple reviews of one Bundle, missing or substituted provenance, Bundle integrity/immutability, independent execution/review statuses, and strict handling of `pass`, `limited`, `inconclusive`, and `failed`. @impl CES-005, CES-006
- [x] 3.5 Provide a thin operator/Coding-Agent handoff adapter for explicit `run` and `review` operations that returns stable references and bounded diagnostics without becoming a graph node, Python quality judge, auto-fixer, or scheduler. @impl CES-004, CES-005

## 4. V1 Node Smoke Cases

- [x] 4.1 Add the HITL1 brief Case and deterministic direct-branch contract tests; invoke the real production HITL1 bridge/parser/admission boundary, preserve its no-tool and call/timeout policy, and emit a Bundle without claiming whole-flow or Research Outcome quality. @impl CES-007
- [x] 4.2 Add the Wave0 worker Case and deterministic direct-branch contract tests; invoke the real production Wave0 bridge/tool policy/validator/controller boundary, require strict model/web preflight for selected live execution, and emit a Bundle without admitting evidence in the Runner. @impl CES-007
- [x] 4.3 Add bounded selected-live smoke entrypoints and report wiring for the two Cases only; keep them manually selected, one outer Runner execution each, and outside routine pytest/CI collection. @impl CES-002, CES-006, CES-007
- [x] 4.4 Add operator documentation under `deerflow_research/` showing the correct working directory, explicit Case invocation, Bundle inspection, and separate human review flow; distinguish execution failure from cognitive result and state that inspection never resumes execution. @impl CES-004, CES-006

## 5. Review And Verification Closeout

- [x] 5.1 **Plan-review obligation (control-placement):** the current apply agent (`root`) reviews the proposal, both delta specs, design, and tasks against the Control Placement Review table, confirms Case/Runner/Review/structure ownership and non-bypassable boundaries, and records any correction as an ordinary unchecked task before implementation. Done when the review has no untracked actionable finding and the focused deterministic contract list is explicit. @impl DRC-010
- [x] 5.1a Keep V1 node selection at the caller-to-runtime boundary: `runtime.evaluation` receives an already selected registered `NODE_SPEC` through its generic adapter and MUST NOT import `graph.nodes.*`; rerun architecture and direct-adapter tests. @impl DRC-010, PRS-015
- [x] 5.1b Materialize only established structured production state-update values into Bundle JSON; reject unknown opaque values and prove the real Wave0 controller output remains inspectable. @impl CES-003, DRC-010
- [x] 5.1c Keep the typed Review Record contract congruent with immutable stored review evidence, provenance, confidence, uncertainty, owning seam, and follow-up. @impl CES-005, DRC-010
- [x] 5.1d Synchronize the existing local-profile `.gitignore` contract fixture with the registered ignored `evals/runs/` workspace. @impl PRS-015, DRC-010
- [x] 5.2 Apply every actionable plan-review correction, then rerun the affected focused contract tests before marking the implementation tasks complete. @impl DRC-010
- [x] 5.3 Run focused Runner/Bundle/Review/architecture tests, `cd deerflow_research && UV_OFFLINE=1 make verify`, `openspec validate add-cognitive-evaluation-suite --strict`, and `git diff HEAD --check`; record `git status --porcelain=v1 --untracked-files=all`, confirm `backend/` and `frontend/` remain clean, and run a real smoke Case only when its explicit prerequisites are available. @impl CES-001..CES-007, PRS-015
- [x] 5.4 **Archive-closeout review obligation (control-placement):** the archive agent (`root`) reviews the actual implementation boundary, Bundle/Review evidence, unresolved tasks, and deterministic results against the same table; corrects or adds ordinary tasks for any mismatch before archive. Done when strict validation, focused evidence, and the final boundary/status record all describe the same change and no required task remains unchecked. @impl DRC-010
