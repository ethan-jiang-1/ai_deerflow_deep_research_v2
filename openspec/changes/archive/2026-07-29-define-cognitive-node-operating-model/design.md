## Context

This is Phase 0 of the cognitive-node-first program: a governance and reader
contract change, not an activation or runtime change. Its implementation surface is
limited to the existing change-local OpenSpec artifacts. A separately admitted
successor may author or rewrite all eleven node-local workflow.md reader projections
and any non-runtime shape checker.

The design corrects a semantic mistake in the first proposal: current direct model
branch discovery was allowed to lead the node taxonomy. Discovery is valuable
source-audited evidence about the current operating mechanism; it is not a durable
product responsibility, participation decision, commitment state, or authority
grant.

### Verified current behavior

graph/topology.py and tests/graph/test_topology_and_implementation.py fix the
ordered denominator at eleven logical nodes: bootstrap, hitl1, topic_planning,
wave0, wave1, wave2_synthesis, targeted_evidence, hitl2, rerun, readiness, and
final_delivery. This denominator is deliberately independent of worker/internal
source scans.

tests/contract/test_workflow_node_inventory.py finds exactly six production packages
with reachable direct run_agent references: hitl1, topic_planning, wave0, wave1,
wave2_synthesis, and targeted_evidence. The closed current direct-branch denominator
in tests/assets/node_agent_capabilities.py contains sixteen individual branches, and
tests/graph/test_node_agent_capability_cohort.py validates it. These sources prove
current wiring and capability bindings, not product quality or future product
commitment.

The focused controller bundle for bootstrap, rerun, hitl2, readiness, and
final_delivery is the lowest responsible evidence for the remaining five current
mechanisms:

| Logical node(s) | Source-audited current operating mechanism | Product decision recorded by this change | Deterministic fact owner |
| --- | --- | --- | --- |
| hitl1, topic_planning, wave0, wave1, wave2_synthesis, targeted_evidence | Active model loop; sixteen branches in total | Bounded cognitive program, current accepted | Node parser/materializer/controller, ledger/gate, and graph route owner remain distinct from model candidate. |
| bootstrap, rerun | Controller-only | Intentional deterministic-controller exclusions | Bundle binding and rerun scope/invalidation/generation contracts. |
| hitl2 | Autonomous deterministic continuation after validated Wave2 pass | Human decision/authorization is conditional and unresolved | HITL2 validator/node owns current legal proceed route; no generic user route menu exists. |
| readiness | Deterministic per-question fallback currently marks questions ready | Read-only evidence critic is accepted-but-deferred | Hard rules/report-plan materializer and node route writer. |
| final_delivery | Deterministic formatter/publisher fallback | Bounded report composition is accepted-but-deferred | Publisher/integrity boundary and node terminal/route writer. |

The current source/spec differences are preserved rather than repaired in this
change. HITL2 retains older human-decision language while its current normal path is
autonomous. Readiness specifies a bounded critic while the closest source explicitly
uses a deterministic fallback. Final delivery specifies an eventual bounded writer
and integrity behavior while current code uses the deterministic formatter/publisher
path. These observations define later Scope Card questions; they do not authorize
runtime edits now.

## Goals / Non-Goals

**Goals:**

- Define one product-responsibility-first, fixed reader contract for every logical
  node, with separate participation mode, commitment state, current operating
  mechanism, primary cognitive/control surface, deterministic authority boundary,
  and audit-only current model-branch evidence.
- Require the future all-node reader shape to use the same Wave2-style structural
  grammar while allowing each node's real product facts, symptoms, branches, and
  tests to differ.
- Preserve closed individual audit ledgers for all eleven logical nodes and all
  sixteen current direct branches, so aggregate language cannot hide an uncovered
  node, repair branch, diagnostic branch, or verifier branch.
- Keep cognitive program, human decision, deterministic guardrail, and wiring
  evidence distinct. The design makes the first cognitive/control seam visible
  without claiming that deterministic tests alone establish cognitive quality.
