# Deep Research Product

The Deep Research Product helps a person turn a research question into a useful
research outcome. Its vocabulary distinguishes the person's intent from internal
runtime and support details.

## Participants

**Primary User**:
A person who brings a research question and is not expected to understand working
directories, credentials, lifecycle phases, diagnostics, or implementation details.
_Avoid_: operator, debugger, runtime client

**User Decision**:
A research choice whose meaning, preference, or tradeoff only the Primary User can
authoritatively provide, such as research scope or a decision between alternatives.
_Avoid_: infrastructure recovery, configuration repair, lifecycle routing

**Research Confirmation**:
A lightweight User Decision process in which the Primary User accepts or adjusts the
system's proposed research approach before active research begins. It produces either
Accepted Research Facts or one current User Decision that remains to be made.
_Avoid_: service setup, operational recovery, an internal lifecycle phase

**Model-Led Research Interaction**:
The free-text conversation in which Deep Research proposes, explains, or clarifies a
research approach with the Primary User. Model interpretations remain candidates until
the User's choice becomes an Accepted Research Fact.
_Avoid_: menu-first intake, model-authorized research fact

**Accepted Research Fact**:
A fact that may direct active research because the Primary User stated it in the
research question or explicitly supplied or confirmed it. System proposals, model
interpretations, and unstated defaults remain advisory until accepted.
_Avoid_: model assumption, prompt default, inferred preference

**Research Outcome**:
The useful result the Primary User seeks after giving a research question: a readable
final report with an answer or recommendation, key evidence and sources, stated scope
and assumptions, and material limitations or uncertainty. It is not evidence that an
internal graph or provider executed.
_Avoid_: successful node execution, retained Run Bundle

## System Boundary

**Deep Research Harness**:
The stable downstream execution environment that creates and coordinates independent
Deep Research Runs. It remains when an individual Run Bundle is deleted, owns no
durable Run state, and is distinct from the generic DeerFlow Harness.
_Avoid_: DeerFlow Harness, Run Bundle, Research State

**Fixture Composition**:
The explicit implementation recipe of one graph: every node is a fixture adapter
(`fixture`), every node is the real factory (`all_real`), or the two are mixed
(`mixed`). It labels implementation composition only — not provider success,
evidence acceptance, or report quality.
_Avoid_: full-fake, full fake, fake graph, all-fake recipe

**Deep Research Run**:
One isolated execution of a research request by the Deep Research Harness. Its
durable state and materials belong to exactly one Run Bundle; one conversation has at
most one active Run, while ended Runs may coexist. A Run is active while its available
Bundle-local Research State is non-terminal, including while it waits for User input;
it is ended when its current Refinement Round is terminal. A Primary User may explicitly
reactivate an available ended Bundle for another Refinement Round. Bundle Loss makes a
Run unavailable, not ended, and an unavailable or lost Bundle cannot be reactivated.
_Avoid_: Deep Research Harness, Durable Research Session, another Run

**Run Refinement**:
A Primary User-directed adjustment to an active Deep Research Run, such as narrowing
scope, adding a question, or changing the requested delivery. It continues the same
Run and Run Bundle rather than creating another Run. Its direction form carries bounded
nonblank text and is distinct from both a Correlated Research Response and an Accepted
Profile Note.
_Avoid_: note, a new Deep Research Run, a second active Bundle, an unscoped message

**Accepted Profile Note**:
A bounded contextual preference or scope constraint accepted during Research
Confirmation as part of the research profile. It is not a general Run inbox and does
not independently start a later Refinement Round.
_Avoid_: Run Refinement, generic note, conversation memory

**Correlated Research Response**:
A Primary User answer to the one current research-confirmation or decision subject. It
may resolve only that subject and cannot also create an unstated Run Refinement.
_Avoid_: Run Refinement, unscoped follow-up, note

**Refinement Round**:
One bounded period of active work within a Deep Research Run. Creating a Bundle starts
its first Round; an explicit capacity-legal refinement of an available ended Bundle
starts a later Round in that same Bundle. A pending direction from an active Run takes
effect only at the completed terminal boundary of the current Round. `STOPPED`,
`CANCELLED`, and `BLOCKED` preserve a pending direction but never consume it
automatically. Earlier reports and materials remain retained for inspection.
_Avoid_: a new Run Bundle, a replacement for the retained Run history

