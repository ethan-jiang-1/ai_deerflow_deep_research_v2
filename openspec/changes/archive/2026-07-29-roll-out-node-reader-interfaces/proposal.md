## Why

Wave2 established that a short, package-local reader projection can direct a
maintainer to the correct owner and proof seam without duplicating a node's control
flow. The other five LLM-bearing node packages still require a reader to reconstruct
their distinct model, human, work-unit, gate, and graph boundaries from several
modules before choosing a first edit.

## What Changes

- Add one non-runtime, package-local `workflow.md` reader projection to each of
  `hitl1`, `topic_planning`, `wave0`, `wave1`, and `targeted_evidence`.
- Add a source worksheet and one symptom-driven reader task for each package, based
  on its own cognitive job, deterministic authority, and lowest responsible test.
- Generalize the approved `node-agent-reader-interface` requirement from its Wave2
  pilot to the completed six-node LLM-bearing cohort, without imposing a shared
  Markdown schema or copying Wave2's repair flow.
- Verify cited source references and existing deterministic tests; retain any
  unresolved feedback or recovery facts only as implemented limitations.

## Change Focus

- **Primary module / causal owner:** The existing `node-agent-reader-interface`
  documentation capability, realized as five bounded reader projections colocated
  with their respective node packages.
- **Question:** Can the Wave2-proven reader-interface method let a maintainer reach
  each remaining LLM-bearing node's actual first modification owner and narrow proof
  seam without inventing a uniform control-flow document or a second authority?
- **Necessary adjacent/external contracts:** `hitl1-node`, `topic-planning-node`,
  `wave0-node`, `wave1-node`, and `targeted-evidence-loop` answer each node's
  required behavior and deterministic owner; `node-agent-capabilities` answers
  capability-body versus metadata and tool-enforcement questions; `node-prompt-catalog`
  answers rendered-prompt composition questions; `research-graph-lifecycle`,
  work-unit, and gate contracts enter only where the selected symptom crosses their
  boundary.
- **Evidence seam:** One manual symptom-driven reader task per package, plus the
  existing lowest-responsibility deterministic test cited by that interface.
- **Not in scope:** Runtime behavior, graph routes, state schema, capability bodies,
  prompt catalog, tool posture, test behavior, a shared documentation module,
  parser/schema/checker/index/generator work, `backend/`, and `frontend/`.
- **Triggered charter policies:** authority-and-projections, change-admission

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `node-agent-reader-interface`: Extend the approved reader-interface requirement
  from the Wave2 pilot to the five remaining LLM-bearing node packages while keeping
  authority with existing code, typed contracts, specs, and tests.

## Impact

- Adds five package-local Markdown reader projections under `agent/src/` and five
  source worksheets now archived under
  `_backlog/_done/_closed_plans/node-agent-control-flow-readability/`.
- Adds an OpenSpec delta and implementation/verification records for the rollout.
- Does not change APIs, dependencies, runtime behavior, `backend/`, or `frontend/`.
