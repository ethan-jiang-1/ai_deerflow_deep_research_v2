## Why

The six active cognitive nodes expose sixteen direct model branches, but their prompt
catalog, capability, bridge, feedback, and test evidence do not yet form one reviewable
program per branch. A branch count or a JSON/parser test cannot establish what the
model was asked, what it could use, which feedback reached a later turn, or which
deterministic owner admitted its candidate.

This change closes that evidence gap without changing cognitive quality, tool
authority, candidate admission, graph routing, or deferred-node behavior.

## What Changes

- Extend the existing test-owned `COHORT_EVIDENCE` denominator into an exact
  sixteen-branch cognitive-program evidence ledger for HITL1, topic-planning, Wave0,
  Wave1, Wave2 synthesis, and targeted evidence. Its case IDs must equal the canonical
  prompt catalog; it remains a read-only review projection.
- Make each branch reviewable through the production prompt renderer/catalog,
  local capability body, requested-versus-enforced tool posture, candidate/admission
  seam, feedback disposition and recipient when a next model request exists, and
  deterministic guardrail.
- Add deterministic composition/feedback evidence and narrowly scoped scenario or
  live-evaluation evidence only for claims that require model judgment.
- Classify existing proof as cognitive-program, deterministic-guardrail, wiring, or
  obsolete duplicate before any later test consolidation.

## Change Focus

- **Primary module / causal owner:** `agent/tests/assets/node_agent_capabilities.py`; its current `COHORT_EVIDENCE` is the closed test-owned denominator for the sixteen direct branch/capability bindings, and the new ledger extends that review projection without becoming runtime authority.
- **Question:** Can every active direct model branch be reviewed as a bounded cognitive program while preserving the existing deterministic owners of tools, candidate admission, feedback, recovery, and routes?
- **Necessary adjacent/external contracts:** `graph/prompt_catalog.py` answers the canonical synthetic branch identity and builder case; `agents/phase_prompt.py` answers final prompt composition; `runtime/node_agent_bridge.py` answers actual tool enforcement and safe failure projection; node-local capability and handler contracts answer branch candidate/admission and feedback facts; `agent/tests/assets/evidence.py` answers central claim identity and collected selection; `openspec/governance/req-registry.yaml` answers active-delta requirement-ID registration; evaluation-hardening answers evidence classification.
- **Evidence seam:** exact equality of the catalog and capability-cohort case IDs; production renderer/bridge contract tests; source-faithful node/subgraph request-sequence tests for feedback; then an explicit branch-ledger scenario/eval disposition only where a claim requires model judgment.
- **Not in scope:** backend, frontend, tool-authority broadening, capability/prompt quality tuning, candidate admission, graph routes, checkpoints, lifecycle behavior, HITL2 interaction, readiness/final-delivery activation, and test deletion. Under explicit user authorization, this change also carries the minimal precondition repair that restores `NRI-003` to its existing accepted reader-interface spec/header and deterministic test traceability; it does not alter reader behavior.
- **Triggered charter policies:** change-admission, authority-and-projections, node-agent-workflow-integrity

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 16 current direct branches | node-agent | Each exact branch answers its current bounded node question only | Trusted assignment/context; external/model material remains data | Local capability requests posture; runtime bridge enforces it | Existing typed candidate; existing node/domain/engine owner admits it | Existing node/subgraph and bridge bounds; the ledger records them but adds no recovery | Catalog, renderer/bridge, source-faithful request-sequence tests, and exact ledger row |

## Capabilities

### New Capabilities

- `cognitive-program-evidence`: exact branch-level review/evidence obligations for current active cognitive programs.

### Modified Capabilities

- `node-prompt-catalog`: catalog cases expose stable branch composition and join to the test-owned feedback review projection without becoming feedback authority.
- `node-agent-capabilities`: local capability evidence records the branch-level cognitive program without granting authority.
- `node-agent-runtime`: bridge evidence records requested/enforced tool posture and bounded feedback/failure projection.
- `evaluation-hardening`: evidence taxonomy and branch ledger distinguish deterministic composition from judgment evaluation.

## Impact

- `agent/` test-owned capability evidence ledger, central evidence links, local capability review fixtures, renderer/bridge and source-faithful node/subgraph tests, and focused scenario/evaluation assets when a judgment claim is actually asserted.
- OpenSpec requirements/evidence registry only; no upstream service, public API, provider, state, or route change.
