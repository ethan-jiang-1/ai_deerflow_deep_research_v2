## 1. Admission And Red Evidence

- [x] 1.1 Apply agent: review the `control-placement` record against the current
  Makefile target graph, confirm `make install`, `profile-setup`, entry preflight,
  and `make lock-check` have one non-overlapping owner each, and correct the
  proposal/design before implementation if a target can bypass the boundary. Done
  when the focused review names the deterministic owner and evidence seam for every
  changed decision.
  Review conclusion: `install` is the sole downstream synchronizer, `profile-setup`
  retains root setup then delegates to it, the shared entry preflight is the only
  local-demo readiness evaluator, and `lock-check` alone evaluates lock freshness.
  The supported entry set includes fake/real CLI and TUI, fixture graph, retained
  observation, the workbench, and the documented launcher; clean-copy process and
  concurrency tests observe their real command boundary. No proposal/design correction
  is required before implementation.
- [x] 1.2 Add red command-contract tests in
  `tests/contract/test_demo_commands.py`, `tests/contract/test_local_profiles.py`, and
  `tests/contract/test_verification_gate_contract.py`, and
  `tests/contract/test_agent_pr_workflow.py` for the complete install extra set,
  recursive profile setup, foreign-`VIRTUAL_ENV` clearing, explicit no-sync runner,
  documented direct-launcher preflight, a CI `make install` bootstrap, and
  independently retained `make lock-check` / offline verify composition. Run the
  focused contract selection and record the expected failures before changing the
  Makefile, launcher, or workflow.
  Red baseline: the focused selection failed because the Makefile has no shared
  `--locked --no-sync` runner or complete install extras, `profile-setup` still syncs
  operations directly, the launcher has no entry preflight, and CI bootstraps with a
  partial direct `uv sync`.
- [x] 1.3 Add a red clean-copy subprocess regression for a missing/incomplete
  project `.venv`, then for a prepared copy, in
  `tests/integration/test_local_entry_environment.py`. It must prove the failure stops
  before an adapter starts and names only `make install`; after setup it must snapshot
  `uv.lock` and `.venv` around credential-free help, full-fake, fixture-graph,
  retained inspection, bounded profile/workbench, and direct-launcher
  missing-credential commands. Every child process must clear `DEEPSEEK_API_KEY`,
  `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, and `TAVILY_API_KEY`; the isolated launcher
  case writes an empty test-owned `.env` before its state snapshot and asserts the
  bounded missing-credential outcome. Add the two-process read-only/help smoke to the
  same focused deterministic seam and record its red baseline.
  Red baseline: a missing copied `.venv` let `make demo-scripted DEMO_ARGS=--help`
  install 200 packages and return success; after the old partial `make install`,
  `make entry-preflight` did not exist.

## 2. Explicit Setup And Ordinary Runner

- [x] 2.1 Review `pyproject.toml` optional dependencies and run
  `cd deep_research_harness && uv lock --check`. Refresh `uv.lock` only if that
  reviewed metadata requires it; otherwise retain the passing tracked lock unchanged
  and record that no historical lock failure is being claimed as current.
  Reviewed `operations` (`python-dotenv`, `ruamel.yaml`), `demo-tui` (`textual`), and
  `demo-real` (`tavily-python`); `uv lock --check` passes, so no lockfile refresh or
  historical lock failure is claimed.
- [x] 2.2 Implement the shared Makefile entry preflight using only the prepared
  project environment's local metadata. It must detect a missing `.venv` or any
  required `operations`, `demo-tui`, or `demo-real` distribution before Python adapter
  execution, perform no lock/sync work, and emit the bounded `make install` action.
- [x] 2.3 Make `install` clear foreign `VIRTUAL_ENV` and run one locked sync with
  `operations`, `demo-tui`, and `demo-real`. Change `profile-setup` to invoke the
  unchanged root setup first and then this complete downstream setup, without editing
  DeerFlow or changing ordinary profile command semantics.
- [x] 2.4 Route ordinary Makefile demo, inspection, and workbench entry commands
  through the shared foreign-env clearing, `--locked --no-sync` runner and preflight.
  Update `run/real-research.sh` to invoke that preflight and then execute its existing
  quoted question with the same no-sync behavior. Preserve each entry's current direct
  extras, `.env` loading, fixture-only `PYTHONPATH`, arguments, credential
  requirements, full-fake versus fixture-graph composition, and allowed ignored run
  or diagnostic outputs. Keep setup and `lock-check` as the only intentional
  exceptions in this entry surface.
- [x] 2.5 Update concise local setup/operation documentation and the static command
  contracts, then change `.github/workflows/agent-tests.yml` to invoke `make install`
  as its one online environment bootstrap before the unchanged offline gate. Register
  the clean-copy public-entry claim in `tests/assets/evidence.py` and the corresponding
  `DPL-005`, `DPL-006`, and `LCP-002` impacts in
  `tests/assets/requirement_evidence.py`. The updates must state and prove the complete
  `make install` setup, retain `make lock-check` as a separate freshness gate, and
  never promise that no-sync validates a lock.
  `ENTRY_RUN` and `PROFILE_RUN` also set `PYTHONDONTWRITEBYTECODE=1`, because the
  clean-copy process test exposed otherwise-valid Python imports writing `.pyc` files
  inside `.venv`; this preserves the declared no-mutation contract without adding a
  second setup owner.

## 3. Deterministic Verification

- [x] 3.1 Turn the focused command and clean-copy regressions green. Verify the
  prepared-copy commands preserve the lock digest and `.venv` snapshot while allowing
  only their explicitly exercised ignored outputs; verify missing extras fail before
  adapter output and overlapping help/read-only commands do not contend over setup.
- [x] 3.2 Run `cd deep_research_harness && uv lock --check`, the focused command,
  profile, and local-entry process suites, then `UV_OFFLINE=1 make verify`. Run
  `openspec validate stabilize-local-entry-environment --strict`,
  `openspec validate --specs`, and `git diff HEAD --check`.

## 4. Closeout

- [x] 4.1 Apply agent: perform the archive-closeout `control-placement` review.
  Confirm ordinary commands have no setup/lock authority, the preflight's only legal
  recovery is `make install`, and `lock-check` alone makes a freshness claim; correct
  any divergent target or evidence before closeout. Done when focused clean-copy and
  concurrency evidence prove those owners at the real Make command boundary.
  Closeout conclusion: dry-run target composition and the clean-copy subprocess tests
  show that every supported entry first calls the shared local-metadata preflight, then
  uses a foreign-env-clearing locked no-sync runner. `install` remains the only
  downstream synchronizer, `profile-setup` only delegates after the unchanged root
  setup, and `lock-check` alone invokes `uv lock --check`; no divergent control path
  or unsupported recovery action remains.
- [x] 4.2 Sync the accepted `demo-pipeline` and `local-configuration-profiles` deltas
  into main specs, archive the completed change, update
  `_backlog/plans/cli-tui-entry-integrity-repair_plan.md` with commands, evidence,
  archive path, and commit, then record `git status --porcelain=v1 --untracked-files=all`
  with `deerflow/`, `backend/`, and `frontend/` clean.
