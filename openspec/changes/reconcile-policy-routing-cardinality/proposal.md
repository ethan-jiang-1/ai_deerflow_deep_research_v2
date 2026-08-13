## Why

The canonical Agent Charter route permits every policy whose trigger applies, but the
policy-library index and DRC-001 still tell a contributor to select `one relevant
policy`. That singular wording can omit a required design or admission review and is
the last current no-code authority mismatch from the alignment audit.

## What Changes

- Reconcile contributor-facing policy-routing language so a change selects every
  canonical policy whose trigger applies, while retaining exactly one primary causal
  owner for the change.
- Update DRC-001 and its scenarios to state the plural routing rule and demonstrate
  that simultaneously applicable policies are selected without becoming runtime
  authority.
- Align directly related authoring-route wording, including the policy-library index
  and OpenSpec context, with the same rule.
- Preserve policy trigger definitions, Focus Card grammar, checker behavior, runtime
  authority, and the existing policy set.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `deep-research-agent-charter`: contributor routing requirements move from a
  singular policy selection to every applicable canonical policy, while retaining one
  primary causal owner and the Charter's guidance-only boundary.

## Change Focus

- **Primary module / causal owner:** `openspec/agent-charter/` contributor-routing
  authority; it owns the durable admission language that DRC-001 specifies.
- **Seam classification:** wiring - aligns existing contributor entry points without introducing a runtime decision.
- **Question:** How can all current contributor entry points state the same
  trigger-based multi-policy route without implying that policies grant runtime
  behavior, permission, or a second causal owner?
- **Necessary adjacent/external contracts:** `openspec/policies/README.md` answers how the canonical policy-library index routes readers; `openspec/config.yaml` and `deep_research_harness/AGENTS.md` answer how the authoring route records selected canonical policy names and conditional review records; neither owns runtime behavior.
- **Evidence seam:** focused Markdown/spec search for residual singular routing
  wording, `openspec validate reconcile-policy-routing-cardinality --strict`,
  `openspec doctor --json`, and the existing Agent Charter checker.
- **Not in scope:** application code, agent-charter checker/parser behavior, policy
  applicability semantics, Focus Card grammar, policy files, runtime authority,
  `deerflow/`, A-002, A-004-T01, and A-009.
- **Triggered review policies:** change-admission, agent-information-map

Ordinary downstream work in this change neither modifies nor source-browses the
`deerflow/` gitlink. The proposal describes pending documentation/spec scope, not a
new runtime fact.

## Impact

- Affected authority: `openspec/agent-charter/README.md`,
  `openspec/policies/README.md`, `openspec/config.yaml`,
  `deep_research_harness/AGENTS.md`, and the `deep-research-agent-charter` main-spec
  delta after approval.
- No application APIs, dependencies, data, graph routes, policy triggers, or
  executable governance behavior change.
- A focused documentation/spec validation demonstrates that contributors receive one
  unambiguous route before the Stage 7 alignment plan is closed.
