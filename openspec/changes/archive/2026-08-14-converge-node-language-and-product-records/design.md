## Context

See [proposal.md](proposal.md) for the motivation and frozen program boundary.

Verified current facts establish the two workstreams' starting points:

- `NodeExecutionRequest` defaults `capability_binding` to `legacy` while accepting
  a nullable capability ref. All production graph request builders already pass
  `required` plus an explicit ref, so the remaining dual mode is internal residue.
- The prompt renderer validates the local capability before the bridge resolves
  tools or a model. The bridge currently treats absent capability policy as a
  permitted branch, so the dual-mode branches must be removed together.
- The root package exports only `__version__` and `deep_research_tool`; package
  metadata, documentation, and entry points make no support promise for the
  request, renderer, factory, or bridge module paths. This is an application-internal
  clean break, not a public Python API migration.
- `CONTEXT.md` is the product glossary, but six tail sections duplicate decisions
  already held by ADR 0011 and 0022-0026, while `Local-First Deployment` describes
  dormant ADR 0002/0008 direction. Current glossary definitions remain the route
  for distinct Evaluation Run Workspace, Evaluation Run Bundle, Cognitive Evaluation
  Review / Review Record, Evaluation Run, and product Run Bundle meanings.

The only external framework remains `deerflow` as an imported host dependency. No
decision in this design requires reading or changing its source.

## Goals / Non-Goals

**Goals:**

- Make the typed request ref the single capability-selection fact and preserve the
  existing agents-loader and bridge admission chain.
- Align current product, model-visible, runtime, requirement, test, and registry
  language through one bounded terminology table.
- Return durable decision, required behavior, and routing statements from the
  glossary to their existing ADR, spec, and policy owners without losing a current
  term or negative guard.
- Leave deterministic proof at the lowest responsible seams and make the two
  workstreams independently recoverable within one archive transaction.

**Non-Goals:**

- Creating a public facade, a compatibility alias, a versioned migration, or a
  third-party Python support promise for the retired internal names.
- Altering node cognitive quality, graph lifecycle/state writers, provider/tool
  policy, retry, terminal outcomes, or the existing 20-branch and 11-node evidence
  denominators.
- Changing evaluation-record retention/import boundaries, executing paid evaluation,
  rewriting ADR/archive/backlog history, or modifying the DeerFlow gitlink.

## Decisions

### Use one mandatory ref and one pre-resolver admission chain

`NodeExecutionRequest` will require a `NodeAgentCapabilityRef` and no longer carry
`capability_binding`. A missing ref is rejected by typed request construction. The
renderer is then the first execution-adjacent step: it loads and validates the ref,
resource, and metadata before it returns final prompt text. The bridge receives only
that validated projection, checks its existing posture/window agreement, and only
then resolves tools, resolves a model, or constructs an embedded agent.

```
graph builder
    -> required NodeAgentCapabilityRef
    -> renderer validates ref/resource/metadata
    -> bridge validates existing posture/window
    -> tools, model, embedded node-agent
```

Invalid, unknown, missing-resource, and package-mismatched refs all terminate at the
left half of this chain. No fallback capability, optional renderer branch, or bridge
path for an absent projection remains. The safe failure stays owned by the existing
bridge/graph failure path; the change neither adds a retry nor introduces a new
lifecycle result.

`package-mismatched` is limited to the existing ref/resource boundary: a package
outside the node namespace fails typed construction; a namespace-rooted but
unimportable package, missing resource, or resource whose metadata ID differs from the
ref fails in the renderer. The existing source-backed catalog remains the authority for
each production builder's exact ref/package/resource tuple. The bridge does not derive
a second node-to-package lookup because that would add a new runtime control fact.

The alternative, retaining a `required` discriminator as a future extension point,
is rejected because ref presence already determines admission and a second fact
creates an impossible combination that requires additional validation and tests.

### Rename identity by responsibility, not by blanket text replacement

