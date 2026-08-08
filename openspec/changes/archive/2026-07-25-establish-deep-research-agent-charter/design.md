## Context

Deep Research is owned by `agent/`, but it is developed inside a much larger
DeerFlow checkout. The root guides correctly describe upstream ownership and
boundaries. They cannot also be the concise product constitution for this
downstream agent, and they are intentionally out of scope for modification.

`agent/AGENTS.md` already owns downstream navigation, structure, ownership, and
testing guidance. Its first substantive section is a generated structural contract,
so it does not currently give a contributor a short instruction for selecting one
primary module and the smallest relevant context. Existing OpenSpec governance
policies cover structure and test evidence, but no permanent source says where Deep
Research's durable principles, recurring design rules, observable requirements, and
current runtime facts belong.

The existing module guide is 463 lines and its generated path inventory alone is
153 lines. `openspec/config.yaml` is 380 lines of default authoring context. Both
surfaces are read before a coding agent can determine whether their detailed facts
apply, which reverses their intended job as information maps. `agent/README.md` now
has an early reading map, but its remaining 471 lines still mix runtime architecture,
local operations, and test-evidence reference. A policy must prevent entry surfaces
from becoming project manuals rather than merely adding navigation above one.

The retired `add-agent-interaction-charter` draft captured one important symptom:
participant-facing outcomes need to be useful both to people and to other AI
consumers. This design keeps that concern, but makes it one component of a broader
Deep Research charter rather than a competing charter.

Constraints:

- `agent/` is the product boundary. `backend/`, `frontend/`, and root guidance are
  upstream facts and constraints, not local design ownership.
- Root `AGENTS.md` and `CLAUDE.md` remain unchanged.
- A charter or policy never creates runtime state, permissions, graph routes,
  schemas, retries, or claims about current behavior. Owning capability specs and
  executable contracts retain that authority.
- The solution must help a contributor reduce context, not create several new
  documents that all must be read for every change.

## Goals / Non-Goals

Goals:

- Give every Deep Research contributor one durable, project-owned place to find
  the product's design posture and decide where a new rule belongs.
- Give Codex and Claude Code the same local module-routing guidance without
  maintaining two divergent copies.
- Make `agent/AGENTS.md` a module attention switch before its detailed structure
  material, without changing the root guides.
- Preserve a consistent contract for both human participants and AI consumers:
  both receive projections of the same authoritative facts, but neither is asked to
  infer control state from prose or diagnostics.
- Turn the minimum local context into a short, reviewable Focus Card and validate
  its shape deterministically for active changes.
- Make context expansion causal and reversible: an adjacent module or upstream
  interface enters scope to answer a named question, not because it might be useful.
- Give `agent/AGENTS.md`, `agent/CLAUDE.md`, `agent/README.md`, and
  `openspec/config.yaml` distinct reader roles, early routing anchors, and
  line-count-first budgets with visible early warnings.
- Decompose the human/operator README into a compact entry page and focused docs so a
  reader opens only the architecture, local-operation, or testing reference needed
  for the present question.
- Keep the exact structural inventory in its machine-readable registry while making
  the generated module-guide block a compact locator rather than a second inventory.

Non-goals:

- Replacing capability specifications, runtime contracts, operational runbooks, or
  the three existing control/evidence/content authorities.
- Adding a generic AI governance framework, a second state machine, or a new
  user-facing product surface.
- Changing DeerFlow configuration, upstream source, graph behavior, provider
  behavior, checkpoints, sandbox artifacts, or root guidance files.
- Proving that a language model has read a document. The enforcement boundary is
  discoverability and change-admission shape, not hidden model cognition.

## Decisions

### 1. One charter tree under OpenSpec governance, scoped to `agent/`

The permanent home will be:

```text
openspec/governance/agent-charter/
  README.md
  charter.md
  policies/
    local-context.md
    authority-and-projections.md
    participant-outcomes.md
    control-and-recovery.md
    change-admission.md
    agent-information-map.md
```

`README.md` is the route map, not a second charter. It tells a contributor which
single policy applies to the present task and where a proposed rule belongs:

