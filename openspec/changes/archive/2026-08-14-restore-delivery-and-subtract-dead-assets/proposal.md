## Why

The current checkout depends on ignored machine-local CI workflows and OpenSpec skills,
so a clean clone cannot run the repository's promised deterministic delivery route or
the required propose-to-polish lifecycle. The same baseline also contains a bounded
set of proven empty scaffolding, superseded evidence, and test-only compatibility
surfaces that can be retired only after repository delivery is restored.

## What Changes

- Restore the exact repository-owned deterministic and manual-live CI workflows, the
  project OpenSpec skills, and their `codex` target from the last tracked delivery
  revision; remove the broad root ignore rules that hid these required artifacts.
- Establish a clean-clone trackedness guard for repository delivery without turning
  ignored local copies into an accepted fallback or changing the manual-live lane.
- Remove the eight redundant `.gitkeep` markers, the empty `tests/e2e` scaffold and
  its structural entry, while retaining all current lane, registry, and suspension
  guards.
- Compare the superseded imported workflow report against its current historical evidence owners,
  then remove the report and its shape-only test; remove the two private demo helpers
  and the legacy short-state planner helper only after their canonical tests carry the
  distinct behavior.
- Keep the five owner-scoped workstreams in one bounded program and archive it only
  when every frozen Candidate and attached obligation has closure evidence.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `deep-research-delivery-efficiency`: the existing deterministic CI delivery
  requirement also requires tracked clean-clone discovery of its workflow and the
  project OpenSpec lifecycle skills, with a fail-closed local-fallback guard.

The structural inventory, historical evidence status, demo behavior, and
topic-planning behavior already have accepted owners; this change restores or
subtracts their current implementation without changing those normative contracts.

## Impact

- Root `.gitignore`, `.github/workflows/`, and `.agents/skills/` become repository
  delivery artifacts; `openspec/governance/project-structure.toml` and its focused
  guard enumerate only current paths.
- Affected downstream surfaces are the project contract tests, test-asset registry
  joins, `deep_research_harness/docs/`, `scripts/_demo_core.py`, and the topic-planning
  prompt helper/export. No public DeerFlow interface, persisted data format, external
  installer, credentialed live behavior, or `deerflow/` source is changed.

## Program Focus

- **Program outcome:** A clean clone has one repository-tracked CI and OpenSpec skill delivery route, and only the proven dead repository, test, evidence, demo, and planner assets are retired behind their existing owners and guards.
- **Candidate / obligation budget:** OR-C01, OR-C02, OR-C04, TA-C01, TA-C02, TA-C05, EC-C04, RC-C02, OR-C06, TA-C03, TA-C04, TA-C06, TA-C07, EC-C01, EC-C03, RC-C07
- **Declared workstream order:** delivery, test-structure, evidence-report, demo-adapter, topic-planner
- **Program decision authority:** Repository Governance Owner approves the frozen program scope, sequence, and whole-program archive closure; each named workstream owner retains its own semantics and implementation decisions.
- **Shared archive invariant:** Every budget ID has the declared owner-scoped evidence, no clean clone depends on ignored local delivery copies, and retained lane, historical-evidence, entry, registry, and planner guards remain falsifiable.
- **Program failure / recovery:** A failed workstream remains active for its owner to forward-repair within the frozen scope. If that cannot close, roll back that workstream and any dependent later workstreams to the pre-workstream invariant; if neither route closes, keep the program active for plan-level re-scope or whole-program rollback, never partial archive.
- **Split / expansion rule:** The five registered workstreams and 16-ID budget are fixed. No workstream becomes a new change and no new Candidate enters without approved plan revision that preserves the eight-change budget.
- **Not in scope:** An external skill installer, new CI lanes, credentialed live execution, public or persisted compatibility changes, runtime behavior changes, and modifying or source-browsing `deerflow/`.

### Workstream Focus: delivery

