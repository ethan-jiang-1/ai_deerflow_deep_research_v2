## 1. Admission Contract Tests

- [x] 1.1 Extend the isolated charter-governance fixture with the `node-agent-workflow-integrity` policy and a complete Node Agent Review record, then add red cases for a missing review, wrong header, incomplete cell, unsupported classification, and simultaneous workflow-outcome review. (`DRC-008`)
- [x] 1.2 Mark the focused charter contract test as deterministic evidence for `DRC-008` without adding a runtime or live-evaluation claim. (`DRC-008`)

## 2. Charter Route And Authoring Boundary

- [x] 2.1 Add the `node-agent-workflow-integrity` policy with its concrete trigger, four owner roles, bounded-review questions, and explicit non-authority boundary; route it from the charter index. (`DRC-008`)
- [x] 2.2 Extend the concise OpenSpec authoring route so selected node-agent changes require the Node Agent Review and so neither OpenSpec configuration nor root runtime configuration becomes node-role or runtime-permission authority. (`DRC-008`)

## 3. Mechanical Admission Gate

- [x] 3.1 Extend the charter checker with the canonical policy name and Node Agent Review table validation: exactly one heading, exact eight-column header and separator, one or more complete rows, and closed `node-agent`/`no-agent` classification. (`DRC-008`)
- [x] 3.2 Preserve independent enforcement when both the Node Agent Review and Workflow Outcome Review policies are selected; do not add source scanning or semantic inference. (`DRC-008`)

## 4. Requirement And Change-Train Registration

- [x] 4.1 Register `DRC-008` in the append-only requirement registry and keep the pending charter delta, policy, checker, and deterministic test aligned. (`DRC-008`)
- [x] 4.2 Update the agentic-workflow governance plan to identify this accepted admission change and the subsequent `establish-node-agent-capabilities` implementation change without claiming runtime behavior from governance prose. (`DRC-008`)

## 5. Verification And Handoff

- [x] 5.1 Run the focused charter contract test and direct checker, including the repository's active proposals, then fix any change-local conformance issue. (`DRC-008`)
- [x] 5.2 Run `cd agent && UV_OFFLINE=1 make verify`, `openspec validate define-node-agent-workflow-governance --strict`, and `git diff HEAD --check`; record `git status --porcelain=v1 --untracked-files=all` and confirm `backend/` and `frontend/` remain clean.
  Completed 2026-07-27: strict OpenSpec validation and `git diff HEAD --check`
  passed. `UV_OFFLINE=1 make verify` passed with 1,857 fast tests, 153 integration
  tests (four expected Gateway-stack skips), and 16 workflow tests. The pre-record
  status was empty; no untracked files, `backend/`, or `frontend/` changes were
  present.
