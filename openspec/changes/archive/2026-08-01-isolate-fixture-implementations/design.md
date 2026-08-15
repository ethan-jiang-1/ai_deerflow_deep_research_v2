## Context

See [proposal.md](proposal.md) for motivation and scope.  The current production
package combines two different concerns in the same import tree: every `NodeSpec`
contains a real and a fake factory, every node package requires `fake.py`, and the
graph builder turns a missing or falsey implementation map into an all-fake graph.
The reflected host reaches that default through `ResearchGraphRecipe.create()`.

Fixture-only state (`FakeFixturePlan`, `fixture_plan`, and the fixture terminal
marker), fixture gate rules, node routing helpers, and deterministic adapter modules
also live below `deerflow_research/src/deerflow_deep_research/`.  Several real node
modules import `engine.fake_control` solely for a generic state-update helper.  This
means that production imports fixture behavior and that absence of configuration can
change public behavior.

The affected seams are graph adapter selection, recipe assembly, checkpoint namespace
derivation, the test/demo launch path, and the current code-derived node-prompt review
projection. `backend/` and `frontend/` remain out of scope.

## Goals / Non-Goals

### Goals

- Make the production source tree deployable without any fixture implementation
  available on its import path.
- Preserve deterministic fixture graph coverage through a deliberately injected,
  complete catalog for tests and credential-free demos.
- Fail before graph compilation for an omitted, empty, incomplete, duplicate, unknown,
  or unavailable adapter selection.
- Make the reflected public lifecycle all-real by construction and prevent old
  full-fixture checkpoints from being resumed as real runs.
- Keep shared non-fixture state mechanics in a neutral production module.
- Keep the generated node-prompt review projection reproducible for an explicit reviewer
  without presenting it as a tracked source-like tree to ordinary coding work.

### Non-Goals

- Change graph topology, phase contracts, real-node model/tool behavior, or add a new
  public mode selector.
- Make fixture code installable in the production wheel, Gateway runtime, or Docker
  image.
- Migrate, resume, or delete historical full-fixture public sessions automatically.
- Change node prompt semantics, runtime prompt selection, or the renderer/builder ownership
  boundary merely to relocate the review projection.
- Modify upstream DeerFlow, `backend/`, or `frontend/`.

## Decisions

### 1. Use a separate source root and a distinct top-level package

Fixture code will live at:

```text
deerflow_research/src_fake/deerflow_deep_research_fixtures/
```

It will be a regular, distinct package rather than another
`deerflow_deep_research` root.  This prevents Python's import-order rules from
silently selecting fixture code for a production import.  Its internal layout can
mirror the logical-node organization, with a catalog root, fixture plans, gate rules,
and per-node adapters.

The fixture package may import documented production contracts such as `NodeFactory`,
`NodeBuildDependencies`, gate contracts, topology names, and neutral state helpers.
The production package must never import it.  Hatch packaging remains limited to
`src/deerflow_deep_research`; production editable/runtime and Docker paths must retain
the same exclusion.  Test and fake-demo launchers add `src_fake` only to the child
process import path.

Alternatives considered:

- Put fakes in `tests/`: rejected because the credential-free demos need the same
  complete deterministic implementation.
- Use another `deerflow_deep_research` source root: rejected because import precedence
  would make the selected implementation implicit and brittle.
- Keep fakes next to real nodes behind naming conventions: rejected because physical
  placement is the boundary being enforced.

### 2. Make production NodeSpec real-only and inject one explicit adapter selection

`NodeSpec` will retain the logical name, contracts, policy, capabilities, and one real
factory.  The production registry will require only production files and import only
the package root's real-only `NODE_SPEC`.

The graph package will expose a small neutral recipe-composition interface. A selection
has one named adapter for every `LOGICAL_NODES` member plus the adapter's capability
profile and a deterministic gate-membership contract; it is validated against the
production specs before `StateGraph` construction. Its paired gate-definition selection
must contain exactly the selected adapters that require a gate, with no unknown or
extraneous gate entry. This keeps a missing gate from silently turning a gated phase into
an ungated one. The all-real selection is assembled directly from registered real
factories. A fixture catalog is an external producer of adapters and matching fixture
gate definitions for that same interface. The wrapper uses the selected adapter metadata,
rather than function identity or a `fake_factory` field, to decide which declared real
capabilities are attached.

`build_research_graph()` and the generic
`ResearchGraphRecipe.from_adapters()` constructor will require explicit paired adapter
and gate selections. They must not use truthiness (`x or default`) for maps. Empty
mappings, missing entries, duplicates, unknown names, invalid adapter kinds,
unavailable real factories, and missing, unknown, extraneous, or adapter-mismatched
gate definitions fail at this seam before compilation. The named
`ResearchGraphRecipe.all_real()` factory is the only production-owned selection; the
internal compatibility constructor `ResearchGraphRecipe.create()` delegates only to
that fixed all-real factory and accepts no selection or mode argument.