**Refinement Admission**:
The acceptance of a Run Refinement into its active Run Bundle. A Primary User may submit
it at any time, but only one pending direction may exist in a Bundle. It takes effect
only at the next safe durable control point and does not rewrite State beneath an
in-flight writer or replace a pending Correlated Research Response.
_Avoid_: a requirement to wait for a prearranged HITL prompt, immediate concurrent State mutation

**Refinement Continuation**:
The explicit textless `refine` form for an available terminal Bundle that already has a
pending Run Refinement. It names that `bundle_id`, supplies no replacement direction or
operation identity, and can consume only the stored direction when capacity permits. It
is never inferred from conversation memory, a profile note, a Handle, or a terminal
status alone.
_Avoid_: automatic restart, a generic retry, a hidden text recovery, a new lifecycle action

**Run Bundle**:
The retained, inspectable, and independently deletable durable record of one Deep
Research Run. It contains that Run's Research State, evidence, content, and Run Event
Journal; it may be deleted externally at any time, making that Run and its retained
diagnostic evidence unavailable without affecting the Harness or another Run.
_Avoid_: disposable temp directory, shared workspace, Deep Research Harness

**Run Bundle ID**:
The fresh opaque identity and locating handle created with one Run Bundle. It identifies
that Run only while its Bundle exists; it is not derived from a conversation and cannot
recover a deleted Run.
_Avoid_: outer conversation id, shared research id, checkpoint key

**Current Bundle Handle**:
The transient Run Bundle ID retained in a current conversation to locate the Run being
worked on next. It may direct a refinement to that Bundle, but does not establish the
Bundle's existence, lifecycle status, or authority; its absence permits Run Discovery
within the trusted conversation scope.
_Avoid_: durable active-Bundle pointer, Run registry, replacement Research State

**Public Controller Workflow**:
The focused public Markdown program the recommended dedicated Agent reads through the
effective operator-owned `file:read` group before it proposes a Deep Research lifecycle
call on an ordinary relevant turn. The full configured read group remains the permission
boundary; the workflow is advisory, while tool schema, trusted runtime, and Bundle-local
State admit effects.
_Avoid_: a copied prompt, an `allowed-tools` workaround, a lifecycle authority, a path-only reader

**Run Discovery**:
The recovery of retained Runs by inspecting Bundle directories and the State contained
inside them within the trusted conversation scope. The Harness keeps no durable active
Bundle pointer or independent Run registry.
_Avoid_: global session registry, persisted active-bundle index, external run catalog

**Bundle Loss**:
The external removal or unavailability of a Run Bundle, including while its Run is
active. It ends the Harness's ability to observe or recover that Run's authoritative
State and supported retained diagnostic or Journal evidence. A supported retained
diagnostic or Journal reader, and participant presentation of that retained material,
require an available selected Bundle and are unavailable after Bundle Loss. This does
not assert secure erasure or the absence of residual physical bytes. No later action may
recreate the Bundle or persist a replacement State for it.
_Avoid_: a terminal lifecycle status, recoverable cleanup, automatic Bundle recreation, secure-erasure guarantee

**External Run Observation**:
An optional non-authoritative log, diagnostic, audit, or metadata record held outside a
Run Bundle. It may outlive the Bundle, but is neither the Run Event Journal nor a
supported retained diagnostic or Journal reader or participant presentation after Bundle
Loss. It cannot establish Run existence, select an active Run, authorize an action,
recover State, or prevent a fresh Run.
_Avoid_: lifecycle authority, run registry, checkpoint, Run Event Journal, post-loss diagnostic fallback, resume authorization

