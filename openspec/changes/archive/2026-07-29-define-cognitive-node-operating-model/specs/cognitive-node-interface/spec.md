> req: CNI-001, CNI-002, CNI-003, CNI-004

# cognitive-node-interface Delta Specification

## ADDED Requirements

### Requirement: Future cognitive reader projections use the product-responsibility-first fixed interface

When a separately admitted change creates or revises a node-local reader projection
under cognitive-node-interface, the projection SHALL lead with one specific Product
responsibility for its logical node. It SHALL then expose these separate fields in
this exact semantic order:

1. Product responsibility.
2. Participation mode.
3. Commitment state.
4. Current operating mechanism, marked source-audited.
5. Primary cognitive/control program surface.
6. Deterministic authority boundary.
7. Current model-branch evidence, marked audit only.

The title SHALL be Node — Product Responsibility. The projection SHALL use, in this
order, the fixed structural headings Node Identity, From Symptoms, Three
Cross-Module Facts, Route Facts, and Evaluation and Verification Order. Three
Cross-Module Facts SHALL contain exactly three bounded facts selected first by
product responsibility, then participation mode/commitment state, and finally
current operating mechanism.

Product responsibility SHALL name a concrete user or research outcome, not a generic
classification. Participation mode SHALL be bounded cognitive program, human
decision/authorization, or deterministic control. Commitment state SHALL be current
accepted, accepted-but-deferred, conditional/unresolved, or intentional controller
exclusion. Current operating mechanism SHALL be an independently source-audited fact
and SHALL NOT replace any of the first three fields.

This requirement establishes the contract only. It SHALL NOT itself create or
rewrite a workflow.md file, activate a model branch, create a human interaction,
require a checker, or change runtime behavior.

#### Scenario: Reader investigates an active bounded cognitive program
- **WHEN** a reader investigates a node with a verified direct model branch
- **THEN** the interface leads with the specific product responsibility, identifies
  bounded cognitive participation as current accepted, routes symptoms first to
  model-visible policy/context/tool/feedback seams, and separately names the
  deterministic candidate-admission and route authority

#### Scenario: Reader investigates a deferred, conditional, or controller node
- **WHEN** a reader opens a readiness, final-delivery, HITL2, bootstrap, or rerun
  projection whose current mechanism has no active model branch
- **THEN** the same fixed shape distinguishes accepted deferred cognitive
  responsibility, conditional human-decision opportunity, or intentional
  deterministic-controller exclusion from the source-audited current mechanism and
  does not fabricate prompt, tool, candidate, user-choice, or route behavior

#### Scenario: Contract is accepted before the all-node rollout
- **WHEN** this capability is accepted before a separately admitted reader rollout
- **THEN** the vocabulary and structural grammar are available for review while
  existing package-local projections remain untouched and no missing projection,
  checker, or runtime behavior is inferred from this contract alone

### Requirement: Product identity and current model-branch evidence remain separate and closed

An admitted change that defines or revises the cognitive-node reader population
SHALL keep a Product Responsibility Review separate from the Charter Model-Branch
Evidence Review. The Product Responsibility Review SHALL contain exactly one
individual row for every logical node in the source-owned topology denominator. Each
row SHALL separately state product responsibility, participation mode, commitment
state, current operating mechanism, and deterministic authority boundary.

The Model-Branch Evidence Review SHALL be audit-only. A Charter node-agent/no-agent
classification, direct run_agent discovery result, or branch count SHALL state only
whether a direct model branch is reachable in the current audited source. It SHALL
NOT appear as a reader title, product responsibility, participation mode,
commitment state, primary cognitive/control program surface, or deterministic
authority boundary.

When current direct model branches are in scope, the change SHALL keep one
individual branch row for every source-audited branch and capability reference. A
grouped node row, aggregate test, generic category, or another branch's evidence
SHALL NOT close a missing row. If the topology or branch discovery set differs from the
accepted review, the change SHALL stop for new admission rather than silently edit a
classification by inference.

#### Scenario: Audit evidence differs from product commitment
- **WHEN** HITL2 has no current direct branch while its product responsibility is a
  conditional human decision, or readiness/final delivery have no current direct
  branch while their responsibilities are accepted-but-deferred
