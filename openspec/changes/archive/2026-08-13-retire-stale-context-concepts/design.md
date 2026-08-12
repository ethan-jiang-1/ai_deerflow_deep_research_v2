## Context

See `proposal.md` for motivation and scope. Stage 2 is a documentation-authority
cleanup, not a behavior or implementation change. The audit has already separated
verified stale concepts (C-004, C-005, C-007 through C-011) from C-006, which was
withdrawn, and from two separate product-contract decisions:

- **A-003 / Rubric and Runner:** the selected criterion-ID admission-metadata contract
  must be reconciled through `reconcile-evaluation-rubric-authority`. This change must
  not reword evaluation glossary text that selects an execution authority.
- **A-004 / diagnostics after Bundle loss:** the selected Bundle-local-only contract
  must be reconciled through `reconcile-post-loss-diagnostic-authority`. This change
  must not assert external retention, an external reader, or a post-loss Support
  Handoff presentation.

The only intended future edit targets are the current explanatory surfaces listed in
the proposal. Main specs, source, tests, cases, registries, governance executables,
archives, and DeerFlow are evidence sources only. Nothing in this design grants an
additional runtime capability or changes a current contract.

## Goals / Non-Goals

**Goals:**

- Give the three workspace/bundle concepts distinct owners and physical meanings.
- Remove assertions that contradict current registered coverage or create an unowned
  requirement.
- Separate current artifacts, absent public capability, planned capability, and dormant
  historical route without treating a file path or ADR as an API contract.
- Preserve historical ADR text and add a consistent, explicitly non-authoritative
  postscript that identifies current applicability by sub-decision.
- Leave an auditable per-adjustment trail that records the exact change, risk, possible
  side effects, controls, and observed effect.

**Non-Goals:**

- Change any runtime behavior, product requirement, evaluation case, Runner, Rubric,
  report schema, handoff schema, user interface, public entry point, or lifecycle
  contract.
- Decide or partially implement A-003 or A-004.
- Generalize this cleanup into a broad rewrite or relocation of `CONTEXT.md` (C-006).
- Change an ADR title or historical body, mutate an archive, add an executable checker,
  or inspect/modify DeerFlow source.

## Decisions

### 1. Use an occurrence allowlist and a six-state classification

Before editing, create an apply-side evidence file in
`_backlog/plans/alignment-audit-2026-08-12/alignment-audit-60-adjustments/stage-2-apply/`.
It must classify every proposed occurrence as exactly one of:

| Classification | Meaning | Stage 2 handling |
| --- | --- | --- |
| `keep-current` | A verified current fact with a named owner | Retain or tighten only enough to preserve the fact. |
| `retire` | A completed, unsupported, or falsely universal current claim | Remove or replace it; do not turn it into a roadmap promise. |
| `relocate-owner` | A current fact is present but attributed to the wrong owner/surface | Point to the named current authority without duplicating a contract. |
| `planned` | A product direction lacks a current producer, schema, or public entry | State that it is planned and no more. |
| `dormant` | Historical direction is preserved but has no active commitment | Preserve rationale and current alternatives; do not call it cancelled. |
| `quarantine` | Correct wording would settle A-003/A-004 or another frozen contract | Make no semantic edit; record the future owning change. |

The table has six named states because `quarantine` is a stop condition rather than a
content disposition. A row also names its C identifier, exact source line/term,
current owner or evidence source, intended target file, risk control, and review
result. Any new occurrence outside the proposal allowlist is a new finding, not
permission to extend this change.

**Why this over global cleanup:** the same words occur in history, specs, and runtime
facts with different meanings. An explicit occurrence record prevents a text search
from turning into an unreviewed semantic rewrite.

### 2. Preserve the three workspace/bundle distinctions

The revised terms must retain this relationship:

| Concept | Owner | Meaning | Must not be called |
| --- | --- | --- | --- |
| DeerFlow host workspace | DeerFlow host environment | Host-level working context used to run the downstream application | an evaluation workspace or Deep Research Run Bundle |
| Deep Research Run Bundle | Deep Research runtime | Durable, independently deletable record of one Deep Research Run | a shared host workspace or evaluation output |
| Evaluation Run Workspace | Cognitive Evaluation Runner | Fresh private execution directory for one evaluation invocation | host workspace, reusable resume directory, or Deep Research Run Bundle |
| Evaluation Run Bundle | Cognitive Evaluation Runner | Immutable record sibling to the Evaluation Run Workspace under one execution root | a child directory inside the workspace |