- **Primary module / causal owner:** repository-delivery
- **Seam classification:** deterministic-guardrail because tracked repository artifacts and a clean-clone guard determine whether the promised CI and OpenSpec lifecycle can be discovered without local residue.
- **Question:** Which exact repository-tracked workflows and project skills make deterministic CI, manual-live isolation, and `propose -> polish -> apply` reproducible from a clean clone?
- **Necessary adjacent/external contracts:** deep-research-delivery-efficiency answers the canonical deterministic CI command and duration check; project-structure answers the exact tracked inventory; the Agent Charter answers the OpenSpec lifecycle boundary; no external installer is admitted.
- **Evidence seam:** A lowest-level repository contract test verifies tracked paths, target metadata, workflow semantics, and a planted missing-delivery violation; a clean-clone preflight supplies bounded integration evidence.
- **Not in scope:** Changing workflow trigger scope, enabling manual-live execution, changing secrets, adding external installers, or changing any downstream runtime behavior.
- **Triggered review policies:** change-admission, control-placement
- **Candidate / obligation IDs:** OR-C01, OR-C02, OR-C04
- **Target / retirement:** Restore the two deleted workflows and the exact project skill tree as tracked artifacts; retire root ignore coverage and machine-local copies as an accepted delivery authority.
- **Surface grade:** cross-boundary repository delivery for contributors, CI, and Codex skill discovery; no runtime API or persisted surface.
- **Decision authority:** Repository Governance Owner selected repository-tracked delivery and approves any recovery that changes the frozen route.
- **Negative path / recovery:** Missing, ignored, altered, or locally shadowed delivery artifacts fail the deterministic guard before subtraction begins; restore only the tracked historical artifacts and their current contract alignment, and keep the program active until the clean-clone route passes.

#### Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Repository delivery ownership | Repository Governance Owner selected repository-tracked delivery | Git index and repository delivery contract test prove exact workflow, skill, and target paths | non-bypassable | A clean clone cannot claim CI or polish availability from ignored local copies; restore the tracked route before any subtraction | Reuses canonical Make and skill routes; avoids an external installer and a second discovery authority | Trackedness negative fixture plus bounded clean-clone preflight |

### Workstream Focus: test-structure

- **Primary module / causal owner:** project-structure
- **Seam classification:** deterministic-guardrail because the structure registry and collected test assets mechanically distinguish a current test surface from empty scaffolding.
- **Question:** After delivery owns its structural half of OR-C04, which empty markers and registry entry can be removed without shrinking current test collection, lane selection, or suspended-evidence guarantees?
- **Necessary adjacent/external contracts:** delivery supplies the completed repository-delivery structural handoff; test-evidence policy answers retained registry joins and suspension evidence.
- **Evidence seam:** Structure checker and focused test-asset/lane contract tests with a planted missing current path or orphaned registry condition.
- **Not in scope:** Activating release E2E, deleting a real test file or selector, changing marker semantics, or modifying delivery-owned paths.
- **Triggered review policies:** change-admission
- **Candidate / obligation IDs:** TA-C01, TA-C02, TA-C03, TA-C04
- **Target / retirement:** Retire eight redundant markers, the empty `tests/e2e` directory, and its exact registry entry; retain non-empty roots, EVH-024 suspension, and executable evidence registries.
- **Surface grade:** repository-internal structural inventory and deterministic test-evidence guard.
- **Decision authority:** Project Structure Owner approves the exact registry subtraction after the delivery handoff.
- **Negative path / recovery:** Any collection, lane, structure, or evidence-join failure restores only the removed test-structure entries and leaves delivery intact; the program remains active for repair.

### Workstream Focus: evidence-report

