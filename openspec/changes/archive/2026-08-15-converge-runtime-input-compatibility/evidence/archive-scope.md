# Archive Scope Snapshot

Captured during apply on 2026-08-15 before archive.

- `git ls-files --stage deerflow` records gitlink
  `160000 66b9e7f21212490cf92fafac137542b9deb06615 0\tdeerflow`.
- `git submodule status -- deerflow` reports
  `66b9e7f21212490cf92fafac137542b9deb06615 deerflow`.
- `git -C deerflow status --porcelain=v1 --untracked-files=all` was empty, and
  `git diff --submodule=short` contains no `deerflow` diff.

This records scope only. It does not assert any upstream DeerFlow behavior or
compatibility, and this change does not modify the gitlink.
