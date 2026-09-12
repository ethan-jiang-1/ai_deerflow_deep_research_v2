# Tasks — harden-entry-doc-navigation

## 1. runtime/ reader index

- [x] 1.1 Create `deep_research_harness/src/deerflow_deep_research/runtime/README.md`: non-authority disclaimer header (COMMANDS.md pattern), 5-cluster reader index (bundle lifecycle/control; graph/node execution; work units; observation/evaluation; debug) with per-cluster file list, one-line responsibility, and owning spec / proof-seam pointers. Verify: all listed filenames exist and relative links resolve (`ls` cross-check).

## 2. Entry routing

- [x] 2.1 Add one row to `deep_research_harness/docs/README.md` Living References table routing to `../src/deerflow_deep_research/runtime/README.md`. Verify: relative link resolves from docs/README.md.
- [x] 2.2 Add one row to `deep_research_harness/README.md` Reading Map routing to `COMMANDS.md`. Verify: link target exists.

## 3. Root README residents and Direction Controls

- [x] 3.1 Extend root `README.md` layout block with 5 registered residents: `config.yaml`+`.env` (host runtime config & credentials, gitignored, host convention), `profiles/`, `skills/public/`, `RUN-*.command` (local launchers, gitignored, indexed in COMMANDS.md), `CONTEXT.md`/`CONTEXT-MAP.md`. Each entry is "what it is + where the authority lives", no restated detail. Verify: block renders, no duplicated contract text.
- [x] 3.2 Collapse the `deep_research_harness/README.md` "Direction Controls" section to a pointer block: one framing sentence + links to `docs/runtime-architecture.md` (Public Controls, Ordinary Controller Loading) + named owning spec `deep-research-harness-run-bundles`; delete all restated contract prose. Verify: no refine/resume rule text remains in that section; links resolve; `check_doc_hygiene.py` rule 2 passes.

## 4. Launcher hygiene

- [x] 4.1 Fix `RUN-010.command` header pointer from `_backlog/_local_demo/runbook-010-tui-auto.md` to `deep_research_harness/docs/runbooks/runbook-010-tui-auto.md`. Verify: referenced path exists.
- [x] 4.2 Run `git rm --cached RUN-020.command` (keep the local file) to align tracking with the `RUN-*.command` ignore rule. Verify: `git check-ignore --no-index RUN-020.command` matches `.gitignore:240`; `git ls-files RUN-020.command` empty; file still on disk.
- [x] 4.3 Add one footnote line to `deep_research_harness/COMMANDS.md` launcher column: the 双击入口 files are local gitignored conveniences (absent from fresh clones); the make target in the same row is the canonical entry. Verify: no table row references a repo-tracked launcher as guaranteed-present.

## 5. Gate verification

- [x] 5.1 Run doc hygiene and closeout governance gates plus the deterministic project gate; confirm no unrelated drift: `python3 openspec/governance/check_doc_hygiene.py` (if independently runnable), `python3 openspec/governance/check_project_gate.py --phase closeout`, `UV_OFFLINE=1 make verify`.
