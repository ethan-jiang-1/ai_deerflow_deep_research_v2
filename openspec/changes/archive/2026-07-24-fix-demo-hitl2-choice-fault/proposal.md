## Why

The standalone fake demo renders a HITL2 option as `proceed: <description>`, but
the graph accepts only the option ID. Pasting the visible line is a normal invalid
choice; today its correctly classified `response_invalid` denial is masked as a
non-retryable `protocol.invalid_result` after trace validation, so the user is told
not to continue even though the retained graph remains safely suspended.

This is a P1 onboarding and lifecycle-presentation defect: the demo's visible
interaction contract disagrees with the value it accepts, and the shared
presentation layer discards useful failure semantics at a valid suspension.

## What Changes

- Make the credential-free `make demo` HITL2 prompt explicitly request a canonical
  option ID while retaining bounded human-readable consequences for each choice.
- Preserve an invalid choice as a safe, retryable input-validation outcome against
  the already suspended graph instead of terminating the local demo with an
  unrelated protocol-fault message.
- Make `ResearchRunExperience` classify only an exact, locally initiated
  `resume/response_invalid` non-record denial before applying trace-continuity
  rules that are meaningful only for a returned checkpoint/result projection;
  reissue an immutable copy of the previously validated HITL2 `AwaitingInput`
  rather than reconstructing state from the denial.
- Add deterministic public CLI and run-experience regression coverage, then register
  the smallest new evidence claims under the affected requirement IDs.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `demo-pipeline`: The standalone fake CLI's HITL2 choice rendering and invalid
  input recovery become an explicit, retryable user interaction contract.
- `research-run-experience`: Classified non-record lifecycle denials after a valid
  suspension retain their safe source category and cannot be masked by trace
  validation intended for valid returned lifecycle projections.

## Impact

- Affected code: the standalone CLI/TUI presentation adapters that consume the
  shared prompt feedback, the runtime-owned run-experience projection, and only
  the existing deterministic demo/run-experience test and evidence-registration
  surfaces needed to prove the behavior.
- No change to graph transition authority, checkpoint schema, retained-artifact
  safety policy, model/web calls, dependencies, Gateway, `backend/`, or `frontend/`.
- The established option IDs remain canonical; this does not add a free-form route
  parser or alter HITL2 graph validation.
