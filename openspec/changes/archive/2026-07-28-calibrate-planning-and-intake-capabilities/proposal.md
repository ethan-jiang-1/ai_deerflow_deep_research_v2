## Why

The first capability cohorts made the local-policy mechanism observable, but topic
planning and Wave1 remain closed `legacy` requests and the research-start path still
has no behavior acceptance for profile-constrained planning, bounded source discovery,
or evidence expansion. Prompt text, parser checks, and aggregate test counts cannot
show that the real node/runtime path honors the intended research and repair limits.

This is the first of two deliberately separated Stage D changes. It makes the
confirmed-profile-to-evidence-intake path reviewable without claiming that Wave2,
targeted gap resolution, or evidence critics have already been calibrated.

## Change Focus

- **Primary module / causal owner:** `agent/src/deerflow_deep_research/graph/`;
  the topic-planning, Wave0, and Wave1 node handlers own placement and deterministic
  admission of their bounded candidates.
- **Question:** Can the real planning and initial-intake workflow preserve confirmed
  profile constraints, enforce its zero-tool or bounded-retrieval posture, admit only
  contract-valid candidates, and retain honest repair/degradation behavior?
- **Necessary adjacent/external contracts:** `node-agent-capabilities` answers how a
  migrated builder binds one validated local policy; `node-prompt-catalog` projects
  that policy for review; `topic-planning-node`, `wave0-node`, and `wave1-node` own
  candidate admission and phase outcomes; `evaluation-hardening` owns central,
  collected evidence claims. The runtime bridge remains the existing executor and
  tool-policy enforcer; its interface is not changed.
- **Evidence seam:** scripted real-node/runtime-bridge cases with fake model/tool
  adapters at the planner materializer and Wave0/Wave1 work-unit submission seams,
  backed by catalog and capability-admission checks.
- **Not in scope:** Wave2 synthesis; targeted worker, repair, source diagnostic, or
  claim verifier; graph topology; public interfaces; checkpoint schema; provider
  policy changes; live-model or research-quality claims; `backend/` and `frontend/`.
- **Triggered charter policies:** node-agent-workflow-integrity, workflow-outcome-review

## What Changes

- Migrate `topic-planning/plan`, `topic-planning/plan-repair`, `wave1/worker`, and
  `wave1/repair` from the closed legacy set to declared node-local capabilities with
  their correct forbidden or required tool posture. Preserve Wave0's existing
  capability references while calibrating its behavioral evidence.
- Define observable planning acceptance: complete profile-constraint preservation,
  bounded coverage/non-overlap, zero model-visible tools, and repair that cannot add
  external facts or alter confirmed profile authority.
- Define observable intake acceptance: Wave0 performs 1--3 permitted retrieval calls
  and reports a truthful degraded outcome; Wave1 makes exactly one permitted search,
  does not re-fetch the Wave0 baseline, and admits claims only through its existing
  validation/ledger boundary. Their repair branches remain zero-tool and cannot invent
  sources, URLs, claims, or questions.
- Extend the global capability matrix from eight to twelve rows with four new
  real-node/fake-capabilities rows, and retain separate scripted-real-workflow claims
  for the planner and worker runtime-bridge/tool paths. Neither evidence class claims
  live language or research quality.
- Update the prompt catalog and capability matrix so the migrated branch set, local
  policy source, tool posture, success evidence, and highest-risk evidence are
  mechanically auditable.

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Topic planning / repair | node-agent | What bounded non-overlapping topics cover the confirmed profile, or how can one invalid draft be structurally repaired without new facts? | Checkpointed confirmed profile and validation metadata are trusted assignment; model text remains a candidate. | Forbidden; the existing runtime bridge receives a required capability request with tools disabled. | `TopicPlan`; parser/materializer owns schema, coverage, stable ids, and checkpoint admission. | Topic-planning node owns one existing structured repair and its terminal outcome. | Matrix: real node with fake capabilities. Workflow: existing real zero-tool bridge selector with scripted adapter. |
| Wave0 source intake / repair | node-agent | Which permitted retrieval results support authoritative source candidates, or how can their draft be structurally repaired without invention? | WorkSpec is trusted assignment; search/fetch/model content remains untrusted evidence. | Required, 1--3 calls; existing execution policy/runtime bridge resolves only permitted tools. Repair keeps a required binding with forbidden posture. | Wave0 worker output; existing validator, controller, and ledger own admission. | Existing worker/controller failure and degradation owners retain their bounds. | Matrix: real node with fake capabilities. Workflow: existing scripted worker bridge/ledger selector. |
| Wave1 evidence extraction / repair | node-agent | Which one-search evidence candidates extend, rather than re-fetch, the assigned Wave0 baseline; how can malformed output be repaired without new evidence? | Topic and Wave0 baseline are trusted assignment; tool/model results remain untrusted evidence. | Worker required, exactly 1 call; repair required binding with forbidden posture; existing execution policy/runtime bridge enforces both. | `Wave1WorkerOutput`; existing validator, controller, and ledger own admission. | Existing worker/controller failure and repair owners retain their bounds. | Matrix: real node with fake capabilities. Workflow: existing scripted worker bridge/ledger selector. |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Invalid planner candidate or coverage failure | Topic-planning parser/materializer | Topic-planning node; its existing one structured repair | Existing blocked/exhausted outcome after the bound | Existing terminal handling; no Wave0 admission | Real planner node with malformed then exhausted scripted results |
| Missing or disallowed planner tool use | Runtime bridge/execution policy | No added recovery; zero-tool request is rejected at the existing boundary | Existing non-success/terminal planning path | Existing terminal handling | Capturing model/tool-resolver trap at the planner node seam |
| Wave0/Wave1 malformed candidate | Respective output parser/validator | Existing per-worker repair bound | Existing rejected/failed work result; no unauthorized ledger admission | Existing controller/gate handling | Scripted work-unit submission and ledger observation |
| Wave0 retrieval shortfall or Wave1 extra/baseline retrieval | Runtime bridge/execution policy plus worker result validator | No new retry policy; existing worker/controller outcome remains bounded | Existing failed or honest degraded worker outcome | Existing gate/controller handling | Existing or revised scripted-real-workflow bridge selector with exact call count, URL baseline, and submitted-result assertions |

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `node-agent-capabilities`: migrate the four planning/Wave1 legacy branches into the
  next closed capability cohort with explicit local policies and evidence rows.
- `node-prompt-catalog`: project the newly migrated branch policies and their correct
  request/runtime tool posture.
- `topic-planning-node`: make the planning/repair capability reference and behavior
  acceptance observable without changing topic authority or graph routing.
- `wave0-node`: specify source-intake/repair behavior evidence for bounded retrieval,
  no fabrication, and honest degradation.
- `wave1-node`: add local capability admission and behavior evidence for one-search
  baseline-aware evidence extraction and zero-tool repair.
- `evaluation-hardening`: register distinct collected branch evidence claims for this
  cohort without treating scripted behavior as live research quality.

## Impact

- Affected code is confined to `agent/src/deerflow_deep_research/graph/nodes/`
  (topic planning, Wave0, Wave1), their capability resources/prompt builders, catalog
  projection, and focused `agent/tests/` evidence assets.
- Existing runtime bridge, node controllers, typed state, graph routes, and public
  DeerFlow integration remain authoritative and unchanged unless an implementation
  discovers a contract conflict, which requires revisiting this proposal.
- No external dependency, API, `backend/`, or `frontend/` change is proposed.
