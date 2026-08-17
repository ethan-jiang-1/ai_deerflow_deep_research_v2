# Portability Candidate Source Proof

Status: verified portable snapshot for this Change.

The fixed identity is recorded in `portability-candidate.json`. Because the working
tree is dirty, `sourceRevision` supplies repository provenance while each SHA-256
identifies the exact candidate bytes.

## Negative Controls

- A manifest containing `openspec/change-guidance/local/routes.md` is rejected as denylisted.
- A one-file content mutation after manifest creation is rejected by digest mismatch.
- A portable Markdown link leaving the selected allowlist is rejected.
- Removing, demoting, or reordering the node-agent route anchors is rejected; the restored seven-decision route passes.
- Retired guidance trees, duplicate members, stale product paths, extra product members, and Harness-to-OpenSpec references are rejected.

These controls are exercised by `test_portable_change_guidance_export.py`,
`test_change_guidance_governance.py`, and `check_harness_dependency_direction.py`.

## Source Verification

- `deep_research_harness/.venv/bin/python -m pytest openspec/tests/governance -q` — 353 passed.
- `python3 openspec/governance/check_harness_dependency_direction.py` — passed.
- `python3 openspec/governance/check_change_guidance.py` — passed.
- `python3 openspec/governance/check_project_reqs.py` — 424 registered, 0 orphan.
- `python3 openspec/governance/check_project_specs.py` — 50 main specs, 0 violations.
- `python3 openspec/governance/check_project_architecture.py` — passed.
- `python3 openspec/governance/check_project_req_coverage.py` — passed.
- `openspec validate make-openspec-practice-portable --strict` — valid.
- `cd deep_research_harness && UV_OFFLINE=1 make verify` — 2499 fast, 252 integration, and 35 workflow tests passed; 4 environment-dependent tests skipped.
- `python3 openspec/governance/portable_change_guidance_export.py openspec/changes/make-openspec-practice-portable/evidence/portability-candidate.json` — candidate verified.
- `git diff --check` — passed.

## Boundary

This evidence proves the source snapshot's neutrality, exact contents, and current
repository integration. It does not claim automatic upgrades, package compatibility,
or facts about any future adopting product.