The term table governs each current use. It prevents the product name, model-visible
program, and deterministic mechanism from becoming synonyms while preserving generic
workflow-phase vocabulary that is not an identity.

| Term | Current use after this change | Owns / does not own |
| --- | --- | --- |
| `LLM-Bearing Node` | Product-facing identity for a graph node with a bounded model role | Identifies the product role; does not own routes, state, or lifecycle |
| `Node Cognitive Control Program` | Model-visible static local policy and its reviewed prompt composition | Guides model cognition; does not grant tools, candidate admission, or graph authority |
| `node-agent` | Runtime/governance mechanism, typed bridge/capability naming, and policy route | Enforces configured execution boundaries; does not become product identity |
| `phase` | Logical workflow sequencing only when it is not an agent identity | Retained where it describes a graph/lifecycle phase, not a product or runtime actor |

The apply work renames current policy-resource title/text, renderer module and
symbols, factory symbol/name, middleware stop symbols, bridge imports/error labels,
current tests, generated/registry inputs, active main-spec requirement names and
bodies, and the current prompt-review documentation. `PHASE_AGENT_NAME` becomes a
node-agent identity with a new internal runtime name; the root
`deep_research_tool` export remains unchanged. Archived material, delta rename
provenance, the explicit retired-term supersession note in
`openspec/agent-charter/concepts.md`, and intentional generic phase wording are
excluded from the residual-current scan.

OpenSpec requires a modified requirement to retain every accepted scenario title.
The exact `WFO-001` title `A direct phase preserves a closed phase-agent stop` is
therefore a validator-compatible legacy scenario identifier, not current product or
runtime terminology. Its body uses `node-agent stop`; no other active requirement
body, registry row, source symbol, policy resource, or current documentation may use
the retired identity. `RER-009` retains all of its scenario titles and replaces its
sole `phase-agent stop` body reference with `node-agent stop`.

The alternative, replacing every word `phase`, is rejected because graph phases are
not the retired identity and a broad replacement would alter unrelated lifecycle
language. The alternative, preserving `Phase Agent` as an internal alias, is rejected
because it keeps a second current identity and weakens the convergence proof.

### Preserve current evidence while retiring migration narration

The capability and evidence specs retain their existing requirement IDs, exact
20-branch catalog/evidence joins, resource validation, static-policy boundary, and
required-versus-forbidden tool posture. Requirement headings are renamed where they
carry a current retired identity; their existing scenarios remain as fail-closed
coverage even when the current requirement text no longer describes a migration
cohort. This follows the OpenSpec modified-requirement rule that a replacement must
carry every prior scenario rather than silently dropping negative evidence.

Apply updates the accepted purposes/requirement names and the requirement/evidence
registries together with their `@impl` and test links. The required post-change scan
distinguishes current owned prose from OpenSpec `FROM` provenance and archive history;
the latter is evidence-only and does not recreate a current product identity.

The alternative, deleting historical scenarios while changing the requirement text,
is rejected because the strict OpenSpec validator correctly treats that as an
unreviewed loss of behavior proof. The alternative, using new requirements only,
is rejected because it would duplicate still-current behavior and disrupt established
coverage ownership without changing the actual runtime contract.

### Delete glossary residue only after a paragraph-to-owner ledger closes

The glossary workstream first records the exact retained owner and current route for
each removable section:

| `CONTEXT.md` material | Retained authority before deletion |
| --- | --- |
| People Initiate Evaluation Review | ADR 0022 and `cognitive-evaluation-suite` |
| Reviews Are Separate Immutable Records | ADR 0023 and `cognitive-evaluation-suite` |
| Review Records Are Traceable | ADR 0024 and `cognitive-evaluation-suite` |
| Rubrics Are Case-Specific Review Authorities | ADR 0025 and `cognitive-evaluation-suite` |
| Evaluation Control And Run Data Are Separate | ADR 0026 and its current status/route |
| Cognitive Control Program Is The First Modification Seam | ADR 0011 and `local-context` policy |
| Local-First Deployment | ADR 0002/0008 historical status; the root README's Dedicated Agent current product route; and the separate Cognitive Evaluation documentation route |