- **Primary module / causal owner:** evaluation-hardening
- **Seam classification:** deterministic-guardrail because current historical evidence routes and evidence checks distinguish retained provenance from a superseded verdict copy.
- **Question:** Do the baseline, attestation, and regression-descent records retain every unique fact needed before the superseded imported workflow report and shape-only test are removed?
- **Necessary adjacent/external contracts:** current evaluation-hardening evidence policy answers registry/claim joins; historical baseline and attestation records answer provenance without becoming current release verdicts.
- **Evidence seam:** Focused provenance comparison and test-asset/evidence contracts prove retained historical routes, redaction, and current regression policy after the report test is gone.
- **Not in scope:** Rewriting frozen evidence payloads, claiming a new release result, running a credentialed live lane, or deleting baseline, attestation, or regression-descent policy.
- **Triggered review policies:** change-admission
- **Candidate / obligation IDs:** TA-C05, OR-C06, TA-C06, TA-C07
- **Target / retirement:** Retire only the superseded imported workflow report and its implementation-shape test after evidence comparison; retain current indexes, dated provenance, and regression descent.
- **Surface grade:** repository historical-evidence route and deterministic evidence governance.
- **Decision authority:** Evaluation Hardening Owner approves the unique-fact comparison and removal evidence.
- **Negative path / recovery:** Any unmatched provenance, inbound route, or evidence-join failure keeps the report/test in place and records the missing owner; no historical record is rewritten to manufacture closure.

### Workstream Focus: demo-adapter

- **Primary module / causal owner:** demo-adapter
- **Seam classification:** wiring because private compatibility helpers only duplicate canonical profile and preflight behavior already owned by the demo adapter path.
- **Question:** Can the canonical profile and preflight tests carry every unique supported-profile and blank-credential behavior before the duplicate private helpers and tests are removed?
- **Necessary adjacent/external contracts:** demo-pipeline answers canonical preflight semantics; entry-surface guards answer that distinct entries and old-root rejection remain current.
- **Evidence seam:** Focused unit and integration tests prove explicit model selection, blank-credential rejection, safe failure before adapter/Bundle construction, and no secret projection through canonical APIs.
- **Not in scope:** Exported constructor changes, model/provider support changes, new credential flows, or runtime/Bundle behavior changes.
- **Triggered review policies:** change-admission
- **Candidate / obligation IDs:** EC-C04, EC-C01, EC-C03
- **Target / retirement:** Move unique helper cases to canonical profile/preflight tests, then retire `_resolve_demo_models`, `check_credentials_available`, and their direct implementation-shape tests.
- **Surface grade:** private implementation and test-only helper/export surface.
- **Decision authority:** Demo Adapter Owner approves that canonical tests cover the retired helper behavior.
- **Negative path / recovery:** A missing canonical behavior or changed safe preflight outcome restores only the affected helper/test until forward repair proves the existing contract; no entry surface is merged or removed.

### Workstream Focus: topic-planner

- **Primary module / causal owner:** topic-planning
- **Seam classification:** wiring because the legacy helper is a test-only short-state projection while production planning already reads and validates the canonical Bundle profile.
- **Question:** Do canonical Bundle-profile assignment tests cover the legacy helper's supported fields while retaining all profile projection and refinement mismatch rejections?
- **Necessary adjacent/external contracts:** topic-planning-node answers the canonical planner assignment; Bundle profile projection validation answers the state-to-profile consistency boundary.
- **Evidence seam:** Focused topic-planning prompt tests prove canonical profile dimensions, degraded fallback, request fallback, language, comparison, and negative profile/refinement projection failures.
- **Not in scope:** Changing profile schemas, planner prompt behavior, Bundle persistence, public planning APIs, or refinement lifecycle semantics.
- **Triggered review policies:** change-admission
- **Candidate / obligation IDs:** RC-C02, RC-C07
- **Target / retirement:** Retire `planner_inputs_from_state`, its export, and the direct legacy test after canonical assignment tests own the supported behavior and existing negative guards.
- **Surface grade:** private test-only helper and module export.
- **Decision authority:** Topic Planning Owner approves canonical test coverage before helper retirement.
- **Negative path / recovery:** Any missing canonical field coverage or lost fail-closed projection behavior restores the helper/test while the workstream repairs forward; production prompt behavior remains the terminal invariant.
