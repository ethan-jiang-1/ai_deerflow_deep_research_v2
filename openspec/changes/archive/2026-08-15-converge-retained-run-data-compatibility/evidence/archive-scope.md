# Archive Scope Evidence

> Task 5.4 snapshot, recorded on 2026-08-15 before archive.

## Gitlink Boundary

```text
git ls-files --stage deerflow
160000 66b9e7f21212490cf92fafac137542b9deb06615 0 deerflow

git submodule status -- deerflow
 66b9e7f21212490cf92fafac137542b9deb06615 deerflow (heads/main-282-g66b9e7f2)
```

`git -C deerflow status --porcelain=v1 --untracked-files=all` produced no output.
`git diff --submodule=short` contains no `Submodule deerflow` stanza. Therefore no
DeerFlow source edit and no gitlink pointer update is part of this change.

## Worktree Scope

`git status --porcelain=v1 --untracked-files=all` lists only:

- `deep_research_harness/scripts/_demo_core.py`;
- retained-data cutover test cleanup/formatting under `deep_research_harness/tests/unit/`;
- this change's `tasks.md`; and
- this change's closeout evidence under `openspec/changes/converge-retained-run-data-compatibility/evidence/`.

The demo scope revision creates a distinct current trusted Bundle scope under the
already ignored local demo root. It does not inspect, alter, or import the old root.
All other modifications are either direct retained-data cutover implementation or
its deterministic evidence. No path under `deerflow/` is included.
