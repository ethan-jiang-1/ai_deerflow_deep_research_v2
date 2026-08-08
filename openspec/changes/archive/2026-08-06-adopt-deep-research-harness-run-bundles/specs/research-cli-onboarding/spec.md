> req: REC-004, REC-005, REC-006, REC-008

## ADDED Requirements

### Requirement: Real CLI uses one Bundle lifecycle vocabulary and truthful loss guidance

The real CLI SHALL consume the shared typed Bundle lifecycle result for start, status,
control, refinement, and inspection. It SHALL display the bounded `bundle_id` where
appropriate and explain active, awaiting-input, ended, and unavailable outcomes with
their legal next action. It SHALL not display or require `research_id`, session
references, checkpoint names, or host paths, and it SHALL not claim that a deleted
Bundle can resume. (`REC-008`)

#### Scenario: CLI reports a deleted Run without false resume guidance
- **WHEN** a CLI action targets a Bundle that was externally deleted
- **THEN** it reports the typed unavailable outcome and guides the user to a fresh independent Run or permitted observation only

## MODIFIED Requirements

### Requirement: Real CLI exposes a safe run reference and local inspection path

The real CLI SHALL expose only the shared bounded `bundle_id` from a lifecycle result as
a selected Run reference. It may offer supported contained Bundle inspection through the
same trusted-scope lifecycle/inspection boundary, but SHALL not display or accept a
session reference, `research_id`, raw path, provider key, checkpoint namespace, or
retained-manifest locator. A deleted, unavailable, foreign, or ambiguous Bundle SHALL
produce truthful bounded guidance and SHALL not offer resume/recovery through a local
path. (`REC-004`)

#### Scenario: CLI inspection cannot reconstruct a lost Run
- **WHEN** a user requests inspection for a deleted Bundle whose historical diagnostic remains
- **THEN** the CLI reports the bounded unavailable outcome and performs no graph, provider, or content recovery

### Requirement: Real CLI reports provider diagnostics and honest fresh-start guidance

The real CLI and TUI SHALL retain the existing redacted provider-diagnostic category,
phase, bounded recovery-observation, diagnostic-reference, and legal-next-action
guarantees. A current Deep Research lifecycle projection SHALL use the shared typed
Bundle result: an inspect action is permitted only for an available selected Bundle and
never for a retained session reference or a diagnostic alone. For the `fresh_start`
legal action, the static `make demo-real` command SHALL be labelled as a distinct fresh
run from `deep_research_harness/`; it SHALL not promise resume or recovery of an
unavailable Bundle. (`REC-006`)

#### Scenario: Provider diagnosis cannot make a deleted Bundle inspectable
- **WHEN** a provider-diagnostic observation remains after its Bundle has been deleted
- **THEN** the CLI may render the safe observation but suppresses inspection/control and
  directs the user only to the typed legal next action

### Requirement: Retained-diagnostic command is executable and read-only

Whenever CLI or TUI renders an available Bundle inspection action, it SHALL render the
documented command shape executable from `deep_research_harness/`:
`make demo-sessions DEMO_ARGS="inspect <bundle-id>"`. The command remains explicitly
read-only and may show only the existing safe diagnostic/timing observations. It SHALL
not accept a session reference, imply retry, resume, cross-process continuation, or
provider conclusion; an unavailable Bundle suppresses the command even when an
external diagnostic remains. (`REC-005`, `REC-006`)

#### Scenario: Rendered inspection command uses Bundle identity
- **WHEN** an authorized available terminal Bundle has a correlated retained diagnostic
- **THEN** the displayed command uses its bounded `bundle_id`, runs from
  `deep_research_harness/`, and returns only a read-only observation
