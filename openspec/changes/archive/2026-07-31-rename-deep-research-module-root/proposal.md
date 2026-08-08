## Why

The generic checkout root `agent/` is ambiguous beside DeerFlow's agent runtime,
`agents/` layer, and graph-node terminology. It is also an established filesystem
contract for governance, CI, Docker, operator commands, and retained local state, so
an unplanned rename would strand data or silently break automation.

## What Changes

- **BREAKING** Rename the checked-out Deep Research module root from `agent/` to
  `deerflow_research/`; it becomes the only canonical source, test, command, and
  documentation path. No permanent alias, symlink, or second source tree remains.
- Preserve the public Python and tool identities: distribution
  `deerflow-deep-research`, import namespace `deerflow_deep_research`, and public
  tool name `deep_research`.
- Move the governed structure registry, generated module guide, project tooling,
  CI path filters/cwds/artifacts, Docker mount and `PYTHONPATH`, scripts, tests,
  current documentation, and active OpenSpec references to the canonical root.
- Establish an explicit, operator-confirmed, idempotent migration for ignored
  retained session data and the Deep Research diagnostic journal from the old root.
  It must reject conflicts, never delete or overwrite data, and preserve a
  recoverable pre-migration state; `.env` is copied/recreated by the operator and
  `.venv` is rebuilt.
- Preserve historical archive paths unless a historical document is still an active
  navigation, command, or validation consumer. Retain CI status identity until
  branch-protection, badge, and external automation consumers have been checked.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `demo-pipeline`: run the supported demo pipeline from the canonical module root.
- `deployment-configuration`: load and mount the downstream package from
  `deerflow_research/src` in local and Docker environments.
- `evaluation-hardening`: run and attest deterministic verification from the
  canonical root without weakening protected-path or release-evidence checks.
- `project-structure`: make `deerflow_research/` the mechanically enforced
  downstream root and generated locator target.
- `research-run-session`: preserve access to ignored retained sessions and
  diagnostics through an explicit, conflict-safe local-data migration during the
  root rename.

## Change Focus

- **Primary module / causal owner:** repository filesystem contract, owned
  mechanically by `openspec/governance/project-structure.toml`; retained-state
  semantics remain owned by `deerflow_research/src/deerflow_deep_research/runtime/`.
- **Question:** How can the checkout root become unambiguous without changing public
  Python identity, splitting ownership, or losing path-addressed local state?
- **Necessary adjacent/external contracts:** governance registry/checkers (canonical
  path inventory and generated guide); CI workflows (trigger, cwd, artifact path
  while retaining status identity); Docker override (host mount, container target,
  `PYTHONPATH`); runtime session/diagnostic stores (retained-state migration);
  GitHub branch protection, badges, and local automation (status and absolute-path
  consumer audit).
- **Evidence seam:** registry/checker fixtures; focused path-contract tests for
  scripts, workflows, Docker rendering, and runtime migration; `uv lock --check`;
  module deterministic verification.
- **Not in scope:** renaming the distribution, import namespace, public tool/API,
  generic DeerFlow agent terminology, `backend/` or `frontend/` product behavior,
  or rewriting historical archives.
- **Triggered charter policies:** local-context, change-admission, authority-and-projections, control-and-recovery, agent-information-map

## Impact

The implementation moves the tracked module directory and updates repository-owned
path consumers under governance, CI, Docker, docs, profiles, scripts, tests, and
current OpenSpec specs. It adds a local retained-data migration path and operator
checklist, but does not migrate secrets, virtual environments, GitHub settings, or
other user-specific external automation automatically. The change must be atomic for
tracked files and allow rollback by reverting those files; operator-migrated local
state is intentionally left untouched by rollback.
