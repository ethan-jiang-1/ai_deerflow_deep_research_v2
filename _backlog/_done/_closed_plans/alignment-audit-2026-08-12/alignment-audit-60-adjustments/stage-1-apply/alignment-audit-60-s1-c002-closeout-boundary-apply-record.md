# Stage 1 Apply Record - C-002 Proposal And Closeout Boundary

> Change: `retire-v1-topology-residue`
> Status: **VERIFIED - A-002 REMAINS DEFERRED**
> Apply-time repository HEAD: `362962a167ca80eb93f08414aa920455732303c6`
> Date: 2026-08-12

## Adjustment C-002

- **Authority owner:** `openspec/config.yaml` proposal and task/closeout authoring
  rules.
- **Affected paths:** `openspec/config.yaml` only.
- **Before:** The proposal rule protected root `backend/` and `frontend/` as if they
  were the active DeerFlow boundary. The closeout rule required those directories to
  stay clean, which neither matched the current `deerflow/` gitlink nor identified the
  actual proof available.
- **After:** Proposal authoring must state that ordinary downstream work does not
  modify or source-browse `deerflow/` without explicit ownership. Archive closeout
  records root Git status, gitlink index/submodule identity, nested-worktree status,
  and a submodule-aware diff review; the rule calls this manual scope/diff evidence.
- **Reason and evidence:** Baseline Git index mode `160000` and `git submodule status`
  identify `deerflow/` as the observed upstream gitlink. No C-002 detector or
  governance executable exists in this change's authority.
- **Main risk:** Removing the inaccurate rule could leave a protection vacuum, while
  overstating manual commands as a detector would create false confidence.
- **Possible side effects:** Archive closeout requires more manual review; a reader may
  still mistake prose for enforcement; existing checkers may not catch a future gitlink
  pointer or nested-worktree change.
- **Risk controls / stop condition:** The updated rule names exact commands and says
  their proof is manual and bounded. It says neither automatic detection nor
  protection exists. Stop and defer A-002 if a detector, test, manifest/TOML, registry,
  or governance executable change becomes necessary.
- **Verification before apply:** The baseline Git metadata commands succeeded with
  empty root/nested porcelain status; the C-001 occurrence table classified all active
  non-archive `backend`/`frontend` terms.
- **Verification after apply:** Final scoped diff review found only the planned
  `openspec/config.yaml`, `deep_research_harness/AGENTS.md`, and Charter topology
  changes plus authorized V-001 format maintenance. `openspec validate
  retire-v1-topology-residue --strict`, `openspec doctor --json`,
  `check_agent_charter.py`, `git diff --check`, and changed-document link inspection
  passed. `make verify` was re-evidenced target-by-target after the original tool
  session lost its final output: fast 2495, integration/blocking-I/O 241 (4 expected
  skips), and workflow 35 all had zero failures/errors. Final gitlink evidence is mode
  `160000` at `66b9e7f21212490cf92fafac137542b9deb06615`, matching submodule status;
  root and nested porcelain status show no extra gitlink change.
- **Observed side effects:** No behavioral side effect can result from this
  documentation-only edit. No documentation inconsistency was observed in the scoped
  C-001/C-002 review. Manual evidence remains manual: it does not become an automatic
  detector or protection mechanism.
- **Remaining mismatch / follow-up owner:** A-002 automatic gitlink detection remains
  `DEFERRED-CODE-CHANGE`; manual evidence is not a substitute.
- **Authorization and date:** User authorized Stage 1 apply on 2026-08-12.
