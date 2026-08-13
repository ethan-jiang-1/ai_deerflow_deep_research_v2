# Stage 5 Apply - A-004 Synced Required/Current Disposition

> Change: `reconcile-post-loss-diagnostic-authority`  
> Date: 2026-08-13  
> Tasks: 3.1, 3.2, 3.3  
> Status: **SYNCED REQUIREMENT WITH BOUNDED LOCAL CURRENT CONFORMANCE**

## One Cross-Spec Answer

The three synchronized owning specifications now give the following single answer.
This is a required-behavior decision plus bounded downstream conformance evidence; it
does not claim universal implementation conformance or a storage-forensics result.

| Question | Required answer after sync | Bounded current observation | Proof limit |
| --- | --- | --- | --- |
| Physical-residue scope | RER, RUS, and REJ do **not** assert secure erasure or absence of physical residual bytes. Such bytes, if any, are not a supported retained record, reader, or participant presentation. | No physical-storage inspection was performed or needed for the supported-reader contract. | No claim about disk blocks, backups, caches, or residual-byte absence. |
| Supported retained reader | A retained diagnostic or Event Journal is readable only from an available selected Run Bundle. A missing, corrupt, foreign, unavailable, or deleted Bundle produces the bounded unavailable result. | The inspected publisher, workbench, and `RunObservationStore` paths resolve and recheck the selected available Bundle before contained I/O. | Limited to the finite downstream paths listed in `01-a004-local-conformance-inspection-and-focused-evidence.md`. |
| Participant presentation | A participant may receive the typed terminal's safe category, opaque reference, recovery/legal-action, and timeout-origin facts. A retained artifact may be presented only through the available Bundle reader; after loss there is no external artifact presentation. | Inspected CLI/TUI/workbench consumers use the shared typed terminal or available-Bundle inspection result; an unavailable result supplies no inspection target or diagnostic facts. | Does not establish behavior of an uninspected, live, future, or third-party presenter. |
| Terminal diagnostic location | A provider terminal is `bundle_journal` only if the available returned Bundle projection verifies the exact terminal reference and matching Bundle identity. Otherwise it is `unavailable`; no replacement reference or external fallback is allowed. | `RunFailure` permits only `bundle_journal` and `unavailable`; the local terminal decision checks availability, matching `bundle_id`, and exact reference. | Existing focused tests and source inspection are not an assertion about every execution route. |
| Support Handoff | Support Handoff is planned, not a current producer, schema, public entry, post-loss reader, or participant presentation. If later implemented, it is Bundle-available only and cannot create a post-loss Journal reader. | No inspected Support Handoff implementation, external write, read, or presentation was found. | Absence in the finite scan cannot prove no future or uninspected implementation. |

## Synchronized Requirement Blocks

| Capability | Main-spec requirement(s) read together | Alignment result |
| --- | --- | --- |
| `research-run-experience` | `Failures are safe, categorized, and diagnosable`; `Shared failure updates expose bounded provider diagnostics and recovery disposition`; `Provider terminal diagnostic location is verified publication truth` | Defines the typed terminal's safe facts and exact `bundle_journal` / `unavailable` publication truth. |
| `research-run-session` | `Retained session diagnosis is summarized, correlated, and redacted`; `Retained session material is observation-only after Bundle authority migration`; `Retained session inspection exposes truthful event-journal observations` | Makes available-Bundle containment and unavailable-after-loss reader/presentation behavior explicit. |
| `run-event-journal` | `An admitted Run has one correlated event journal before execution`; `Event journal inspection is read-only and safe for people and agents` | Gives the Journal the Bundle's supported lifetime and prohibits external historical Journal, diagnostic, and Support Handoff fallback. |

The synced requirements preserve the existing no-recovery/no-authority boundary and
redaction: retained observations cannot establish a Run, select it, authorize control,
or turn inspection into resume, retry, recovery, or recreation. They remove every
required external post-loss reader and presentation path.

## Required/Current Disposition

The bounded local inspection and four existing focused tests recorded in
`01-a004-local-conformance-inspection-and-focused-evidence.md` found no prohibited
external diagnostic, external Journal, `support_journal`, or Support Handoff crossing
and no stale `session_bundle` consumer. Therefore no `DEFERRED-CODE-CHANGE` was created
by A-004. This is **not** a declaration that no such gap can exist outside the inspected
paths.

The sole remaining A-004 discrepancy is **DEFERRED-TOOLING-CHANGE A-004-T01**: strict
OpenSpec validation preserves two legacy RER scenario titles, even though their
operative bodies now require `bundle_journal` or `unavailable` and prohibit external
fallback. The owner is a separately authorized OpenSpec tooling change that adds
scenario-rename support with a red validator test; a later RER maintenance change may
then retire the compatibility identifiers. Stage 6 terminology/status propagation does
not own this validator or scenario-shape work.

No code, test, typed contract, storage, configuration, governance executable,
`CONTEXT.md`, ADR, archive, or DeerFlow path was changed to reach this disposition.

## Evidence Boundary

This record relies on the synchronized main specs, the active change deltas, finite local
source-to-consumer inspection, and existing deterministic test evidence. It does not
prove live behavior, every environment, every future or uninspected path, physical
erasure, residual-byte absence, or semantic compatibility beyond the stated contracts.
