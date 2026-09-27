# Design

## Context

The workbench already holds typed readers: `ResearchGraphRecipe` (composition,
per-node `adapter_kinds`, prerequisites), the lifecycle's state, the trace
projector's frames, `NodeContextStore` captures, the adapter's
`create_work_unit_store`, and the host-side `OperatorWorkspaceReader`. The
`/context` pane rendered a summary because the capture content was never
projected; the driver now carries the pending request, and the capture store
answers content directly.

## Goals / Non-Goals

**Goals:** the operator can see the harness and its debug targets, and can read
what a captured model invocation was given and allowed. **Non-Goals:** no new
authority, no rebuilt prompts, no write in the exploration paths (read-only, no
lease), and no host paths in any pane.

## Decisions

1. **Read every fact through its owning typed reader.** Recipe facts come from
   the executor's recipe, Bundle facts from the lifecycle/trace projector, unit
   facts from the adapter's typed work-unit store (a first attempt listed the
   bundle's `work/` directory names directly - rejected because a typed owner
   already existed). Alternative - walking bundle directories - rejected.
2. **The drill-down is a selector, not a second pane.** `/context <node>#<n>`
   renders one invocation's bounded detail into the same pane; excerpts are
   capped (1200 characters for policy text, 800 for layer content) with an
   explicit truncation marker so a large prompt cannot flood the log.
3. **Layer content, not just hashes.** Runbook-031 promises the runtime MD bytes;
   showing the identity, sha256 and size without the content would leave the
   debugger unable to answer "what instructions did the model get", so each layer
   prints a bounded excerpt.
4. **Both id-taking entries list candidates.** The operator cannot know a Bundle
   id, so `/replay` mirrors `/attach`'s bounded candidate list with postures.
5. **One command for the evidence chain.** `make debugger-proof` sequences the
   five lanes; `make tui-experiences` runs the fifteen journeys alone.
6. **The experience suite is the acceptance layer, not a bigger unit test.**
   Each journey is an operator scenario with its own app and Bundle root, a
   realistic terminal size, and a dwell, printing PASS/FAIL per journey - it
   found the two dead ends and the missing action list in this very round.

## Risks / Trade-offs

- [/harness can drift from the recipe] → every fact is read from the recipe object
  at runtime; a mutation check confirms the assertions fail if the facts are
  removed.
- [A large capture could flood a pane] → excerpts are bounded with a marker, and
  the pane keeps its own max height.
- [The experience suite adds ~35 seconds to the evidence lane] → accepted: it is
  the only lane that asserts whole operator journeys, and it is not part of the
  default `make verify`.
