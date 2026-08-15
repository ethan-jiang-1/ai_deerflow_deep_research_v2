## Context

`NodeExecutionRequest` currently carries an unconstrained mixture of objective,
expected output, and requested tool window. The shared prompt renderer preserves the
common policy and untrusted-data envelope, while the graph-owned catalog exposes the
sixteen direct builder branches. Neither surface states which static cognitive policy
belongs to a request or whether its requested tool policy can actually be bound at
runtime.

This is the first runtime change after the governance admission work. The governance
and prompt-catalog changes are archived, their accepted contracts form this change's
baseline, and their recorded full deterministic gates are not replaced by focused
cohort evidence. The first implementation task re-confirms that baseline and runs
the cohort's full deterministic gate. The proposal's six branches are a vertical
cohort, not evidence that all sixteen catalog branches have migrated.

## Goals / Non-Goals

**Goals:**

- Establish a small typed capability reference and a validated node-local cognitive
  policy resource for the first cohort.
- Keep static role/method/tool posture/authority/uncertainty separate from dynamic
  graph assignment and from parser/evaluator/materializer ownership.
- Make one renderer compose base policy, capability policy, trusted assignment/output
  contract, and untrusted data; make the runtime bridge enforce actual tools and
  numeric bounds rather than trusting rendered text.
- Prove each migrated branch's successful and highest-risk behavior at a real
  renderer/bridge/node seam, then record that evidence as a cohort matrix.

**Non-Goals:**

- Do not make any claim about model judgment quality, source selection quality, or
  live-provider performance.
- Do not migrate the remaining ten catalog branches, enable an LLM in a deterministic
  node, or add generic dynamic prompt configuration.
- Do not create a graph route, checkpoint writer, lifecycle result, retry policy, or
  provider dependency. Existing branch owners retain those behaviors.
- Do not change `backend/` or `frontend/`.

## Decisions

### 1. A capability reference is small; its governance projection is not a request field

Introduce a frozen domain `NodeAgentCapabilityRef` with exactly a stable capability
ID, a package identity rooted under `deerflow_deep_research.graph.nodes`, and a simple
relative Markdown resource name rooted under that package's `capabilities/` directory.
It rejects an absolute path, traversal, a non-Markdown name, or a package outside that
node namespace. `NodeExecutionRequest` also carries an explicit capability reference
with an exclusive ref invariant: `legacy` requires no ref and preserves the
pre-cohort renderer path; `required` requires exactly one syntactically valid ref.
Request validation rejects any other binding/ref combination before node invocation.
The loader then resolves that declared ref before model-visible work; an unknown,
missing, or mismatched local resource follows the existing node-owned non-success
path. A migrated request uses `required` together with that ref, the graph-owned
trusted assignment, expected output contract, source artifact refs, and numeric
execution window. The ref cannot carry prompt text, route data, parser name, repair
rule, evidence selector, or tool object.

Each migrated node package owns a `capabilities.py` declaration plus its Markdown
resource below `capabilities/`. Its first line is exactly one
`<!-- node-agent-capability: <JSON object> -->` metadata comment of at most 4 KiB
UTF-8, which is stripped before rendering; the remaining Markdown body is at most
16 KiB UTF-8. The comment decodes to exactly a version-1 object with the fields
`schema_version`, `capability_id`, `role`, `method`, `authority_limit`,
`completion_condition`, `uncertainty_boundary`, and `tool_posture`; unknown fields
are rejected. `capability_id` must match the ref. `tool_posture` is exactly either
`{"kind":"forbidden"}` or
`{"kind":"required","allowed_tool_names":[...]}`. The required name list is
non-empty, unique, and lexicographically sorted; a forbidden posture carries no tool
names. The Markdown body is static capability policy only. The agents layer validates
this metadata against the ref before it contributes text. No parsed field may select
a route, checkpoint writer, parser/evaluator/materializer, repair rule, evidence
selector, or live tool object, and the body never becomes an execution controller.

