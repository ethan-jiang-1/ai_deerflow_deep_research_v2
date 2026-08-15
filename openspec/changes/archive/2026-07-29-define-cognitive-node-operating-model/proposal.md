## Why

The existing reader-interface work correctly documents six packages with current
direct model branches, but its binary discovery result was being mistaken for the
permanent product identity of all logical nodes. That makes a deterministic
controller look like a failed agent, and can erase HITL2's conditional
human-decision opportunity or readiness/final-delivery's accepted deferred cognitive
responsibilities.

Before a later rollout gives every node the Wave2-shaped reader interface, this
change establishes the product-responsibility-first vocabulary, the closed audit
denominators, and the deterministic authority boundary that make that interface
truthful. It changes planning and specification artifacts only; it neither creates
an agent loop nor treats a reader projection as runtime control.

## Product Responsibility Review

This is the primary classification record. Product responsibility names the specific
research outcome; participation mode and commitment state are separate product
decisions; current operating mechanism is a source-audited fact. A direct model
branch or Charter binary flag is not permitted to fill any of the first three
columns.

| Logical node | Product responsibility | Participation mode | Commitment state | Current operating mechanism | Primary cognitive/control program surface | Deterministic authority boundary and current fact source |
| --- | --- | --- | --- | --- | --- | --- |
| bootstrap | Atomically bind and validate the trusted bootstrap bundle | Deterministic control | Intentional controller exclusion | Controller-only | Bundle store/domain contract plus bootstrap node handler | Bundle store/domain contract and node handler own binding, terminal disposition, and state update. |
| hitl1 | Turn bounded human request/profile material into advisory-brief or semantic-intake candidates | Bounded cognitive program | Current accepted | Active model loop; four direct branches | Package-local capability Markdown, prompts, and bounded bridge request | HITL1 parser/domain and graph owners admit candidates and publish the profile/route. |
| topic_planning | Decompose a confirmed profile into a bounded research-plan candidate | Bounded cognitive program | Current accepted | Active model loop; two direct branches | Package-local capability Markdown, prompts, and bounded bridge request | Deterministic materializer/controller admits the plan, materializes topics, and writes the route. |
| wave0 | Acquire and evaluate authoritative-source evidence for an assigned work unit | Bounded cognitive program | Current accepted | Active model loop; worker and repair branches | Package-local capability Markdown, prompts, worker bridge, and bounded retrieval posture | Validator/controller and submission ledger admit work-unit candidates and evidence. |
| wave1 | Extract source-grounded evidence for assigned work and surface bounded repair candidates | Bounded cognitive program | Current accepted | Active model loop; worker and repair branches | Package-local capability Markdown, prompts, worker bridge, and bounded retrieval posture | Validator/controller, ledger, critic, and gate retain evidence, admission, and route authority. |
| wave2_synthesis | Synthesize accepted evidence into findings, relations, and research gaps | Bounded cognitive program | Current accepted | Active model loop; synthesis and repair branches | Package-local capability Markdown, prompts, and dedicated zero-tool bridge | Node admission writes preview; deterministic gate owns executable routing. |
| targeted_evidence | Resolve a gate-projected evidence gap through targeted retrieval, diagnosis, or claim verification | Bounded cognitive program | Current accepted | Active model loop; four direct branches | Package-local capability Markdown, prompts, worker bridge, and bounded retrieval posture | Worker/repair admission and graph builder retain evidence and executable-edge authority. |
| hitl2 | Offer a user decision only when a genuine non-inferable preference or irreversible authorization is identified | Human decision / authorization | Conditional / unresolved | Autonomous deterministic continuation; validates Wave2 pass and applies proceed | Current deterministic HITL2 validator/node; later typed human-decision contract only after admission | Boundary validator/node maps only a valid typed choice to a legal route; current production path accepts no generic route menu. |
| rerun | Execute an already validated rerun scope, invalidating projections and advancing generation safely | Deterministic control | Intentional controller exclusion | Controller-only | Typed rerun contract, planner, and node | Rerun contract/planner/node own scope validation, invalidation, generation mutation, and route. |
| readiness | Judge per-question evidence sufficiency and answerability | Bounded cognitive program | Accepted-but-deferred | Deterministic critic fallback currently marks each question ready | Current critic fallback/hard rules; later bounded read-only critic contract after admission | Hard rules and report-plan materializer own verdict admission and route; a later critic remains read-only. |
| final_delivery | Compose and communicate a report plus citation map from the readiness-bounded plan and accepted evidence | Bounded cognitive program | Accepted-but-deferred | Deterministic formatter/publisher fallback | Current deterministic formatter/publisher; later bounded composer contract after admission | Integrity gate and publisher retain validation, publication, terminal status, and route authority. |

