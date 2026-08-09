## 1. Admission And Red Evidence

- [x] 1.1 Apply agent: re-read the `agent-information-map` policy, the DRC-006 main
  requirement, the current README, and its three focused document owners. Confirm the
  six surfaces and their detail-owner links describe current approved behavior rather
  than archived-change claims; correct the proposal/spec/design if a named surface has
  no current owner.
  Review conclusion: the README and `CONTEXT.md` establish the dedicated-Agent/tool,
  standalone operator CLI, TUI, and workbench boundaries; approved demo and CLI specs
  establish full-fake, fixture-graph, and all-real composition; the three focused docs
  own commands, authority, and verification detail. No artifact correction is needed.
- [x] 1.2 Add a red static README contract in
  `tests/contract/test_demo_commands.py` named
  `test_readme_entry_surfaces_route_to_current_detail_owners`. It covers the `Entry
  Surfaces` heading and columns before `Reading Map`, each named route's composition
  and non-goal distinction, and links to local operations, runtime architecture, and
  testing/evaluation. Record that the current shallow table fails this selection before
  editing documentation.
  Red baseline: the focused selector fails with `ValueError: substring not found` for
  `## Entry Surfaces`, proving that the shallow table cannot meet the required route
  grammar.

## 2. Information Map Implementation

- [x] 2.1 Replace the root README's entry-point table with the early `Entry Surfaces`
  map. Preserve the existing Reading Map, quick start, and canonical command spelling;
  route readers to focused detail owners instead of copying command, lifecycle, or test
  procedures into the new table.
- [x] 2.2 Turn the focused documentation contract green and register its one
  `DRC-006` `PUBLIC_ENTRY` claim, `readme-entry-surfaces`, and its one matching
  requirement impact in the existing test-owned evidence assets. Preserve existing
  command-contract ownership and avoid an unrelated evidence catalog rewrite.

## 3. Verification And Closeout

- [x] 3.1 Run `cd deep_research_harness && UV_OFFLINE=1 uv run --no-sync --extra
  operations python -m pytest tests/contract/test_demo_commands.py
  tests/contract/test_agent_charter_governance.py`, then `UV_OFFLINE=1 make
  governance` and `UV_OFFLINE=1 make test-assets`. Confirm the README stays within the
  charter's readable information-map posture and that the detailed document links and
  required command spellings remain valid.
- [x] 3.2 Run `cd deep_research_harness && UV_OFFLINE=1 make verify`, `openspec
  validate document-entry-surfaces --strict`, applicable documentation/architecture
  gates, and `git diff HEAD --check`. Sync the accepted `deep-research-agent-charter`
  delta, then run `openspec validate --specs` before archiving. Update
  `_backlog/plans/cli-tui-entry-integrity-repair_plan.md` with evidence and archive
  path, commit, then record `git status --porcelain=v1 --untracked-files=all` with
  `deerflow/`, `backend/`, and `frontend/` clean.
