## Why

Six already-approved requirements are present in their owning main-spec bodies,
registry, implementation evidence, and archived deltas but are missing from the main
spec `> req:` headers. The resulting ownership drift makes the clean repository fail
both requirement governance checks and prevents later changes from starting on a
green baseline.

## What Changes

- Add `EVH-030` to the existing `evaluation-hardening` main-spec header.
- Add `WAN-011` and `WAN-012` to the existing `wave0-node` main-spec header.
- Add `WON-011` and `WON-012` to the existing `wave1-node` main-spec header.
- Add `WOU-012` to the existing `work-unit-kernel` main-spec header.
- Make no requirement-body, runtime, test, registry, or evidence-mapping change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. This change restores ownership metadata for requirements whose approved text is
already present; `.openspec.yaml` therefore declares `skip_specs: true` rather than
inventing duplicate delta requirements.

## Change Focus

- **Primary module / causal owner:** `openspec/governance/` requirement identity governance owns consistency between registry entries and owning main-spec headers.
- **Seam classification:** wiring - the change repairs traceability links without changing requirement semantics or executable behavior.
- **Question:** Do all six approved requirements have exactly one owning declaration in their current main specs?
- **Necessary adjacent/external contracts:** `openspec/specs/{evaluation-hardening,wave0-node,wave1-node,work-unit-kernel}/spec.md` answer whether their existing requirement bodies are declared by their headers; no external contract is needed.
- **Evidence seam:** `check_project_reqs.py` and `check_project_req_coverage.py` must both pass from the repository root, with the other governance checks remaining green.
- **Not in scope:** Requirement prose, IDs, implementation, tests, evidence mappings, runtime behavior, `deerflow/`, or any downstream product code.
- **Triggered review policies:** change-admission

## Impact

Only the four owning main-spec header lines change. No API, dependency, runtime path,
test behavior, or DeerFlow surface changes.
