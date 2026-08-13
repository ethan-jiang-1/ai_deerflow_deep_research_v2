## Why

Approved `research-run-experience` requirements still permit a provider diagnostic
to outlive Bundle loss through a support-journal fallback. Approved
`research-run-session` and `run-event-journal` requirements instead require Bundle-local
diagnostics and unavailable inspection after loss. These are incompatible required
answers for the same participant-visible diagnostic boundary.

The selected A-004 product decision is narrow and explicit: supported lifecycle
diagnostics are Bundle-local. After Bundle loss, supported inspection is unavailable;
no external Journal, diagnostic, or Support Handoff is read or presented.

## What Changes

- Modify the run-experience diagnostic-location and publication requirements to remove
  the external `support_journal` fallback and make `unavailable` the truthful result
  when an exact diagnostic record cannot be published to an available Bundle; use the
  existing typed contained-record location `bundle_journal` rather than the stale
  `session_bundle` label.
- Modify the retained-session and Event Journal requirements to state the same
  Bundle-local-only contract, including the distinction between possible physical
  residual bytes and an unsupported reader or participant presentation.
- Distinguish safe category, reference, recovery, and legal-action fields already
  projected from a typed terminal result from a readable retained diagnostic artifact:
  the former do not authorize an external record, reader, or later post-loss inspection.
- Preserve all existing no-recovery, no-selection, redaction, and lifecycle-authority
  boundaries. A later Support Handoff remains `planned`; this change does not approve
  external retention or a post-loss reader.
- Do not change application code, typed contracts, tests, storage, `CONTEXT.md`, ADRs,
  configuration, or DeerFlow. Apply-time conformance inspection must record a
  `DEFERRED-CODE-CHANGE` instead of altering implementation if current behavior still
  writes, reads, or presents an external diagnostic.

## Change Focus

- **Primary module / causal owner:** `openspec/specs/research-run-experience/spec.md`; it owns the participant-visible terminal diagnostic location and the current external-fallback requirement.
- **Seam classification:** deterministic-guardrail - the changed boundary constrains deterministic diagnostic publication and typed lifecycle projection, not a model role or human decision.
- **Question:** When a Bundle is unavailable or cannot contain an exact diagnostic record, what diagnostic artifact may be read or presented, and which safe terminal facts remain a typed lifecycle projection without granting an external post-loss reader?
- **Necessary adjacent/external contracts:** `openspec/specs/research-run-session/spec.md` answers what retained session material is readable and where it may live; `openspec/specs/run-event-journal/spec.md` answers the Event Journal's lifetime and post-loss inspection boundary; `deep_research_harness/src/deerflow_deep_research/domain/run_experience.py` answers the current typed diagnostic-location contract; `deep_research_harness/tests/` contains the lowest responsible deterministic publication/inspection evidence seam. No DeerFlow interface is required.
- **Evidence seam:** apply-time source-to-result inspection of the local terminal-publication, retained-session inspection, Event Journal paths, and typed diagnostic-location literal, followed by existing focused deterministic tests. Planning does not claim that these checks already prove all live or future paths.
- **Not in scope:** application code, typed contracts, tests, fixtures, storage, deletion implementation, new diagnostic retention, Support Handoff implementation, `CONTEXT.md`, ADRs, governance executables, `openspec/config.yaml`, archived changes, or the `deerflow/` gitlink or source.
- **Triggered review policies:** local-context,authority-and-projections,participant-outcomes,control-and-recovery,workflow-outcome-review,change-admission

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Bundle unavailable or deleted before supported inspection | Typed Bundle lifecycle result and available Bundle-local State | No diagnostic recovery owner; no external fallback is authorized | `unavailable`; no retained diagnosis is read or presented | Existing lifecycle-supplied fresh independent Run or other permitted non-diagnostic observation | Lifecycle/inspection result contract with a deleted or unavailable Bundle fixture |
| Exact terminal diagnostic cannot be published and verified in an available Bundle | Typed terminal incident plus the Bundle publication proof | Existing publisher performs no new recovery; no support-journal fallback | `unavailable` diagnostic location while the original terminal category and lifecycle authority remain unchanged | Existing terminal's single legal action; never resume or retry from a diagnostic | Publication-proof and shared terminal projection contract |
| Physical storage may retain bytes after Bundle loss | Outside the supported diagnostic contract; no supported Deep Research reader owns those bytes | None | No supported diagnostic observation follows from possible residual bytes | None is derived from those bytes | Documentation/spec review; not a claim of secure erasure or storage forensics |

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `research-run-experience`: remove post-loss external diagnostic fallback from the participant-visible terminal and failure contracts.
- `research-run-session`: make the retained-session diagnostic lifetime, readability, and planned Support Handoff boundary explicit.
- `run-event-journal`: make the Bundle-local Journal's supported lifetime and post-loss inspection boundary explicit.

## Impact

- The three listed main-spec requirements will be synchronized only after separately
  authorized apply work.
- Current `run_experience` typed fields, publication adapters, retained-session
  storage, and tests are evidence to inspect during apply, not authority for the product
  decision. If a current path retains, reads, or presents an external diagnostic, apply
  must record the gap as `DEFERRED-CODE-CHANGE`; this planning change does not repair it.
- Current accepted RER text calls the Bundle-contained location `session_bundle`, while
  the local typed/runtime contract and focused fixtures use `bundle_journal` for the
  same exact verified contained-publication condition. This delta corrects the owning
  requirement to the established typed literal. Apply must still record a
  `DEFERRED-CODE-CHANGE` if the inspected condition or any consumer differs; Stage 6
  owns only propagation of the accepted wording to explanatory surfaces.
- Ordinary downstream work neither modifies nor source-browses the `deerflow/` gitlink;
  this change neither needs nor authorizes that boundary.
