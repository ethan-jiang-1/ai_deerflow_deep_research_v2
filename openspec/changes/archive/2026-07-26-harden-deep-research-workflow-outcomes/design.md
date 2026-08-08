## Context

Deep Research has six production graph-node packages that call `run_agent`:
`hitl1`, `topic_planning`, `wave0`, `wave1`, `wave2_synthesis`, and
`targeted_evidence`. Their successful paths are covered by a syntax-discovered
workflow inventory, but their failure paths have evolved independently.

Verified current behavior is uneven:

- HITL1 preserves a `NodeProblem`, bounded provider recovery, and a
  `TerminalIncidentProjection`.
- Wave0 maps a non-successful worker invocation into a closed work-attempt
  category, which its controller can retain and aggregate.
- Topic planning discards a bridge-supplied `NodeProblem` and maps it to generic
  exhaustion. BUG-010 demonstrated the user-visible result when its shared
  30-second policy budget expires.
- Wave1, Wave2 synthesis, and targeted evidence convert known non-successful
  results into generic `ValueError` values, losing safe provider classification
  before their phase/controller can decide the outcome.

The Agent Charter and `openspec/config.yaml` already direct contributors toward
shared facts, bounded recovery, actionable participant outcomes, and a lowest
responsible evidence seam. They currently guide judgement but do not require a
workflow change to record its failure-outcome design or prove it across every
discovered model owner.

## Goals / Non-Goals

**Goals:**

- Preserve one safe, typed invocation failure from the raw-binding bridge through
  the owning phase and its eventual lifecycle/session/CLI/TUI outcome.
- Keep recovery phase-owned and bounded, while making the chosen disposition
  visible and mechanically testable.
- Give topic planning an independent, phase-appropriate model-call budget and a
  provider-failure path that does not masquerade as malformed structured output.
- Turn the existing real-workflow inventory into a failure-outcome completeness
  check across all current and future `run_agent` owners.
- Strengthen the charter's practical effect through a triggered policy, a
  proposal-level decision record, and deterministic evidence without granting the
  charter runtime authority.

**Non-Goals:**

- Eliminate provider failures or promise every blocked run can resume.
- Create a global retry controller, a UI-local retry loop, or a new lifecycle
  authority.
- Change DeerFlow host code, the frontend application, provider configuration, or
  the existing durability contract.
- Rewrite historical diagnostic bundles or infer a missing incident from old logs.
- Require every phase to expose the same recovery action; legal next action stays
  a property of the checkpointed result and durability.

## Decisions

### Decision 1: Add a small workflow-outcome seam, not a global retry framework

Add a domain-owned workflow-outcome module beside the existing
`NodeProblem`/`TerminalIncidentProjection` contracts. Its interface will accept a
node invocation result or a caught local exception plus the logical phase, and
return a bounded safe outcome: successful result, classified failure, or
cancellation propagation. It will centralize these invariants:

- A known `NodeProblem` retains its code, certainty, provider observation, and
  originating phase.
- A non-success result with no safe problem becomes an explicit bounded unknown;
  raw exception text and provider bodies never enter state or presentation.
- `CancelledError` is propagated rather than converted into a failure or success.
- Direct terminal phases build `TerminalIncidentProjection` from the preserved
  fact; worker phases build a closed work-attempt failure for their existing
  controller instead of inventing a terminal incident per work item.

The seam does not choose a retry count, graph route, or user command. Each phase
declares its own disposition table over the normalized result. This creates depth
where the behavior truly repeats (safe classification and projection) while keeping
business recovery local to the phase that owns the operation.

Alternative considered: copy HITL1 helpers into every node. Rejected because the
same fact would be reinterpreted in six implementations, creating future drift.

Alternative considered: put all retries in `RuntimeNodeAgentBridge`. Rejected
because the bridge cannot know whether a phase's next legal action is a model retry,
structured-output repair, work-unit retry, graph repair, or terminal block.

### Decision 2: Make the phase failure-outcome table an explicit contract

Each real `run_agent` owner will have a small, closed table in its owning
capability specification and deterministic tests. The table distinguishes at least:

