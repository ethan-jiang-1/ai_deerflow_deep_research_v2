## Context

`check_project_architecture.py` currently enforces the import matrix two ways that overlap:

- `project-structure.toml` `[imports]` already lists, per layer, every permitted top-level
  namespace (`domain`, `engine`, `agents`, `graph`, `nodes`, `runtime`).
- The checker additionally hard-codes `REQUIRED_IMPORT_POLICY` (lines 38-45) and compares
  each TOML layer against it at lines 338-343.

The real import-direction enforcement (`_external_allowed` at 736, `_validate_module_imports`
at 813) already derives its allowed namespaces from `manifest.imports` plus `INTERNAL_LAYERS`;
it does not read `REQUIRED_IMPORT_POLICY`. That table exists only to assert the TOML does not
diverge from a frozen copy. The archived `wire-harness-observability-entrypoints` change
proved the risk: adding `httpx_sse` to the TOML without editing the frozen copy turned the
guard red. See proposal.md for motivation.

Two vocabularies also share the word "layer": `ownership_layers` (5 layers in
`project-structure.toml:19`) and the import keys (6, because `nodes` is a graph-owned import
sub-layer). The current code does not name this distinction.

## Goals / Non-Goals

**Goals:**

- Make `project-structure.toml` `[imports]` the single machine authority for the per-layer
  import matrix.
- Keep the checker able to reject an unknown namespace without re-introducing a per-layer set.
- State the ownership-layer versus import-layer distinction so it is not re-ambiguous.
- Fix the spec drift where PRS-002 omitted `gateway_observer.py`'s `httpx`/`httpx_sse` usage.

**Non-Goals:**

- Changing any runtime import-direction rule. The accepted and rejected imports are identical
  before and after this change.
- Folding the file-level provider-classifier exceptions (`httpx`/`openai`/`httpx_sse`
  file-specific allowances) into the TOML. Those remain a narrower spec-owned constraint.
- Touching `deerflow/`, the submodule branch identity wording, or `harness` naming.

## Decisions

### 1. Split the fused matrix into a fixed internal-direction constraint and a TOML-authorized external-namespace set

`REQUIRED_IMPORT_POLICY` conflates two things. The internal-layer import directions (which
internal layer each layer may import) are a spec-owned, non-weakenable invariant:
`test_manifest_cannot_weaken_domain_boundary` already asserts the manifest cannot make
`domain` import `runtime`. The external namespaces (packages outside the internal layers) are
extensible and were the actual drift surface (`httpx_sse`). Split them:

- `REQUIRED_INTERNAL_IMPORT_POLICY`: per layer, the exact internal-layer set it may import
  (`domain` → none; `engine` → `{domain}`; `agents` → `{domain}`; `graph` →
  `{domain, engine, nodes}`; `nodes` → `{domain, engine}`; `runtime` → `{domain, graph,
  agents}`). The checker asserts `set(imports[layer]) & INTERNAL_LAYERS == this`, so the
  manifest cannot weaken an internal direction.
- A closed top-level-namespace whitelist for external namespaces: `stdlib`, `pydantic`,
  `deerflow`, `langchain`, `langgraph`, `httpx`, `httpx_sse`, `openai`. Every non-internal
  value in `[imports]` must belong to it; the checker never lists which external namespace a
  layer may use.

This removes the per-layer external-namespace set from the checker. Assigning an
already-whitelisted namespace to a layer is a TOML-only edit; introducing a genuinely new
namespace still needs a one-time whitelist entry, but no longer a per-layer exact match.

Error codes: the internal-direction assertion keeps `imports.policy` (so
`test_manifest_cannot_weaken_domain_boundary` is unchanged); an unknown external namespace
reports a new `imports.namespace` code.

**Alternative considered:** fully delete the matrix and rely on the whitelist alone.
Rejected: it would let the manifest weaken internal boundaries (e.g. `domain` → `runtime`),
which `test_manifest_cannot_weaken_domain_boundary` and PRS-002 forbid.

### 2. Keep the file-level provider-classifier exceptions as-is

`_external_allowed` (lines 727-735) allows `openai`/`httpx` only in `node_agent_bridge.py`
and `httpx`/`httpx_sse` only in `gateway_observer.py`. These are narrower than the per-layer
matrix and are owned by PRS-002's "direct provider classifier imports stay at the raw
binding" scenario. They do not duplicate the per-layer set, so they stay. The spec delta
updates that scenario's prose to include `gateway_observer.py`.

### 3. Name the two layer vocabularies instead of merging them

Keep `ownership_layers` at five (`runtime`, `domain`, `engine`, `agents`, `graph`, per
PRS-001) and `INTERNAL_LAYERS` at six (adding `nodes`). In the checker, rename or annotate
`INTERNAL_LAYERS` as the import-boundary layer set and document that `nodes` is the
graph-owned node-package import sub-layer, not an ownership layer. `architecture-policy.md`
gains one sentence recording the distinction so it does not look like a 5-vs-6 inconsistency.

### 4. Regression proof at the checker's own seam

Extend `tests/contract/test_import_boundaries.py`:
- Keep `test_manifest_cannot_weaken_domain_boundary` passing — it now proves the
  internal-direction assertion rather than the fused matrix.
- Add a red-before-green case that assigning an already-whitelisted namespace (e.g.
  `pydantic`) to a new layer in `[imports]` is accepted with a TOML-only edit, and a negative
  case that an unknown namespace (e.g. `bogus_ns`) is rejected.

The strongest proof is behavioral: a copied manifest with a whitelisted namespace reassigned
across layers passes the checker, while the same manifest with an added internal layer is
rejected. The existing direction tests already cover the unchanged import rules.

## Risks / Trade-offs

- [Internal-direction constraint is still a hard-coded copy of the spec] → It encodes only
  the non-weakenable internal-layer directions (a spec-owned invariant), not the extensible
  external namespaces, so it is no longer a drift surface; the PRS-002 prose remains the
  semantic owner and any internal-direction change is a deliberate spec change.
- [Whitelist itself becomes a second truth] → The whitelist only enumerates legal top-level
  namespaces (a mechanical fact); it never says which layer uses which.
- [Splitting the check weakens validation] → The internal-direction assertion stays exact per
  layer; the external-namespace check is whitelist plus the existing `_validate_module_imports`
  derivation, so no direction rule is lost.
- [Spec delta corrects drift beyond the stated "single authority" scope] → The
  `gateway_observer.py` spec correction is within the same modified requirement (PRS-002) and
  is required for the delta to be true; it adds no behavior.
- [Migration is a refactor with a live guard] → No runtime behavior changes; rollback is a
  plain revert, verified by the full `check_project_architecture.py` run and `make verify`.
