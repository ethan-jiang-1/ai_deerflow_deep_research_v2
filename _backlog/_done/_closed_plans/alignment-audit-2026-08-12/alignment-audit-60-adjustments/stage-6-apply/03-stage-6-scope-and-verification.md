# Stage 6 Apply - Scope And Verification

> Change: `normalize-post-decision-terminology-status`
> Date: 2026-08-13
> Status: **APPLY VERIFIED - ARCHIVE NOT AUTHORIZED**

## Actual Documentation Result

| Adjustment | Changed explanatory authority | Explicitly unchanged |
| --- | --- | --- |
| D-001 | The allowlisted Runner, Case, Rubric, and short Rubric explanation in `CONTEXT.md`; a new ADR 0025 applicability postscript. They now distinguish identity/version plus unique criterion IDs as deterministic non-model metadata from review-only Rubric content and judgment, and retain the Runner's `completed` / `failed` status. | ADR 0025 title and historical body; CES/EVH/HITL1 main specs; code, tests, controls, and Run behavior. |
| D-002 | The allowlisted Bundle Loss, External Run Observation, Journal, and Support Handoff definitions in `CONTEXT.md`; ADR 0006's existing applicability postscript. They now distinguish supported Bundle-local reader/presentation from external records and physical residue, retain `planned` Support Handoff, and remove the A-004-quarantine status. | ADR 0006 title and historical body; RER/RUS/REJ main specs; external storage behavior, Support Handoff implementation, and A-004-T01 scenario titles. |

The first tracked-only scope check did not list the three untracked Stage 6 evidence
files. It was rerun using `git diff --name-only` plus
`git ls-files --others --exclude-standard`; the combined Stage 6 allowlist matched
exactly: the three apply evidence files, the planning-validation count correction,
`CONTEXT.md`, ADR 0006, ADR 0025, and the active change's `tasks.md`.

After that exact check, an unrelated user-owned modification appeared in
`openspec/CONTEXT.md`: an Authority Ladder explanation. It is outside this change,
does not overlap any Stage 6 target occurrence, and is deliberately not staged,
modified, or described as Stage 6 output. The concept-map work was already committed as
`b54eaea`; the Stage 6 apply baseline began clean and contains no Stage 6 edit to those
concept-map paths.

No `openspec/specs/`, `deep_research_harness/src/`,
`deep_research_harness/tests/`, `deerflow/`, `openspec/config.yaml`, or
`openspec/governance/` path is part of Stage 6 output.

## Checks

| Check | Result | Evidence / limit |
| --- | --- | --- |
| Exact occurrence and main-spec review | passed | D-001 text is limited to CES's identity/version plus unique criterion-ID boundary; D-002 text is limited to RER/RUS/REJ's reader/presentation/physical-residue boundary. No new requirement or conformance claim was introduced. |
| ADR postscript protocol | passed | ADR 0006 only revised its existing postscript; ADR 0025 only appended a dated postscript. Both titles and historical bodies are unchanged. |
| Changed ADR local links | passed | Each local `CONTEXT.md` / owning-main-spec target resolves from its ADR directory. No new link checker executable was introduced. |
| `openspec validate normalize-post-decision-terminology-status --strict` | passed | Planning/change structure only, not runtime conformance. |
| `openspec doctor --json` | healthy | Local OpenSpec root health only. |
| `python3 openspec/governance/check_agent_charter.py` | passed | Charter governance shape only. |
| `git diff HEAD --check` | passed | No whitespace errors; not an ownership or semantic proof. |
| Combined Stage 6 scope allowlist | exact match before the later unrelated user edit | Covers tracked diff and untracked Stage 6 apply evidence. |
| `cd deep_research_harness && UV_OFFLINE=1 make verify` | passed | Project governance, lock check, Ruff check/format, test assets, requirement coverage, and fast/integration/workflow deterministic targets exited zero. Fast JUnit records `2495` tests with no failures/errors/skips. The full gate still has the known environment limitation of four Gateway-stack integration skips; it does not prove physical/live/future behavior. |

Passing documentation/governance/deterministic checks does not prove secure erasure,
absence of residual bytes, every live/credentialed/third-party path, future behavior,
or universal semantic conformance. The D-001/D-002 records retain their earlier bounded
local-conformance evidence and proof limits.

## Remaining Work And Stop

All apply tasks through 3.5 are complete. `DEFERRED-TOOLING-CHANGE A-004-T01` remains
owned by a separate validator/scenario-rename change. Archive tasks 4.1 through 4.5
remain unchecked: a distinct archive authorization is required before closeout review,
preflight, archive, ledger completion, or commit.
