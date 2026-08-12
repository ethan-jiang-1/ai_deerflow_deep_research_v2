## 1. Reconfirm The Bounded Baseline

- [x] 1.1 Record the apply-time HEAD, `openspec list --json`,
  `git status --porcelain=v1 --untracked-files=all`, `git ls-files --stage deerflow`,
  `git submodule status -- deerflow`, and `git -C deerflow status --porcelain=v1
  --untracked-files=all`; stop if another active change or an overlapping user edit
  makes the documentation boundary ambiguous. This last command inspects Git worktree
  metadata only, not DeerFlow source.
- [x] 1.2 Reclassify each active non-archive `backend`/`frontend` occurrence before
  editing: C-001 root-mirror claims are targets; valid `deerflow/backend/...` paths,
  domain terms, host-interface terms, and legacy-root negative guards are retained.
  Save the path, term, and classification in the C-001 Adjustment Record; exclude
  archives, lockfile entries, and `deerflow/` content by the stated change boundary.
- [x] 1.3 Confirm the target list is limited to `openspec/config.yaml`,
  `deep_research_harness/AGENTS.md`, `openspec/agent-charter/charter.md`, and
  `deep_research_harness/README.md`; confirm no code, test, governance executable,
  manifest/TOML, registry, generated inventory, archive, or `deerflow/` source/worktree
  edit is planned.

## 2. Correct The Current Topology And Closeout Language

- [x] 2.1 Apply C-001 atomically: replace only the stale root-mirror descriptions in
  `openspec/config.yaml`, `deep_research_harness/AGENTS.md`, and
  `openspec/agent-charter/charter.md` with the verified `deep_research_harness/`
  downstream and `deerflow/` gitlink boundary; state that ordinary work does not modify
  or source-browse DeerFlow.
- [x] 2.2 Apply C-002 in `openspec/config.yaml`: replace proposal/archive instructions
  that protect nonexistent root upstream directories with required manual gitlink
  scope/diff evidence and its explicit proof limits; retain A-002 as
  `DEFERRED-CODE-CHANGE` and do not add a detector claim.
- [x] 2.3 Inspect the scoped diff for the three C-001/C-002 files; verify one coherent
  topology answer, preserve valid legacy-root guards, and stop if the needed wording
  requires a runtime, governance-executable, or main-spec change.

## 3. Correct The Editable Harness Documentation

- [x] 3.1 Apply C-003 only in `deep_research_harness/README.md`: replace the invalid
  sibling path with `../deerflow/backend/packages/harness` while preserving the stated
  repository-root command context.
- [x] 3.2 Compare the README command with `deep_research_harness/pyproject.toml` and the
  lockfile; record agreement without editing dependency metadata or adding another
  installation route.
- [x] 3.3 Apply V-001 only to
  `deep_research_harness/tests/contract/test_selected_change_closeout.py`: use the
  configured Ruff formatter's exact adjacent-literal rewrite; inspect the one-file diff
  and run the focused test to prove unchanged closeout-guardrail behavior. Stop if the
  formatter proposes any other file or semantic edit.

## 4. Verify And Record The Bounded Result

- [x] 4.1 From the repository root, run `openspec validate
  retire-v1-topology-residue --strict`, `openspec doctor --json`,
  `python3 openspec/governance/check_agent_charter.py .`, and `git diff --check`; then
  separately run `cd deep_research_harness && UV_OFFLINE=1 make verify`. Manually inspect
  changed Markdown links in the four target documents. Stop and report any failure
  without changing code or tests to obtain green output. On 2026-08-13, the exact
  `make verify` invocation reached its integration stage before its tool-session output
  handle was lost; its Makefile-equivalent targets then passed with recorded JUnit
  evidence: fast 2495, integration/blocking-I/O 241 (4 skips), workflow 35.
- [x] 4.2 Re-run the Git metadata evidence from task 1.1 and review
  `git diff --submodule=short` plus repository status. Record precisely that the evidence
  establishes the observed gitlink boundary and scoped diff, not automatic protection of
  the gitlink pointer or nested worktree.
- [x] 4.3 Write separate C-001, C-002, and C-003 Adjustment Records under
  `_backlog/plans/alignment-audit-2026-08-12/`, each with Before/After, risk, possible
  side effects, controls, verification bounds, observed side effects, and remaining
  mismatch owner.
- [x] 4.4 Perform an independent human plan/diff review against `proposal.md` and
  `design.md`; confirm that A-002 remains deferred, all retained active
  `backend`/`frontend` occurrences have semantic classifications, and no frozen path
  changed. User accepted this review conclusion and explicitly authorized archive on
  2026-08-13; the reviewed boundary includes only C-001/C-002/C-003 and V-001.
- [x] 4.5 Obtain separate authorization before applying these tasks or archiving the
  change; after archive, stop and perform the Stage 1 local re-audit before requesting
  Stage 2 authorization. Apply was separately authorized on 2026-08-12; archive remains
  unauthorized and requires a new authorization after all verification tasks pass.
