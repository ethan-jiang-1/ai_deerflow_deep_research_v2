## Context

See `proposal.md` for motivation. The current charter checker has a fixed list of
charter-local policy names, parses only `Triggered charter policies`, and conditionally
validates the independent Workflow Outcome and Node Agent review tables. The current
authoring route and focused fixture mirror that same charter-local assumption.

The two 2026-08-02 repair archives show the intended gap without becoming normative
runtime evidence. The provider-outcome repair separated a shared provider observation,
bridge classification, topic-planning recovery, and terminal projection. The HITL1
intake repair separated typed profile facts, correlated human input, local deterministic
confirmation, and residual semantic candidates. No active change other than this V1
proposal needs migration; archived artifacts are historical records.

## Goals / Non-Goals

**Goals:**

- Add one external, conditional, non-runtime review policy for cross-layer control
  placement.
- Make one canonical registry resolve both charter-local and external policy documents
  and their optional mechanical record validators.
- Migrate active Focus Cards to a single `Triggered review policies` field without
  weakening existing selected-review checks.
- Add deterministic, isolated evidence for the record's structural boundaries and
  preserve the long-term V1/V2 roadmap in `_backlog/plans/`.

**Non-Goals:**

- Do not add `openspec/guardrails/`, a session runner, dossier schema, reviewer
  identity, automated semantic judgment, or a commit/archive hook.
- Do not scan source or prose to decide whether a policy should have been selected.
- Do not create runtime types, gates, routes, state fields, prompts, provider policy,
  retries, human actions, or quality thresholds.
- Do not retrofit archived proposals or claim that a table would have prevented a
  historical repair or an external provider-budget outcome.

## Decisions

### 1. Add one external policy, not a second charter family

Create `openspec/policies/README.md` and `openspec/policies/control-placement.md`.
The README establishes the boundary: policies guide OpenSpec change design; the Agent
Charter routes local review; governance validates deterministic shape; a later V2 owns
cross-session orchestration. The new policy contains the trigger, the four closed
design postures, the exact review questions, the composition rules, and the
non-authority boundary.

The charter index links to the external policy and `charter.md` gains the narrow
principle: "Cognition proposes; deterministic owners validate, admit, and route."
Existing focused policies remain the owner of their own question. In particular,
Control Placement Review complements rather than duplicates Node Agent Review,
Workflow Outcome Review, human-interaction-integrity, authority-and-projections, or
control-and-recovery.

Rejected alternative: move the policy into
`openspec/governance/agent-charter/policies/` or create separate gate-classification,
prompt/code-ownership, and simple-control policies. The former hides its cross-change
role; the latter repeats existing guidance and creates a competing governance
authority.

### 2. Use one registry and one Focus Card field

Replace `Triggered charter policies` with `Triggered review policies` for active
proposals, authoring guidance, checker fixtures, and the V1 proposal itself. The field
uses one comma-separated canonical-name list on its single Focus Card list item, or
`none: <short rationale>`; it does not split external and charter policy selection into
separate required fields or allow continuation lines that the deterministic parser
would need to reinterpret.

The checker owns a small canonical registry. Each entry supplies its canonical name,
documentation path, and, where applicable, a record validator. Existing charter
policies resolve to their existing paths; `control-placement` resolves to the external
policy path. The checker confirms a declared canonical name is known and its document
exists, then runs only the validators selected by that declaration.

The migration is intentionally active-only. The implementation updates this proposal
before final checker verification, and it updates any concurrently active change if
one exists at implementation time. It never rewrites archive artifacts. An old field
in an active proposal fails after the migration, giving contributors one authoritative
shape rather than indefinitely accepting both spellings.

Until that checker-and-route implementation lands, this proposal retains the current
`Triggered charter policies` field and selects only policies known to the current
checker. The implementation changes its Focus Card and adds its Control Placement
Review in the same atomic migration that enables the new field; this keeps the active
planning home conformant both before and after the cutover.

Rejected alternative: retain both field names indefinitely. That permits a proposal
to conceal whether an external policy was selected and makes the checker contract
ambiguous.

### 3. Validate only the declared Control Placement Review shape

When `control-placement` appears in Triggered review policies, the checker requires
exactly one `## Control Placement Review` heading and the exact seven-column header and
separator specified by `DRC-009`. It requires at least one complete row, accepts only
`advisory`, `bounded-repair`, `human-decision`, or `non-bypassable` in the posture
column, and requires `human-interaction-integrity` in the same policy list if any row
uses `human-decision`.

