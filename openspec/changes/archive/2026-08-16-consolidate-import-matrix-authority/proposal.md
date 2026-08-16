## Why

`check_project_architecture.py` hard-codes a per-layer import matrix
(`REQUIRED_IMPORT_POLICY`) that duplicates the `[imports]` table already in
`project-structure.toml`. That second source of truth drifted once already (the archived
`wire-harness-observability-entrypoints` change added `httpx_sse` to the TOML but not to
the checker, turning the guard red) and contradicts the policy that forbids an
independent import matrix. This change removes the per-layer duplicate so the TOML owns
per-layer assignment and the checker no longer carries a per-layer set.

## What Changes

- Replace `REQUIRED_IMPORT_POLICY`'s fused per-layer exact-set comparison with a split: a
  fixed non-weakenable internal-layer direction constraint, plus a closed
  top-level-namespace whitelist; the TOML `[imports]` table then owns per-layer assignment of
  whitelisted namespaces.
- Clarify the two distinct layer vocabularies: `ownership_layers` (5 layers:
  `runtime`, `domain`, `engine`, `agents`, `graph`) versus the import-boundary layers
  (6 keys, additionally `nodes` as the graph-owned node-package import sub-layer).
- Record the single-authority rule in `architecture-policy.md` so the already-stated
  "must not contain an independent import matrix" is actually enforced, and add a
  deterministic regression test that the checker no longer hard-codes a per-layer matrix.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `project-structure`: the import matrix's machine authority becomes the
  `project-structure.toml` `[imports]` table, and the import-boundary layers (including
  `nodes`) are distinguished from the five ownership layers (PRS-002).

## Impact

- `openspec/governance/check_project_architecture.py` — remove the hard-coded matrix,
  add namespace-whitelist validation.
- `openspec/governance/project-structure.toml` — the `[imports]` table is the authority;
  possibly a clarifying comment, no behavioral change.
- `openspec/governance/architecture-policy.md` — implement the no-independent-matrix rule.
- `openspec/governance/` contract tests and the project-structure delta — regression seam.
- No `deerflow/` source, no runtime import-rule change, no runtime behavior change.

## Change Focus

- **Primary module / causal owner:** `openspec/governance/check_project_architecture.py`
  (PRS-002 mechanical enforcement) with `project-structure.toml` `[imports]` as its authority.
- **Seam classification:** deterministic-guardrail — the edit target is the deterministic
  architecture checker's internal authority source; no model, human decision, or graph route.
- **Question:** what is the single machine authority for the per-layer import matrix, and
  how does the checker still enforce import boundaries without a hard-coded per-layer set?
- **Necessary adjacent/external contracts:** `project-structure.toml` `[imports]` (becomes
  the sole machine matrix); `architecture-policy.md` (states the no-independent-matrix rule);
  a contract test seam (asserts the checker no longer hard-codes the matrix).
- **Evidence seam:** `check_project_architecture.py` full run plus the existing import
  boundary tests, plus one new regression test asserting the checker derives from TOML.
- **Not in scope:** runtime import-rule semantics, `deerflow/` source, submodule branch
  identity wording, `harness` naming ambiguity.
- **Triggered review policies:** change-admission, control-placement

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| External-namespace authorization (which external package each layer may import) | None — no model or person proposes import rules | `project-structure.toml` `[imports]` is the direct fact for per-layer assignment; `check_project_architecture.py` is the deterministic evaluator; internal-layer directions stay a fixed non-weakenable invariant | non-bypassable | PRS-002 internal import-direction rules are not weakened; a genuinely new namespace takes effect only after a one-time whitelist entry plus TOML assignment, and an already-whitelisted namespace is reassigned by TOML alone | Removes the fused `REQUIRED_IMPORT_POLICY` per-layer duplicate; keeps the internal-direction invariant and reuses existing `_external_allowed` / `_validate_module_imports` TOML-derived checks | Full `check_project_architecture.py` run + import-boundary contract tests + new internal-direction and external-namespace regressions |