The C-004 wording may say the Runner creates a workspace and bundle as siblings under
one execution root. It must not change that physical arrangement, assert a new storage
contract, or infer a relationship for Deep Research Run Bundles.

### 3. Retire stale evaluation wording without changing evaluation authority

C-005.a removes future-tense phrases such as "new Suite" and a completed V1 structural
change obligation. The retained text continues to identify `evals/control/`,
`evals/runs/`, the Runner source owner, and the separate role of `tests/eval/`.

C-005.b replaces the current glossary's archived-change dependence with the extant
`local-context` policy pointer. Historical changes remain unmodified and may be used
only as history, not as current authority.

C-007 changes only the policy-cardinality description in `openspec/CONTEXT.md` and
`openspec/agent-charter/README.md`: a change has one primary causal owner and may select
multiple canonical policies when each is actually triggered. The `agent-information-map`
policy applies because the Charter route is a contributor entry surface: retain its
short routing role and link to policy detail rather than duplicating selection rules.
The wording must not make every policy mandatory, change checker behavior, change
`openspec/config.yaml`, or imply a policy creates runtime authority. The previously
reported singular wording in `deep_research_harness/AGENTS.md` is not an independent
target: its comma-separated Focus Card instruction is compatible with multiple selected
policies and no verified contradiction was found.

**Rejected alternative:** rework the runner/rubric definitions in this change. That
would cross the A-003 quarantine and pre-empt a main-spec reconciliation.

### 4. Make coverage and review claims no stronger than their evidence

For C-008, retain the definition of a Node Cognitive Smoke Scenario, but state that
the versioned case registry identifies current Suite coverage. Do not claim every
LLM-Bearing Node has such a scenario, and do not turn all-node coverage into a new
Stage 2 roadmap, case, or requirement.

For C-009, retain the structured, immutable Review Record and four-state result. The
wording must continue to say that `limited` and `inconclusive` never silently count as
`pass`, but it must remove the glossary-created claim that they require an independent
human-readable report. This is a retirement of an unowned current requirement, not a
claim that structured records are an already-delivered report experience.

**Rejected alternative:** state that a JSON or structured record is automatically a
complete reader experience. That would replace one unsupported product claim with
another.

### 5. Split artifact fact from capability status

The following disposition is fixed for this change:

| Concept | Status and wording boundary |
| --- | --- |
| `final/report.md` in a Run Bundle | `keep-current`: a current final-delivery artifact; its presence alone creates no Primary User public capability. |
| Primary User reopen/copy/export | `retire`: no current public entry; do not label it planned or create a future commitment. |
| Support Handoff | `planned`: no current producer, schema, or public entry. Do not state retention, reader, or participant-presentation behavior after Bundle loss. |
| Dedicated Primary-User TUI | `dormant`: historical route with no active commitment; the current route remains the Dedicated Agent and reflected `deep_research` tool. |
| Local-First deployment based on that dedicated TUI | `dormant`: not an active product route; this does not change the separate local evaluation surface. |

The revised glossary may rename the current report term to `Final Report Artifact` so
the artifact is not confused with export capability. It must not add an export command,
public reader, authorization rule, retention promise, handoff data shape, or UI.

**Rejected alternative:** label every absent capability `planned`. The user explicitly
approved `planned` only for Support Handoff; report export has no such commitment.

### 6. Append, never rewrite, ADR status/applicability postscripts

Each targeted ADR receives the same postscript heading and three-part boundary:

```markdown
## Current Status And Applicability (<apply-date>)

This postscript records current applicability only. It does not alter this ADR's
historical title, decision text, or runtime authority.

- **Current applicability:** ...
- **Non-current / planned / dormant scope:** ...
- **Current owner or route:** ...
```

The bullets must be individualized as follows:

| ADR | Current applicability | Postscript boundary | Required current-owner/route link |
| --- | --- | --- | --- |
| 0002 | The distinction between Primary User and operator concerns remains useful. | Dedicated Primary-User TUI is dormant; current route is Dedicated Agent plus reflected tool. | `[deployment-configuration](../../../openspec/specs/deployment-configuration/spec.md#requirement-dedicated-agent-is-provisioned-in-the-effective-user-scope)` |
| 0003 | Deployment Owner responsibility for service configuration remains current. | Dedicated-TUI local setup path is dormant. | `[deployment-configuration](../../../openspec/specs/deployment-configuration/spec.md)` |
| 0006 | No new current Support Handoff behavior is created. | Dedicated-TUI presentation is dormant; Support Handoff is planned; Bundle-loss semantics remain A-004 quarantine. | `[Support Handoff](../../CONTEXT.md)` as a current terminology/status entry only, not a behavior contract, after C-010.b |
| 0008 | Existing Bundle lifecycle/isolation is unaffected. | The dedicated-TUI Local-First first-product route is dormant. | `[deep-research-harness-run-bundles](../../../openspec/specs/deep-research-harness-run-bundles/spec.md)` |
| 0010 | `final/report.md` remains a current Bundle artifact. | Its historical Primary User inspect/copy/export claim is non-current; no planned export commitment is created. | `[final-delivery-node](../../../openspec/specs/final-delivery-node/spec.md)` |

