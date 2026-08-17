> req: PCG-001, PCG-002, PCG-003, PCG-004, PCG-005, PCG-006

## Purpose

Defines a product-neutral OpenSpec change-admission kernel, independently selectable
agent-workflow profiles, project-owned composition boundary, and evidence required to
export and prove a portable practice across repositories.

## ADDED Requirements

### Requirement: Portable Change Guidance has one product-neutral kernel

The portable practice SHALL provide one guidance kernel whose rules cover only
change admission, fact/decision authority, ownership, bounded context, evidence,
negative paths, recovery, migration, and deletion closure. Kernel documents and
validator inputs SHALL NOT require a product name, repository layout, framework,
local policy set, requirement identifier, runtime role, tool permission, or current
implementation fact. The kernel SHALL state that it guides design and admission only
and cannot create runtime behavior, authority, permission, or a native OpenSpec
operation. (`PCG-001`)

#### Scenario: Kernel is used by a different product
- **WHEN** an adopting repository supplies its own product, paths, owners, and enabled profiles
- **THEN** the unchanged kernel can evaluate its portable grammar without a Deep Research name, path, requirement ID, or DeerFlow assumption

#### Scenario: Guidance cannot grant runtime behavior
- **WHEN** a portable rule discusses state, recovery, tools, nodes, or lifecycle outcomes
- **THEN** it routes exact behavior to the adopting project's owning specification and executable contract rather than claiming authority itself

### Requirement: Reusable profiles are independent and explicitly enabled

The portable practice SHALL publish three independently selectable profiles named
`workflow-control`, `node-agent`, and `deerflow-downstream`. Each profile SHALL own a
bounded trigger set, canonical policy names, required authoring fields or review
records, and its portable validation rules. A project SHALL explicitly declare its
enabled profiles in local composition. A disabled profile SHALL add no selectable
policy, proposal field, review record, document-completeness obligation, or validation
failure. When one change triggers policies from multiple enabled profiles, the local
composition SHALL require the union of all applicable obligations without allowing
one profile to satisfy or suppress another. (`PCG-002`)

#### Scenario: Core-only adoption has no profile obligations
- **WHEN** a project enables the kernel and no profiles
- **THEN** profile policy names and review records are neither selectable nor required

#### Scenario: Multiple profile triggers compose
- **WHEN** a change triggers one policy from `workflow-control` and one from `node-agent`
- **THEN** validation requires both profiles' independent obligations and rejects a proposal that supplies only one review

### Requirement: Local composition owns project bindings

Each adopting project SHALL own a local composition that binds the portable kernel
and selected profiles to its product route, capability specifications, exact paths,
policy registry, proposal extensions, budgets, evidence commands, and decision
owners. The portable source SHALL NOT own or infer those bindings. Local composition
SHALL preserve one fact authority for each project-owned binding, SHALL distinguish
portable validation from local filesystem and policy admission, and SHALL reject an
enabled policy whose profile is absent or incomplete. (`PCG-003`)

#### Scenario: Two products retain different structure authorities
- **WHEN** two repositories adopt the same kernel and profiles but use different layouts
- **THEN** each local wrapper validates its own structure authority without copying either repository's exact paths into the portable source

#### Scenario: Local binding is incomplete
- **WHEN** a project enables a profile but omits its canonical trigger or review schema
- **THEN** local composition validation fails closed instead of silently weakening the profile

### Requirement: Node-agent authoring preserves an explicit cognition-versus-code gate

The `node-agent` profile SHALL contain one prominent first-read authoring route before
an agent navigates implementation for an LLM-bearing node or direct model branch. Its
filename and exact target path MAY be project-selected, but its complete semantic
contract SHALL remain present, reachable from the profile index, and mechanically
protected against omission or demotion.

