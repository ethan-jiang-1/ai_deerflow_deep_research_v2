## Why

The six existing node-local `workflow.md` files are useful but form an incomplete,
non-uniform reader surface: five logical nodes have no maintenance projection, and
the current reader specification expressly permits no shared inventory or checker.
The archived cognitive-node contract is therefore not yet visible where maintainers
begin work, nor mechanically protected from a missing or misleading card.

This change makes the approved eleven-node reader contract concrete without changing
any model, tool, graph, state, or lifecycle behavior. It also carries the archived
Change 0 delta requirements into active main-spec synchronization, rather than making
the new reader surface depend on archive-only normative text.

## What Changes

- Add a `workflow.md` reader projection to each of the five remaining logical node
  packages and rewrite the existing six projections to one fixed, product-
  responsibility-first shape.
- Define a non-runtime static inventory/checker and focused fixtures/tests that prove
  exactly one projection per current logical node, required identity fields, and
  fixed structural headings while rejecting Charter branch labels as card identity.
- Add `cognitive-node-interface` as an active main capability, preserving the four
  requirements previously specified only by the archived Change 0 delta.
- Modify `node-agent-reader-interface` so its existing six package-local obligations
  coexist with the eleven-node interface and its checker rather than forbidding one.
- Register the reader-checking implementation and its focused test seam in the
  canonical project-structure governance inventory.

## Change Focus

- **Primary module / causal owner:**
  `agent/src/deerflow_deep_research/graph/nodes/<node>/workflow.md`; these are the
  reader interfaces being made complete and uniform.
- **Question:** How can a maintainer start at any logical node and identify its
  product responsibility, current mechanism, deterministic authority and correct
  first investigation seam without treating Markdown as runtime control or inferring
  an active model/human path?
- **Necessary adjacent/external contracts:**
  `graph/topology.py` answers the exact eleven-node denominator;
  `node-agent-reader-interface` answers the six current reader obligations;
  `project-structure.toml` answers where the checker and tests may live; the archived
  Change 0 deltas supply the accepted fixed reader vocabulary that this change
  synchronizes into active specs.
- **Evidence seam:** a deterministic reader-inventory checker and focused contract
  tests, with the current topology as the denominator; existing node-specific tests
  remain evidence for linked owners, not a claim that Markdown changes behavior.
- **Not in scope:** `backend/`, `frontend/`, prompt/capability bodies, `run_agent`,
  tool bindings, parser/materializer/ledger/gate logic, graph routes, checkpoints,
  lifecycle outcomes, model/human activation, or a quality/evaluation claim for any
  cognitive program.
- **Triggered charter policies:** change-admission, authority-and-projections

## Capabilities

### New Capabilities

- `cognitive-node-interface`: the fixed, product-responsibility-first non-runtime
  reader contract and the exact eleven-node reader inventory/checker obligation.

### Modified Capabilities

- `node-agent-reader-interface`: preserve and integrate the existing six reader
  projections within the now complete eleven-node reader surface.
- `project-structure`: register the canonical checker and test locations that enforce
  the reader interface without expanding the runtime package surface.

## Impact

- `agent/src/deerflow_deep_research/graph/nodes/*/workflow.md`, including five new
  package-local Markdown files and six rewrites.
- One deterministic, non-runtime reader checker plus focused fixtures/tests under
  canonical `agent/` locations, registered in project-structure governance.
- `openspec/specs/` requirements and the corresponding OpenSpec governance registry.
- No public DeerFlow API, runtime dependency, provider, stored state, or behavior
  change.
