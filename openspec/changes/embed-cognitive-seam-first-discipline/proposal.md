## Why

The archived progressive plan
`_backlog/_done/_closed_plans/node-agent-cognitive-loop-governance-progressive-plan.md`
(closed changes 0–11) established this project's central engineering discipline: an
LLM-Bearing Node is a two-part program. Its Node Cognitive Control Program
(capability Markdown, prompt builders, model-visible context, structured feedback)
directs model behavior and is the first modification seam for a node-behavior
symptom; its Deterministic Control Boundary (parser, materializer, admission, ledger,
gate, route) admits only legal candidates and is the guardrail, not a substitute
repair site. The plan is archived and no longer live context. The vocabulary exists
in `deep_research_harness/CONTEXT.md` ("Node Agent Control"), but the discipline —
symptom-to-seam routing, Focus Card seam classification, cognitive-hypothesis
requirement — is not in the charter, the policies, or the coding guide. Coding agents
therefore still default to parser/gate/route/bridge edits for node-behavior symptoms.
This change embeds the discipline into the live governance and context layers so every
future OpenSpec change and implementation starts with the right attention.

## What Changes

- Add one durable charter principle: cognitive programs are the first modification
  seam for an LLM-Bearing Node's behavior; `run_agent` presence is mechanism
  evidence, never a node's product identity.
- Extend the local-context policy with a seam-classification rule: a node-behavior
  symptom is routed first to its cognitive-program seam (capability Markdown, prompt
  builder, feedback) before any deterministic edit is admitted; the Focus Card gains
  a required `Seam classification` field with closed values
  `cognitive-program | human-decision | deterministic-guardrail | wiring`; a
  cognitive-program edit states its cognitive hypothesis and observable result.
- Add the plan's canonical identity vocabulary to `deep_research_harness/CONTEXT.md`
  (Product Responsibility, Participation Mode, Commitment State, Current Operating
  Mechanism, Current Model-Branch Evidence, Seam Classification) plus one decision
  section recording the seam-first rule and its pointers.
- Add a short pointer in the `deep_research_harness/AGENTS.md` focus gate so an
  ordinary session routes node-behavior symptoms through the seam rule.
- Enforce the new Focus Card field mechanically: the charter checker's Focus Card
  field set gains `Seam classification` and validates its closed values and a short
  rationale, and the in-flight `calibrate-real-demo-model-contracts` proposal gains
  its deterministic-guardrail seam declaration so governance stays green.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `deep-research-agent-charter`: DRC-002 gains a symptom-routing SHALL; DRC-004
  gains a Focus Card seam-classification SHALL; the charter, local-context policy,
  checker, and their contract tests realize the discipline. The change does not
  alter any node capability, prompt, tool posture, admission, ledger, gate, route,
  retry, terminal, or lifecycle behavior.

## Impact

- Primary module: `openspec/governance/agent-charter/` (charter + local-context
  policy) and the Deep Research Product context (`deep_research_harness/CONTEXT.md`).
- Adjacent: a pointer in `deep_research_harness/AGENTS.md`; the charter checker
  `openspec/governance/check_agent_charter.py` and its contract test
  `deep_research_harness/tests/contract/test_agent_charter_governance.py`; the
  OpenSpec authoring rule in `openspec/config.yaml`; and one seam-declaration line
  in the active proposal
  `openspec/changes/calibrate-real-demo-model-contracts/proposal.md`.
- No modification under `deerflow/`, `backend/`, or `frontend/`; no runtime
  behavior, prompt, capability, tool, budget, retry, terminal, or lifecycle change.

## Change Focus

- **Primary module / causal owner:** `openspec/governance/agent-charter/` owns the
  durable seam-first discipline and its local-context policy;
  `deep_research_harness/CONTEXT.md` owns the canonical vocabulary that makes the
  two-part node program nameable.
- **Seam classification:** deterministic-guardrail — the change edits the
  deterministic governance/checker layer that guards change admission (charter,
  local-context policy, charter checker, context vocabulary); no node capability
  Markdown, prompt builder, feedback, or human-decision surface changes.
- **Question:** How does a coding agent route a node-behavior symptom to the
  cognitive control program first, and how does every OpenSpec change declare the
  seam it edits, without turning guidance into runtime authority?
- **Necessary adjacent/external contracts:** `deep-research-agent-charter` spec
  (answers which requirements own the focus-gate routing and Focus Card shape);
  `deep_research_harness/CONTEXT.md` (answers which canonical terms name the
  two-part program); `deep_research_harness/AGENTS.md` focus gate (answers where an
  ordinary session first loads the rule). `none` for DeerFlow public interfaces.
- **Evidence seam:** `make governance` (charter checker plus spec/req/architecture
  checks), `openspec change validate --strict`, the charter checker contract test,
  and `git diff --check`.
- **Not in scope:** runtime behavior; node capability Markdown or prompt-builder
  edits; ledger, gate, or route changes; projecting the 11-node/20-branch evidence
  inventory into context; editing the archived plan; root `AGENTS.md` and
  `CLAUDE.md` (upstream constraints).
- **Triggered review policies:** none: governance-only documentation change — no model, tool, provider, worker, retry, terminal, diagnostic, or lifecycle-projection path changes, and no node LLM-bearing role, capability policy, tool posture, output admission, or repair semantics change.
