## Context

See `proposal.md` for motivation. Six node packages currently contain independently
shaped, hand-authored maintenance maps; the topology has eleven logical nodes. The
existing reader-interface spec deliberately permits no shared checker, while the
archived Change 0 delta defined a fixed all-node contract but was archived without
syncing its requirements into main specs.

`workflow.md` is a projection: code, typed contracts, approved specs, and tests
remain the source of truth. The design must make that projection easier to navigate
without creating a second authority or importing Markdown into the runtime.

## Goals / Non-Goals

**Goals:**

- Give every logical node one compact reader card with the same product-first entry
  shape and symptom-oriented navigation.
- Keep active cognitive, deferred cognitive, conditional human-decision, and
  intentional deterministic-controller cards equally honest about their current
  mechanisms.
- Add a deterministic check that catches missing/card-shape drift against the
  topology, and register its implementation/test paths in structural governance.
- Synchronize the archived cognitive-node contract as main-spec requirements through
  this active change.

**Non-Goals:**

- No runtime parse/render/load of reader Markdown; no prompt, capability, tool,
  model, parser, gate, route, checkpoint, lifecycle, state, or human-interaction
  change.
- No quality assessment of current cognitive programs, no branch-count-derived
  product classification, and no attempt to resolve deferred/conditional activation.

## Decisions

### One node-local card, with fixed human-facing headings

Every package under the source-owned logical-node inventory receives one colocated
`workflow.md`. Cards use the fixed title, ordered identity fields, and five headings
from `cognitive-node-interface`; prose below each heading stays node-specific. Active
nodes identify their bounded question, current capability/prompt/tool posture,
feedback recipient, candidate admission owner, and route consumer. Bootstrap/rerun
document trusted deterministic control; HITL2 documents its current autonomous
continuation and unresolved human-decision premise; readiness/final delivery document
their current fallback and activation dossier prerequisite.

This preserves node locality and lets every maintainer enter through the same small
interface. A generated central document was rejected: it would separate navigation
from the package it describes and become a shallow duplicate of source ownership.

### Checker validates a small declared reader interface, not prose quality

Add a zero-dependency checker under `agent/scripts/` with a pure validation surface
used by focused tests. It reads the topology denominator and each node-local Markdown
file, checking exact card presence, title/identity-field order, required headings,
and the non-runtime authority notice. It reports the logical node and violated
invariant. It does not interpret broad prose, judge whether a responsibility is
specific, validate arbitrary code/test references, execute imports beyond the
established topology discovery, inspect model branches as identity, or infer whether
an owner is behaviorally correct.

The focused inventory contract test extends the existing `workflow_nodes` evidence
surface with fixture mutations for a missing card, missing identity field, missing
commitment, forbidden Charter identity, bad heading order, and missing authority
notice. The
full architecture checker verifies that registered paths exist and that a registered
path cannot be placed upstream; it does not reject arbitrary unregistered files or
own Markdown semantics.

Structured frontmatter was rejected. It would introduce a second, parser-oriented
authoring surface and invite runtime reuse. Fixed visible fields are sufficient for a
reader interface and a bounded static checker.

### Main specs absorb the archived Phase 0 contract

This active change adds `cognitive-node-interface` with CNI-001 through CNI-005,
modifies NRI-001 to permit common validation, adds NRI-003 for coexistence, and adds
the project-structure requirement for validation paths. The archived Change 0
artifacts remain historical evidence only. Requirement identifiers are added to the
registry during implementation before any later archive, so active main specs rather
than history own the contract.

### Verification distinguishes card conformance from runtime evidence

Reader checks prove coverage and navigation shape only. Existing node-specific tests
remain linked proof seams for behavior facts named by a card; they are not rerun or
reclassified merely because a Markdown projection changed. Verification runs the new
focused checker tests, the project architecture checker, strict OpenSpec validation,
and the existing deterministic `agent` gate before closure.

## Risks / Trade-offs

- [Cards drift into second behavior specifications] -> Require the authority notice,
  source/spec/test links, and checker limits; reject line-by-line implementation
  duplication during review.
- [Uniform fields erase real differences between controller, deferred, and active
  nodes] -> Use the shared shape with explicit participation/commitment/current-
  mechanism values and node-specific symptom paths.
- [Checker becomes a fragile Markdown parser] -> Constrain it to stable visible
  fields/headings and authority notice; no source-reference validation or semantic
  prose scoring.
- [Archived requirements remain orphaned] -> Add CNI/NRI/PRS identifiers to the
  active registry and sync this change's delta specs at closure.

## Migration Plan

1. Add the checker and contract-test support without runtime registration.
2. Rewrite the six existing cards and add the five missing cards against audited
   current owners.
3. Register the new checker/test paths and requirement identifiers, record the
   focused test-evidence impact, then run focused validation and the full
   deterministic gate.
4. Sync the delta specs into main specs before archive. Rollback is a normal source
   revert; cards and checker have no persisted data, migration, or runtime consumer.
