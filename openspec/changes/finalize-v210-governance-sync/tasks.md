# Tasks

## 1. Governance ledger alignment

- [x] 1.1 Update `[upstream_gitlink].commit` in `openspec/governance/project-structure.toml` to `ceebf97fc31afbbfe2aadf7c8d82b03c3742d5d7` (submodule 本体不动). Verify: from repo root, `python3 openspec/governance/check_project_architecture.py` exits 0 — this is the red-before-green proof (baseline red: `ERROR [gitlink.index_commit]` recorded in the proposal). ✓ GATE_EXIT=0
- [x] 1.2 Update root `README.md` framework note (框架运行时基座 line) to `ceebf97f`（ethan tip，= 上游 v2.1.0）with a mirror pointer to `CURRENT_DEERFLOW_PIN` in `deep_research_harness/tests/contract/test_deerflow_public_api.py`. Verify: `grep -n "66b9e7f2" README.md` returns nothing and the note's commit equals `git ls-files --stage deerflow` output. ✓ 零命中；gitlink = ceebf97f

## 2. CNI-001 delta apply

- [x] 2.1 Apply the MODIFIED `cognitive-node-interface` delta: replace CNI-001's self-title clause with the `# <node> — <responsibility>` wording in `openspec/specs/cognitive-node-interface/spec.md`, keeping the complete requirement and its scenario verbatim otherwise. Verify: all 11 `deep_research_harness/src/deerflow_deep_research/graph/nodes/*/workflow.md` H1s satisfy the new wording, and from `deep_research_harness/` the node workflow reader-interface contract test passes. ✓ 36/36 passed

## 3. Verification gate

- [x] 3.1 From repo root run `python3 openspec/governance/check_project_gate.py --phase closeout` directly (no pipe); exit code 0 required. ✓ 全部六个 checker exit=0（初跑曾红于 focus.field_missing，已按 checker 解析格式 `- **Field:** value` 重写 Focus Card）
- [x] 3.2 From `deep_research_harness/` run `UV_OFFLINE=1 make verify` directly; exit code 0 required. ✓ exit 0：fast 2707 passed / integration 327 passed + 4 skipped / workflow 35 passed
- [x] 3.3 From repo root run `openspec validate finalize-v210-governance-sync --strict`, `git diff HEAD --check`, and record `git status --porcelain=v1 --untracked-files=all`, `git ls-files --stage deerflow`, `git submodule status deerflow`; exit codes measured directly. ✓ validate strict 通过；diff check 干净；gitlink stage 与 submodule status 均 `ceebf97fc31afbbfe2aadf7c8d82b03c3742d5d7 deerflow (remotes/origin/ethan)`
- [x] 3.4 Run the three governance gate tests (`openspec/tests/governance/`) and confirm they pass with the updated fixture pin. ✓ unittest discover 全过（strict-validation / change-guidance / delta-specs / requirement-reservation），GOV_TESTS_EXIT=0
