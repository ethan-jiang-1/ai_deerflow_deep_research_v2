# TUI Is The Primary User Interface

Deep Research has three entry interfaces with distinct audiences: the dedicated Deep
Research Textual TUI serves the Primary User, the CLI serves Smoke Test Operators and
debugging, and the API serves integration clients. The interfaces must project one
shared research outcome and recovery meaning, but the CLI's diagnostic convenience
must not define the Primary User experience. The current DeerFlow-wide Terminal
Workbench remains a host chat interface rather than the Deep Research TUI owner until
a separately approved integration can consume the Deep Research interaction contract.
This preserves a user-centered TUI while retaining a direct, scriptable route for
diagnosing real integrations.

## Current Status And Applicability (2026-08-13)

This postscript records current applicability only. It does not alter this ADR's
historical title, decision text, or runtime authority.

- **Current applicability:** The distinction between Primary User and operator concerns remains useful.
- **Non-current / planned / dormant scope:** The dedicated Primary-User TUI is dormant; the current route is the Dedicated Agent plus reflected tool.
- **Current owner or route:** `src/deerflow_deep_research/runtime/` deployment configuration contracts