No postscript may call an entire ADR obsolete, reinterpret old prose as a current API,
or supply the A-004 retention answer. `<apply-date>` is the single ISO-8601 calendar
date when all five postscripts are applied; it must not be prefilled from planning. Its
`Current owner or route` bullet must contain the designated relative link above, and
apply validation must confirm that the resolved target and required heading (when named)
exist. The 0006 link records only the C-010.b terminology/status disposition; it must
not be read as a current Support Handoff behavior owner. Before appending, the apply
record captures the SHA-256 and byte length of each existing ADR. After appending, it
verifies the preexisting byte prefix is unchanged and that the remainder begins with the
one approved postscript heading. If any preexisting working-tree content differs from
the expected prefix, stop; do not overwrite or normalize it. A documentation tool that
does not understand the note still sees the untouched historical decision before it.

### 7. Separate planning, apply, and closeout evidence

The proposal/design/tasks establish what may be reviewed. They do not authorize apply.
Before any target edit, a separate explicit Stage 2 apply authorization is required and
the apply agent must first record a fresh baseline: HEAD, all worktree changes, active
OpenSpec changes, and unchanged DeerFlow gitlink/worktree metadata.

Each applied adjustment has its own complete Adjustment Record. C-005 and C-010 are
split into `.a`/`.b`/`.c` records; C-011 has one record plus one sub-row per ADR. Each
record must include exact before/after text, risk, possible side effects, controls,
verification, observed side effects (including bounded "none observed" evidence), and
remaining mismatch owner. No generic "CONTEXT cleanup" record can replace these rows.

## Risks / Trade-offs

- [A documentation edit chooses A-003 or A-004 indirectly] -> Quarantine the listed
  terms; stop the individual edit when it needs a Runner/Rubric contract or post-loss
  diagnostic retention answer, and defer to the named future change.
- [Workspace terminology rewrites actual storage semantics] -> Limit C-004 to the
  verified owner/sibling distinction; cross-check the existing runner evidence without
  editing it.
- [A status label is read as a cancellation or implementation promise] -> Define
  `dormant` as retained history without active commitment and `planned` as direction
  without current capability; do not use `planned` for report export.
- [An ADR postscript is mistaken for historical rewrite] -> Append a uniform dated
  postscript that expressly preserves title/body and links current owner/route.
- [Removal of an unsupported requirement is mistaken for loss of product interest] ->
  State the narrow retirement and leave future report/coverage work to a separately
  owned product change.
- [A broad text sweep changes valid facts] -> Use the allowlist, per-occurrence
  classification, targeted diff review, and a hard stop for unlisted findings.
- [An ADR owner link becomes stale or malformed] -> Use only the five named relative
  targets above and record each source-to-target existence check after apply.
- [An ADR append accidentally rewrites historical bytes] -> Record the pre-append byte
  length and SHA-256, compare its prefix after the edit, and stop on any difference.
- [Existing user work is overwritten] -> Capture the pre-apply worktree and review the
  staged/unstaged diff after each adjustment; never revert unrelated changes.

## Migration Plan

1. Obtain a new, explicit Stage 2 apply authorization after review of this completed
   plan. Planning authorization does not satisfy this condition.
2. Record the fresh baseline and create the per-occurrence classification table plus
   empty per-adjustment evidence records.
3. Apply only the allowlisted explanatory edits, review each C item independently, and
   stop immediately at a quarantine or frozen-path boundary.
4. Run the listed documentation/governance validation, fill observed-side-effect and
   proof-bound fields, then conduct the required local re-audit before archive.
5. Archive only when all authorized tasks are complete and no unowned wording is being
   silently treated as resolved. Stop after archive for the separate Stage 3
   authorization.

## Open Questions

None. The only material questions discovered by the audit are deliberately quarantined
to the already named A-003 and A-004 changes; they are not deferred design choices for
this cleanup.
