## 1. Acceptance Transcript Baseline

- [x] 1.1 Run the focused existing HITL1 semantic tests and evidence-contract tests;
  record their deterministic baseline before changing the lifecycle suite.
- [x] 1.2 Add a red direct complete-proposal-presentation test and a scripted
  real-node/fake-capabilities multi-visit acceptance test that cover natural
  confirmation and a full source-constrained revision followed by later confirmation.
  Replace the existing context-`action_ids` assertion with one proving complete-
  proposal context omits both JSON instruction and duplicated `accept_suggestion`,
  while `HumanInputRequest.action_ids` and the visible control remain present; also
  assert correlated requests, zero-tool semantic calls, proposal versions, the
  first-party-source/citation constraints in the visible interaction subject, and no
  profile write before graph-owned acceptance. (`HIN-011`, `HIC-004`)
- [x] 1.3 Add a red scripted real-node/fake-capabilities test covering a bounded
  proposal question, ambiguity/clarification, and exhausted semantic failure. Assert
  proposal/control preservation, no consumed answer/rejection round for question or
  ambiguity, no profile write on failure, and that the node-generated fallback has no
  raw candidate JSON, schema/JSON, or hidden-action-token instruction. Treat scripted
  question/clarification text as candidate-routing evidence, not live quality proof.
  (`HIN-011`, `HIC-004`)

## 2. Focused Lifecycle Correction

- [x] 2.1 Run the red transcript tests; inspect the HITL1 node and domain interaction
  contract to isolate any additional causal gap beyond the confirmed complete-proposal
  context leak, without widening to graph topology, checkpoint schema, adapter, API,
  provider, or prompt-resource changes.
- [x] 2.2 Replace the confirmed complete-proposal JSON instruction and duplicated
  `accept_suggestion` context value with bounded ordinary confirmation/revision/question
  guidance. Preserve `HumanInputRequest.action_ids` and `InteractionProjection.controls`,
  then implement any other demonstrated HITL1/domain correction only when necessary for
  the transcripts. Preserve the existing zero-tool posture, three-call semantic bound,
  cancellation propagation, and graph-owned candidate admission. (`HIN-011`, `HIC-004`)
- [x] 2.3 Run the focused lifecycle tests green and verify that complete-proposal
  presentation and node-generated semantic-failure fallback retain no raw candidate
  JSON, schema/JSON instruction, or hidden action token; verify separately that
  scripted question/ambiguity candidates preserve the proposal/control without making
  a live language-quality claim. (`HIN-011`, `HIC-004`)

## 3. Evidence Registration And Verification

- [x] 3.1 Add two unique central `TestEvidenceClaim` entries: one for the successful
  confirmation/revision/question/ambiguity lifecycle and one for exhausted semantic
  fallback; bind both to their distinct collected selectors and deterministic
  real-node/fake-capabilities authenticity. (`EVH-014`)
- [x] 3.2 Update only the required requirement-impact/evidence assets and add or
  adjust direct contract tests and `@impl` ownership markers so duplicate selectors,
  aggregate substitutions, missing post-sync requirement coverage, or a live-model-
  quality claim cannot validate the lifecycle evidence. (`EVH-014`)
- [x] 3.3 Run focused checks: `cd agent && UV_OFFLINE=1 uv run pytest
  tests/graph/test_hitl1_node.py tests/contract/test_evidence_claim_contract.py` and
  the narrow test-asset/evidence checker targets selected by the changed assets.
- [x] 3.4 Run the required final gates: `cd agent && UV_OFFLINE=1 make verify`;
  `openspec validate harden-hitl1-profile-interaction-lifecycle --strict`;
  `python3 openspec/governance/check_project_reqs.py .`;
  `python3 openspec/governance/check_project_specs.py .`;
  `python3 openspec/governance/check_project_architecture.py .`;
  `python3 openspec/governance/check_agent_charter.py .`; and `git diff HEAD --check`.
- [x] 3.5 Record `git status --porcelain=v1 --untracked-files=all`, confirm
  `backend/` and `frontend/` remain clean, and review the completed OpenSpec task
  checklist before archive.
