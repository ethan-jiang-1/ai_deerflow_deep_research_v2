# A-002 Implementation And Verification

> Change: `establish-gitlink-boundary-detector`
> Date: 2026-08-13
> Status: **IMPLEMENTATION VERIFIED - ARCHIVE/COMMIT NOT AUTHORIZED**

## Delivered Change

| Surface | Actual adjustment | Risk and side-effect control |
| --- | --- | --- |
| `project-structure.toml` | Adds `PRS-018` and the exact two-key `[upstream_gitlink]` lock: `deerflow` at `66b9e7f21212490cf92fafac137542b9deb06615`. | A future bump fails until its staged root pointer, lock, nested `HEAD`, and clean nested state agree. This check does not approve the bump. |
| Architecture checker | Adds immutable lock parsing, path/commit validation, a metadata-only gitlink evaluator, and exclusion of the declared gitlink from the pre-existing root walk. | The evaluator uses only `lstat` plus fixed read-only `git ls-files --stage -z`, `git rev-parse --verify HEAD`, and `git status --porcelain=v1 --untracked-files=all` vectors. There is no source walk, source read, remote/history query, or mutating/recovery command. |
| Contract evidence | Adds hermetic empty parent/nested Git fixtures for malformed lock, path/index/HEAD mismatches, command failure, malformed output, all nested dirty classes, a staged matching bump, `--imports-only`, command vectors, and no-upstream-walk behavior. | Tests never refer to the real `deerflow/` checkout. Existing import-only fixtures declare a static lock and assert no metadata command is issued. |
| Requirement authority | Registers `PRS-018`, maps it to the live architecture contract, synchronizes the active delta to the `project-structure` main spec, and documents the metadata-only proof limit. | The requirement expressly excludes DeerFlow source, runtime, remote, release, and compatibility claims. |
| Archive authoring guidance | Narrows `openspec/config.yaml`: manual Git observations remain supplementary scope/diff evidence, while full architecture governance is the automatic metadata detector. | This removes the old contradiction without claiming that either evidence path authorizes a bump or proves compatibility. |

## Red-To-Green Evidence

Before the checker implementation, the focused suite failed in exactly the intended
way: 16 malformed, moved, or dirty gitlink cases were accepted by the old checker.
After implementation and two additional closed-condition cases, the focused set passed:

```text
UV_OFFLINE=1 uv run --extra operations pytest \
  tests/contract/test_architecture_governance.py \
  tests/contract/test_import_boundaries.py \
  tests/contract/test_live_architecture_contract.py -q
92 passed
```

## Verification

| Check | Result | Limit |
| --- | --- | --- |
| `openspec validate establish-gitlink-boundary-detector --strict` | Passed | Validates change artifacts, not runtime compatibility. |
| `openspec validate --all --strict` | 50 passed, 0 failed | Validates specs/change shape. |
| `openspec doctor --json` | Healthy | Repository-local OpenSpec health only. |
| Requirement/spec/architecture/coverage/Charter checks | All passed | Deterministic project governance only. |
| `UV_OFFLINE=1 make verify` | Passed: fast `2518`, integration `241` selected (4 existing Gateway skips), workflow `35` | No live/credentialed run; workflow emitted 42 non-failing existing Pydantic serializer warnings. |
| `git diff --check` | Passed | Whitespace only. |
| Root/nested gitlink post-check | Root index remains `160000 66b9e7f21212490cf92fafac137542b9deb06615 0\tdeerflow`; `git diff --submodule=short -- deerflow` and nested porcelain are empty | Confirms no real pointer or nested-worktree mutation by A-002. |

## Observed Side Effects And Remaining Boundary

No adverse side effect was observed in the above deterministic checks. Existing full
manifests now require the static gitlink lock; the only direct minimal fixtures were
updated accordingly. The full root structure walk now intentionally excludes
`deerflow/`, so it cannot become an accidental upstream source scan.

The delivered detector proves only declared local Git metadata consistency. It cannot
prove source conformance, API/runtime compatibility, remote identity, release quality,
or authorization of an upstream revision. Archive and commit remain separate user
decisions. The five task-5 archive-gate obligations remain unchecked until a separate
explicit archive authorization is supplied.