The route SHALL first require classification as `cognitive-program`,
`deterministic-guardrail`, `human-decision`, or `wiring`; it SHALL NOT infer the seam
from the first file opened or from the presence or absence of a model call. For a
model-bearing behavior symptom it SHALL inspect, in order: the owning cognitive
control contract and bounded cognitive responsibility; prompt construction and trusted
versus untrusted model-visible context; structured candidate output, feedback
recipient, bounded repair, and stop condition; the lowest deterministic proof plus
applicable cognitive evaluation and its limitation; and only then the parser,
evaluator/materializer, ledger, gate, graph, and other deterministic handoff owners
that admit effects. Tool posture SHALL identify its runtime enforcer, and guidance,
prompts, and review records SHALL NOT grant tools, state writes, routes, retries,
permissions, or result acceptance.

For deterministic-guardrail, human-decision, or wiring work with no model-bearing
behavior symptom, the route SHALL start from the actual typed/domain/control/graph/
adapter owner, record why cognition is not causal, and SHALL NOT fabricate a prompt,
capability, or repair loop. A node's project-local workflow map MAY project exact local
sources, but SHALL remain a reader map rather than runtime configuration or a second
specification. (`PCG-006`)

#### Scenario: Coding agent does not default to traditional code
- **WHEN** an LLM-bearing node exhibits a wrong role, model-visible policy, context, tool posture, candidate, or feedback symptom
- **THEN** the first-read route requires cognitive contract, prompt/context, output/repair, and proof/evaluation review before admitting a parser, gate, route, bridge, or test as the causal edit

#### Scenario: Coding agent does not turn all node work into prompts
- **WHEN** the changed decision is deterministic admission, human semantic decision, or wiring and cognition is not causal
- **THEN** the route records the no-cognition rationale and starts at the authoritative typed/control/graph/adapter owner without inventing model-facing work

#### Scenario: Renaming the route cannot erase its semantics
- **WHEN** an adopting project renames or relocates the node-agent first-read document
- **THEN** profile completeness still requires every ordered cognition-versus-code decision, authority boundary, and non-model branch and rejects an abbreviated or demoted replacement

### Requirement: Portable validation is pure and local admission remains compatible

The portable grammar validator SHALL accept all content and configuration through
explicit inputs and SHALL NOT traverse a repository, read implicit product or manifest
files, execute commands, import a project wrapper, or depend on mutable wrapper
globals. It SHALL return deterministic structured validation results. An adopting
project SHALL retain a local wrapper for its filesystem, policy-set, path, budget, and
CLI contracts; extraction of the pure validator SHALL NOT silently change an existing
wrapper's declared command path, arguments, or success/failure semantics. (`PCG-004`)

#### Scenario: Pure validation runs without a repository
- **WHEN** a test supplies a proposal, enabled portable schemas, and validation options directly
- **THEN** the validator returns the same result without a working tree, product file, subprocess, or local wrapper import

#### Scenario: Local CLI compatibility is preserved
- **WHEN** the Deep Research wrapper delegates portable grammar evaluation to the kernel
- **THEN** its existing command path, arguments, and zero/non-zero outcome remain compatible while local checks stay outside the kernel

### Requirement: Portable guidance is an allowlisted, verified snapshot

The portable snapshot SHALL contain only the product-neutral core, selected profiles,
and pure validation kernel. The source SHALL record its revision, selected profile set,
relative paths, and SHA256 digest for every portable file. Verification SHALL reject
local composition, product material, project requirement/specification content,
architecture registries, tests, evidence, changes, archives, broken portable links,
source-specific literals, and digest mismatches. Future adopters SHALL own their local
bindings; this Change does not require or perform cross-repository adoption. (`PCG-005`)

#### Scenario: A denylisted file enters the snapshot
- **WHEN** the manifest includes product, local, test, evidence, specification, change, archive, or architecture material
- **THEN** verification rejects the snapshot instead of treating project authority as portable practice

#### Scenario: A portable file changes after manifest creation
- **WHEN** an allowlisted file's bytes no longer match its recorded digest
- **THEN** verification rejects the snapshot until the source intentionally publishes corrected bytes and new digests

#### Scenario: Source verification closes the snapshot
- **WHEN** neutrality, allowlist, link, digest, governance, strict Change validation, and Harness independence checks all pass
- **THEN** the snapshot is complete for this Change without requiring another repository or another Change