The ordered row set is exactly graph/topology.py::LOGICAL_NODES. The six
source-audited current active owners are not a product category: the six active
owners and their sixteen direct branches appear only in the audit appendix below.
The HITL2 row remains conditional until a later change has an approved genuine
decision trigger. Readiness and final delivery are accepted deferred work, not
evidence that an LLM is already active.

## What Changes

- Add the cognitive-node-interface capability. It defines one fixed,
  product-responsibility-first reader contract for every logical node: product
  responsibility, participation mode, commitment state, current operating mechanism,
  primary cognitive/control program surface, deterministic authority boundary, and
  audit-only current model-branch evidence.
- Define the fixed Wave2-shaped reader structure that a later rollout must use:
  product responsibility in the title and metadata order, followed by Node Identity,
  From Symptoms, Three Cross-Module Facts, Route Facts, and Evaluation and
  Verification Order. This change does not create or rewrite a workflow.md file.
- Preserve separate, source-owned current evidence: one individual row for each of
  the eleven logical nodes and one individual row for each of the sixteen current
  direct branches. Charter node-agent/no-agent labels remain an audit-only
  present/absent direct-branch classification, not a product label or activation
  claim.
- Require readers to distinguish a model candidate, a future human choice, and the
  deterministic writer that admits candidates, changes state, publishes artifacts,
  or selects a route.
- Clarify coexistence with node-agent-reader-interface. Its six current package-local
  reader obligations remain intact until a separately admitted all-node rollout
  applies the fixed interface to all eleven nodes.

## Capabilities

### New Capabilities

- cognitive-node-interface: product-responsibility-first reader contract and
  evidence/authority boundaries for every logical node.

### Modified Capabilities

- node-agent-reader-interface: clarify that its six existing package-local reader
  obligations coexist with, but do not substitute for, the later all-node
  cognitive-node interface rollout.

## Change Focus

- **Primary module / causal owner:** proposed cognitive-node-interface OpenSpec
  capability. It owns the non-runtime reader contract and audit discipline. The
  future authored reader projections belong to a separately admitted all-node rollout,
  not this change.
- **Question:** How can a maintainer identify each logical node's specific product
  responsibility and correct first cognitive/control seam without allowing current
  model-branch discovery, Markdown, or a Charter review to become product identity
  or a second authority?
- **Necessary adjacent/external contracts:**
  - node-agent-reader-interface: answers how the existing six package-local
    workflow.md obligations coexist with the future eleven-node fixed-shape rollout.
  - node-agent-capabilities: supplies the accepted capability references and direct
    branch evidence for the current sixteen-branch audit; it is not modified here.
  - hitl2-node, readiness-node, and final-delivery-node: identify the accepted or
    unresolved product commitments that must remain distinct from current mechanisms;
    none is modified here.
- **Evidence seam:** graph/topology.py and
  tests/graph/test_topology_and_implementation.py establish the ordered eleven-node
  denominator. tests/contract/test_workflow_node_inventory.py together with
  tests/domain/test_node_agent_capability.py establishes the six current discovered
  model owners and local capability-admission boundary. The closed sixteen-branch
  matrix is tests/assets/node_agent_capabilities.py as validated by
  tests/graph/test_node_agent_capability_cohort.py. Focused bootstrap, rerun, HITL2,
  readiness, and final-delivery tests, plus their closest node sources, establish the
  remaining five current mechanisms. These prove current wiring and authority seams,
  not cognitive quality, future activation, or a user-experience decision.
- **Not in scope:** all workflow.md rewrites; a static/generated checker; capability
  body or prompt edits; tools; model calls; state; checkpoints; routes; lifecycle;
  HITL2 interrupts/cards; UI adapters; test reclassification; specification
  synchronization; and implementation changes under agent/, backend/, or frontend/.
- **Triggered charter policies:** change-admission, authority-and-projections, and
  node-agent-workflow-integrity. This change selects neither
  human-interaction-integrity nor workflow-outcome-review because it changes no
  interaction, model/tool path, recovery, terminal behavior, or lifecycle outcome.

## Node Agent Review — Charter Model-Branch Evidence Appendix