- Keep deterministic authority explicit: a model candidate or user choice never
  receives authority to write state, publish artifacts, mutate checkpoints, or
  select an executable route.

**Non-Goals:**

- Create, rewrite, parse, generate, or validate any workflow.md file.
- Add a model call, capability body, prompt builder, tool permission, structured
  candidate, checkpoint field, route, retry, lifecycle transition, HITL2 interrupt,
  human-decision UX, or UI adapter.
- Resolve source/spec drift for HITL2, readiness, final delivery, or Wave1.
- Synchronize deltas into accepted main specs; modify agent/, backend/, or frontend/;
  or use this review record as runtime registry or configuration.

## Decisions

### 1. Product responsibility leads the fixed reader interface

Every future conforming reader projection uses this exact semantic order:

1. Product responsibility: one specific user/research outcome, never a generic
   category such as active agent or controller.
2. Participation mode: bounded cognitive program, human decision/authorization, or
   deterministic control.
3. Commitment state: current accepted, accepted-but-deferred,
   conditional/unresolved, or intentional controller exclusion.
4. Current operating mechanism: source-audited active model loop, autonomous
   deterministic continuation, deterministic fallback, or controller-only behavior.
5. Primary cognitive/control program surface: capability/prompt, typed human
   decision contract, or deterministic controller as appropriate.
6. Deterministic authority boundary: the owner that validates/adopts candidates or
   choices and writes state, artifacts, checkpoints, or route.
7. Current model-branch evidence: a separate audit-only direct-branch statement.

The fixed title is Node — Product Responsibility. The mandatory structural headings
are Node Identity, From Symptoms, Three Cross-Module Facts, Route Facts, and
Evaluation and Verification Order. Three Cross-Module Facts contains exactly three
bounded facts. An active cognitive card begins with model-visible program and
feedback facts; an accepted deferred card begins with the future bounded question
and current fallback; a conditional human-decision card begins with the genuine
decision trigger; an intentional controller card begins with its safety rationale.

The previously overloaded phrase product cognitive role is retired. It conflated
product responsibility with participation mode and allowed current mechanism to
displace product intent.

**Alternatives considered:**

- A current mechanism first interface was rejected because a temporary fallback or a
  current direct model branch would silently redefine product identity.
- A generic category field was rejected because it cannot tell a maintainer what
  research outcome is at risk.
- Copying the Wave2 prompt or repair facts into every node was rejected; the shape is
  common, the factual contents are node-owned.

### 2. Charter binary classification is a separate source audit

The Charter-required node-agent/no-agent classification remains available only in a
separate Model-Branch Evidence Appendix. It means present or absent reachable direct
model branch today. It cannot occupy a reader title, product-responsibility column,
participation-mode field, commitment-state field, Scope Card identity, or authority
boundary.

The audit is closed at one individual row per current logical node and one
individual row per current direct branch. The topology set must equal the
eleven-node ledger; the capability fixture set must equal the sixteen-branch ledger.
If discovery changes either set, a new Scope Card is required before prose is edited
by inference.

**Alternatives considered:**

- Keeping the binary classification as the primary inventory was rejected because it
  would mark HITL2, readiness, and final delivery as permanently non-cognitive and
  would hide meaningful controller exclusions.
- Omitting the audit was rejected because the current branch denominator and
  capability bindings are valuable verification facts; their correct place is
  evidence, not identity.

### 3. Participation and commitment preserve honest differences

Current accepted active cognitive programs are not the same as accepted deferred
programs, conditional human-decision opportunities, or intentional controller
exclusions.

- HITL2 is conditional/unresolved. A later experience may proceed only when a real
  non-inferable preference or irreversible authorization is approved; raw internal
  routes are never a valid user experience.
- Readiness and final delivery are accepted-but-deferred. Their current fallback
  mechanisms remain visible until dedicated critic/composer activation changes
  provide bounded inputs, candidates, authority, and evaluation.
- Bootstrap and rerun are intentional deterministic-controller exclusions. Their
  cards explain why injecting a model or human decision would blur trusted
  binding/invalidation/generation authority rather than improve cognitive quality.