| Condition | Fact owner | Phase decision | Durable outcome |
| --- | --- | --- | --- |
| successful result | node result | continue | normal phase state |
| invalid structured output | phase validator | bounded format repair | repair result or specified exhaustion |
| provider timeout/unavailable | bridge result | phase- or work-controller-owned bounded recovery | provider incident or classified work attempt |
| configuration/authentication/non-retryable provider failure | bridge result | fail closed | preserved terminal/attempt category |
| local unknown failure | phase boundary | fail closed | explicit unknown, never fabricated provider data |
| cancellation | task/runtime | propagate | existing cancellation semantics |

The exact recovery is intentionally not global:

- HITL1 and topic planning may use their explicitly bounded provider-retry policy.
- Wave0, Wave1, and targeted evidence let their existing work-unit controller own
  retry and aggregation after receiving a classified worker failure.
- Wave2 synthesis uses its phase/gate contract; a direct invocation failure must
  retain an incident if it terminally blocks rather than escaping as an opaque
  graph exception.

Alternative considered: require every provider timeout to retry exactly once.
Rejected because worker retries, gate repair, and direct lifecycle recovery have
different correctness and cost constraints.

### Decision 3: Split HITL1 and topic-planning execution policies

The current shared zero-tool policy is a hidden coupling: a short, profile-brief
budget also governs a structured topic plan. Define separately named policies with
the same zero-tool authority but independent budgets. Topic planning will start
with a 60-second per-invocation wall-time ceiling, one model call per invocation,
and its own bounded provider recovery. HITL1 retains its existing bounded brief
policy unless a separate change alters it.

The bound remains an enforcement limit, not a promise that every provider call
will succeed. A timeout is still represented as `provider.timeout`, and the
phase's table controls the one allowed recovery or terminal disposition.

Alternative considered: raise the shared 30-second limit. Rejected because it
silently changes HITL1 latency/cost behavior and leaves failure information loss
unfixed.

### Decision 4: Preserve one source of truth through diagnostics and projections

The checkpointed `latest_incident` remains the terminal authority for direct
phase failures. Work-unit attempts/accepted ledger remain the authority for worker
failures; their existing controller derives any exhausted aggregate. The run-session
journal, diagnostic record, `ResearchRunExperience`, CLI, and TUI only project
those facts.

For a terminal outcome, human and machine projections will use the same bounded
fields: category, phase, certainty, worker category when applicable, observed
recovery disposition, safe diagnostic reference, durability, and one legal next
action. The display layer must not infer a retry, resume, or provider diagnosis
from timing, text, a bundle path, or its own local state.

Alternative considered: let `demo_real.py` inspect event timing and synthesize a
better message. Rejected because it creates a second, non-durable authority and
would still leave API/TUI consumers inconsistent.

### Decision 5: Upgrade workflow evidence from existence coverage to outcome coverage

Extend the AST-discovered model-owner inventory with a declared outcome-coverage
entry for every discovered owner. Each entry names the owner, its applicable
failure classes, a deterministic scripted-real-node selector, and a lifecycle or
work-controller projection selector. Validation fails when:

- a production `run_agent` owner has no outcome entry;
- an entry has no collected deterministic workflow evidence;
- a declared applicable class lacks an assertion at the owning phase seam; or
- a direct-terminal or worker aggregate cannot be observed through its owning
  lifecycle/controller interface.

This preserves the existing success-path workflow claims and adds failure-path
claims rather than replacing them. A focused semantic table can be reviewed before
implementation; AST discovery prevents newly introduced owners from silently
escaping the table.

Alternative considered: use only live provider tests. Rejected because timeout and
failure behavior must be deterministic, cheap, and reproducible in the normal
verification gate.

### Decision 6: Strengthen charter admission with a triggered decision record

Add a `workflow-outcome-review` charter policy. It is triggered when a change adds
or changes a model, tool, provider, worker, retry, terminal, diagnostic, or
lifecycle projection path. The policy requires the owning spec to name the failure
table, fact owner, recovery owner/bound, legal next action, and proof seam.

