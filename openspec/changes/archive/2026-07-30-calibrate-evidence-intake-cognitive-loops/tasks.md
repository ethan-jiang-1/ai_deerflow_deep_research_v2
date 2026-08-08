## 1. Calibration Contracts And Governance

- [x] 1.1 Register `WAN-008`, `WON-008`, and `EVH-019` in
  `openspec/governance/req-registry.yaml` before running requirement-ID governance;
  preserve their capability ownership and never reuse an existing identifier.
- [x] 1.2 Add failing focused deterministic tests for the six branch-local
  composition/boundary constraints: Wave0's rendered relevant/independent-source
  criterion and proposed-metadata limit (not a source-quality verdict), Wave0
  non-inventive repair, Wave1 baseline-aware provenance, Wave1 non-broadening repair,
  SourceDiagnostic assignment scope, and ClaimVerifier uncertainty/review-only scope.
  For both repair branches, cover the actual subgraph invocation: the same trusted
  assignment and a compact closed validation category are present, while raw
  exceptions and artifact/checkpoint/ledger/review/gate/route data are absent and
  draft/tool observations remain untrusted. Prove the Wave0 repair is entered only
  for its initial parser/typed-structural failure and the Wave1 repair only for its
  initial parser or local semantic-validation failure; a later
  `SubmissionValidationFailure`, its codes, and artifact-validation detail neither
  invoke nor enter either repair, and retain the existing controller terminal/retry
  path. Prove the rendered assignment is only the initial topic/baseline projection,
  never a raw work/attempt/record identity, and cannot be promoted into candidate
  evidence; include a Wave1 baseline-URL injection attempt.
- [x] 1.3 Define a dedicated typed evidence-intake calibration corpus with one normal
  and one highest-risk case for each Wave0/Wave1 branch (twelve cases total), stable
  case/branch identities, trusted assignments, untrusted boundaries, expected
  constraints, criterion ids, rubrics, permitted degradation, nondeterministic
  boundaries, and per-case bounds. Keep it separate from the existing
  intake/planning corpus, `LIVE_CANARIES`, and the `ScenarioCase` registry. Give the
  Wave1 repair highest-risk case a baseline-URL promotion attempt so its rubric can
  distinguish scope/newness guidance from candidate-evidence authority.
- [x] 1.4 Extend or factor the test-only calibration selection helpers so each corpus
  keeps its own fixed denominator while selected cases reuse the typed rubric report
  safely. Extend the report validator's current single-corpus lookup to a closed
  two-corpus resolver with global case-id uniqueness and exact case/branch/criterion
  matching. Prove duplicate/cross-corpus identities, mismatched case/branch/criteria,
  unsupported disposition, sensitive/unbounded rationale, or a missing required
  bound fail closed without changing the evidence-v1 marker or breaking an older
  evidence-v1 archive without a rubric result.
- [x] 1.5 Add a dedicated evidence-intake selected-live runner that reuses only the
  typed rubric/report and preflight primitives. Wave0/Wave1 worker cases SHALL invoke
  their generated request through a real model-and-web bridge after strict model/web
  preflight; repair and critic cases SHALL invoke their generated zero-tool request
  through a real model-only bridge after strict model preflight. Do not reuse the
  zero-tool-only intake/planning execution harness, a fake capability, `LIVE_CANARIES`,
  or a full-pipeline path as judgment-quality evidence. Preserve one outer attempt,
  declared bounded resource observations, and no default execution. Treat request
  tool posture/bounds, successful bridge execution, and the production branch parser
  (plus Wave1 local semantic validation) as hard invariants: failure records a live
  run failure without a rubric result. Build critic requests from a test-owned,
  deterministic accepted-assignment projection only, never a forged record/artifact
  or a full pipeline.
- [x] 1.6 Update only the affected `COGNITIVE_PROGRAM_EVIDENCE` rows
  (`wave0/worker`, `wave0/repair`, `wave1/worker`, `wave1/repair`,
  `wave1/source-diagnostic`, and `wave1/claim-verifier`) and their central
  requirement-evidence claims. Set `JUDGMENT_EVALUATION_REQUIRED` with rationale,
  rubric, and nondeterministic boundary; update worker-to-repair trusted-input and
  feedback-disposition metadata for the bounded assignment/category while omitting
  raw parser and post-candidate validation detail. Do not add a live-result authority
  field to the deterministic evidence ledger.

## 2. Wave0 Source-Intake Calibration

- [x] 2.1 Revise the Wave0 initial capability/prompt composition to make assigned
  topic relevance, independent source selection, untrusted retrieval handling,
  proposed-metadata limits, and honest degradation explicit while retaining the
  existing required retrieval posture and bounded request window.
