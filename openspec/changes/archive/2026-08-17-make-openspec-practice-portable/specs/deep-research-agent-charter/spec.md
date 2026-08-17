> req: DRC-001, DRC-005, DRC-012, DRC-014

## MODIFIED Requirements

### Requirement: A canonical Deep Research Change Guidance route is discoverable

The project SHALL maintain `openspec/change-guidance/README.md` as the sole local
routing index for Deep Research design/admission guidance. The route SHALL compose the
product-neutral kernel, independently enabled `workflow-control`, `node-agent`, and
`deerflow-downstream` profiles, and Deep Research-owned local extensions. It SHALL
route contributors to every canonical enabled policy whose trigger applies while the
change retains one primary causal owner or a bounded registered Program form.

Portable core/profile prose SHALL have one editable owner under `core/` or
`profiles/`; Deep Research paths, exact enabled-policy set, Program extensions,
information-map budgets, module routing, and operation closeout SHALL have one editable
owner under `local/` or another named local authority. The router SHALL distinguish
guidance, owning capability specifications, scoped procedures, current runtime facts,
and exact structure authority. No guidance or composition document SHALL create
runtime behavior, authority, permission, or a native OpenSpec operation. Old current
policy locations SHALL NOT remain as copies, aliases, or alternative routes after
cutover. (`DRC-001`, `DRC-005`)

#### Scenario: Contributor routes a local change without scanning the repository
- **WHEN** a contributor begins a Deep Research change affecting one owned module
- **THEN** the local router identifies the applicable core/local rules and every triggered enabled profile, then directs the contributor to the owning capability and evidence seam

#### Scenario: Multiple applicable policy triggers are all selected
- **WHEN** one change triggers policies from more than one enabled profile
- **THEN** the local composition requires the union of their canonical review obligations without allowing one profile to suppress another

#### Scenario: Multiple selected policies do not create runtime authority
- **WHEN** a contributor selects more than one triggered policy through local composition
- **THEN** all policies remain design/admission guidance and exact lifecycle actions, state, routes, permissions, and provider behavior remain in owning capability contracts

#### Scenario: Charter and policy library are discoverable from OpenSpec root
- **WHEN** a contributor opens `openspec/` to begin a Deep Research change
- **THEN** `openspec/README.md` reaches the sole local Change Guidance router, which reaches core, every enabled profile, local extensions, and owning specifications without a second route

#### Scenario: A behavior proposal is placed in its owning contract
- **WHEN** portable or local guidance identifies a proposed lifecycle action, state field, graph route, permission, or provider behavior
- **THEN** the router directs that proposal to its owning capability delta and no guidance document claims to establish the behavior

#### Scenario: Disabled profile cannot create an obligation
- **WHEN** a local composition does not enable a reusable profile
- **THEN** that profile's policies cannot be selected and do not create proposal fields, review records, or completeness failures

#### Scenario: Local composition does not duplicate portable authority
- **WHEN** Deep Research adds a path, Program extension, budget, or local policy binding
- **THEN** the local owner records only that binding and links to unchanged portable semantics instead of copying kernel or profile prose

#### Scenario: Retired policy path cannot remain current
- **WHEN** governance checks the post-cutover Change Guidance tree and inbound links
- **THEN** it rejects a duplicate old policy file, stale current link, second router, or unregistered member

### Requirement: LLM-node authoring follows one current-only cognitive route

The project SHALL maintain `deep_research_harness/AGENTS.md` as the application-owned,
current-only first read before a Coding Agent creates, changes, or reviews an
LLM-Bearing Node or direct model branch. It SHALL preserve the former node-edit map's
full semantic contract without depending on an OpenSpec path. The portable
`node-agent` profile defines and validates that semantic contract from the upstream
development framework; the Harness guide SHALL route work in this order: classify
`cognitive-program`, `deterministic-guardrail`, `human-decision`, or `wiring`; inspect
the Node Cognitive Control Contract and local capability; inspect prompt builder and
trusted/untrusted model-visible context; trace structured output, feedback, bounded
repair, and stop condition; inspect focused deterministic proof and applicable
cognitive evaluation; then inspect deterministic admission, materialization, ledger,
gate, and Python/LangGraph route owners.