**Run Event Journal**:
The bounded, redacted, Bundle-local record of material execution facts for one admitted
Run. It shares the Bundle's lifetime; supported inspection and participant presentation
require an available selected Bundle and are unavailable after Bundle Loss, without an
external historical Journal, diagnostic, or Support Handoff fallback. This does not
assert secure erasure or the absence of residual physical bytes. It is neither a raw
application log nor lifecycle authority.
_Avoid_: External Run Observation, checkpoint, terminal State, raw log, external post-loss reader

**Live Progress Projection**:
A best-effort, non-durable rendering of safe current execution facts to a live DeerFlow
subscriber. It does not establish retained evidence or authorize an action.
_Avoid_: Run Event Journal, lifecycle result, checkpoint

**Research State**:
The lifecycle and control facts for one Deep Research Run, contained within its Run
Bundle. It cannot survive Bundle deletion or act as a cross-Run or Harness authority.
_Avoid_: external checkpoint, Harness state, shared state

## Validation

**Smoke Test**:
A bounded operator-facing verification run that exercises the real integration path as
closely as practical; it is not a Primary User product interface.
_Avoid_: end-user onboarding, production user journey

**Smoke Test Operator**:
A contributor or operator who runs a Smoke Test and can act on concise technical setup
or diagnostic information.
_Avoid_: Primary User, research participant

**Passing Smoke Test**:
A Smoke Test that uses real model and web integrations, follows bounded default
decisions, and finishes by producing a readable report for its fixed research question.
_Avoid_: a successful preflight, a retained session, a partial graph traversal

## Entry Interfaces

**Primary User Interface**:
`dormant`: the historical dedicated Deep Research TUI route through which a Primary
User would run and follow Deep Research. It has no active commitment and is not a
current runnable entry route; the Dedicated Agent and reflected `deep_research` tool
remain the current route.
_Avoid_: the standalone demo TUI, the smoke-test CLI, the Host Terminal Workbench, a raw lifecycle payload

**Current Recommended User Route**:
The Dedicated Agent's ordinary-language workflow and reflected `deep_research` tool.
It is the current route a Primary User uses to start and follow Deep Research.
_Avoid_: the dormant Primary User Interface, an Operator Interface, a local diagnostic

**Standalone Demo TUI**:
A contributor/operator visualizer for a shared Deep Research Run experience. It can
exercise real or fixture composition but is not a Primary User product interface or a
Host Terminal Workbench.
_Avoid_: Current Recommended User Route, Primary User Interface, generic recovery client

**Local Session Workbench**:
A fixed local-profile Operator Interface for bounded Run Bundle observation and legal
control projection. Its current profile is the configured fixture demo profile; a real
local profile is not a current product capability.
_Avoid_: generic recovery client, filesystem explorer, a Primary User Interface

**Operator Interface**:
The supported contributor/operator CLI used for Smoke Tests, debugging, and scriptable
operational work. Its current commands and exit semantics are an operational contract,
not a versioned general-purpose product CLI for external callers.
_Avoid_: the Primary User Interface, a public product CLI

**Integration Interface**:
The API through which another program invokes or observes Deep Research using its
published contract.
_Avoid_: the Primary User Interface, an operator console

**Host Terminal Workbench**:
The DeerFlow-wide terminal chat interface; it is not the owner of the dedicated Deep
Research Primary User Interface.
_Avoid_: the Deep Research TUI

## Node Agent Control

**LLM-Bearing Node**:
A logical graph node whose bounded model work contributes to a Research Outcome. It is
a two-part program: a Node Cognitive Control Program directs model behavior, while its
Deterministic Control Boundary admits only legal work and results.
_Avoid_: a conventional function call with an incidental model response

**Node Cognitive Control Program**:
The node-local, runtime-loaded MD/prompt, bounded model-visible inputs, and structured
feedback that together direct a model's goal, method, evidence and uncertainty handling,
output contract, and repair behavior. It is a first-class product program that must be
reviewed, tested, and evaluated for cognitive quality.
_Avoid_: graph routing configuration, an inactive documentation summary

**Node Cognitive Control Contract**:
The pre-implementation design anchor for an LLM-Bearing Node. It states the node's
user-serving cognitive responsibility; trusted and untrusted inputs; bounded method
and tool strategy; useful candidate, evidence, and uncertainty standard; feedback and
repair loop; and the final Deterministic Control Boundary. The runtime control program,
implementation, tests, and evaluations all refine the same contract.
_Avoid_: a second behavior authority, a prose-only implementation afterthought

