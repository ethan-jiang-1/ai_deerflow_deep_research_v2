## Why

Several current contributor and OpenSpec-authoring surfaces still describe repository-root
`backend/` and `frontend/` as DeerFlow upstream mirrors, although this checkout instead
contains DeerFlow at the `deerflow/` gitlink. The same stale topology causes an invalid
editable-harness path and makes proposal/closeout prose imply protection for directories
that are not this checkout's upstream boundary.

## What Changes

- Replace the stale root-mirror description in `openspec/config.yaml`,
  `deep_research_harness/AGENTS.md`, and `openspec/agent-charter/charter.md` with the
  verified boundary: `deep_research_harness/` is the downstream product and `deerflow/`
  is an upstream gitlink that is leveraged but neither modified nor source-browsed for
  this change.
- Correct `openspec/config.yaml` proposal and archive guidance to require honest manual
  scope/diff evidence for the `deerflow/` gitlink, without claiming that a gitlink
  detector already exists.
- Correct the Quick Start editable harness path in `deep_research_harness/README.md` to
  `../deerflow/backend/packages/harness`, preserving its repository-root execution
  context.
- Apply one verification-unblocking format-only maintenance edit in
  `deep_research_harness/tests/contract/test_selected_change_closeout.py`: let the
  repository's configured Ruff formatter join two adjacent string literals in one
  `write_text()` test fixture. The string value, test inputs, assertions, and behavior
  remain unchanged.
- Retain active main-spec references to `backend/` and `frontend/` where they are valid
  negative guards against placing downstream source in those paths.

## Change Focus

- **Primary module / causal owner:** `openspec/config.yaml` authoring route; it owns the
  stale topology and closeout guidance presented to every OpenSpec change author.
- **Seam classification:** deterministic-guardrail (repository topology and documented
  installation paths are checked against Git metadata and tracked configuration, not
  inferred from runtime behavior).
- **Question:** How can current authoring and contributor entry documents name the actual
  `deerflow/` gitlink boundary without weakening valid legacy-root placement guards or
  claiming unimplemented mechanical enforcement?
- **Necessary adjacent/external contracts:** `deep_research_harness/AGENTS.md` and
  `openspec/agent-charter/charter.md` answer whether the local contributor route uses
  the same product/upstream boundary; `deep_research_harness/README.md` answers the
  repository-root editable-install command; Git index metadata answers whether
  `deerflow/` is a gitlink. No DeerFlow source interface is needed.
- **Evidence seam:** `git ls-files --stage deerflow`, `git submodule status -- deerflow`,
  an exact current-authority occurrence review, and a repository-root command/path
  check; no runtime test or DeerFlow source inspection is required.
- **Not in scope:** application code, runtime contracts, governance executables,
  manifests/TOML, main specs, archived changes, `deerflow/` content or worktree, an
  automatic gitlink detector (A-002), and global replacement of valid `backend` or
  `frontend` terms. The only test-file exception is V-001: configured Ruff formatting
  of one adjacent-literal expression, with no test semantic or behavior change.
- **Triggered review policies:** change-admission, agent-information-map

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. This change corrects authoring and contributor documentation only; it changes no
observable runtime behavior or main-spec requirement. `skip_specs: true` is declared in
the change metadata.

## Impact

- Affected documentation: `openspec/config.yaml`, `deep_research_harness/AGENTS.md`,
  `openspec/agent-charter/charter.md`, and `deep_research_harness/README.md`.
- One test file receives a format-only V-001 maintenance edit; no test behavior,
  application API, dependency metadata, runtime storage, graph behavior, governance
  executable, or DeerFlow source is affected.
- Closeout will rely on recorded manual evidence until a separately authorized A-002
  detector change exists.