Update `openspec/config.yaml` so every active change records its triggered charter
policies in `Change Focus`; a `workflow-outcome-review` selection requires a
`## Workflow Outcome Review` table. Governance can validate the presence and
shape of this decision record, while semantic correctness remains enforced by the
owning specs and deterministic outcome tests. `none` remains valid only with a
short rationale, avoiding a mandate to load every policy for every change.

Alternative considered: move the charter out of `governance/`. Rejected because
location is not the missing enforcement mechanism; the charter correctly remains
guidance, and this change makes its triggered use visible and reviewable.

## Risks / Trade-offs

- [Longer topic-planning wall time raises latency and cost] -> Keep one-call and
  retry bounds explicit; expose the observed timeout/recovery rather than hiding it.
- [A common helper grows into a global workflow controller] -> Limit its interface
  to safe result normalization and incident/worker-failure construction; routes and
  recovery tables remain phase-owned.
- [Outcome coverage becomes paperwork] -> AST discovery, collected selectors, and
  negative detector tests make omissions mechanically visible.
- [Legacy terminal records lack a new incident] -> Treat them as honestly unknown;
  do not backfill from inference or alter terminal authority.
- [A broader sweep changes established worker semantics] -> Preserve existing
  work-unit controller, gate, and ledger ownership; test each worker's current
  retry/aggregation behavior before modifying its classification adapter.

## Migration Plan

1. Land typed outcome seam and its direct contract tests without changing routes.
2. Split the topic-planning budget and implement its failure table, including the
   BUG-010 regression at node, lifecycle, session, and CLI projection seams.
3. Migrate the remaining five discovered owners one at a time, retaining existing
   worker/controller and gate contracts.
4. Enable outcome-coverage inventory enforcement only after entries and tests exist
   for all currently discovered owners; its negative test proves a new owner cannot
   bypass the requirement.
5. Add the charter policy and config/checker decision-record validation alongside
   the implementation, then require it for future relevant changes.

Rollback is source-only: revert the new adapters and policy enforcement together.
Existing checkpoint records remain readable because new incident/projection fields
are optional; no migration rewrites or replays retained runs.

## Open Questions

- Does the current deterministic scripted workflow harness expose enough direct
  terminal projection for Wave2, or is one narrow mixed-graph fixture needed?
- Should the 60-second topic-planning ceiling be a fixed runtime policy constant
  for this release or an internal configuration field in a later bounded-config
  change? This proposal selects the constant to avoid widening public config.
- Which existing worker failure enum values can represent provider timeout without
  exposing provider-specific details, and where is a distinct `unknown` aggregate
  already sufficient?

## Evidence

### Focused Deterministic Verification (2026-07-26)

- `cd agent && env -u VIRTUAL_ENV uv run --extra operations pytest tests/domain/test_workflow_outcomes.py tests/domain/test_work_unit_state.py tests/engine/test_gate_kernel.py tests/graph/test_hitl1_node.py tests/graph/test_topic_planning_node.py tests/graph/test_wave2_synthesis_real.py tests/graph/test_targeted_evidence_real.py tests/graph/test_work_unit_component.py tests/unit/test_research_runtime_capabilities.py tests/unit/test_run_session_store.py tests/contract/test_run_experience_failures.py tests/contract/test_workflow_node_inventory.py -m "not (requires_llm or release_e2e or postgres)"`
  - Passed: `213 passed in 6.97s` (domain outcome contract, direct nodes, worker-controller/gate behavior, runtime capability policy, retained session, run experience, and inventory).
- `cd agent && env -u VIRTUAL_ENV uv run --extra operations --extra demo-tui pytest tests/integration/test_topic_planning_lifecycle.py tests/integration/test_wave0_work_units.py tests/integration/test_wave1_work_units.py tests/integration/test_demo_real.py tests/integration/test_demo_tui.py -m "not (requires_llm or release_e2e or postgres)"`
  - Passed: `54 passed in 8.14s` (direct lifecycle/session incident retention, worker outcomes, CLI, and TUI projections).
- `cd agent && env -u VIRTUAL_ENV uv run --extra operations pytest tests -m "workflow and not (requires_llm or release_e2e or postgres)"`
  - Passed: `16 passed, 1969 deselected in 14.88s` (scripted real workflow conformance).