Node-owned governance projections record parser/evaluator/materializer, repair
owner/bound, catalog case, and evidence rows beside the declaration or test assets.
They deliberately do not enlarge `NodeExecutionRequest`.

Alternative considered: put every declaration and resource in an agents-global
registry. Rejected because it centralizes node cognition and forces agents to own
graph branch knowledge. Alternative considered: make the request carry full policy
text. Rejected because graph input would become mutable prompt authority.

### 2. Use a closed transitional legacy set, never a generic fallback

capability reference is transitional only during this cohort because ten direct
production builders have not yet migrated. The migrated catalog cases are exactly
`hitl1/semantic-intake`, `hitl1/semantic-intake-repair`, `wave0/worker`,
`wave0/repair`, `wave2-synthesis/synthesis`, and `wave2-synthesis/repair`. The closed
legacy set is exactly `hitl1/brief`, `hitl1/brief-repair`,
`targeted-evidence/claim-verifier`, `targeted-evidence/repair`,
`targeted-evidence/source-diagnostic`, `targeted-evidence/worker`,
`topic-planning/plan`, `topic-planning/plan-repair`, `wave1/worker`, and
`wave1/repair`. A migrated builder sets binding to `required` and supplies its exact
reference; a missing or malformed binding/ref is rejected before node invocation, and
an unknown, missing, or mismatched local resource follows the existing node-owned
non-success path before model construction. A non-migrated builder sets binding to
`legacy` with no reference, receives no inferred capability, and continues through
the existing legacy rendering path only until its own sequential cohort change
migrates it.

Once the inventory has no legacy branches, a final cohort removes the optional
compatibility path and makes the reference mandatory for every production request.
No fallback resource, default capability, or one-size-fits-all cognitive policy is
introduced by this migration.

Alternative considered: declare all sixteen resources immediately while testing only
three. Rejected because it creates a bulk prompt project with unproven node behavior.
Alternative considered: require the reference immediately and block every untouched
branch. Rejected because it prevents a reviewable vertical cohort.

### 3. Renderer resolves policy text; bridge enforces posture and budgets

The agents-owned renderer loads the package base policy and the validated local
capability resource, then composes exactly four layers in stable order:

1. base safety policy;
2. capability policy;
3. graph-provided trusted assignment and expected-output contract; and
4. delimited untrusted artifact/tool/source data.

It returns the rendered prompt plus a typed capability projection, not an arbitrary
system-prompt override. For `forbidden`, the projection requires
`tools_enabled=false`, no request call requirement, and no model-visible tools. For
`required`, it requires `tools_enabled=true`, `minimum_tool_calls >= 1`, a non-empty
call limit, and a non-empty resource set that is a subset of the selected
`ExecutionPolicy.allowed_tool_names`. The bridge resolves only the intersection with
configured actual tools; a required posture needs at least one such tool, not every
operator-provided Wave0 alternative. A mismatch, no permitted actual tool, or a
forbidden visible tool fails before `build_node_agent` or tool dispatch. Existing
middleware remains the authority for path, sandbox, cancellation, and cumulative
budgets.

Alternative considered: let a capability resource directly name live tool objects or
replace the bridge prompt. Rejected because resource text would gain runtime
permission and bypass the bridge's trusted configuration boundary.

### 4. Migrate one complete branch family at a time

The first cohort covers the six catalog cases listed above. It deliberately spans a
zero-tool semantic branch and repair, a required-tool source-intake branch, a zero-tool
source-intake repair, and zero-tool accepted-evidence synthesis and repair. The
capability IDs are `hitl1-semantic-intake`, `hitl1-semantic-intake-repair`,
`wave0-authoritative-source-intake`, `wave0-source-intake-repair`,
`wave2-evidence-synthesis`, and `wave2-evidence-synthesis-repair`. Wave0 normal and
repair are distinct because their tool postures differ. The Wave2 normal builder must
explicitly disable tools, and its node receives a dedicated zero-tool bridge policy
rather than the current base resolver's HITL1 bridge. For every case, the real node
still owns parsing, deterministic admission, repair, materialization, and route
decisions.