**Deterministic Control Boundary**:
The code-owned authority that enforces tool and access limits, budgets, state,
persistence, route selection, and candidate admission. It constrains the Node Cognitive
Control Program but does not substitute for its cognitive design.
_Avoid_: the model's reasoning policy, a Markdown-controlled route

**Product Responsibility**:
The enduring user-serving responsibility an LLM-Bearing Node exists to fulfill — what
the node is for. It outlives any particular mechanism or branch.
_Avoid_: the current loop that happens to run, a mechanism described as a purpose

**Participation Mode**:
Whether a node participates as a model-directed cognitive program, a deterministic
owner, a human decision, or an intentional controller exclusion.
_Avoid_: a role claim inferred from the running mechanism

**Commitment State**:
The node's recorded acceptance of its latest candidate: `current accepted`,
`accepted-but-deferred`, `conditional/unresolved`, or `intentional controller
exclusion`.
_Avoid_: an unrecorded or inferred acceptance

**Current Operating Mechanism**:
The program branch a node runs today — which `run_agent` loop, controller, or
deterministic path is live. It proves that the mechanism exists, never what the node
is for.
_Avoid_: equating the mechanism with the node's product identity

**Current Model-Branch Evidence**:
Observable facts showing whether today's running branch is the model branch —
evidence, not identity.
_Avoid_: inferring a model branch from configuration order or file presence

**Seam Classification**:
The closed classification of a change's primary edit target —
`cognitive-program | human-decision | deterministic-guardrail | wiring` — declared
bare on the Focus Card with a short rationale.
_Avoid_: inferring the seam from the first file opened or from `run_agent` presence

**Cognitive Evaluation Suite**:
The independently invoked `evals/` system that observes Node Cognitive Control Program
behavior through a Python Cognitive Evaluation Runner and a separate Cognitive Evaluation
Agent Workflow. It is distinct from `tests/`, is not automatically collected by pytest
or normal deterministic verification, and records private local evaluation evidence
rather than treating an ordinary regression result as cognitive proof.
_Avoid_: `tests/eval/`, an always-on CI lane, an unstructured live demo

**Evaluation Control Surface**:
The slow-changing, source-controlled declarations under `evals/control/`: registered
Evaluation Execution Cases, their versioned Rubrics, the Evaluation Review Protocol, and
their schemas or registries. It contains no generated workspace, Bundle, or Review
Record. The Runner implementation remains in the governed package source root rather
than alongside these control artifacts.
_Avoid_: generated run data, a Python source root, mutable evaluator output

**Evaluation Run Store**:
The ignored, fast-changing local record area under `evals/runs/`. Each invocation creates
an isolated workspace and immutable Bundle there; separately immutable Review Records may
reference that Bundle without being written into it. No Case, Rubric, protocol, or other
control authority is stored in this subtree.
_Avoid_: a shared resume workspace, source-controlled control artifacts, a mutable Bundle

**Cognitive Evaluation Runner**:
The Python program that prepares a declared execution environment, sends bounded input
to the production node or flow, and captures its objective outputs, events, artifacts,
resource use, and diagnostics as an Evaluation Run Bundle. Every execution receives a
new isolated local Evaluation Run Workspace and does not reuse another execution's
checkpoint, artifacts, or bundle. It executes exactly once without retry or recovery,
then reports only `completed` or `failed`. Deterministic admission may compare only a
Case-linked Rubric's identity/version and unique criterion-ID set as non-model
case-control-integrity metadata. The Runner and its execution subject do not interpret
those IDs as quality or read Rubric prose, weights, thresholds, evaluator guidance, or
cognitive results; they produce no cognitive quality verdict. It makes a best effort to
preserve every observable input, output, log, and trace needed for later review.
_Avoid_: a hidden pytest marker, a copied node implementation, an evaluator, a quality verdict, a retry controller

