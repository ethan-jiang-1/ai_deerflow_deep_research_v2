## Why

The glossary and two current-applicability ADR surfaces still preserve wording that
predates the accepted A-003 Rubric/Runner and A-004 post-Bundle-loss decisions. The
result is misleading explanatory authority: it says a Rubric is never a Runner input and
that an External Run Observation may outlive a Bundle, although the current contracts
make a narrower deterministic-admission distinction and prohibit a supported external
post-loss diagnostic reader or participant presentation.

Stage 6 projects those already-synchronized required contracts into explanatory
terminology and ADR applicability only. It neither changes behavior nor reopens either
product decision.

## What Changes

- Normalize the Evaluation Runner, Execution Case, Rubric, and review-authority glossary
  wording: deterministic admission may validate Rubric identity/version and unique
  criterion IDs as non-model control metadata; criterion content and cognitive judgment
  remain review-only, and the Runner remains `completed` or `failed` only.
- Normalize the Bundle Loss, External Run Observation, Run Event Journal, and Support
  Handoff glossary wording: a supported retained reader or participant presentation is
  Bundle-local and unavailable after Bundle loss; this does not claim physical erasure;
  Support Handoff remains planned and cannot be a current post-loss fallback.
- Add or revise only current-applicability notes for ADR 0025 and ADR 0006. Preserve
  their titles and historical decisions, state the accepted current boundaries, and link
  to their owning current specification or glossary term.
- Record one exact occurrence allowlist and separate D-001/D-002 Adjustment Records in
  Stage 6 planning evidence. Any other wording mismatch becomes a new finding rather
  than permission to expand the change.
- Preserve the existing uncommitted concept-map changes in `deep_research_harness/AGENTS.md`,
  `deep_research_harness/CONTEXT.md`, `openspec/agent-charter/README.md`, and
  `openspec/agent-charter/concepts.md`; they are not part of this change and must be
  re-baselined before any Stage 6 target edit.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/CONTEXT.md`; it is the current explanatory vocabulary that must faithfully route A-003/A-004 terminology to the already approved main-spec owners.
- **Seam classification:** wiring - this change reconnects explanatory vocabulary and ADR applicability notes to settled owners without changing a cognitive role, human decision, deterministic guardrail, or runtime behavior.
- **Question:** How can current glossary and ADR applicability wording state the settled Rubric/Runner and post-Bundle-loss diagnostic boundaries precisely while preserving the distinction between required behavior, bounded current conformance, planned capability, historical decision text, and deferred tooling work?
- **Necessary adjacent/external contracts:** `openspec/specs/cognitive-evaluation-suite/spec.md`, `openspec/specs/evaluation-hardening/spec.md`, and `openspec/specs/hitl1-node/spec.md` define the selected A-003 admission-metadata and non-quality-execution boundary; `openspec/specs/research-run-experience/spec.md`, `openspec/specs/research-run-session/spec.md`, and `openspec/specs/run-event-journal/spec.md` define the selected A-004 Bundle-local reader/presentation boundary; ADR 0006 and ADR 0025 retain historical rationale but require a current applicability boundary. No DeerFlow interface is required.
- **Evidence seam:** exact allowlisted occurrence review against the six owning main-spec blocks and the Stage 4/5 post-archive dispositions, followed by scoped documentation diff review and existing documentation/governance validation. No live, physical-storage, or universal runtime claim is created.
- **Not in scope:** main specs or delta specs, application code, typed contracts, tests, fixtures, registries, prompts, Runner behavior, support-handoff implementation/schema, external retention, `A-004-T01` scenario-rename tooling, `openspec/config.yaml`, governance executables, archived artifacts, DeerFlow, and any non-allowlisted explanatory file. The pre-existing concept-map worktree changes are preserved but not edited by this change.
- **Triggered review policies:** agent-information-map,authority-and-projections,change-admission

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. This change modifies explanatory terminology and historical-applicability notes
only; it changes no observable behavior or main-spec requirement. `skip_specs: true` is
therefore declared in `.openspec.yaml`.

## Impact

- Planning allowlist: `deep_research_harness/CONTEXT.md`,
  `deep_research_harness/docs/adr/0006-layered-support-disclosure.md`, and
  `deep_research_harness/docs/adr/0025-rubrics-are-case-specific-review-authorities.md`.
- Any later apply is docs-only and must preserve the pre-existing concept-map edits in
  the shared worktree. It must not modify code, tests, specs, configuration, governance
  executables, archives, or DeerFlow.
- The user must separately authorize apply, then separately authorize archive. Neither
  authorization is granted by this Stage 6 planning request.
