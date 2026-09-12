# evaluation-hardening Delta

> req: EVH-005

## MODIFIED Requirements

### Requirement: Release gate combines deterministic CI with optional LLM canary

The existing five pairwise-disjoint rapid or credentialed evidence selections,
offline/no-implicit-sync rapid deterministic gate, strict selected live/release lanes,
and stable existing workflow/status identity guarantees remain unchanged. Their
canonical rapid deterministic command is
`cd deep_research_harness && UV_OFFLINE=1 make verify`. A sixth,
pairwise-disjoint `periodic` selection SHALL contain maintained deterministic
public-entry scenarios whose clean-copy setup cost is intentionally excluded from the
rapid gate. The periodic selection SHALL be credential-free, offline-capable after its
explicit setup, and represented by a first-class pytest marker and test-evidence
selection; `make test`, `make verify`, and every rapid focused target SHALL exclude it.
Test-asset governance SHALL collect and validate periodic selectors and their central
claims without executing their process bodies as part of the rapid gate.
`tests/scenarios_suspended/` remains distinct: it contains only credentialed release
diagnostics that are not active supported-contract evidence. A dedicated CI workflow
SHALL run the periodic target when a pull request or `master` push changes the declared
entry-environment dependency surface: `deep_research_harness/Makefile`,
`pyproject.toml`, `uv.lock`, `run/**`, `scripts/**`, `src/**`, `src_fixtures/**`,
`tests/scenarios_periodic/**`, or the periodic workflow definition. It SHALL also run
daily and by manual dispatch; its result SHALL be visible as a distinct CI job, without
claiming repository branch-protection configuration. The periodic target SHALL write a
machine-readable duration report and enforce a declared per-scenario budget or an
explicit owner/reason/expiry waiver. CI path filters, working directories, artifacts,
release-attestation scopes, and protected-path checks for the existing rapid workflow
SHALL continue to use `deep_research_harness/`, while `backend/`, `frontend/`, and
`openspec/` boundary checks remain repository-root checks. A filesystem-root change
SHALL not rename the existing rapid workflow display name, job/status identity, test
lane, or evidence semantic. (`EVH-005`, `EVH-032`)

OpenSpec governance evidence SHALL NOT be part of the Harness `make verify`
composition. The project SHALL maintain one OpenSpec root governance aggregate that
combines every registered OpenSpec checker — requirements registry, main-spec
structure, project architecture, Change Guidance, requirement evidence coverage, and
Harness dependency direction — as an OpenSpec-side gate run from the repository root.
The aggregate SHALL be orchestration-only: it SHALL invoke each component checker,
preserve its exit code, and aggregate results without owning rule semantics, writing
the requirement registry, or reimplementing delta/registry parsing. The aggregate
SHALL expose a read-only planning phase that delegates active-change admission checks
to the owning components (Change Guidance for the Focus Card, the selected-change
scope of the specification checker for delta headers and titles, the planning scope
of the requirement checker for reservations and collisions, and native strict change
validation for MODIFIED requirement/scenario preservation) and a closeout phase that
requires a zero exit from every component checker before a change SHALL be archived
through repository agent workflows; closeout SHALL NOT add a separate consistency
checker because the component checkers own registry, header, and evidence
consistency. Harness verification SHALL remain independently runnable without the
OpenSpec tree, and no Harness guide, documentation, Makefile, application test, or
asset SHALL read, import, execute, or link OpenSpec content. (`EVH-005`)

#### Scenario: Canonical verification starts from the Harness root
- **WHEN** a developer runs the complete rapid deterministic verification gate
- **THEN** `cd deep_research_harness && UV_OFFLINE=1 make verify` performs the existing
  local aggregate without resolving a former downstream root

#### Scenario: Governance gate runs beside Harness verification
- **WHEN** archive closeout runs for an active change
- **THEN** the OpenSpec root aggregate runs every registered checker from the
  repository root with component exit codes preserved and no duplicate consistency
  check, and `cd deep_research_harness && UV_OFFLINE=1 make verify` completes
  independently without executing or linking OpenSpec content

#### Scenario: A failing closeout stops repository archive workflows
- **WHEN** any component checker exits non-zero at closeout
- **THEN** the aggregate exits non-zero and repository archive agent workflows stop
  with the failing checker identified before native archive runs; a direct native
  `openspec archive` invocation is not blocked

#### Scenario: Planning admission delegates to component owners
- **WHEN** the read-only planning phase checks an active change
- **THEN** Focus Card grammar is evaluated by the Change Guidance checker, delta
  header/title rules by the specification checker's selected-change scope, ID
  reservations and collisions by the requirement checker's planning scope, and
  MODIFIED requirement/scenario preservation by native strict change validation,
  with no parsing reimplemented inside the aggregate