The route SHALL make bounded cognitive responsibility, input authority, requested
method/tool posture and runtime enforcer, useful candidate and uncertainty standard,
feedback/repair, proof limitation, and deterministic handoff reviewable without
becoming runtime configuration, permission, state/route authority, or a second
behavior specification. For deterministic, human-decision, or wiring work where no
model-bearing symptom is causal, it SHALL require the author to name the actual owner
and why cognition is not causal; it SHALL NOT fabricate prompt or model-capability
work. Deterministic governance SHALL reject a missing, demoted, or semantically
incomplete route or any Harness dependency on OpenSpec content. (`DRC-012`)

#### Scenario: Coding Agent starts an LLM-node change from cognition
- **WHEN** a Coding Agent begins to create, change, or review an LLM-Bearing Node
- **THEN** the Harness guide and local router direct it to the node-agent first-read route before implementation navigation, and the route supplies ordered cognitive review before deterministic handoff owners

#### Scenario: Deterministic work is not forced into a prompt change
- **WHEN** a Coding Agent changes a deterministic, human-decision, or wiring surface with no causal model-bearing symptom
- **THEN** the route directs it to the actual typed, domain, control, graph, or adapter owner after recording why cognition is not causal, without requiring a model capability or prompt

#### Scenario: A missing authoring route fails governance
- **WHEN** any classification, cognitive contract, prompt/context, output/repair, proof/evaluation, deterministic-handoff, or explicit non-model branch is absent or demoted from the profile route, local router, or Harness guide
- **THEN** Change Guidance governance rejects the incomplete route before those documents can claim charter conformance

### Requirement: Deep Research product context is separately discoverable and non-authoritative

The project SHALL maintain `openspec/product/README.md` as the sole canonical OpenSpec
front door for the properties that distinguish Deep Research from other agent
workflows. It SHALL be a concise navigation map that identifies the product-specific
question/outcome, evidence and uncertainty posture, local workflow orientation, and
the exact existing owners a reader must open for terminology, approved behavior,
current facts, architecture, and proof. The information-map policy and deterministic
Change Guidance checker SHALL warn at 60 lines and reject the map above 80 lines.

`openspec/README.md`, `openspec/config.yaml`, the local Change Guidance router, and
governance navigation SHALL make this front door discoverable while retaining their
own bounded roles. The product front door SHALL NOT define or override vocabulary
owned by `deep_research_harness/CONTEXT.md`, behavior owned by a specification or
active delta, current facts owned by code/contracts/tests, exact paths owned by
`project-structure.toml`, or node authoring owned by its local guidance route. It SHALL
NOT add `product/instance.yaml`, a fixed outcome/workflow/capability schema, a second
glossary, runtime Markdown configuration, or another current product entry.
`openspec/product/deep-research.md` SHALL be retired in the same cutover without a
compatibility copy; historical archive text remains unchanged. (`DRC-014`)

#### Scenario: Reader finds Deep Research-specific orientation without loading generic guidance as a handbook
- **WHEN** a contributor needs to understand what makes this repository a Deep Research product
- **THEN** `openspec/` routes to `product/README.md`, which answers orientation and links each detailed question to its existing authority

#### Scenario: Generic authoring route remains bounded
- **WHEN** a contributor opens OpenSpec context, the local Change Guidance router, or governance navigation for ordinary work
- **THEN** each entry retains its authoring, policy-routing, or checker-navigation role and links product orientation only when needed without becoming a product handbook

#### Scenario: Product context cannot claim product behavior or runtime authority
- **WHEN** the front door describes terminology, required behavior, current runtime, structure, or proof
- **THEN** it links to the owning glossary, spec/delta, code/contracts/tests, structure registry, or evidence policy instead of copying or overriding the fact

#### Scenario: Old and extra product entries fail governance
- **WHEN** `product/deep-research.md`, a machine configuration file, or an unregistered Markdown member appears beside `product/README.md`
- **THEN** exact-member governance fails rather than accepting multiple current product surfaces

#### Scenario: Product context remains a reading map
- **WHEN** `product/README.md` exceeds its concise navigation role
- **THEN** governance warns at 60 lines and rejects above 80 lines, routing detail to its owner