- [x] 2.2 Revise the Wave0 repair capability/prompt composition and its subgraph
  invocation at the existing initial parser/typed-structural seam to bind the same
  trusted assignment, invalid draft, retained observations, and compact closed
  structural category. Render only the topic projection used by the initial request,
  not raw work/attempt/record identity. Keep only draft/observations in the
  untrusted-data block; omit raw exception strings and
  artifact/checkpoint/ledger/review/gate/route data; preserve zero-tool,
  non-inventive repair and no artifact/ledger/gate/route authority. Assignment/category
  may constrain scope only and cannot seed source metadata, URLs, facts, fetch
  outcomes, or limitations. Do not extend the repair to a post-candidate
  `SubmissionValidationFailure` or expose its codes.
- [x] 2.3 Make focused Wave0 prompt, validator, and real-node fake-capability tests
  pass, including shortfall/degradation, prompt-injection resistance, one-to-three
  request-window posture, wired parser/typed-structural repair feedback,
  invalid-repair non-admission, downstream submission-validation non-entry, and
  unchanged deterministic validator/controller/ledger ownership.

## 3. Wave1 Evidence-Intake And Review Calibration

- [x] 3.1 Revise the Wave1 initial capability/prompt composition to make accepted
  Wave0 baseline exclusion, bounded new-source selection, source/claim provenance,
  counterevidence, and honest open-question uncertainty explicit while retaining the
  existing one-retrieval posture.
- [x] 3.2 Revise the Wave1 repair capability/prompt composition and its subgraph
  invocation at the existing initial parser or local semantic-validation seam so it
  receives only the same trusted assignment, invalid draft, retained observations,
  and compact closed category. Render only the initial topic/baseline projection, not
  raw work/attempt/record identity. Keep only draft/observations untrusted, omit raw
  exception strings and authority-bearing state, and prove it cannot add a source,
  URL, claim, reference, or open question; a baseline URL can constrain newness but
  cannot seed new repair evidence. Do not extend the repair to a
  post-candidate `SubmissionValidationFailure` or expose its codes.
- [x] 3.3 Revise the SourceDiagnostic and ClaimVerifier capability/prompt composition
  to request decision-ready but assignment-bound review classifications and
  uncertainty, while preserving their zero-tool, review-only, no-publication/no-gate
  boundaries.
- [x] 3.4 Make focused Wave1 prompt, review-materializer, gate-projection, and
  real-node fake-capability tests pass, including baseline duplicate exclusion,
  wired parser/local-semantic repair and non-admission, downstream
  submission-validation non-entry, critic identity binding, malformed or
  out-of-assignment critic suppression during missing-review dispatch, and unchanged
  controller/materializer/gate ownership.

## 4. Selected Live Evidence And Test Assets

- [x] 4.1 Implement the separate `requires_llm` evidence-intake calibration
  collection and its twelve cases. Each case shall retain stable identity, exact
  branch tool posture, branch-appropriate real dependency seam and strict credential
  preflight, complete rubric disposition semantics, hard invariants, bounded
  diagnostics, and available cost/latency observations without mutating lifecycle
  state. Require production parser/local-semantic validation and exact branch tool
  posture/bounds before assigning a rubric; a failed hard invariant remains a failed
  live run with no rubric disposition. Critic fixtures may represent only their
  prompt's accepted-assignment projection, never a forged submission/review artifact.
- [x] 4.2 Add focused governance tests proving deterministic selections exclude both
  calibration collections, the two collection denominators and identities remain
  disjoint, tool-bearing/zero-tool preflight and live dependency seams are strict,
  canonical canaries retain their six fixed cases and deadline budget, and fake
  fixtures cannot close a branch judgment-quality claim.
- [x] 4.3 Regenerate the prompt catalog and update only affected requirement impacts,
  evidence assertions, and test-asset governance metadata.

## 5. Verification And Change Evidence

- [x] 5.1 Run the narrow Wave0, Wave1, critic, prompt-catalog, evidence-registry,
  calibration-contract, repair-feedback (including downstream submission-validation
  non-entry), collection-selection, preflight, and canonical-canary tests with
  `cd agent && uv run --extra operations pytest tests/graph/test_wave0_worker.py tests/integration/test_wave0_work_units.py tests/integration/test_wave1_work_units.py tests/unit/test_wave1_critic_prompts.py tests/unit/test_wave1_review.py tests/graph/test_prompt_catalog.py tests/graph/test_cognitive_program_evidence.py tests/graph/test_node_agent_capability_cohort.py tests/unit/test_live_evaluation.py tests/unit/test_evidence_intake_calibration.py -m "not requires_llm"`
  (adjust only for a deliberately renamed new focused test). Record any explicitly
  selected live execution as supplemental rather than an offline prerequisite.
- [x] 5.2 Run `cd agent && UV_OFFLINE=1 make verify`,
  `openspec validate calibrate-evidence-intake-cognitive-loops --strict`,
  `python3 openspec/governance/check_project_reqs.py .`, and `git diff HEAD --check`.
- [x] 5.3 Record `git status --porcelain=v1 --untracked-files=all`, confirm
  `backend/` and `frontend/` remain clean, and reconcile the proposal, design,
  three delta specs, tasks, and the six named branch-ledger rows before declaring the
  implementation complete and requesting archive authority.