Each reference's package identity and resource filename are fixed for this cohort:

| Catalog case | Package identity | Resource file |
| --- | --- | --- |
| `hitl1/semantic-intake` | `deerflow_deep_research.graph.nodes.hitl1` | `capabilities/hitl1-semantic-intake.md` |
| `hitl1/semantic-intake-repair` | `deerflow_deep_research.graph.nodes.hitl1` | `capabilities/hitl1-semantic-intake-repair.md` |
| `wave0/worker` | `deerflow_deep_research.graph.nodes.wave0` | `capabilities/wave0-authoritative-source-intake.md` |
| `wave0/repair` | `deerflow_deep_research.graph.nodes.wave0` | `capabilities/wave0-source-intake-repair.md` |
| `wave2-synthesis/synthesis` | `deerflow_deep_research.graph.nodes.wave2_synthesis` | `capabilities/wave2-evidence-synthesis.md` |
| `wave2-synthesis/repair` | `deerflow_deep_research.graph.nodes.wave2_synthesis` | `capabilities/wave2-evidence-synthesis-repair.md` |

Alternative considered: migrate by node owner instead of direct branch. Rejected
because normal and repair branches can have different tool or candidate contracts.

### 5. Evidence uses branch x behavior x authenticity, not pytest volume

The cohort matrix has one row per migrated direct branch. Every row names its catalog
case, capability ID, declaration source, production entrypoint, success claim ID, and
highest-risk claim ID. The two claim IDs are distinct collected `TestEvidenceClaim`
records, so their selectors, behavior labels, and deterministic authenticity remain
independently checkable. Static declaration/resource and catalog checks are separate
from recording bridge and scripted real-node journeys. A test that exercises a
different branch, a generic owner-level test, or a raw pytest count cannot satisfy a
row.

The matrix is a test-owned governance projection. It does not claim live model
quality, nor does it become an execution registry.

## Risks / Trade-offs

- [The optional reference becomes permanent] -> The closed legacy inventory is
  mechanically checked and the follow-up removal condition is explicit.
- [Markdown resource becomes a second runtime authority] -> A bounded metadata
  header is validated and stripped, while only its policy body is rendered; runtime
  bridge/middleware keep all execution permission and admission authority.
- [Required tools are shown but not truly available] -> Recording bridge tests prove
  the permitted-tool intersection, one available Wave0 alternative, and the
  no-permitted-tool failure before model construction.
- [A repair path is hidden behind a happy-path capability] -> Each catalog case has
  its own matrix row; Wave0 normal and repair must retain distinct capability IDs and
  postures.
- [Wave2 silently borrows the HITL1 policy] -> Its normal request explicitly disables
  tools and mixed-recipe tests bind it to a dedicated zero-tool policy.
- [An accepted predecessor contract is superseded before implementation] -> Reconfirm
  the archived governance and catalog baseline and reject any active competing delta
  before changing the cohort.

## Migration Plan

1. Before implementation, confirm that the archived
   `define-node-agent-workflow-governance` and `make-node-prompts-auditable`
   contracts remain the accepted baseline, with no active competing delta for the
   catalog/runtime seam.
2. Add the domain reference, header/resource validation and composition seam, runtime
   posture admission, Wave2-specific bridge policy, and direct invalid fixtures before
   migrating a node.
3. Add the three node-local declaration/resource pairs and migrate the six catalog
   cases, with each case's catalog projection and scripted real-node journey green
   before the next family.
4. Register the six rows with distinct success and high-risk claim IDs and run focused
   checks, then the full deterministic gate. Subsequent changes migrate the remaining
   closed legacy set.

Rollback removes the cohort references/resources and restores the prior renderer path
for those branches as one unit. It creates no persistent data, checkpoint schema,
provider configuration, or external API migration.

## Open Questions

None. The remaining entry condition is mechanical: re-run this change's entry gate
against the accepted catalog and runtime contracts, including a clean protected-path
baseline, before implementation.
