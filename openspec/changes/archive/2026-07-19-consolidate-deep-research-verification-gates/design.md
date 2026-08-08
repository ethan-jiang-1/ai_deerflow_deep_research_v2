## Context

The repository already has strong deterministic test governance, but its final composition is duplicated. `agent/Makefile` exposes `lock-check`, `lint`, `test-assets`, `test-req-coverage`, `test-fast`, `test-integration`, and `test-workflow` separately and has no `verify` or root-governance target. `make test` is deliberately only the exact pytest-selection union of the three focused lanes; it is not the complete verification command because it omits lock, lint, asset, requirement, and root-governance checks. The integration lane already contains `test_demo_tui.py` and invokes `uv run --extra operations --extra demo-tui`, but current `make install` prepares only `operations`; therefore its documented setup does not currently prepare a deterministic verifier for offline execution. `agent-tests.yml`, `agent-release-e2e.yml`, and the archive guidance in `openspec/config.yaml` maintain different subsets. The release workflow currently uses the broad `make test` aggregate while the PR workflow spells out the three focused lanes.

`check_project_req_coverage.py` currently parses test docstrings and proves that every declared alive requirement has deterministic test-side ownership. It does not inspect production-source ownership annotations. There are currently 86 Python source files under `agent/src/` containing `@impl`, so a typo or a reference to a retired ID can remain unnoticed. The tracked seven-line `req-registry.yaml.tmp` is not an authority and has drifted from `req-registry.yaml`.

The current stakeholder and execution environment are one developer on one local machine. Existing workflow files are retained as future-compatible declarations, but hosted CI operation is neither assumed nor required. The change is governance-only: it affects no graph, runtime, checkpoint, sandbox, model, tool, or release behavior.

## Goals / Non-Goals

**Goals:**

- Establish one zero-credential local command, `cd agent && make verify`, as the complete deterministic verification command and deterministic portion of the OpenSpec archive gate.
- Keep the exact gate composition mechanically reviewable and protected by focused local contract tests.
- Make existing workflow definitions delegate to the same target without making remote execution a completion condition.
- Reject unknown and retired production-source `@impl` references while preserving existing test-side coverage semantics.
- Remove the stale temporary registry and retain one canonical requirement registry.

**Non-Goals:**

- No hosted runner, GitHub repository setting, branch protection, required check, secret, team approval, release automation, or other multi-contributor process is created or required.
- No doctor, configure, infrastructure probe, Postgres, live-model, release-E2E, or network-dependent command enters `make verify`.
- No new test framework, line-coverage target, `GATES.md`, shell runner, or second requirement/evidence catalog is introduced.
- No runtime configuration, dependency, graph node, typed state/checkpoint, node-agent role, sandbox artifact, public entry surface, or mount changes.
- No files under `backend/` or `frontend/` are modified.

## Decisions

### 1. `agent/Makefile` owns the executable composition

`make install` will first become the canonical deterministic setup command: it SHALL run `uv sync --locked --extra operations --extra demo-tui`. `demo-tui` is an existing locked optional dependency, not a new runtime dependency; it is necessary because the already-selected integration lane imports Textual. `--locked` prevents setup from silently regenerating `uv.lock` before the verifier's lock check. This setup happens before verification and is intentionally not a `verify` prerequisite. `verify` SHALL use an exported target-specific `UV_NO_SYNC := 1` value inherited by every prerequisite recipe, so each existing `uv run` (including the subprocesses started by `test-assets`) refuses implicit synchronization; an unprepared environment therefore fails rather than downloading, resolving, or mutating the environment during verification.

Add `.PHONY` thin targets. `governance` is a fail-fast, ordered recipe that runs exactly these commands from `agent/`, each with `..` as the repository-root argument:

```make
python3 ../openspec/governance/check_project_reqs.py ..
python3 ../openspec/governance/check_project_specs.py ..
python3 ../openspec/governance/check_project_architecture.py ..
```

`verify` has no recipe, declares the inherited `export UV_NO_SYNC := 1` guard above its prerequisites, and its prerequisites are exactly:

1. `governance`
2. `lock-check`
3. `lint`
4. `test-assets`
5. `test-req-coverage`
6. `test-fast`
7. `test-integration`
8. `test-workflow`