| Need | Canonical home |
|---|---|
| Stable cross-capability project principle | `charter.md` |
| Repeated design/admission rule with a narrow trigger | `policies/<topic>.md` |
| Observable product behavior, command, schema, or permission | owning capability spec and delta |
| Operator procedure or incident steps | a scoped operational document/runbook |
| Current execution fact | typed runtime state, ledger, sandbox content, code, or tests owned by that fact |

This uses the existing `openspec/governance/` home rather than a top-level
`openspec/policies/` tree, because the repository already treats that directory as
the discoverable extension point for project-wide OpenSpec governance. It avoids
making an `agent/CHARTER.md` that is easy for an OpenSpec author to miss, while
`agent/AGENTS.md` supplies the short local pointer for source work.

`agent/CLAUDE.md` is a compatibility entrypoint, not a second module guide. It uses
the repository's established `@AGENTS.md` import convention so Claude Code receives
the same local routing, exclusions, and Focus Card rule that Codex reads from
`agent/AGENTS.md`. The authoritative local prose remains in `AGENTS.md`; the thin
entrypoint prevents drift without attempting to replace the unchanged root guides.

Alternatives considered:

- Edit root `AGENTS.md` / `CLAUDE.md`: rejected because they own broader DeerFlow
  orientation and must remain untouched.
- Add several nested `AGENTS.md` files: rejected because path-specific fragments
  would increase discovery work and make the source of local principles ambiguous.
- Keep only a UX policy: rejected because authority, recovery, and bounded context
  are equally necessary to an agent-facing system.

### 7. Entry documents are bounded information maps with line-count budgets

The charter gains an `agent-information-map.md` policy for the four entry surfaces
that otherwise compete to explain the product. It assigns one primary reader and
job to each surface:

| Surface | Primary reader and job | Not its job |
|---|---|---|
| `agent/AGENTS.md` | Coding agent: choose the smallest local implementation/spec/test context | Product handbook, live-status report, exact path inventory, or command catalog |
| `agent/CLAUDE.md` | Claude Code: import the one authoritative coding-agent guide | A second instruction set or a prose explanation of the product |
| `agent/README.md` | Human/operator: introduce the product, offer quick start, and route deeper reading | Detailed architecture, operations, or test-evidence reference |
| `agent/docs/README.md` | Human/operator: select one task-scoped document | A second product overview or full document dump |
| `agent/docs/runtime-architecture.md` | Human/operator: inspect downstream runtime and authority boundaries | Operations or test execution instructions |
| `agent/docs/local-operations.md` | Operator: run profiles, diagnostics, and retained-session workflows | Runtime authority or coding-agent guidance |
| `agent/docs/testing-and-evaluation.md` | Contributor/operator: inspect test selection and evidence posture | The enumerable test registry or runtime behavior authority |
| `openspec/config.yaml` | OpenSpec author: state project boundary, truth discipline, and authoring route | Full DeerFlow architecture, runtime facts, roadmap, or design history |

Line count is the deterministic maintenance signal because it represents the amount
of default attention a reader must spend. The charter checker reports a warning before
rejecting a hard budget:

| Surface | Warning | Failure |
|---|---:|---:|
| `agent/AGENTS.md` | 120 lines | more than 160 lines |
| `agent/CLAUDE.md` | 10 lines | more than 12 lines |
| `openspec/config.yaml` | 140 lines | more than 180 lines |
| `agent/README.md` | more than 200 lines | none |

`agent/README.md` must place `## Reading Map` within its first 80 lines and route to
the docs index plus the three focused documents. The policy uses no word-count quota:
prose quality remains a review concern, while the checker keeps default-context size
visible and bounded. Each surface must link out to the authoritative detail instead of
duplicating it.

### 8. The generated structure block becomes a locator, not an inventory

`project-structure.toml` remains the exact machine-readable path inventory and the
architecture checker remains its authority/enforcement boundary. The checker will
render a compact block into `agent/AGENTS.md` containing only the registry path,
source root, test root, ownership-layer grammar, and validation command. It will not
repeat every required path. This keeps a coding agent's first read short while
retaining deterministic completeness checks in the registry.

### 9. The human README becomes a shallow entry page

The root README will retain only product orientation, the entry-point table, a short
requirements/setup path, a small high-frequency command set, and `## Reading Map`.
It will not retain detailed runtime, profile, retained-session, or test-evidence
reference material simply because those topics are relevant to some operators.

