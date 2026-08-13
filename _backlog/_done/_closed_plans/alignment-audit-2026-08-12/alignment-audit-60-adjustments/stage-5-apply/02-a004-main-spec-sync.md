# Stage 5 Apply - A-004 Main-Spec Sync

> Change: `reconcile-post-loss-diagnostic-authority`
> Date: 2026-08-13
> Tasks: 3.1, 3.2
> Status: **SYNCED - REQUIRED/CURRENT DISPOSITION RECORDED SEPARATELY**

## Normal OpenSpec Sync

The sync workflow used only the three delta paths returned by
`openspec status --change reconcile-post-loss-diagnostic-authority --json` and the
one current `openspec instructions specs` rule snapshot. The rules require observable or
mechanically verifiable downstream behavior without redefining DeerFlow internals, and
lowest-responsible zero-API deterministic evidence. No operation header was copied into
a main specification.

| Owning capability | Delta path | Main-spec path | Synced requirement blocks |
| --- | --- | --- | --- |
| Research Run Experience | `openspec/changes/reconcile-post-loss-diagnostic-authority/specs/research-run-experience/spec.md` | `openspec/specs/research-run-experience/spec.md` | `Failures are safe, categorized, and diagnosable`; `Shared failure updates expose bounded provider diagnostics and recovery disposition`; `Provider terminal diagnostic location is verified publication truth`. |
| Research Run Session | `openspec/changes/reconcile-post-loss-diagnostic-authority/specs/research-run-session/spec.md` | `openspec/specs/research-run-session/spec.md` | `Retained session diagnosis is summarized, correlated, and redacted`; `Retained session material is observation-only after Bundle authority migration`. |
| Run Event Journal | `openspec/changes/reconcile-post-loss-diagnostic-authority/specs/run-event-journal/spec.md` | `openspec/specs/run-event-journal/spec.md` | `An admitted Run has one correlated event journal before execution`; `Event journal inspection is read-only and safe for people and agents`. |

The seven modified blocks preserve their existing scenario sets. RER now removes every
required `support_journal` location/fallback and uses `bundle_journal` only for exact
verified contained publication; its unavailable path preserves the bounded terminal
facts without an external artifact. RUS and REJ now make reader, presentation,
physical-residue, and planned-Support-Handoff boundaries equally explicit.

## Sync Scope and Initial Validation

- `openspec validate --specs`: **49 passed, 0 failed**.
- `openspec validate reconcile-post-loss-diagnostic-authority --strict`: passed after
  the validation-compatible A-004-T01 disposition.
- `git diff --check` and `git diff HEAD --check`: passed with no output.
- The main-spec diff names exactly the three tabled main specs. No application source,
  test, typed contract, storage, configuration, governance executable, `CONTEXT.md`,
  ADR, archive, or DeerFlow path was changed by this sync.

These checks establish main-spec structure, change structure, whitespace validity, and
bounded changed-path scope. They do not establish runtime conformance, semantic proof
for every route, physical erasure, or future behavior. The separate required/current
record names the bounded conformance conclusion.