**Evaluation Execution Case**:
A named, versioned, registered declaration of one finite Node Evaluation Run or Flow
Evaluation Run. It supplies only the execution subject, fixed inputs/fixtures, required
services, budget, control-version identity, and the linked Rubric identity/version with
its unique criterion-ID set for deterministic case-control-integrity admission only.
The Runner accepts this case rather than free-form prompts, paths, model overrides, or
resume state.
_Avoid_: an arbitrary script invocation, a Rubric quality input, an unbounded user request

**Evaluation Rubric**:
The versioned, case-specific cognitive assessment criteria associated with one
Evaluation Execution Case. It refines the Node Cognitive Control Contract's quality
standard into observable expectations for that case. Deterministic admission may compare
only its identity/version and unique criterion-ID set as non-model case-control-integrity
metadata. Criterion prose, weights, thresholds, evaluator guidance, and cognitive
judgment remain upper-review content; they do not enter a subject fixture, model-facing
execution input, execution output, or Runner completion status. The Evaluation Review
Protocol owns review method and output shape, not case quality criteria.
_Avoid_: a model-facing quality input, a Runner quality verdict, a replacement Node Cognitive Control Contract, generic evaluator prose

**Evaluation Run Workspace**:
The newly created, Runner-owned private local execution directory for exactly one
Cognitive Evaluation Runner invocation. Under one execution root, the immutable
Evaluation Run Bundle is its sibling; neither is the DeerFlow host workspace or a Deep
Research Run Bundle. It prevents earlier or concurrent evaluations from affecting its
observation.
_Avoid_: a host workspace, a shared resume directory, a reused checkpoint namespace, a Deep Research Run Bundle

**Evaluation Run Bundle**:
The immutable private local record of one Cognitive Evaluation Runner execution: the
execution-case input and control-version identity; actual node/flow outputs and artifacts;
and an Observation Trace of events, logs, tool/model observations, resource use, and
diagnostics. On failure it preserves every material observation the Runner obtained before
the stop. It lets an evaluator assess the same costly execution without rerunning it.
Under one execution root it is the sibling of that execution's Evaluation Run Workspace,
not a child directory within it. Export redaction is not an `evals/` requirement in the
current evaluation scope.
_Avoid_: a Deep Research Run Bundle, a mutable conversation transcript, a quality verdict, a shared run directory

**Observation Trace**:
The Runner's chronological, objective record of observable execution events between the
declared Evaluation Execution Case input and its actual output or failure. It exposes
enough of an otherwise black-box Node Cognitive Control Program for later assessment but
does not infer a quality judgment.
_Avoid_: an evaluator conclusion, a reconstructed hidden chain of thought

**Cognitive Evaluation Agent Workflow**:
A bounded multi-turn Agent workflow that receives an Evaluation Run Bundle, the relevant
Node Cognitive Control Contract, and an evaluation rubric. It may be run by a Coding
Agent or another approved evaluator interface to inspect artifacts and source seams,
then produce a read-only Cognitive Evaluation Review. In V1 it follows an Evaluation
Review Protocol rather than becoming a new runtime Controller or graph node. It never
alters the captured execution result, production prompt/code, rubric, or execution
environment, and it never triggers a new costly run on its own. A person explicitly
chooses whether and when to submit a retained Bundle for review; the Runner never starts
review automatically.
_Avoid_: a Python execution driver, a one-shot opaque LLM judge, an auto-fixer, a new runtime agent

**Evaluation Review Protocol**:
The concise, versioned review instructions and output shape used by a Coding Agent or
other evaluator to inspect an Evaluation Run Bundle. It gives V1 repeatability without
creating a separately loaded Python control, evaluator runtime, or evaluator graph.
_Avoid_: a production prompt authority, a second graph, a per-node Python judge

