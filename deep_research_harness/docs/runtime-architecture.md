# Deep Research Runtime Architecture

This is a human-facing orientation to the downstream runtime. It does not replace the
owning OpenSpec capability specification, typed contracts, Bundle-local State, evidence
ledger, content stores, code, or tests as authority for current behavior.

## Product Boundary

Deep Research is an independent downstream package. The Deep Research Harness owns the
lifecycle boundary for one continuing research run. Its controller is a nested Python
`StateGraph`, while bounded agent loops execute inside graph nodes. DeerFlow is the host
runtime and does not import this package. The generated
[logical topology](deep-research-topology.md) lists current nodes, terminal states, and
semantic edges.

Production node packages expose real factories only. Deterministic fixture adapters live
in the separate non-production `src_fake/deerflow_deep_research_fixtures/` package and
are excluded from the production wheel, reflected runtime, and Docker source mount. The
reflected `deep_research` host constructs the all-real recipe and never imports or
discovers fixture source.

## Harness And Run Bundles

The Harness receives trusted outer-conversation context and is the only component that
can create, locate, mutate, or control a Run Bundle. A fresh opaque `bundle_id` is the
Bundle directory identity, run identity, and public control target while the Bundle is
available. It is never derived from a user, conversation, message, or request text.

Before a new Bundle becomes discoverable, the Harness creates initial Bundle-local State
and required content roots in a contained staging location and publishes the complete
Bundle atomically. A transient Current Bundle Handle may help a later action, but it is
validated against the selected Bundle and cannot prove existence or authority. When no
Handle is present, discovery reads only Bundle directories and Bundle-local State within
the trusted scope. It never falls back to a session record, cache, diagnostic, or
external persistence namespace.

A Bundle-local non-terminal State is active, including when it awaits input. A terminal
current refinement round is ended. The Harness admits at most one active Bundle in a
trusted scope, while any number of available ended Bundles may remain inspectable.

If a Bundle is deleted, unreadable, or fails validation, it is unavailable permanently
for that run. The Harness does not recreate it, infer its State, or recover it from an
observation. A new independent run may still be started when the typed result permits
it. Cognitive Evaluation workspaces and bundles remain a separate domain and never
enter Deep Research discovery or control.

## Public Controls

The reflected `deep_research` tool supports `infra_probe | start | resume | status |
cancel | refine`. Its lifecycle actions consume the same typed Bundle result projected
to the graph, CLI, TUI, workbench, and agent instructions.

| Action | Contract |
| --- | --- |
| `start` | Creates a fresh Bundle only when the trusted scope has no active Bundle. |
| `resume` | Consumes only the correlated response for the current pending interaction. |
| `status` and `cancel` | Validate the selected Bundle before reading or changing lifecycle State. |
| `refine` | A nonblank text form submits one bounded direction. A textless form is only an explicit continuation for an available terminal `bundle_id` that already holds a pending direction. |

An available ended Bundle requires an explicit `bundle_id` for `refine`; the Harness does
not guess a retained ended target. A Bundle retains at most one pending direction. A
text-bearing `refine` remains distinct from `resume`, which consumes only the correlated
pending response, and from an Accepted Profile Note, which is canonical profile content
rather than a post-confirmation lifecycle write. An admitted direction does not replace a
pending response or overwrite an in-flight State writer.

The current round consumes a pending direction only after it synchronizes a completed
terminal boundary. Stopped, cancelled, and blocked terminal states preserve a pending
direction but do not restart it. A later explicit textless continuation may consume that
stored direction only when the selected terminal Bundle has capacity; it supplies no new
text and cannot reconstruct the stored text. A terminal Bundle with no future
full-rerun capacity projects `start`, whether or not it retains a pending direction.
The typed result separates the submitted action's code from the Bundle's pending/current
projection and legal next action. If a different Bundle is already active in the same
scope, reopening an ended Bundle returns the typed conflict or continuation outcome
instead of creating competing active work.

Known IM transports and non-interactive contexts refuse `start` and `resume`. Typed
results communicate the legal next action; adapters only present that fact and do not
infer alternative lifecycle paths.

## Ordinary Controller Loading

The recommended dedicated Agent has the ordered `deep-research-control` and `file:read`
groups. Before that Agent is provisioned or reported ready, Harness configuration verifies
one effective operator-owned `file:read` group with a public `read_file` binding. It never
creates, repairs, probes, or narrows that group; the full configured group is the actual
permission boundary, not a skill-path-only reader.

For a relevant ordinary non-slash turn, DeerFlow loads the canonical public controller
`SKILL.md` through `read_file` and records its skill reference before a later AI message
may make one exclusive `deep_research` call. Deferred `describe_skill` discovery can
precede that read but cannot substitute for it. The public skill has no `allowed-tools`
workaround, and its Markdown may propose a candidate only: tool schema, trusted runtime,
and Bundle-local lifecycle remain the effect authorities.

## State, Content, And Nodes

Each selected Run Bundle contains the durable Research State, evidence references,
pending interaction, pending/current refinement facts, terminal facts, and content for
that run.
State writes are versioned, atomic, and single-writer. Content stores receive a
runtime-bound Bundle reference rather than a caller-selected identity or filesystem
root, preserving containment and atomic publication for request, profile, work-unit,
evidence, and synthesis artifacts.

Bootstrap receives an already published Bundle and creates only contained bootstrap
content. HITL1 persists its pending interaction and profile facts in the selected
Bundle. Topic planning, Wave1, Wave2, evidence materialization, and node-agent bridges
receive the selected Bundle context or contained interfaces; they cannot select a
Bundle, derive an id, or become lifecycle writers.

The evidence ledger remains the accepted-evidence authority inside the selected Bundle;
candidate and evidence bodies remain content rather than lifecycle State. Worker and
node retry policies retain their owning components, but no diagnostic or presentation
surface can turn a retained observation into a lifecycle retry or recovery.

## Projections And Observations

The public tool, graph bridge, CLI, TUI, workbench, agent SOUL, and public skill use one
typed result containing bounded `bundle_id`, availability/lifecycle facts, and legal
next action where disclosure is valid. They do not expose a host path or construct a
lifecycle result from a report, session reference, diagnostic, or local cache.

Retained diagnostic observations may record bounded facts after a result has been
validated, including after a Bundle is gone. They remain read-only and cannot locate,
authorize, resume, cancel, refine, recreate, or reconstruct a Bundle. Local operator
routes are documented in [local operations](local-operations.md).

## Source And Structural Contract

Production source lives under `deep_research_harness/src/deerflow_deep_research/`,
fixture source lives under
`deep_research_harness/src_fake/deerflow_deep_research_fixtures/`, and tests live under
`deep_research_harness/tests/`. Only test processes and fixture demo child commands add
`src_fake` to their import path. See [`../AGENTS.md`](../AGENTS.md) for ownership
boundaries, the stable node-package shape, development order, and the current structure
contract.

The canonical machine-readable structure registry is
The application boundary is verified from this directory with:

```bash
UV_OFFLINE=1 make verify
```
