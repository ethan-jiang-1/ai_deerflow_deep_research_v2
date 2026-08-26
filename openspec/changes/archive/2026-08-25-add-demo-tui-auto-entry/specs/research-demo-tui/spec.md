# research-demo-tui Delta

> req: RED-010

## ADDED Requirements

### Requirement: Demo TUI provides an explicit zero-human-input auto entry

The standalone demo TUI SHALL offer an explicit auto entry for embedded-smoke
mode: once the local preflight passes, it SHALL dispatch one fixed research
start carrying the graph-owned scripted policy intent (`StartRun` with the
fixed question, `scripted=True`, and no declared `profile_intent`) without any
composer input, and SHALL reach a terminal outcome with zero human typing,
while rendering the shared run updates. The auto flag
SHALL be accepted only for embedded-smoke mode: the command line SHALL reject
the flag in other modes, and fixture and Gateway observer modes SHALL keep
their interactive behavior unchanged. The TUI SHALL NOT construct a profile,
answer HITL1 or HITL2 itself, or alter the graph-owned scripted policy — it
only submits the start and projects the shared lifecycle result. (`RED-010`)

#### Scenario: Auto entry dispatches a fixed scripted start after preflight
- **WHEN** embedded-smoke mode is launched with the auto flag and the local preflight passes
- **THEN** the TUI dispatches one `StartRun` carrying the fixed question, `scripted=True`, and no `profile_intent`, and reaches a terminal outcome with zero human input

#### Scenario: Auto flag is rejected outside embedded-smoke mode
- **WHEN** the auto flag is used without embedded-smoke mode
- **THEN** the command line rejects the combination at argument parsing, and fixture or Gateway observer mode retains its interactive behavior

#### Scenario: Scripted run passes HITL1 and HITL2 as graph-owned phases
- **WHEN** the auto entry starts a scripted run
- **THEN** HITL1 and HITL2 pass as graph-owned policy phases without a human-facing input prompt, and the terminal outcome comes from the shared lifecycle result
