# Design: restore-agents-structure-locator

## Context

The canonical structure locator in `deep_research_harness/AGENTS.md`
(`<!-- BEGIN/END GENERATED: PROJECT-STRUCTURE -->` block) was removed in commit
`54886b8` together with its render/freshness machinery in
`check_project_architecture.py` (`render_guide_block`, `_validate_guide`,
`--render-guide`) and the registry `[guide]` table. The main spec (PRS-004) still
normatively requires it. See proposal.md — Why.

## Goals / Non-Goals

**Goals:**

- Restore the marker-bounded locator block in `deep_research_harness/AGENTS.md`,
  rendered from the registry (never hand-maintained).
- Restore the deterministic render + freshness machinery in
  `check_project_architecture.py` so the block cannot silently drift again — the
  PRS-004 scenario "Generated locator follows the registry" becomes machine-checked.
- Restore the `[guide]` registry table and its parsing/validation.

**Non-Goals:**

- No product-runtime change; no `deerflow/` touch; no `make verify` change.
- PRS-004's existing text stays untouched; a new PRS-021 requirement owns the
  checker's restored enforcement (missing/duplicate/drifted block rejection and
  `--render-guide`).
- Do NOT modify `check_doc_hygiene.py` (independent doc-layer gate).

## Decisions

1. **Restore the original design faithfully, do not re-invent.**
   The old `render_guide_block` / `_validate_guide` / `--render-guide` / `[guide]`
   design was spec-aligned and working; restoring it faithfully minimizes risk.
   *Alternative (hand-written static block) rejected: it would drift again and fail
   PRS-004's rendered-from-registry scenario.*

2. **Freshness lives in `check_project_architecture.py`, not in `check_doc_hygiene.py`.**
   The locator is a structural-registry projection owned by PRS-004; the architecture
   checker is the owning enforcer (as originally). The doc-hygiene gate stays a
   separate concern (ADR index / entry-chain links / encoding-newline).

3. **Revert the `architecture-policy.md` relabel.**
   The previous change marked the generated block "future plan"; after restoration it
   exists again, so the original policy text (describing it as an active authority
   surface with a regeneration step) is true again. Reverting keeps policy == reality.

4. **Markers are registry-declared, not checker-hard-coded.**
   `begin_marker` / `end_marker` live in `project-structure.toml` under `[guide]` (as
   originally), so a marker change is a registry edit, not a checker edit.

## Risks / Trade-offs

- **[Freshness check could break closeout if AGENTS.md is mid-edit]** → The block is
  restored together with the checker in the same apply; closeout runs only after both.
- **[Adding `[guide]` changes manifest schema]** → `load_manifest` gains required
  `[guide]` parsing; the registry is updated in the same change, so schema stays
  consistent.
- **[Old code may not match current checker internals]** → `render_guide_block` uses
  only fields already present in the current `StructureManifest` (source/fixture/test
  roots, ownership layers, `node_root`, `node_public_export`); only `[guide]` fields
  are new.
- **[Previous change's relabel is committed]** → Reverting it is a normal follow-up
  edit; the two changes are related but independently coherent (gate change archived
  first, locator restoration after).
