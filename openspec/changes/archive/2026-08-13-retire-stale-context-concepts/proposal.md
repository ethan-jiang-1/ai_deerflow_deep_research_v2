## Why

Current glossary and historical ADR surfaces still present several completed, absent, or
no-longer-current concepts as if they were active product or evaluation contracts. This
creates avoidable ambiguity between the DeerFlow host workspace, a Deep Research Run
Bundle, evaluation-run storage, current artifacts, and future or dormant product
surfaces.

This Stage 2 cleanup makes current explanatory authority honest without changing runtime
behavior, main-spec requirements, evaluation cases, or implementation. It also leaves the
two product-contract reconciliations, A-003 Rubric/Runner authority and A-004 diagnostic
availability after Bundle loss, to their separately named changes.

## What Changes

- Correct the glossary definition of an Evaluation Run Workspace so it is the
  Runner-owned per-execution directory and is not confused with the DeerFlow host
  workspace or a Deep Research Run Bundle.
- Retire completed-work future tense and a closed-change citation from the current
  evaluation glossary, while retaining the present control/run-data separation and its
  current owners.
- Make OpenSpec review-policy routing accurately permit one primary owner and every
  actually triggered canonical policy in the current OpenSpec glossary and Charter
  route, without changing the charter checker, policy library, or `openspec/config.yaml`.
- Remove unsupported current claims that every LLM-Bearing Node has a Suite smoke
  scenario or that `limited` and `inconclusive` require an independent readable report.
  Preserve the registered-current-coverage boundary, the structured Review Record, and
  the four-state result semantics.
- Separate current `final/report.md` Bundle output from a non-current Primary User
  reopen/copy/export capability; mark Support Handoff as planned and the dedicated
  Primary-User TUI plus its Local-First route as dormant.
- Append a uniform, postscript-only current-status/applicability note to ADRs 0002,
  0003, 0006, 0008, and 0010. Their titles and historical bodies remain unchanged.
- Do not act on C-006. Its broad CONTEXT relocation proposal was withdrawn because it
  was not a verified mismatch.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/CONTEXT.md`; it is the
  current Deep Research vocabulary surface that contains the stale assertions and must
  route each retained fact to its actual owner.
- **Seam classification:** wiring -- this change reconnects explanatory terminology to
  current owners and historical status; it changes no cognitive role, decision, or
  deterministic runtime behavior.
- **Question:** How can current vocabulary and selected historical ADRs distinguish
  existing facts from completed work, absent capability, planned capability, and dormant
  historical route without silently deciding A-003 or A-004?
- **Necessary adjacent/external contracts:** `openspec/CONTEXT.md` and
  `openspec/agent-charter/README.md` answer the current policy-cardinality wording;
  the five listed ADRs answer how their historical rationale is retained with a
  non-authoritative applicability postscript; `deployment-configuration` owns the
  current Dedicated Agent/reflected-tool route, `deep-research-harness-run-bundles`
  owns Bundle lifecycle/isolation, and `final-delivery-node` owns `final/report.md` as
  a Bundle artifact. No DeerFlow interface is needed.
- **Evidence seam:** exact occurrence review of the allowlisted explanatory files;
  current-owner cross-checks against non-archived main specs, registries, and repository
  source without editing them; OpenSpec strict validation and documentation/governance
  checks after apply.
- **Not in scope:** application code, tests, cases, registries, main specs, report or
  handoff schemas, Runner behavior, Rubric content, UI, public entry points, lifecycle
  semantics, governance executables, `openspec/config.yaml`, archived changes, and the
  `deerflow/` gitlink or its source. In particular, this change neither settles
  Rubric/Runner authority (A-003) nor whether supported diagnostics survive Bundle loss
  (A-004).
- **Triggered review policies:** change-admission, agent-information-map

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. The change corrects current explanatory and historical-status documentation only.
It changes no observable behavior or main-spec requirement, so `skip_specs: true` is
declared in the change metadata.

## Impact

- Planned apply allowlist: `deep_research_harness/CONTEXT.md`, `openspec/CONTEXT.md`,
  `openspec/agent-charter/README.md`, and
  `deep_research_harness/docs/adr/0002-tui-is-the-primary-user-interface.md`,
  `0003-deployment-owns-research-service-configuration.md`,
  `0006-layered-support-disclosure.md`, `0008-start-with-a-local-first-tui.md`, and
  `0010-completed-reports-remain-portable-in-local-first.md`.
- Planning and apply evidence remains in
  `_backlog/plans/alignment-audit-2026-08-12/alignment-audit-60-adjustments/`; each
  applied C item requires its own Adjustment Record with observed side effects.
- No runtime API, graph, storage contract, dependency, main specification, governance
  executable, or DeerFlow content changes.