- **THEN** the review records the absent current branch only in audit evidence and
  retains the distinct product responsibility, participation mode, and commitment
  state

#### Scenario: Discovery denominator changes
- **WHEN** a proposed source audit finds a missing, extra, or changed logical node
  or direct branch
- **THEN** the proposal identifies the source difference, opens a new Scope Card,
  and reconciles the individual node and branch ledgers before any reader
  classification changes

#### Scenario: A reviewer checks all-node coverage
- **WHEN** a reviewer compares the reader inventory against the current topology
  and direct-branch fixture
- **THEN** the reviewer can establish exact set equality for the individual
  eleven-node and sixteen-branch rows without relying on a group label or aggregate
  test count

### Requirement: Reader projections preserve deterministic authority seams

A reader projection admitted under cognitive-node-interface SHALL distinguish a
model candidate, a human choice, and the deterministic writer that admits a
candidate/choice or writes state, artifact, checkpoint, lifecycle result, or route.
It SHALL name the existing parser, validator, materializer, gate, ledger, publisher,
node handler, or typed contract with that authority.

For an active bounded cognitive program, From Symptoms SHALL begin with the
cognitive program before parser/graph symptoms, and Three Cross-Module Facts SHALL
cover model visibility, bounded loop/feedback, and candidate-to-authority handoff.
For a human decision, the facts SHALL cover the real decision trigger, bounded
human-facing brief/response binding, and deterministic choice validation. For an
intentional controller, the facts SHALL cover trusted inputs, deterministic
decision/recovery, and lifecycle/route authority.

The projection SHALL NOT create a model invocation, tool permission, graph route,
checkpoint write, retry policy, terminal disposition, or human interaction contract.

#### Scenario: Model candidate reaches admission
- **WHEN** an active bounded cognitive program returns a structured candidate
- **THEN** the reader directs the maintainer to the existing deterministic admission
  owner and does not attribute candidate acceptance, artifact publication, checkpoint
  mutation, or route choice to the model

#### Scenario: Human choice is considered
- **WHEN** a later change considers a HITL2 user decision
- **THEN** the reader distinguishes the user-visible decision from raw internal
  routes and identifies the typed validator and deterministic route writer that
  retain authority

#### Scenario: Controller-only node receives an upstream result
- **WHEN** bootstrap or rerun receives validated upstream state or a validated
  rerun scope
- **THEN** the reader explains its deterministic transition and does not infer that
  accepting an upstream result requires a model or human-decision layer inside the
  controller node

### Requirement: Deferred and conditional participation require separately admitted behavior

A projection whose participation is accepted-but-deferred bounded cognition or
conditional/unresolved human decision/authorization SHALL identify the later bounded
behavior change required before that participation becomes active. It SHALL name the
current fallback/controller and SHALL NOT add a generic model loop, capability,
prompt, tool posture, route menu, interrupt, or user interaction merely to make the
node appear cognitive.

An accepted-but-deferred cognitive projection SHALL name the future bounded question,
authorized model-visible input boundary, candidate schema, feedback/eval need, and
deterministic materializer/gate/publisher as activation prerequisites for that later
change to define. The projection SHALL NOT choose or imply their concrete behavior
before that separate admission.
A conditional human-decision projection SHALL state the genuine non-inferable
preference or irreversible authorization still required before experience design
begins. An intentional controller exclusion SHALL state the safety reason model or
human participation is the wrong seam.

#### Scenario: Readiness or final delivery activation is considered
- **WHEN** a maintainer considers activating the readiness critic or final report
  composer
- **THEN** a separately admitted change must define the bounded question, inputs,
  tool posture, typed candidate, deterministic authority, feedback/failure posture,
  and evaluation plan before a direct model branch is added

#### Scenario: HITL2 interaction is considered
- **WHEN** a maintainer considers changing HITL2 from its current autonomous path
- **THEN** a separately admitted human-decision contract must identify a genuine
  trigger, trusted response binding, meaningful user-visible choice, and
  deterministic legal route mapping before an interrupt or model assistance is
  added

#### Scenario: Controller exclusion remains meaningful
- **WHEN** a reader investigates bootstrap or rerun
- **THEN** the projection identifies the trusted binding or rerun-scope safety seam
  and rejects capability/prompt or generic interaction edits as the first response
  to a controller symptom