These are the existing zero-credential gates. `test-integration` already owns integration, blocking-I/O, SQLite viability, durability coverage, and the locked `demo-tui` integration cases, so its narrower convenience targets are not repeated. The target does not include `test`, because the three focused deterministic selections already form the governed complete aggregate; `make test` remains that narrower test-only selector union for developers who need only pytest selection. It also does not include `format`, because verification must not rewrite the checkout; `lint` already checks formatting. After `make install` or matching CI setup has prepared both extras, `UV_OFFLINE=1 make verify` is the acceptance path: its inherited no-sync guard prevents provisioning or environment mutation, and it introduces no model call, credential, live/release/Postgres selection, or network test.

Alternative considered: introduce `run_gates.sh` or document a copied command list. Rejected because either creates another composition authority. Alternative considered: make a quick gate the archive default. Rejected because the project is deliberately using one full local verification before archive to compensate for the absence of required hosted CI.

### 2. Local execution is authoritative; workflows are declarative consumers

`openspec/config.yaml` will name only `cd agent && UV_OFFLINE=1 make verify` for its hard **deterministic verification** command, rather than copy its components. Its finalization block will separately require strict `openspec validate <change-name> --strict`, `git diff HEAD --check` (covering staged or unstaged changes), and recorded applicable boundary/config/doctor/infra-probe evidence; it will not pretend that a no-argument Make target can validate an arbitrary change name or repeat the three checker commands. The `jobs.deterministic` job in each of the two existing workflow files will prepare the same extras through `uv sync --locked --extra operations --extra demo-tui`, then invoke the same target once as `UV_OFFLINE=1 make verify`. `agent-tests.yml` will add `.github/workflows/agent-release-e2e.yml` to both existing PR/push path filters, so a standalone release-workflow edit selects the contract that verifies it. This is the only trigger adjustment: the release workflow's triggers, release-acceptance job, secrets, and artifact-upload definitions remain unchanged.

Local contract tests will inspect the archive-guidance block, both PR/push path-filter lists, and scoped `jobs.deterministic` commands—not workflow-wide substrings—so archive guidance and both deterministic job definitions must delegate once through `UV_OFFLINE=1 make verify`, the release-workflow path cannot evade the existing contract, and no component gate command list remains; `make test-release-e2e` remains legal in the separate release-acceptance job. They will also assert the exact Makefile composition, inherited exported no-sync guard, and exact root-relative governance commands, so removing a gate, allowing implicit environment synchronization, or reintroducing a divergent command list fails locally. `agent/README.md` and the human-authored command/cadence text in `agent/AGENTS.md` will identify `make verify` as the canonical complete verification target and its offline invocation while retaining the documented meaning of `make test`. Actual GitHub Actions execution is not evidence for this change, and no remote setup task exists.

Alternative considered: leave the workflow files unchanged until hosted CI is enabled. Rejected because they already exist and would preserve a known stale command list. Declarative alignment is cheap and does not require operating remote infrastructure.

### 3. Production `@impl` discovery is syntax-aware and registry-backed

Extend the zero-external-dependency requirement checker to inspect only the canonical production root `agent/src/**/*.py`. Use Python AST for module, class, synchronous-function, and async-function docstrings and `tokenize` comment tokens for inline or standalone comments; do not scan arbitrary string literals, docs, generated reports, tests, or archived artifacts. Reuse the existing `@impl` payload/range parsing semantics only after discovery, so a string literal that merely contains annotation-shaped text cannot become ownership.

Parse the canonical registry with the same top-level-entry and `[DEPRECATED]` semantics used by `check_project_reqs.py`, rather than treating comments or other YAML-like text as assignments. A production annotation fails with its ID, repository-relative source path, and line when available when the ID is unknown or retired. Source decoding, AST, or tokenization errors likewise fail closed with an actionable relative location. Source annotations remain optional ownership markers: no requirement is added that every alive ID appear in production source, and they do not substitute for collected test evidence.

Focused temporary-root tests will cover a valid source ID, unknown source ID, retired source ID, module/class/synchronous-function/async-function docstrings, inline and standalone comment discovery, ignored ordinary strings, source decoding/error-path failure, diagnostic path reporting, and the unchanged uncovered-test behavior. Because source discovery could falsely pass on an empty or mis-scoped scan, one detector smoke test will place a known invalid annotation in the canonical source subtree and prove it is found. That smoke test proves discovery scope; it does not turn optional production annotations into a non-empty-source requirement.

Alternative considered: regex the complete source text. Rejected because examples or ordinary string constants could be mistaken for ownership annotations. Alternative considered: move this rule into `check_test_assets.py`. Rejected because registry validity and alive-requirement coverage already belong to `check_project_req_coverage.py`.

### 4. One registry remains authoritative

