## Why

The post-migration convergence plan needs a bounded program form to coordinate a
fixed set of owner-scoped workstreams, but the current admission route only accepts
one `## Change Focus`. Without a bootstrap, a multi-owner change could bypass the
existing focus boundary or attempt to approve its own broader rule.

## What Changes

- Preserve the ordinary proposal route: it continues to require exactly one
  `## Change Focus` with one primary causal owner.
- Add a bounded program proposal route with one `## Program Focus` and registered
  `### Workstream Focus: <stable-id>` records. A program records its complete
  Candidate/obligation budget, ordered workstreams, shared archive invariant,
  failure/recovery rule, split/expansion rule, and exclusions; each workstream
  retains the full Focus Card fields, its IDs, and independently selected policies.
- Extend the OpenSpec authoring route, local-context and change-admission guidance,
  and application Focus Gate to distinguish the two proposal forms without making a
  program a runtime owner, shared writer, or semantic authority for another
  workstream.
- Extend the charter checker and its contract fixtures to reject malformed program
  budgets, duplicate IDs, missing owners or required fields, and workstream records
  that are absent from or outside the declared program registration.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `deep-research-agent-charter`: active-change admission supports a mechanically
  bounded program form while preserving the ordinary single-owner Focus Card route.

## Impact

- `openspec/config.yaml`, `openspec/policies/local-context.md`,
  `openspec/policies/change-admission.md`, and `deep_research_harness/AGENTS.md`
  authoring guidance
- `openspec/governance/check_agent_charter.py` and
  `deep_research_harness/tests/contract/test_agent_charter_governance.py`
- The `deep-research-agent-charter` main-spec requirement after this change is
  implemented and archived

## Change Focus

- **Primary module / causal owner:** OpenSpec Governance / Agent Charter admission; it owns the proposal grammar and deterministic validation boundary.
- **Seam classification:** deterministic-guardrail because the charter checker admits only complete proposal forms and creates no runtime authority.
- **Question:** How can a declared program coordinate a frozen set of owner-scoped workstreams without widening the ordinary single-owner change route or creating a shared runtime authority?
- **Necessary adjacent/external contracts:** Agent Charter active-change admission and change-admission policy: whether ordinary and program forms remain exclusive and fail closed; contributor information-map contract: how `openspec/config.yaml` and `deep_research_harness/AGENTS.md` route authors to the right form without becoming product authority.
- **Evidence seam:** `deep_research_harness/tests/contract/test_agent_charter_governance.py` planted valid and invalid active-proposal fixtures plus `check_agent_charter.py`.
- **Not in scope:** Implementing any of the 54 audit Candidates, changing DeerFlow, granting a program runtime authority, or allowing static validation to certify semantic diff scope.
- **Triggered review policies:** local-context, change-admission, control-placement, control-and-recovery, agent-information-map

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Program admission budget and registered workstream records | No cognitive candidate or human judgment; an author supplies declarative proposal text for review | `check_agent_charter.py` evaluates proposal grammar and the program's internal budget/registration closure; apply/archive review retains semantic-scope judgment | non-bypassable | An ordinary change remains exactly one Focus Card; a malformed program is rejected before implementation, and an uncloseable workstream stays active for approved forward repair, rollback, or plan-level re-scope | Extends the existing charter gate rather than adding a runtime coordinator, shared writer, or parallel approval path | Planted program-proposal fixtures in `test_agent_charter_governance.py` and the repository charter-governance command |
