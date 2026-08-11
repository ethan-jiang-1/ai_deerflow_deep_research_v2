## 1. Restore Requirement Ownership

- [x] 1.1 Run `check_project_reqs.py` and `check_project_req_coverage.py` before editing and confirm their failures are limited to `EVH-030`, `WAN-011`, `WAN-012`, `WON-011`, `WON-012`, and `WOU-012` ownership; compare each current tagged requirement block with its archived `2026-08-11-stabilize-evidence-worker-output-envelopes` delta.
- [x] 1.2 Add the six existing IDs only to their four owning main-spec `> req:` headers, verifying each ID already tags the matched requirement block in that same spec.

## 2. Verify The Green Baseline

- [x] 2.1 From `deep_research_harness/`, run `make governance` and `make test-req-coverage`; confirm requirement ownership, coverage, main-spec structure, project structure, and Agent Charter governance pass.
- [x] 2.2 Run `cd deep_research_harness && UV_OFFLINE=1 make verify`, `openspec validate repair-requirement-ownership-baseline --strict`, and `git diff --check`; record any unrelated pre-existing failure without expanding scope.
- [x] 2.3 Inspect `git status --porcelain=v1 --untracked-files=all` and a scoped diff of the four main specs. Confirm this change adds only its planning artifacts and the four header edits, preserves any unrelated existing worktree modifications, and leaves `deerflow/` untouched.