- `cd agent && env -u VIRTUAL_ENV uv run --extra operations python scripts/check_test_assets.py`
  - Passed: `13 incidents`, `11 real nodes`, `7 critical faults`, `6 model-workflow nodes`, `158 central claims`, and `1975 deterministic tests`; the focused selections include `workflow=16`.

Credentialed provider execution is supplemental evidence only and remains the bounded
5.3 task; the deterministic results above are the behavioral conformance evidence.

### Complete Deterministic Gate And Boundary Snapshot (2026-07-26)

- `cd agent && UV_OFFLINE=1 make verify`
  - Passed with exit code `0`. The gate ran project requirement/spec/architecture and
    charter governance, lock verification, Ruff lint/format, test-asset and
    requirement coverage, plus fast, integration, and workflow deterministic lanes.
- `openspec validate harden-deep-research-workflow-outcomes --strict`
  - Passed: `Change 'harden-deep-research-workflow-outcomes' is valid`.
- `git diff HEAD --check`
  - Passed with no output.
- `git status --porcelain=v1 --untracked-files=all`
  - Captured changes only under `_backlog/bugs/`, `agent/`, and `openspec/`, including
    the new workflow-outcome contract/spec/policy and BUG-011. `git diff --name-only
    HEAD -- backend frontend` returned no paths, so the protected upstream boundaries
    remain untouched.

BUG-011 was discovered while running the full gate, recorded before remediation, and
reproduced twice with `tests/graph/test_research_graph.py::test_readiness_and_final_repairs_converge_before_completion` (`1 failed in 1.72s`). After narrowing the gate-bypass condition to non-completed terminals, that regression and the direct-terminal Wave2 guard both passed (`1 passed in 0.94s` each).

### BUG-012 Diagnostic Reference Regression (2026-07-26)

- The bounded real-demo observation exposed a CLI-to-bundle diagnostic-reference
  split and was recorded first as `BUG-012`.
- The smallest deterministic reproducer is:
  `cd agent && env -u VIRTUAL_ENV uv run --extra operations pytest tests/contract/test_run_experience_failures.py::test_blocked_terminal_without_checkpointed_reference_uses_the_retained_bundle_reference -q`.
  It was red twice before the repair, for both an unclassified blocked terminal and a
  non-provider terminal incident with no checkpointed reference.
- `ResearchRunExperience` now allocates or reuses one terminal reference before it
  publishes the retained session, then supplies that same reference to the terminal
  failure projection. The regression passed: `2 passed in 1.02s`.
- Focused post-fix verification passed:
  `22 passed` for `test_run_experience_failures.py`, `25 passed` for
  `test_run_session_store.py`, `24 passed` for the real CLI/TUI render tests,
  `5 passed` for topic-planning lifecycle, and both BUG-011 guards passed.
- The complete deterministic gate was re-run after the repair:
  `1809 passed, 2 deselected` (fast), `148 passed, 4 skipped, 15 deselected`
  (integration; Gateway stack unavailable), and `16 passed, 1971 deselected`
  (workflow), with exit code `0`.

### Supplemental Credentialed Demo (2026-07-26)

- Executed exactly one bounded live run:
  `cd agent && make demo-real-scripted DEMO_ARGS='--question "OpenSpec 的普及程度、正面与负面影响；只采用有影响力团队或社区的一手资料，并给出引用。"'`.
  It returned the existing safe blocked outcome (`wave0`, worker category
  `structured_output`) and therefore exited `2`; no second live run was started.
- The retained run was
  `r_TslYsahrz0UPeenXC-O1DtYNKJnRr4AH71XUow20nmo`. Read-only
  `make demo-sessions DEMO_ARGS='inspect r_TslYsahrz0UPeenXC-O1DtYNKJnRr4AH71XUow20nmo'`
  reported `blocked@wave0`, `retained`, `same_process`, and the same
  `diag_53pN1ZHqaGjPq04E00IFZ1YY` reference printed by the CLI.
- The bundle summary, terminal trace, and support journal each retained that reference
  alongside `research.blocked`, `wave0`, and `structured_output`; this agrees with
  the controller-derived typed workflow outcome rather than creating a display-only
  diagnosis.