The checker preserves independent validation for selected Node Agent and Workflow
Outcome Review records. It does not decide whether rows are redundant, whether a
direct fact is truly authoritative, whether a replay conclusion is correct, or
whether a proposal should select this policy. Those are design-review questions, not
machine-verifiable facts.

Rejected alternative: source scan for `run_agent`, checkpoint fields, or keywords.
Planned behavior can trigger a policy before source exists, and static scanning cannot
decide semantic ownership without both false positives and false negatives.

### 4. Make evidence describe the real boundary, not a new test taxonomy

The policy requires an evidence-seam answer but adds no evidence runner. Its guidance
requires an actual producer-to-consumer handoff test when a direct fact crosses
owners, and a write/reload/direct-consumer test when that fact is durable. A feature
with a human input and an invariant uses separate rows with `human-decision` and
`non-bypassable` postures instead of collapsing different effects into one label.

The V1 design records two historical replays:

| Archive | Placement question V1 would force | Actual resolution | Explicit limit |
| --- | --- | --- | --- |
| `fix-topic-planning-provider-outcomes` | Which owner classifies a provider/stop fact, which owner admits its observation, and which owner owns bounded recovery? | Bridge classifies one invocation; default-deny execution policy admits observation; topic planning owns its existing retry; terminal presentation only projects typed facts. | The policy cannot supply provider budget or determine that a new retry is safe. |
| `harden-hitl1-comparison-intake` | Which facts must be typed before acceptance, which inputs are human decisions, and which model outputs are only candidates? | Profile owns comparison/language completeness; correlated HITL1 input owns acceptance; exact confirmation is local; residual semantic handling remains candidate-only. | The policy cannot prove a subject grammar or model response is useful. |

This table is a replay baseline, not a claim of counterfactual prevention. It is kept
with V1's design; the long-term plan keeps the V1/V2 roadmap.

### 5. Synchronize the governance inventory and deterministic evidence

The implementation adds `DRC-009` to the append-only requirement registry, updates
the main Charter spec through this delta, marks the policy, checker, and focused test
with the requirement, and registers both new external policy paths in
`project-structure.toml`. The existing focused charter-governance fixture is extended
to materialize both policy roots and registry entries without using the real
repository. Requirement evidence references the focused test that covers independent
review enforcement.

The concise `openspec/config.yaml` route and the Deep Research module guide are
updated together. They remain within existing information-map budgets and point to
the external policy rather than reproducing its detailed matrix or examples.

## Risks / Trade-offs

- [The review becomes ceremony] -> Keep it conditional, use one row per changed
  decision/fact, require a concrete avoided/reused control and lowest responsible
  evidence seam, and retain replay counterexamples.
- [An author omits an applicable policy] -> The checker deliberately cannot infer
  applicability; Focus Card review, code review, and later V2 challenge remain the
  human feedback channels.
- [External policy paths create a second registry] -> Keep one checker-owned mapping
  from canonical name to documentation path and optional structural validator.
- [Migration breaks an active proposal] -> Keep this proposal on the current field
  until the route and checker land, then update every active proposal atomically with
  the field migration, leave archives untouched, and prove both migrated and malformed
  fixtures deterministically.
- [V1 expands into V2] -> Keep `openspec/guardrails/`, runner/dossier behavior, and
  review provenance out of the file list and retain V2's explicit deferred checkpoint
  in the backlog plan.

## Migration Plan

1. Add red fixture coverage for the renamed Focus Card field, external policy lookup,
   valid and invalid Control Placement Review tables, human-decision composition, and
   coexistence with current selected reviews.
2. Add the external policy/index, route it from the charter, update concise authoring
   guidance, and add the non-authority principle without introducing runtime behavior.
3. Implement the registry and conditional validator, then atomically migrate this
   active proposal and any other active proposal discovered at that time to Triggered
   review policies.
4. Register `DRC-009`, structural paths, and focused evidence; update the long-term
   V1/V2 plan status and retain the two repair replays as bounded evidence.
5. Run focused checker tests, repository governance checks, strict OpenSpec
   validation, and the offline deterministic verification gate before archive.

Rollback removes the route, registry entry, external policy, field migration, and
validator together. It has no persistent state or runtime data to migrate; archived
artifacts remain readable as historical records.

## Open Questions

None. V2's delivery hooks and cross-session evidence model are explicitly deferred
and therefore do not alter this task breakdown.