**Cognitive Evaluation Review**:
The structured, read-only result of a Cognitive Evaluation Agent Workflow. It contains
an immutable reference to the assessed Bundle; the execution Case and control version;
the Node Cognitive Control Contract, rubric, and Review Protocol versions; evaluator
identity or interface; time; Cognitive Evaluation Result; rubric evidence, confidence,
and unknowns; the likely owning layer and first source seam; and proposed follow-up such
as a new scenario or OpenSpec change. It follows the Evaluation Review Protocol, advises
a Coding Agent or human, and does not make production changes. Each review is a separate,
immutable Review Record that references, but never alters, its Evaluation Run Bundle;
more than one review may assess the same Bundle.
_Avoid_: a patch, an ungrounded narrative, a production-state write, a Bundle mutation

**Cognitive Evaluation Execution Status**:
The Runner's objective two-state account of one execution: `completed` when its declared
subject finishes, or `failed` otherwise. A failed bundle retains its typed phase/reason
and any material collected before failure, but is not retried by the Runner. A caller may
start a fresh isolated Runner execution instead. Execution Status is independent of the
Cognitive Evaluation Result.
_Avoid_: a quality grade, a provider error silently treated as a cognitive failure, retry state

**Node Cognitive Smoke Scenario**:
The minimum bounded, manually runnable Cognitive Evaluation Suite scenario for one
LLM-Bearing Node. It executes the declared production node branch through the Runner
under controlled inputs and budget, then preserves a private local, interpretable result
bundle for later rubric assessment. The versioned Evaluation Case registry identifies
which Nodes currently have Suite coverage; this definition makes no all-node coverage
claim.
_Avoid_: a unit test, a raw provider transcript, a claim that one run proves quality or that every Node has a scenario

**Node Evaluation Run**:
A Cognitive Evaluation Runner execution whose subject is one LLM-Bearing Node and an
explicit production branch. It is the primary evaluation lane because it isolates one
Node Cognitive Control Program while retaining the production prompt, bridge, and
deterministic admission seam.
_Avoid_: a copied model call, a whole-graph regression, an implied all-branches claim

**Flow Evaluation Run**:
A Cognitive Evaluation Runner execution whose subject is a bounded complete or declared
graph flow. It is a distinct, lower-frequency integration lane that observes how nodes
compose into a Research Outcome after Node Evaluation Runs establish their own baseline.
_Avoid_: a substitute for node-level diagnosis, an unbounded production Deep Research Run

**Cognitive Evaluation Result**:
The four-state cognitive assessment produced by a Cognitive Evaluation Agent Workflow:
`pass` when the observed behavior satisfies its rubric; `limited` when a declared,
inspectable quality or coverage limitation remains; `inconclusive` when the available
bundle cannot support an honest assessment; or `failed` when a critical cognitive rubric
fails. `limited` and `inconclusive` never silently count as pass. Execution failure
remains a separate Execution Status.
_Avoid_: a binary assertion, an unreviewed LLM-judge verdict, a Runner status

## Service Responsibility

**Deployment Owner**:
The person or organization that configures and maintains the model, web-research, and
other service prerequisites for a Deep Research deployment.
_Avoid_: Primary User, Smoke Test Operator

**Research Service Prerequisite**:
A configured capability, such as a model or web-research service, that the system
needs to perform research but that does not define the Primary User's research intent.
_Avoid_: User Decision, research scope

**System Recovery**:
The system-owned effort to restore progress toward a Research Outcome after an
operational interruption, within declared safety, cost, and evidence limits.
_Avoid_: a Primary User troubleshooting task, a User Decision

**Support Handoff**:
`planned`: a bounded, redacted support summary with no current producer, schema, or
public entry. It is not a current external retained diagnostic or Journal reader or
participant presentation after Bundle Loss. A future separately approved capability must
not create an implicit post-loss fallback. Its future behavior is outside this glossary
entry.
_Avoid_: a current support capability, an opaque diagnostic reference alone, a raw exception dump, a post-loss fallback

**Final Report Artifact**:
`final/report.md` is the current final-delivery artifact in a Run Bundle. Its presence
does not establish a Primary User public capability to reopen, copy, or export it.
_Avoid_: a public export contract, an inferred reader, raw graph artifacts

**Recovery Point**:
A durable, safe point in a Run Bundle's Research State from which the system can resume
legal research work without replaying an unconfirmed user decision while the Bundle is
available.
_Avoid_: a local UI cursor, an inferred phase