This table satisfies the Charter review requirement as a separate audit appendix.
Its Classification column records only current direct-branch evidence: node-agent
means a reachable production direct model branch was discovered; no-agent means no
such branch was discovered. Neither label names product responsibility,
participation mode, commitment state, deterministic authority, or an authorization
to add behavior.

| Surface | Classification, audit only | Bounded cognitive question or deterministic-control rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| hitl1 | node-agent; hitl1/brief, hitl1/brief-repair, hitl1/semantic-intake, hitl1/semantic-intake-repair | Produces profile-intake candidates; it does not publish a profile or choose a route. | Trusted assignment/correlated human material is distinct from untrusted model text. | Four forbidden-tool capabilities; node-agent bridge enforces resolved posture. | Typed advisory candidates; HITL1 parser/domain and graph owners admit and publish. | Existing typed repair/failure path is bounded by node owner. | Workflow inventory, capability matrix, and HITL1 graph tests. |
| topic_planning | node-agent; topic-planning/plan, topic-planning/plan-repair | Produces plan/repair candidates; it does not materialize topics or route. | Confirmed profile is trusted assignment; model text is untrusted candidate. | Both capabilities are forbidden-tool; bridge enforces actual posture. | Typed plan candidate; deterministic materializer/controller admits it. | Existing bounded repair/exhaustion owner. | Workflow inventory, capability rows, and topic-planning tests. |
| wave0 | node-agent; wave0/worker, wave0/repair | Retrieves/evaluates assigned authoritative-source work or repair; it does not admit evidence. | Work unit/expected output are trusted; sources and model output remain evidence/candidates. | Worker requests listed retrieval tools; repair is forbidden-tool; runtime bridge enforces subset/bounds. | Work-unit candidates; validator/controller and submission ledger admit them. | Existing worker-controller bounded repair/failure path. | Workflow inventory, matrix, and Wave0 integration seams. |
| wave1 | node-agent; wave1/worker, wave1/repair | Extracts source-grounded evidence or repair candidates; it does not decide baseline, ledger, critic, or gate outcome. | Caller work/baseline is trusted assignment; model/source material is untrusted evidence. | Worker has bounded retrieval posture; repair is forbidden-tool; runtime policy enforces availability. | Work-unit candidates; validator/controller, ledger, critic, and gate retain authority. | Existing worker-controller bounded repair/failure path. | Workflow inventory, matrix, and Wave1 integration seams. |
| wave2_synthesis | node-agent; wave2-synthesis/synthesis, wave2-synthesis/repair | Synthesizes findings/relations/gaps or repair candidates; it does not write a route. | Accepted evidence and assignment are trusted context; output is untrusted candidate. | Dedicated forbidden-tool capabilities and zero-tool bridge policy enforce posture. | Parsed/validated synthesis; node admission writes preview, deterministic gate writes route. | One bounded repair attempt and current invocation-failure owner. | Workflow inventory, matrix, real-node/gate tests. |
| targeted_evidence | node-agent; targeted-evidence/worker, targeted-evidence/repair, targeted-evidence/source-diagnostic, targeted-evidence/claim-verifier | Retrieves, diagnoses, or verifies one projected gap; it does not select graph edge. | Gate-projected gap/assignment are trusted; sources/output are evidence/candidates. | Worker retrieval is bounded; repair/diagnostic/verifier are forbidden-tool; bridge enforces policy. | Typed work/critic candidates; deterministic worker/repair admission and graph builder retain authority. | Existing worker-controller bounded repair/failure path. | Workflow inventory, matrix, targeted-evidence real-node tests. |
| bootstrap | no-agent; no reachable direct model branch | Atomic trusted-bundle binding has no bounded cognitive question or user choice. | Validated start state/bundle contract is authoritative. | No model-visible tools or bridge invocation. | No model candidate; bundle validator/node handler write legal update. | Existing typed binding failure reaches its node-owned disposition. | bootstrap node/domain tests. |
| hitl2 | no-agent; no reachable direct model branch | Current path validates Wave2 pass and autonomously applies proceed. A future human decision remains conditional/unresolved, not current behavior. | Accepted predecessor state is validated; no user choice is currently accepted. | No model-visible tools; deterministic recommendation path, no bridge invocation. | Current path has no model/human candidate; boundary validator/node writes legal route. | Malformed predecessor fails closed; raw internal-route menus remain excluded. | hitl2 node source and HIT-001/HIT-002 tests. |
| rerun | no-agent; no reachable direct model branch | Executes validated rerun scope, invalidation, generation, and reset; cognition belongs upstream. | Validated rerun payload/state is parsed by typed contract. | No model-visible tools or bridge invocation. | No model candidate; rerun planner/node owns deterministic scope application and route. | Existing generation bound and terminal disposition are node-owned. | rerun node/contracts/tests. |
| readiness | no-agent; no reachable direct model branch | Current deterministic fallback marks verdicts ready; accepted read-only evidence critic is deferred. | Must-answer questions and accepted references are state facts. | Current fallback has no model/tools; future posture needs separate activation and runtime enforcement. | Current fallback output is materialized by hard rules/report-plan owner; routing remains deterministic. | Existing schema/hard-rule failure path owns fail-closed/blocked/repair behavior. | readiness critic source, REA-002/REA-006, readiness tests. |
| final_delivery | no-agent; no reachable direct model branch | Current formatter produces report/citation artifacts; accepted bounded writer is deferred. | Readiness plan and accepted references are authoritative. | Current formatter has no model/tools; future writer needs separate activation and enforcement. | Publisher/node writes artifacts, completed status, and route; writer would never publish directly. | Missing bundle and publication conflict follow current deterministic/store-owned failure paths. | final-delivery node/writer and focused tests. |

