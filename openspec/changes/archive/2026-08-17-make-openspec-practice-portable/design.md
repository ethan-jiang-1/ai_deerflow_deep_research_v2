## Context

See `proposal.md` for motivation and the three deltas for required behavior.

Verified current state:

- `openspec/change-guidance/` is one Deep Research-specific tree with a root router,
  two root documents, and ten policy files; `check_change_guidance.py` combines
  portable-looking grammar with project paths, exact members, budgets, IDs, and local
  navigation checks.
- `openspec/product/deep-research.md` is the only current product entry, while
  `deep_research_harness/CONTEXT.md` owns the glossary and
  `project-structure.toml` owns exact structure.
- `check_change_guidance.py` is a declared local CLI; Program Focus and conditional
  review grammar are current Deep Research authoring contracts.
- No active OpenSpec change overlaps this scope at proposal time. `deerflow/` is a
  read-only gitlink boundary and is not an implementation source for this Program.

Approved target state:

```text
openspec/change-guidance/
├── README.md
├── core/
│   └── change-practice.md
├── profiles/
│   ├── workflow-control/
│   │   └── workflow-control.md
│   ├── node-agent/
│   │   └── node-agent.md
│   └── deerflow-downstream/
│       └── deerflow-downstream.md
└── local/
    └── deep-research.md

openspec/governance/
├── change_guidance_kernel.py
├── check_change_guidance.py
├── selected-change-closeout.py
└── selected-change-closeout.md

openspec/tests/governance/
└── test_*.py

openspec/product/
└── README.md
```

Completed state: this repository publishes a verified portable snapshot whose
neutrality, composition, links, and exact bytes are mechanically checked here.

## Goals / Non-Goals

**Goals:**

- Give every portable rule, local binding, exact path, product fact, and release fact
  one accountable owner and mechanically test the boundaries between them.
- Preserve current Deep Research authoring results and local CLI behavior through a
  reversible extraction followed by atomic document/path cutovers.
- Make the smallest useful portability promise: an allowlisted source snapshot proved
  by neutrality, composition, link, digest, and integration checks.
- Leave enough evidence that later deletion, adoption, upgrade, and source correction
  do not depend on reconstructing intent from commit history.

**Non-Goals:**

- A universal agent-workflow ontology, configuration schema, architecture checker,
  package, generator, remote include, automatic sync service, or compatibility policy.
- Runtime, graph, node, prompt, state, checkpoint, tool, provider, or lifecycle change.
- Moving the Deep Research glossary or making the product front door an authority.
- Cross-repository adoption work or claims about a future product.

## Decisions

### 1. Separate portable semantics from project composition

`core/`, selected `profiles/`, and `change_guidance_kernel.py` form the only portable
source. `change-guidance/README.md`, `local/`, `config.yaml`, product docs, source
specs/IDs, manifests, wrapper, tests, and evidence remain project-owned.

This creates a one-way dependency:

```text
portable core + enabled profiles + pure validator
                         ↓
             project-owned local composition
                         ↓
       project specs / structure / code / evidence
```

Portable content cannot import or link back to a source-local path. Local composition
may link to portable content and owning local sources but may not copy their prose or
exact inventories.

The repository dependency direction is one-way: `openspec/` is an upstream development
and governance framework that may inspect `deep_research_harness/`; the downstream
application SHALL NOT read, import, execute, or link OpenSpec content. Harness-owned
coding guidance therefore carries its complete application authoring route directly,
while OpenSpec links to that downstream contract for application facts. OpenSpec
governance tests live under `openspec/tests/governance/`, and Harness verification is
independently runnable without the OpenSpec tree.

Alternative rejected: move everything product-specific into `product/`. That would
make a navigation document a competing authority for structure, grammar, and runtime
facts rather than reducing coupling.

### 2. Use three independent profiles, not a product template

The profiles correspond to separable triggers:

| Profile | Portable jurisdiction | Explicit exclusion |
| --- | --- | --- |
| `workflow-control` | state/control placement, human decision, recovery, participant and terminal outcomes | no concrete state, route, retry, or permission |
| `node-agent` | bounded cognition, tool posture, candidate admission, repair/evidence review | no assumption every node uses an LLM or tools |
| `deerflow-downstream` | public upstream boundary, downstream-only change discipline, gitlink compatibility posture | no DeerFlow internals or source-browsing permission |

