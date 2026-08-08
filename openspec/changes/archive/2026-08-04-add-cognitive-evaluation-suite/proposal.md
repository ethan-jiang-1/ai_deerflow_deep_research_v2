## Why

The current `tests/` and live-calibration helpers prove deterministic workflow seams and
selected provider behavior, but they do not provide one independent, inspectable execution
record for evaluating an LLM-bearing node's cognitive control. Runner mechanics, run data,
and judgment criteria are too easy to conflate, which encourages a failed live call to be
mistaken for a quality verdict or a retry to be hidden inside a test.

This change establishes a Local-First Cognitive Evaluation Suite with a Python Runner that
executes exactly once and a separately invoked, review-only evaluator workflow. It is needed
now because node MD/prompt behavior is a first-class program and the recent real CLI failure
needs evidence that can be inspected without asking the user to replay an expensive run.

## What Changes

- Add a `cognitive-evaluation-suite` capability under `deerflow_research/`.
- Add a registered, versioned Case model that accepts only bounded node or flow execution
  declarations, fixed fixtures, service prerequisites, resource bounds, and control-version
  identity; reject free-form prompts, paths, model overrides, and resume state.
- Add a Python Cognitive Evaluation Runner in the governed
  `src/deerflow_deep_research/runtime/evaluation/` source layer. It creates one fresh
  isolated workspace per invocation, executes one declared Case once, captures inputs,
  outputs, artifacts, logs, events, tool/model observations, resource use, and diagnostics,
  and reports only `completed` or `failed` execution status.
- Add an immutable Evaluation Run Bundle and separate immutable Review Record contract.
  A review admission verifies the retained Bundle manifest and declared content digests before
  it can reference the Bundle. Review admission also resolves the Case, Contract, Rubric, and
  Protocol against the Bundle's recorded control identities. A Bundle remains evidence; a
  Review Record references it and records the versioned Case, control, Contract, Rubric,
  Review Protocol, evaluator, four-state result, evidence,
  confidence, unknowns, owning seam, and follow-up.
- Make review explicitly human-initiated. The Runner never automatically invokes, queues,
  retries, resumes, or selects an evaluator. A later attempt is a new Runner invocation and
  receives a new workspace and Bundle.
- Keep the control and generated-run surfaces physically separate under
  `deerflow_research/evals/`: slow-changing source-controlled `control/` for Cases, Rubrics,
  protocol, schemas, and registries; ignored fast-changing `runs/` for workspaces, Bundles,
  and Review Records. The Runner implementation is in the governed source package, not
  either subtree.
- Add V1 node smoke Cases for the HITL1 brief branch and the Wave0 worker branch. Flow
  evaluation, routine CI collection, automatic review, automatic retry/recovery, portable
  redaction, and a user-facing support handoff remain out of scope.
- Preserve the existing `tests/eval/`, `tests/scenarios/`, `evaluation-hardening` live
  calibration contracts, production node admission, lifecycle state, routes, and provider
  recovery. The new Runner reuses their lowest responsible production seams without copying
  node implementations or making their reports a second authority.
- Synchronize `openspec/governance/project-structure.toml`, its generated locator/checker
  fixtures, and `deerflow_research/.gitignore` for the new source, control, and run paths.

## Capabilities

### New Capabilities

- `cognitive-evaluation-suite`: manually invoked node/flow execution Cases, isolated
  immutable Bundles, and review-only Cognitive Evaluation Records.

### Modified Capabilities

- `project-structure`: register the governed Runner source and the separated
  `deerflow_research/evals/control/` and ignored `deerflow_research/evals/runs/` surfaces.

## Change Focus

