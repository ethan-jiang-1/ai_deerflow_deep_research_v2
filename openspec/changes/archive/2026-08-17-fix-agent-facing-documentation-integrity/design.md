## Context

See proposal.md — Why. The affected files are navigation and explanatory surfaces:
they must match existing filesystem paths, Makefile target semantics, and pytest
configuration without duplicating runtime authority. `deerflow/` is an upstream
gitlink and is neither modified nor source-browsed by this change.

## Goals / Non-Goals

**Goals:**
- Make every repaired navigation target and command example mechanically checkable.
- Give contributors enough test-placement and network-boundary context to choose an
  appropriate local seam before editing tests.
- Keep one operational authority for each command: the Makefile and local-operations
  guide, with entry documents linking rather than redefining behavior.

**Non-Goals:**
- Restoring or generating a DeerFlow digest, changing upstream documentation, or
  asserting that no external research notes can ever exist.
- Renaming test directories, changing marker behavior, or adding a new test runner.
- Altering CLI, profile, credential, or network behavior.

## Decisions

### D1. Correct stale references; do not add replacement compatibility trees

Root navigation will link to the existing read-only `deerflow/AGENTS.md` and
`deerflow/backend/AGENTS.md` surfaces and explicitly state that the old digest notes
are not distributed with the submodule. `_backlog/README.md` will describe its paths
relative to this checkout, use the actual `deerflow/` submodule locations, and avoid
claiming an upstream branch it cannot establish. `openspec/README.md` will describe
the change store as it currently behaves (active deltas when present; archived
otherwise) instead of asserting active deltas exist.

Alternative rejected: recreate `_digest/` or add redirect placeholders. Either would
misrepresent the missing research material as a maintained local authority and expand
scope into the upstream gitlink boundary.

### D2. Keep command truth in the Makefile and local-operations guide

The Harness README and root README will use `PROFILE=<name>` for Gateway-backed
`demo-real`, label `demo-real-scripted` as an explicit embedded-smoke calibration, and
link readers to `docs/local-operations.md` for operational detail. Documentation
contracts will compare examples to existing target semantics instead of executing a
credentialed command.

Alternative rejected: duplicate profile/credential setup in every README. That creates
several operational authorities that drift independently.

### D3. Document test taxonomy rather than renaming stable paths

`docs/testing-and-evaluation.md` will give a concise placement table for the current
top-level test directories, disclose the autouse public-network denial and the
`requires_llm`/`release_e2e` exceptions, and state that `tests/fixtures/` contains
shared helper modules rather than pytest fixture declarations. Focused contracts check
that those terms remain present and that the documented directory names exist.
Navigation contracts live in `tests/contract/test_documentation_integrity.py`;
test-surface contracts live in `tests/contract/test_test_surface_orientation.py`.
Contracts derive expected commands from the Makefile/local-operations text instead of
hardcoding duplicated strings, so a future Make target edit updates the documentation
contract rather than silently breaking a second copy.

Alternative rejected: rename `fixtures` or reorganize test roots. That would create a
broad import and selection migration with no behavior improvement.

## Risks / Trade-offs

- [A prose change drifts from a Make target] → Focused exact-command contracts read the
  Makefile and documentation together.
- [A reference is valid in a historical archive but not current navigation] → Audit
  only active entry documentation named by the proposal; leave archives untouched.
- [Taxonomy becomes a duplicate test catalog] → Document categories and placement only;
  selectors and evidence claims remain test-owned registries.

## Migration Plan

1. Add focused documentation contracts that fail for the stale path/command wording.
2. Correct the named active documentation surfaces and add concise taxonomy/boundary
   text.
3. Run the focused contracts, governance, strict OpenSpec validation, and the standard
   diff/submodule closeout checks. Rollback is a content-only reversal with no data or
   runtime migration.

## Open Questions

None.
