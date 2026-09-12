# Design — attach-logical-node-summaries

## Context

`LogicalPhase` (`src/deerflow_deep_research/domain/identifiers.py`) is already the single
authority for node names and order; `LOGICAL_NODES`, the registry package list, and the
generated topology document all derive from it. Each node package's `workflow.md` H1
already carries a one-line human meaning, but it lives only in that reader projection.
See proposal.md — Why.

## Goals / Non-Goals

**Goals:**
- Give the unified naming data one canonical summary line per logical node.
- Make the generated topology doc self-explanatory without opening node packages.
- Keep the summaries drift-proof with tests rather than prose conventions.

**Non-Goals:**
- No renames of logical names, state keys, spec directories, or package paths.
- No change to `NodeSpec` (PRS-003-owned frozen contract), registry validation, or any
  runtime/runtime-visible behavior. The topology snapshot's node/edge/reachability
  checks (`validate_topology`) are untouched.

## Decisions

1. **Own the summaries in `identifiers.py` next to `LogicalPhase`, as a frozen
   `Mapping[LogicalPhase, str]`.**
   Why there: the module is already documented as the single source of truth for phase
   names; the summary is an attribute of the logical phase, not of a node package's
   registration. Alternative considered — a `summary` field on `NodeSpec` — rejected:
   it changes a spec-owned frozen contract and duplicates the fact per package, and
   `NodeRegistry` only sees registered packages rather than the phase list.
   `StrEnum` members cannot carry extra fields cleanly, so a sibling frozen mapping
   keyed by the enum keeps the enum the name/order authority while the mapping adds
   meaning. A module-level completeness check (every member has exactly one nonblank
   summary) fails fast at import.

2. **Render summaries in `topology_snapshot.py` as `` - `name` — Summary text ``.**
   The renderer is already the generated-doc authority; the em-dash form matches the
   existing `workflow.md` H1 convention (`# wave1 — Extract ...`). Edges and terminals
   stay as-is; only the Nodes section gains text.

3. **Pin drift with the existing contract test plus one new projection test.**
   `tests/contract/test_topology_snapshot.py` already owns the regenerate-and-compare
   assertion (`committed doc == render_topology_snapshot()`), so once the doc is
   regenerated that coverage extends to summaries automatically. Add to the same
   module a projection-match test: every node package `workflow.md` H1 title after
   its em-dash equals the canonical summary for that logical name. Authority stays
   in `identifiers.py`; `workflow.md` H1s become projections, honoring the repo
   boundary that guides are never a second authority.

4. **`skip_specs: true`.** No spec pins the rendered doc format and no runtime
   behavior changes; inventing a requirement would violate the no-invented-deltas rule.

## Risks / Trade-offs

- [Summary and workflow.md H1 diverge] → test (3b) fails, naming the mismatched node.
- [A reader treats the summary as runtime semantics] → summaries live in a
  docs-only projection path (`topology_snapshot.py`), never imported by graph
  composition, lifecycle, or admission code; the doc header already states it is
  generated and non-authoritative.
- [Enum completeness check could break exotic import order] → the check is a plain
  loop over the enum in `identifiers.py` itself, with no cross-module imports.
