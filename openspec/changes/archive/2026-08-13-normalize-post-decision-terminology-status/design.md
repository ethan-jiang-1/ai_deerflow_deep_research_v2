## Context

See `proposal.md` for the motivation and scope. A-003 and A-004 are already
accepted and synchronized into their owning main specifications. The remaining
problem is narrower: current explanatory wording still answers both decisions too
broadly. In particular, the glossary says that a Rubric is never Runner input and
that an External Run Observation may outlive a Bundle without saying that it cannot
be a supported post-loss diagnostic/Journal reader or participant presentation.

This change is documentation-only. The main specifications remain the required
behavior owners; local implementation evidence remains only bounded current-path
evidence. The historical ADR bodies are decision records, not replaceable current
requirements.

## Goals / Non-Goals

**Goals:**

- Give the selected glossary terms and ADR applicability notes one precise,
  non-conflicting explanation of A-003 and A-004.
- Preserve the distinction between deterministic control metadata and Rubric content
  or cognitive judgment.
- Preserve the distinction between physical storage residue, supported retained
  readers, and participant presentation after Bundle loss.
- Protect the existing uncommitted concept-map work while a future apply changes the
  same `CONTEXT.md` file.

**Non-Goals:**

- No main or delta specification, runtime source, typed contract, test, fixture,
  registry, prompt, configuration, governance executable, archive, or DeerFlow path
  is changed.
- No current implementation claim, support-retention system, Support Handoff,
  external reader, secure-erasure guarantee, or A-004-T01 validator/scenario-title
  repair is created.
- No historical ADR title or historical ADR body is rewritten.

## Decisions

### 1. The apply allowlist is closed and occurrence-based

Only the following files may be edited during a separately authorized apply:

| File | Allowed occurrence(s) | Prohibited edit |
| --- | --- | --- |
| `deep_research_harness/CONTEXT.md` | Definitions of Cognitive Evaluation Runner, Evaluation Execution Case, Evaluation Rubric, Bundle Loss, External Run Observation, Run Event Journal, and Support Handoff; the short `Rubrics Are Case-Specific Review Authorities` explanatory section | Any other glossary term, the user-owned concept-map hunk, runtime/status assertions, or a copied requirement/task list |
| `deep_research_harness/docs/adr/0025-rubrics-are-case-specific-review-authorities.md` | One dated `## Current Status And Applicability (...)` postscript | Its title or historical body |
| `deep_research_harness/docs/adr/0006-layered-support-disclosure.md` | Revise only its existing dated `## Current Status And Applicability (...)` postscript | Its title or historical body |

Every other occurrence is a new finding. It is not permission to widen this change.

### 2. D-001 uses a two-layer Rubric/Runner explanation

| Surface | Before | Apply-time replacement boundary |
| --- | --- | --- |
| Runner and Case glossary definitions | A Rubric is categorically not read by the Runner; the Case omits the narrowly admissible Rubric metadata. | Deterministic admission may compare only Rubric identity/version and its unique criterion-ID set as non-model case-control-integrity metadata. |
| Rubric definition and short explanatory section | Rubric is read only by upper review and never becomes Runner input. | Criterion prose, weights, thresholds, evaluator guidance, cognitive result, and all quality judgment remain review-only. They do not enter subject fixtures, model-facing execution input, execution output, or Runner completion status. |
| ADR 0025 current-applicability postscript | No current-boundary note exists. | State the same distinction while preserving the historical body: Runner reports only `completed` or `failed`; it produces no cognitive quality verdict. |

This wording follows `cognitive-evaluation-suite` rather than treating an implementation
format check as a new behavioral rule. "Reads" must be qualified as deterministic
admission of the named metadata, never evaluation of criterion semantics.

### 3. D-002 separates three post-loss questions

| Surface | Before | Apply-time replacement boundary |
| --- | --- | --- |
| Bundle Loss / External Run Observation | Bundle loss ends State observation, while a generic external observation may outlive the Bundle. | A possible external record does not establish a supported retained diagnostic or Journal reader, or participant presentation, after Bundle loss. This does not say that no external bytes or generic record can exist. |
| Run Event Journal / Support Handoff | Journal is Bundle-local; Support Handoff is only labelled planned. | Supported retained diagnostic/Journal inspection and presentation require the available selected Bundle and are `unavailable` after loss. Support Handoff remains planned, has no current producer/schema/public entry, and cannot be a current or future implicit post-loss fallback. |
| ADR 0006 current-applicability postscript | It leaves Bundle loss in A-004 quarantine. | Replace only that stale status with the accepted boundary: Dedicated TUI remains dormant; Support Handoff remains planned; it is not current external retention or a post-loss reader/presentation. |