- **Primary module / causal owner:** `deerflow_deep_research.runtime.evaluation` owns the Runner's Case admission, isolated execution workspace, Bundle materialization, and execution-status fact.
- **Question:** How can one manually selected node execution produce complete, immutable, reviewable evidence while keeping cognitive judgment, retries, lifecycle state, and production candidate admission outside the Runner?
- **Necessary adjacent/external contracts:** `graph/nodes/hitl1/` and `graph/nodes/wave0/` answer how the first two Cases invoke the real production branches and retain their existing parser/admission/tool owners; `evaluation-hardening` answers how existing deterministic and selected live evidence remains separate from this Suite; `project-structure` answers how source, control, and ignored run paths are registered and mechanically checked; `openspec/governance/req-registry.yaml` answers how CES/PRS requirement identities become globally unique pending requirements before implementation evidence refers to them; `deerflow_research/.gitignore` answers how generated run material stays local.
- **Evidence seam:** typed Case/Bundle/Review Record contract tests; Runner tests with external model/web adapters bounded at the declared bridge; isolated filesystem and immutability tests; direct HITL1 and Wave0 node smoke invocations; no full-flow quality claim.
- **Not in scope:** `backend/`, `frontend/`, DeerFlow host changes, public API/TUI behavior, production graph topology or lifecycle state, production retry/recovery policy, automatic evaluator orchestration, flow Cases in V1, CI/nightly collection, portable redaction, shared/multi-user storage, and user-facing Support Handoff.
- **Triggered review policies:** change-admission, authority-and-projections, control-placement, human-interaction-integrity, node-agent-workflow-integrity, workflow-outcome-review

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Whether a Case may execute | None; a registered Case is a bounded declaration | Case registry and Runner admission validator | non-bypassable | No free-form prompt/path/model override/resume state; invalid Case never invokes production | Reuses existing node `NODE_SPEC` and bridge contracts instead of copying nodes | Case schema, registry, and rejection tests |
| Execution result and Bundle publication | Node output is an untrusted candidate; Runner observes, never judges | Runner owns execution status; Bundle writer owns immutable evidence materialization | non-bypassable | Bundle is complete-or-failed evidence, never a lifecycle checkpoint or quality verdict; a fresh invocation is the only retry | Avoids a second production controller and hidden test retry | Runner failure/partial-observation and bundle-integrity tests |
| Cognitive quality conclusion | Upper review workflow or human evaluator supplies judgment | Review Record validator verifies the retained Bundle manifest/content digests and resolves the Case, Contract, Rubric, and Protocol to its recorded control identities before storing its reference; it cannot write production state | advisory | `pass`, `limited`, `inconclusive`, and `failed` remain separate from execution status; an altered, incomplete, or stale-control Bundle is not reviewable; no result admits a candidate or route | Allows multiple reviews of one costly run without mutating evidence | Review Record schema, Bundle-integrity, and control/reference-integrity tests |
| Starting upper review | A person explicitly decides whether and when to submit a retained Bundle | Human/operator action selects the Bundle; Runner has no review trigger | human-decision | No automatic queue, invocation, retry, or resume; the Bundle remains inspectable if review is deferred | Keeps expensive execution and judgment independently schedulable | Manual review command/adapter contract and no-auto-trigger test |
| Control versus generated run paths | None | Project-structure registry and ignore rules own path classification | non-bypassable | `evals/control/` cannot contain run output; `evals/runs/` cannot contain control authority or source | Prevents mutable evidence from contaminating versioned control | Architecture checker, clean-checkout, and `git check-ignore` tests |

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| HITL1 brief Case | node-agent | What conservative, decision-ready brief candidate can the production HITL1 brief branch produce from the fixed question? | Case fixture/question is trusted assignment; model output and provider material remain untrusted | No tools; production HITL1 bridge and its existing call/timeout policy enforce the posture | Typed HITL1 brief candidate; existing HITL1 parser and confirmation flow remain admission owners | Production branch/bridge owns bounded repair; Runner records failure once and does not recover | Direct HITL1 node fake-capability proof plus selected real node smoke |
| Wave0 worker Case | node-agent | What assignment-faithful source-intake candidate can the production Wave0 worker produce under bounded retrieval? | Fixed WorkSpec/topic is trusted; web/model observations and candidate facts remain untrusted | Declared web search only; production Wave0 capability policy and bridge enforce tool scope/budget | Typed Wave0 candidate; existing validator, controller, and ledger admit evidence | Production work-unit recovery remains owner; Runner records one execution failure | Direct Wave0 real-node/fake-capability proof plus selected real model/web smoke |
| Upper Cognitive Evaluation Agent Workflow (review-only) | node-agent | Does the Bundle satisfy the Case Rubric and what uncertainty or owning seam should be inspected next? | Bundle, Node Contract, Case-linked Rubric, and Review Protocol are read-only evidence; none grants production authority | No production tools, state writes, route controls, or rerun permission; evaluator interface enforces read-only access | Cognitive Evaluation Review / Review Record; deterministic Review Record contract accepts only its typed shape | Review workflow reports its own failure or `inconclusive`; a person may start another review, never an automatic run | Protocol fixture, read-only boundary, and Review Record validation tests |
| Python Runner | no-agent | Executes and observes a declared branch; it does not make a cognitive judgment | Only registered Case and runtime service bindings; no Rubric input to the execution process | Runtime bridge, cancellation, resource bounds, and filesystem containment enforce the Case | Execution Status and Bundle; no candidate admission or graph route | Runner fails closed after its one attempt; caller explicitly starts a fresh isolated invocation | Runner contract, cancellation, timeout, and no-rerun tests |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Case is unknown, stale, or violates its declared schema | Case registry/Runner admission validator | Caller corrects the registered Case; no execution or automatic retry | Runner invocation is rejected before production work and no Bundle is claimed as completed | Fix/select a valid Case and invoke explicitly | Registry, schema, and pre-invocation rejection tests |
| Required model/web prerequisite is unavailable | Runner preflight/runtime binding | Deployment owner; no hidden setup or retry inside Runner | Execution Status `failed` with typed preflight reason and retained diagnostics | Configure the prerequisite or explicitly select a later fresh run | Offline preflight and failure-bundle tests |
| Production node/flow branch fails, times out, is cancelled, or returns malformed output | Production bridge/node and Runner observation boundary | Production recovery remains unchanged; Runner has exactly one outer execution | Execution Status `failed`; all material observations obtained before stop remain in Bundle | Inspect Bundle, correct owner, then start a new Case invocation if appropriate | Direct bridge/node tests plus Runner timeout/cancel/partial-observation tests |
| Bundle cannot be finalized immutably or fails later evidence/control integrity verification | Bundle writer/filesystem owner | No automatic repair; operator investigates the local run store | Execution Status `failed` on finalization failure; a later evidence or control-identity integrity failure is rejected before review and leaves execution status unchanged | Repair storage or implementation and execute a new isolated run | Atomic publication, manifest/content-digest and control-identity verification, and immutability tests |
| Person defers or declines review | Human/operator | Person decides whether to review later; Runner does nothing | Bundle remains retained with execution status only | Explicitly submit the same Bundle to an approved review interface later | No-auto-review and retained-Bundle tests |
| Review workflow cannot assess the Bundle | Review workflow/Review Record validator | Person may start another review of the same immutable Bundle; no execution retry | Review is `inconclusive` or failed; execution status is unchanged | Correct review inputs/protocol or request a separate review | Review protocol, four-state, and Bundle-reference tests |
| Candidate is assessable but misses Case Rubric criteria | Review workflow | No production repair or Runner retry | Review Result `limited` or `failed` according to the rubric; never pass silently | Inspect the named control seam and propose a separate change | Rubric fixture and Review Record result tests |

## Impact

Implementation is limited to the downstream `deerflow_research/` module: a new governed
runtime evaluation package, control declarations, ignored local run storage, scripts or
operator adapter for explicit invocation, focused deterministic contracts, and two selected
node smoke Cases. It may reuse existing `tests/scenarios` bridge helpers through explicit
interfaces but must not duplicate production node implementations or alter their routes,
state, admission, or recovery. It does not change `backend/` or `frontend/`, external APIs,
database schemas, model/provider configuration, or the existing deterministic verification
selection. The project-structure registry/checker and `.gitignore` are part of the required
governance synchronization because the new paths are structural and generated.
