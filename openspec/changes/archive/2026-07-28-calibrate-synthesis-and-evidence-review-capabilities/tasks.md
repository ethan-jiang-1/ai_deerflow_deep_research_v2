## 1. Red Deterministic Acceptance Cases

- [x] 1.1 Add focused failing capability and catalog tests for the four targeted-evidence requests, including exact IDs/resources, the seven exact worker tool names, the closed legacy inventory, requested-versus-runtime posture, and matrix expansion from twelve to sixteen rows.
- [x] 1.2 Add Wave2 real-node/fake-capabilities cases proving assigned-evidence-only synthesis and zero-tool repair non-admission for an unassigned ref, gaps-only draft, or invented finding/gap.
- [x] 1.3 Add targeted worker real-node/fake-capabilities normal and risk cases for exactly one permitted retrieval, gate-gap identity preservation, validator/ledger-only admission, and no-artifact/ledger result after malformed repair.
- [x] 1.4 Add SourceDiagnostic and ClaimVerifier real-node/fake-capabilities cases proving forbidden-tool posture plus propagation of malformed or out-of-scope assigned references before critic materialization and without an artifact write.
- [x] 1.5 Add separate scripted-real-workflow cases for Wave2, targeted worker, and critic bridge paths that assert only call bounds, untrusted-data handling, and deterministic admission or non-admission; critic failure cases assert no new retry, route, or artifact authority.

## 2. Capability Admission And Request Composition

- [x] 2.1 Add four targeted-evidence declarations and package-local Markdown policies for worker, repair, SourceDiagnostic, and ClaimVerifier; bind their production request builders as required capabilities with one required-retrieval and three forbidden-tool postures.
- [x] 2.2 Make the smallest production prompt or validation corrections required by the red Wave2 cases while retaining existing parser, materializer, gate-preview, gate, route, and recovery owners.
- [x] 2.3 Make the smallest targeted worker, repair, or critic request/validation corrections required by the red cases while retaining existing work-unit controller, ledger, critic materializer, route, and recovery owners; do not add a critic retry, terminal, or route layer.
- [x] 2.4 Extend prompt-catalog registrations so Wave2 plus all four targeted cases render their exact local policy composition and requested/runtime tool distinction without resolving live tools.

## 3. Evidence Governance And Review Assets

- [x] 3.1 Register `NAC-007`, `NPC-005`, `WSN-005`, `TEL-005`, and `EVH-016` in the requirement registry and add smallest-sufficient requirement-impact records.
- [x] 3.2 Extend the direct capability matrix from twelve to sixteen rows with independent normal and highest-risk claims for each targeted branch; preserve Wave2 claims and use exact collected selectors at the lowest responsible seam.
- [x] 3.3 Register distinct scripted-real-workflow claims for the Wave2, targeted-worker, and critic bridge paths without asserting live model, source, critic, or research quality.
- [x] 3.4 Regenerate and review `agent/node_prompts/` so all six evidence-evaluation cases expose local capability composition and requested/runtime tool posture.

## 4. Verification And Handoff

- [x] 4.1 Run the focused Wave2, targeted worker/critic, capability/catalog, and evidence-governance tests, then `cd agent && UV_OFFLINE=1 uv run python scripts/check_test_assets.py`.
- [x] 4.2 Run `cd agent && UV_OFFLINE=1 make verify`, `openspec validate calibrate-synthesis-and-evidence-review-capabilities --strict`, and `git diff HEAD --check`; record `git status --porcelain=v1 --untracked-files=all` and confirm `backend/` and `frontend/` remain clean before archive.
