## 1. Immutable Plan And Final Gate Boundaries

> Implementation status (2026-07-30): started. The active work is the readiness
> persistence seam and final-delivery gate boundary; checkboxes remain unchecked until
> their focused tests pass.

- [x] 1.1 Add failing deterministic readiness/store tests proving that the admitted
  `ReadinessReportPlan` is written at its canonical `ContentRef` path, reads back with
  an exact hash match, and never yields a fabricated ref after persistence failure.
- [x] 1.2 Add failing final-delivery/gate tests for contained/hash-matched plan reads,
  no model or publisher call on absent/divergent plans, fresh current-attempt gate-view
  validation that cannot reuse prior `report_refs`, publisher-returned artifact
  re-reads/hash and fixed-shape checks, real final-artifact checks, accepted-evidence
  no-publication checks, gate-owned completion, and the existing
  repair/evidence-blocked/exhausted routes.
- [x] 1.3 Implement the bounded immutable report-plan persistence/read seam through the
  appropriate controller/store protocol without changing readiness judgment/admission
  ownership. Add the non-checkpointed `FinalDeliveryGateView` wrapper consumption and
  validation, replace the fixture-only real final gate with its deterministic checks,
  and make the gate's final-delivery `pass` projection, rather than the node result,
  write the completed terminal facts.

## 2. Final Composer Contract And Admission

- [x] 2.1 Add failing deterministic tests in `agent/tests/unit/test_final_delivery_real.py`
  for bounded readiness/evidence projection, typed layout-candidate cardinality and
  complete-permutation schema, exact plan-text/backing-submission-reference rendering,
  mandatory-uncertainty preservation, no publication on rejected output, and no raw
  rejected output in state. Run
  `cd agent && UV_OFFLINE=1 uv run --extra operations pytest tests/unit/test_final_delivery_real.py`.
- [x] 2.2 Add final-delivery typed projection, closed layout candidate, parser,
  evaluator, deterministic renderer, and fresh final-attempt gate-view seams. Retain
  only admitted bounded result material for publication; keep report refs, terminal
  facts, gate results, and routes outside the candidate, and make only a verified gate
  pass write completion.
- [x] 2.3 Add the narrow `FinalDeliveryBundleStoreProtocol`, its
  `FINAL_DELIVERY_BUNDLE` node capability, and invocation/dependency injection alongside
  the existing publication bundle. The protocol must support only bounded plan/evidence
  reads and post-publication contained/hash-checked artifact reads, while the existing
  work-unit store implements it without exposing work-unit control. Make direct factory
  and graph-wrapper injection fail before request construction when either dependency is
  absent; update focused node-package and capability-injection tests.

## 3. Bounded Node-Agent Integration

- [x] 3.1 Add a package-local final composer capability and source-faithful request
  builder with a forbidden-tool posture, bounded assignment, and delimited untrusted
  evidence projection. Add red/green local resource and request-composition tests.
- [x] 3.2 Add a final-delivery-specific one-invocation zero-tool `ExecutionPolicy` and
  runtime resolver bridge. Prove it is selected for a runnable real-final recipe and
  cannot inherit readiness or upstream policy/tool posture.
- [x] 3.3 Replace only real formatter composition with one `run_agent` layout-order
  invocation, deterministic candidate admission/rendering, and fresh-view gate
  evaluation before terminal completion. Preserve full-fake behavior, final gate
  topology, publisher idempotence/conflict behavior, and graph lifecycle ownership.
- [x] 3.4 Project bridge, policy, timeout, malformed-output, unsupported-candidate, and
  publisher/read-back failure through the existing deterministic
  repair/evidence-blocked/terminal owners without a model retry, model publication, a
  publisher overwrite, or a new route. Add focused regression tests for each failure
  class.

## 4. Catalog, Evidence, And Evaluation

- [x] 4.1 Add the stable `final-delivery/composer` prompt catalog case and generated
  `agent/node_prompts/` projection. Extend prompt-catalog freshness and rendering
  tests to prove no runtime/model/evidence access occurs.
- [x] 4.2 Add the twentieth capability/cohort/cognitive-program evidence row and its
  distinct normal/highest-risk deterministic claims. Update requirement registry and
  requirement-impact mappings for FID, NAC, NPC, NOA, CPE, and EVH requirements.
- [x] 4.3 Add a scripted real-bridge workflow test proving the exact zero-tool policy,
  final rendered request, candidate parser/evaluator, publisher handoff, and gate owner
  execute in order with external model adapters replaced.
- [x] 4.4 Add a bounded labeled final-composition evaluation corpus for layout quality
  and exact conclusion, uncertainty, and citation-map preservation. Keep credentialed
  execution explicitly selected and preflighted; classify its result separately from
  deterministic conformance and do not claim source truth or research quality.
- [x] 4.5 Update `final_delivery/workflow.md` as a factual reader projection after the
  implementation, preserving its non-authority boundary and pointing symptoms to the
  new candidate/admission/gate seams.

## 5. Verification And Closure

- [x] 5.1 Run focused readiness/store, final-delivery/gate, capability-injection/runtime-resolver,
  prompt-catalog, scripted-bridge, final-gate/mixed-graph, and evaluation-asset tests.
- [x] 5.2 Run `cd agent && UV_OFFLINE=1 make verify` before archive.
- [x] 5.3 Run `openspec validate activate-final-report-composition-loop --strict` and
  `git diff HEAD --check`; record `git status --porcelain=v1 --untracked-files=all`
  and confirm `backend/` and `frontend/` remain clean before requesting archive
  authorization.