`agent/docs/README.md` will route readers to three focused documents:

| Question | Document |
|---|---|
| How do downstream graph, checkpoint, evidence, and sandbox authorities fit together? | `runtime-architecture.md` |
| How do I run profiles, demos, diagnosis, and the local workbench? | `local-operations.md` |
| How are deterministic, live, and release tests selected and interpreted? | `testing-and-evaluation.md` |

The move preserves existing factual content and links rather than creating a second
architecture or operations authority. The charter checker will validate only the
root-map and docs-index links plus the lower README warning threshold; the documents
remain human-facing reference, not default coding-agent context.

### 2. A small focus gate, not a request to read the whole project

The human-authored beginning of `agent/AGENTS.md`, before its generated structure
block, will link to the charter index and prescribe this local lookup order:

1. identify one primary causal module and current capability spec/delta;
2. read the closest implementation and lowest responsible test seam;
3. name only the adjacent modules and DeerFlow public interfaces that the local
   change actually depends on, together with the question that admits each one;
4. expand beyond those sources only to resolve a named interface, authority,
   compatibility, or observed-failure question; and
5. return to the primary module when the question is answered.

Codex reads this local guide directly. Claude Code reaches the identical content
through `agent/CLAUDE.md` importing `AGENTS.md`; neither agent receives a separate
local policy branch.

The gate rejects repository-wide orientation, searching for analogous implementations,
and a possible future use as reasons to read another source. Those activities are not
automatically wrong, but they need to be recast as a concrete question tied to a named
contract. If ownership remains ambiguous after the local spec, implementation, and
test seam, the contributor stops and clarifies the Focus Card rather than treating a
wider scan of `backend/`, `frontend/`, root material, or sibling changes as a way to
discover an owner.

Each active proposal will contain this exact, short `## Change Focus` card:

```md
- **Primary module / causal owner:** ...
- **Question:** ...
- **Necessary adjacent/external contracts:** ...
- **Evidence seam:** ...
- **Not in scope:** ...
```

The module guide will include this compact choice table before the generated
structure details. It is a routing aid, not a replacement for the existing ownership
section:

| Change's central question | Start with this primary owner |
|---|---|
| Typed meaning, invariant, or pure data contract | `domain/` |
| Deterministic rule, validation, gate, or retry policy | `engine/` |
| Bounded model role, prompt, middleware, or structured result | `agents/` |
| Phase composition, node routing, or graph capability injection | `graph/` |
| DeerFlow binding, trusted context, I/O, persistence, or lifecycle adapter | `runtime/` |
| Presentation command or docs that only projects an existing result | its adapter/doc, plus the named owning result contract |

For a cross-layer patch, the card names the module that owns the semantic decision,
not merely the first adapter file that happens to change. Other layers are listed as
adjacent contracts and are read only as far as that interface requires. A non-`none`
adjacent/external entry is an admission record, not a reading wishlist: it names the
contract and the decision it must answer. Newly discovered necessary contracts update
the card before the scope grows; resolving a question does not create a standing reason
to keep unrelated host code in context.

`openspec/config.yaml` will require the card for future authoring. A small
zero-dependency checker will validate its existence and field shape in active
changes, along with the charter's permanent pointers and stable context-expansion
anchors in the local policy and module guide. The checker deliberately does not decide
whether a named question is semantically sufficient; review and the owning spec retain
that judgment. The existing active provider-recovery proposal will be given the card
as part of this migration.

### 3. Separate authority from communication

The charter will state the following source hierarchy without redefining its owners:

1. approved capability specs define required behavior;
2. one active owning delta defines pending behavior;
3. code, typed contracts, checkpoint/ledger/content authorities, and tests establish
   current execution facts and conformance evidence;
4. the charter and policies guide design/admission only;
5. summaries, CLI/TUI wording, diagnostics, and retained projections communicate
   facts but never become a competing control authority.

`authority-and-projections.md` applies when an implementation adds a record,
summary, status view, diagnostic, or recovery surface. It requires the change to name
the existing owner rather than create a shadow record just because a presentation
needs convenience.

### 4. Treat human and AI participants as first-class consumers