Delete tracked `openspec/governance/req-registry.yaml.tmp`; do not migrate or merge its contents. `req-registry.yaml` remains the sole append-only registry. The named temporary path is forbidden as a repository artifact, so a focused contract can fail if a second catalog is silently revived. Final validation proves working-tree absence and the expected deletion with `git diff HEAD`; it deliberately does not require staging merely to make `git ls-files` forget an index entry.

### 5. Boundary evidence starts from a recorded worktree baseline

Before the red phase, record `git status --porcelain=v1 --untracked-files=all` for the whole worktree and separately for `backend/` and `frontend/`. Existing non-overlapping entries outside the protected paths are user-owned baseline, not evidence created by this change; if one overlaps an owned implementation path, stop for direction rather than overwrite or normalize it. A nonempty baseline under `backend/` or `frontend/` is instead a precondition failure for this change's strict boundary proof: obtain direction or use a clean worktree before applying, because a status-only comparison cannot prove that an already-modified protected file was left untouched. At final validation, both protected-path porcelain status and `git diff HEAD -- backend frontend` must be empty. This supplements rather than replaces `git diff HEAD --check`: `git diff` detects whitespace in tracked deltas but cannot see a newly untracked protected file.

All OpenSpec and Git path checks in this change run from the repository root. `cd agent && …` is a scoped Make invocation only; subsequent root-relative `backend`, `frontend`, `agent/uv.lock`, and `openspec/` pathspecs must not be issued while the shell remains under `agent/`, where Git would silently reinterpret them as `agent/<path>`.

## Risks / Trade-offs

- **[Risk] Full local verification increases archive time.** -> Run it once as the deterministic archive gate; credentialed, networked, Postgres, and release lanes remain excluded.
- **[Risk] A single workflow step has coarser future hosted-CI log grouping.** -> Make prints each invoked command and failing target; hosted execution ergonomics can be revisited when remote CI becomes an actual operating surface.
- **[Risk] Source scanning could accept an accidentally empty tree.** -> Add a canonical-path detector smoke test with a known invalid annotation, plus parse-error reporting.
- **[Risk] Makefile/workflow contract tests can become brittle.** -> Assert only the owned composition and delegation contract, not unrelated formatting or action versions.
- **[Risk] `make verify` could be mistaken for the pytest-only aggregate.** -> Preserve `make test`, state its narrower selector role in the Makefile contract and docs, and reserve `make verify` for the canonical complete deterministic gate.
- **[Risk] A local environment may be absent.** -> Keep installation/setup outside the target, state the lock-derived-environment precondition, and keep the target free of live/network test members.
- **[Risk] `uv run` can silently synchronize an unprepared environment.** -> Export `UV_NO_SYNC=1` from `verify` to every prerequisite recipe and assert that propagation in the Makefile contract; the verifier then fails rather than mutating its environment.
- **[Risk] Setup can omit a selected extra or rewrite the lock.** -> Sync the existing locked `demo-tui` extra alongside `operations` with `uv sync --locked`, assert that exact local/CI setup contract, and run the final verifier with `UV_OFFLINE=1`.
- **[Risk] A release-workflow-only edit can evade its contract.** -> Include the release workflow path in the existing agent-tests PR/push filters and assert both lists locally; do not alter the release workflow's own triggers.
- **[Risk] `git diff` cannot see untracked protected files or distinguish prior user edits.** -> Record a porcelain-v1 status baseline before work, compare protected paths against it at the end, and preserve non-overlapping user changes.
- **[Trade-off] Workflow files change before they are operationally relied on.** -> This prevents known drift at low cost, while remote success remains explicitly outside acceptance.

## Migration Plan

0. Record the worktree/protected-path baseline. Stop for direction if it overlaps an owned implementation path or either protected upstream path is nonempty; otherwise preserve unrelated user-owned entries.
1. Add failing focused tests for the exact deterministic setup/Makefile/workflow delegation, root-relative governance invocation, source `@impl` validation/error reporting, and temporary-registry absence.
2. Implement `governance`/`verify` and the checker extension; keep all existing focused lane semantics unchanged.
3. Align the OpenSpec archive guidance and existing workflow definitions, then delete the stale temporary registry.
4. Run focused tests, strict change validation, and final boundary/diff checks, then execute `cd agent && make install && UV_OFFLINE=1 make verify` locally as the final deterministic acceptance gate.

Rollback is a normal source revert: there is no data migration, runtime state, remote repository setting, or deployed infrastructure to undo.

## Open Questions

None. Remote CI operation and multi-contributor policy are deliberately deferred to a future change if the project reaches that stage.
