## Context

The repository has two intentionally different execution surfaces. The public
reflected `deep_research` tool constructs the default all-fake recipe and its
public skill and SOUL must continue to warn that it is not a research engine.
The standalone demo constructs a recipe with all eleven node modes set to
`real`. Both surfaces currently serialize `implementation_mode=full_fake`
because the result contract supplies that default and lifecycle projection never
uses the recipe.

The active OpenSpec main specs also contain archive placeholders, incomplete
`> req:` headers, and early-prefix language that describes later nodes as still
fake. The requirement registry checker sees some of that drift while the
coverage checker derives a different notion of alive requirements.

No upstream DeerFlow behavior, configuration, public-skill behavior, MCP, ACP,
subagent, sandbox mount, backend, or frontend integration changes are required.

## Goals / Non-Goals

### Goals

- Project a truthful, recipe-derived implementation mode on every lifecycle
  result, including denial and status projections.
- Preserve the default public entry as `full_fake` and the all-fake graph's
  existing no-research-output guarantees.
- Replace stale main-spec text rather than accumulating parallel requirements.
- Make main-spec purpose/header/registry ownership mechanically consistent and
  use that same ownership projection in requirement coverage.
- Replace the module-guide chronology with a stable current capability matrix.

### Non-Goals

- Selecting an implementation recipe from caller input, a checkpoint, a
  session binding, or a manifest.
- Exposing an all-real public Gateway tool or changing the public skill/SOUL
  safety boundary.
- Changing graph topology, state schema, artifact authority, persistence,
  deployment configuration, or any file under `backend/` or `frontend/`.
- Retrofitting every historical archive artifact; archives remain history.

## Decisions

### Derive a closed mode from the recipe

`ResearchGraphRecipe` already retains the normalized implementation-mode tuple.
It will expose one derived closed value:

| Resolved node modes | Result value |
| --- | --- |
| all `fake` | `full_fake` |
| all `real` | `all_real` |
| otherwise | `mixed` |

`DeepResearchControlResult` will validate this closed vocabulary. The recipe is
the sole source; it is not checkpointed and callers cannot set it. Each handler
will pass its recipe value to normal projections and denials, so a standalone
all-real pre-graph denial cannot be mislabeled full-fake.

Keeping a free-form string was rejected because it permits a future typo or
unreviewed label to reintroduce an untruthful public result. Storing the mode in
`ResearchState` was rejected because recipe selection is runtime construction
fact, not lifecycle control authority.

### Retain the public full-fake boundary explicitly

The default `build_research_handlers()` path continues to instantiate the
default all-fake recipe. Public skill and SOUL statements therefore remain
correct and will be documented as entry-surface behavior, not as a claim that
all available node implementations are fake. The capability matrix will make
the three distinct facts visible: real factory availability, standalone demo
recipe, and public reflected-tool recipe.

### Replace stale requirements in place

The affected early-node specs keep their integration requirements, because the
real prefix, fake regression, and dependency fail-closed behavior are still
valid. Their complete requirement blocks are modified to replace the obsolete
claim that a mixed prefix is `full_fake` with the recipe-derived `mixed` result.
No requirement is removed merely because one historical sentence is obsolete.

The same approach modifies the lifecycle and demo requirements. Main-spec
Purpose text and headers are repaired directly when the change is applied;
archive-generated `TBD` text is removed from active authority, not copied to a
new specification.

### Treat active terminology as current authority, not an archive index

The active main specs, requirement registry, `agent/AGENTS.md`, and
`agent/README.md` will describe current behavior and stable compatibility facts.
They will not retain numbered-change chronology, phrases such as "later Wave", or
former skeleton/phase-completion narratives as an explanation of present behavior.
Archived OpenSpec artifacts remain the only historical record and are not edited.

`full_fake` remains permitted only where it names the current all-fake recipe or
the public reflected-tool safety boundary. It must not be used as a proxy for a
mixed or all-real execution. The implementation will add deterministic active-
authority scans with a small explicit allowlist for these current facts, so this
removal policy is verifiable rather than a one-time prose cleanup.

### Separate structural and ownership validation, then share ownership

`check_project_specs.py` remains the structural authority for main specs and
will reject a missing, empty, or archive-placeholder Purpose as well as a missing
Requirements section. `check_project_reqs.py` will expose a pure ownership
projection for active main specs. For each non-retired registry entry, the
capability name encoded in the registry must match exactly one main-spec
directory, and that directory's pre-heading `> req:` header must declare the
entry. A main-spec header may not declare an active requirement owned by another
capability.

`check_project_req_coverage.py` will consume the same projection rather than
independently accepting any header token as alive. This preserves existing
test-evidence responsibilities while preventing one checker from passing an
incomplete header that the registry checker rejects. Purpose validation remains
structural rather than being duplicated in test-evidence coverage.

### Keep mode propagation at the handler boundary

`ResearchActionHandler` owns the configured recipe, so its snapshot and
handler-generated denial projections will receive the derived mode explicitly.
The top-level reflected tool may continue to call generic `denial_result()`
without a recipe because it can only use the default all-fake host. The standalone
demo reaches its configured handlers through `build_demo_host()` and therefore
receives the all-real/mixed mode even for a handler denial. This keeps the public
tool boundary explicit without adding a globally mutable recipe selector.

## Risks / Trade-offs

- Existing tests may assert the old literal default. → Update only tests that
  construct all-real or mixed recipes; retain all default public-tool assertions.
- A strict registry-to-header check can reveal additional omissions beyond the
  initially observed IDs. → Repair all active main headers in the same change and
  add focused malformed-fixture coverage.
- The mode describes recipe selection, not proof of provider success. → Name and
  document it as implementation composition; retain terminal status, evidence,
  and report contracts as separate truth.
- A capability matrix can become stale. → Derive its node list from the stable
  topology/recipe facts where practical and avoid change-number chronology.

## Migration Plan

1. Add red deterministic tests for recipe-to-result projection and malformed
   specification ownership fixtures.
2. Implement the closed mode projection and preserve default all-fake behavior.
3. Repair registry headers, Purpose text, affected main-spec requirements, and
   the module guide/README wording.
4. Run the three root governance checkers, focused agent tests, then the
   canonical deterministic verification command.

Rollback is source-only: reverting this change restores the prior result label
and documentation. No persisted state, artifact format, configuration, or
provider migration is introduced.

## Open Questions

None. The public boundary is intentionally all-fake, and the standalone demo is
already the all-real consumer; this change only makes that existing separation
truthful and mechanically maintained.
