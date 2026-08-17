# Deployment Owns Research Service Configuration

Models, web-research services, credentials, and related configuration are required
Research Service Prerequisites, but they are owned by the Deployment Owner rather than
the Primary User. The dedicated Deep Research TUI may provide a separate setup path
for a local single-user deployment, but a research journey must not require a person
to interpret `.env`, provider names, or internal diagnostics in order to express or
advance their research intent.

## Current Status And Applicability (2026-08-13)

This postscript records current applicability only. It does not alter this ADR's
historical title, decision text, or runtime authority.

- **Current applicability:** Deployment Owner responsibility for service configuration remains current.
- **Non-current / planned / dormant scope:** The dedicated-TUI local setup path is dormant.
- **Current owner or route:** `src/deerflow_deep_research/runtime/` deployment configuration contracts
