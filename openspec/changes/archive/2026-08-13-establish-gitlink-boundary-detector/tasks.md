## 1. Apply Admission And Boundary Inventory

- [x] 1.1 Obtain an explicit apply authorization naming
  `establish-gitlink-boundary-detector`; planning completion, the A-002 todo priority,
  and the closed alignment audit do not authorize implementation. The apply agent
  records the date, allowed governance/evidence paths, and the prohibition on reading
  or modifying DeerFlow source.
- [x] 1.2 Re-establish the baseline with repository HEAD, active changes,
  `git status --porcelain=v1 --untracked-files=all`, `git ls-files --stage deerflow`,
  `git submodule status -- deerflow`, `git -C deerflow status --porcelain=v1
  --untracked-files=all`, and `git diff --submodule=short`. Treat this only as
  metadata evidence; stop if the gitlink is unexpected, nested worktree is dirty, or
  an overlapping user change exists. Do not open DeerFlow source.
- [x] 1.3 Apply agent: re-read the proposal, its Control Placement Review,
  `control-placement` and `control-and-recovery` policies, design, `PRS-018` delta,
  current `project-structure` spec/registry/checker, and the existing architecture
  fixtures. Add each actionable collision, missing rejection case, or source-read risk
  as an unchecked ordinary task before edits. Done when the record names the review
  result and every resulting task/defer.

## 2. Red Deterministic Boundary Evidence

- [x] 2.1 Allocate `PRS-018` in `openspec/governance/req-registry.yaml` and register
  its pending requirement/evidence ownership before any production annotation or main
  spec sync. Verify the registry and pending delta with the focused requirement checks.
- [x] 2.2 Add temporary parent/nested Git fixture helpers that create only empty
  local commits and a mode-`160000` root index entry. The helpers must set local fixture
  author identity, use fixed metadata-only Git commands, contain all paths under the
  test temporary directory, and never reference the real `deerflow/` checkout. Preserve
  a separate `--imports-only` fixture path that contains only a valid static lock.
- [x] 2.3 Write bad-boundary red architecture-contract cases: the unimplemented
  detector currently accepts them, so they must initially fail by expecting a closed
  rejection for missing/malformed/extra-key lock, ordinary-directory/symlink boundary,
  missing/non-gitlink/multi-stage root entry, pointer mismatch, nested `HEAD` mismatch,
  metadata-command failure, and each staged, unstaged, deleted, and untracked nested
  dirty condition. Add the matching clean boundary as a green control. Verify the red
  condition with
  `cd deep_research_harness && UV_OFFLINE=1 uv run --extra operations pytest
  tests/contract/test_architecture_governance.py -q`.
- [x] 2.4 Add a red case that stages one matching new gitlink pointer and matching
  registry lock without requiring a parent commit, and a paired mismatch case. This
  proves that the detector accepts only declared intentional-bump state and does not
  infer approval. Add a command-recorder case that asserts only the three fixed
  read-only Git metadata vectors are issued in full mode, while `--imports-only` issues
  none. Verify with the same focused command.
- [x] 2.5 Prevent the existing full-check source-root walk from descending into the
  declared gitlink. The detector's metadata-only boundary prohibits recursive upstream
  traversal even when no source text is read; retain every existing downstream
  structure check and add the gitlink path only to its walk exclusion set.

## 3. Registry And Checker Implementation

- [x] 3.1 Add an exact `[upstream_gitlink]` section to
  `openspec/governance/project-structure.toml` containing only `path = "deerflow"` and
  baseline full `commit = "66b9e7f21212490cf92fafac137542b9deb06615"`; extend manifest
  parsing with an immutable validated boundary record. Reject missing/extra table keys,
  non-normalized or escaping paths, and non-40-lowercase-hex values before Git
  inspection; retain syntax-only parsing for `--imports-only`.
