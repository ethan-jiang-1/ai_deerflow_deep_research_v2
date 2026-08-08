## Why

Deep Research is a project-owned agent inside a much larger DeerFlow checkout.
The repository-level guides correctly protect the upstream host boundary, but they
do not give a contributor a short, durable way to recover the Deep Research
product's own intent. That makes ordinary work prone to broad, unfocused context
gathering and leaves human and AI participants with inconsistent expectations.

The initial focus rule identifies what should be read first, but it needs one more
guard: a contributor must not widen scope merely because another directory, document,
or upstream implementation might be useful. Each expansion needs a concrete question
and ends when that question is answered; otherwise the larger host repository becomes
an expensive substitute for local product understanding.

The provider-timeout incident made the cost concrete: an agent-facing system must
be explicit about ownership, evidence, recovery, and the next legal action. Those
are project principles, not a one-off CLI wording fix.

The same attention problem now exists in the project's entry documents:
`agent/AGENTS.md` and `openspec/config.yaml` have grown into long default context
loads. A coding agent must read their routing rule before it can decide whether the
remaining material is relevant. The project needs explicit roles and line-count
budgets so its navigation surfaces stay navigable as the product grows.

## Change Focus

- **Primary module / causal owner:** the downstream `agent/` product and its
  OpenSpec governance; this change owns the local authoring path, not a runtime
  module.
- **Question:** how a contributor finds the smallest authoritative context, admits
  only causally necessary expansion, and designs Deep Research behavior that people
  and AI consumers can both act on.
- **Necessary adjacent/external contracts:** only named neighboring `agent/`
  interfaces and public DeerFlow integration facts required by the active
  capability.
- **Evidence seam:** deterministic governance checks for the charter tree,
  navigation pointers, and active-change focus cards.
- **Not in scope:** `AGENTS.md` and `CLAUDE.md` at the repository root, all
  `backend/` and `frontend/` source, DeerFlow runtime behavior, provider settings,
  graph topology, checkpoint schema, sandbox layout, and public entry wiring.

## What Changes

- Establish `openspec/governance/agent-charter/` as the permanent home for the
  Deep Research Agent Charter, its index, and focused companion policies. The
  charter distinguishes durable principles from capability specifications,
  operations playbooks, and current runtime facts.
- Add a concise module-focus gate at the start of `agent/AGENTS.md`. A change in
  `agent/` begins by selecting one primary causal module, then its active
  specification, evidence seam, and only named adjacent/public DeerFlow interfaces;
  every scope expansion must answer a named interface, authority, compatibility, or
  observed-failure question. General orientation, speculative future relevance, and
  upstream implementation browsing are not admission reasons; unresolved ownership
  stops expansion until the Focus Card is clarified. Upstream repository guidance
  remains a boundary, not the local product's design authority.
- Add `agent/CLAUDE.md` as a thin Claude Code compatibility entrypoint that imports
  `AGENTS.md`. It exposes the same local focus gate and exclusions without copying
  or competing with the Codex-facing source of truth.
- Establish an information-map policy that assigns distinct jobs to the contributor
  entry documents: `agent/AGENTS.md` routes a code change, `agent/CLAUDE.md` imports
  that routing unchanged, and `agent/README.md` is a compact human/operator entry
  page. Move its detailed runtime architecture, local operations, and testing material
  into task-scoped `agent/docs/` documents behind a human-facing docs index. Reduce
  `openspec/config.yaml` to a short OpenSpec-authoring context rather than an
  accumulated project manual.
- Add line-count-first governance budgets with an early warning before a hard limit.
  The checker warns at 120 lines and fails above 160 for `agent/AGENTS.md`, warns at
  10 and fails above 12 for `agent/CLAUDE.md`, warns at 140 and fails above 180 for
  `openspec/config.yaml`, and warns above 200 for `agent/README.md`. It requires an
  early README reading map but intentionally gives that human-facing document no
  hard line cap.
- Add policies for local context selection, source-of-truth discipline,
  participant contracts for humans and AI consumers, control/recovery behavior,
  and change admission. Policies guide design and review; they cannot create a
  runtime route, permission, state field, or operational fact.
- Make a small Focus Card mandatory in active OpenSpec proposals and add a
  deterministic governance check for the charter's required pointers and card
  shape, including stable local-context expansion-gate anchors. The card states its
  primary module/causal owner, question, named adjacent or external contracts,
  evidence seam, and exclusions so future work need not rediscover the whole
  repository.
- Synchronize the charter tree, module-guide pointer, OpenSpec authoring rule,
  structure registry, generated guide block, and governance test. The retired
  `add-agent-interaction-charter` draft is not an additional implementation path.

## Capabilities

### New Capabilities

- `deep-research-agent-charter`: Defines the permanent local charter, its policy
  components, the primary-module focus contract, participant obligations, and its governed
  evolution. Requirements: `DRC-001`, `DRC-002`, `DRC-003`, `DRC-004`, `DRC-005`,
  `DRC-006`.

### Modified Capabilities

- `project-structure`: Registers the canonical charter tree and its module-guide
  focus gate while preserving the root guide boundary, and changes the generated
  module-guide projection from a full inventory to a compact structural locator.
  Requirements: `PRS-004`, `PRS-009`.

## Impact

Implementation is documentation and deterministic governance tooling only:
`openspec/governance/agent-charter/`, `openspec/governance/README.md`,
`openspec/governance/architecture-policy.md`,
`openspec/governance/project-structure.toml`, two small governance checkers,
`openspec/config.yaml`, `agent/AGENTS.md`, `agent/CLAUDE.md`, `agent/README.md`,
the task-scoped `agent/docs/` information map, and focused `agent/tests/contract/`
coverage. The existing real-demo recovery
proposal receives the new Focus Card so there is one live authoring convention.

No `backend/` or `frontend/` files change. No DeerFlow configuration section,
extensions configuration key, public/custom skill, per-user Agent/SOUL, MCP, ACP,
subagent, reflected tool, graph node, typed state/checkpoint data, node-agent role,
or sandbox artifact is changed. There is no next-agent-build or Gateway-restart
impact. The lowest responsible evidence is zero-API deterministic governance
validation; live provider or end-to-end testing is not relevant.
