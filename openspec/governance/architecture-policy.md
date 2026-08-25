# Architecture Governance Policy

This directory is a project extension to OpenSpec. OpenSpec does not load it
implicitly, so `openspec/config.yaml` and the repository/module `AGENTS.md` files
must retain short bootstrap pointers to this policy and its checker.

## Authority

| Surface | Authority |
|---|---|
| Active `project-structure` main spec | Normative semantic requirements after the first archive |
| One active owning delta | Pending normative requirements before the first archive |
| `project-structure.toml` | Exact machine-readable structural enumeration |
| Generated block in `deep_research_harness/AGENTS.md` | FUTURE PLAN (not yet implemented): a deterministic compact locator for the registry, roots, grammar, and checker |
| Human-authored `deep_research_harness/AGENTS.md` text | Navigation, rationale, commands, and explicitly labelled future plans |
| Archived change artifacts | Historical context only |
| Contract tests and `check_project_architecture.py` | Mechanical enforcement |

The registry is subordinate to the owning spec. It contains enumerable facts,
not a second prose architecture. This policy defines ownership and update rules
only; it must not contain an independent directory tree or import matrix.

## Import Matrix Authority

The per-layer import matrix splits into two authorities:

- **Internal-layer import directions** (which internal layer each layer may import) are a
  fixed, non-weakenable constraint encoded in `check_project_architecture.py` as
  `REQUIRED_INTERNAL_IMPORT_POLICY`. The `[imports]` table cannot add an internal layer to a
  layer that the owning spec excludes.
- **External namespaces** are authorized per layer solely by the `[imports]` table in
  `project-structure.toml`, checked against a closed top-level-namespace whitelist in the
  checker. Assigning an already-whitelisted namespace to a layer is a TOML-only edit; a
  genuinely new namespace needs a one-time whitelist entry.

The checker therefore does not hard-code a per-layer external-namespace set. The `[imports]`
table has six import-boundary keys (`domain`, `engine`, `agents`, `graph`, `nodes`,
`runtime`) where `nodes` is the graph-owned node-package import sub-layer; the five
ownership layers (`runtime`, `domain`, `engine`, `agents`, `graph`) are a distinct
vocabulary.

## Lifecycle

Before `openspec/specs/project-structure/spec.md` exists, exactly one active
`project-structure` delta may own the pending structural requirements and must
contain the registry reference marker. Once the main spec exists, it is the
active authority. An archived delta never substitutes for a missing or stale
main-spec reference.

## Synchronized Changes

A change that adds, removes, renames, reassigns a structural path, or changes the
declared upstream gitlink lock must:

1. update the owning delta when semantic requirements change;
2. update `project-structure.toml` with the exact current enumeration;
3. regenerate the bounded locator in `deep_research_harness/AGENTS.md` (future plan — the generated locator block is not yet implemented);
4. update deterministic contract fixtures and the smallest sufficient requirement
   evidence mapping; and
5. pass `check_project_architecture.py` before archive.

A new node that conforms to the existing node-package grammar adds its current
package path to the registry without rewriting the grammar. Changing the grammar
itself requires a `project-structure` spec change.

The registry's `[upstream_gitlink]` table is one exact metadata lock, not a source,
runtime, remote, release, or compatibility assertion. Full architecture governance
checks the declared path, root index gitlink, nested `HEAD`, and nested porcelain
state through fixed read-only metadata operations only. The imports-only mode validates
the table's static shape but does not inspect the filesystem or invoke Git. An
intentional upstream bump requires one reviewed change to update the staged root pointer
and declared lock together; the checker verifies that consistency but cannot approve
the bump, recover a mismatch, or determine compatibility.

FUTURE PLAN (not yet implemented): a generated block in
`deep_research_harness/AGENTS.md`, bounded by markers declared in the registry, would
name the registry, source root, test root, ownership layers, node grammar, and
validation command without repeating the required-path inventory. Until it exists, the
human-authored `deep_research_harness/AGENTS.md` text and the TOML registry are the
only authorities; the TOML registry remains the exact enumerable authority.