Project enablement controls which profiles exist in the selectable registry; per-change
triggers control which enabled policy obligations apply. Validation computes the union,
never a first-match result.

Alternative rejected: one `deerflow-agent-workflow` bundle. It would force LangGraph-
only adopters to accept DeerFlow rules and make node-agent concerns inseparable from
general control/recovery practice.

The current `node-edit-map.md` is a load-bearing semantic contract, not a filename to
preserve mechanically. Its target projection is the prominent
`profiles/node-agent/node-agent.md` first-read route. The cutover preserves classification
and this order: cognitive contract → prompt/context → structured output/feedback/
repair → deterministic proof and cognitive evaluation → deterministic handoff. It
also preserves the explicit non-model branch. This prevents two symmetric coding-agent
errors: modifying Python because it is found first, and turning deterministic/human/
wiring work into prompt work merely because the node can use a model.

### 3. Extract a pure evaluator behind a compatible wrapper

`change_guidance_kernel.py` accepts explicit proposal text and declarative grammar
schemas and returns structured violations. It performs no filesystem access, command
execution, manifest discovery, product loading, or wrapper import.

`check_change_guidance.py` remains the local CLI and owns:

- repository root and file loading;
- enabled profiles, canonical local policies, Program extensions, paths, and budgets;
- product, information-map, exact-member, link, and local operation checks;
- rendering structured kernel violations as the existing CLI's success/failure result.

S1 extracts only proposal/review grammar. S2 changes document topology and composition
after equivalence tests close, reducing rollback scope.

Alternative rejected: parameterize the current monolithic checker in place. Hidden
globals and repository traversal would remain an accidental portable API, and another
project could not distinguish reusable grammar from Deep Research policy.

### 4. Assign paragraph ownership before moving files

S2 begins with a paragraph-level ledger for every current guidance rule. Each row
records current source, target owner, portable/local classification, current consumers,
requirement owner, and retirement action. A target file cannot be populated until its
rows have exactly one owner; a source file cannot be deleted until all current inbound
links and checker/spec bindings have moved.

The cutover is atomic at the active-tree level: update core/profiles/local documents,
router, config, wrapper registry, specs, structure registry, entry links, and focused
tests in the same workstream, then delete old current policy paths. Git history and
archives retain history; compatibility documents do not.

Alternative rejected: copy first and deprecate later. Two editable policy trees would
make drift legal and leave no deterministic retirement point.

### 5. Keep product front door navigational and structure-neutral

`product/README.md` answers what product this is and where terminology, required
behavior, current facts, architecture, and evidence live. It does not repeat those
facts, select profiles mechanically, or declare an exact member schema.

S3 enumerates all current non-archive consumers before replacing
`product/deep-research.md`. The new file, all current links, checker bindings,
`project-structure.toml`, owning deltas, and negative fixtures change together; the old
file is deleted. Archive links are deliberately historical and are not rewritten.

Alternative rejected: add `product/instance.yaml`. The current repository already has
an exact structure authority, and one known adopter does not justify a second generic
binding schema.

### 6. Publish a digest-bound portable snapshot

The export allowlist contains only:

- all `openspec/change-guidance/core/**` files;
- all files for each selected profile under
  `openspec/change-guidance/profiles/<profile>/**`;
- `openspec/governance/change_guidance_kernel.py`.

The manifest records source repository/revision, snapshot date, selected profiles,
relative paths, and SHA-256 per file. Export walks from the allowlist rather than
copying `openspec/` and deleting a denylist afterward. A portable Markdown link must
resolve inside the selected allowlist or name a target-local owner role without a
source path.

The snapshot promises exact bytes and a bounded allowlist. Any future adopter owns its
product front door, router, config, local extensions, wrapper, specs/changes,
structure/ID governance, tests, and evidence. This Change creates no automatic update
or package-compatibility promise.

Alternative rejected: package/generator/submodule distribution. It would introduce
versioning, release, rollback, consumer inventory, and compatibility contracts before
real repeated adoption shows which mechanism is justified.

