> req: RED-005

## ADDED Requirements

### Requirement: TUI exposes shared run inspection truth without local path inference

The Textual demo SHALL render the same opaque run reference, inspectability state,
retention truth, no-resume distinction, and exact `make -C agent demo-sessions
DEMO_ARGS="inspect <research_id>"` command supplied through shared run updates. It
shall not offer a platform-specific filesystem-open action. It SHALL not derive a
host path from a trace, action, option, or local stage state. Required asynchronous
publication and cleanup SHALL complete before the shared handler returns; synchronous
Textual unmount may only release locks already finalized and SHALL not perform or rely
on asynchronous session I/O. (`RED-005`)

#### Scenario: TUI shows the same paused-run reference as CLI
- **WHEN** the shared run experience projects a retained HITL-1 or HITL-2 session
- **THEN** the TUI presents the same reference and inspectability truth as the CLI without decoding a lifecycle `Command`
