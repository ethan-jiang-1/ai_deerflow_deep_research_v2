## Context

See proposal.md — Why. The repository already treats the non-production adapter tree as
"fixture": the manifest key is `fixture_root`, the package is
`deerflow_deep_research_fixtures`, the owning capability is `fixture-source-isolation`,
and the commands are `demo-fixture-graph` / `--fixture`. Only the containing source-root
directory and its live references still say `src_fake`. The directory is on `PYTHONPATH`
in several run roots, is enumerated in the structure manifest, and appears as a CI path
filter, so the rename is a single atomic structural edit rather than an isolated file
move.

## Goals / Non-Goals

**Goals:**
- Align the non-production source-root directory name with the repository's authoritative "fixture" vocabulary.
- Keep the import package name, isolation semantics, public symbols, and every runtime fact unchanged.
- Leave the structure registry, generated locator block, CI path filter, and all live references synchronized and checker-clean.

**Non-Goals:**
- Renaming the package `deerflow_deep_research_fixtures`.
- Renaming the `FAKE_GRAPH` / `REAL_NODE_FAKE_CAPABILITIES` authenticity vocabulary or `tests/fixtures/`.
- Any behavior, state, route, error-code, diagnostic, or persistence change.
- Rewriting historical `_backlog/` or `openspec/changes/archive/**` paths.

## Decisions

**Rename the directory to `src_fixtures/`; keep the package name.**
`src_fixtures` is the only candidate that (a) matches the manifest/package/spec term,
(b) preserves the `src/` ↔ `src_*` alternate-source-root symmetry, and (c) avoids the
already-occupied `tests/fixtures/` name. Alternatives rejected: `fixtures/` collides with
`tests/fixtures/`; `src_fakes/` keeps the misleading term; role-based names such as
`src_adapters/` drop the deterministic-fixture signal and misdescribe test usage.

**No compatibility alias or symlink.** `PRS-001`/`PRS-017` reject a tracked alias or
second source root, so the rename is a plain `git mv` with all references updated in the
same change; there is no transitional period.

**Specs are modified, not skipped.** Unlike a pure module-file rename, the literal path
lives in requirement statements (`FSI-001`, `FSI-003`, `PRS-001`, `PRS-017`, `PRS-019`,
`EVH-005`), so the change carries MODIFIED deltas that preserve each full statement and
every surviving scenario verbatim with only the path substituted. Behavior is unchanged,
so no NEW requirement is introduced and `skip_specs` is not used.

**The generated `AGENTS.md` block is re-rendered, not hand-edited.** `fixture_root` in
`project-structure.toml` is the single source; `check_project_architecture.py
--render-guide` regenerates the locator block, and the checker enforces it (`PRS-021`).

## Risks / Trade-offs

- [A live `src_fake` reference is missed, so an import path or CI filter rots] → Sweep with `rg "src_fake"` over live trees; the architecture checker, the CI-workflow contract test, and `make verify` all fail loudly on a missed reference.
- [CI periodic workflow silently stops triggering after the folder move] → Update `.github/workflows/agent-entry-environment-regression.yml` and the `test_entry_environment_regression_workflow` contract assertion that pins the path filter.
- [Generated locator block drifts] → Re-render via the architecture checker and let its diff-match check gate the change.
- [Directory rename breaks editable installs or demo PYTHONPATH] → `pythonpath` in `pyproject.toml` and every `PYTHONPATH=src_fake` in the Makefile are updated atomically; `make demo` and `make demo-scripted` prove zero-credential fixture execution still starts.

## Migration Plan

1. `git mv deep_research_harness/src_fake deep_research_harness/src_fixtures`.
2. Update harness references: `pyproject.toml`, `Makefile`, `scripts/_demo_core.py`, and the five test files that pin the literal path.
3. Update the CI workflow path filter and its contract assertion.
4. Update governance: `project-structure.toml` `fixture_root`, the `check_project_architecture.py` literal, the `required-paths.toml` fixture entries, and the `req-registry.yaml` FSI-001 description; verify with `req-registry` tooling.
5. Re-render the `AGENTS.md` generated block and update the four living docs.
6. Run the closeout gates. Rollback is `git revert` of the change commit; no persisted run state, Bundle, or profile is touched, so there is no data migration to undo.