### 7. Use guards that prove sensitivity and deletion closure

| Boundary | Guard | Planted negative | Passing restoration |
| --- | --- | --- | --- |
| Kernel neutrality | recursive portable literal/path/ID scan plus neutral fixture | add source product/path/ID | restore exact file and pass |
| Pure validator | direct unit fixture | attempt filesystem/subprocess/wrapper dependency | restore pure input and pass |
| Profile composition | local wrapper fixtures | omit one of two triggered reviews | restore review and pass |
| Profile optionality | core-only/disabled fixtures | select disabled policy | remove selection and pass |
| Node authoring semantics | profile semantic-parity fixture | omit/reorder one stage, infer from first file/model-call presence, or delete the non-model branch | restore all ordered stages and both classification paths, then pass |
| Single prose owner | ownership/link ledger and exact tree guard | leave old policy or duplicate paragraph owner | remove duplicate and pass |
| Product front door | exact member/link/budget/owner-route checks | stale link, extra member, missing owner route | restore registered entry and pass |
| Structure authority | architecture guard plus review | duplicate exact structure fields in product/local schema | remove competing fields and pass |
| Export identity | manifest/digest verifier | tamper one portable file or include denylisted path | regenerate intentional digests or restore bytes and pass |
| Upstream scope | metadata-only git evidence | changed gitlink pointer or nested worktree | restore observed baseline before closeout |

Automated guards own syntax, membership, and deterministic invariants only. Semantic
owner/profile fitness is an explicit review event recorded in the Change evidence,
with the workstream owner escalating unresolved conflict to Program decision authority.

## Risks / Trade-offs

- **Portable rules become vague after removing local examples** → Require neutral
  fixtures for each profile; move only bindings, not the core decision question or
  negative-path obligation.
- **The pure API accidentally mirrors Deep Research grammar** → Test core-only and
  differently named local fields; reject source literals/IDs recursively; keep Program
  Focus in local composition.
- **Atomic document migration is a large diff** → Complete S1 separately, freeze the
  ownership/consumer ledger, execute S2 as one workstream, and provide a whole-tree
  rollback rather than aliases.
- **Clean path cutover breaks an unknown link** → Block S2/S3 until current non-archive
  consumers are enumerable; use planted stale-link fixtures and forward-fix or restore
  the former single entry.
- **Portability is overclaimed** → Limit the claim to the exact kernel/profiles,
  neutrality rules, and snapshot process proved here; do not claim another product
  has adopted it.
- **Manual semantic review is mistaken for mechanical proof** → Evidence labels
  fixture claims and human decisions separately; no keyword
  scan certifies semantic ownership.

## Migration Plan

1. **S0 — baseline/admission:** capture current active changes, checker contracts,
   proposal grammar, conditional reviews, exact guidance/product consumers, structure
   and requirement owners, glossary links, and gitlink metadata. Block on unknown
   consumers.
2. **S1 — portable validation:** plant coupling/purity/ID negatives; extract pure
   grammar evaluation; delegate from the compatible wrapper; register the module and
   direct tests. Roll back delegation if current outcomes differ.
3. **S2 — guidance cutover:** finish the ownership ledger; create exact core/profile/
   local trees; compose enabled profiles; update wrapper/config/specs/registry/entries/
   tests; delete old policy paths; prove multi-profile, disabled-profile, duplicate-
   owner, stale-link, and current-compatibility cases.
4. **S3 — product cutover:** inventory current links; create `product/README.md`;
   update all current consumers, specs, registry, checker, and fixtures; delete
   `deep-research.md`; preserve glossary owner and archive text.
5. **S4 — snapshot:** run all source verification and planted negatives; generate
   allowlist/denylist/digests and source evidence; publish the fixed verified snapshot.
6. **Closeout:** compare scope, diff, ownership, deletions, guards, and snapshot
   evidence; then archive this Change as one unit.

No runtime data moves, so there is no dual write, shadow state, or data rollback. Path
recovery restores the last passing single current entry or forward-repairs to the one
approved target; it never leaves permanent old/new aliases.

## Open Questions

None. Adoption by another product is future work outside this Change.