`participant-outcomes.md` requires participant-facing capability changes to design
both projections from shared typed facts. Human output answers what happened, why it
matters, and the nearest legal action. AI-facing output provides stable bounded
fields/enums so another agent need not parse prose. Both projections must preserve
safe disclosure boundaries; neither receives secrets, raw provider content, prompt
text, host paths, or an invented recovery action.

The policy names expected dimensions such as outcome, owner/phase, category,
retry/recovery disposition, safe correlation reference, and allowed action. It does
not introduce a universal schema: the owning capability decides which fields exist
and their exact type.

### 5. Recovery is a bounded, owned control concern

`control-and-recovery.md` establishes the design posture for transient failure:
retry only where the owning phase has an explicit bounded policy, surface the
observed closed category and disposition, and direct the participant to one legal
next action. It rejects silent fallback, unbounded retry, and a presentation layer
that claims resume or repair without the owning runtime contract.

The provider-recovery change is a direct initial consumer of this policy, but the
policy does not alter that change's implementation or decide its retry budget.

### 6. Policy evolution stays lightweight and traceable

`change-admission.md` will define a compact trigger-based review. A contributor
consults only the relevant policy when a change affects local context, source of
truth, participant output, recovery/control, or admission itself. A new rule goes
into the charter only if it is durable and cross-cutting; otherwise it becomes a
focused policy or owning capability requirement. A policy change that would alter
runtime behavior must also have an owning capability delta.

The charter checker will be added to the existing `agent/Makefile` governance
target and receive focused contract tests. It will reuse the repository root as its
input and use only the standard library, matching the other governance checkers.

## Risks / Trade-offs

- [The charter becomes another long document everyone must read] -> The index routes
  by trigger and the module-guide gate asks for one relevant policy, not the whole
  tree.
- [A mechanical check gives false confidence in prose quality] -> The checker
  validates only stable locations, links, Focus Card shape, and the expansion-gate
  anchors; specs, tests, and review remain the semantic gates.
- [The focus gate blocks necessary investigation] -> A concrete interface,
  authority, compatibility, or observed-failure question admits the needed contract;
  the card can be revised as discovery changes the real scope.
- [A policy is mistaken for runtime authority] -> Every charter/policy begins with
  its scope and non-authority boundary, and the index explicitly routes behavioral
  changes to an owning spec.
- [Root and local guidance conflict] -> The charter makes root guidance an upstream
  constraint and confines its own scope to `agent/`; it neither edits nor overrides
  root guidance.
- [Codex and Claude Code guides drift] -> `agent/CLAUDE.md` imports the single
  authoritative `agent/AGENTS.md`, and the deterministic checker verifies that the
  compatibility entrypoint remains present and linked.
- [Entry documents grow back into default manuals] -> their roles, focused-doc links,
  and deterministic line-count warnings/failures are owned by the information-map
  policy and charter checker; exact structural detail remains in TOML rather than the
  generated guide.
- [Retiring the narrow draft loses requirement history] -> Its allocated IDs remain
  in the append-only registry with an explicit supersession marker and are not reused.

## Migration Plan

1. Add the canonical charter tree, shared local module guide, Claude Code import
   entrypoint, OpenSpec authoring rule, and requirement registry/structure entries.
2. Add the deterministic checker, focused contract fixtures, and the `make
   governance` invocation; update the generated structure block through the existing
   architecture checker.
3. Add the Focus Card to the already-active provider-recovery proposal and verify all
   active changes satisfy the new convention.
4. Tighten the local-context policy, module-guide gate, authoring pointer, checker,
   and red fixtures so speculative expansion cannot silently become the default.
5. Add the information-map policy, compact the coding-agent/OpenSpec entry context,
   decompose the human README into a shallow entry page and focused docs, and make
   line-count warnings/failures visible in deterministic checks.
6. Render the compact structural locator and run focused governance tests, the
   existing root governance checks, strict validation for this change, and the
   regular downstream deterministic gate.

Rollback removes only the charter documents, pointers, and checker introduced by this
change. No runtime data, provider configuration, or execution state is migrated or
needs recovery.

## Open Questions

None. The initial policy topics are deliberately finite; future policies require a
concrete recurring trigger and a charter-index entry rather than speculative folders.