## 16-Branch Evidence Ledger

This closed audit records every current direct branch from
tests/assets/node_agent_capabilities.py. It is not evidence that a deferred or
conditional product responsibility already has a model loop, or that branch-level
quality has been evaluated. A node aggregate or a different branch's evidence cannot
substitute for an individual row.

| Current direct branch | capability reference | Production entrypoint |
| --- | --- | --- |
| hitl1/brief | hitl1-profile-brief | graph/nodes/hitl1/node.py::build_real |
| hitl1/brief-repair | hitl1-profile-brief-repair | graph/nodes/hitl1/node.py::build_real |
| hitl1/semantic-intake | hitl1-semantic-intake | graph/nodes/hitl1/node.py::build_real |
| hitl1/semantic-intake-repair | hitl1-semantic-intake-repair | graph/nodes/hitl1/node.py::build_real |
| topic-planning/plan | topic-planning-profile-decomposition | graph/nodes/topic_planning/node.py::build_real |
| topic-planning/plan-repair | topic-planning-plan-repair | graph/nodes/topic_planning/node.py::build_real |
| wave0/worker | wave0-authoritative-source-intake | graph/nodes/wave0/subgraph.py::run_wave0_work_units_real |
| wave0/repair | wave0-source-intake-repair | graph/nodes/wave0/subgraph.py::run_wave0_work_units_real |
| wave1/worker | wave1-evidence-extraction | graph/nodes/wave1/subgraph.py::run_wave1_work_units_real |
| wave1/repair | wave1-evidence-extraction-repair | graph/nodes/wave1/subgraph.py::run_wave1_work_units_real |
| wave2-synthesis/synthesis | wave2-evidence-synthesis | graph/nodes/wave2_synthesis/node.py::build_real |
| wave2-synthesis/repair | wave2-evidence-synthesis-repair | graph/nodes/wave2_synthesis/node.py::build_real |
| targeted-evidence/worker | targeted-gap-evidence-retrieval | graph/nodes/targeted_evidence/subgraph.py::run_gap_workers |
| targeted-evidence/repair | targeted-gap-evidence-repair | graph/nodes/targeted_evidence/subgraph.py::run_gap_workers |
| targeted-evidence/source-diagnostic | targeted-source-diagnostic | graph/nodes/targeted_evidence/node.py::build_real |
| targeted-evidence/claim-verifier | targeted-claim-verifier | graph/nodes/targeted_evidence/node.py::build_real |

If source discovery changes either denominator, the change must stop for a new Scope
Card and reconcile both ledgers before any reader classification is changed.

## Impact

- Revises only the existing change-local OpenSpec proposal, design, delta
  specifications, and apply ledger. These are governance/interface artifacts and do
  not own runtime facts.
- Does not create workflow.md, modify source code, prompt/capability Markdown,
  runtime configuration, test assets, generated projections, or accepted main
  specifications.
- Does not modify backend/ or frontend/, introduce a dependency, or change a public
  API, graph topology, lifecycle result, tool policy, candidate-admission boundary,
  or human interaction.