Alternatives considered:

- Retain `fake_factory` as an optional production field: rejected because the
  production contract would still own a fixture implementation slot.
- Let `build_research_graph()` lazily import a catalog by a mode string: rejected
  because it reverses the dependency direction and makes fixture availability a
  runtime property of production.
- Depend on factory object identity to infer real versus fixture: rejected because it
  hides the capability decision and cannot describe an externally supplied adapter.

### 3. Keep fixture plans, routing, and gates in the fixture package

The fixture catalog will bind a deterministic scenario when it creates adapters and
fixture gate definitions.  Adapters and `FixtureSequenceRule` close over that scenario
and use the existing visit facts from state, so fixture plan data does not enter the
production checkpoint schema.  A changed fixture scenario therefore creates a new
fixture recipe rather than mutating a public `ResearchActionInput` or `ResearchState`.

Production removes `FakeFixturePlan`, `fixture_plan`, `terminal_fixture_marker`, and
fixture-only state ownership/schema entries.  Fixture routing, the old
`choose_fixture()` behavior, `FixtureSequenceRule`, and fixture gate definition
construction move under `src_fake`.  Real gate definition construction remains in
production under a name that does not imply fixture ownership.

The generic node state update currently named `node_update()` moves from
`engine.fake_control` to a neutral production state module and is renamed/documented
as a normal node update helper.  Real node imports are changed to this neutral helper;
the fixture package uses it through the public contract.  `engine.fake_control` and
production `engine/gate_fixtures` cease to exist.

Alternatives considered:

- Keep a `fixture_plan` extension field in `ResearchState`: rejected because it makes
  fixture control durable production state and allows a public checkpoint to carry a
  fixture selector.
- Move all helpers to a generic `utils` module: rejected by the structural policy and
  because it obscures ownership.

### 4. Separate public all-real assembly from injected test/demo assembly

Production provides an explicit all-real recipe factory.  `build_research_handlers()`
and the lazily created reflected `GraphHost` use that factory when no recipe is
supplied.  They never attempt to import a fixture package.  An explicitly supplied
recipe remains a generic `GraphHost` test/demo seam; it is validated before handler
registration and does not make the default host fixture-aware.

The fixture package provides the fixture recipe factory used by fake demos and tests.
It may import `ResearchGraphRecipe` from `runtime.research` solely to call the documented
generic composition seam `ResearchGraphRecipe.from_adapters()`; it must not call
`ResearchGraphRecipe.all_real()` or `.create()`, or import a `GraphHost`, action handler,
or control host. A mixed test recipe is assembled at its test composition root: it starts
with the fixture catalog's paired selections, overlays only the named production real
adapters, then rebuilds the gate selection from the final adapter choices: it replaces
fixture gates with matching real gates and removes a fixture gate when the selected real
adapter has none. It calls `from_adapters()` with the complete pairs and never reintroduces
an `implementation_modes` selector. Demo scripts
and fixture-backed local-session tools request the full fixture recipe only after their
child process has enabled `src_fake`; real demo scripts use the all-real production factory.
The local session tools remain fixed-profile standalone demo/operator surfaces, not public
composition roots. The fixture recipe is marked test/demo-only at its composition root so it
cannot be projected through the reflected public lifecycle.

This is one deep seam: callers choose one complete recipe at construction, while graph
selection, capability attachment, gate definitions, and validation remain internal.

### 5. Revise the public recipe namespace and treat old fixture sessions as legacy

The public all-real recipe gets a new fixed recipe revision and namespace domain.
Namespace derivation includes that fixed revision, so the former full-fixture public
namespace cannot be opened as the new graph.  The compatibility fingerprint continues
to validate a fixed recipe; it is never a selector.

When a current public operation encounters a binding from the retired fixture revision,
it rejects before opening a provider, sandbox, or graph.  Existing retained records
may still be inspected through their existing read-only path, but cannot resume,
cancel, migrate, or create a new lifecycle.  Fixture test/demo recipes use a distinct
non-public namespace revision to avoid collision with either public version. Current
control-result projection takes `implementation_mode` from the selected recipe; it
must not default to `full_fake`. The legacy `full_fake` value may be parsed only as
inspection metadata for a retired record, while a newly composed fixture recipe
projects `fixture` and the reflected public recipe projects `all_real`.

Alternatives considered:

- Reinterpret v1 checkpoints with all-real nodes: rejected because checkpoint state
  and adapter semantics differ, and it could execute a session under a new meaning.
- Automatically migrate v1 checkpoints: rejected because there is no reliable
  migration authority for fixture plan state or old adapter selection.
- Preserve the public fixture namespace and only change its default: rejected because
  an old identifier could still select an unintended implementation.