If that ledger finds an actual unique current rule or a missing current route, the
workstream adds it to the listed owner before deletion. It does not modify ADR
historical decision text/status merely to make the ledger pass. `CONTEXT.md` keeps
the current canonical definitions and every `_Avoid_` block, including the distinct
evaluation and Run terms. Generated records remain projections of their existing
sources, and archive/completed-backlog terms remain history rather than current
authority.

The alternative, shortening the glossary by deleting all related language at once,
is rejected because it could collapse Evaluation Run Bundle and product Run Bundle
or strand the current route to a decision. Creating a new permanent terminology
registry is rejected because the glossary, ADRs, specs, and charter already have
separate declared responsibilities.

### Program closure recovers by workstream but archives once

`node-contract-language` is complete before `glossary-records` removes any record
that uses the approved term table. A failure in the first workstream blocks the
second. A failure in the second may be repaired in its documentation/record writer
scope or rolled back with its dependent changes; neither workstream may archive
alone. The program's only authority is this ordering and closure decision. Runtime
facts, package resources, graph admission, ADR decisions, and record ownership stay
with their existing owners.

## Risks / Trade-offs

- [A test fixture still constructs a request without a ref] -> Establish the missing-
  ref construction test first, inventory all test and production constructors, and
  use the catalog join to prove all current branches are explicit.
- [A malformed ref reaches a resolver through an optional renderer branch] -> Add
  bridge tests with tool/model/factory spies and retain a zero-construction assertion
  for invalid, unknown, and package-mismatched refs.
- [A name replacement changes an unrelated lifecycle phase or leaves a live identity]
  -> Use the term table, a current-surface inventory, and an allowlist limited to
  archive/provenance/generic-phase uses, the charter supersession note, and the exact
  validator-compatible `WFO-001` scenario title; review each remaining match before
  closeout.
- [A glossary deletion loses a real evaluation distinction] -> Require the
  paragraph-to-owner ledger plus retained-term and `_Avoid_` checks before deleting
  any tail section or dormant entry.
- [A generated projection becomes stale after record changes] -> Run its existing
  freshness/check adapters and fail the workstream on stale, extra, or missing output.
- [Historical prose is mistaken for current drift] -> Keep archives and completed
  backlog read-only, exclude them from current-surface scans, and verify no new
  current route points back to them as authority.

## Migration Plan

1. Re-read this design, both workstream review records, the selected policies, source
   facts, and current tests. Add an ordinary unchecked task for every actionable
   scope or authority finding before target edits.
2. Add red deterministic constructor, renderer, bridge, catalog, and current-language
   tests. The bridge fixtures prove invalid admission reaches no tool resolver, model
   resolver, or embedded-agent construction.
3. Remove the request dual mode, update every production and test constructor, then
   simplify renderer/bridge paths to the mandatory validated projection. Run the
   focused request/prompt/bridge/catalog/evidence suites before renaming terminology.
4. Apply the term table across current policy resources, application-internal symbols,
   tests, current prompt-review documentation, requirement/evidence registries, and
   the six affected main specs. Regenerate and verify any owned projection; preserve
   only the declared generic-phase, historical, and strict-validator exclusions.
5. Build and verify the glossary paragraph-to-owner ledger. Add any demonstrably
   missing current route to its existing owner, then delete only the seven approved
   glossary records while retaining all definitions and `_Avoid_` entries.
6. Run focused tests and source/document scans, then the complete deterministic,
   governance, strict OpenSpec, and Git/submodule-scope evidence named in tasks.
   On any failure, forward-repair only the owning workstream or roll it back as the
   Program Focus requires; leave the entire change active until both close.
