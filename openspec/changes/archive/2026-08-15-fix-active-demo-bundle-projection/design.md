## Context

See `proposal.md` for motivation. Bundle-local Research State remains the lifecycle
authority. The verified failing result is a record-bearing
`active_bundle_exists` response with `status=active`; the shared presentation module
currently accepts its record fields and then attempts to construct a terminal update,
whose closed outcome vocabulary excludes `active`.

The all-real demo adapter currently derives its trusted scope solely from the retained
root and profile kind. This lets an available Bundle from one local process block every
later fresh demo start, despite the standalone demo's explicit lack of a cross-process
continuation promise. Fixture and local workbench commands intentionally rely on their
stable profile and must not inherit this behavior.

## Goals / Non-Goals

**Goals:**

- Preserve the lifecycle result as the only source for active/conflict facts.
- Give shared CLI/TUI consumers a closed, safe active-run outcome with a selected
  Bundle snapshot and one legal recovery direction.
- Let a later all-real demo process admit an independent run without touching retained
  Bundles from earlier processes.

**Non-Goals:**

- Recovering, reconciling, or deleting a prior graph/checkpoint.
- Adding a generic cross-process session controller or new Bundle store.
- Altering the fixture profile, graph topology, node/model behavior, or upstream
  DeerFlow code.

## Decisions

### Project active results before terminal construction

Add the closed `research.active` failure category to the shared run-experience
contract. After a result is validated as record-bearing and its safe observation is
published, classify either `active_bundle_exists` or `status=active` as `Fault` with
that snapshot. The lifecycle remains responsible for the conflict and legal controls;
the presentation layer only explains that it cannot join the active Run and does not
infer a pending response.

Alternative considered: classify every active result as checkpoint inconsistency. This
would incorrectly label a legitimate concurrently active Run as corrupted. Alternative
considered: make `active` a terminal outcome. That would falsely assert a completed
lifecycle and violate the existing closed terminal contract.

### Fresh scope only for all-real standalone adapter instances

Retain the project-local root and the fixture profile's deterministic scope. For an
adapter with a selected real model profile, append an adapter-generated opaque token to
the trusted local outer-thread identity. The token is generated within trusted demo
composition, is neither user input nor a persisted registry, and does not alter Bundle
identity. A new process therefore cannot discover or mutate a prior process's active
Bundle through its own start action.

Alternative considered: automatically cancel prior scopes during startup. This would
let a presentation adapter make a lifecycle decision about an unknown Run, violating
Bundle ownership and risking cancellation of valid work. Alternative considered:
delete the old directory. That would discard diagnostics and bypass lifecycle control.

### Render the selected Bundle for faults

When a `Fault` contains a snapshot, adapters render the same safe Bundle identity,
durability, and inspection truth already used by awaiting and terminal updates. This
adds no control authority and keeps the active-run recovery action actionable without
path disclosure.

## Risks / Trade-offs

- [Retained real Bundles accumulate across distinct demo processes] -> Existing bounded
  retention remains in effect; this change neither expands retention nor deletes
  records. Operators can use supported lifecycle/inspection operations.
- [A valid concurrent active Run is projected as a fault] -> The `research.active`
  category explicitly says it is non-terminal and directs query/cancel; no termination
  or retry is inferred.
- [Fixture/workbench scope changes accidentally] -> Scope isolation is conditional on
  a real model profile and receives a deterministic unit test.

## Migration Plan

No state migration is required. Existing retained Bundles remain in their original
scopes and are never rewritten by a later real demo launch. The known stale Bundle is
ended separately through the public lifecycle `cancel` action after confirming no
process holds its graph checkpoint. Rolling back code restores the earlier projection
behavior but does not modify Bundles created under the new code.