### 6. Keep the node-prompt review projection hidden, local, and untracked

**Verified current behavior.** `scripts/prompt_dump.py` obtains code-owned synthetic
`PromptCatalogCase` values from `graph.prompt_catalog` and renders them through the shared
`agents.phase_prompt.render_node_agent_prompt()` interface. Its current
`deerflow_research/node_prompts/` tree contains that deterministic output; no runtime path
loads those Markdown files. The prompt builders, shared renderer, and runtime bridge remain
the owners of prompt behavior, while the generated tree is only a review projection.

**Decision.** Replace that committed root with the explicitly local
`deerflow_research/.node-prompt-review/` workspace. The name says both what the files contain
and why they exist, while the leading dot keeps an optional generated review aid out of normal
source browsing. `deerflow_research/.gitignore` will ignore exactly that root; the old
`node_prompts/` tree will be removed from the index and
`openspec/governance/project-structure.toml` will no longer require either root to exist.

`make prompt-dump` will remain an explicit review command and will write only the hidden root.
`make prompt-dump-check` will continue to validate an already generated local tree without
writing it, including its bounded-path and stale-content protections. A missing local tree is a
clear precondition failure for that opt-in command, not a clean-checkout or CI failure. The fast
deterministic suite will retain source-level catalog-inventory, renderer, and temporary-tree
generation tests, but it will neither create nor require `.node-prompt-review/`; therefore
`UV_OFFLINE=1 make verify` remains valid on a clean checkout.

The local projection has no runtime consumer, API, checkpoint, or compatibility contract. It
can be deleted and regenerated at any time, and neither the Markdown nor its presence may
select a prompt, a tool posture, a graph route, or an agent action.

Alternatives considered:

- Keep a committed dot-prefixed tree: rejected because `.gitignore` does not hide tracked
  files, so it would retain both the distracting source-like surface and the committed-baseline
  claim.
- Move the canonical prompt source into a hidden directory: rejected because the existing
  graph builders and shared renderer are the executable owners and must remain discoverable in
  their ownership layers.

## Risks / Trade-offs

- [Fixture tests import a package unavailable in ordinary production installs] -> Test
  commands and fake demos explicitly add `src_fake`; a focused test proves that a
  production import and wheel do not resolve it.
- [A partial migration leaves a real module importing fixture control] -> AST
  architecture validation rejects production-to-fixture imports, `fake.py` node files,
  and the retired fake-control modules.
- [Fixture test coverage becomes less convenient because plans are recipe-bound] -> A
  compact fixture catalog factory accepts a deterministic scenario and returns a new
  recipe, keeping plan setup at one explicit composition root.
- [A mixed test recipe pairs a real adapter with the wrong or absent gate] -> The
  composition contract validates the complete adapter/gate pair before compilation;
  focused graph tests cover missing, extraneous, and mismatched definitions.
- [Public callers lose ability to resume old fixture runs] -> The old records remain
  read-only and return a bounded new-run/inspection outcome; this is intentional to
  protect semantic compatibility.
- [Packaging configuration accidentally expands later] -> Wheel-content and launch-path
  tests verify the explicit package list and absence of `src_fake` on real paths.
- [A prompt change no longer produces a committed Markdown diff] -> Explicit reviewers run
  `make prompt-dump` and inspect the hidden local projection; source-level inventory, renderer,
  and runtime-bridge tests retain deterministic correctness evidence without claiming that a
  local review workspace is a source-of-truth baseline.
- [A local reviewer checks stale output] -> `make prompt-dump-check` remains read-only and
  reports missing, stale, unsafe, or unexpected local paths; regenerating the ignored tree is
  the only recovery.

## Migration Plan

1. Add red tests for paired adapter/gate selection validation, package/import isolation,
   default all-real host construction, retired namespace behavior, and fixture-demo/local-session
   launch paths.
2. Add the fixture package/catalog and move deterministic adapters, plans, fixture gates,
   and routing there; remove production fake files and fixture state fields.
3. Refactor production registry, adapter selection, builder, recipe construction, and
   neutral state helper imports.  Update the reflected host to use the all-real recipe.
4. Revise checkpoint/session compatibility checks and public namespace revision; update
   test/demo hosts to inject fixture recipes explicitly.
5. Update packaging, Makefile/test import paths, structural registry/checker, public
   skill/Agent wording, specs, and evidence registries.  Run focused tests first, then
   the deterministic verification suite.
6. Replace the committed node-prompt catalog with the ignored `.node-prompt-review/` local
   workspace; update the dump/check command contract, source-level evidence, structural
   registry, documentation, and Git tracking before running both clean-checkout and explicit
   local-review verification.

Rollback is a code deployment rollback to the prior release for in-flight public v2
runs.  It does not reinterpret or migrate either public fixture v1 data or v2 real
data across recipe revisions; retained records stay inspectable under the release that
understands them.