This distinction prevents an absent model call from becoming a false no-change
decision.

### 4. Reader projections are navigation, never runtime control

The reader interface routes an investigation to the first semantic owner; it does
not define runtime behavior. Code, typed contracts, accepted specs, and focused
tests own current facts. Capability Markdown may be model-visible policy in an
active node, but workflow.md is not a capability and cannot grant an invocation,
tool permission, route, state write, recovery policy, or lifecycle outcome.

Every reader therefore separates:

- trusted assignment/context from untrusted user, source, tool, or model material;
- requested capability posture from the bridge/runtime policy that enforces actual
  tools, budget, and sandbox;
- model candidate or human choice from parser/validator/materializer/gate/publisher
  admission; and
- a descriptive route field from the deterministic writer and consumer of an
  executable graph edge.

### 5. The existing six readers coexist with later uniform rollout

node-agent-reader-interface continues to own the six required package-local
projections. This change neither declares those cards nonconforming nor rewrites
them. cognitive-node-interface establishes the shared contract that the later
eleven-node rollout must apply to the six existing cards and five new cards.

This prevents phase 0 from pretending that a vocabulary change already delivered an
all-node reader interface, checker, or cognitive-program evaluation.

### 6. Semantic propagation is an explicit pre-apply gate

Before Phase 0 is applied, a review checks each proposal, design, delta spec, and
task artifact against the same field order and closed ledgers. It verifies that
product responsibility is specific and first; participation and commitment are
separate; current mechanism is source-owned; deterministic authority is named;
Charter/direct-run-agent evidence is audit-only; and no node/branch row is grouped
or missing. The source-audit tasks refer to the two closed ledgers, rather than
duplicating a task for every row.

## Risks / Trade-offs

- **A reader becomes stale after a later behavior change** → Later changes must
  re-run discovery and update the factual projection with the owning source/spec
  evidence; the reader never becomes source of truth.
- **An audit label again displaces product semantics** → The Product Responsibility
  Review precedes the audit appendix, and the semantic propagation gate rejects
  audit-only labels in identity fields.
- **A uniform structure invents a nonexistent loop** → Deferred, conditional, and
  controller cards use the same headings but name only real current seams and future
  activation boundaries.
- **Many green deterministic tests are mistaken for cognitive evaluation** → The
  16-branch ledger records current bindings and entrypoints only; later quality work
  must define and prove its own evaluation scope.
- **Phase 0 leaks into Phase 1 or runtime behavior** → Tasks reject workflow.md,
  checker, prompt, capability, model, tool, state, route, and lifecycle edits.

## Migration Plan

There is no deploy, data migration, runtime configuration change, or rollback:
Phase 0 changes planning artifacts only.

1. Re-run the topology denominator, owner/local-capability discovery, direct-branch
   cohort, and focused controller bundles. A different owner, branch, current
   mechanism, or drift fact stops the change for a new Scope Card.
2. Reconcile all eleven individual product-responsibility rows and all sixteen
   individual branch rows against that evidence, then perform the semantic
   propagation review across every artifact.
3. Validate this OpenSpec change strictly and confirm that only approved planning
   paths changed. Do not sync specs, archive, or begin Phase 1 without separate
   user direction.
4. Any successor that authors the eleven workflow.md cards or a checker is
   independently admitted; it must not be silently started by this change.

## Open Questions

- What exact non-inferable preference or irreversible authorization would justify a
  HITL2 decision experience, and would it use model assistance? This requires its
  own separately admitted decision-experience change.
- What bounded readiness evaluation can distinguish insufficient judgment from
  blocked repair without allowing a critic to control routing? This requires its own
  separately admitted activation change.
- What report-composition and citation rubric can support a bounded writer while
  preserving deterministic integrity/publishing authority? This requires its own
  separately admitted activation change.
- Which precise source/spec differences found during Phase 0 require their own
  behavior change rather than an interface correction? Each remains a new Scope
  Card decision.