The wording must retain the existing no-authority boundary: a diagnostic, Journal, or
external observation cannot establish a Run, select it, authorize an action, recover
State, or turn inspection into retry, resume, recovery, or recreation. Typed terminal
category, opaque reference, recovery facts, and legal action are not retained-artifact
reads and may not be misdescribed as an external diagnostic presentation.

### 4. ADRs receive append-only current-applicability postscripts

ADR 0025 receives a dated postscript. ADR 0006 already has one, so its postscript is
revised in place. Neither action changes the title, prose, historical rationale, or
runtime authority of an ADR. Each postscript must name an owning current main-spec or
glossary route and explicitly say that it records current applicability only.

The rejected alternative is a historical-body rewrite. That would erase the reason the
old wording existed and blur an archived decision with a current behavioral contract.

### 5. The worktree baseline is a hard admission gate

`deep_research_harness/AGENTS.md`, `deep_research_harness/CONTEXT.md`,
`openspec/agent-charter/README.md`, and the untracked
`openspec/agent-charter/concepts.md` contain pre-existing concept-map work. An apply
agent must capture their status and diff before target edits. It may edit the precise
allowlisted glossary occurrences in `CONTEXT.md` only after confirming that the
concept-map hunk is preserved verbatim. If a user edit overlaps a target occurrence or
the baseline cannot distinguish ownership, it must stop for direction rather than
overwrite, stage, revert, or absorb the edit.

### 6. A-004-T01 remains separate

The legacy RER scenario titles `Verified bundle record enables session-bundle location`
and `Support-journal fallback retains observed origins` remain strict-validation
compatibility identifiers. Their scenario bodies already contain the selected
`bundle_journal` / `unavailable` behavior. Stage 6 neither edits specs nor declares
these labels resolved; `DEFERRED-TOOLING-CHANGE A-004-T01` remains owned by a separate
OpenSpec validator/scenario-rename change.

## Risks / Trade-offs

- **Metadata wording is misread as permission to pass Rubric content into execution**
  -> Limit every D-001 occurrence to identity/version plus unique criterion IDs, state
  the non-model/non-quality exclusions beside it, and review the full scoped diff.
- **"No supported reader" is misread as secure erasure or as a ban on every generic
  external log** -> State separately that the boundary is supported diagnostic/Journal
  reader and participant presentation, and make no physical-residue assertion.
- **A planned Support Handoff is read as a present external fallback** -> Retain its
  `planned` status and explicitly prohibit a current or implicit post-loss fallback.
- **An ADR postscript accidentally rewrites history** -> Use append-only/in-place
  postscript edits only and compare the historical body before and after apply.
- **The shared dirty `CONTEXT.md` loses user work** -> Record the apply baseline and
  stop on overlap; never use a broad replacement or restoration command.
- **An explanatory edit conceals a current/required mismatch** -> Do not claim new
  conformance. Preserve the existing bounded A-003/A-004 dispositions and record any
  newly observed implementation mismatch as separately owned deferred work.

## Migration Plan

1. Obtain separate explicit APPLY authorization and capture the protected worktree,
   HEAD, active-change, and exact occurrence baseline.
2. Create separate apply-time D-001 and D-002 Adjustment Records before editing.
3. Modify only the allowlisted glossary occurrences and ADR postscripts, using the two
   matrices above; do not edit historical ADR content.
4. Review the scoped diff against the six owning main-spec blocks and the Stage 4/5
   archived dispositions. Stop and record a new finding if any text requires a new
   behavioral decision.
5. Run the documentation/governance checks and required archive preflight. Record
   observed side effects and proof limits in both Adjustment Records.
6. Obtain separate archive authorization. Archive only after all tasks are complete;
   then re-establish the no-active-change baseline and advance the progressive ledger.

Rollback before archive is a scoped reversal of only the Stage 6 allowlisted changes,
after preserving user-owned changes and the evidence record. After archive, a corrective
OpenSpec change is required; archived material is never rewritten.
