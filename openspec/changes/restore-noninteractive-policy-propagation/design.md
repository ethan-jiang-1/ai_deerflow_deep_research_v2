## Context

See [proposal.md](proposal.md) for motivation. The verified local path has four
separate facts that currently do not compose: a scripted `StartRun` sends a policy
shape but not an explicit non-interactive marker; the reflected tool checks the
context with loose mapping/truthiness logic; `BundleGraphExecutor` creates initial
graph values without the policy; and its resume path invokes the existing checkpoint
without new initial values. `ResearchState` already has a policy field, HITL1 already
consumes it at its direct node seam, and HITL2 currently follows its ordinary
recommendation instead of a policy-selected `proceed` route.

The selected Bundle checkpoint is the durable graph-state authority. The request
bundle owns profile artifacts and Bundle-local State owns lifecycle status. Neither
CLI/TUI adapters nor the generic GraphHost may become a second source of policy or a
replacement checkpoint.

## Goals / Non-Goals

**Goals:**

- Admit one complete, strictly validated policy only from trusted runtime context.
- Carry that input through the existing tool/controller/executor chain only when
  trusted runtime composition supplies an executor, to a new graph's first state
  write, then prove checkpoint durability through an actual lifecycle execution.
- Preserve node-owned admission: HITL1 retains pair/language validation and HITL2
  retains the existing `proceed` route as the policy result.
- Keep deterministic evidence at the production `run_deep_research()` and real
  `BundleGraphExecutor` seam with controlled external dependencies.

**Non-Goals:**

- No demo recipe selection, CLI/TUI lifecycle controller, public tool-schema field,
  executor selection, generic-checkpoint fallback, or DeerFlow implementation
  change. An uncomposed fallback/full-fake lifecycle remains unchanged.
- No policy that can select a graph recipe, reply to an interrupt, invent a profile,
  override a terminal state, or recover a missing Bundle.
- No live provider result as proof of policy propagation.

## Decisions

### 1. Use one closed runtime action-input value

The runtime will introduce one immutable typed action-input value that represents
either ordinary interactive execution or the complete two-flag policy. The reflected
tool validates trusted runtime context before every input-bearing lifecycle dispatch;
validation requires actual boolean `true` values and rejects unknown/missing fields.
Only a new `start` turns a validated policy into the typed action input carried to the
controller. A later marked `resume` or `refine` remains subject to the same bounded
denial, but cannot create or replace a graph-state input. The
canonical marker is `non_interactive=True`; the existing trusted
`disable_clarification=True` marker remains a compatibility alias subject to the same
closed-policy validation. `ResearchRunExperience` emits only the canonical marker.
The public tool schema remains unchanged.

Passing a raw context mapping through the controller was rejected because every
consumer would need to revalidate it and a later action could accidentally become a
state writer. Letting a presentation adapter validate it was rejected because adapter
context is a projection and has no lifecycle authority.

### 2. Make the graph executor the sole initial-state writer

`BundleControl` will carry the typed input only on its new-Bundle start path when
trusted runtime composition has supplied a `BundleGraphExecutor`. That executor will
serialize the accepted policy into its existing initial graph values before the first
graph invocation. It will not update an existing snapshot; `resume`, reproject, and
refinement continuation receive no state-writing input, even if a later runtime
context was validly checked. The policy change will not instantiate or select an
executor: without one, the approved fallback/full-fake lifecycle retains its existing
behavior. This makes the composed Bundle checkpoint the sole later policy owner
without adding a Bundle-local State copy or a separate policy store.

Writing the policy directly from `tool.py`, keeping it in `ResearchRunExperience`, or
passing it on every invocation was rejected because each would create another writer
or allow a later context to override durable graph state.

### 3. Consume policy only at existing node-owned decisions

HITL1 will retain its deterministic comparison and language admission before writing a
degraded profile. A failed admission remains the existing blocked terminal with no
profile artifact. HITL2 will select its existing `proceed` outcome only when the
checkpointed policy allows it; otherwise it retains its ordinary autonomous
recommendation. Both successful policy uses will append bounded markers to the
existing execution trace instead of introducing an audit record or presentation-side
receipt.

Using a demo-generated answer or a new human-input control was rejected because it
would bypass node-owned validation and create new lifecycle authority.

### 4. Project scripted intent once from the run experience

For a scripted `StartRun`, `ResearchRunExperience` will supply both the explicit
non-interactive marker and full policy in the existing transport context. It will send
no policy on later actions, preserving the boundary that only the checkpoint can
control continuation. This is a projection of intent; the tool remains responsible for
admission and the graph remains responsible for effects.

### 5. Prove handoff, persistence, and negative paths separately

Focused tests will first make the missing handoff observable: strict malformed-policy
cases at the tool boundary; one `ResearchRunExperience` transport-context assertion;
HITL1/HITL2 direct node behavior; and a production `run_deep_research()` lifecycle
test that explicitly supplies an actual executor, controlled recipe/adapters, and a
reopened checkpoint. The integration test must observe real initial graph values and
later checkpoint consumption rather than asserting a hand-built node state. A separate
fallback test guards that policy propagation has not selected graph work. Test-evidence
metadata will be updated only for new or changed collected selectors and their changed
requirement links.

## Risks / Trade-offs

- [A strict policy parser rejects a previously truthy context] -> Preserve the
  existing bounded `INTERACTIVE_REQUIRED` outcome and add table-driven malformed
  cases so callers receive a stable denial rather than implicit coercion.
- [A same-start replay accidentally rewrites graph state] -> The controller passes
  action input only to the new-Bundle executor start path; replay and resume tests
  assert the checkpointed policy is unchanged.
- [A graph test hides the public handoff] -> Retain a production
  `run_deep_research()` integration test with a real executor, not only direct node
  fixtures.
- [Policy propagation silently changes full-fake behavior] -> Inject the executor
  explicitly in the lifecycle proof and retain a direct fallback regression that
  asserts no graph composition is selected.
- [Audit evidence becomes a second control surface] -> Use the existing bounded
  execution trace solely as an observation; route and lifecycle facts stay owned by
  the graph and Bundle state.

## Migration Plan

No persistent schema migration is required: the graph-state policy field already
exists and remains optional for pre-change Bundles. Deploy the strict admission and
one-time initial-state write together. Existing Bundles without the field retain
interactive behavior; rollback preserves their Bundle ownership and does not attempt
to reconstruct or inject policy from runtime context.
