## 1. Readiness Critic Contract

- [x] 1.1 Add red unit tests for bounded evidence projection, exact question-set and
  accepted-reference candidate validation, duplicate/unknown/missing verdict rejection,
  retained-field/cardinality bounds, exclusion of rejected and unused critic-only output
  from checkpoint state, conservative model-failure projection, and integrity-invalid
  store-read structural exhaustion without a model call. Update the readiness
  fixture to provide a scripted work-unit store that returns ledger-shaped synthesis
  evidence. Run `cd agent && UV_OFFLINE=1 uv run --extra operations pytest tests/unit/test_readiness_real.py`.
- [x] 1.2 Add the readiness-local zero-tool capability resource and request builder;
  construct its model-visible evidence projection only from the validated ledger/store
  seam and bounded checkpointed questions.
- [x] 1.3 Declare readiness's `WORK_UNIT_CONTROLLER` capability; make the direct real
  factory reject a missing controller with `work_unit_capability_missing`; and add the
  existing graph-wrapper injection/fail-before-factory coverage for readiness. Update
  the existing node-package and topology capability assertions to include readiness.
- [x] 1.4 Add the readiness-specific zero-tool `ExecutionPolicy` and bridge assembly
  in the existing per-node runtime resolver. Prove a real-readiness recipe resolves
  that bridge rather than an upstream default, with no new topology or public API.
- [x] 1.5 Replace the real all-ready fallback with one `NodeExecutionCapabilities`
  request and deterministic `ReadinessCriticOutput` admission. Permit only supplied
  questions and projection-backed refs, build the checkpoint summary only from the
  bounded materializer-consumed per-question projection, and preserve full-fake fixture
  behavior, hard-rule precedence, materializer ownership, and node-owned routes.
- [x] 1.6 Project bridge, policy, and malformed-output failure to conservative
  `blocked_repair_required` verdicts without adding a local retry or a new route; map
  accepted-evidence read/integrity failure to the existing structural `exhausted`
  branch before a model request.

## 2. Evidence And Evaluation

- [x] 2.1 Add a scripted real-bridge conformance test proving the readiness capability
  is zero-tool, bounded, and reaches the existing materializer/route owner; add direct
  provider/policy/structured-output failure regressions and a pre-invocation
  accepted-evidence reader-failure regression.
- [x] 2.2 Add bounded labeled answerability evaluation assets for supported,
  insufficient, and repair-required cases. Classify deterministic conformance and
  credentialed live judgment results separately; do not execute live evaluation unless
  separately selected and preflighted.
- [x] 2.3 Update requirement registry/evidence ownership for `EVH-021` and the
  readiness activation claims, with collected deterministic test references.

## 3. Verification And Closure

- [x] 3.1 Run the focused readiness unit, capability-injection/runtime-resolver,
  scripted-bridge, graph-route, and evaluation asset checks after the implementation
  tests are in place. At minimum run `cd agent && UV_OFFLINE=1 uv run --extra operations
  pytest tests/unit/test_readiness_real.py tests/unit/test_work_unit_capabilities.py
  tests/unit/test_research_runtime_capabilities.py tests/contract/test_research_node_packages.py
  tests/graph/test_topology_and_implementation.py`.
- [x] 3.2 Run `cd agent && UV_OFFLINE=1 make verify` before archive.
- [x] 3.3 Run `openspec validate activate-readiness-evidence-critic-loop --strict` and
  `git diff HEAD --check`; record `git status --porcelain=v1 --untracked-files=all`
  and confirm `backend/` and `frontend/` remain clean before requesting archive authorization.