- [x] 3.2 Extend the full `check_project_architecture.py` path with the closed
  metadata-only sequence: non-symlink directory, exactly one sole stage-zero `160000`
  root entry matching the lock, matching nested `HEAD`, then empty nested porcelain
  including untracked paths. Every Git error or malformed output fails closed. Use fixed
  argument vectors and condition-specific redacted diagnostics; `--imports-only` must
  not resolve the boundary or issue Git. Do not run source readers, filesystem walks,
  remote/history/configuration queries, or mutating Git commands.
- [x] 3.3 Update every existing minimal TOML/manifest fixture and live architecture
  contract to declare a valid isolated boundary rather than silently bypassing the new
  field. Preserve present structural/import assertions and the command-line checker
  contract.
- [x] 3.4 Update `project-structure` architecture policy, the smallest sufficient
  requirement-evidence mapping, and the archive-evidence sentence in
  `openspec/config.yaml` to name the registry/checker/test synchronization and its
  metadata-only proof limit. The configuration wording must retain manual observations
  as supplementary scope/diff evidence, not deny the full detector or turn an
  intentional bump procedure into automatic approval or runtime-compatibility claim.
- [x] 3.5 Run focused red-to-green proof:
  `cd deep_research_harness && UV_OFFLINE=1 uv run --extra operations pytest
  tests/contract/test_architecture_governance.py tests/contract/test_live_architecture_contract.py -q`,
  then `python3 openspec/governance/check_project_architecture.py .`.

## 4. Specification Synchronization And Verification

- [x] 4.1 Sync the reviewed `project-structure` delta to its main spec through the
  OpenSpec sync workflow. Verify that `PRS-018` and all four scenarios are present
  without altering unrelated requirements; update any required main-spec source index
  only for the new ID.
- [x] 4.2 Run `openspec validate establish-gitlink-boundary-detector --strict`,
  `openspec validate --all --strict`, `openspec doctor --json`,
  `python3 openspec/governance/check_project_reqs.py .`,
  `python3 openspec/governance/check_project_specs.py .`,
  `python3 openspec/governance/check_project_architecture.py .`,
  `python3 openspec/governance/check_project_req_coverage.py .`, and
  `python3 openspec/governance/check_agent_charter.py .`.
- [x] 4.3 Run `cd deep_research_harness && UV_OFFLINE=1 make verify` and
  `git diff HEAD --check`. Record focused/full results and their proof limits:
  metadata integrity only, not DeerFlow source, runtime, remote, release, or
  compatibility verification.
- [x] 4.4 Confirm `git diff --submodule=short` contains no `deerflow/` pointer change
  for this detector change. If it does, stop: an upstream bump needs its own explicit
  user decision and reviewed change rather than being absorbed here.

## 5. Archive Gate And Closeout

- [x] 5.1 Archive agent: re-read the actual boundary, completed tasks, Control
  Placement Review, focused fixture results, and full verification. Add every actionable
  finding as an unchecked ordinary task; do not archive while any remains. Done when
  the recorded conclusion names the detector's exact metadata-only guarantee and its
  non-goals.
- [x] 5.2 Obtain a separate explicit archive authorization after all relevant tasks,
  sync state, and evidence are reviewable. Planning or apply authorization does not
  authorize archive.
- [x] 5.3 Before archive, recapture root/nested Git metadata using the commands from
  task 1.2; rerun the strict validation, architecture checker, full deterministic gate,
  and `git diff HEAD --check`. Record that these commands observe or check only the
  defined metadata boundary and do not modify DeerFlow.
- [x] 5.4 Archive only through the normal OpenSpec archive workflow after the separate
  authorization. Do not use archive to imply that an upstream bump was authorized or
  that the pinned revision is runtime-compatible.
- [x] 5.5 Re-establish the post-archive active-change/gitlink baseline, update the
  A-002 todo and any successor plan with actual observed side effects, and stop. A-004-T01
  and A-009 remain independent work and must not begin automatically.
