# Stage 3 Baseline And Boundary

> Stage: 3 - Post-Cleanup Read-Only Re-Audit
> Date: 2026-08-13
> Authorization: user instruction to continue the progressive plan after Stage 2 archive
> Status: complete; no Stage 4 authorization is implied

## Authorized Scope

This Stage is a read-only re-audit of current, non-archive authority after the Stage 1
and Stage 2 changes. It may write audit evidence only under
`_backlog/plans/alignment-audit-2026-08-12/`. It does not create an OpenSpec change or
edit current authority.

The following remained outside the authorization:

- application code, tests, registries, manifests, TOML, governance executables, and
  main specs;
- `openspec/config.yaml`, current CONTEXT/ADR/README/Charter authority, and all
  archived changes; and
- the `deerflow/` gitlink and its source. The gitlink was inspected only through Git
  metadata; no DeerFlow source was opened.

## Fresh Baseline

| Fact | Observation |
| --- | --- |
| Repository HEAD | `09a2e3b7525d65e9c0e56d93c20735727be31e04` (`docs: retire stale context concepts`) |
| Root worktree before evidence write | clean (`git status --porcelain=v1 --untracked-files=all` produced no output) |
| Active OpenSpec changes | none (`openspec list --json`) |
| DeerFlow index entry | mode `160000`, commit `66b9e7f21212490cf92fafac137542b9deb06615` |
| DeerFlow submodule status | matches that commit; nested porcelain status empty |
| Initial scoped diff | no diff; `git diff --submodule=short HEAD` and `git diff HEAD --check` were empty/successful |

## Evidence Method

1. Compare the completed C-001..C-011 adjustment records and their archive-local
   re-audits with the current target authorities. A textual hit is classified by its
   actual role; it is not automatically a remaining mismatch.
2. Search current non-archive authority using explicit paths and exclusions. An early
   broad file-list command displayed archive filenames but did not open archive content
   or use it as Stage 3 evidence. Later searches use only current roots.
3. Re-read the current main specs, focused implementation, and deterministic tests for
   A-003, A-004, and A-009. The code is evidence of current behavior, not permission
   to alter required behavior.
4. Run current structural and deterministic gates. Passing results are recorded only
   within the capability each command actually proves.

## Current Verification

| Command | Result | Proof boundary |
| --- | --- | --- |
| `openspec validate --all --strict` | 49 passed, 0 failed | Main-spec structure and OpenSpec validation; not cross-spec semantic compatibility. |
| `openspec doctor --json` | healthy | Local OpenSpec root health. |
| `python3 openspec/governance/check_agent_charter.py` | passed | Charter shape and selected-policy syntax, not whether prose has one semantic answer. |
| `python3 openspec/governance/check_project_req_coverage.py` | passed | Every alive requirement has a deterministic `@impl` reference; not assertion-level semantic equivalence. |
| `cd deep_research_harness && UV_OFFLINE=1 make verify` | passed | Existing deterministic gate. Its asset check reports 2,771 deterministic tests, with fast 2,495, integration 241, and workflow 35 selections; live/credentialed evidence was not run. |
| `git diff HEAD --check` | passed before Stage 3 evidence writes | No baseline whitespace error. |

The current `Makefile` writes JUnit XML only for the fast lane, so the fast report
records 2,495 tests with zero failures, errors, and skips. The integration and workflow
counts above are the gate's selected counts, not fabricated JUnit summaries.

## Boundary Result

Stage 3 found no reason to reopen Stage 1's topology cleanup or modify a frozen path.
It confirmed two unresolved P1 main-spec conflicts, the explicitly deferred gitlink
detector gap, and the already bounded traceability limitation. It also registered a
remaining policy-cardinality wording inconsistency without modifying it. The complete
classification is in `01-c001-c011-before-after-reaudit.md`,
`02-current-authority-conflicts-and-evidence.md`, and
`03-reduced-mismatch-ledger-and-next-gate.md`.
