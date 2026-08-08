## Why

The completed retained-event journal makes real Wave0 exhaustion observable, but its
closed `worker.failed` category cannot distinguish a provider/model invocation failure,
tool failure, structured-output parse failure, or source validation failure. The
credentialed run `r_e8w-cpL9Juk5Q2JEM7Dsv47hZefpnbRaxYtY9MxN6aI` exhausted all
three attempts at this boundary, so a focused safe classification is now needed before
any root-cause remediation can be justified.

## What Changes

- Classify reachable Wave0 node-agent, repair-parser, and result-validation failure
  branches into a closed redacted worker failure category.
- Carry that category through the existing attempt/exhaustion events and terminal
  incident without retaining raw model/tool bodies or exception text.
- Add scripted lowest-seam regressions for each category and one deterministic
  Wave0 exhaustion projection.

## Capabilities

### New Capabilities

- `deep-research-wave0-worker-failure-classification`: closed, redacted classification
  of real Wave0 worker failures across agent invocation, parser/repair, and validation.

### Modified Capabilities

- `research-run-session`: retained event/summary projections include the refined
  closed Wave0 worker failure category.
- `research-run-experience`: terminal incident and safe terminal presentation preserve
  the optional diagnosis separately from the existing lifecycle failure code.
- `gate-kernel`: writes the optional diagnosis only for a Wave0 exhausted outcome,
  while retaining sole authority for the existing route and terminal transition.
- `work-unit-kernel`: worker terminal/exhaustion projection preserves a safe failure
  classification without changing retry or gate authority.
- `wave0-node`: maps only its trusted node-agent, parse/repair, and typed submission
  boundaries to the new closed diagnostic contract.

## Impact

Changes are limited to `agent/` Wave0/runtime/work-unit contracts and deterministic
tests, plus OpenSpec and BUG-005 records. No provider API, raw log retention,
`backend/`, or `frontend/` change is in scope. The evidence is deterministic
workflow conformance at the node-agent bridge and work-unit seams; the captured live
run is only a redacted trigger, not proof of a provider-specific cause.
