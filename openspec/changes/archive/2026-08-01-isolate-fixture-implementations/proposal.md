## Why

The production source tree currently contains deterministic fake node implementations and
shared runtime helpers named for fake control.  That makes fixture behavior deployable with
the production package, lets real nodes depend on fixture-named code, and permits an omitted
or empty implementation map to select an all-fake lifecycle at a public entry point.

Fixture behavior needs an explicit source, packaging, and composition seam: production code
must not import or ship it, while tests and credential-free demos must retain a deterministic
full-fixture lifecycle.  The reflected tool must construct a real recipe explicitly and must
not reinterpret checkpoints created by the former fixture default.

## What Changes

- Add a `src_fake/deerflow_deep_research_fixtures/` source root with a distinct Python
  package name, complete deterministic fixture adapter and gate catalogs, and a mirrored
  logical-node layout.
- **BREAKING** Remove fake factories and fixture-only helpers from the production
  `deerflow_deep_research` package.  Production node specs expose real adapters only; tests
  and demos compose fixture adapters through an injected catalog.
- Make recipe construction and graph building explicit: omitted adapter or gate selections
  select no implicit fixture recipe, and empty, incomplete, or mismatched paired selections
  fail before graph compilation.
- Make the reflected `deep_research` control host explicitly all-real.  Fixture recipes are
  available only to test and demo assembly roots, with real-runtime readiness failures
  projected through the existing typed lifecycle outcome path.
- Give the public real recipe a distinct checkpoint namespace/revision from the retired
  full-fixture public recipe.  Existing fixture checkpoints remain inspection-only and are
  never used to select or run a fixture adapter.
- Move shared state-update mechanics out of `engine.fake_control`; keep fixture routing and
  fixture-plan interpretation in the fixture package.
- Update source-layout validation, build/test/demo and fixture-backed local-session commands,
  public skill/Agent guidance, and deterministic evidence to enforce the new seam.
- Replace the committed `deerflow_research/node_prompts/` tree with the ignored, on-demand
  `deerflow_research/.node-prompt-review/` workspace. The latter remains a code-derived
  review projection only; source prompt builders and the shared renderer remain authoritative.

## Capabilities

### New Capabilities
- `fixture-source-isolation`: Defines the separate fixture source package, one-way import and
  packaging rules, and explicit fixture catalog composition for tests and demos.

### Modified Capabilities
- `project-structure`: Changes the node package grammar and registers the production and
  fixture source roots plus their enforceable import/package rules, and removes the generated
  prompt projection from the tracked structural inventory.
- `node-prompt-catalog`: Moves the deterministic prompt projection from a committed tree to an
  ignored hidden local review workspace while retaining source-level catalog and renderer proof.
- `research-graph-lifecycle`: Makes recipe selection explicit, preserves deterministic fixture
  workflows outside production, and changes the reflected lifecycle default to all-real.
- `runtime-integration`: Defines explicit public all-real host assembly and protects new
  lifecycle dispatch from retired fixture checkpoint namespaces.
- `research-session-lifecycle-binding`: Retains recipe compatibility as validation only and
  makes retired fixture sessions inspection-only rather than adapter-selection inputs.
- `demo-pipeline`: Makes fake demos explicitly load the fixture catalog/source root while real
  demos remain all-real.
- `deployment-configuration`: Updates the public skill and dedicated Agent from a
  full-fixture control surface to an honest real-research entry surface.

## Change Focus

- **Primary module / causal owner:** `deerflow_research/src/deerflow_deep_research/graph/implementation_map.py` and its node-adapter selection seam.
- **Question:** How can the graph select real or deterministic fixture adapters without
  shipping fixture implementations in the production package or allowing an implicit fixture
  recipe at a public composition root, while keeping the code-derived node-prompt review
  projection reproducible without presenting it as a tracked source-like tree?
- **Necessary adjacent/external contracts:** `project-structure` answers the two-source-root,
  package, import grammar, ignored-root, and structural-registration rules;
  `runtime/research.py` and `runtime/control.py` answer explicit recipe assembly and public
  checkpoint compatibility; `runtime/session_lifecycle_binding.py` answers read-only treatment
  of retired fixture sessions; `demo-pipeline` answers how credential-free demos load fixtures
  without widening production imports; `deployment-configuration` answers the public skill and
  Agent outcome contract; `node-prompt-catalog` answers the generated projection's
  source-of-truth and local-review boundary.
- **Evidence seam:** graph recipe-composition contracts for missing/empty/mismatched
  adapter-gate selections and injected fixture catalogs; architecture checker violations for
  production-to-fixture imports and wheel contents; reflected lifecycle tests with a real
  recipe and a retired-fixture namespace; scripted fixture-demo and local-session command
  tests using only the fixture source root; and prompt-catalog source/render tests plus ignored
  local-review-root and architecture-registry contract tests.
- **Not in scope:** changes under `backend/` or `frontend/`; new model roles, tool policies,
  graph topology, real-research quality claims, automatic checkpoint migration, or a public
  caller-controlled recipe/mode argument; prompt semantic changes, runtime prompt selection,
  or a second prompt authority.
- **Triggered charter policies:** authority-and-projections, change-admission, workflow-outcome-review

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Empty, incomplete, unknown, or mismatched adapter/gate selection | implementation selection | composition root supplies one complete named recipe; no fallback | graph is not compiled or invoked | correct the fixed assembly recipe | implementation-map contract tests |
| Production code imports or wheel includes fixture code | project-structure checker/build metadata | no runtime recovery; source/build validation fails | package/test build rejected | remove the reverse import or fixture package from production build | architecture-checker and wheel-content tests |
| Public all-real entry lacks a required model, tool, or storage prerequisite | existing typed real-node/runtime outcome owner | existing bounded preflight/outcome path; no fixture substitution | typed unavailable or blocked result, according to the owning lifecycle contract | configure the missing prerequisite and start a new run | reflected runtime test with a fake missing capability |
| Retired full-fixture checkpoint is encountered from the public real recipe | recipe namespace/compatibility owner | no adapter selection or automatic migration | inspection-only legacy result; no resume under the real recipe | inspect legacy metadata or start a new real run | namespace and lifecycle compatibility tests |

## Impact

- Production package layout, `NodeSpec`, graph recipe/builder construction, public tool host,
  checkpoint namespace handling, and architecture validation change.
- Test and demo commands gain an explicit fixture-source import path; production wheel contents
  exclude `deerflow_deep_research_fixtures`.
- Node-prompt review output becomes an explicit, ignored local workspace rather than a committed
  diff or a required checkout path; deterministic source-level rendering and inventory evidence
  remains in the standard gate.
- Existing full-fixture public lifecycle sessions are deliberately not resumed by the new
  all-real public recipe.  No user-controlled recipe selector or upstream DeerFlow change is
  introduced.
