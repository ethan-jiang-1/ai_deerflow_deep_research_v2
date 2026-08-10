## Context

The verified governance facts that shape this design:

- `deep_research_harness/CONTEXT.md` "Node Agent Control" already names the
  two-part program (`LLM-Bearing Node`, `Node Cognitive Control Program`, `Node
  Cognitive Control Contract`, `Deterministic Control Boundary`) but lacks the
  canonical identity facts the archived plan requires: product responsibility,
  participation mode, commitment state, current operating mechanism, and current
  model-branch evidence remain unnameable in the live vocabulary, so a coding agent
  cannot distinguish "what this node is for" from "what loop runs today".
- `openspec/governance/agent-charter/README.md` "Where Rules Belong" assigns durable
  principles to `charter.md`, repeated triggered rules to `policies/<topic>.md`, and
  observable behavior to owning capability specs. This change follows that table
  instead of piling guidance into one file.
- `openspec/governance/agent-charter/policies/local-context.md` already owns the
  primary-module focus gate, the minimum-context rule, and the Focus Card. The
  archived plan's scope-card obligation — "say why a proposed change belongs there
  instead of at a parser, fixture, route, or generic runtime helper" — has no live
  home there; the seam-classification field is that obligation made explicit.
- `openspec/governance/check_agent_charter.py` mechanically enforces Focus Card
  field presence and ignores extra fields. Adding `Seam classification` to its
  required field set is the enforcement seam that survives an attention lapse; the
  checker mechanically validates the field's presence, closed-value membership, and
  a non-empty rationale exactly as it already validates control-placement
  `Design posture` closed values (DRC-009 requires the checker to validate closed
  posture values). The policy remains the canonical statement of the closed values;
  the checker never judges which classification is semantically true for a change.
- `deep_research_harness/AGENTS.md` is 81 lines (charter warning at 120, reject at
  160), leaving budget for a 2–3 line focus-gate pointer.
- `openspec/config.yaml` is 98 lines (reject at 180) and carries the Focus Card
  authoring rule; the seam field is added to that rule without exceeding the budget.
- The in-flight `calibrate-real-demo-model-contracts` proposal is the only other
  active change. Its seam is honestly `deterministic-guardrail` (Journal evidence
  and attribution for existing budget/parser boundaries; explicitly not prompts,
  budgets, or contracts), so adding the field there demonstrates the discipline
  rather than contradicting it.

The accepted `deep-research-agent-charter` spec (DRC-001..011) remains the
behavioral authority for charter/policy structure. The delta extends DRC-002 and
DRC-004 requirement text with full updated content and adds scenarios; no new
requirement IDs are introduced.

## Goals / Non-Goals

**Goals:**

- Make the cognitive-control-program-first discipline live in every layer a coding
  agent loads before a change: charter principle, local-context policy, Focus Card
  field, CONTEXT.md vocabulary, and the AGENTS.md focus gate.
- Make a missing, empty, non-closed-value, or rationale-less seam declaration fail
  governance mechanically, not just in review.
- Keep every edit inside the guidance layers; touch no runtime surface.

**Non-Goals:**

- No change to node capability Markdown, prompt builders, tool posture, budgets,
  admission, ledger, gate, route, retry, terminal, or lifecycle behavior.
- No projection of the 11-node/20-branch evidence inventory into context files; the
  inventory stays owned by the archived plan, its closed changes, and the
  `_backlog/_reference/` notes.
- No edit to the archived plan or to root `AGENTS.md` / `CLAUDE.md`.
- No new model or human-decision path, and no new runtime authority of any kind.

## Placement

Per the charter's "Where Rules Belong" table:

| Piece | Canonical home | Why there |
| --- | --- | --- |
| "Cognitive programs are the first modification seam" principle | `charter.md` Principles | Durable cross-capability posture, not a one-off feature contract |
| Symptom-to-first-seam table, closed seam values, Focus Card field | `policies/local-context.md` | Repeated triggered rule with a concrete trigger (node-behavior symptom / new proposal) |
| Canonical identity vocabulary and seam-first decision record | `deep_research_harness/CONTEXT.md` | Domain language of the two-part node program; plan terms are project-specific |
| Focus-gate pointer | `deep_research_harness/AGENTS.md` | Entry route loads the rule at session start; line budget allows it |
| Focus Card field presence, closed values, rationale | `check_agent_charter.py` + contract test | Mechanical presence, closed-value membership, and non-empty-rationale checks; the policy owns the canonical values |
| Requirement backing | `deep-research-agent-charter` delta (DRC-002, DRC-004) | Keeps policy and spec aligned; scenarios make the rule testable |

## Verification

- `openspec change validate --strict` passes for the new change and for the updated
  in-flight proposal.
- `make governance` runs from `deep_research_harness/`; every check attributable to
  this change passes. The pre-existing `check_project_reqs` failure (unregistered
  DPL-011/012, NOA-015, REJ-006/007, TOP-009, WAN-010, introduced by the in-flight
  `calibrate-real-demo-model-contracts` unarchived delta) is an external blocker
  expected to clear when that change archives.
- The charter checker contract test passes with the extended field set, including
  closed-value rejection and acceptance coverage for each seam value.
- `git diff --check` is clean.
